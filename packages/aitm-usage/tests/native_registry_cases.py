"""Attach a real monitor registry to synthetic native files and host custody."""

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from monitor_inbox_cases import MonitorInboxFiles

from aitm_usage import monitor_registry
from aitm_usage._monitor_qualification import _LiveProfile


def native_registry_policy(
    monkeypatch, native, *, control, projects, installations, evidence
):
    directories = {
        item.path: item
        for item in (
            control,
            *(project.state for project in projects),
            *(anchor for project in projects for anchor in project.anchors),
            *(item.directory for item in installations),
        )
    }
    paths = {Path(name) for name in directories}
    real_resolve = Path.resolve

    def resolve(path, *args, **kwargs):
        if path in paths:
            return path
        return real_resolve(path, *args, **kwargs)

    def directory(path, **_):
        try:
            return directories[path]
        except KeyError:
            raise FileNotFoundError(path) from None

    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setattr(monitor_registry, "_directory", directory)
    monkeypatch.setattr(monitor_registry, "_probe", native._snapshot)
    initial = monitor_registry.RegistryView(
        projects=projects,
        source_key_id=evidence.key_id,
    )
    root = Path(control.path)
    writer = monitor_registry.Registry(root, Mock())
    with monkeypatch.context() as setup:
        setup.setattr(writer, "source_evidence", lambda: evidence)
        files = MonitorInboxFiles(
            monkeypatch, projects[0].project_id, writer=writer, initial_view=initial
        )
    monkeypatch.setattr(monitor_registry, "_read_private", files.read)

    @contextmanager
    def open_writer(registry):
        assert registry.root == root
        lease = Mock()
        writer = monitor_registry.Registry(root, lease)
        writer._live_profile = _LiveProfile(
            control,
            lease,
            evidence.pseudonymize("generation", "fixture"),
            installations,
            lambda _: True,
        )
        try:
            yield writer
        finally:
            writer._writer = None

    monkeypatch.setattr(monitor_registry.Registry, "writer", open_writer)
    return SimpleNamespace(
        registry=monitor_registry.Registry(root),
        inbox=files.inbox,
        files=files,
    )
