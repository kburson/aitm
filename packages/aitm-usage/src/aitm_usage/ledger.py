"""A private, project-bound SQLite history and per-source ingest checkpoints."""

import ctypes
import errno
import fcntl
import hashlib
import hmac
import os
import pwd
import re
import secrets
import sqlite3
import stat
import sys
import unicodedata
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from .types import (
    CommandDigest,
    CommandReceipt,
    DevelopmentBinding,
    InboxCommand,
    LedgerBatch,
    LedgerView,
    MarkerDisposition,
    QuotaEvidence,
    Revision,
    ScopeCorrection,
    ScopeEnrollment,
    ScopeMarker,
    SourceBoundary,
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
ACL_TYPE_EXTENDED = 0x100
_ACL_EMPTY = b"!#acl 1\n"
# The default macOS home ancestry carries this non-inheriting delete protection.
_ACL_DENY_DELETE = (
    _ACL_EMPTY + b"group:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:deny:delete\n"
)

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


@cache
def _mac_acl() -> ctypes.CDLL:
    if sys.platform != "darwin":
        raise LedgerError("Private ACL validation requires macOS")
    try:
        lib = ctypes.CDLL(None, use_errno=True)
        lib.acl_get_link_np.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.acl_get_link_np.restype = ctypes.c_void_p
        lib.acl_get_fd_np.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.acl_get_fd_np.restype = ctypes.c_void_p
        lib.acl_to_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ssize_t)]
        lib.acl_to_text.restype = ctypes.c_void_p
        lib.acl_free.argtypes = [ctypes.c_void_p]
        lib.acl_free.restype = ctypes.c_int
    except (AttributeError, OSError):
        raise LedgerError("Private ACL validation is unavailable") from None
    return lib


def _check_acl(target: Path | int, *, ancestor: bool = False) -> None:
    lib = _mac_acl()
    ctypes.set_errno(0)
    if isinstance(target, Path):
        acl = lib.acl_get_link_np(os.fsencode(target), ACL_TYPE_EXTENDED)
    else:
        acl = lib.acl_get_fd_np(target, ACL_TYPE_EXTENDED)
    if not acl:
        if ctypes.get_errno() == errno.ENOENT:
            return
        raise LedgerError("Unable to validate private ACL")
    try:
        text = lib.acl_to_text(acl, None)
        if not text:
            raise LedgerError("Unable to classify private ACL")
        try:
            value = ctypes.string_at(text)
        finally:
            lib.acl_free(text)
    finally:
        lib.acl_free(acl)
    if value != _ACL_EMPTY and not (ancestor and value == _ACL_DENY_DELETE):
        raise LedgerError("Unsafe private ACL")


def _project_path(root: Path) -> Path:
    root = root.absolute()
    if ".." in root.parts:
        raise LedgerError("Private ledger path must be canonical")
    return root


def _path_id(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _path_exists(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        raise LedgerError("Private ledger path is unavailable") from None
    return True


def _check_path(path: Path, *, directory: bool = False) -> os.stat_result:
    try:
        info = path.lstat()
        _private(info, directory=directory)
        _check_acl(path)
        if not os.path.samestat(info, path.lstat()):
            raise LedgerError("Private ledger path changed")
    except OSError:
        raise LedgerError("Private ledger path is unavailable") from None
    return info


def _validated_path(
    path: Path, *, directory: bool, allow_missing: bool = False
) -> tuple[tuple[int, int], ...]:
    path = _project_path(path)
    identities = []
    for ancestor in reversed(path.parents):
        try:
            info = ancestor.lstat()
            # Root-owned sticky directories protect each trusted owner's child.
            sticky_system = info.st_uid == 0 and info.st_mode & stat.S_ISVTX
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid not in (0, os.geteuid())
                or (info.st_mode & 0o022 and not sticky_system)
            ):
                raise LedgerError("Unsafe private ledger ancestry")
            _check_acl(ancestor, ancestor=True)
            if not os.path.samestat(info, ancestor.lstat()):
                raise LedgerError("Private ledger ancestor changed")
        except FileNotFoundError:
            if allow_missing:
                return tuple(identities)
            raise LedgerError("Private ledger ancestry is unavailable") from None
        except OSError:
            raise LedgerError("Private ledger ancestry is unavailable") from None
        identities.append(_path_id(info))
    if not allow_missing or _path_exists(path):
        identities.append(_path_id(_check_path(path, directory=directory)))
    return tuple(identities)


def validate_private_path(
    path: Path, *, directory: bool = False, allow_missing: bool = False
) -> None:
    """Validate trusted ancestry and any existing destination before private I/O."""
    _validated_path(path, directory=directory, allow_missing=allow_missing)


def _ensure_private_directory(path: Path) -> None:
    validate_private_path(path, directory=True, allow_missing=True)
    if not _path_exists(path.parent):
        _ensure_private_directory(path.parent)
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        validate_private_path(path, directory=True)
    except OSError:
        raise LedgerError("Unable to create private ledger directory") from None
    else:
        validate_private_path(path, directory=True)
        _sync_directory(path.parent)


def _sync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        raise LedgerError("Unable to synchronize private ledger directory") from None


@dataclass(frozen=True, slots=True)
class _PinnedPath:
    path: Path
    fd: int
    directory: bool
    identities: tuple[tuple[int, int], ...]

    def check(self) -> None:
        try:
            info = os.fstat(self.fd)
            _private(info, directory=self.directory)
            _check_acl(self.fd)
        except OSError:
            raise LedgerError("Private ledger descriptor is unavailable") from None
        if self.identities[-1] != _path_id(info) or self.identities != _validated_path(
            self.path, directory=self.directory
        ):
            raise LedgerError("Pinned private ledger path changed")


@contextmanager
def _pin_directory(path: Path) -> Iterator[_PinnedPath]:
    identities = _validated_path(path, directory=True)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        raise LedgerError("Private ledger directory is unavailable") from None
    try:
        pin = _PinnedPath(path, fd, True, identities)
        pin.check()
        yield pin
    finally:
        os.close(fd)


@contextmanager
def _lease(path: Path, *, create: bool = False) -> Iterator[_PinnedPath]:
    validate_private_path(path, allow_missing=create)
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
    created = False
    try:
        if create:
            try:
                fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
                created = True
            except FileExistsError:
                fd = os.open(path, flags)
        else:
            fd = os.open(path, flags)
    except OSError:
        raise LedgerError("Writer lease file is unavailable") from None

    try:
        pin = _PinnedPath(path, fd, False, _validated_path(path, directory=False))
        pin.check()
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise WriterActive("writer-active") from None
        pin.check()
        if created:
            try:
                os.fsync(fd)
            except OSError:
                raise LedgerError("Unable to synchronize writer lease") from None
            _sync_directory(path.parent)
        yield pin
    finally:
        os.close(fd)


def _control_root() -> Path:
    # A process-local HOME override must never select a second writer guard.
    try:
        home = Path(pwd.getpwuid(os.geteuid()).pw_dir)
    except KeyError:
        raise LedgerError(
            "Unable to resolve private account control location"
        ) from None
    return home / "Library" / "Application Support" / "aitm-usage-control"


def _physical_ancestry(
    path: Path,
) -> tuple[tuple[tuple[int, int], tuple[str, ...]], ...]:
    # Each existing directory anchors the remaining path, including a missing tail.
    components = tuple(
        unicodedata.normalize("NFC", part).casefold() for part in path.parts
    )
    return tuple(
        (identity, components[depth:])
        for depth, identity in enumerate(
            _validated_path(path, directory=True, allow_missing=True), start=1
        )
    )


def _guard_path(root: Path, project_id: UUID) -> Path:
    if type(project_id) is not UUID:
        raise LedgerError("A project UUID is required")
    control = _project_path(_control_root())
    project_ancestry = _physical_ancestry(root)
    # APFS firmlinks can share a physical ancestor without sharing its path spelling.
    for control_identity, control_tail in _physical_ancestry(control):
        for project_identity, project_tail in project_ancestry:
            if control_identity == project_identity:
                length = min(len(control_tail), len(project_tail))
                if control_tail[:length] == project_tail[:length]:
                    raise LedgerError("Writer guard must be outside project state")
    return control / f"{project_id}.lock"


@contextmanager
def project_guard(
    root: Path, project_id: UUID, *, initialize: bool = False
) -> Iterator[_PinnedPath]:
    """Take the stable UUID guard before creating or replacing project state."""
    root = _project_path(root)
    path = _guard_path(root, project_id)
    validate_private_path(root, directory=True, allow_missing=initialize)
    # Once local state exists the guard must already exist, even during recovery.
    create = initialize and not any(
        _path_exists(root / name) for name in (STORE_NAME, LOCK_NAME)
    )
    if create:
        _ensure_private_directory(path.parent)
    else:
        validate_private_path(path.parent, directory=True)
    with _lease(path, create=create) as guard:
        yield guard


def _key_path(root: Path) -> Path:
    return root / STORE_NAME / KEY_NAME


def _database_path(root: Path) -> Path:
    return root / STORE_NAME / DATABASE_NAME


def _read_key(root: Path, project_id: UUID, expected: tuple[int, int]) -> bytes:
    try:
        fd = os.open(_key_path(root), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        raise LedgerError("Private pseudonym key is unavailable") from None
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        _private(info)
        _check_acl(fd)
        if _path_id(info) != expected:
            raise LedgerError("Private pseudonym key changed")
        payload = handle.read(16 + KEY_SIZE + 1)
    if len(payload) != 16 + KEY_SIZE or payload[:16] != project_id.bytes:
        raise LedgerError("Pseudonym key project identity mismatch")
    return payload[16:]


def _identity(project_id: UUID, key: bytes) -> LedgerIdentity:
    return LedgerIdentity(project_id, "sha256:" + hashlib.sha256(key).hexdigest())


def _state_files(root: Path) -> tuple[tuple[int, int], ...]:
    database = _database_path(root)
    files = (
        database,
        database.with_name(database.name + "-wal"),
        database.with_name(database.name + "-shm"),
        _key_path(root),
    )
    return tuple(_path_id(_check_path(path)) for path in files)


def _validate_storage(root: Path, project_id: UUID) -> bytes:
    guard = _guard_path(root, project_id)
    validate_private_path(guard.parent, directory=True)
    _check_path(guard)
    validate_private_path(root, directory=True)
    _check_path(root / LOCK_NAME)
    _check_path(root / STORE_NAME, directory=True)
    return _read_key(root, project_id, _state_files(root)[-1])


@dataclass(frozen=True, slots=True)
class _WritePaths:
    root: Path
    pinned: tuple[_PinnedPath, ...]
    files: tuple[tuple[int, int], ...]

    def check(self) -> None:
        for pin in self.pinned:
            pin.check()
        if self.files != _state_files(self.root):
            raise LedgerError("Pinned private ledger files changed")


@contextmanager
def _connection(database: Path, *, write: bool) -> Iterator[sqlite3.Connection]:
    # Retain WAL/SHM across connection closes. A mode=ro opener otherwise
    # may need to create sidecars the next time it reads an idle WAL database.
    mode = "rw" if write else "ro"
    with closing(
        sqlite3.connect(f"{database.as_uri()}?mode={mode}", uri=True, timeout=1)
    ) as conn:
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_TRUSTED_SCHEMA, False)
        if write:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA synchronous=FULL")
        yield conn


def _schema_objects(
    conn: sqlite3.Connection,
) -> tuple[tuple[str, str, str, str | None], ...]:
    return tuple(
        conn.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name"
        )
    )


@cache
def _supported_schema() -> tuple[tuple[str, str, str, str | None], ...]:
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.executescript(_SCHEMA)
        return _schema_objects(conn)


def _validate_identity(conn: sqlite3.Connection, identity: LedgerIdentity) -> None:
    if conn.execute("PRAGMA user_version").fetchone() != (SCHEMA_VERSION,):
        raise LedgerError("Unsupported ledger schema")
    if conn.execute("PRAGMA application_id").fetchone() != (APPLICATION_ID,):
        raise LedgerError("Unrecognized ledger application")
    if conn.execute("PRAGMA journal_mode").fetchone() != ("wal",):
        raise LedgerError("Ledger requires WAL")
    if _schema_objects(conn) != _supported_schema():
        raise LedgerError("Invalid ledger table schema")
    row = conn.execute(
        "SELECT project_id, key_id FROM identity WHERE singleton = 1"
    ).fetchone()
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


def _create_store(root: Path, project_id: UUID, pins: tuple[_PinnedPath, ...]) -> None:
    # Publish the initialized key, database and WAL sidecars in one rename.
    # A crash before that rename leaves no partial canonical ledger.
    with TemporaryDirectory(prefix=".initializing-", dir=root) as name:
        staging = Path(name)
        _check_path(staging, directory=True)
        key = secrets.token_bytes(KEY_SIZE)
        key_file = staging / KEY_NAME
        key_fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(key_fd, "wb") as handle:
            os.fchmod(handle.fileno(), 0o600)
            _private(os.fstat(handle.fileno()))
            _check_acl(handle.fileno())
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
        for pin in pins:
            pin.check()
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


def _current_command(
    conn: sqlite3.Connection,
    key: SourceRef,
    command: InboxCommand,
    digest: CommandDigest,
) -> tuple[int, CommandReceipt] | None:
    row = conn.execute(
        "SELECT revision, payload FROM revisions WHERE key = ? ORDER BY revision DESC LIMIT 1",
        (key.value,),
    ).fetchone()
    if row is None:
        return None
    revision = _decode(row[1], Revision)
    receipt = revision.record
    if (
        not isinstance(receipt, CommandReceipt)
        or receipt.digest != digest
        or receipt.command != command
    ):
        raise ConflictError("Inbox command ID has conflicting bytes")
    return row[0], receipt


def _append_checkpoint(
    conn: sqlite3.Connection,
    sequence: int,
    batch: LedgerBatch,
    *,
    revisions_changed: bool,
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
    current_payload = None if stored is None else stored[0]
    prior_payload = None if prior is None else _encode(prior, SourceCheckpoint)
    if current_payload != prior_payload and (
        revisions_changed or current_payload != payload
    ):
        raise ConflictError("Source checkpoint has changed")
    if current_payload == payload:
        return False
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
    _write_paths: _WritePaths | None = field(default=None, repr=False, compare=False)

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
        with project_guard(root, project_id, initialize=True) as guard:
            _ensure_private_directory(root)
            store = root / STORE_NAME
            with (
                _pin_directory(root) as project,
                _lease(root / LOCK_NAME, create=not _path_exists(store)) as local,
            ):
                if not _path_exists(store):
                    try:
                        _create_store(root, project_id, (guard, project, local))
                    except OSError:
                        raise LedgerError(
                            "Unable to initialize private ledger"
                        ) from None
                return cls.open(root, project_id)

    @classmethod
    def open(cls, root: Path, project_id: UUID) -> "Ledger":
        root = _project_path(root)
        with _read_snapshot(root, project_id) as (_, identity, key):
            return cls(root, identity, key)

    def pseudonymize(self, namespace: str, raw_reference: str) -> SourceRef:
        """Derive a stable private reference with a domain specific to its use."""
        if (
            type(namespace) is not str
            or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", namespace)
            or type(raw_reference) is not str
            or not raw_reference
        ):
            raise ValueError("A reference namespace and identifier are required")
        message = (
            b"aitm-usage/source-ref/v1\0"
            + self.identity.project_id.bytes
            + namespace.encode("ascii")
            + b"\0"
        )
        try:
            raw_bytes = raw_reference.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("Invalid source reference encoding") from None
        digest = hmac.digest(self._key, message + raw_bytes, "sha256")
        return SourceRef(
            f"hmac-sha256:{digest.hex()}:{self._reference_tag(digest).hex()}"
        )

    def _reference_tag(self, digest: bytes) -> bytes:
        message = (
            b"aitm-usage/source-proof/v1\0" + self.identity.project_id.bytes + digest
        )
        return hmac.digest(self._key, message, "sha256")

    def validate_source_ref(self, reference: SourceRef) -> None:
        """Reject pseudonyms without a valid proof for this project and key."""
        if type(reference) is not SourceRef:
            raise LedgerError("Source reference authentication failed")
        try:
            value = SourceRef(reference.value).value
        except (AttributeError, ValueError):
            raise LedgerError("Source reference authentication failed") from None
        _, digest, tag = value.split(":")
        if not hmac.compare_digest(
            self._reference_tag(bytes.fromhex(digest)).hex(), tag
        ):
            raise LedgerError("Source reference authentication failed")

    def validate_marker(self, marker: ScopeMarker) -> None:
        _encode(marker, ScopeMarker, validate_ref=self.validate_source_ref)
        if marker.project_id != self.identity.project_id:
            raise LedgerError("Scope marker project identity mismatch")

    def validate_boundary(self, boundary: SourceBoundary) -> None:
        _encode(boundary, SourceBoundary, validate_ref=self.validate_source_ref)

    def validate_command(self, command: InboxCommand) -> CommandDigest:
        if command.project_id != self.identity.project_id:
            raise LedgerError("Inbox command project identity mismatch")
        canonical = _encode(
            command, InboxCommand, validate_ref=self.validate_source_ref
        ).encode("utf-8")
        payload = command.payload
        if isinstance(payload, ScopeCorrection):
            marker = payload.replacement
        elif isinstance(payload, DevelopmentBinding):
            marker = payload.marker
        else:
            marker = payload
        if isinstance(marker, ScopeMarker) and marker.receipt_ref is not None:
            expected = self.pseudonymize("scope-receipt", str(marker.marker_id))
            if expected != marker.receipt_ref:
                raise LedgerError("Scope receipt does not match command identity")
        return CommandDigest("sha256:" + hashlib.sha256(canonical).hexdigest())

    def command_receipt(self, command: InboxCommand) -> CommandReceipt | None:
        """Read the current receipt without acquiring the writer lease."""
        digest = self.validate_command(command)
        key = self.pseudonymize("inbox-command", str(command.command_id))
        with self.reader() as conn:
            previous = _current_command(conn, key, command, digest)
        return None if previous is None else previous[1]

    def require_writer(self) -> None:
        if self._writer is None or self._write_paths is None:
            raise LedgerError("Inbox consumption requires the project writer")
        self._write_paths.check()

    def commit_command(
        self,
        receipt: CommandReceipt,
        effects: tuple[Revision, ...],
        *,
        expected_sequence: int,
    ) -> CommandReceipt:
        """Atomically append command effects and the pending or final receipt."""
        self.require_writer()
        command = receipt.command
        if self.validate_command(command) != receipt.digest:
            raise ValueError("Inbox command digest mismatch")
        if bool(effects) != (receipt.disposition is MarkerDisposition.ACCEPTED):
            raise ValueError("Only accepted commands write effects")
        for effect in effects:
            record = effect.record
            if isinstance(record, CommandReceipt):
                raise ValueError("An inbox receipt cannot be a command effect")
            marker = record.marker if isinstance(record, ScopeEnrollment) else record
            if isinstance(marker, ScopeMarker):
                self.validate_marker(marker)
        _encode(receipt, CommandReceipt, validate_ref=self.validate_source_ref)
        _encode(
            LedgerBatch(effects), LedgerBatch, validate_ref=self.validate_source_ref
        )

        key = self.pseudonymize("inbox-command", str(command.command_id))
        with self._write_transaction() as conn:
            previous = _current_command(conn, key, command, receipt.digest)
            if previous is not None:
                number, current = previous
                if (
                    current.disposition is not MarkerDisposition.PENDING
                    or receipt.disposition is MarkerDisposition.PENDING
                ):
                    return current
            else:
                number = 0
            head = _head(conn)
            if head != expected_sequence:
                raise ConflictError("Ledger changed during inbox evaluation")
            sequence = head + 1
            conn.execute("INSERT INTO commits VALUES (?)", (sequence,))
            _append_revisions(
                conn, sequence, (*effects, Revision(key, number + 1, receipt))
            )
            self.require_writer()
        return receipt

    def validate_quota(self, evidence: QuotaEvidence) -> None:
        _encode(evidence, QuotaEvidence, validate_ref=self.validate_source_ref)

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
        with (
            project_guard(self.root, self.identity.project_id) as guard,
            _lease(self.lock_path) as local,
            _pin_directory(self.root) as project,
            _pin_directory(self.root / STORE_NAME) as store,
        ):
            paths = _WritePaths(
                self.root, (guard, local, project, store), _state_files(self.root)
            )
            with self.reader():
                pass
            paths.check()
            with _connection(self.database_path, write=True) as conn:
                yield Ledger(self.root, self.identity, self._key, conn, paths)

    def apply(self, batch: LedgerBatch) -> int:
        # Reject malformed envelopes before the writer opens a transaction.
        _encode(batch, LedgerBatch, validate_ref=self.validate_source_ref)
        for revision in batch.revisions:
            record = revision.record
            if isinstance(record, (CommandReceipt, ScopeEnrollment)):
                raise LedgerError("Inbox records require atomic command admission")
            if (
                isinstance(record, ScopeMarker)
                and record.project_id != self.identity.project_id
            ):
                raise LedgerError("Scope marker project identity mismatch")
        if self._writer is not None:
            return self._apply(batch)
        with self.writer() as writer:
            return writer._apply(batch)

    @contextmanager
    def _write_transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self._writer
        paths = self._write_paths
        assert conn is not None and paths is not None
        paths.check()
        key = _read_key(self.root, self.identity.project_id, paths.files[-1])
        if not hmac.compare_digest(key, self._key):
            raise LedgerError("Ledger identity changed")
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            _validate_identity(conn, self.identity)
            yield conn

    def _apply(self, batch: LedgerBatch) -> int:
        with self._write_transaction() as conn:
            head = _head(conn)
            sequence = head + 1
            conn.execute("INSERT INTO commits VALUES (?)", (sequence,))
            revisions_changed = _append_revisions(conn, sequence, batch.revisions)
            checkpoint_changed = _append_checkpoint(
                conn, sequence, batch, revisions_changed=revisions_changed
            )
            if revisions_changed or checkpoint_changed:
                self.require_writer()
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
                self.identity.project_id,
                sequence,
                tuple(
                    _decode(row[0], Revision, validate_ref=self.validate_source_ref)
                    for row in revisions
                ),
                tuple(
                    _decode(
                        row[0], SourceCheckpoint, validate_ref=self.validate_source_ref
                    )
                    for row in checkpoints
                ),
            )
