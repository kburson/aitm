"""Verify current ordinary PR evidence from the trusted target checkout."""

import argparse
import base64
import json
import os
import re
import select
import stat
import subprocess
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from python_gate import _policy_error

WORKFLOW = ".github/workflows/ci.yml"
GH_VERSION = "2.97.0"
ISSUER = "https://token.actions.githubusercontent.com"
PREDICATE = "https://slsa.dev/provenance/v1"
MAX_ARCHIVE = 2**22
MAX_MEMBER = 2**20
MAX_API = 2**24
CONTROLS = {
    "workflow": WORKFLOW,
    "observer": "tools/ci/pytest_evidence.py",
    "policy": "tools/ci/policy.json",
    "gate": "tools/ci/python_gate.py",
    "lock": "packages/aitm-usage/uv.lock",
}
VERIFIER = "tools/ci/verify_pr.py"
BASE_FILES = {
    "observer": CONTROLS["observer"],
    "policy": CONTROLS["policy"],
    "lock": CONTROLS["lock"],
    "configuration": "packages/aitm-usage/pyproject.toml",
}
ARTIFACTS = {"base", "python", "collector", "evidence"}
FIXED_JOBS = {"collect-evidence", "aitm-ci"}
CI_ANCESTORS = {"", "packages", "packages/aitm-usage", "tools"}
CI_CONFIG_NAMES = {
    ".coveragerc",
    "pytest.ini",
    "pytest.toml",
    ".pytest.toml",
    "pyproject.toml",
    "ruff.toml",
    ".ruff.toml",
    "conftest.py",
    "setup.cfg",
    "tox.ini",
    "sitecustomize.py",
    "usercustomize.py",
    "pytest.py",
    "coverage.py",
}
RUFF_CONFIG_NAMES = {".ruff.toml", "ruff.toml", "pyproject.toml"}


class Hold(ValueError):
    """A specific evidence requirement was not met."""


def require(condition, reason):
    if not condition:
        raise Hold(reason)


def digest(value, size=40):
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{size}}}", value)


def positive(value):
    return type(value) is int and value > 0


def timestamp(value):
    date = datetime.fromisoformat(value)
    require(date.utcoffset() is not None, "missing timezone in evidence timestamp")
    return date


def decode_json(raw):
    def unique(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), "duplicate JSON object member")
        return result

    def nonfinite(_value):
        raise Hold("nonfinite JSON number")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def run_bounded(argv, maximum):
    deadline = time.monotonic() + 90
    data = bytearray()
    try:
        with subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ) as process:
            try:
                while True:
                    remaining = deadline - time.monotonic()
                    require(
                        remaining > 0
                        and select.select([process.stdout], [], [], remaining)[0],
                        "trusted command timed out",
                    )
                    chunk = os.read(
                        process.stdout.fileno(), min(65536, maximum + 1 - len(data))
                    )
                    if not chunk:
                        break
                    data.extend(chunk)
                    require(
                        len(data) <= maximum, "trusted command output exceeds limit"
                    )
                require(
                    process.wait(timeout=max(0, deadline - time.monotonic())) == 0,
                    "trusted command failed",
                )
            finally:
                if process.poll() is None:
                    process.kill()
    except (OSError, subprocess.TimeoutExpired):
        raise Hold("trusted command could not complete") from None
    return bytes(data)


class GitHub:
    def __init__(self, repo):
        require(
            isinstance(repo, str)
            and re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repo)
            and repo.split("/")[1] not in {".", ".."},
            "invalid GitHub repository name",
        )
        self.repo = repo
        self.url = f"https://github.com/{repo}"

    def command(self, args, maximum):
        return run_bounded(["gh", *args], maximum)

    def api(self, endpoint, *, paginate=False, limit=MAX_API):
        path = f"repos/{self.repo}"
        if endpoint:
            path += "/" + endpoint
        args = ["api", "--hostname", "github.com", "--method", "GET", path]
        if paginate:
            args.extend(("--paginate", "--slurp"))
        try:
            return self.command(args, limit)
        except Hold as exc:
            # Endpoint strings only contain validated repository identities and route components.
            raise Hold(
                f"GitHub read failed for {endpoint or 'repository'}: {exc}"
            ) from None

    def document(self, endpoint):
        return decode_json(self.api(endpoint))

    def pages(self, endpoint, key):
        pages = decode_json(self.api(endpoint, paginate=True))
        require(isinstance(pages, list) and pages, f"missing {key} pages")
        total = pages[0]["total_count"]
        require(type(total) is int and total >= 0, f"invalid {key} count")
        entries = []
        for page in pages:
            require(
                page["total_count"] == total and isinstance(page[key], list),
                f"inconsistent {key} pagination",
            )
            entries.extend(page[key])
        require(len(entries) == total, f"incomplete {key} pagination")
        return entries

    def attestation(self, subject, bundle, ref, merge):
        version = self.command(["--version"], 4096).decode().splitlines()[0].split()
        require(
            version[:3] == ["gh", "version", GH_VERSION],
            f"use pinned GitHub CLI {GH_VERSION}",
        )
        with TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.json"
            attestation = candidate.with_name("attestation.sigstore.json")
            candidate.write_bytes(subject)
            attestation.write_bytes(bundle)
            try:
                raw = self.command(
                    [
                        "attestation",
                        "verify",
                        str(candidate),
                        "--hostname",
                        "github.com",
                        "--repo",
                        self.repo,
                        "--bundle",
                        str(attestation),
                        "--signer-workflow",
                        f"{self.repo}/{WORKFLOW}",
                        "--cert-oidc-issuer",
                        ISSUER,
                        "--predicate-type",
                        PREDICATE,
                        "--source-ref",
                        ref,
                        "--source-digest",
                        merge,
                        "--signer-digest",
                        merge,
                        "--deny-self-hosted-runners",
                        "--format",
                        "json",
                    ],
                    MAX_ARCHIVE,
                )
            except Hold:
                raise Hold(
                    "signature verification failed with pinned GitHub CLI"
                ) from None
        return decode_json(raw)


@dataclass(frozen=True)
class Pull:
    number: int
    repository_id: int
    target: str
    head_branch: str
    base: str
    head: str
    merge: str

    @property
    def merge_ref(self):
        return f"refs/pull/{self.number}/merge"


def branch_name(value):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9_./-]+", value)
        and not value.startswith("-")
        and ".." not in value
        and all(
            part and not part.startswith(".") and not part.endswith(".lock")
            for part in value.split("/")
        )
    )


def check_ref(github, ref, sha, context):
    document = github.document("git/ref/" + quote(ref.removeprefix("refs/"), safe="/"))
    require(
        document["ref"] == ref
        and document["object"]["sha"] == sha
        and document["object"]["type"] == "commit",
        f"live {context} moved or is not a commit",
    )


def live_pull(github, number, target):
    repository = github.document("")
    require(
        repository["visibility"] == "public"
        and repository["full_name"] == github.repo
        and positive(repository["id"]),
        "repository identity or public signing route unavailable",
    )
    pr = github.document(f"pulls/{number}")
    require(
        pr["number"] == number
        and pr["state"] == "open"
        and pr["merged"] is False
        and pr["mergeable"] is True,
        "PR identity, open state or mergeability unavailable",
    )
    base, head = pr["base"], pr["head"]
    for endpoint in (head, base):
        require(
            endpoint["repo"]["full_name"] == github.repo
            and endpoint["repo"]["id"] == repository["id"],
            "ordinary same-repository linkage required",
        )
    require(base["ref"] == target, "PR target disagrees with declared target")
    require(branch_name(head["ref"]), "invalid PR head branch")
    require(
        all(
            digest(value)
            for value in (base["sha"], head["sha"], pr["merge_commit_sha"])
        ),
        "PR head, base or tested commit missing",
    )
    pull = Pull(
        number,
        repository["id"],
        target,
        head["ref"],
        base["sha"],
        head["sha"],
        pr["merge_commit_sha"],
    )
    check_ref(github, f"refs/heads/{target}", pull.base, "target")
    check_ref(github, pull.merge_ref, pull.merge, "merge ref")
    return pull


def canonical_workflow(github):
    workflow = github.document("actions/workflows/ci.yml")
    require(
        workflow["path"] == WORKFLOW
        and workflow["state"] == "active"
        and positive(workflow["id"]),
        "canonical workflow unavailable",
    )
    return workflow["id"]


def run_identity(run, pull, workflow):
    require(
        run["workflow_id"] == workflow
        and run["path"] == WORKFLOW
        and run["event"] == "pull_request"
        and run["head_sha"] == pull.head
        and run["repository"]["id"]
        == run["head_repository"]["id"]
        == pull.repository_id
        and positive(run["id"])
        and positive(run["run_attempt"])
        and positive(run["check_suite_id"]),
        "canonical run identity is contradictory",
    )


def matches_pull(run, pull):
    associations = run["pull_requests"]
    require(
        isinstance(associations, list) and associations,
        "canonical run has no PR association",
    )
    matching = [item for item in associations if item["number"] == pull.number]
    require(len(matching) <= 1, "duplicate PR association")
    if not matching:
        return False
    endpoint = matching[0]
    head, base = endpoint["head"], endpoint["base"]
    require(
        head["repo"]["id"] == base["repo"]["id"] == pull.repository_id
        and head["sha"] == pull.head
        and head["ref"] == pull.head_branch
        and digest(base["sha"])
        and branch_name(base["ref"]),
        "canonical run PR association disagrees with repository or head",
    )
    return (base["sha"], base["ref"]) == (pull.base, pull.target)


def newest_run(github, pull, workflow):
    runs = github.pages(
        f"actions/workflows/{workflow}/runs?head_sha={pull.head}&event=pull_request&per_page=100",
        "workflow_runs",
    )
    # GitHub's filtered run search caps each query at 1,000 results.
    require(len(runs) < 1000, "canonical run search reached the provider limit")
    require(len({run["id"] for run in runs}) == len(runs), "duplicate canonical run")
    matching = []
    for run in runs:
        run_identity(run, pull, workflow)
        if matches_pull(run, pull):
            matching.append(run)
    require(
        matching,
        "no canonical run for the exact live candidate; trigger a fresh PR event",
    )
    return max(matching, key=lambda run: (timestamp(run["created_at"]), run["id"]))


def successful(record):
    return record.get("status") == "completed" and record.get("conclusion") == "success"


def read_attempt(github, pull, workflow, selected):
    run, attempt = selected["id"], selected["run_attempt"]
    path = f"actions/runs/{run}/attempts/{attempt}"
    require(successful(selected), "selected attempt is not complete and successful")
    record = github.document(path)
    run_identity(record, pull, workflow)
    require(
        record["id"] == run
        and record["run_attempt"] == attempt
        and record["check_suite_id"] == selected["check_suite_id"]
        and matches_pull(record, pull)
        and successful(record),
        "selected attempt identity or outcome disagrees",
    )
    run_created = timestamp(selected["created_at"])
    started = timestamp(record["run_started_at"])
    require(started >= run_created, "selected attempt start predates run")
    if attempt == 1:
        require(
            record["created_at"] == selected["created_at"],
            "first attempt creation disagrees with canonical run",
        )
    else:
        # GitHub can persist a rerun record after recording its start. Job and
        # signature freshness still use the attempt's reported start time.
        require(
            run_created
            <= timestamp(record["created_at"])
            <= timestamp(record["updated_at"]),
            "selected rerun creation falls outside the run and attempt update times",
        )
    suite = github.document(f"check-suites/{selected['check_suite_id']}")
    require(
        suite["id"] == selected["check_suite_id"]
        and suite["app"]["slug"] == "github-actions"
        and positive(suite["app"]["id"])
        and suite["head_sha"] == pull.head
        and successful(suite),
        "authenticated GitHub Actions check suite disagrees",
    )
    return path, started, suite


def verify_jobs(github, pull, selected, path, started, suite, required):
    jobs = github.pages(f"{path}/jobs?per_page=100", "jobs")
    names = [job["name"] for job in jobs]
    require(
        len(names) == len(required)
        and set(names) == required
        and len({job["id"] for job in jobs}) == len(required),
        "required job missing, duplicated or unexpected in selected attempt",
    )
    result = {}
    for job in jobs:
        job_id = job["id"]
        require(
            positive(job_id)
            and job["run_id"] == selected["id"]
            and job["run_attempt"] == selected["run_attempt"]
            and job["head_sha"] == pull.head
            and successful(job)
            and timestamp(job["started_at"]) >= started,
            f"required job {job['name']} is failed, stale or carried over",
        )
        check = github.document(f"check-runs/{job_id}")
        require(
            check["id"] == job_id
            and check["name"] == job["name"]
            and check["head_sha"] == pull.head
            and check["check_suite"]["id"] == suite["id"]
            and check["app"]["id"] == suite["app"]["id"]
            and check["app"]["slug"] == "github-actions"
            and successful(check)
            and timestamp(check["started_at"]) == timestamp(job["started_at"]),
            f"required job {job['name']} does not match its authenticated check record",
        )
        result[job["name"]] = job_id
    return result


def commit(github, sha):
    node = github.document(f"git/commits/{sha}")
    require(
        node["sha"] == sha and digest(node["tree"]["sha"]),
        "raw commit identity disagrees",
    )
    return node


def tree_entries(github, tree):
    document = github.document(f"git/trees/{tree}?recursive=1")
    require(
        document["sha"] == tree and document["truncated"] is False,
        "incomplete authenticated source tree",
    )
    entries = {item["path"]: item for item in document["tree"]}
    require(
        len(entries) == len(document["tree"]), "duplicate authenticated source path"
    )
    return entries


def gate_controls(entries):
    controls = {}
    for path, entry in entries.items():
        if entry["type"] == "tree":
            continue
        directory, _, name = path.rpartition("/")
        if (
            path.startswith((".github/", "tools/ci/", "packages/aitm-usage/tests/"))
            or path in BASE_FILES.values()
            or directory in CI_ANCESTORS
            and name in CI_CONFIG_NAMES
            or path.startswith("packages/aitm-usage/")
            and name in RUFF_CONFIG_NAMES
        ):
            controls[path] = (entry["mode"], entry["type"], entry["sha"])
    return controls


def regular_blob(entries, path):
    entry = entries.get(path, {})
    require(
        entry.get("type") == "blob"
        and entry.get("mode") in {"100644", "100755"}
        and digest(entry.get("sha")),
        "missing or invalid gate-control blob",
    )
    return entry["sha"]


def blob(github, identity):
    data = github.document(f"git/blobs/{identity}")
    require(
        data["encoding"] == "base64" and data["sha"] == identity,
        "GitHub blob identity disagrees",
    )
    raw = base64.b64decode("".join(data["content"].splitlines()), validate=True)
    blob_id = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    require(
        data["size"] == len(raw) and blob_id == identity,
        "GitHub blob content disagrees",
    )
    return raw


def verify_controls(github, pull, tree, reviewed_tree):
    base_tree = commit(github, pull.base)["tree"]["sha"]
    base = tree_entries(github, base_tree)
    candidate = tree_entries(github, tree)
    changed = gate_controls(base) != gate_controls(candidate)
    require(
        reviewed_tree == tree or reviewed_tree is None and not changed,
        "gate controls changed or disposition is stale; provide the exact reviewed tree",
    )
    required = dict(CONTROLS)
    if VERIFIER in candidate:
        required["verifier"] = VERIFIER
    controls = {key: regular_blob(candidate, path) for key, path in required.items()}
    base_blobs = {
        key: blob(github, regular_blob(base, path)) for key, path in BASE_FILES.items()
    }
    base_policy = decode_json(base_blobs["policy"])
    policy = decode_json(blob(github, controls["policy"])) if changed else base_policy
    for item in (base_policy, policy):
        problem = _policy_error(item)
        require(not problem, f"invalid trusted or reviewed policy: {problem}")
    for key in (
        "pr_jobs",
        "push_jobs",
        "required_tests",
        "required_children",
        "helpers",
    ):
        require(
            set(base_policy[key]) <= set(policy[key]),
            f"reviewed policy weakens existing {key}",
        )
    require(
        policy["optional_skips"].items() <= base_policy["optional_skips"].items()
        and not (set(policy["pr_jobs"]) & FIXED_JOBS),
        "reviewed policy weakens skip rules or overlaps canonical jobs",
    )
    for path in policy["helpers"]:
        regular_blob(candidate, path)
    base_identity = {
        "base": pull.base,
        "tree": base_tree,
        **{name: sha256(raw).hexdigest() for name, raw in base_blobs.items()},
    }
    return policy, controls, base_identity


def read_evidence_archive(data):
    require(0 < len(data) <= MAX_ARCHIVE, "evidence archive exceeds size limit")
    names = {"candidate.json", "attestation.sigstore.json"}
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            members = archive.infolist()
            require(
                len(members) == len(names)
                and {member.orig_filename for member in members} == names,
                "unexpected, missing or duplicate evidence archive member",
            )
            content = {}
            for member in members:
                mode = stat.S_IFMT(member.external_attr >> 16)
                require(
                    mode in (0, stat.S_IFREG) and 0 < member.file_size <= MAX_MEMBER,
                    "unsafe or oversized evidence archive member",
                )
                with archive.open(member) as stream:
                    raw = stream.read(MAX_MEMBER + 1)
                require(
                    0 < len(raw) == member.file_size <= MAX_MEMBER,
                    "evidence archive member length disagrees",
                )
                content[member.orig_filename] = raw
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError, OSError):
        raise Hold("invalid evidence archive") from None
    return content["candidate.json"], content["attestation.sigstore.json"]


def attempt_archive(github, pull, selected):
    run, attempt = selected["id"], selected["run_attempt"]
    artifacts = github.pages(f"actions/runs/{run}/artifacts?per_page=100", "artifacts")
    require(
        len({item["id"] for item in artifacts})
        == len({item["name"] for item in artifacts})
        == len(artifacts),
        "duplicate attempt artifact ID or name",
    )
    current = {}
    for item in artifacts:
        name = re.fullmatch(r"aitm-ci-([a-z]+)-a([1-9][0-9]*)", item["name"])
        require(
            name and name[1] in ARTIFACTS and int(name[2]) <= attempt,
            "unexpected attempt artifact name",
        )
        if int(name[2]) != attempt:
            continue
        link = item["workflow_run"]
        require(
            positive(item["id"])
            and item["expired"] is False
            and link["id"] == run
            and link["head_sha"] == pull.head
            and link["head_branch"] == pull.head_branch
            and link["repository_id"]
            == link["head_repository_id"]
            == pull.repository_id
            and re.fullmatch(r"sha256:[0-9a-f]{64}", item["digest"])
            and positive(item["size_in_bytes"]),
            "attempt artifact custody, digest or expiry disagrees",
        )
        current[name[1]] = item
    require(set(current) == ARTIFACTS, "missing selected attempt artifact")
    final = current["evidence"]
    require(
        final["size_in_bytes"] <= MAX_ARCHIVE, "evidence archive exceeds size limit"
    )
    raw = github.api(f"actions/artifacts/{final['id']}/zip", limit=MAX_ARCHIVE)
    require(
        len(raw) == final["size_in_bytes"]
        and final["digest"] == "sha256:" + sha256(raw).hexdigest(),
        "downloaded archive size or digest disagrees",
    )
    subject, bundle = read_evidence_archive(raw)
    return final, subject, bundle


def verify_certificate(github, pull, selected, started, subject, bundle):
    invocation = (
        f"{github.url}/actions/runs/{selected['id']}/attempts/{selected['run_attempt']}"
    )
    workflow_uri = f"{github.url}/{WORKFLOW}@{pull.merge_ref}"
    results = github.attestation(subject, bundle, pull.merge_ref, pull.merge)
    require(
        isinstance(results, list) and len(results) == 1,
        "expected exactly one verified signature",
    )
    verified = results[0]["verificationResult"]
    claims = {
        "issuer": ISSUER,
        "sourceRepositoryIdentifier": str(pull.repository_id),
        "sourceRepositoryURI": github.url,
        "sourceRepositoryDigest": pull.merge,
        "sourceRepositoryRef": pull.merge_ref,
        "sourceRepositoryVisibilityAtSigning": "public",
        "buildSignerURI": workflow_uri,
        "buildSignerDigest": pull.merge,
        "buildConfigURI": workflow_uri,
        "buildConfigDigest": pull.merge,
        "buildTrigger": "pull_request",
        "runInvocationURI": invocation,
        "runnerEnvironment": "github-hosted",
    }
    cert = verified["signature"]["certificate"]
    for key, expected in claims.items():
        require(cert.get(key) == expected, f"verified certificate {key} disagrees")
    digest_sha = sha256(subject).hexdigest()
    statement = verified["statement"]
    require(
        statement["predicateType"] == PREDICATE
        and statement["subject"]
        == [{"name": "candidate.json", "digest": {"sha256": digest_sha}}],
        "verified statement does not name the exact signed candidate subject",
    )
    times = verified["verifiedTimestamps"]
    require(
        isinstance(times, list)
        and times
        and all(timestamp(item["timestamp"]) >= started for item in times),
        "verified transparency or timestamp evidence missing or predates attempt",
    )
    return invocation, digest_sha


def report_evidence(subject, pull, selected, tree, policy, controls, base_identity):
    report = decode_json(subject)
    require(report["schema"] == "aitm.ci-candidate/v2", "candidate schema disagrees")
    expected = {
        "pr": pull.number,
        "head": pull.head,
        "base": pull.base,
        "tested": pull.merge,
        "tree": tree,
        "run": selected["id"],
        "attempt": selected["run_attempt"],
    }
    for key, value in expected.items():
        require(
            type(report[key]) is type(value) and report[key] == value,
            f"candidate {key} disagrees",
        )
    require(
        report["controls"] == controls,
        "candidate control blobs disagree with tested tree",
    )
    lanes = {name: "success" for name in policy["pr_jobs"]}
    require(report["jobs"] == lanes, "candidate lane outcomes disagree")
    checkouts = {name: pull.merge for name in lanes}
    checkouts.update({"collector": pull.merge, "python-base": pull.base})
    require(report["checkouts"] == checkouts, "candidate checkout evidence disagrees")
    require(
        all(
            report["base_identity"][key] == value
            for key, value in base_identity.items()
        ),
        "trusted base evidence disagrees with authenticated source",
    )
    require(
        isinstance(report["base_identity"]["image"], str)
        and report["base_identity"]["image"]
        and report["base_identity"]["runtime"] == "3.13.9",
        "trusted base runner or runtime evidence missing",
    )
    platform = report["platform"]
    require(
        (platform["os"], platform["filesystem"]) == ("Darwin", "apfs")
        and all(
            isinstance(platform[key], str) and platform[key]
            for key in ("image", "xcode")
        ),
        "required Darwin APFS evidence missing",
    )
    require(digest(report["wheel"], 64), "candidate wheel digest missing")
    for key in ("inventory", "source_inventory", "baseline"):
        require(digest(report[key], 64), f"candidate {key} digest missing")
    result = report["result"]
    require(
        result["passed"] is True
        and result["failures"] == []
        and positive(result["tests"])
        and positive(result["baseline_tests"])
        and result["tests"] >= result["baseline_tests"],
        "candidate Python evidence is not passing",
    )
    coverage = result["coverage"]
    require(
        set(coverage) == {"product", "helpers"}, "candidate coverage scope disagrees"
    )
    for scope, counts in coverage.items():
        covered, total = counts["covered_lines"], counts["num_statements"]
        require(
            type(covered) is int
            and positive(total)
            and 0 <= covered <= total
            and 100 * covered >= policy["line_floor"] * total,
            f"candidate {scope} coverage missing, invalid or below 90%",
        )
    children = report["children"]
    require(
        len(children) == len(policy["required_children"])
        and {item["label"] for item in children} == set(policy["required_children"])
        and len({item["pid"] for item in children}) == len(children)
        and all(
            positive(item["pid"])
            and type(item["returncode"]) is int
            and item["returncode"] == 0
            and positive(item["covered_lines"])
            for item in children
        ),
        "required child evidence is incomplete",
    )
    return coverage


def verify_pr(github, number, target, checkout, *, reviewed_tree=None):
    """Return a dated receipt or raise Hold without changing GitHub state."""
    require(
        positive(number) and branch_name(target), "invalid PR number or declared target"
    )
    require(
        reviewed_tree is None or digest(reviewed_tree), "invalid reviewed tree digest"
    )
    try:
        pull = live_pull(github, number, target)
        require(
            checkout == pull.base, "trusted checkout is not the current live target"
        )
        workflow = canonical_workflow(github)
        selected = newest_run(github, pull, workflow)
        path, started, suite = read_attempt(github, pull, workflow, selected)
        tested = commit(github, pull.merge)
        require(
            [entry["sha"] for entry in tested["parents"]] == [pull.base, pull.head],
            "tested merge has incorrect ordered base/head parents",
        )
        tree = tested["tree"]["sha"]
        policy, controls, base_identity = verify_controls(
            github, pull, tree, reviewed_tree
        )
        jobs = verify_jobs(
            github,
            pull,
            selected,
            path,
            started,
            suite,
            set(policy["pr_jobs"]) | FIXED_JOBS,
        )
        artifact, subject, bundle = attempt_archive(github, pull, selected)
        invocation, subject_digest = verify_certificate(
            github, pull, selected, started, subject, bundle
        )
        coverage = report_evidence(
            subject, pull, selected, tree, policy, controls, base_identity
        )
        require(
            live_pull(github, number, target) == pull
            and canonical_workflow(github) == workflow
            and newest_run(github, pull, workflow) == selected,
            "live candidate or canonical attempt changed during verification",
        )
    except Hold:
        raise
    except (KeyError, TypeError, ValueError, IndexError):
        raise Hold(
            "malformed or incomplete GitHub or signed candidate evidence"
        ) from None
    return {
        "status": "pass",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "repository": github.repo,
        "repository_id": pull.repository_id,
        "pr": number,
        "target": target,
        "head": pull.head,
        "base": pull.base,
        "tested": pull.merge,
        "tree": tree,
        "workflow_id": workflow,
        "run_id": selected["id"],
        "run_attempt": selected["run_attempt"],
        "run": invocation,
        "artifact_id": artifact["id"],
        "archive_digest": artifact["digest"],
        "subject_digest": subject_digest,
        "jobs": jobs,
        "controls": controls,
        "reviewed_tree": reviewed_tree,
        "coverage": coverage,
    }


def checked_out_base(root, executable):
    git = ["git", "--no-optional-locks", "-C", str(root)]
    require(
        not run_bounded(
            [*git, "status", "--porcelain", "--untracked-files=no"], MAX_MEMBER
        ),
        "use a clean trusted target checkout",
    )
    head = run_bounded([*git, "rev-parse", "HEAD"], 4096).decode().strip()
    require(digest(head), "trusted checkout has an invalid HEAD")
    entry = (
        run_bounded(
            [
                *git,
                "ls-tree",
                "--format=%(objectmode) %(objectname)",
                head,
                "--",
                VERIFIER,
            ],
            4096,
        )
        .decode()
        .split()
    )
    require(
        executable == root / VERIFIER
        and not executable.is_symlink()
        and len(entry) == 2
        and entry[0] in {"100644", "100755"}
        and digest(entry[1]),
        "run the delivered verifier from the trusted checkout",
    )
    actual = run_bounded(
        [*git, "hash-object", "--no-filters", "--", str(executable)], 4096
    )
    require(
        actual.decode().strip() == entry[1],
        "executing verifier bytes disagree with trusted HEAD",
    )
    return head


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--reviewed-tree",
        help="exact independently reviewed tree with owner disposition",
    )
    args = parser.parse_args(argv)
    try:
        github = GitHub(args.repo)
        executable = Path(__file__).absolute()
        checkout = checked_out_base(executable.parents[2], executable)
        receipt = verify_pr(
            github,
            args.pr,
            args.target,
            checkout,
            reviewed_tree=args.reviewed_tree,
        )
    except Hold as exc:
        receipt = {
            "status": "hold",
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "reason": str(exc),
        }
    args.output.write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
