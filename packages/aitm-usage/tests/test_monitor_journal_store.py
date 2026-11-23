"""Private routing journal custody, publication and transaction boundaries."""

import os
import shutil
import sqlite3
import stat
from contextlib import closing, contextmanager, nullcontext
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, Mock, call

import pytest

from aitm_usage import _monitor_journal_store as journal
from aitm_usage import host_fs, ledger, monitor_registry
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_registry import Registry, RegistryView, _ServiceEvidence

_V1_APPLICATION_ID = 0x4149544A
# Exact schema from the last v1 writer, before any upgrade code existed.
_V1_SCHEMA = """
CREATE TABLE identity (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    key_id TEXT NOT NULL
) STRICT;
CREATE TABLE commits (
    sequence INTEGER PRIMARY KEY
) STRICT;
CREATE TABLE claims (
    key TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    digest TEXT NOT NULL,
    payload BLOB NOT NULL,
    sequence INTEGER NOT NULL REFERENCES commits
) STRICT;
CREATE TABLE disputes (
    key TEXT NOT NULL REFERENCES claims(key),
    contender TEXT NOT NULL,
    digest TEXT NOT NULL,
    evidence BLOB NOT NULL,
    sequence INTEGER NOT NULL REFERENCES commits,
    PRIMARY KEY (key, contender, digest, evidence)
) STRICT;
CREATE TABLE progress (
    source TEXT NOT NULL,
    surface TEXT NOT NULL,
    stream TEXT NOT NULL,
    locator TEXT NOT NULL,
    incarnation TEXT NOT NULL,
    sequence INTEGER NOT NULL REFERENCES commits,
    cursor BLOB NOT NULL,
    PRIMARY KEY (source, surface, stream, locator, incarnation, sequence)
) STRICT;
"""
_V1_TABLES = ("identity", "commits", "claims", "disputes", "progress")
# Exact additive DDL from the last v2 writer, retained independently of v3.
_V2_REVISION_SCHEMA = """
CREATE TABLE claim_revisions (
    key TEXT NOT NULL REFERENCES claims(key),
    sequence INTEGER NOT NULL REFERENCES commits,
    later_ordinal INTEGER NOT NULL,
    material TEXT NOT NULL,
    predecessor TEXT NOT NULL,
    payload BLOB NOT NULL,
    PRIMARY KEY (key, sequence, later_ordinal),
    UNIQUE (key, material)
) STRICT;
"""
_V3_CONTENT_SCHEMA = """
CREATE TABLE content_disputes (
    key TEXT PRIMARY KEY REFERENCES claims(key),
    sequence INTEGER NOT NULL REFERENCES commits,
    payload BLOB NOT NULL
) STRICT;
"""
_V4_DISPOSITION_SCHEMA = """
CREATE TABLE route_dispositions (
    command TEXT PRIMARY KEY,
    hold TEXT NOT NULL UNIQUE,
    sequence INTEGER NOT NULL UNIQUE REFERENCES commits,
    payload BLOB NOT NULL
) STRICT;
"""


def _directory(registry: Registry) -> Path:
    return registry.root / "routing-journal-v1"


def _database(registry: Registry) -> Path:
    return _directory(registry) / "journal.sqlite3"


def _key(registry: Registry) -> Path:
    return registry.root / "source-key-v1"


def _sequences(store: journal.JournalStore) -> list[tuple[int]]:
    with store.transaction() as conn:
        return conn.execute("SELECT sequence FROM commits ORDER BY sequence").fetchall()


@contextmanager
def _sqlite(database):
    with closing(sqlite3.connect(database)) as conn, conn:
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
        yield conn


def _create_v1_store(writer):
    evidence = writer.source_evidence()
    _directory(writer).mkdir(mode=0o700)
    database = _database(writer)
    database.touch(mode=0o600)
    with _sqlite(database) as conn:
        assert conn.execute("PRAGMA journal_mode=WAL").fetchone() == ("wal",)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript("BEGIN IMMEDIATE;\n" + _V1_SCHEMA)
        conn.execute(f"PRAGMA application_id = {_V1_APPLICATION_ID}")
        conn.execute("PRAGMA user_version = 1")
        conn.execute("INSERT INTO identity VALUES (1, ?)", (evidence.key_id,))
        conn.executemany("INSERT INTO commits VALUES (?)", [(1,), (2,)])
        conn.execute(
            "INSERT INTO claims VALUES ('key', 'project', 'digest', x'00ff', 1)"
        )
        conn.execute(
            "INSERT INTO disputes VALUES ('key', 'contender', 'other', x'fe01', 2)"
        )
        conn.execute(
            "INSERT INTO progress VALUES ('source', 'surface', 'stream', 'locator',"
            " 'incarnation', 1, x'0102')"
        )
    return evidence


def _create_v2_store(writer):
    evidence = _create_v1_store(writer)
    with _sqlite(_database(writer)) as conn:
        conn.execute(_V2_REVISION_SCHEMA)
        conn.execute("PRAGMA user_version = 2")
        conn.execute("INSERT INTO commits VALUES (3)")
        conn.executemany(
            "INSERT INTO claim_revisions VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("key", 2, 7, "revision-2", "digest", b"\x00revision-2\xff"),
                ("key", 3, 9, "revision-3", "revision-2", b"\x00revision-3\xfe"),
            ],
        )
    return evidence


def _create_v3_store(writer):
    evidence = _create_v2_store(writer)
    with _sqlite(_database(writer)) as conn:
        conn.execute(_V3_CONTENT_SCHEMA)
        conn.execute("PRAGMA user_version = 3")
        conn.execute("INSERT INTO content_disputes VALUES ('key', 3, x'00ff')")
    return evidence


def _create_legacy_store(writer, version):
    return {1: _create_v1_store, 2: _create_v2_store, 3: _create_v3_store}[version](
        writer
    )


def _legacy_rows(conn, version):
    names = _V1_TABLES
    if version >= 2:
        names += ("claim_revisions",)
    if version >= 3:
        names += ("content_disputes",)
    return {
        name: conn.execute(f"SELECT * FROM {name} ORDER BY rowid").fetchall()
        for name in names
    }


def _schema_objects(conn):
    return conn.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name"
    ).fetchall()


def _storage_identity(registry):
    directory = _directory(registry)
    return {
        path: path.stat() for path in (directory, _key(registry), *directory.iterdir())
    }


def _assert_storage_identity(identities):
    assert all(os.path.samestat(info, path.stat()) for path, info in identities.items())


def _durable_bytes(registry):
    return {
        path: path.read_bytes()
        for path in _directory(registry).iterdir()
        if not path.name.endswith("-shm")
    }


def _assert_exact_legacy_upgrade(tmp_path, monkeypatch, version):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = _create_legacy_store(writer, version)
        identities = _storage_identity(registry)
        with _sqlite(_database(registry)) as conn:
            original_schema = _schema_objects(conn)
            original_rows = _legacy_rows(conn, version)
            old_tip = conn.execute("SELECT max(sequence) FROM commits").fetchone()
        statements = []
        open_database = journal._open

        @contextmanager
        def trace_migration(database, *, write):
            with open_database(database, write=write) as conn:
                if write:
                    conn.set_trace_callback(statements.append)
                yield conn

        with monkeypatch.context() as patch:
            patch.setattr(journal, "_open", trace_migration)
            store = journal.JournalStore(writer)
        _assert_upgrade_trace(statements, version)
        assert store.evidence == evidence
        with store.transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (4,)
            assert conn.execute("PRAGMA application_id").fetchone() == (
                _V1_APPLICATION_ID,
            )
            assert _legacy_rows(conn, version) == original_rows
            assert (
                conn.execute("SELECT max(sequence) FROM commits").fetchone() == old_tip
            )
            assert conn.execute("SELECT key_id FROM identity").fetchone() == (
                evidence.key_id,
            )
            assert conn.execute("SELECT * FROM route_dispositions").fetchall() == []
            new_schema = _schema_objects(conn)
            added = {"route_dispositions"}
            if version < 3:
                added.add("content_disputes")
                assert conn.execute("SELECT * FROM content_disputes").fetchall() == []
            if version == 1:
                added.add("claim_revisions")
                assert conn.execute("SELECT * FROM claim_revisions").fetchall() == []
            assert [row for row in new_schema if row[2] not in added] == original_schema
    with registry.writer() as writer:
        with journal.JournalStore(writer).transaction() as conn:
            assert _legacy_rows(conn, version) == original_rows
        _assert_storage_identity(identities)
    with _sqlite(":memory:") as conn:
        conn.executescript(
            _V1_SCHEMA
            + _V2_REVISION_SCHEMA
            + _V3_CONTENT_SCHEMA
            + _V4_DISPOSITION_SCHEMA
        )
        assert _schema_objects(conn) == new_schema
    fresh = Registry(tmp_path / "fresh")
    with fresh.writer() as writer:
        writer.source_evidence()
        with journal.JournalStore(writer).transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (4,)
            assert _schema_objects(conn) == new_schema


def test_exact_v1_upgrade_preserves_rows_and_matches_fresh_v2(tmp_path, monkeypatch):
    # Retain the baseline node ID after later schema upgrades.
    _assert_exact_legacy_upgrade(tmp_path, monkeypatch, 1)


def test_exact_v2_upgrade_preserves_rows_and_matches_fresh_v3(tmp_path, monkeypatch):
    _assert_exact_legacy_upgrade(tmp_path, monkeypatch, 2)


def test_exact_v3_upgrade_preserves_rows_and_matches_fresh_v4(tmp_path, monkeypatch):
    _assert_exact_legacy_upgrade(tmp_path, monkeypatch, 3)


def _assert_legacy_upgrade_rolls_back(tmp_path, monkeypatch, failure, version):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _create_legacy_store(writer, version)
        identities = _storage_identity(registry)
        expected_bytes = _durable_bytes(registry)
        with _sqlite(_database(registry)) as conn:
            original_schema = _schema_objects(conn)
            original_rows = _legacy_rows(conn, version)

        directory = _directory(registry)
        saved = registry.root / "saved"
        open_database = journal._open
        check_store = journal.JournalStore._check_store
        migration = None
        interrupted = False

        @contextmanager
        def observe_write_connection(database, *, write):
            nonlocal migration
            with open_database(database, write=write) as conn:
                if write:
                    migration = conn
                yield conn

        def fail_precommit(store, root, pin):
            nonlocal interrupted
            if (
                migration is not None
                and migration.in_transaction
                and migration.execute("PRAGMA user_version").fetchone() == (4,)
            ):
                assert (
                    migration.execute("SELECT * FROM route_dispositions").fetchall()
                    == []
                )
                assert _legacy_rows(migration, version) == original_rows
                if version == 1:
                    assert (
                        migration.execute("SELECT * FROM claim_revisions").fetchall()
                        == []
                    )
                interrupted = True
                if failure == "interrupt":
                    raise RuntimeError("injected interruption after migration DDL")
                directory.rename(saved)
                shutil.copytree(saved, directory)
            check_store(store, root, pin)

        with monkeypatch.context() as patch:
            patch.setattr(journal, "_open", observe_write_connection)
            patch.setattr(journal.JournalStore, "_check_store", fail_precommit)
            error = RuntimeError if failure == "interrupt" else LedgerError
            with pytest.raises(error):
                journal.JournalStore(writer)
        assert interrupted
        if failure == "replace-directory":
            shutil.rmtree(directory)
            saved.rename(directory)
        _assert_storage_identity(identities)
        assert _durable_bytes(registry) == expected_bytes
        with _sqlite(_database(registry)) as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (version,)
            assert _schema_objects(conn) == original_schema
            assert _legacy_rows(conn, version) == original_rows
        with journal.JournalStore(writer).transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (4,)
            assert _legacy_rows(conn, version) == original_rows


@pytest.mark.parametrize("failure", ["interrupt", "replace-directory"])
def test_v1_upgrade_rolls_back_after_ddl_and_can_retry(tmp_path, monkeypatch, failure):
    _assert_legacy_upgrade_rolls_back(tmp_path, monkeypatch, failure, 1)


@pytest.mark.parametrize("failure", ["interrupt", "replace-directory"])
def test_v2_upgrade_rolls_back_after_ddl_and_can_retry(monkeypatch, failure):
    _observe_upgrade_requests(monkeypatch, 2, failure=failure)


@pytest.mark.parametrize("failure", ["interrupt", "replace-directory"])
def test_v3_upgrade_rolls_back_after_ddl_and_can_retry(monkeypatch, failure):
    _observe_upgrade_requests(monkeypatch, 3, failure=failure)


def _journal_metadata(monkeypatch, version, damage=None):
    expected_schema = (("table", "identity", "identity", "fixture identity DDL"),)
    observed_schema = expected_schema
    values = {
        "PRAGMA application_id": (journal._APPLICATION_ID,),
        "PRAGMA user_version": (version,),
        "PRAGMA journal_mode": ("wal",),
        "SELECT singleton, key_id FROM identity": [(1, "fixture-key")],
        "PRAGMA foreign_key_check": None,
    }
    if damage == "PRAGMA application_id = 0":
        values["PRAGMA application_id"] = (0,)
    elif damage is not None and damage.startswith("PRAGMA user_version = "):
        stored_version = int(damage.rsplit(" ", 1)[-1])
        values["PRAGMA user_version"] = (stored_version,)
        observed_schema += (("table", f"unexpected-v{version}", "legacy", None),)
    elif damage is not None and damage.startswith(("CREATE TABLE ", "ALTER TABLE ")):
        observed_schema += (("table", "unexpected", "unexpected", None),)
    elif damage == "UPDATE identity SET key_id = 'foreign'":
        values["SELECT singleton, key_id FROM identity"] = [(1, "foreign")]
    elif damage == "DELETE FROM identity":
        values["SELECT singleton, key_id FROM identity"] = []
    elif damage == "UPDATE claims SET sequence = 999":
        values["PRAGMA foreign_key_check"] = ("claims", 1, "commits", 0)
    else:
        assert damage is None

    def read(sql):
        result = values[sql]
        return Mock(
            fetchone=Mock(return_value=result), fetchall=Mock(return_value=result)
        )

    connection = Mock(spec=sqlite3.Connection)
    connection.execute.side_effect = read
    monkeypatch.setattr(journal, "_schema_objects", lambda conn: observed_schema)
    monkeypatch.setattr(journal, "_supported_schema", lambda version: expected_schema)
    return connection


@pytest.mark.parametrize(
    ("damage", "message"),
    [
        ("PRAGMA application_id = 0", "application"),
        pytest.param(
            "PRAGMA user_version = 3",
            "table schema",
            id="PRAGMA user_version = 3-schema version",
        ),
        ("PRAGMA user_version = 2", "table schema"),
        ("CREATE TABLE claim_revisions (key TEXT) STRICT", "table schema"),
        ("UPDATE identity SET key_id = 'foreign'", "source key identity"),
        ("UPDATE claims SET sequence = 999", "foreign key"),
    ],
)
def test_invalid_v1_is_refused_before_upgrade(monkeypatch, damage, message):
    connection = _journal_metadata(monkeypatch, 1, damage)

    with pytest.raises(LedgerError, match=message):
        journal._validate_identity(connection, "fixture-key", version=None)
        journal._validate_foreign_keys(connection)


def test_damaged_legacy_store_is_left_byte_for_byte_unchanged(tmp_path):
    damage = "UPDATE claims SET sequence = 999"
    message = "foreign key"
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _create_v1_store(writer)
        with _sqlite(_database(registry)) as conn:
            conn.execute(damage)
        identities = _storage_identity(registry)
        expected_bytes = _durable_bytes(registry)
        with pytest.raises(LedgerError, match=message):
            journal.JournalStore(writer)
        _assert_storage_identity(identities)
        assert _durable_bytes(registry) == expected_bytes


def test_exact_v1_validation_refuses_v2_without_modifying_either_store(monkeypatch):
    v1 = _journal_metadata(monkeypatch, 1)
    v2 = _journal_metadata(monkeypatch, 2)
    assert journal._validate_identity(v1, "fixture-key", version=1) == 1
    with pytest.raises(LedgerError, match="schema version"):
        journal._validate_identity(v2, "fixture-key", version=1)

    header_reads = [("PRAGMA application_id",), ("PRAGMA user_version",)]
    assert [call.args for call in v1.execute.call_args_list] == [
        *header_reads,
        ("PRAGMA journal_mode",),
        ("SELECT singleton, key_id FROM identity",),
    ]
    assert [call.args for call in v2.execute.call_args_list] == header_reads
    v1.commit.assert_not_called()
    v2.commit.assert_not_called()


def test_revision_table_enforces_foreign_keys_and_uniqueness_in_writes(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _create_v1_store(writer)
        with journal.JournalStore(writer).transaction(write=True) as conn:
            assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
            assert conn.execute("PRAGMA synchronous").fetchone() == (2,)
            insert = "INSERT INTO claim_revisions VALUES (?, ?, ?, ?, ?, ?)"
            for key, sequence in [("missing", 1), ("key", 999)]:
                with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
                    conn.execute(insert, (key, sequence, 7, "new", "old", b"payload"))
            conn.execute(insert, ("key", 2, 7, "new", "old", b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
                conn.execute(insert, ("key", 2, 8, "new", "old", b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
                conn.execute(insert, ("key", 2, 7, "another", "old", b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="cannot store TEXT"):
                conn.execute(insert, ("key", 2, 8, "another", "old", "invalid"))


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
        database = _database(registry)
        database.chmod(0o644)
        try:
            with pytest.raises(LedgerError, match="Unsafe private ledger path"):
                _sequences(reopened)
            with pytest.raises(LedgerError, match="Unsafe private ledger path"):
                journal.JournalStore(writer)
        finally:
            database.chmod(0o600)
        assert _sequences(reopened) == [(1,)]
        saved = tmp_path / "displaced-database"
        database.rename(saved)
        try:
            with pytest.raises(LedgerError, match="unavailable"):
                _sequences(reopened)
            with pytest.raises(LedgerError, match="unavailable"):
                journal.JournalStore(writer)
            assert not database.exists()
        finally:
            saved.rename(database)
        assert _sequences(reopened) == [(1,)]


@pytest.mark.parametrize("arrives_during_publication", [False, True])
def test_preexisting_empty_store_is_never_replaced(
    request, monkeypatch, arrives_during_publication
):
    if not arrives_during_publication:
        memory = _journal_observations(monkeypatch)
        for name in journal._FILES:
            del memory.files[memory.store / name]
        before = dict(memory.files)
        create = Mock(side_effect=AssertionError("attachment tried to replace a store"))
        monkeypatch.setattr(journal.JournalStore, "_create", create)
        with pytest.raises(LedgerError, match="unavailable"):
            journal.JournalStore(memory.writer)
        assert memory.files == before
        create.assert_not_called()
        memory.open_database.assert_not_called()
        return

    tmp_path = request.getfixturevalue("tmp_path")
    registry = Registry(tmp_path / "monitor")
    directory = _directory(registry)
    identity = None
    publish = host_fs.publish_noreplace

    def publish_with_competing_target(*args):
        nonlocal identity
        directory.mkdir(mode=0o700)
        identity = directory.stat()
        return publish(*args)

    with registry.writer() as writer:
        writer.source_evidence()
        monkeypatch.setattr(host_fs, "publish_noreplace", publish_with_competing_target)
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
def test_attachment_never_initializes_or_adopts_source_key(
    request, monkeypatch, key_state
):
    if key_state != "missing":
        memory = _journal_observations(monkeypatch)
        if key_state != "changed":
            memory.writer.view = Mock(return_value=RegistryView())
        for path in tuple(memory.files):
            if path.is_relative_to(memory.store):
                del memory.files[path]
        key_path = _key(memory.writer)
        if key_state == "uninitialized":
            del memory.files[key_path]
        message = "requires an initialized source key"
        if key_state == "changed":
            journal._read_private.return_value = b"X" * 32
            message = "Routing journal source key changed"
        before = dict(memory.files)
        expected_key_id = memory.writer.view().source_key_id
        with pytest.raises(LedgerError, match=message):
            journal.JournalStore(memory.writer)
        assert memory.writer.view().source_key_id == expected_key_id
        assert memory.files == before
        memory.writer.source_evidence.assert_not_called()
        if key_state == "changed":
            memory.pin.assert_called_once_with(memory.writer.root)
            assert journal._read_private.call_args.args[1] == journal._SOURCE_KEY_FILE
            assert journal._read_private.return_value == b"X" * 32
        else:
            memory.pin.assert_not_called()
        memory.open_database.assert_not_called()
        return

    tmp_path = request.getfixturevalue("tmp_path")
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        _key(registry).unlink()
        expected_key_id = writer.view().source_key_id
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        assert writer.view().source_key_id == expected_key_id
        assert not _directory(registry).exists()
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
def test_foreign_or_damaged_schema_refuses_without_repair(monkeypatch, damage):
    connection = _journal_metadata(monkeypatch, journal._SCHEMA_VERSION, damage)

    with pytest.raises(LedgerError):
        journal._validate_identity(connection, "fixture-key", version=None)


def test_damaged_current_store_is_left_byte_for_byte_unchanged(tmp_path):
    damage = "ALTER TABLE claims ADD COLUMN unexpected TEXT"
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


_PHYSICAL_STORE_CASES = {
    ("hardlink", "-wal"),
    ("symlink", "-shm"),
}


def _journal_observations(monkeypatch):
    key = b"j" * 32
    evidence = _ServiceEvidence(key)
    root_path = Path("/fixture/monitor")
    store_path = root_path / journal._STORE
    root_ids = ((1, 1), (1, 2))
    root = SimpleNamespace(path=root_path, identities=root_ids, check=Mock(), fd=3)
    folder = SimpleNamespace(
        path=store_path, identities=(*root_ids, (1, 3)), check=Mock()
    )
    lease = SimpleNamespace(identities=(*root_ids, (1, 4)), check=Mock())
    view = RegistryView(source_key_id=sha256(key).hexdigest())
    writer = SimpleNamespace(
        root=root_path,
        lease=lease,
        view=lambda: view,
        source_evidence=Mock(return_value=evidence),
    )
    files = {
        path: SimpleNamespace(
            st_mode=stat.S_IFREG | 0o600,
            st_nlink=1,
            st_uid=os.geteuid(),
            st_dev=1,
            st_ino=index,
        )
        for index, path in enumerate(
            [
                root_path / journal._SOURCE_KEY_FILE,
                *(store_path / name for name in journal._FILES),
            ],
            start=5,
        )
    }
    files[store_path] = SimpleNamespace(st_mode=stat.S_IFDIR | 0o700)

    def lstat(path):
        try:
            return files[path]
        except KeyError:
            raise FileNotFoundError(path) from None

    connection = MagicMock()
    connection.execute.return_value.fetchall.return_value = []
    open_database = Mock(return_value=nullcontext(connection))
    monkeypatch.setattr(Path, "lstat", lstat)
    monkeypatch.setattr(ledger, "_check_acl", Mock())
    pinned = {root_path: root, store_path: folder}
    pin = Mock(side_effect=lambda path: nullcontext(pinned[path]))
    monkeypatch.setattr(journal, "_pin_directory", pin)
    monkeypatch.setattr(journal, "_read_private", Mock(return_value=key))
    monkeypatch.setattr(journal, "_open", open_database)
    monkeypatch.setattr(
        journal, "_validate_identity", Mock(return_value=journal._SCHEMA_VERSION)
    )
    monkeypatch.setattr(journal, "os", SimpleNamespace(fsync=Mock()))
    return SimpleNamespace(
        writer=writer,
        store=store_path,
        directory=folder,
        files=files,
        pin=pin,
        open_database=open_database,
    )


def _assert_journal_path_policy_refuses_open(monkeypatch, suffix, damage):
    memory = _journal_observations(monkeypatch)
    writer, store_path = memory.writer, memory.store
    open_database, files = memory.open_database, memory.files
    store = journal.JournalStore(writer)
    open_database.assert_called_once_with(store_path / journal._DATABASE, write=False)
    open_database.reset_mock()

    path = store_path / (journal._DATABASE + suffix)
    if damage == "permissions":
        files[path].st_mode = stat.S_IFREG | 0o644
    elif damage == "hardlink":
        files[path].st_nlink = 2
    elif damage == "symlink":
        files[path].st_mode = stat.S_IFLNK | 0o777
    else:
        del files[path]

    message = "unavailable" if damage == "missing" else "Unsafe private ledger path"
    with pytest.raises(LedgerError, match=message):
        _sequences(store)
    with pytest.raises(LedgerError, match=message):
        journal.JournalStore(writer)
    open_database.assert_not_called()


@pytest.mark.parametrize("suffix", ["", "-wal", "-shm"])
@pytest.mark.parametrize("damage", ["permissions", "symlink", "hardlink", "missing"])
def test_unsafe_database_and_sidecars_refuse_before_open(
    request, monkeypatch, suffix, damage
):
    if (damage, suffix) not in _PHYSICAL_STORE_CASES:
        _assert_journal_path_policy_refuses_open(monkeypatch, suffix, damage)
        return

    tmp_path = request.getfixturevalue("tmp_path")
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
        path = _database(registry).with_name(_database(registry).name + suffix)
        saved = tmp_path / "original"
        if damage == "hardlink":
            os.link(path, saved)
        else:
            path.rename(saved)
            path.symlink_to(saved)
        with pytest.raises(LedgerError):
            _sequences(store)
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        if damage == "symlink":
            assert path.is_symlink()


def test_live_handle_refuses_replacement_key_with_identical_bytes(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = writer.source_evidence()
        key = _key(registry)
        original = key.read_bytes()
        key_id = writer.view().source_key_id
        key.write_bytes(b"X" * 32)
        try:
            with pytest.raises(LedgerError, match="Routing journal source key changed"):
                journal.JournalStore(writer)
            assert key.read_bytes() == b"X" * 32
            assert writer.view().source_key_id == key_id
            assert not _directory(registry).exists()
        finally:
            key.write_bytes(original)
        store = journal.JournalStore(writer)
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
        with pytest.raises(RuntimeError, match="injected body failure"):
            with store.transaction(write=True) as conn:
                conn.execute("INSERT INTO commits VALUES (1)")
                raise RuntimeError("injected body failure")
        assert _sequences(store) == []


def test_body_failure_rolls_back_private_transaction(monkeypatch):
    memory = _journal_observations(monkeypatch)
    store = journal.JournalStore(memory.writer)
    connection = MagicMock(spec=sqlite3.Connection)
    memory.open_database.reset_mock()
    memory.open_database.return_value = nullcontext(connection)
    failure = RuntimeError("injected body failure")

    with pytest.raises(RuntimeError, match="injected body failure") as error:
        with store.transaction(write=True) as conn:
            assert conn is connection
            conn.execute("INSERT INTO commits VALUES (1)")
            raise failure

    assert error.value is failure
    memory.open_database.assert_called_once_with(
        memory.store / journal._DATABASE, write=True
    )
    assert connection.execute.call_args_list == [
        call("BEGIN IMMEDIATE"),
        call("INSERT INTO commits VALUES (1)"),
    ]
    connection.__exit__.assert_called_once_with(RuntimeError, failure, ANY)
    connection.commit.assert_not_called()


def test_retired_writer_cannot_reopen_or_use_saved_store(monkeypatch):
    memory = _journal_observations(monkeypatch)
    registry = Registry(memory.writer.root)
    monkeypatch.setattr(monitor_registry, "_ensure_private_directory", Mock())
    monkeypatch.setattr(
        monitor_registry,
        "_lease",
        lambda path, *, create: nullcontext(
            SimpleNamespace(identities=memory.writer.lease.identities, check=Mock())
        ),
    )
    monkeypatch.setattr(Registry, "view", lambda self: memory.writer.view())
    monkeypatch.setattr(
        Registry, "source_evidence", lambda self: memory.writer.source_evidence()
    )

    with registry.writer() as writer:
        store = journal.JournalStore(writer)
    with registry.writer() as replacement:
        assert _sequences(journal.JournalStore(replacement)) == []
        memory.pin.reset_mock()
        memory.open_database.reset_mock()
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            _ = store.evidence
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            _sequences(store)
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            journal.JournalStore(writer)
        memory.pin.assert_not_called()
        memory.open_database.assert_not_called()


@pytest.mark.parametrize("version", [1, 2, 3])
def test_legacy_upgrade_uses_one_transaction_and_only_final_version(
    monkeypatch, version
):
    _observe_upgrade_requests(monkeypatch, version)


def _assert_upgrade_trace(statements, version):
    normalized = [" ".join(sql.split()).upper() for sql in statements]
    assert normalized.count("BEGIN IMMEDIATE") == 1
    assert normalized.count("COMMIT") == 1
    assert [sql for sql in normalized if sql.startswith("PRAGMA USER_VERSION =")] == [
        "PRAGMA USER_VERSION = 4"
    ]
    creates = [sql for sql in normalized if sql.startswith("CREATE TABLE")]
    assert len(creates) == 4 - version
    assert creates[-1].startswith("CREATE TABLE ROUTE_DISPOSITIONS")


def _observe_upgrade_requests(monkeypatch, version, *, failure=None):
    def normalize(sql):
        return " ".join(sql.rstrip().removesuffix(";").split())

    def table_row(statement):
        ddl = normalize(statement)
        name = ddl.split()[2]
        return "table", name, name, ddl

    base = tuple(table_row(sql) for sql in _V1_SCHEMA.split(";") if sql.strip())
    migrations = tuple(
        table_row(sql)
        for sql in (_V2_REVISION_SCHEMA, _V3_CONTENT_SCHEMA, _V4_DISPOSITION_SCHEMA)
    )

    def supported(schema_version):
        assert schema_version in {1, 2, 3, 4}
        return tuple(sorted((*base, *migrations[: schema_version - 1])))

    reported = version
    catalog = list(supported(version))
    statements = []
    validate = journal._validate_identity
    memory = _journal_observations(monkeypatch)
    original_ids = memory.directory.identities
    monkeypatch.setattr(journal, "_validate_identity", validate)
    monkeypatch.setattr(journal, "_supported_schema", supported)

    def check_directory():
        if failure == "interrupt" and reported == 4:
            assert tuple(sorted(catalog)) == supported(4)
            raise RuntimeError("injected interruption after migration DDL")

    memory.directory.check.side_effect = check_directory

    def connect(path, *, write):
        assert path == memory.store / journal._DATABASE
        before = reported, catalog.copy()

        def execute(statement):
            nonlocal reported
            sql = normalize(statement)
            if write:
                statements.append(sql)
            if sql == ("BEGIN IMMEDIATE" if write else "BEGIN"):
                return None
            metadata = {
                "PRAGMA application_id": (_V1_APPLICATION_ID,),
                "PRAGMA user_version": (reported,),
                "PRAGMA journal_mode": ("wal",),
                "SELECT singleton, key_id FROM identity": [
                    (1, memory.writer.view().source_key_id)
                ],
                "PRAGMA foreign_key_check": None,
            }
            if sql in metadata:
                if (
                    failure == "replace-directory"
                    and write
                    and reported == 4
                    and sql == "PRAGMA foreign_key_check"
                ):
                    memory.directory.identities = (*original_ids[:-1], (1, 99))
                value = metadata[sql]
                return SimpleNamespace(fetchone=lambda: value, fetchall=lambda: value)
            if (
                sql
                == "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name"
            ):
                return sorted(catalog)
            assert write, f"Read-only journal issued {sql}"
            if sql.startswith("PRAGMA user_version = "):
                reported = int(sql.split()[-1])
            else:
                row = table_row(sql)
                assert row in migrations and row not in catalog
                catalog.append(row)
            return None

        def close_transaction(error, *_):
            nonlocal reported, catalog
            if not write:
                return
            if error is None:
                statements.append("COMMIT")
            else:
                statements.append("ROLLBACK")
                reported, catalog = before

        connection = MagicMock(spec=sqlite3.Connection)
        connection.execute.side_effect = execute
        connection.__exit__.side_effect = close_transaction
        return nullcontext(connection)

    memory.open_database.side_effect = connect
    if failure is not None:
        error, message = {
            "replace-directory": (
                LedgerError,
                "Pinned routing journal storage changed",
            ),
            "interrupt": (RuntimeError, "injected interruption after migration DDL"),
        }[failure]
        with pytest.raises(error, match=message):
            journal.JournalStore(memory.writer)
        assert [
            entry.kwargs["write"] for entry in memory.open_database.call_args_list
        ] == [
            False,
            True,
        ]
        if failure == "replace-directory":
            assert memory.directory.identities != original_ids
        assert statements[-2:] == ["PRAGMA foreign_key_check", "ROLLBACK"]
        assert "COMMIT" not in statements
        assert reported == version
        assert tuple(sorted(catalog)) == supported(version)

        memory.directory.identities = original_ids
        failure = None
        memory.open_database.reset_mock()
        statements.clear()
    journal.JournalStore(memory.writer)
    assert [entry.kwargs["write"] for entry in memory.open_database.call_args_list] == [
        False,
        True,
    ]
    assert reported == 4
    assert tuple(sorted(catalog)) == supported(4)
    _assert_upgrade_trace(statements, version)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_exact_legacy_gate_refuses_v3_without_any_storage_byte_changes(
    monkeypatch, version
):
    connection = _journal_metadata(monkeypatch, journal._SCHEMA_VERSION)

    with pytest.raises(LedgerError, match="schema version"):
        journal._validate_identity(connection, "fixture-key", version=version)

    assert [call.args for call in connection.execute.call_args_list] == [
        ("PRAGMA application_id",),
        ("PRAGMA user_version",),
    ]


@pytest.mark.parametrize("version", [1, 2])
@pytest.mark.parametrize(
    "damage",
    [
        "PRAGMA user_version = 4",
        "PRAGMA user_version = 0",
        "CREATE TABLE content_disputes (key TEXT) STRICT",
        "UPDATE identity SET key_id = 'foreign'",
    ],
)
def test_mixed_or_unknown_legacy_schema_is_refused_without_migration(
    monkeypatch, version, damage
):
    connection = _journal_metadata(monkeypatch, version, damage)

    with pytest.raises(LedgerError):
        journal._validate_identity(connection, "fixture-key", version=None)


def test_content_dispute_table_enforces_private_strict_foreign_keys(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _create_v2_store(writer)
        with journal.JournalStore(writer).transaction(write=True) as conn:
            insert = "INSERT INTO content_disputes VALUES (?, ?, ?)"
            assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
            assert conn.execute("PRAGMA synchronous").fetchone() == (2,)
            for key, sequence in [("missing", 1), ("key", 999)]:
                with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
                    conn.execute(insert, (key, sequence, b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="cannot store TEXT"):
                conn.execute(insert, ("key", 3, "invalid"))
            conn.execute(insert, ("key", 3, b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
                conn.execute(insert, ("key", 3, b"different"))


def test_route_disposition_table_enforces_strict_identity_and_commit(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _create_v3_store(writer)
        with journal.JournalStore(writer).transaction(write=True) as conn:
            insert = "INSERT INTO route_dispositions VALUES (?, ?, ?, ?)"
            with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
                conn.execute(insert, ("command", "hold", 999, b"payload"))
            with pytest.raises(sqlite3.IntegrityError, match="cannot store TEXT"):
                conn.execute(insert, ("command", "hold", 3, "payload"))
            conn.execute(insert, ("command", "hold", 3, b"payload"))
            for values in (
                ("command", "other-hold", 2, b"payload"),
                ("other-command", "hold", 2, b"payload"),
                ("other-command", "other-hold", 3, b"payload"),
            ):
                with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
                    conn.execute(insert, values)


def test_paired_journal_upgrade_occurs_only_with_first_committed_pair(tmp_path):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.source_evidence()
        store = journal.JournalStore(writer)
        with store.transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (4,)
        with pytest.raises(RuntimeError, match="abort pair"):
            with store.transaction(write=True) as conn:
                store._enable_paired(conn)
                raise RuntimeError("abort pair")
        with store.transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (4,)
        with store.transaction(write=True) as conn:
            store._enable_paired(conn)
            conn.execute("INSERT INTO commits VALUES (1)")
            conn.execute("INSERT INTO paired_settlements VALUES (1, ?)", (b"pair",))
    with registry.writer() as writer:
        store = journal.JournalStore(writer)
        with store.transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (5,)
            assert conn.execute("SELECT * FROM paired_settlements").fetchall() == [
                (1, b"pair")
            ]
            with pytest.raises(
                LedgerError, match="Unsupported routing journal schema version"
            ):
                journal._validate_identity(conn, writer.view().source_key_id, version=4)
