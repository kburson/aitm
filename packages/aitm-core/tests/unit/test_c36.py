"""Verify the profile generator's path contracts without using host services."""

import sys
from pathlib import Path

import pytest

from aitm_core.verification import containment_macos
from aitm_core.verification.containment_macos import macos_profile, probe_macos


def test_profile_limits_write_access_to_the_output_root():
    profile = macos_profile(
        (Path("/captured/source"), Path("/locked/environment")),
        Path("/test/output"),
        (Path("/tool/uv"),),
    )
    assert '(allow file-write* (subpath "/test/output"))' in profile
    assert '(subpath "/captured/source")' in profile
    assert '(subpath "/locked/environment")' in profile
    assert '(literal "/tool/uv")' in profile
    assert "(deny network*)" in profile
    assert "(deny default)" in profile
    assert '(allow file-read-data (literal "/"))' in profile
    assert '(subpath "/")' not in profile


@pytest.mark.parametrize(
    "inputs,output",
    [
        (("/private/source",), "/private/source/output"),
        (("/private/output/source",), "/private/output"),
        (("/private/output",), "/private/output"),
        (("relative/source",), "/private/output"),
        (("/private/source",), "/"),
        (("/private/source",), "/private/elsewhere/../output"),
    ],
)
def test_profile_refuses_unbounded_or_overlapping_paths(inputs, output):
    with pytest.raises(ValueError, match="containment"):
        macos_profile(tuple(map(Path, inputs)), Path(output), (Path("/tool/uv"),))


def test_profile_quotes_paths_without_creating_rules():
    profile = macos_profile(
        (Path('/source/quote"here'),),
        Path("/scratch/with space"),
        (Path("/tool/back\\slash"),),
    )
    assert r'(subpath "/source/quote\"here")' in profile
    assert '(subpath "/scratch/with space")' in profile
    assert r'(literal "/tool/back\\slash")' in profile


def test_probe_reports_when_the_helper_is_missing(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(containment_macos.os, "access", lambda _path, _mode: False)
    capability = probe_macos()
    assert capability.assurance is None
    assert "missing" in capability.reason


def test_probe_is_unavailable_off_macos(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    capability = probe_macos()
    assert capability.assurance is None
    assert "requires an actual macOS host" in capability.reason
