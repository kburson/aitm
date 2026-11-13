"""One GitHub-hosted macOS/APFS trial with a fixed, reviewed synthetic catalog."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import plistlib
import pwd
import re
import stat
import subprocess
import tempfile

STORY = 268
REPO = "kburson/aitm"
BRANCH = "refs/heads/codex/spike-268-macos-observation"
CATALOG = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
POLICY = {
    "full": ["alpha", "beta", "gamma"],
    "selected": ["alpha", "beta"],
    "allowed_fixture": "fixture.sh",
    "worker": "nobody",
    "assertion": "exact stdout plus successful exit",
}


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def json_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, check=False, timeout=20)


def output(*args):
    value = run(*args)
    require(value.returncode == 0, f"{Path(args[0]).name} failed")
    return value.stdout.decode().strip()


def worker(account, home, *args):
    return run(
        "/usr/bin/sudo", "-n", "-u", account,
        "/usr/bin/env", "-i", "PATH=/usr/bin:/bin", "LC_ALL=C",
        f"HOME={home}", f"TMPDIR={home}", *args, cwd=home,
    )


def evidence_context():
    repository = os.environ.get("GITHUB_REPOSITORY")
    source = os.environ.get("GITHUB_SHA")
    tree = output("/usr/bin/git", "rev-parse", "HEAD^{tree}")
    require(
        repository == REPO
        and os.environ.get("GITHUB_EVENT_NAME") == "push"
        and os.environ.get("GITHUB_REF") == BRANCH
        and os.environ.get("GITHUB_RUN_ATTEMPT") == "1"
        and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted"
        and os.environ.get("RUNNER_OS") == "macOS"
        and os.environ.get("RUNNER_ARCH") == "ARM64"
        and source == output("/usr/bin/git", "rev-parse", "HEAD"),
        "unexpected run identity",
    )
    host = os.environ.get("RUNNER_NAME", "")
    image = os.environ.get("ImageVersion", "")
    require(bool(host and image), "runner name or image version missing")
    return {
        "repository": repository, "source": source, "tree": tree,
        "ref": BRANCH, "event": "push",
        "run": int(os.environ["GITHUB_RUN_ID"]), "attempt": 1,
        "runner": host, "runner_environment": "github-hosted",
        "runner_label": "macos-26", "runner_image_version": image,
        "platform": platform.platform(), "python": platform.python_version(),
        "catalog_sha256": json_digest(CATALOG), "policy_sha256": json_digest(POLICY),
        "controller_sha256": digest(Path(__file__).read_bytes()),
        "fixture_sha256": digest(Path(__file__).with_name("fixture.sh").read_bytes()),
    }


def check_boundary(shared, private, fixture, account, home, upload):
    identity = worker(account, home, "/usr/bin/id", "-u")
    groups = worker(account, home, "/usr/bin/id", "-G")
    env = worker(account, home, "/usr/bin/env")
    require(identity.returncode == groups.returncode == env.returncode == 0, "cannot observe worker principal")
    uid = int(identity.stdout)
    gid_set = [int(g) for g in groups.stdout.split()]
    account_uid = pwd.getpwnam(account).pw_uid
    require(uid not in (0, os.getuid()) and (uid & 0xFFFFFFFF) == (account_uid & 0xFFFFFFFF), "worker is not separate")
    require(80 not in gid_set and 0 not in gid_set, "worker has administrative group")
    require(worker(account, home, "/usr/bin/sudo", "-n", "/usr/bin/true").returncode != 0, "worker has passwordless elevation")
    keys = {row.partition(b"=")[0] for row in env.stdout.splitlines()}
    require(keys == {b"HOME", b"TMPDIR", b"PATH", b"LC_ALL"}, "worker inherited unexpected environment")
    test_device = output("/bin/df", "-P", str(shared)).splitlines()[-1].split()[0]
    info = run("/usr/sbin/diskutil", "info", "-plist", test_device)
    require(info.returncode == 0 and plistlib.loads(info.stdout).get("FilesystemType") == "apfs", "test volume is not verified APFS")

    marker = private / "controller-marker"
    marker.write_text("controller-owned\n")
    marker.chmod(0o600)
    fixture_before = digest(fixture.read_bytes())
    require(worker(account, home, "/bin/test", "-r", str(fixture)).returncode == 0, "worker cannot read pinned fixture")
    require(worker(account, home, "/bin/test", "-w", str(fixture)).returncode == 1, "worker can modify fixture")
    require(worker(account, home, "/bin/cat", str(marker)).returncode != 0, "worker can read controller marker")
    probe = worker(account, home, "/bin/sh", "-c", 'printf "%s\\n" benign > "$1"', "probe", str(marker))
    require(probe.returncode != 0 and marker.read_text() == "controller-owned\n", "worker can change controller marker")
    receipt_path = private / "receipt.json"
    probe = worker(account, home, "/bin/sh", "-c", 'printf "%s\\n" benign > "$1"', "probe", str(receipt_path))
    require(probe.returncode != 0 and not receipt_path.exists(), "worker can create controller receipt")
    require(stat.S_IMODE(private.stat().st_mode) == 0o700 and private.stat().st_uid == os.getuid(), "controller receipt directory is not private")
    staging_probe = worker(account, home, "/bin/sh", "-c", 'printf benign > "$1"', "probe", str(upload))
    require(staging_probe.returncode != 0 and not upload.exists(), "worker can create staged receipt")
    return {
        "filesystem": "apfs", "controller_uid": os.getuid(), "worker_uid": uid,
        "worker_groups": gid_set, "worker_environment_keys": sorted(k.decode() for k in keys),
        "worker_elevation": "denied", "worker_marker_read": "denied",
        "worker_marker_write": "denied", "worker_receipt_create": "denied", "worker_staged_receipt_create": "denied",
        "fixture_worker_write": "denied", "pinned_fixture_sha256": fixture_before,
        "native_process_probe": "worker identity observed through sudo and id",
    }


def assess(expected, proposed_catalog, candidate_result, observations, context):
    """Controller considers only its own execution observations and exact assignment."""
    if json_digest(proposed_catalog) != context["catalog_sha256"]:
        return {"status": "refused", "reason": "inventory identity mismatch", "outcomes": {}}
    if candidate_result is not None:
        if candidate_result["attempt"] != context["attempt"]:
            return {"status": "refused", "reason": "attempt mismatch", "outcomes": {}}
        if candidate_result["authority"] != "controller-observed":
            return {"status": "refused", "reason": "worker receipt has no authority", "outcomes": {}}
    outcomes = {
        case: observations.get(case, "missing") if case in expected else "unobserved"
        for case in CATALOG
    }
    evidence_complete = all(outcomes[case] in {"pass", "fail"} for case in expected)
    return {
        "status": "fail" if "fail" in outcomes.values() else ("pass" if evidence_complete else "refused"),
        "evidence_complete": evidence_complete,
        "outcomes": outcomes,
    }


def exercise(fixture, home, context):
    def observe(case, variant):
        outcome = worker("nobody", home, "/bin/sh", str(fixture), case, variant)
        verdict = "pass" if outcome.returncode == 0 and outcome.stdout == (CATALOG[case] + "\n").encode() else "fail"
        invocations.append({"mode": mode, "case": case, "variant": variant,
                            "returncode": outcome.returncode, "stdout_sha256": digest(outcome.stdout),
                            "outcome": verdict})
        return verdict

    results = {}
    invocations = []
    for mode in ("full", "selected"):
        expected = POLICY[mode]
        observations = {case: observe(case, "normal") for case in expected}
        wrong = {"alpha": observe("alpha", "negative")}
        matrix = {
            "positive": assess(expected, CATALOG, None, observations, context),
            "missing_catalog": assess(expected, {k: v for k, v in CATALOG.items() if k != "gamma"}, None, {}, context),
            "worker_receipt": assess(expected, CATALOG, {"attempt": 1, "authority": "worker", "outcomes": observations}, {}, context),
            "reported_pass_without_observation": assess(expected, CATALOG, {"attempt": 1, "authority": "controller-observed", "outcomes": observations}, {}, context),
            "known_failure_with_missing_sibling": assess(expected, CATALOG, None, wrong, context),
            "stale_attempt": assess(expected, CATALOG, {"attempt": 0, "authority": "controller-observed", "outcomes": observations}, observations, context),
        }
        require(matrix["positive"]["status"] == "pass", f"{mode}: positive fixture failed")
        require(all(matrix[key]["status"] == "refused" for key in ("missing_catalog", "worker_receipt", "reported_pass_without_observation", "stale_attempt")), f"{mode}: expected refusal absent")
        failure = matrix["known_failure_with_missing_sibling"]
        require(failure["status"] == "fail" and not failure["evidence_complete"], f"{mode}: failure or missing sibling lost")
        results[mode] = {"assignment": expected, "assignment_sha256": json_digest(expected), "matrix": matrix}
    return {"modes": results, "fixture_invocations": invocations}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = {"schema": "aitm.spike-268/v1", "issue": STORY, "status": "refused",
               "scope": "allowlisted synthetic fixture; no pytest or child coverage claim"}
    private = Path(tempfile.mkdtemp(prefix="aitm268-controller-", dir="/private/tmp"))
    args.receipt.parent.mkdir(mode=0o700)
    try:
        receipt["identity"] = evidence_context()
        with tempfile.TemporaryDirectory(prefix="aitm268-fixture-", dir="/private/tmp") as location:
            shared = Path(location)
            shared.chmod(0o755)
            fixture = shared / "fixture.sh"
            fixture.write_bytes(Path(__file__).with_name("fixture.sh").read_bytes())
            fixture.chmod(0o444)
            home = shared / "home"
            home.mkdir(mode=0o755)
            receipt["boundary"] = check_boundary(shared, private, fixture, "nobody", home, args.receipt)
            receipt["observations"] = exercise(fixture, home, receipt["identity"])
            require(digest(fixture.read_bytes()) == receipt["identity"]["fixture_sha256"], "fixture drift")
            require((private / "controller-marker").read_text() == "controller-owned\n", "controller marker drift")
            receipt["status"] = "synthetic-scope-pass"
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired, plistlib.InvalidFileException) as exc:
        receipt["reason"] = str(exc)
    finally:
        private_receipt = private / "receipt.json"
        require(not private_receipt.exists(), "receipt appeared before controller write")
        with private_receipt.open("xb") as file:
            os.fchmod(file.fileno(), 0o600)
            file.write((json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode())
        require(worker("nobody", "/private/tmp", "/bin/cat", str(private_receipt)).returncode != 0, "worker can read sealed receipt")
        # Publish only after all worker invocations end.
        with args.receipt.open("xb") as published:
            os.fchmod(published.fileno(), 0o600)
            published.write(private_receipt.read_bytes())
        require(worker("nobody", "/private/tmp", "/bin/cat", str(args.receipt)).returncode != 0, "worker can read staged receipt")
        print(f"Controller receipt SHA-256: {digest(args.receipt.read_bytes())}")
        print(f"Pilot status: {receipt['status']}")
        private_receipt.unlink()
        (private / "controller-marker").unlink(missing_ok=True)
        private.rmdir()
    return 0 if receipt["status"] == "synthetic-scope-pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
