"""Exercise the packaging and boundary contracts from a child process."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2]


def invoke(*args, cwd, env=None):
    return subprocess.run(
        [os.fspath(arg) for arg in args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    work = tmp_path_factory.mktemp("wheel")
    wheels = work / "wheels"
    environment = work / "venv"
    built = invoke("uv", "build", "--wheel", "--out-dir", wheels, PACKAGE, cwd=work)
    assert built.returncode == 0, built.stderr
    created = invoke("uv", "venv", "--python", sys.executable, environment, cwd=work)
    assert created.returncode == 0, created.stderr
    (wheel,) = wheels.glob("aitm_core-*.whl")
    bin_dir = environment / "bin"
    requirements = work / "runtime.txt"
    exported = invoke(
        "uv",
        "export",
        "--locked",
        "--no-dev",
        "--no-emit-workspace",
        "--package",
        "aitm-core",
        "--no-header",
        "--output-file",
        requirements,
        cwd=PACKAGE,
    )
    assert exported.returncode == 0, exported.stderr
    installed = invoke(
        "uv",
        "pip",
        "install",
        "--python",
        bin_dir / "python",
        "--requirement",
        requirements,
        cwd=work,
    )
    assert installed.returncode == 0, installed.stderr
    installed = invoke(
        "uv",
        "pip",
        "install",
        "--python",
        bin_dir / "python",
        "--no-deps",
        wheel,
        cwd=work,
    )
    assert installed.returncode == 0, installed.stderr
    return work, bin_dir


def test_installed_entrypoint(installed):
    work, bin_dir = installed
    env = {**os.environ, "PATH": os.fspath(bin_dir)}
    env.pop("PYTHONPATH", None)
    help_run = invoke(bin_dir / "aitm", "--help", cwd=work, env=env)
    assert help_run.returncode == 0, help_run.stderr
    assert "promote" in help_run.stdout and "decompose" in help_run.stdout
    script = """
import pathlib, subprocess, sys

def external_call(*args, **kwargs):
    raise AssertionError("external call during import")

subprocess.Popen = external_call
def audit(event, args):
    if event.startswith("socket.") or event in ("os.system", "os.posix_spawn", "os.exec"):
        raise AssertionError("external call during import")

sys.addaudithook(audit)
import aitm_core
import aitm_core.cli.app
assert pathlib.Path(aitm_core.__file__).is_relative_to(pathlib.Path(sys.prefix))
assert not any(name.startswith("aitm_core.cli.") and name.rsplit(".",1)[-1] not in
               {"app", "catalog"} for name in sys.modules)
"""
    probe = invoke(bin_dir / "python", "-I", "-c", script, cwd=work, env=env)
    assert probe.returncode == 0, probe.stderr


def test_result_schema_and_exit_codes(installed):
    work, bin_dir = installed
    script = """
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
results = [
    CommandResult(operation_id="op", local=local, publication=publication)
    for local, publication in [
        ("completed", "not-applicable"),
        ("refused", "not-applicable"),
        ("conflict", "not-applicable"),
        ("integrity-error", "not-applicable"),
        ("completed", "pending"),
    ]
]
assert LocalOutcome.REFUSED == "refused"
assert PublicationOutcome.PENDING == "pending"
for expected, result in enumerate(results):
    payload = result.model_dump_json()
    assert CommandResult.model_validate_json(payload) == result
    assert result.exit_code == expected
    print(payload)
"""
    result = invoke(bin_dir / "python", "-I", "-c", script, cwd=work)
    assert result.returncode == 0, result.stderr
    payloads = [json.loads(line) for line in result.stdout.splitlines()]
    assert payloads[0] == {
        "schema": "aitm.command-result/v1",
        "operation_id": "op",
        "local": "completed",
        "publication": "not-applicable",
        "pending": [],
        "evidence": [],
        "recovery": None,
    }
    assert payloads[-1]["local"] == "completed"
    assert payloads[-1]["publication"] == "pending"


def test_missing_route_and_port_decline(installed):
    work, bin_dir = installed
    script = """
import json
from typer.testing import CliRunner
from aitm_core.cli.app import build_cli
from aitm_core.services import ServicePorts, UnavailablePort

result = CliRunner().invoke(build_cli({("probe",): "aitm_core.cli.deliberately_unregistered"}),
                            ["--json", "probe"])
assert result.exit_code != 0
assert json.loads(result.stdout)["local"] == "unavailable"
ports = ServicePorts()
for name in ("policy_resolution", "policy_refresh", "validation_gate",
             "write_authorization", "attempt_preflight", "init_hooks",
             "action_retry", "lane_selection", "kind_requirements",
             "aggregate_evidence", "story_exit_guards"):
    try:
        ports.require(name)
    except UnavailablePort as error:
        assert error.port == name
    else:
        raise AssertionError(f"{name} reported available")
"""
    result = invoke(bin_dir / "python", "-I", "-c", script, cwd=work)
    assert result.returncode == 0, result.stderr
