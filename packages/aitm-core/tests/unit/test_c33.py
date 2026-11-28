"""Check normalized paths and stable identity without external operations."""

import pytest
from pydantic import ValidationError

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.verification import CapturedInput, CaptureManifest
from aitm_core.verification.capture import CaptureUnavailable, _relative


def test_manifest_uses_canonical_exact_authority_and_paths():
    source = SourceSnapshot(commit="a" * 40, tree="b" * 40)
    recorded = CapturedInput(
        path="bin/check", origin="tracked", digest="d" * 64, executable=True
    )
    manifest = CaptureManifest(
        authority_store="planning-fixture",
        story=16,
        attempt="attempt",
        binding="binding",
        generation=1,
        branch="refs/heads/story",
        source=source,
        policy=source,
        policy_digest="c" * 64,
        declarations=("extras/*.json",),
        output_roots=("outputs",),
        entries=(recorded,),
    )
    restored = CaptureManifest.model_validate_json(manifest.content)
    assert restored == manifest and restored.digest == manifest.digest
    assert restored.model_copy(update={"generation": 2}).digest != manifest.digest
    assert (
        restored.model_copy(update={"output_roots": ("other",)}).digest
        != manifest.digest
    )

    with pytest.raises(ValidationError, match="unique and sorted"):
        CaptureManifest.model_validate_json(
            manifest.model_copy(update={"entries": (recorded, recorded)}).content
        )

    assert _relative("extras/**/*.json") == "extras/**/*.json"
    for path in ("../*.json", "/tmp/*.json", "a//b", "a/.git/**", "a\\b"):
        with pytest.raises(CaptureUnavailable, match="Unsafe capture path"):
            _relative(path)
