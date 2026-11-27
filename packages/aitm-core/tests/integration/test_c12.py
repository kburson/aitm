"""Exercise the installed initialization, doctor and real Git hook contract."""

import json
import subprocess
from dataclasses import replace
from pathlib import Path
from sys import executable
from types import SimpleNamespace

from aitm_core.providers.githost import ProtectResult
from aitm_core.services import ServicePorts
from aitm_core.setup.doctor import doctor
from aitm_core.setup.init import _active_installation, _readiness
from aitm_core.store.objects import Repository
from tests.integration.test_c11 import RECORDS, git, init
from tests.integration.test_c11 import policy_inputs as policy_inputs
from tests.integration.test_c11 import repository as repository


def test_hook_chain(repository, policy_inputs, tmp_path_factory):
    root = repository
    hook_dir = root / "custom hooks"
    hook_dir.mkdir()
    git(root, "config", "core.hooksPath", str(hook_dir))
    foreign = b'#!/bin/sh\nprintf "foreign:%s\\n" "$1" >&2\nexit 17\n'
    (hook_dir / "pre-push").write_bytes(foreign)
    (hook_dir / "pre-push").chmod(0o755)
    (root / ".gitignore").write_bytes(b"keep-this\n.aitm/\n")
    args = (
        "--local",
        "--default-branch",
        "trunk",
        "--planning-branch",
        "project/records",
    )
    _, prepared = init(root, *args, *policy_inputs)
    assert prepared["publication"] == "pending", prepared
    assert (root / ".gitignore").read_bytes() == b"keep-this\n.aitm/\n/.aitm/\n"
    assert "git add -- .gitignore" in prepared["evidence"]
    git(root, "add", ".gitignore")
    git(root, "commit", "-qm", "Land ignore independently")
    _, resumed = init(root)
    assert "git add -- .gitignore" not in resumed["evidence"], resumed
    git(root, "add", ".aitm.toml", "aitm-workflow.toml")
    git(root, "commit", "-qm", "Land bootstrap")
    _, ready = init(root)
    assert ready["local"] == "completed", ready
    assert "init_hooks" not in ready["pending"], ready
    assert any("force pushes" in line for line in ready["evidence"]), ready
    assert git(root, "config", "core.hooksPath") == str(hook_dir)

    def run(*args, data=None):
        return subprocess.run(
            ("git", "-C", str(root), *args),
            input=data,
            capture_output=True,
            check=False,
        )

    git(root, "switch", "-q", "project/records")
    checked_out = subprocess.run(
        (str(Path(executable).with_name("aitm")), "doctor", "--json"),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "checkout" in json.loads(checked_out.stdout)["pending"]
    blocked = run("commit", "--allow-empty", "-m", "Ordinary planning commit")
    assert blocked.returncode
    assert b"planning ref" in blocked.stderr
    git(root, "switch", "-qc", "review-ref")
    git(root, "commit", "--allow-empty", "-qm", "Review branch commit")
    good = git(root, "rev-parse", RECORDS)
    code = git(root, "rev-parse", "trunk")
    zero = "0" * len(good)

    def push_hook(revision, target):
        return subprocess.run(
            (str(hook_dir / "pre-push"), "origin", "fixture"),
            cwd=root,
            input=f"refs/heads/review-ref {revision} {target} {zero}\n".encode(),
            capture_output=True,
            check=False,
        )

    refused = push_hook(code, RECORDS)
    assert refused.returncode and refused.returncode != 17
    assert b"foreign:" not in refused.stderr
    chained = push_hook(good, RECORDS)
    assert chained.returncode == 17
    assert b"foreign:origin" in chained.stderr
    assert push_hook(code, "refs/heads/review-ref").returncode == 17
    before = (hook_dir / "pre-push").read_bytes()
    _, rerun = init(root)
    assert rerun["local"] == "completed", rerun
    assert (hook_dir / "pre-push").read_bytes() == before
    assert push_hook(good, RECORDS).returncode == 17

    command = subprocess.run(
        (str(Path(executable).with_name("aitm")), "doctor", "--json"),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    report = json.loads(command.stdout)
    assert report["local"] == "completed", report
    assert any("unanchored .aitm/" in line for line in report["evidence"]), report

    git(root, "switch", "-q", "trunk")
    (root / ".gitignore").write_bytes(b"keep-this\n.aitm/\n")
    _, upgraded = init(root)
    assert upgraded["local"] == "completed", upgraded
    assert (root / ".gitignore").read_bytes() == b"keep-this\n.aitm/\n/.aitm/\n"

    installation, _ = _active_installation(Repository(root, RECORDS))
    missing_probe = doctor(installation, ServicePorts(lane_selection=None))
    assert "lane-probe" in missing_probe.pending
    hosted = replace(
        installation,
        store=installation.store.model_copy(update={"planning_remote": "origin"}),
    )

    def protect(target, rules):
        return ProtectResult(
            target=target,
            rules=rules,
            status="manual",
            instructions=("Disable force pushes on the planning ref.",),
            settings_url="https://fixture.invalid/settings/branches",
        )

    _readiness(
        hosted, ServicePorts(init_git_host=SimpleNamespace(protect_branch=protect))
    )
    manual = doctor(hosted)
    assert "protection" in manual.pending
    assert "https://fixture.invalid/settings/branches" in manual.evidence
    assert any("manual" in line for line in manual.evidence)

    unrelated = tmp_path_factory.mktemp("unrelated-repo")
    git(unrelated, "init", "-q", "-b", "main")
    git(unrelated, "config", "user.name", "Another repository")
    git(unrelated, "config", "user.email", "fixture@example.invalid")
    git(unrelated, "config", "core.hooksPath", str(hook_dir))
    git(unrelated, "commit", "--allow-empty", "-qm", "Same configured hooks directory")
