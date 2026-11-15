"""Run bounded, read-only story validation for an exact reviewed input."""

import argparse
import json
import os
import re
import stat
import subprocess
import tarfile
from collections import Counter
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from ci_advisory import REPO, REPOSITORY_ID, TARGET
from python_gate import _outcomes
from verify_pr import (
    GitHub,
    blob,
    commit,
    digest,
    positive,
    regular_blob,
    require,
    tree_entries,
)

PATH = ".github/workflows/fast-story-shadow.yml"
PLAN = ".aitm/stories/002/292/plan"
SCHEMA = "aitm.ci-fast-story-shadow/v1"
PARAMETERS = ("base", "head", "tested", "tree")
DOC = re.compile(
    rb"docs/(?:[a-zA-Z0-9][a-zA-Z0-9_.-]*/)*[a-zA-Z0-9][a-zA-Z0-9_.-]*\.md"
)
CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
SIGNER = (
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHUMiV961oHTv1SdmEHM/VPEgl2xVUgt3x1XDcT75asG"
)
PRINCIPAL = "aitm-fast-shadow-sar"
NAMESPACE = "aitm-fast-story-admission"
PROFILES = ("packages/aitm-usage/tests", "tools/ci/tests")
PRODUCT = Path("packages/aitm-usage")


def classify_diff(raw):
    parts = raw.split(b"\0")
    if parts[-1] or len(parts) < 3 or len(parts) % 2 != 1:
        return ()
    paths = []
    for header, path in zip(parts[0:-1:2], parts[1:-1:2]):
        fields = header.split()
        if len(fields) != 5 or not DOC.fullmatch(path):
            return ()
        mode, new_mode, _, _, status = fields
        if new_mode != b"100644" or (mode, status) not in {
            (b":000000", b"A"),
            (b":100644", b"M"),
        }:
            return ()
        paths.append(path.decode("ascii"))
    return tuple(paths)


def reviewed_tuple(admission, review):
    require(
        isinstance(admission, dict)
        and set(admission) == {"schema", "pr", "review_sha256", *PARAMETERS}
        and admission["schema"] == "aitm.fast-story-admission/v1"
        and positive(admission["pr"])
        and all(digest(admission[key]) for key in PARAMETERS),
        "invalid admission tuple",
    )
    require(
        b"**Verdict: ACCEPTED.**" in review
        and f"https://github.com/{REPO}/pull/{admission['pr']})".encode() in review
        and sha256(review).hexdigest() == admission["review_sha256"]
        and all(admission[key].encode() in review for key in PARAMETERS),
        "independent review does not bind this admission",
    )
    return {key: admission[key] for key in ("pr", *PARAMETERS)}


def phase_evidence(document, expected, child_labels):
    require(document.get("collected") == expected, "execution inventory disagrees")
    outcomes, errors = _outcomes(document, {})
    require(not errors and set(outcomes) == set(expected), "incomplete exact outcomes")
    children = document["children"]
    require(
        all(
            isinstance(child, dict)
            and positive(child.get("pid"))
            and type(child.get("returncode")) is int
            and child["returncode"] == 0
            and isinstance(child.get("label"), str)
            for child in children
        )
        and len({child["pid"] for child in children}) == len(children)
        and Counter(child["label"] for child in children) == Counter(child_labels),
        "required native children disagree",
    )
    return outcomes


def verify_admission_signature(raw, signature):
    with TemporaryDirectory(prefix="aitm-shadow-review-") as directory:
        folder = Path(directory)
        signers = folder / "allowed-signers"
        signers.write_text(f"{PRINCIPAL} {SIGNER.strip()}\n")
        detached = folder / "manifest.sig"
        detached.write_bytes(signature)
        result = subprocess.run(
            [
                "/usr/bin/ssh-keygen",
                "-Y",
                "verify",
                "-f",
                str(signers),
                "-I",
                PRINCIPAL,
                "-n",
                NAMESPACE,
                "-s",
                str(detached),
            ],
            input=raw,
            capture_output=True,
        )
    require(result.returncode == 0, "independent admission signature is invalid")


def admission_from_planning(github, planning_commit):
    require(digest(planning_commit), "invalid planning revision")
    branch = github.document("branches/planning")
    require(
        branch["protected"] is True and branch["name"] == "planning",
        "planning is unprotected",
    )
    current = branch["commit"]["sha"]
    if planning_commit != current:
        comparison = github.document(f"compare/{planning_commit}...{current}")
        require(
            comparison["status"] == "ahead"
            and comparison["merge_base_commit"]["sha"] == planning_commit,
            "admission revision is outside protected planning history",
        )
    tree = commit(github, planning_commit)["tree"]["sha"]
    entries = tree_entries(github, tree)
    raw = blob(github, regular_blob(entries, f"{PLAN}/shadow-admission.json"))
    signed = blob(github, regular_blob(entries, f"{PLAN}/shadow-admission.json.sig"))
    verify_admission_signature(raw, signed)
    review = blob(github, regular_blob(entries, f"{PLAN}/shadow-admission-review.md"))
    return reviewed_tuple(json.loads(raw), review)


def verify_live_subject(github, subject):
    repo = github.document("")
    require(
        repo["id"] == REPOSITORY_ID
        and repo["full_name"] == REPO
        and repo["default_branch"] == TARGET,
        "repository identity changed",
    )
    branch = github.document(f"branches/{TARGET}")
    pull = github.document(f"pulls/{subject['pr']}")
    require(
        branch["protected"] is True
        and branch["commit"]["sha"] == subject["base"]
        and pull["number"] == subject["pr"]
        and pull["state"] == "open"
        and pull["base"]["ref"] == TARGET
        and pull["base"]["sha"] == subject["base"]
        and pull["base"]["repo"]["id"] == pull["head"]["repo"]["id"] == REPOSITORY_ID
        and pull["head"]["sha"] == subject["head"]
        and pull["merge_commit_sha"] == subject["tested"],
        "live pull request no longer matches the reviewed subject",
    )


def git(root, *command):
    return subprocess.check_output(["git", "-C", str(root), *command])


def verify_checkout(root, entries):
    expected = {}
    for entry in entries.removesuffix(b"\0").split(b"\0"):
        header, name = entry.split(b"\t", 1)
        mode, kind, oid = header.split()
        require(kind == b"blob", "archive contains an unsupported Git entry")
        expected[name] = mode, oid
    actual = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            mode, value = b"120000", os.fsencode(os.readlink(path))
        elif path.is_dir():
            continue
        else:
            info = path.lstat()
            require(stat.S_ISREG(info.st_mode), "archive contains a nonregular file")
            mode = b"100755" if info.st_mode & stat.S_IXUSR else b"100644"
            value = path.read_bytes()
        header = f"blob {len(value)}\0".encode()
        actual[os.fsencode(path.relative_to(root))] = (
            mode,
            sha1(header + value).hexdigest().encode(),
        )
    require(
        actual == expected,
        "materialized archive differs from exact Git paths and blobs",
    )


def source_digest(root):
    result = sha256()
    for path in sorted(root.rglob("*")):
        if path.is_dir() and not path.is_symlink():
            continue
        name = os.fsencode(path.relative_to(root))
        content = (
            os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
        )
        result.update(
            b"\0".join(
                (name, str(path.lstat().st_mode).encode(), sha256(content).digest())
            )
        )
    return result.hexdigest()


def collect_or_execute(root, cwd, scratch, python, environment, name, args):
    output = scratch / f"{name}.json"
    env = {
        **environment,
        "PYTHONPATH": f"{root / 'tools/ci'}:{cwd / PRODUCT / 'src'}",
        "AITM_CI_PYTEST_EVIDENCE": str(output),
        "AITM_CI_CHILD_EVIDENCE": "1",
    }
    command = subprocess.run(
        [
            str(python),
            "-m",
            "pytest",
            "-c",
            str(cwd / PRODUCT / "pyproject.toml"),
            "--rootdir",
            str(cwd),
            "-p",
            "pytest_evidence",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(scratch.parent / "fixtures" / name),
            "--tb=long",
            "-q",
            *args,
        ],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if command.returncode or name == "selected":
        print(command.stdout.decode(errors="replace"), end="", flush=True)
    command.check_returncode()
    document = json.loads(output.read_bytes())
    print(f"{name} reported {len(document['collected'])} collected IDs", flush=True)
    return document


def collection(document):
    rows = document["collected"]
    require(
        document["schema"] == "aitm.pytest-evidence/v1"
        and document["exit_code"] == 0
        and isinstance(rows, list)
        and rows
        and len(rows) == len(set(rows))
        and not document["children"]
        and not document["deselected"]
        and not document["reports"],
        "complete collection evidence unavailable",
    )
    return rows


def execute(root, work, tested):
    for directory in ("source", "fixtures", "receipts", "home", "temp"):
        (work / directory).mkdir()
    candidate = work / "source"
    with tarfile.open(fileobj=BytesIO(git(root, "archive", tested))) as archive:
        archive.extractall(candidate, filter="data")
    verify_checkout(candidate, git(root, "ls-tree", "-rz", "--full-tree", tested))
    before = source_digest(candidate)
    env = {
        name: os.environ[name]
        for name in ("PATH", "LANG", "LC_ALL", "UV_PYTHON_INSTALL_DIR")
        if name in os.environ
    }
    env.update(
        HOME=str(work / "home"),
        TMPDIR=str(work / "temp"),
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        UV_PROJECT_ENVIRONMENT=str(work / "venv"),
    )
    subprocess.run(
        [
            "uv",
            "sync",
            "--locked",
            "--python",
            "3.13.9",
            "--project",
            str(candidate / PRODUCT),
        ],
        cwd=candidate,
        env=env,
        check=True,
    )
    python = work / "venv/bin/python"
    receipts = work / "receipts"
    trusted = collect_or_execute(
        root, root, receipts, python, env, "trusted", ("--collect-only", *PROFILES)
    )
    tested_inventory = collect_or_execute(
        root,
        candidate,
        receipts,
        python,
        env,
        "tested",
        ("--collect-only", *PROFILES),
    )
    inventory = collection(trusted)
    require(
        collection(tested_inventory) == inventory,
        "trusted and candidate collections disagree",
    )
    policy = json.loads((root / "tools/ci/policy.json").read_bytes())
    mandatory = set(policy["required_tests"]) | {CLI}
    chosen = [row for row in inventory if row in mandatory]
    require(set(chosen) == mandatory, "mandatory inventory incomplete")
    raw = collect_or_execute(root, candidate, receipts, python, env, "selected", chosen)
    outcomes = phase_evidence(raw, chosen, policy["required_children"])
    require(
        source_digest(candidate) == before, "tested source mutated during execution"
    )
    return {
        "selected": chosen,
        "mandatory": sorted(mandatory),
        "outcomes": outcomes,
        "trusted_collection": trusted,
        "tested_collection": tested_inventory,
        "execution": raw,
    }


def run(github, root, work, planning_commit):
    require(
        os.environ.get("GITHUB_REPOSITORY") == REPO
        and os.environ.get("GITHUB_REF") == f"refs/heads/{TARGET}"
        and os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        and os.environ.get("GITHUB_WORKFLOW_REF")
        == f"{REPO}/{PATH}@refs/heads/{TARGET}",
        "untrusted shadow workflow route",
    )
    subject = admission_from_planning(github, planning_commit)
    verify_live_subject(github, subject)
    require(
        git(root, "rev-parse", "HEAD").decode().strip() == subject["base"]
        and os.environ.get("GITHUB_SHA") == subject["base"]
        and os.environ.get("GITHUB_WORKFLOW_SHA") == subject["base"],
        "controller checkout differs from current protected base",
    )
    git(root, "fetch", "--no-tags", "origin", f"refs/pull/{subject['pr']}/merge")
    tested = subject["tested"]
    require(
        git(root, "rev-parse", "FETCH_HEAD").decode().strip() == tested
        and git(root, "show", "-s", "--format=%P", tested).decode().split()
        == [subject["base"], subject["head"]]
        and git(root, "rev-parse", f"{tested}^{{tree}}").decode().strip()
        == subject["tree"],
        "synthetic tested commit disagrees with reviewed subject",
    )
    raw = git(root, "diff", "--raw", "-z", "--no-renames", subject["base"], tested)
    changed = classify_diff(raw)
    result = execute(root, work, tested) if changed else None
    verify_live_subject(github, subject)
    return {
        "schema": SCHEMA,
        "repository_id": REPOSITORY_ID,
        "planning_commit": planning_commit,
        "scope": "advisory",
        "mode": "selected" if changed else "full-required",
        "run_id": int(os.environ["GITHUB_RUN_ID"]),
        "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "subject": subject,
        "docs_paths": changed,
        "result": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("admission")
    parser.add_argument("work", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    decision = run(GitHub(REPO), root, args.work, args.admission)
    args.receipt.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n")
    print(
        f"Fast story shadow for PR {decision['subject']['pr']} returned {decision['mode']}"
    )


if __name__ == "__main__":
    main()
