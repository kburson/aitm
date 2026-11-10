"""Private routing journal custody, publication and transaction boundaries."""

import os
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from aitm_usage import _monitor_journal_store as journal
from aitm_usage import host_fs
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_registry import Registry


def _directory(registry: Registry) -> Path:
    return registry.root / "routing-journal-v1"


def _database(registry: Registry) -> Path:
    return _directory(registry) / "journal.sqlite3"


def _key(registry: Registry) -> Path:
    return registry.root / "source-key-v1"


def _sequences(store: journal.JournalStore) -> list[tuple[int]]:
    with store.transaction() as conn:
        return conn.execute("SELECT sequence FROM commits ORDER BY sequence").fetchall()


def test_genesis_is_private_and_retains_exact_identity_on_reopen(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = writer.source_evidence()
        store = journal.JournalStore(writer)
        assert store.evidence == evidence
        assert _sequences(store) == []
        with store.transaction(write=True) as conn:
            conn.execute("INSERT INTO commits VALUES (1)")
        directory = _directory(registry)
        files = tuple(sorted(directory.iterdir()))
        assert {path.name for path in files} == {
            "journal.sqlite3",
            "journal.sqlite3-wal",
            "journal.sqlite3-shm",
        }
        assert directory.stat().st_mode & 0o777 == 0o700
        assert all(path.stat().st_mode & 0o777 == 0o600 for path in files)
        identities = {path: path.stat() for path in (directory, *files)}
    with registry.writer() as writer:
        reopened = journal.JournalStore(writer)
        assert reopened.evidence == evidence
        assert _sequences(reopened) == [(1,)]
        assert all(
            os.path.samestat(info, path.stat()) for path, info in identities.items()
        )


@pytest.mark.parametrize("arrives_during_publication", [False, True])
def test_preexisting_empty_store_is_never_replaced(
    tmp_path, monkeypatch, arrives_during_publication
):
    registry = Registry(tmp_path / "monitor")
    directory = _directory(registry)
    identity = None

    def create_empty_store():
        nonlocal identity
        directory.mkdir(mode=0o700)
        identity = directory.stat()

    def publish_with_competing_target(*args):
        create_empty_store()
        return publish(*args)

    with registry.writer() as writer:
        writer.source_evidence()
        if arrives_during_publication:
            publish = host_fs.publish_noreplace
            monkeypatch.setattr(
                host_fs, "publish_noreplace", publish_with_competing_target
            )
        else:
            create_empty_store()
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        assert identity is not None and os.path.samestat(identity, directory.stat())
        assert list(directory.iterdir()) == []


def test_genesis_refuses_a_replaced_staging_database(tmp_path, monkeypatch):
    registry = Registry(tmp_path / "monitor")
    open_file = os.open

    def replace_staged_database(path, flags, mode=0o777, *, dir_fd=None):
        fd = open_file(path, flags, mode, dir_fd=dir_fd)
        if path == "journal.sqlite3" and flags & os.O_EXCL:
            os.rename(path, "replaced", src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
            replacement = open_file(path, flags, mode, dir_fd=dir_fd)
            os.close(replacement)
        return fd

    with registry.writer() as writer:
        writer.source_evidence()
        monkeypatch.setattr(os, "open", replace_staged_database)
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        assert not _directory(registry).exists()


def test_interrupted_parent_sync_is_confirmed_on_reopen(tmp_path, monkeypatch):
    registry = Registry(tmp_path / "monitor")
    sync = os.fsync
    directory = _directory(registry)
    with registry.writer() as writer:
        evidence = writer.source_evidence()
        root_identity = registry.root.stat()

        def fail_published_root_sync(fd):
            if directory.exists() and os.path.samestat(os.fstat(fd), root_identity):
                raise OSError("injected publication sync failure")
            sync(fd)

        with monkeypatch.context() as patch:
            patch.setattr(os, "fsync", fail_published_root_sync)
            with pytest.raises(LedgerError):
                journal.JournalStore(writer)
        original = directory.stat()
        database = _database(registry).stat()

    confirmed = False

    def record_root_sync(fd):
        nonlocal confirmed
        sync(fd)
        if os.path.samestat(os.fstat(fd), root_identity):
            confirmed = True

    monkeypatch.setattr(os, "fsync", record_root_sync)
    with registry.writer() as writer:
        reopened = journal.JournalStore(writer)
        assert confirmed
        assert reopened.evidence == evidence
        assert _sequences(reopened) == []
        assert os.path.samestat(original, directory.stat())
        assert os.path.samestat(database, _database(registry).stat())


@pytest.mark.parametrize(
    "key_state", ["uninitialized", "unrecorded", "missing", "changed"]
)
def test_attachment_never_initializes_or_adopts_source_key(tmp_path, key_state):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        if key_state in {"missing", "changed"}:
            writer.source_evidence()
        if key_state == "missing":
            _key(registry).unlink()
        if key_state in {"unrecorded", "changed"}:
            _key(registry).write_bytes(b"X" * 32)
            _key(registry).chmod(0o600)
        expected_key_id = writer.view().source_key_id
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        assert writer.view().source_key_id == expected_key_id
        assert not _directory(registry).exists()
        if key_state in {"unrecorded", "changed"}:
            assert _key(registry).read_bytes() == b"X" * 32
        else:
            assert not _key(registry).exists()


@pytest.mark.parametrize(
    "damage",
    [
        "PRAGMA application_id = 0",
        "PRAGMA user_version = 0",
        "ALTER TABLE claims ADD COLUMN unexpected TEXT",
        "UPDATE identity SET key_id = 'foreign'",
        "DELETE FROM identity",
    ],
)
def test_foreign_or_damaged_schema_refuses_without_repair(tmp_path, damage):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        journal.JournalStore(writer)
        database = _database(registry)
        with closing(sqlite3.connect(database)) as conn, conn:
            conn.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
            conn.execute(damage)
        original = database.stat()
        expected_bytes = {
            path: path.read_bytes()
            for path in _directory(registry).iterdir()
            if not path.name.endswith("-shm")
        }
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        assert os.path.samestat(original, database.stat())
        assert {path: path.read_bytes() for path in expected_bytes} == expected_bytes


@pytest.mark.parametrize("suffix", ["", "-wal", "-shm"])
@pytest.mark.parametrize("damage", ["permissions", "symlink", "hardlink", "missing"])
def test_unsafe_database_and_sidecars_refuse_before_open(tmp_path, suffix, damage):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
        path = _database(registry).with_name(_database(registry).name + suffix)
        saved = tmp_path / "original"
        if damage == "permissions":
            path.chmod(0o644)
        elif damage == "hardlink":
            os.link(path, saved)
        else:
            path.rename(saved)
            if damage == "symlink":
                path.symlink_to(saved)
        with pytest.raises(LedgerError):
            _sequences(store)
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        if damage == "missing":
            assert not path.exists()
        if damage == "symlink":
            assert path.is_symlink()


def test_live_handle_refuses_replacement_key_with_identical_bytes(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = writer.source_evidence()
        store = journal.JournalStore(writer)
        key = _key(registry)
        replacement = tmp_path / "replacement"
        shutil.copy2(key, replacement)
        replacement.replace(key)
        with pytest.raises(LedgerError):
            _ = store.evidence
        with pytest.raises(LedgerError):
            _sequences(store)
        assert writer.source_evidence() == evidence


def test_live_handle_refuses_store_swap_and_rolls_back_staged_sequence(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
        directory = _directory(registry)
        saved = registry.root / "saved"
        with pytest.raises(LedgerError):
            with store.transaction(write=True) as conn:
                conn.execute("INSERT INTO commits VALUES (1)")
                directory.rename(saved)
                shutil.copytree(saved, directory)
        shutil.rmtree(directory)
        saved.rename(directory)
        assert _sequences(store) == []


def test_body_failure_rolls_back_private_transaction(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
        with pytest.raises(RuntimeError, match="injected body failure"):
            with store.transaction(write=True) as conn:
                conn.execute("INSERT INTO commits VALUES (1)")
                raise RuntimeError("injected body failure")
        assert _sequences(store) == []


def test_retired_writer_cannot_reopen_or_use_saved_store(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
    with registry.writer() as replacement:
        assert _sequences(journal.JournalStore(replacement)) == []
        with pytest.raises(LedgerError):
            _ = store.evidence
        with pytest.raises(LedgerError):
            _sequences(store)
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
