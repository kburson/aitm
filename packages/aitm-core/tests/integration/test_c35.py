"""Qualify the installed verification route with real Git, uv, and a child process."""

from hashlib import sha256
from json import loads
from pathlib import Path

from aitm_core.models.operations import story_event_path
from aitm_core.services import preflight_policy
from aitm_core.verification.lanes import select_lane
from tests.integration.test_c08 import DEFAULT, commit_file, configured_settings, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.integration.test_c32 import installed_attempt
from tests.integration.test_c34 import captured_project
from tests.integration.test_c34 import wheel_origin as wheel_origin


def test_captured_run(topology, tmp_path, wheel_origin):
    installation, binding = installed_attempt(topology)
    root = Path(binding.worktree)
    git(root, "switch", "-q", "verification")
    server, wheel_url, hits = wheel_origin
    captured_project(root, tmp_path, wheel_url)
    verify = b"""\
import os
import stat
from pathlib import Path

import fixture_dep

assert fixture_dep.VALUE == 41
assert not (Path.cwd().stat().st_mode & stat.S_IWUSR)
assert not (Path(__file__).stat().st_mode & stat.S_IWUSR)
assert os.environ["PYTHONDONTWRITEBYTECODE"] == "1"
scratch = Path(os.environ["TMPDIR"])
assert not scratch.is_relative_to(Path.cwd())
(scratch / "test-output").write_text("writable")
print("captured dependency", fixture_dep.VALUE)
"""
    commit_file(root, "verify.py", verify)
    settings = configured_settings(topology.genesis).replace(
        "uv run pytest", "uv run python verify.py"
    )
    allow = settings.replace('prepare_network = "deny"', 'prepare_network = "allow"')
    commit_file(topology.code, ".aitm.toml", allow.encode())
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    assert preflight_policy(installation).policy.config.test.prepare_network == "allow"
    binding_args = (
        "16",
        "--binding",
        binding.identity,
        "--generation",
        str(binding.generation),
        "--session",
        binding.session,
    )
    prepared = cli(root, "test", "prepare", *binding_args)
    assert prepared["local"] == "completed", prepared["evidence"]
    assert hits
    hit_count = len(hits)

    result = cli(root, "test", *binding_args)
    assert result["local"] == "completed", result
    receipt_path = Path(loads(result["evidence"][0])["receipt"])
    receipt = loads(receipt_path.read_bytes())
    assert receipt["result"] == "passed"
    assert (
        receipt["selected_assurance"]
        == receipt["proven_assurance"]
        == "captured-export"
    )
    assert receipt["source"]["commit"] == git(root, "rev-parse", "HEAD")
    output = (receipt_path.parent / "stdout.log").read_bytes()
    assert output == b"captured dependency 41\n"
    assert receipt["stdout_sha256"] == sha256(output).hexdigest()
    assert len(hits) == hit_count
    assert receipt["stdout_sha256"] != receipt["stderr_sha256"]

    doctor = cli(root, "doctor")
    assert "lane-probe" not in doctor["pending"]
    assert any("captured-export" in line for line in doctor["evidence"])

    commit_file(root, "verify.py", verify + b"raise SystemExit(7)\n")
    prepared = cli(root, "test", "prepare", *binding_args)
    assert prepared["local"] == "completed", prepared["evidence"]
    server.shutdown()
    failed = cli(root, "test", *binding_args)
    assert failed["local"] == "refused", failed
    failed_receipt = loads(Path(loads(failed["evidence"][0])["receipt"]).read_bytes())
    assert failed_receipt["result"] == "failed"
    assert failed_receipt["exit_code"] == 7
    assert failed_receipt["capture_manifest"] != receipt["capture_manifest"]

    if select_lane("contained").probe().assurance is not None:
        return
    revision = installation.repository.tip()
    commit_file(
        topology.code,
        ".aitm.toml",
        settings.replace(
            'assurance = "captured-export"', 'assurance = "contained"'
        ).encode(),
    )
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    pending = cli(root, "test", *binding_args)
    assert pending["local"] == "unavailable", pending
    assert "lane-probe" in pending["pending"]
    assert installation.repository.tip() == revision
    path = story_event_path(16)
    lines = installation.repository.read_blobs(revision.tree, (path,))[path]
    starts = [
        event
        for event in map(loads, lines.splitlines())
        if event["type"] == "core.execution.recorded"
        and event["data"]["phase"] == "started"
    ]
    assert len(starts) == 2
