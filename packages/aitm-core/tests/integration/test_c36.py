"""Qualify the installed contained lane against the real macOS sandbox."""

import sys
from json import loads
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from aitm_core.services import preflight_policy
from tests.integration.test_c08 import (
    DEFAULT,
    commit_file,
    configured_settings,
    git,
    identify,
)
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c11 import init
from tests.integration.test_c11 import policy_inputs as policy_inputs
from tests.integration.test_c16 import cli
from tests.integration.test_c32 import installed_attempt
from tests.integration.test_c34 import captured_project
from tests.integration.test_c34 import wheel_origin as wheel_origin


@pytest.mark.skipif(sys.platform != "darwin", reason="requires actual macOS sandbox")
def test_macos_containment(topology, tmp_path, wheel_origin, policy_inputs):
    installation, binding = installed_attempt(topology)
    root = Path(binding.worktree)
    git(root, "switch", "-q", "verification")
    _, wheel_url, _ = wheel_origin
    captured_project(root, tmp_path, wheel_url)
    outside = tmp_path / "undeclared.txt"
    outside.write_text("private to the fixture")
    code = f"""\
import errno
import os
import socket
import subprocess
import sys
from pathlib import Path

import fixture_dep

assert fixture_dep.VALUE == 41
scratch = Path(os.environ["TMPDIR"])
(scratch / "allowed").write_text("yes")
outside = Path({str(outside)!r})
def denied(action):
    try:
        action()
    except OSError as error:
        assert error.errno in (errno.EPERM, errno.EACCES), error
    else:
        raise AssertionError("sandbox allowed a forbidden operation")

denied(outside.read_bytes)
denied(outside.stat)
denied(lambda: outside.write_text("changed"))
denied(lambda: Path(__file__).chmod(0o644))
denied(lambda: Path(fixture_dep.__file__).chmod(0o644))
denied(lambda: socket.create_connection(("127.0.0.1", {urlsplit(wheel_url).port})))
check = "from pathlib import Path; Path(" + repr(str(outside)) + ").read_bytes()"
result = subprocess.run((sys.executable, "-Bc", check), capture_output=True)
assert result.returncode and b"PermissionError" in result.stderr, result
print("contained descendant")
"""
    commit_file(root, "verify.py", code.encode())
    config = (
        configured_settings(topology.genesis)
        .replace("uv run pytest", "uv run python verify.py")
        .replace('assurance = "captured-export"', 'assurance = "contained"')
        .replace('prepare_network = "deny"', 'prepare_network = "allow"')
    )
    commit_file(topology.code, ".aitm.toml", config.encode())
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    assert preflight_policy(installation).policy.config.test.assurance == "contained"
    doctor = cli(root, "doctor")
    assert "lane-probe" not in doctor["pending"], doctor["evidence"]
    assert any("macOS sandbox-exec qualified" in item for item in doctor["evidence"])
    bootstrap = tmp_path / "bootstrap"
    bootstrap.mkdir()
    git(bootstrap, "init", "-q", "-b", "trunk")
    identify(bootstrap)
    commit_file(bootstrap, ".gitignore", b"/.aitm/\n")
    _, prepared_init = init(
        bootstrap, "--local", "--default-branch", "trunk", *policy_inputs
    )
    assert prepared_init["publication"] == "pending", prepared_init["evidence"]
    git(bootstrap, "add", ".aitm.toml", "aitm-workflow.toml")
    git(bootstrap, "commit", "-qm", "Land bootstrap policy")
    _, ready = init(bootstrap, "--local")
    assert ready["local"] == "completed", ready["evidence"]
    committed = (bootstrap / ".aitm.toml").read_bytes()
    commit_file(
        bootstrap,
        ".aitm.toml",
        committed.replace(b'assurance = "captured-export"', b'assurance = "contained"'),
    )
    _, initialized = init(bootstrap, "--local")
    assert initialized["local"] == "completed", initialized["evidence"]
    assert any(
        "macOS sandbox-exec qualified" in item for item in initialized["evidence"]
    ), initialized["evidence"]

    args = (
        "16",
        "--binding",
        binding.identity,
        "--generation",
        str(binding.generation),
        "--session",
        binding.session,
    )
    prepared = cli(root, "test", "prepare", *args)
    assert prepared["local"] == "completed", prepared["evidence"]
    result = cli(root, "test", *args)
    assert result["local"] == "completed", result["evidence"]
    path = Path(loads(result["evidence"][0])["receipt"])
    receipt = loads(path.read_bytes())
    assert receipt["proven_assurance"] == "contained"
    assert receipt["command"][0] == "/usr/bin/sandbox-exec"
    assert (path.parent / "stdout.log").read_bytes() == b"contained descendant\n"
    assert outside.read_text() == "private to the fixture"
