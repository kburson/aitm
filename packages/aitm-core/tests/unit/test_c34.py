"""Prove captured wheel custody and the exact environment cache address."""

import pytest
from pydantic import ValidationError

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.verification import CapturedInput, CapturedInputs, CaptureManifest
from aitm_core.verification.provision import (
    EnvironmentIdentity,
    EnvironmentReceipt,
    ProvisionTools,
    ProvisionUnavailable,
    _lock_inputs,
)


def test_environment_identity_binds_lock_tools_policy_and_artifact(tmp_path):
    source = SourceSnapshot(commit="a" * 40, tree="b" * 40)
    tools = ProvisionTools(
        installer="/usr/bin/uv",
        installer_version="uv fixture",
        installer_digest="c" * 64,
        python="/usr/bin/python",
        python_version="3.13",
        python_digest="d" * 64,
        platform="fixture-platform",
    )
    manifest = CaptureManifest(
        authority_store="test-store",
        story=16,
        attempt="fixture",
        binding="fixture-binding",
        generation=1,
        branch="refs/heads/fixture",
        source=source,
        policy=source,
        policy_digest="e" * 64,
        declarations=(),
        output_roots=(),
        entries=tuple(
            CapturedInput(
                path=path, origin="tracked", digest=digit * 64, executable=False
            )
            for path, digit in zip(
                ("pyproject.toml", "uv.lock", "wheels/fixture.whl"), "123"
            )
        ),
    )
    capture = CapturedInputs(tmp_path, manifest)
    capture.source_directory.mkdir()
    lock = capture.source_directory / "uv.lock"
    document = """version = 1
[[package]]
name = "fixture"
source = { path = "wheels/fixture.whl" }
wheels = [{ filename = "fixture.whl", hash = "sha256:%s" }]
"""
    lock.write_text(document % ("4" * 64))
    with pytest.raises(ProvisionUnavailable, match="captured hash disagrees"):
        _lock_inputs(capture)
    lock.write_text(document % ("3" * 64))
    project, lock_digest = _lock_inputs(capture)
    identity = EnvironmentIdentity(
        capture=manifest.digest,
        source=source,
        project_digest=project,
        lock_digest=lock_digest,
        policy=source,
        policy_digest=manifest.policy_digest,
        tools=tools,
    )
    for change in (
        {"capture": "f" * 64},
        {"lock_digest": "f" * 64},
        {"policy_digest": "f" * 64},
        {"tools": tools.model_copy(update={"python_digest": "f" * 64})},
    ):
        assert identity.model_copy(update=change).digest != identity.digest
    with pytest.raises(ValidationError, match="pattern"):
        EnvironmentReceipt(
            identity=identity, runtime="../someone-else", inventory_digest="a" * 64
        )
