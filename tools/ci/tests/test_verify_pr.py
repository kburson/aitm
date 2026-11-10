import gzip
import json
import sys
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZipInfo

import pytest
from verify_pr import (
    VERIFIER,
    GitHub,
    Hold,
    checked_out_base,
    main,
    read_evidence_archive,
    run_bounded,
    verify_pr,
)

FIXTURES = Path(__file__).parent / "fixtures" / "verify-pr"
REPO = "kburson/aitm"
REPO_ID = 1450406435
PR = 108
TARGET = "ci-proof/103-integration"
BASE = "afbaf6e93ab1ad57a312b06a75b0d09029b9409a"
HEAD = "f780f875986e95bd654c0553c574c336f728a4fa"
MERGE = "0ab2aebd8e4ab78d93a1f010f84c5e811d714733"
RUN = 42821747864
SUITE = 115969504499
RUN_LIST = (
    f"actions/workflows/412848571/runs?head_sha={HEAD}&event=pull_request&per_page=100"
)
ATTEMPT = f"actions/runs/{RUN}/attempts/1"
JOBS = f"{ATTEMPT}/jobs?per_page=100"
ARTIFACTS = f"actions/runs/{RUN}/artifacts?per_page=100"
ARCHIVE = "actions/artifacts/13766658345/zip"
WORKFLOW = "actions/workflows/ci.yml"


class FixtureGitHub(GitHub):
    def __init__(self):
        super().__init__(REPO)
        self.documents = json.loads(
            gzip.decompress((FIXTURES / "proof-api.json.gz").read_bytes())
        )
        self.raw_archive = (FIXTURES / "proof-archive.zip").read_bytes()
        self.verified = None

    def api(self, endpoint, *, paginate=False, limit=None):
        if endpoint == ARCHIVE:
            return self.raw_archive
        document = self.documents.get(endpoint)
        if document is None:
            raise Hold(f"missing fixture API {endpoint}")
        assert isinstance(document, list) is paginate
        return json.dumps(document).encode()

    def command(self, args, maximum):
        if args[:2] == ["attestation", "verify"]:
            if self.verified is not None:
                return json.dumps(self.verified).encode()
            args = [
                *args,
                "--custom-trusted-root",
                str(FIXTURES / "public-trusted-root.jsonl"),
            ]
        return super().command(args, maximum)

    def check(self, *, checkout=BASE, reviewed_tree=None):
        return verify_pr(self, PR, TARGET, checkout, reviewed_tree=reviewed_tree)


def rewritten_archive(entries):
    buf = BytesIO()
    with ZipFile(buf, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return buf.getvalue()


def with_archive(client, raw):
    client.raw_archive = raw
    artifact = next(
        item
        for item in client.documents[ARTIFACTS][0]["artifacts"]
        if item["name"] == "aitm-ci-evidence-a1"
    )
    artifact.update(size_in_bytes=len(raw), digest="sha256:" + sha256(raw).hexdigest())


def replace_policy(client, transform):
    base_commit = client.documents[f"git/commits/{BASE}"]
    base_tree = client.documents[f"git/trees/{base_commit['tree']['sha']}?recursive=1"]
    base_entry = next(
        x for x in base_tree["tree"] if x["path"] == "tools/ci/policy.json"
    )
    raw = client.documents[f"git/blobs/{base_entry['sha']}"]
    import base64

    policy = json.loads(base64.b64decode(raw["content"]))
    transform(policy)
    contents = json.dumps(policy).encode()
    object_id = sha1(f"blob {len(contents)}\0".encode() + contents).hexdigest()
    client.documents[f"git/blobs/{object_id}"] = {
        "encoding": "base64",
        "sha": object_id,
        "size": len(contents),
        "content": base64.b64encode(contents).decode(),
    }
    commit = client.documents[f"git/commits/{MERGE}"]
    tree = client.documents[f"git/trees/{commit['tree']['sha']}?recursive=1"]
    candidate_entry = next(
        x for x in tree["tree"] if x["path"] == "tools/ci/policy.json"
    )
    candidate_entry["sha"] = object_id
    return tree["sha"], object_id


@pytest.fixture
def client():
    return FixtureGitHub()


@pytest.fixture(scope="module")
def verified_signature():
    client = FixtureGitHub()
    subject, bundle = read_evidence_archive(client.raw_archive)
    return client.attestation(subject, bundle, f"refs/pull/{PR}/merge", MERGE)


def test_authentic_canonical_proof_passes_with_offline_signature(client):
    result = client.check()
    assert result["run_id"] == RUN
    assert result["run_attempt"] == 1
    assert result["head"] == HEAD
    assert result["base"] == BASE
    assert result["tested"] == MERGE
    assert result["coverage"]["product"]["covered_lines"] > 0
    assert result["artifact_id"] == 13766658345
    assert result["verified_at"].endswith("+00:00")


def test_authentic_bootstrap_archive_verifies_as_its_own_signature(client):
    subject, bundle = read_evidence_archive(
        (FIXTURES / "bootstrap-archive.zip").read_bytes()
    )
    result = client.attestation(
        subject,
        bundle,
        "refs/pull/107/merge",
        "96ab651324a28198d58b8c75c8448d07763fa2a9",
    )
    certificate = result[0]["verificationResult"]["signature"]["certificate"]
    assert certificate["runInvocationURI"].endswith("/42819951099/attempts/1")
    assert certificate["sourceRepositoryIdentifier"] == str(REPO_ID)


@pytest.mark.parametrize(
    ("endpoint", "path", "value", "reason"),
    [
        ("", ("visibility",), "private", "public"),
        ("pulls/108", ("number",), 109, "PR identity"),
        ("pulls/108", ("head", "repo", "id"), 999, "same-repository"),
        ("pulls/108", ("base", "ref"), "trunk", "target"),
        ("pulls/108", ("head", "sha"), "f" * 40, "fixture API"),
        (f"git/ref/heads/{TARGET}", ("object", "sha"), "f" * 40, "target"),
        ("git/ref/pull/108/merge", ("object", "sha"), "f" * 40, "merge ref"),
        (WORKFLOW, ("path",), ".github/workflows/lookalike.yml", "canonical workflow"),
        (RUN_LIST, (0, "workflow_runs", 0, "pull_requests"), [], "association"),
        (RUN_LIST, (0, "workflow_runs", 0, "workflow_id"), 999, "canonical run"),
        (RUN_LIST, (0, "workflow_runs", 0, "repository", "id"), 999, "canonical run"),
        (ATTEMPT, ("run_attempt",), 2, "selected attempt"),
        (ATTEMPT, ("status",), "in_progress", "selected attempt"),
        (f"check-suites/{SUITE}", ("app", "slug"), "lookalike", "check suite"),
        (
            f"git/commits/{MERGE}",
            ("parents",),
            [{"sha": HEAD}, {"sha": BASE}],
            "ordered",
        ),
        (JOBS, (0, "jobs", 0, "conclusion"), "skipped", "required job"),
        (JOBS, (0, "jobs", 0, "conclusion"), "cancelled", "required job"),
        (JOBS, (0, "jobs", 0, "run_attempt"), 2, "required job"),
        (JOBS, (0, "jobs", 0, "started_at"), "2020-01-01T00:00:00Z", "required job"),
        (JOBS, (0, "jobs", 0, "name"), "unknown-job", "required job"),
        (
            ARTIFACTS,
            (0, "artifacts", 0, "name"),
            "aitm-ci-unexpected-a1",
            "artifact name",
        ),
        (ARTIFACTS, (0, "artifacts", 2, "expired"), True, "artifact custody"),
        (ARTIFACTS, (0, "artifacts", 2, "workflow_run", "id"), 999, "artifact custody"),
        (ARTIFACTS, (0, "artifacts", 2, "digest"), "sha256:" + "1" * 64, "archive"),
    ],
)
def test_fails_closed_on_one_bad_provider_field(client, endpoint, path, value, reason):
    data = client.documents[endpoint]
    for key in path[:-1]:
        data = data[key]
    data[path[-1]] = value
    with pytest.raises(Hold, match=reason):
        client.check()


@pytest.mark.parametrize("operation", ["remove", "duplicate"])
def test_missing_or_duplicate_required_attempt_jobs(client, operation):
    page = client.documents[JOBS][0]
    if operation == "remove":
        page["jobs"].pop()
        page["total_count"] -= 1
    else:
        page["jobs"].append(page["jobs"][0].copy())
        page["total_count"] += 1
    with pytest.raises(Hold, match="job"):
        client.check()


@pytest.mark.parametrize("operation", ["remove", "duplicate"])
def test_missing_or_duplicate_final_attempt_artifact(client, operation):
    page = client.documents[ARTIFACTS][0]
    final = next(
        item for item in page["artifacts"] if item["name"] == "aitm-ci-evidence-a1"
    )
    if operation == "remove":
        page["artifacts"].remove(final)
        page["total_count"] -= 1
    else:
        page["artifacts"].append(dict(final, id=final["id"] + 1))
        page["total_count"] += 1
    with pytest.raises(
        Hold, match="selected attempt artifact|duplicate attempt artifact"
    ):
        client.check()


def test_incomplete_pagination_refuses_ambiguous_inventory(client):
    client.documents[RUN_LIST][0]["total_count"] += 1
    with pytest.raises(Hold, match="incomplete"):
        client.check()


def test_newer_pending_run_cannot_fall_back_to_signed_pass(client):
    page = client.documents[RUN_LIST][0]
    newer = dict(page["workflow_runs"][0], id=RUN + 1, status="queued", conclusion=None)
    page["workflow_runs"].append(newer)
    page["total_count"] += 1
    with pytest.raises(Hold, match="selected attempt"):
        client.check()


def test_older_run_in_second_page_does_not_replace_current(client):
    page = client.documents[RUN_LIST][0]
    older = dict(
        page["workflow_runs"][0], id=RUN - 1, created_at="2026-01-01T00:00:00Z"
    )
    page["total_count"] = 2
    client.documents[RUN_LIST].append({"total_count": 2, "workflow_runs": [older]})
    assert client.check()["run_id"] == RUN


def test_unchanged_candidate_recheck_detects_movement(client, verified_signature):
    read = client.api

    def move_on_second_read(endpoint, **kwargs):
        if endpoint == "pulls/108" and client.verified is not None:
            client.documents[endpoint]["merge_commit_sha"] = "f" * 40
        return read(endpoint, **kwargs)

    def verify_then_move(subject, bundle, ref, merge):
        client.verified = verified_signature
        return verified_signature

    client.api = move_on_second_read
    client.attestation = verify_then_move
    with pytest.raises(Hold, match="merge ref"):
        client.check()


@pytest.mark.parametrize(
    "claim",
    [
        "issuer",
        "sourceRepositoryIdentifier",
        "buildSignerURI",
        "buildSignerDigest",
        "buildConfigURI",
        "buildConfigDigest",
        "buildTrigger",
        "sourceRepositoryRef",
        "sourceRepositoryDigest",
        "runInvocationURI",
        "sourceRepositoryURI",
        "runnerEnvironment",
        "sourceRepositoryVisibilityAtSigning",
    ],
)
def test_wrong_cryptographically_verified_claim_holds(
    client, verified_signature, claim
):
    # Model the independently verified certificate boundary one claim at a time.
    client.verified = json.loads(json.dumps(verified_signature))
    cert = client.verified[0]["verificationResult"]["signature"]["certificate"]
    cert[claim] = "wrong"
    with pytest.raises(Hold, match=claim):
        client.check()


def override_signed_report(client, verified_signature, transform):
    # Exercise post-verification report policy with a test-only verified output.
    subject, bundle = read_evidence_archive(client.raw_archive)
    report = json.loads(subject)
    transform(report)
    subject = json.dumps(report).encode()
    with_archive(
        client,
        rewritten_archive(
            [
                ("candidate.json", subject),
                ("attestation.sigstore.json", bundle),
            ]
        ),
    )
    client.verified = json.loads(json.dumps(verified_signature))
    statement = client.verified[0]["verificationResult"]["statement"]
    statement["subject"][0]["digest"]["sha256"] = sha256(subject).hexdigest()


@pytest.mark.parametrize(
    ("path", "value", "reason"),
    [
        (("schema",), "aitm.ci-candidate/v1", "schema"),
        (("head",), "f" * 40, "candidate head"),
        (("base",), "f" * 40, "candidate base"),
        (("tested",), "f" * 40, "candidate tested"),
        (("tree",), "f" * 40, "candidate tree"),
        (("run",), RUN + 1, "candidate run"),
        (("attempt",), 2, "candidate attempt"),
        (("pr",), 107, "candidate pr"),
        (("controls", "workflow"), "f" * 40, "control"),
        (("checkouts", "python"), "f" * 40, "checkout"),
        (("jobs", "python"), "skipped", "lane"),
        (("result", "passed"), False, "Python evidence"),
        (
            ("result", "coverage", "product"),
            {"covered_lines": 179, "num_statements": 200},
            "product coverage",
        ),
        (
            ("result", "coverage", "helpers"),
            {"covered_lines": 179, "num_statements": 200},
            "helpers coverage",
        ),
        (("base_identity", "observer"), "f" * 64, "trusted base"),
        (("children", 0, "covered_lines"), 0, "child"),
        (("platform", "filesystem"), "other", "Darwin"),
        (("wheel",), "invalid", "wheel"),
    ],
)
def test_signed_payload_claims_do_not_override_trusted_evidence(
    client, verified_signature, path, value, reason
):
    def mutate(report):
        branch = report
        for key in path[:-1]:
            branch = branch[key]
        branch[path[-1]] = value

    override_signed_report(client, verified_signature, mutate)
    with pytest.raises(Hold, match=reason):
        client.check()


def test_both_unrounded_coverage_floors_accept_exactly_ninety(
    client, verified_signature
):
    def mutate(report):
        report["result"]["coverage"] = {
            "product": {"covered_lines": 9000, "num_statements": 10000},
            "helpers": {"covered_lines": 9, "num_statements": 10},
        }

    override_signed_report(client, verified_signature, mutate)
    assert client.check()["coverage"]["helpers"]["covered_lines"] == 9


def test_gate_controls_require_matching_reviewed_tree_and_keep_existing_jobs(client):
    tree, _ = replace_policy(client, lambda p: p["pr_jobs"].remove("quality"))
    with pytest.raises(Hold, match="reviewed tree"):
        client.check()
    with pytest.raises(Hold, match="weakens.*pr_jobs"):
        client.check(reviewed_tree=tree)


@pytest.mark.parametrize(
    "path",
    [
        "packages/aitm-usage/conftest.py",
        "tools/conftest.py",
        "packages/aitm-usage/.coveragerc",
        "packages/aitm-usage/sitecustomize.py",
    ],
)
def test_active_ci_hook_additions_require_review(client, path):
    commit = client.documents[f"git/commits/{MERGE}"]
    tree = client.documents[f"git/trees/{commit['tree']['sha']}?recursive=1"]
    tree["tree"].append(
        {"path": path, "mode": "100644", "type": "blob", "sha": "1" * 40}
    )
    with pytest.raises(Hold, match="reviewed tree"):
        client.check()


def test_reviewed_additive_policy_requires_the_new_job(client):
    tree, _ = replace_policy(client, lambda p: p["pr_jobs"].append("file-quality"))
    with pytest.raises(Hold, match="required job"):
        client.check(reviewed_tree=tree)


def test_reviewed_candidate_binds_added_verifier_blob(client, verified_signature):
    tree_id, policy_id = replace_policy(client, lambda p: p["helpers"].append(VERIFIER))
    tree = client.documents[f"git/trees/{tree_id}?recursive=1"]
    verifier_id = "7" * 40
    tree["tree"].append(
        {"path": VERIFIER, "mode": "100644", "type": "blob", "sha": verifier_id}
    )

    def add_signed_controls(report):
        report["controls"].update(policy=policy_id, verifier=verifier_id)

    with pytest.raises(Hold, match="control blobs"):
        client.check(reviewed_tree=tree_id)
    override_signed_report(client, verified_signature, add_signed_controls)
    assert client.check(reviewed_tree=tree_id)["controls"]["verifier"] == verifier_id


def test_archive_rejects_tampered_subject_with_real_signature(client):
    subject, bundle = read_evidence_archive(client.raw_archive)
    with_archive(
        client,
        rewritten_archive(
            [
                ("candidate.json", subject + b" "),
                ("attestation.sigstore.json", bundle),
            ]
        ),
    )
    with pytest.raises(Hold, match="signature"):
        client.check()


@pytest.mark.parametrize(
    "name",
    [
        "../candidate.json",
        "unexpected.json",
        "candidate.json/",
        "candidate.json\x00suffix",
    ],
)
def test_archive_rejects_nonexact_member_names(name):
    raw = rewritten_archive([(name, b"{}"), ("attestation.sigstore.json", b"{}")])
    if "\x00" in name:
        # zipfile normalizes names on write. Mutate both filename records without
        # changing their declared byte lengths to reproduce the raw NUL form.
        raw = rewritten_archive(
            [("candidate.jsonZsuffix", b"{}"), ("attestation.sigstore.json", b"{}")]
        ).replace(b"candidate.jsonZsuffix", b"candidate.json\x00suffix")
    with pytest.raises(Hold, match="archive member"):
        read_evidence_archive(raw)


def test_archive_rejects_symlink_and_overlarge_members():
    link = ZipInfo("candidate.json")
    link.create_system = 3
    link.external_attr = 0o120777 << 16
    for member in [(link, b"target"), ("candidate.json", b"x" * (2**20 + 1))]:
        raw = rewritten_archive([member, ("attestation.sigstore.json", b"{}")])
        with pytest.raises(Hold, match="archive member"):
            read_evidence_archive(raw)


def test_archive_rejects_malformed_zip():
    with pytest.raises(Hold, match="archive"):
        read_evidence_archive(b"not a zip archive")


def test_bounded_command_rejects_overlarge_output_and_failure():
    assert run_bounded([sys.executable, "-c", "print('abc')"], 4) == b"abc\n"
    with pytest.raises(Hold, match="limit"):
        run_bounded([sys.executable, "-c", "print('abcd')"], 4)
    with pytest.raises(Hold, match="command"):
        run_bounded([sys.executable, "-c", "raise SystemExit(1)"], 4)


@pytest.fixture
def local_checkout(tmp_path):
    import subprocess

    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args])

    def commit():
        git("add", "--all")
        git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "fixture",
        )
        return git("rev-parse", "HEAD").decode().strip()

    git("init", "-q")
    tracked = tmp_path / "tracked"
    tracked.write_text("initial")
    executable = tmp_path / VERIFIER
    executable.parent.mkdir(parents=True)
    return git, commit, tracked, executable


def test_dirty_trusted_checkout_is_refused(tmp_path, local_checkout):
    _, commit, tracked, executable = local_checkout
    executable.write_text("delivered verifier")
    head = commit()
    assert checked_out_base(tmp_path, executable) == head
    tracked.write_text("changed")
    with pytest.raises(Hold, match="clean"):
        checked_out_base(tmp_path, executable)


def test_untracked_executable_cannot_impersonate_delivered_verifier(
    tmp_path, local_checkout
):
    _, commit, _, executable = local_checkout
    commit()
    executable.write_text("untracked verifier")
    with pytest.raises(Hold, match="delivered verifier"):
        checked_out_base(tmp_path, executable)


def test_executing_bytes_are_compared_to_trusted_git_blob(tmp_path, local_checkout):
    git, commit, _, executable = local_checkout
    executable.write_text("delivered verifier")
    commit()
    git("update-index", "--assume-unchanged", VERIFIER)
    executable.write_text("substitute verifier")
    with pytest.raises(Hold, match="executing verifier bytes"):
        checked_out_base(tmp_path, executable)


def test_cli_writes_dated_blocker_for_invalid_repo(tmp_path):
    output = tmp_path / "result.json"
    assert (
        main(
            [
                "--repo",
                "invalid",
                "--pr",
                "108",
                "--target",
                TARGET,
                "--output",
                str(output),
            ]
        )
        == 1
    )
    result = json.loads(output.read_text())
    assert result["status"] == "hold"
    assert "repository" in result["reason"]
    assert result["verified_at"].endswith("+00:00")
