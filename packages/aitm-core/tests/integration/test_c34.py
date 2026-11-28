"""Qualify isolated locked provisioning and the installed offline prepare route."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from subprocess import run
from sys import executable
from threading import Thread
from zipfile import ZipFile

import pytest

from aitm_core.services import preflight_policy
from aitm_core.setup.journal import state_directory
from aitm_core.verification import provision as provision_module
from aitm_core.verification.capture import capture_inputs
from aitm_core.verification.provision import provision, validate_environment
from tests.integration.test_c08 import DEFAULT, commit_file, configured_settings, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.integration.test_c32 import installed_attempt


@pytest.fixture
def wheel_origin(tmp_path):
    wheels = tmp_path / "http-wheel"
    wheels.mkdir()
    wheel = wheels / "fixture_dep-1.0.0-py3-none-any.whl"
    info = "fixture_dep-1.0.0.dist-info"
    with ZipFile(wheel, "w") as archive:
        archive.writestr("fixture_dep.py", "VALUE = 41\n")
        archive.writestr(
            f"{info}/METADATA",
            "Metadata-Version: 2.1\nName: fixture-dep\nVersion: 1.0.0\n",
        )
        archive.writestr(
            f"{info}/WHEEL",
            "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        archive.writestr(
            f"{info}/RECORD",
            f"fixture_dep.py,,\n{info}/METADATA,,\n{info}/WHEEL,,\n{info}/RECORD,,\n",
        )
    hits = []

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, _format, *_arguments):
            pass

        def do_GET(self):
            hits.append(self.path)
            super().do_GET()

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(Handler, directory=str(wheels))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, f"http://127.0.0.1:{server.server_port}/{wheel.name}", hits
    finally:
        if thread.is_alive():
            server.shutdown()
        server.server_close()
        thread.join()


def captured_project(root, tmp_path, wheel_url):
    project = root / "pyproject.toml"
    project.write_text(f"""[project]
name = "capture-fixture"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = ["fixture-dep @ {wheel_url}"]
""")
    locked = run(
        (
            "uv",
            "lock",
            "--no-index",
            "--no-python-downloads",
            "--cache-dir",
            str(tmp_path / "test-uv-cache"),
            "--python",
            executable,
        ),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert locked.returncode == 0, locked.stderr
    git(root, "add", "pyproject.toml", "uv.lock")
    git(
        root,
        "commit",
        "-qm",
        "Capture a dependency locked to the fixture wheel endpoint",
    )


def test_provision_policy(topology, tmp_path, monkeypatch, wheel_origin):
    installation, binding = installed_attempt(topology)
    repo = installation.repository
    root = Path(binding.worktree)
    git(root, "switch", "-q", "verification")
    server, wheel_url, hits = wheel_origin
    captured_project(root, tmp_path, wheel_url)
    assert preflight_policy(installation).policy is not None
    planning = repo.tip()
    git(topology.planning, "pull", "--ff-only", "-q", "origin")
    new_shared = topology.advance_planning(
        ".aitm/README.md", b"Concurrent planning bytes.\n"
    )
    arguments = (
        "test",
        "prepare",
        "16",
        "--binding",
        binding.identity,
        "--generation",
        str(binding.generation),
        "--session",
        binding.session,
    )
    denied = cli(root, *arguments)
    assert denied["local"] == "unavailable", denied
    assert any("aitm test prepare 16" in item for item in denied["evidence"])
    assert repo.tip() == planning and new_shared != planning.revision
    receipts = state_directory(repo) / "verification" / "environments"
    assert not list(receipts.glob("*.json"))

    allow = configured_settings(topology.genesis).replace(
        'prepare_network = "deny"', 'prepare_network = "allow"'
    )
    commit_file(topology.code, ".aitm.toml", allow.encode())
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    policy = preflight_policy(installation).policy
    assert policy is not None and policy.config.test.prepare_network == "allow"
    planning = repo.tip()
    assert planning.revision == new_shared
    inputs = capture_inputs(installation, binding, policy, parent=tmp_path)
    offline = cli(root, *arguments, "--offline")
    assert offline["local"] == "unavailable", offline
    assert any("--offline" in item for item in offline["evidence"])

    def interrupted(_tools, _inputs, environment, _scratch, *, offline):
        assert not offline
        environment.mkdir()
        (environment / "partial.txt").write_text("Incomplete install")
        raise OSError("Interrupted fixture installer")

    with monkeypatch.context() as patch:
        patch.setattr(provision_module, "_sync", interrupted)
        result = provision(installation, binding, policy, inputs)
    assert result.status == "unavailable" and result.prepared is None
    assert not list(receipts.glob("*.json"))

    atomic = provision_module._atomic_write

    def fail_environment(path, value):
        if path.parent.name == "environments":
            raise OSError("Interrupted environment receipt publication")
        return atomic(path, value)

    with monkeypatch.context() as patch:
        patch.setattr(provision_module, "_atomic_write", fail_environment)
        result = provision(installation, binding, policy, inputs)
    assert result.status == "unavailable" and result.prepared is None
    assert not list(receipts.glob("*.json"))
    assert not list((receipts.parent / "installer").glob("*.json"))

    downloads = len(hits)
    result = provision(installation, binding, policy, inputs)
    assert result.status == "ready", result
    assert len(hits) > downloads
    server.shutdown()
    server.server_close()
    prepared = result.prepared
    assert prepared is not None
    installed = run(
        (
            str(prepared.directory / "bin/python"),
            "-I",
            "-B",
            "-c",
            "import fixture_dep; assert fixture_dep.VALUE == 41",
        ),
        capture_output=True,
        text=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stderr
    assert not (root / ".venv").exists()
    assert (
        validate_environment(installation, binding, policy, inputs, prepared).status
        == "ready"
    )
    offline = cli(root, *arguments, "--offline")
    assert offline["local"] == "completed", offline
    assert any(prepared.receipt.identity.digest in item for item in offline["evidence"])
    assert len(list(receipts.glob("*.json"))) == 1 and repo.tip() == planning

    tools = provision_module._tools()
    changed_tools = tools.model_copy(update={"installer_digest": "f" * 64})
    with monkeypatch.context() as patch:
        patch.setattr(
            provision_module,
            "_tools",
            lambda: changed_tools,
        )
        assert (
            validate_environment(installation, binding, policy, inputs, prepared).status
            == "stale"
        )

    previous_cache = provision_module._cached
    with monkeypatch.context() as patch:

        def changes_during_readback(cache, identity):
            prepared = previous_cache(cache, identity)
            patch.setattr(provision_module, "_tools", lambda: changed_tools)
            return prepared

        patch.setattr(provision_module, "_cached", changes_during_readback)
        assert (
            provision(installation, binding, policy, inputs, offline=True).status
            == "unavailable"
        )

    dependency = next(prepared.directory.rglob("fixture_dep.py"))
    dependency.chmod(0o644)
    dependency.write_text("VALUE = 99\n")
    dependency.chmod(0o444)
    assert (
        validate_environment(installation, binding, policy, inputs, prepared).status
        == "stale"
    )
    commit_file(
        topology.code, ".aitm.toml", configured_settings(topology.genesis).encode()
    )
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    deny_policy = preflight_policy(installation).policy
    assert deny_policy is not None and deny_policy.config.test.prepare_network == "deny"
    assert (
        validate_environment(installation, binding, policy, inputs, prepared).status
        == "stale"
    )
    deny_inputs = capture_inputs(installation, binding, deny_policy, parent=tmp_path)
    copied = provision(installation, binding, deny_policy, deny_inputs, offline=True)
    assert copied.status == "ready", copied
    assert (
        copied.prepared is not None and copied.prepared.directory != prepared.directory
    )
    assert copied.prepared.receipt.identity.policy_digest == deny_policy.source.digest
    installer = next(
        (state_directory(repo) / "verification" / "installer").glob("*.json")
    )
    installer.write_text("{}")
    copied_dependency = next(copied.prepared.directory.rglob("fixture_dep.py"))
    copied_dependency.chmod(0o644)
    copied_dependency.write_text("VALUE = 99\n")
    copied_dependency.chmod(0o444)
    assert (
        provision(installation, binding, deny_policy, deny_inputs, offline=True).status
        == "unavailable"
    )

    commit_file(root, "uv.lock", (root / "uv.lock").read_bytes() + b"\n# new lock\n")
    assert (
        validate_environment(
            installation, binding, deny_policy, deny_inputs, copied.prepared
        ).status
        == "stale"
    )
    assert repo.tip() == planning
