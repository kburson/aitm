from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from test_ledger import _memory_ledger

from aitm_usage import ledger, monitor_control, scope_admission
from aitm_usage.ledger import Ledger
from aitm_usage.monitor_registry import (
    RegisteredProject,
    Registry,
    RegistryView,
    _PhysicalDirectory,
    _ServiceEvidence,
)


class MonitorInboxFiles:
    """Supply queued bytes and pinned identities to the real monitor inbox."""

    def __init__(self, monkeypatch, project_id, *, writer=None):
        self.descriptors = {}
        self.identities = {}
        self.ledger = _memory_ledger(ledger, project_id, b"p" * 32)
        if writer is None:
            self.root = Path("/fixture/monitor")
            self.files = {self.root: {}, self.ledger.root: {}}
            evidence = _ServiceEvidence(b"a" * 32)
            state = self.identity(str(self.ledger.root))
            view = RegistryView(
                projects=(
                    RegisteredProject(project_id, state, "Fixture", None, (), None),
                ),
                source_key_id=evidence.key_id,
            )
            writer = Registry(self.root, Mock())
            monkeypatch.setattr(writer, "source_evidence", lambda: evidence)
        else:
            self.root = writer.root
            view = writer.view()
            evidence = writer.source_evidence()
            state = scope_admission._project(view, project_id).state
            self.ledger = replace(self.ledger, root=Path(state.path))
            self.files = {self.root: {}, self.ledger.root: {}}
            self.identities[state.path] = state
        self.files[self.root][scope_admission._SOURCE_KEY_FILE] = evidence.key
        self.writer = writer
        self.inbox = monitor_control.ControlInbox(self.root)

        def read_registry(registry, **kwargs):
            assert registry.root == self.root
            return view

        def open_ledger(root, requested_project):
            assert root == self.ledger.root and requested_project == project_id
            return self.ledger

        monkeypatch.setattr(Registry, "view", read_registry)
        monkeypatch.setattr(Registry, "command_status", Mock(return_value=None))
        monkeypatch.setattr(Ledger, "open", open_ledger)
        host = SimpleNamespace(
            listdir=self.listdir, unlink=self.unlink, fsync=Mock(), stat=self.stat
        )
        for module in (scope_admission, monitor_control):
            monkeypatch.setattr(module, "_pin_directory", self.pin)
            monkeypatch.setattr(module, "_private_child", self.child)
            monkeypatch.setattr(module, "_read_private", self.read)
            monkeypatch.setattr(module, "_publish", self.publish)
            monkeypatch.setattr(module, "_path_exists", self.files.__contains__)
            monkeypatch.setattr(module, "os", host)
        monkeypatch.setattr(scope_admission, "_directory", self.identity)
        monkeypatch.setattr(monitor_control, "_publication", lambda _: nullcontext())
        monkeypatch.setattr(monitor_control, "_ensure_private_directory", self.ensure)

    @property
    def inbox_files(self):
        return self.files[self.root / monitor_control.INBOX_NAME]

    def grant_files(self, grant_id):
        return self.files[self.root / scope_admission._GRANTS / str(grant_id)]

    def identity(self, name, *, private=True):
        assert private
        if name in self.identities:
            return self.identities[name]
        entries = tuple(self.files)
        return _PhysicalDirectory(name, (1, entries.index(Path(name)) + 1))

    def ensure(self, path):
        self.files.setdefault(path, {})

    def pin(self, path):
        assert path in self.files
        fd = self.identity(str(path)).identity[-1]
        self.descriptors[fd] = path
        return nullcontext(SimpleNamespace(path=path, fd=fd, check=Mock()))

    def child(self, parent, name, *, create):
        path = parent.path / name
        if create:
            self.ensure(path)
        return self.pin(path) if path in self.files else nullcontext(None)

    def read(self, directory, name):
        return self.files[directory.path].get(name)

    def publish(self, directory, name, data, *, before_commit=None):
        if before_commit is not None:
            before_commit()
        entries = self.files[directory.path]
        if name in entries:
            return False
        entries[name] = data
        return True

    def listdir(self, fd):
        return tuple(self.files[self.descriptors[fd]])

    def unlink(self, name, *, dir_fd):
        del self.files[self.descriptors[dir_fd]][name]

    def stat(self, name, *, dir_fd, follow_symlinks):
        assert not follow_symlinks
        if name not in self.files[self.descriptors[dir_fd]]:
            raise FileNotFoundError(name)
        return object()
