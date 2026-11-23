"""Feed private inbox bytes and persisted rows to real scope and ledger code."""

from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock

from test_ledger import _LedgerRows

from aitm_usage import ledger as ledger_module
from aitm_usage import scopes
from aitm_usage.ledger import Ledger


def attach_scope_inbox_ledger(monkeypatch, ledger):
    rows = _LedgerRows(ledger.identity, ledger_module.APPLICATION_ID, ())
    monkeypatch.setattr(Ledger, "reader", lambda _: rows.connect(write=False))
    monkeypatch.setattr(
        Ledger, "_write_transaction", lambda _: rows.connect(write=True)
    )
    monkeypatch.setattr(Ledger, "writer", lambda writer: nullcontext(writer))
    project, inbox, acks = (
        SimpleNamespace(fd=index, check=Mock()) for index in range(3)
    )
    project.path = ledger.root
    states = {directory.fd: {} for directory in (project, inbox, acks)}

    def pin(path):
        assert path == ledger.root
        return nullcontext(project)

    def child(parent, name, *, create):
        if parent is project and name == scopes.INBOX_NAME:
            return nullcontext(inbox)
        assert parent is inbox and name == scopes.ACKS_NAME and create
        return nullcontext(acks)

    def read(directory, name):
        return states[directory.fd].get(name)

    def publish(directory, name, contents, *, replace_pending=False):
        entries = states[directory.fd]
        if name in entries and not replace_pending:
            return False
        entries[name] = contents
        return True

    def unlink(name, *, dir_fd):
        del states[dir_fd][name]

    monkeypatch.setattr(scopes, "_pin_directory", pin)
    monkeypatch.setattr(scopes, "_private_child", child)
    monkeypatch.setattr(scopes, "_publication", lambda _: nullcontext())
    monkeypatch.setattr(scopes, "_read_private", read)
    monkeypatch.setattr(scopes, "_publish", publish)
    monkeypatch.setattr(
        scopes,
        "os",
        SimpleNamespace(
            listdir=lambda fd: tuple(states[fd]), unlink=unlink, fsync=Mock()
        ),
    )

    def open_ledger(path, project_id=None):
        assert path == ledger.root
        assert project_id in (None, ledger.identity.project_id)
        return ledger

    monkeypatch.setattr(Ledger, "open", staticmethod(open_ledger))
    return rows
