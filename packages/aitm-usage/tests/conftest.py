import pytest


@pytest.fixture
def legacy_monitor_qualification(tmp_path, monkeypatch):
    """Retain the older native substrate behaviors inside these tests only."""
    from aitm_usage.monitor_registry import Registry

    require = Registry._require_live_source
    fixture_authority = object()

    def require_live_source(writer, approved, **kwargs):
        if writer.root.is_relative_to(tmp_path):
            return fixture_authority
        return require(writer, approved, **kwargs)

    monkeypatch.setattr(Registry, "_require_live_source", require_live_source)
    return require
