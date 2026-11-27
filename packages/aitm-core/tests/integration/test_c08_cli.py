"""Installed command proof for explicit anchored refresh and stale diagnosis."""

import json
import subprocess
import sys
from pathlib import Path

from aitm_core.models.common import StoreAnchor
from tests.support.c07 import DEFAULT, PLANNING, WORKFLOW, WORKFLOW_BYTES, settings_at


def git(root, *args, data=None):
    return (
        subprocess.check_output(
            ["git", "-C", str(root), *args], input=data, stderr=subprocess.PIPE
        )
        .decode()
        .strip()
    )


def test_installed_refresh_ignores_story_policy_and_reports_stale_code(tmp_path):
    worktree = tmp_path / "clone"
    remote = tmp_path / "code-remote.git"
    worktree.mkdir()
    remote.mkdir()
    git(worktree, "init", "-b", "trunk")
    git(remote, "init", "--bare", "-b", "trunk")
    git(worktree, "config", "user.email", "core@example.test")
    git(worktree, "config", "user.name", "AITM Test")
    root_tree = git(worktree, "mktree", data=b"")
    genesis = git(worktree, "commit-tree", root_tree, "-m", "aitm-planning-root: v1")
    git(worktree, "update-ref", PLANNING, genesis)

    settings = worktree / ".aitm.toml"
    settings.write_text(
        settings_at(genesis).replace('trunk = "trunk"', 'trunk = "hosted-code/trunk"')
    )
    workflow = worktree / WORKFLOW
    workflow.parent.mkdir(parents=True)
    workflow.write_bytes(WORKFLOW_BYTES)
    git(worktree, "add", ".aitm.toml", WORKFLOW)
    git(worktree, "commit", "-m", "commit independently anchored policy")
    policy_tip = git(worktree, "rev-parse", DEFAULT)
    git(worktree, "remote", "add", "hosted-code", str(remote))
    git(worktree, "push", "hosted-code", f"{DEFAULT}:{DEFAULT}")

    anchor = StoreAnchor(
        store_uuid="fixture-store",
        code_default_ref=DEFAULT,
        planning_ref=PLANNING,
        planning_remote=None,
        root_commit=genesis,
    )
    anchor_path = tmp_path / "anchor.json"
    anchor_path.write_text(anchor.model_dump_json())
    installation = tmp_path / "installation.json"
    installation.write_text(
        json.dumps(
            {
                "bootstrap_source": "fixture-selected-default",
                "code_repository": "fixture-code",
                "planning_repository": "fixture-records",
                "code_remote": "hosted-code",
                "code_remote_ref": DEFAULT,
                "issuer": {
                    "backlog": "local",
                    "backlog_repository": "fixture-issues",
                    "numbering_namespace": "fixture-ids",
                },
            }
        )
    )

    git(worktree, "switch", "-c", "story-edit")
    settings.write_text("this is deliberately not committed policy\n")
    git(worktree, "add", ".aitm.toml")
    git(worktree, "commit", "-m", "story edit must not establish authority")
    command = Path(sys.executable).with_name("aitm")
    options = [
        str(command),
        "planning",
        "validate",
        "--json",
        "--anchor",
        str(anchor_path),
        "--repository",
        str(worktree),
    ]

    def run(*extra):
        completed = subprocess.run(
            [*options, *extra],
            cwd=worktree,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.stdout, completed.stderr
        return completed.returncode, json.loads(completed.stdout)

    fresh_status, fresh = run("--refresh", "--installation", str(installation))
    assert fresh_status == 0 and fresh["local"] == "completed", fresh
    assert any(f"Committed policy {policy_tip}" in line for line in fresh["evidence"])
    assert any("freshness: fresh" in line for line in fresh["evidence"])
    assert git(worktree, "rev-parse", PLANNING) == genesis

    git(worktree, "remote", "set-url", "hosted-code", str(tmp_path / "offline"))
    cached_status, cached = run()
    assert cached_status == 0 and cached["local"] == "completed"

    stale_status, stale = run("--refresh", "--installation", str(installation))
    assert stale_status == 4 and stale["publication"] == "pending", stale
    assert any("freshness: stale" in line for line in stale["evidence"])
    assert any(f"Committed policy {policy_tip}" in line for line in stale["evidence"])
    assert settings.read_text() == "this is deliberately not committed policy\n"
