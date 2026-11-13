"""Read canonical trunk push CI for advisory use."""

import argparse
import json
import stat
import sys
from collections import Counter
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import python_gate
from verify_pr import (
    WORKFLOW,
    GitHub,
    Hold,
    blob,
    canonical_workflow,
    commit,
    decode_json,
    digest,
    positive,
    regular_blob,
    require,
    successful,
    timestamp,
    tree_entries,
)

REPO = "kburson/aitm"
REPOSITORY_ID = 1450406435
WORKFLOW_ID = 412848571
TARGET = "trunk"
REQUIRED = {"python", "quality", "file-checks", "collect-evidence"}
PUSH_SKIPS = {"python-base", "aitm-ci"}
FAILURES = {"failure", "timed_out", "action_required"}
MAX_ARCHIVE = 4 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
ARTIFACT_MEMBERS = {
    "capability.json",
    "children.json",
    "helper-coverage.json",
    "product-coverage.json",
    "product-inventory.json",
    "product-junit.xml",
    "pytest.json",
    "timings.json",
    "wheel.json",
}
RUN_FIELDS = (
    "id",
    "run_number",
    "run_attempt",
    "check_suite_id",
    "run_started_at",
    "status",
    "conclusion",
)
JOB_FIELDS = (
    "id",
    "name",
    "head_sha",
    "status",
    "conclusion",
    "started_at",
    "completed_at",
)
EVIDENCE_ERRORS = (ValueError, KeyError, TypeError, OSError)


def live_target(github):
    repo = github.document("")
    require(
        repo["id"] == REPOSITORY_ID and repo["full_name"] == REPO,
        "canonical repository identity disagrees",
    )
    require(
        canonical_workflow(github) == WORKFLOW_ID, "canonical workflow ID disagrees"
    )
    branch = github.document(f"branches/{TARGET}")
    sha = branch["commit"]["sha"]
    require(
        branch["name"] == TARGET and branch["protected"] is True and digest(sha),
        "canonical protected branch is unavailable",
    )
    return sha


def run_identity(run, sha):
    require(
        run["path"] == WORKFLOW
        and run["workflow_id"] == WORKFLOW_ID
        and run["event"] == "push"
        and run["head_branch"] == TARGET
        and run["head_sha"] == sha
        and run["repository"]["id"] == run["head_repository"]["id"] == REPOSITORY_ID
        and all(positive(run[key]) for key in RUN_FIELDS[:4])
        and timestamp(run["run_started_at"]) >= timestamp(run["created_at"]),
        "canonical run identity disagrees",
    )


def run_fields(run):
    return tuple(run[key] for key in RUN_FIELDS)


def latest_run(github, sha):
    runs = github.pages(
        f"actions/workflows/{WORKFLOW_ID}/runs?branch={TARGET}&event=push&head_sha={sha}&per_page=100",
        "workflow_runs",
    )
    require(len(runs) < 1000, "canonical run search reached the provider limit")
    for run in runs:
        run_identity(run, sha)
    for key in ("id", "run_number"):
        require(len({run[key] for run in runs}) == len(runs), "duplicate canonical run")
    return max(runs, key=lambda run: run["run_number"], default=None)


def check_suite(github, run):
    suite = github.document(f"check-suites/{run['check_suite_id']}")
    require(
        suite["id"] == run["check_suite_id"]
        and suite["head_sha"] == run["head_sha"]
        and suite["head_branch"] == TARGET
        and suite["app"]["slug"] == "github-actions"
        and positive(suite["app"]["id"]),
        "canonical Actions check suite identity disagrees",
    )
    return suite


def authenticate_job(github, job, run, suite, id_counts):
    job_id = job["id"]
    require(
        positive(job_id)
        and id_counts[job_id] == 1
        and job["head_sha"] == run["head_sha"]
        and job["run_id"] == run["id"]
        and job["run_attempt"] == run["run_attempt"],
        "attempt job identity disagrees",
    )
    if job["status"] == "completed":
        require(
            timestamp(job["completed_at"])
            >= timestamp(job["started_at"])
            >= timestamp(run["run_started_at"]),
            "attempt job timestamps disagree",
        )
    check = github.document(f"check-runs/{job_id}")
    require(
        check["check_suite"]["id"] == suite["id"]
        and check["app"] == suite["app"]
        and all(check[key] == job[key] for key in JOB_FIELDS),
        "attempt job and Actions check disagree",
    )


def check_jobs(github, route, run, suite, gaps, failures):
    listed = github.pages(f"{route}/jobs?per_page=100", "jobs")
    valid = [
        job
        for job in listed
        if isinstance(job, dict)
        and positive(job.get("id"))
        and isinstance(job.get("name"), str)
    ]
    if len(valid) != len(listed):
        gaps.append("invalid push job record")
    id_counts = Counter(job["id"] for job in valid)
    jobs = {}
    if any(job.get("name") not in REQUIRED | PUSH_SKIPS for job in valid):
        gaps.append("unexpected push job")
    for name in sorted(REQUIRED):
        matches = [job for job in valid if job["name"] == name]
        if len(matches) != 1:
            gaps.append(f"{name}:missing-or-duplicate")
            continue
        job = matches[0]
        try:
            authenticate_job(github, job, run, suite, id_counts)
        except EVIDENCE_ERRORS:
            gaps.append(f"{name}:unverified")
            continue
        jobs[name] = job
        if job["status"] == "completed" and job["conclusion"] in FAILURES:
            failures.append(f"{name}:{job['conclusion']}")
        elif not successful(job):
            gaps.append(f"{name}:{job['conclusion'] or job['status']}")
    return jobs


def read_push_archive(raw):
    require(0 < len(raw) <= MAX_ARCHIVE, "invalid push archive length")
    try:
        with ZipFile(BytesIO(raw)) as zipped:
            members = zipped.infolist()
            require(
                len(members) == len(ARTIFACT_MEMBERS)
                and {member.orig_filename for member in members} == ARTIFACT_MEMBERS,
                "unexpected, missing or duplicate push archive members",
            )
            result = {}
            for member in members:
                require(
                    stat.S_IFMT(member.external_attr >> 16) in (0, stat.S_IFREG)
                    and 0 < member.file_size <= MAX_MEMBER,
                    "unsafe or oversized push archive member",
                )
                if member.filename.endswith(".json"):
                    with zipped.open(member) as stream:
                        data = stream.read(MAX_MEMBER + 1)
                    require(
                        len(data) == member.file_size,
                        "push archive member length disagrees",
                    )
                    result[member.filename] = decode_json(data)
            return result
    except (BadZipFile, RuntimeError, NotImplementedError, EOFError):
        raise Hold("invalid push evidence archive") from None


def replay_policy(github, sha, docs):
    tree = commit(github, sha)["tree"]["sha"]
    entries = tree_entries(github, tree)
    root = Path(__file__).resolve().parents[2]
    controls = {}
    for path in (WORKFLOW, "tools/ci/python_gate.py", "tools/ci/policy.json"):
        controls[path] = regular_blob(entries, path)
        raw = blob(github, controls[path])
        require(
            raw == (root / path).read_bytes(),
            "trusted push control differs from checkout",
        )
        if path.endswith("policy.json"):
            policy = decode_json(raw)
    require(
        set(policy["push_jobs"]) == REQUIRED - {"collect-evidence"},
        "trusted push jobs differ from intake contract",
    )
    prefix = "packages/aitm-usage/"
    inventory = sorted(
        path.removeprefix(prefix)
        for path in entries
        if path.startswith(prefix + "src/aitm_usage/") and path.endswith(".py")
    )
    require(
        inventory and inventory == sorted(docs["product-inventory.json"]),
        "push product inventory disagrees with protected tree",
    )
    require(digest(docs["wheel.json"]["digest"], 64), "invalid wheel evidence")
    result = python_gate.evaluate(
        policy,
        docs["pytest.json"],
        docs["product-coverage.json"],
        docs["product-inventory.json"],
        docs["helper-coverage.json"],
        docs["children.json"],
        docs["capability.json"],
        mode="push",
    )
    require(result["passed"], "trusted #103 push policy replay failed")
    return {"tree": tree, "controls": controls, "policy_result": result}


def verify_push_artifact(github, run, jobs):
    name = f"aitm-ci-python-a{run['run_attempt']}"
    artifacts = github.pages(
        f"actions/runs/{run['id']}/artifacts?per_page=100", "artifacts"
    )
    matches = [item for item in artifacts if item["name"] == name]
    require(
        len(matches) == 1, "missing or duplicate Python artifact for current attempt"
    )
    item = matches[0]
    link = item["workflow_run"]
    size = item["size_in_bytes"]
    require(
        positive(item["id"])
        and item["expired"] is False
        and link["id"] == run["id"]
        and link["head_sha"] == run["head_sha"]
        and link["head_branch"] == TARGET
        and link["repository_id"] == link["head_repository_id"] == REPOSITORY_ID
        and positive(size)
        and size <= MAX_ARCHIVE
        and timestamp(jobs["collect-evidence"]["completed_at"])
        >= timestamp(item["created_at"])
        >= timestamp(jobs["python"]["started_at"]),
        "current attempt Python artifact custody disagrees",
    )
    raw = github.api(f"actions/artifacts/{item['id']}/zip", limit=MAX_ARCHIVE)
    require(
        len(raw) == size and item["digest"] == "sha256:" + sha256(raw).hexdigest(),
        "push archive digest or size disagrees",
    )
    result = replay_policy(github, run["head_sha"], read_push_archive(raw))
    return {"id": item["id"], "digest": item["digest"], **result}


def observe(github, *, expected=None, shadow=False):
    """Read one current decision through a provider-owned transport."""
    sha = live_target(github)
    run = latest_run(github, sha)
    outcome = {
        "schema": "aitm.ci-advisory/v1",
        "repository_id": REPOSITORY_ID,
        "workflow_id": WORKFLOW_ID,
        "target": TARGET,
        "provenance": "shadow" if shadow else "live",
        "sha": sha,
        "status": "pending",
        "current_verified": False,
        "failures": [],
        "gaps": [],
        "jobs": {},
        "artifact": None,
    }
    gaps, failures = outcome["gaps"], outcome["failures"]
    if run is None:
        outcome["status"] = "stale" if expected else "pending"
        gaps.append("no run for live trunk")
        return outcome
    identity = (run["id"], run["run_attempt"])
    outcome.update(
        run_id=identity[0],
        attempt=identity[1],
        run_number=run["run_number"],
        started_at=run["run_started_at"],
    )
    if expected is not None and expected != identity:
        outcome["status"] = "stale"
        gaps.append("requested run or attempt is no longer current")
        return outcome
    route = f"actions/runs/{identity[0]}/attempts/{identity[1]}"
    attempt = github.document(route)
    run_identity(attempt, sha)
    require(run_fields(attempt) == run_fields(run), "selected run attempt changed")
    suite = check_suite(github, run)
    jobs = check_jobs(github, route, run, suite, gaps, failures)
    outcome["jobs"] = {name: job["id"] for name, job in jobs.items()}
    if successful(attempt) and successful(suite) and not gaps:
        try:
            outcome["artifact"] = verify_push_artifact(github, attempt, jobs)
        except Hold as exc:
            gaps.append(str(exc))
        except EVIDENCE_ERRORS:
            gaps.append("invalid push artifact evidence")
    elif attempt["status"] == "completed":
        if not successful(attempt):
            gaps.append(f"workflow:{attempt['conclusion']}")
        if not successful(suite):
            gaps.append(f"check-suite:{suite['conclusion'] or suite['status']}")
    try:
        same_target = live_target(github) == sha
        current = latest_run(github, sha) if same_target else None
        same_attempt = current is not None and run_fields(current) == run_fields(run)
        if same_attempt:
            final_attempt = github.document(route)
            run_identity(final_attempt, sha)
            same_attempt = run_fields(final_attempt) == run_fields(attempt)
    except EVIDENCE_ERRORS:
        gaps.append("current target and attempt could not be reverified")
        outcome["status"] = "red" if failures else "incomplete"
    else:
        if not same_attempt:
            outcome["status"] = "stale"
            gaps.append("protected target or attempt changed during readback")
        else:
            outcome["current_verified"] = True
            if failures:
                outcome["status"] = "red"
            elif attempt["status"] == "completed":
                outcome["status"] = "green" if outcome["artifact"] else "incomplete"
    return outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", metavar=("RUN", "ATTEMPT"), type=int, nargs=2)
    args = parser.parse_args(argv)
    if args.expect and not all(map(positive, args.expect)):
        parser.error("run and attempt must be positive")
    try:
        result = observe(
            GitHub(REPO), expected=tuple(args.expect) if args.expect else None
        )
    except Hold as exc:
        print(f"advisory intake unavailable: {exc}", file=sys.stderr)
        return 2
    except EVIDENCE_ERRORS:
        print("advisory intake unavailable: invalid provider evidence", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
