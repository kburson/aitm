"""SQLite custody for the coordinator's private routing journal."""

import hmac
import os
import sqlite3
from collections.abc import Iterator
from contextlib import ExitStack, closing, contextmanager
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from . import host_fs
from .ledger import (
    LedgerError,
    _check_acl,
    _check_path,
    _connection,
    _path_exists,
    _path_id,
    _pin_directory,
    _PinnedPath,
    _private,
    _schema_objects,
)
from .monitor_registry import _SOURCE_KEY_FILE, Registry, _ServiceEvidence
from .scopes import _read_private

_STORE = "routing-journal-v1"
_DATABASE = "journal.sqlite3"
_FILES = (_DATABASE, f"{_DATABASE}-wal", f"{_DATABASE}-shm")
_APPLICATION_ID = 0x4149544A  # AITJ
_LEGACY_SCHEMA_VERSION = 1
_REVISION_SCHEMA_VERSION = 2
_SCHEMA_VERSION = 3
_SCHEMA = """
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
_REVISION_SCHEMA = """
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

_CONTENT_DISPUTE_SCHEMA = """
CREATE TABLE content_disputes (
    key TEXT PRIMARY KEY REFERENCES claims(key),
    sequence INTEGER NOT NULL REFERENCES commits,
    payload BLOB NOT NULL
) STRICT;
"""


@cache
def _supported_schema(version: int) -> tuple[tuple[str, str, str, str | None], ...]:
    if version not in {
        _LEGACY_SCHEMA_VERSION,
        _REVISION_SCHEMA_VERSION,
        _SCHEMA_VERSION,
    }:
        raise LedgerError("Unsupported routing journal schema version")
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.executescript(_SCHEMA)
        if version in {_REVISION_SCHEMA_VERSION, _SCHEMA_VERSION}:
            conn.execute(_REVISION_SCHEMA)
        if version == _SCHEMA_VERSION:
            conn.execute(_CONTENT_DISPUTE_SCHEMA)
        return _schema_objects(conn)


def _validate_identity(
    conn: sqlite3.Connection, key_id: str, *, version: int | None = _SCHEMA_VERSION
) -> int:
    try:
        if conn.execute("PRAGMA application_id").fetchone() != (_APPLICATION_ID,):
            raise LedgerError("Unrecognized routing journal application")
        stored = conn.execute("PRAGMA user_version").fetchone()
        if stored not in {
            (_LEGACY_SCHEMA_VERSION,),
            (_REVISION_SCHEMA_VERSION,),
            (_SCHEMA_VERSION,),
        } or (version is not None and stored != (version,)):
            raise LedgerError("Unsupported routing journal schema version")
        stored_version = stored[0]
        if conn.execute("PRAGMA journal_mode").fetchone() != ("wal",):
            raise LedgerError("Routing journal requires WAL")
        if _schema_objects(conn) != _supported_schema(stored_version):
            raise LedgerError("Invalid routing journal table schema")
        if conn.execute("SELECT singleton, key_id FROM identity").fetchall() != [
            (1, key_id)
        ]:
            raise LedgerError("Routing journal source key identity mismatch")
        return stored_version
    except sqlite3.Error:
        raise LedgerError("Invalid routing journal database") from None


def _validate_foreign_keys(conn: sqlite3.Connection) -> None:
    if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise LedgerError("Invalid routing journal foreign key references")


def _file_identity(path: Path) -> tuple[int, int]:
    return _path_id(_check_path(path))


@dataclass(frozen=True, slots=True)
class _StoreIdentity:
    directory: tuple[tuple[int, int], ...]
    files: tuple[tuple[int, int], ...]

    @classmethod
    def capture(cls, directory: _PinnedPath) -> "_StoreIdentity":
        directory.check()
        return cls(
            directory.identities,
            tuple(_file_identity(directory.path / name) for name in _FILES),
        )

    def check(self, directory: _PinnedPath) -> None:
        if self != self.capture(directory):
            raise LedgerError("Pinned routing journal storage changed")

    def sync(self, directory: _PinnedPath) -> None:
        for name, identity in zip(_FILES, self.files, strict=True):
            fd = os.open(
                name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory.fd
            )
            try:
                info = os.fstat(fd)
                _private(info)
                _check_acl(fd)
                if _path_id(info) != identity:
                    raise LedgerError("Pinned routing journal file changed")
                os.fsync(fd)
            finally:
                os.close(fd)
        os.fsync(directory.fd)
        self.check(directory)


@contextmanager
def _open(database: Path, *, write: bool) -> Iterator[sqlite3.Connection]:
    with ExitStack() as stack:
        try:
            conn = stack.enter_context(_connection(database, write=write))
        except sqlite3.Error:
            raise LedgerError("Unable to open private routing journal") from None
        yield conn


def _initialize_database(staging: _PinnedPath, key_id: str) -> _StoreIdentity:
    database = staging.path / _DATABASE
    fd = os.open(
        _DATABASE,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=staging.fd,
    )
    try:
        os.fchmod(fd, 0o600)
        info = os.fstat(fd)
        _private(info)
        _check_acl(fd)
        created = _path_id(info)
    finally:
        os.close(fd)
    staging.check()
    if _file_identity(database) != created:
        raise LedgerError("Staged routing journal database changed")
    with _open(database, write=True) as conn:
        if _file_identity(database) != created:
            raise LedgerError("Staged routing journal database changed")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript("BEGIN IMMEDIATE;\n" + _SCHEMA)
        conn.execute(_REVISION_SCHEMA)
        conn.execute(_CONTENT_DISPUTE_SCHEMA)
        conn.execute(f"PRAGMA application_id = {_APPLICATION_ID}")
        conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        conn.execute("INSERT INTO identity VALUES (1, ?)", (key_id,))
        conn.commit()
        if conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone() != (0, 0, 0):
            raise LedgerError("Unable to checkpoint new routing journal")
        _validate_identity(conn, key_id)
    identity = _StoreIdentity.capture(staging)
    if identity.files[0] != created:
        raise LedgerError("Staged routing journal database changed")
    identity.sync(staging)
    return identity


class JournalStore:
    """Open the exact private journal under one live registry writer."""

    def __init__(self, writer: Registry):
        self._writer = writer
        self._lease = writer.lease
        key_id = writer.view().source_key_id
        if key_id is None:
            raise LedgerError("Routing journal requires an initialized source key")
        self._key_id = key_id
        with _pin_directory(writer.root) as root:
            self._check_root(root)
            self._key_file = _file_identity(root.path / _SOURCE_KEY_FILE)
            published = None
            if not _path_exists(root.path / _STORE):
                self._evidence = self._read_evidence(root)
                published = self._create(root)
            with _pin_directory(root.path / _STORE) as directory:
                self._identity = _StoreIdentity.capture(directory)
                if published is not None:
                    published.check(directory)
                with self._pinned_transaction(root, directory, write=False) as conn:
                    expected = _SCHEMA_VERSION if published is not None else None
                    version = _validate_identity(conn, key_id, version=expected)
                    if published is None:
                        self._evidence = self._read_evidence(root)
                if version != _SCHEMA_VERSION:
                    self._upgrade(root, directory, version)
                # Confirm a validated store even if a prior publisher lost its sync.
                try:
                    os.fsync(root.fd)
                except OSError:
                    raise LedgerError(
                        "Unable to synchronize routing journal publication"
                    ) from None
                self._check_store(root, directory)

    def _check_root(self, root: _PinnedPath) -> None:
        if (
            self._writer.lease is not self._lease
            or self._lease.identities[:-1] != root.identities
        ):
            raise LedgerError("Routing journal coordinator custody changed")
        root.check()

    def _check_authority(self, root: _PinnedPath) -> None:
        self._check_root(root)
        if self._writer.view().source_key_id != self._key_id:
            raise LedgerError("Routing journal registry source key identity changed")
        try:
            key = _read_private(root, _SOURCE_KEY_FILE)
        except OSError:
            raise LedgerError("Routing journal source key is unavailable") from None
        if (
            key is None
            or len(key) != 32
            or not hmac.compare_digest(sha256(key).hexdigest(), self._key_id)
            or _file_identity(root.path / _SOURCE_KEY_FILE) != self._key_file
        ):
            raise LedgerError("Routing journal source key changed")

    def _read_evidence(self, root: _PinnedPath) -> _ServiceEvidence:
        # The existing registry path may initialize a key in other contexts.
        self._check_authority(root)
        evidence = self._writer.source_evidence()
        if evidence.key_id != self._key_id:
            raise LedgerError("Routing journal source key changed")
        self._check_authority(root)
        return evidence

    def _check_store(self, root: _PinnedPath, directory: _PinnedPath) -> None:
        self._check_authority(root)
        self._identity.check(directory)

    def _create(self, root: _PinnedPath) -> _StoreIdentity:
        try:
            with TemporaryDirectory(
                prefix=".journal-initializing-", dir=root.path
            ) as name:
                with _pin_directory(Path(name)) as staging:
                    self._check_root(root)
                    identity = _initialize_database(staging, self._key_id)
                    self._check_authority(root)
                    identity.check(staging)
                    if not host_fs.publish_noreplace(
                        root.fd, staging.path.name, root.fd, _STORE
                    ):
                        raise LedgerError("Private routing journal already exists")
                    return identity
        except (OSError, sqlite3.Error, host_fs.HostFilesystemError):
            raise LedgerError("Unable to publish private routing journal") from None

    @property
    def evidence(self) -> _ServiceEvidence:
        self._writer.lease
        with (
            _pin_directory(self._writer.root) as root,
            _pin_directory(root.path / _STORE) as directory,
        ):
            self._check_store(root, directory)
            return self._evidence

    @contextmanager
    def _pinned_transaction(
        self, root: _PinnedPath, directory: _PinnedPath, *, write: bool
    ) -> Iterator[sqlite3.Connection]:
        self._check_store(root, directory)
        with _open(directory.path / _DATABASE, write=write) as conn, conn:
            self._check_store(root, directory)
            conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield conn
            self._check_store(root, directory)

    def _upgrade(self, root: _PinnedPath, directory: _PinnedPath, version: int) -> None:
        try:
            with self._pinned_transaction(root, directory, write=True) as conn:
                _validate_identity(conn, self._key_id, version=version)
                _validate_foreign_keys(conn)
                if version == _LEGACY_SCHEMA_VERSION:
                    conn.execute(_REVISION_SCHEMA)
                    if _schema_objects(conn) != _supported_schema(
                        _REVISION_SCHEMA_VERSION
                    ):
                        raise LedgerError(
                            "Invalid routing journal intermediate table schema"
                        )
                conn.execute(_CONTENT_DISPUTE_SCHEMA)
                conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
                _validate_identity(conn, self._key_id)
                _validate_foreign_keys(conn)
        except sqlite3.Error:
            raise LedgerError("Unable to upgrade private routing journal") from None

    @contextmanager
    def transaction(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        self._writer.lease
        with (
            _pin_directory(self._writer.root) as root,
            _pin_directory(root.path / _STORE) as directory,
            self._pinned_transaction(root, directory, write=write) as conn,
        ):
            _validate_identity(conn, self._key_id)
            yield conn
            _validate_identity(conn, self._key_id)
