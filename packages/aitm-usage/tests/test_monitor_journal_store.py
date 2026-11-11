"""Private routing journal custody, publication and transaction boundaries."""

import os
import shutil
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

import pytest

from aitm_usage import _monitor_journal_store as journal
from aitm_usage import host_fs
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_registry import Registry

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


def _legacy_rows(conn, version):
    names = _V1_TABLES + (("claim_revisions",) if version == 2 else ())
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


def _assert_exact_legacy_upgrade(tmp_path, version):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = (_create_v1_store if version == 1 else _create_v2_store)(writer)
        identities = _storage_identity(registry)
        with _sqlite(_database(registry)) as conn:
            original_schema = _schema_objects(conn)
            original_rows = _legacy_rows(conn, version)
            old_tip = conn.execute("SELECT max(sequence) FROM commits").fetchone()
        store = journal.JournalStore(writer)
        assert store.evidence == evidence
        with store.transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (3,)
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
            assert conn.execute("SELECT * FROM content_disputes").fetchall() == []
            new_schema = _schema_objects(conn)
            added = {"content_disputes"}
            if version == 1:
                added.add("claim_revisions")
                assert conn.execute("SELECT * FROM claim_revisions").fetchall() == []
            assert [row for row in new_schema if row[2] not in added] == original_schema
    with registry.writer() as writer:
        with journal.JournalStore(writer).transaction() as conn:
            assert _legacy_rows(conn, version) == original_rows
        _assert_storage_identity(identities)
    with _sqlite(":memory:") as conn:
        conn.executescript(_V1_SCHEMA + _V2_REVISION_SCHEMA + _V3_CONTENT_SCHEMA)
        assert _schema_objects(conn) == new_schema
    fresh = Registry(tmp_path / "fresh")
    with fresh.writer() as writer:
        writer.source_evidence()
        with journal.JournalStore(writer).transaction() as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (3,)
            assert _schema_objects(conn) == new_schema


def test_exact_v1_upgrade_preserves_rows_and_matches_fresh_v2(tmp_path):
    # Retain the baseline node ID; the fresh target is now v3.
    _assert_exact_legacy_upgrade(tmp_path, 1)


def test_exact_v2_upgrade_preserves_rows_and_matches_fresh_v3(tmp_path):
    _assert_exact_legacy_upgrade(tmp_path, 2)


def _assert_legacy_upgrade_rolls_back(tmp_path, monkeypatch, failure, version):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        (_create_v1_store if version == 1 else _create_v2_store)(writer)
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
                and migration.execute("PRAGMA user_version").fetchone() == (3,)
            ):
                assert (
                    migration.execute("SELECT * FROM content_disputes").fetchall() == []
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
            assert conn.execute("PRAGMA user_version").fetchone() == (3,)
            assert _legacy_rows(conn, version) == original_rows


@pytest.mark.parametrize("failure", ["interrupt", "replace-directory"])
def test_v1_upgrade_rolls_back_after_ddl_and_can_retry(tmp_path, monkeypatch, failure):
    _assert_legacy_upgrade_rolls_back(tmp_path, monkeypatch, failure, 1)


@pytest.mark.parametrize("failure", ["interrupt", "replace-directory"])
def test_v2_upgrade_rolls_back_after_ddl_and_can_retry(tmp_path, monkeypatch, failure):
    _assert_legacy_upgrade_rolls_back(tmp_path, monkeypatch, failure, 2)


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
def test_invalid_v1_is_refused_before_upgrade(tmp_path, damage, message):
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


def test_exact_v1_validation_refuses_v2_without_modifying_either_store(tmp_path):
    v1_registry = Registry(tmp_path / "v1")
    v2_registry = Registry(tmp_path / "v2")
    with v1_registry.writer() as writer:
        v1 = _create_v1_store(writer)
    with v2_registry.writer() as writer:
        v2 = _create_v2_store(writer)
        with _sqlite(_database(writer)) as conn:
            assert conn.execute("PRAGMA user_version").fetchone() == (2,)
    expected_bytes = [
        _durable_bytes(registry) for registry in (v1_registry, v2_registry)
    ]
    with _sqlite(_database(v1_registry)) as conn:
        journal._validate_identity(conn, v1.key_id, version=1)
    with _sqlite(_database(v2_registry)) as conn:
        with pytest.raises(LedgerError, match="schema version"):
            journal._validate_identity(conn, v2.key_id, version=1)
    assert [
        _durable_bytes(registry) for registry in (v1_registry, v2_registry)
    ] == expected_bytes


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


@pytest.mark.parametrize("version", [1, 2])
def test_legacy_upgrade_uses_one_transaction_and_only_final_version(
    tmp_path, monkeypatch, version
):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        (_create_v1_store if version == 1 else _create_v2_store)(writer)
        statements = []
        open_database = journal._open

        @contextmanager
        def trace_migration(database, *, write):
            with open_database(database, write=write) as conn:
                if write:
                    conn.set_trace_callback(statements.append)
                yield conn

        monkeypatch.setattr(journal, "_open", trace_migration)
        journal.JournalStore(writer)
        normalized = [" ".join(sql.split()).upper() for sql in statements]
        assert normalized.count("BEGIN IMMEDIATE") == 1
        assert normalized.count("COMMIT") == 1
        assert [
            sql for sql in normalized if sql.startswith("PRAGMA USER_VERSION =")
        ] == ["PRAGMA USER_VERSION = 3"]
        creates = [sql for sql in normalized if sql.startswith("CREATE TABLE")]
        assert len(creates) == (2 if version == 1 else 1)
        assert creates[-1].startswith("CREATE TABLE CONTENT_DISPUTES")


@pytest.mark.parametrize("version", [1, 2])
def test_exact_legacy_gate_refuses_v3_without_any_storage_byte_changes(
    tmp_path, version
):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        evidence = writer.source_evidence()
        journal.JournalStore(writer)
        expected = {p: p.read_bytes() for p in _directory(registry).iterdir()}
        with journal._open(_database(registry), write=False) as conn:
            with pytest.raises(LedgerError, match="schema version"):
                journal._validate_identity(conn, evidence.key_id, version=version)
        assert {p: p.read_bytes() for p in expected} == expected


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
    tmp_path, version, damage
):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        (_create_v1_store if version == 1 else _create_v2_store)(writer)
        with _sqlite(_database(registry)) as conn:
            conn.execute(damage)
        identities = _storage_identity(registry)
        expected = _durable_bytes(registry)
        with pytest.raises(LedgerError):
            journal.JournalStore(writer)
        _assert_storage_identity(identities)
        assert _durable_bytes(registry) == expected


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
