"""Qualify the installed private export against exact Git and workspace inputs."""

from dataclasses import replace
from os import link
from pathlib import Path
from shutil import copytree

import pytest

from aitm_core.services import preflight_policy
from aitm_core.verification import capture as capture_module
from aitm_core.verification.capture import (
    CaptureUnavailable,
    capture_applicable,
    capture_inputs,
)
from tests.integration.test_c08 import commit_file, configured_settings, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c32 import installed_attempt


def test_capture_manifest(topology, tmp_path, monkeypatch):
    settings = configured_settings(topology.genesis).replace(
        "inputs = []", 'inputs = ["fixtures/*.txt"]'
    )
    commit_file(topology.code, ".aitm.toml", settings.encode())
    installation, binding = installed_attempt(topology)
    policy = preflight_policy(installation).policy
    assert policy is not None
    root = Path(binding.worktree)
    git(root, "switch", "-q", "verification")
    commit_file(root, ".gitattributes", b"source.bin export-ignore\n")
    (root / "source.bin").write_bytes(b"Exact committed input\x00\n")
    (root / "source.bin").chmod(0o755)
    git(root, "add", "source.bin")
    git(root, "commit", "-qm", "Add executable tracked input")
    revision = git(root, "rev-parse", "HEAD")
    fixtures = root / "fixtures"
    fixtures.mkdir()
    extra = fixtures / "extra.txt"
    extra.write_bytes(b"Declared fixture\n")
    (root / "scratch.txt").write_text("Undeclared")
    parent = tmp_path / "captures"
    parent.mkdir()

    capture = capture_inputs(installation, binding, policy, parent=parent)
    exported = capture.source_directory
    assert exported.is_relative_to(parent) and not exported.is_relative_to(root)
    assert capture.candidate.source.commit == revision
    assert capture.candidate.capture_manifest == capture.manifest.digest
    assert (exported / "source.bin").read_bytes() == b"Exact committed input\x00\n"
    assert (exported / "fixtures/extra.txt").read_bytes() == b"Declared fixture\n"
    assert not (exported / "scratch.txt").exists()
    assert extra.stat().st_ino != (exported / "fixtures/extra.txt").stat().st_ino
    assert not ((exported / "source.bin").stat().st_mode & 0o222)
    assert (exported / "source.bin").stat().st_mode & 0o111
    assert capture_applicable(installation, binding, policy, capture)

    tampered_path = copytree(capture.directory, tmp_path / "tampered")
    tampered = replace(capture, directory=tampered_path)
    tampered.source_directory.chmod(0o755)
    omitted = tampered.source_directory / "unexpected"
    omitted.mkdir(mode=0o555)
    tampered.source_directory.chmod(0o555)
    assert not capture_applicable(installation, binding, policy, tampered)
    tampered.source_directory.chmod(0o755)
    omitted.rmdir()
    destination = tampered.source_directory / "source.bin"
    destination.unlink()
    link(exported / "source.bin", destination)
    tampered.source_directory.chmod(0o555)
    assert not capture_applicable(installation, binding, policy, tampered)
    tampered.source_directory.chmod(0o755)
    destination.unlink()
    tampered.source_directory.chmod(0o555)

    forged_path = copytree(capture.directory, tmp_path / "forged")
    forged_manifest = capture.manifest.model_copy(
        update={
            "entries": tuple(
                row for row in capture.manifest.entries if row.path != "source.bin"
            )
        }
    )
    forged_source = forged_path / "source"
    forged_source.chmod(0o755)
    (forged_source / "source.bin").unlink()
    forged_source.chmod(0o555)
    forged_receipt = forged_path / "manifest.json"
    forged_receipt.chmod(0o644)
    forged_receipt.write_bytes(forged_manifest.content)
    forged_receipt.chmod(0o444)
    forged = replace(capture, directory=forged_path, manifest=forged_manifest)
    assert not capture_applicable(installation, binding, policy, forged)

    (root / "source.bin").write_bytes(b"Transient original edit")
    assert (exported / "source.bin").read_bytes() == b"Exact committed input\x00\n"
    assert not capture_applicable(installation, binding, policy, capture)
    git(root, "restore", "source.bin")
    assert capture_applicable(installation, binding, policy, capture)

    extra.write_bytes(b"Changed fixture")
    assert (exported / "fixtures/extra.txt").read_bytes() == b"Declared fixture\n"
    assert not capture_applicable(installation, binding, policy, capture)
    extra.unlink()
    with pytest.raises(CaptureUnavailable, match="matched no"):
        capture_inputs(installation, binding, policy, parent=parent)

    extra.symlink_to(root / "scratch.txt")
    with pytest.raises(CaptureUnavailable, match="regular|unsafe|symbolic"):
        capture_inputs(installation, binding, policy, parent=parent)
    extra.unlink()
    extra.write_bytes(b"Declared fixture\n")

    original = capture_module._read_extra
    changed = []

    def change_during_capture(root, path):
        result = original(root, path)
        if not changed:
            extra.write_bytes(b"Concurrent fixture replacement")
            changed.append(path)
        return result

    with monkeypatch.context() as patch:
        patch.setattr(capture_module, "_read_extra", change_during_capture)
        with pytest.raises(CaptureUnavailable, match="input changed"):
            capture_inputs(installation, binding, policy, parent=parent)
    assert changed == ["fixtures/extra.txt"]
    extra.write_bytes(b"Declared fixture\n")
    with pytest.raises(CaptureUnavailable, match="overlap"):
        capture_inputs(
            installation, binding, policy, parent=parent, output_roots=("fixtures",)
        )
    with pytest.raises(CaptureUnavailable, match="worktree"):
        capture_inputs(installation, binding, policy, parent=root)
    assert list(parent.iterdir()) == [capture.directory]
    assert capture_applicable(installation, binding, policy, capture)

    commit_file(root, "source.bin", b"Candidate advanced")
    assert not capture_applicable(installation, binding, policy, capture)
