"""A private, project-bound SQLite history and per-source ingest checkpoints."""

import fcntl
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import stat
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from .types import (
    LedgerBatch,
    LedgerView,
    Revision,
    ScopeMarker,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
    _decode,
    _encode,
)

SCHEMA_VERSION = 1
APPLICATION_ID = 0x41495455  # AITU
STORE_NAME = "state"
DATABASE_NAME = "usage.sqlite3"
KEY_NAME = "pseudonym.key"
LOCK_NAME = "writer.lock"
KEY_SIZE = 32

_SCHEMA = """
CREATE TABLE identity (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    project_id TEXT NOT NULL,
    key_id TEXT NOT NULL
) STRICT;
CREATE TABLE commits (
    sequence INTEGER PRIMARY KEY
) STRICT;
CREATE TABLE revisions (
    key TEXT NOT NULL,
    revision INTEGER NOT NULL,
    sequence INTEGER NOT NULL REFERENCES commits,
    payload TEXT NOT NULL,
    PRIMARY KEY (key, revision)
) STRICT;
CREATE INDEX revision_sequence ON revisions (sequence, key, revision);
CREATE TABLE checkpoints (
    source_ref TEXT NOT NULL,
    sequence INTEGER NOT NULL REFERENCES commits,
    payload TEXT NOT NULL,
    PRIMARY KEY (source_ref, sequence)
) STRICT;
"""


class LedgerError(RuntimeError):
    """The private project state cannot be used."""


class WriterActive(LedgerError):
    """Another collector holds the project writer lease."""


class ConflictError(LedgerError):
    """The proposed batch would change immutable history or stale source state."""


@dataclass(frozen=True, slots=True)
class LedgerIdentity:
    project_id: UUID
    key_id: str
    schema_version: int = SCHEMA_VERSION


def _private(info: os.stat_result, *, directory: bool = False) -> None:
    if directory:
        valid = stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
    else:
        valid = (
            stat.S_ISREG(info.st_mode)
            and stat.S_IMODE(info.st_mode) == 0o600
            and info.st_nlink == 1
        )
    if not valid or info.st_uid != os.geteuid():
        raise LedgerError("Unsafe private ledger path")


def _check_path(path: Path, *, directory: bool = False) -> None:
    try:
        _private(path.lstat(), directory=directory)
    except OSError as error:
        raise LedgerError("Private ledger path is unavailable") from error


def _project_path(root: Path) -> Path:
    root = root.absolute()
    if root.resolve() != root:
        raise LedgerError("Project state path must be canonical")
    return root


def _sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def _lease(path: Path, *, create: bool = False) -> Iterator[None]:
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        if create:
            try:
                fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                fd = os.open(path, flags)
        else:
            fd = os.open(path, flags)
    except OSError as error:
        raise LedgerError("Writer lease file is unavailable") from error

    try:
        info = os.fstat(fd)
        _private(info)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise WriterActive("writer-active") from error
        _check_path(path)
        if not os.path.samestat(info, path.lstat()):
            raise LedgerError("Writer lease file changed")
        yield
    finally:
        os.close(fd)


def _key_path(root: Path) -> Path:
    return root / STORE_NAME / KEY_NAME


def _database_path(root: Path) -> Path:
    return root / STORE_NAME / DATABASE_NAME


def _read_key(root: Path, project_id: UUID) -> bytes:
    try:
        fd = os.open(_key_path(root), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as error:
        raise LedgerError("Private pseudonym key is unavailable") from error
    with os.fdopen(fd, "rb") as handle:
        _private(os.fstat(handle.fileno()))
        payload = handle.read(16 + KEY_SIZE + 1)
    if len(payload) != 16 + KEY_SIZE or payload[:16] != project_id.bytes:
        raise LedgerError("Pseudonym key project identity mismatch")
    return payload[16:]


def _identity(project_id: UUID, key: bytes) -> LedgerIdentity:
    return LedgerIdentity(project_id, "sha256:" + hashlib.sha256(key).hexdigest())


def _validate_storage(root: Path, project_id: UUID) -> bytes:
    _project_path(root)
    _check_path(root, directory=True)
    _check_path(root / LOCK_NAME)
    _check_path(root / STORE_NAME, directory=True)
    database = _database_path(root)
    for suffix in ("", "-wal", "-shm"):
        _check_path(database.with_name(database.name + suffix))
    return _read_key(root, project_id)


@contextmanager
def _connection(database: Path, *, write: bool) -> Iterator[sqlite3.Connection]:
    # Retain WAL/SHM across connection closes. A mode=ro opener otherwise
    # may need to create sidecars the next time it reads an idle WAL database.
    mode = "rw" if write else "ro"
    with closing(
        sqlite3.connect(f"{database.as_uri()}?mode={mode}", uri=True, timeout=1)
    ) as conn:
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
        if write:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA synchronous=FULL")
        yield conn


def _validate_identity(conn: sqlite3.Connection, identity: LedgerIdentity) -> None:
    if conn.execute("PRAGMA user_version").fetchone() != (SCHEMA_VERSION,):
        raise LedgerError("Unsupported ledger schema")
    if conn.execute("PRAGMA application_id").fetchone() != (APPLICATION_ID,):
        raise LedgerError("Unrecognized ledger application")
    if conn.execute("PRAGMA journal_mode").fetchone() != ("wal",):
        raise LedgerError("Ledger requires WAL")
    try:
        row = conn.execute(
            "SELECT project_id, key_id FROM identity WHERE singleton = 1"
        ).fetchone()
        conn.execute(
            """SELECT commits.sequence, revisions.key, revisions.revision, revisions.sequence,
                      revisions.payload, checkpoints.source_ref, checkpoints.sequence,
                      checkpoints.payload
               FROM commits CROSS JOIN revisions CROSS JOIN checkpoints LIMIT 0"""
        )
    except sqlite3.OperationalError as error:
        if error.sqlite_errorcode != sqlite3.SQLITE_ERROR:
            raise
        raise LedgerError("Invalid ledger table schema") from error
    if row != (str(identity.project_id), identity.key_id):
        raise LedgerError("Ledger project or key identity mismatch")


@contextmanager
def _read_snapshot(
    root: Path, project_id: UUID
) -> Iterator[tuple[sqlite3.Connection, LedgerIdentity, bytes]]:
    key = _validate_storage(root, project_id)
    identity = _identity(project_id, key)
    with _connection(_database_path(root), write=False) as conn, conn:
        conn.execute("BEGIN")
        _validate_identity(conn, identity)
        yield conn, identity, key


def _create_store(root: Path, project_id: UUID) -> None:
    # Publish the initialized key, database and WAL sidecars in one rename.
    # A crash before that rename leaves no partial canonical ledger.
    with TemporaryDirectory(prefix=".initializing-", dir=root) as name:
        staging = Path(name)
        key = secrets.token_bytes(KEY_SIZE)
        key_file = staging / KEY_NAME
        key_fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(key_fd, "wb") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(project_id.bytes + key)
            handle.flush()
            os.fsync(handle.fileno())
        database = staging / DATABASE_NAME
        fd = os.open(database, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
        with _connection(database, write=True) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("BEGIN IMMEDIATE;\n" + _SCHEMA)
            conn.execute(f"PRAGMA application_id = {APPLICATION_ID}")
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.execute(
                "INSERT INTO identity VALUES (1, ?, ?)",
                (str(project_id), _identity(project_id, key).key_id),
            )
            conn.commit()
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        for suffix in ("", "-wal", "-shm"):
            _check_path(database.with_name(database.name + suffix))
        _sync_directory(staging)
        staging.rename(root / STORE_NAME)
        _sync_directory(root)


def _head(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COALESCE(MAX(sequence), 0) FROM commits").fetchone()[0]


def _check_revision_identity(previous: Revision, proposed: Revision) -> None:
    before, after = previous.record, proposed.record
    if type(before) is not type(after):
        raise ConflictError("Revision changes its record type")
    if isinstance(before, UsageObservation) and isinstance(after, UsageObservation):
        before_scope = (
            before.boundary.provider,
            before.boundary.stream_ref,
            before.boundary.session_ref,
        )
        after_scope = (
            after.boundary.provider,
            after.boundary.stream_ref,
            after.boundary.session_ref,
        )
        if before_scope != after_scope or any(
            old is not None and old != new
            for old, new in (
                (before.request_ref, after.request_ref),
                (before.message_ref, after.message_ref),
            )
        ):
            raise ConflictError("Revision changes its source identity")
    if isinstance(before, ScopeMarker) and isinstance(after, ScopeMarker):
        if (before.marker_id, before.provider, before.session_ref) != (
            after.marker_id,
            after.provider,
            after.session_ref,
        ):
            raise ConflictError("Revision changes its marker identity")


def _append_revisions(
    conn: sqlite3.Connection, sequence: int, revisions: tuple[Revision, ...]
) -> bool:
    inserted = False
    for revision in revisions:
        payload = _encode(revision, Revision)
        key = revision.key.value
        existing = conn.execute(
            "SELECT payload FROM revisions WHERE key = ? AND revision = ?",
            (key, revision.revision),
        ).fetchone()
        if existing is not None:
            if existing[0] != payload:
                raise ConflictError("Immutable revision payload conflict")
            continue
        latest = conn.execute(
            "SELECT revision, payload FROM revisions WHERE key = ? ORDER BY revision DESC LIMIT 1",
            (key,),
        ).fetchone()
        if latest is not None:
            if revision.revision <= latest[0]:
                raise ConflictError("Revision number is older than accepted history")
            _check_revision_identity(_decode(latest[1], Revision), revision)
        conn.execute(
            "INSERT INTO revisions VALUES (?, ?, ?, ?)",
            (key, revision.revision, sequence, payload),
        )
        inserted = True
    return inserted


def _append_checkpoint(
    conn: sqlite3.Connection, sequence: int, batch: LedgerBatch
) -> bool:
    checkpoint = batch.checkpoint
    prior = batch.prior_checkpoint
    if checkpoint is None:
        if prior is not None:
            raise ValueError("A prior checkpoint requires an updated checkpoint")
        return False

    source_ref = checkpoint.cursor.source_ref.value
    stored = conn.execute(
        "SELECT payload FROM checkpoints WHERE source_ref = ? ORDER BY sequence DESC LIMIT 1",
        (source_ref,),
    ).fetchone()
    payload = _encode(checkpoint, SourceCheckpoint)
    if stored is not None and stored[0] == payload:
        return False
    current_payload = None if stored is None else stored[0]
    prior_payload = None if prior is None else _encode(prior, SourceCheckpoint)
    if current_payload != prior_payload:
        raise ConflictError("Source checkpoint has changed")
    if prior is not None:
        if checkpoint.provider.provider is not prior.provider.provider:
            raise ConflictError("Source checkpoint changes provider")
        if (
            checkpoint.cursor.incarnation_ref == prior.cursor.incarnation_ref
            and checkpoint.cursor.locator_ref == prior.cursor.locator_ref
            and checkpoint.cursor.offset < prior.cursor.offset
        ):
            raise ConflictError("Source cursor cannot move backwards")
    conn.execute(
        "INSERT INTO checkpoints VALUES (?, ?, ?)", (source_ref, sequence, payload)
    )
    return True


@dataclass(frozen=True, slots=True)
class Ledger:
    root: Path
    identity: LedgerIdentity
    _key: bytes = field(repr=False, compare=False)
    _writer: sqlite3.Connection | None = field(default=None, repr=False, compare=False)

    @property
    def database_path(self) -> Path:
        return _database_path(self.root)

    @property
    def key_path(self) -> Path:
        return _key_path(self.root)

    @property
    def lock_path(self) -> Path:
        return self.root / LOCK_NAME

    @classmethod
    def initialize(cls, root: Path, project_id: UUID) -> "Ledger":
        root = _project_path(root)
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        _check_path(root, directory=True)
        store = root / STORE_NAME
        with _lease(root / LOCK_NAME, create=not store.exists(follow_symlinks=False)):
            if not store.exists(follow_symlinks=False):
                _create_store(root, project_id)
            return cls.open(root, project_id)

    @classmethod
    def open(cls, root: Path, project_id: UUID) -> "Ledger":
        root = _project_path(root)
        with _read_snapshot(root, project_id) as (_, identity, key):
            return cls(root, identity, key)

    def pseudonymize(self, namespace: str, raw_reference: str) -> SourceRef:
        """Derive a stable private reference with a domain specific to its use."""
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", namespace) or not raw_reference:
            raise ValueError("A reference namespace and identifier are required")
        message = b"aitm-usage/source-ref/v1\0" + namespace.encode("ascii") + b"\0"
        digest = hmac.digest(
            self._key, message + raw_reference.encode("utf-8"), "sha256"
        )
        return SourceRef("hmac-sha256:" + digest.hex())

    @contextmanager
    def reader(self) -> Iterator[sqlite3.Connection]:
        """Open a read-only snapshot for status, exports and SQLite backups."""
        with _read_snapshot(self.root, self.identity.project_id) as (conn, identity, _):
            if identity != self.identity:
                raise LedgerError("Ledger identity changed")
            yield conn

    @contextmanager
    def writer(self) -> Iterator["Ledger"]:
        """Hold the stable process lease across one or more batch writes."""
        _project_path(self.root)
        _check_path(self.root, directory=True)
        with _lease(self.lock_path):
            with self.reader():
                pass
            with _connection(self.database_path, write=True) as conn:
                yield Ledger(self.root, self.identity, self._key, conn)

    def apply(self, batch: LedgerBatch) -> int:
        # Reject malformed envelopes before the writer opens a transaction.
        _encode(batch, LedgerBatch)
        for revision in batch.revisions:
            if (
                isinstance(revision.record, ScopeMarker)
                and revision.record.project_id != self.identity.project_id
            ):
                raise LedgerError("Scope marker project identity mismatch")
        if self._writer is not None:
            return self._apply(batch)
        with self.writer() as writer:
            return writer._apply(batch)

    def _apply(self, batch: LedgerBatch) -> int:
        conn = self._writer
        assert conn is not None
        key = _validate_storage(self.root, self.identity.project_id)
        if not hmac.compare_digest(key, self._key):
            raise LedgerError("Ledger identity changed")
        _validate_identity(conn, self.identity)
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            head = _head(conn)
            sequence = head + 1
            conn.execute("INSERT INTO commits VALUES (?)", (sequence,))
            revisions_changed = _append_revisions(conn, sequence, batch.revisions)
            checkpoint_changed = _append_checkpoint(conn, sequence, batch)
            if revisions_changed or checkpoint_changed:
                return sequence
            conn.rollback()
            return head

    def as_of(self, sequence: int | None = None) -> LedgerView:
        with self.reader() as conn:
            head = _head(conn)
            if sequence is None:
                sequence = head
            if type(sequence) is not int or not 0 <= sequence <= head:
                raise ValueError("Sequence is outside committed ledger history")
            revisions = conn.execute(
                """SELECT payload FROM revisions WHERE sequence <= ?
                   ORDER BY sequence, key, revision""",
                (sequence,),
            )
            checkpoints = conn.execute(
                """SELECT c.payload FROM checkpoints c
                   JOIN (
                       SELECT source_ref, MAX(sequence) AS latest
                       FROM checkpoints WHERE sequence <= ? GROUP BY source_ref
                   ) h ON h.source_ref = c.source_ref AND h.latest = c.sequence
                   ORDER BY c.source_ref""",
                (sequence,),
            )
            return LedgerView(
                sequence,
                tuple(_decode(row[0], Revision) for row in revisions),
                tuple(_decode(row[0], SourceCheckpoint) for row in checkpoints),
            )
