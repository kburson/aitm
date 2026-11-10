"""Fixed-view private SQLite backups and guarded, same-identity restore."""

import hashlib
import json
import os
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from .host_fs import HostFilesystemError, exchange_entries, publish_noreplace
from .ledger import (
    DATABASE_NAME,
    KEY_NAME,
    LOCK_NAME,
    MONITOR_SCHEMA_VERSION,
    STORE_NAME,
    SUPPORTED_SCHEMA_VERSIONS,
    Ledger,
    LedgerError,
    LedgerIdentity,
    WriterActive,
    _check_acl,
    _check_path,
    _connection,
    _head,
    _identity,
    _lease,
    _path_id,
    _pin_directory,
    _PinnedPath,
    _private,
    _read_key,
    _state_files,
    _sync_directory,
    _validate_identity,
    _validated_path,
    project_guard,
)
from .scopes import (
    ACKS_NAME,
    INBOX_NAME,
    _marker,
    _private_child,
    _publication,
    _publish,
    _read_private,
    _read_publications,
)
from .service import (
    ANCHORS_NAME,
    CLAUDE_SESSIONS_NAME,
    REGISTRATION_NAME,
    _anchor_commit_sequence,
    _anchor_revision,
    _authorized_config,
    _session_filename,
    _staged_anchor,
    load_registration,
)
from .types import (
    CommandAcknowledgment,
    CommandReceipt,
    LedgerView,
    MarkerDisposition,
    Provider,
    SourceAnchorCommand,
    _decode,
    _encode,
)

_MANIFEST = "manifest.json"
_KEY = f"{STORE_NAME}/{KEY_NAME}"
_DATABASE = f"{STORE_NAME}/{DATABASE_NAME}"


class BackupError(LedgerError):
    """The project backup or restore could not be verified."""


@dataclass(frozen=True, slots=True)
class BackupReceipt:
    project_id: UUID
    key_id: str
    schema_version: int
    sequence: int
    manifest_sha256: str

    def as_dict(self) -> dict:
        return {
            "project_id": str(self.project_id),
            "key_id": self.key_id,
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "manifest_sha256": self.manifest_sha256,
        }


@dataclass(frozen=True, slots=True)
class RestoreReceipt(BackupReceipt):
    pass


def _json(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _absolute(path: Path) -> Path:
    if not path.is_absolute() or ".." in path.parts or not path.name:
        raise BackupError("Expected an absolute canonical backup path")
    return path


def _require_outside(
    directory: _PinnedPath, path: Path, *, file: bool = False, missing: bool = False
) -> None:
    """Reject physical containment, including alternate APFS path spellings."""
    directory.check()
    ancestry = _validated_path(
        _absolute(path), directory=not file, allow_missing=missing
    )
    if directory.identities[-1] in ancestry:
        raise BackupError("Recovery material overlaps a replaceable directory")


def _copy_file(directory: _PinnedPath, name: str, destination: Path) -> str:
    """Copy a private regular file by descriptor and hash the bytes copied."""
    directory.check()
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory.fd)
    with os.fdopen(fd, "rb") as source:
        info = os.fstat(fd)
        _private(info)
        _check_acl(fd)
        digest = hashlib.sha256()
        with _create_file(destination) as output:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        current = os.stat(name, dir_fd=directory.fd, follow_symlinks=False)
        if not os.path.samestat(info, current) or (
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ) != (current.st_size, current.st_mtime_ns, current.st_ctime_ns):
            raise BackupError("Private backup file changed during copy")
    directory.check()
    return digest.hexdigest()


@contextmanager
def _create_file(path: Path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        _private(os.fstat(fd))
        _check_acl(fd)
        yield output
        output.flush()
        os.fsync(fd)


def _copy_snapshot(reader: sqlite3.Connection, destination: Path) -> None:
    with _create_file(destination):
        pass
    with closing(sqlite3.connect(destination)) as copy:
        reader.backup(copy)


def _private_store(root: Path) -> Path:
    store = root / STORE_NAME
    store.mkdir(mode=0o700)
    _check_path(store, directory=True)
    return store


def _candidate(root: Path, identity: LedgerIdentity) -> Ledger:
    with _create_file(root / LOCK_NAME):
        pass
    path = root / _DATABASE
    _check_path(path)
    with _connection(path, write=True) as conn:
        _validate_identity(conn, identity)
        sequence = _head(conn)
        if conn.execute("PRAGMA integrity_check").fetchall() != [("ok",)] or (
            conn.execute("PRAGMA foreign_key_check").fetchone() is not None
        ):
            raise BackupError("Invalid backup database integrity")
        if conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone() != (0, 0, 0):
            raise BackupError("Unable to prepare clean restore sidecars")
    _state_files(root)
    _sync_directory(path.parent)
    candidate = Ledger.open(root, identity.project_id)
    if candidate.identity != identity:
        raise BackupError("Backup project or key identity mismatch")
    if identity.schema_version == MONITOR_SCHEMA_VERSION:
        candidate.monitor_as_of(sequence)
    return candidate


def _receipts(ledger: Ledger, view: LedgerView) -> dict[UUID, CommandReceipt]:
    receipts = {}
    for entry in view.current:
        receipt = entry.record
        if not isinstance(receipt, CommandReceipt):
            continue
        command = receipt.command
        if receipt.digest != ledger.validate_command(
            command
        ) or entry.key != ledger.pseudonymize("inbox-command", str(command.command_id)):
            raise BackupError("Invalid durable command receipt")
        receipts[command.command_id] = receipt
    return receipts


def _authority_names(ledger: Ledger, view: LedgerView) -> tuple[str, ...]:
    names = [REGISTRATION_NAME]
    current = {entry.key: entry for entry in view.current}
    for entry in view.current:
        receipt = entry.record
        if (
            not isinstance(receipt, CommandReceipt)
            or not isinstance(receipt.command.payload, SourceAnchorCommand)
            or receipt.disposition is not MarkerDisposition.ACCEPTED
        ):
            continue
        command = receipt.command
        effect = _anchor_revision(ledger, command.payload)
        if current.get(effect.key) != effect:
            raise BackupError("Backup anchor effect is unavailable")
        sequence = _anchor_commit_sequence(ledger, entry, effect, view.sequence)
        if sequence is None:
            raise BackupError("Backup anchor commit is unavailable")
        names.extend(
            (
                f"{ANCHORS_NAME}/{command.command_id}.json",
                f"{ANCHORS_NAME}/{command.command_id}.{sequence}.attested",
            )
        )
    return tuple(sorted(names))


def _authority(project: _PinnedPath, names: tuple[str, ...]) -> dict[str, bytes]:
    data = {}
    with _private_child(project, ANCHORS_NAME, create=False) as anchors:
        for name in names:
            if name == REGISTRATION_NAME:
                value = _read_private(project, name)
            else:
                value = (
                    None if anchors is None else _read_private(anchors, Path(name).name)
                )
            if value is None:
                raise BackupError("Required private backup authority is missing")
            data[name] = value
    return data


def _write_authority(project: _PinnedPath, data: dict[str, bytes]) -> None:
    if not _publish(project, REGISTRATION_NAME, data[REGISTRATION_NAME]):
        raise BackupError("Backup authority staging already exists")
    if len(data) > 1:
        with _private_child(project, ANCHORS_NAME, create=True) as anchors:
            assert anchors is not None
            for name, value in data.items():
                if name != REGISTRATION_NAME and not _publish(
                    anchors, Path(name).name, value
                ):
                    raise BackupError("Backup anchor staging already exists")


def _file_digest(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _manifest(
    candidate: Ledger, view: LedgerView, files: dict[str, str]
) -> tuple[bytes, BackupReceipt]:
    identity = candidate.identity
    body = {
        "format": f"aitm-usage.backup/v{identity.schema_version}",
        "project_id": str(identity.project_id),
        "key_id": identity.key_id,
        "schema_version": identity.schema_version,
        "sequence": view.sequence,
        "files": files,
    }
    proof = candidate.pseudonymize("collector-backup-manifest", _json(body).decode())
    data = _json({**body, "proof": proof.value})
    return data, BackupReceipt(
        identity.project_id,
        identity.key_id,
        identity.schema_version,
        view.sequence,
        hashlib.sha256(data).hexdigest(),
    )


def _authority_digests(data: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}


@contextmanager
def _publication_parent(destination: Path, store: _PinnedPath) -> Iterator[int]:
    _require_outside(store, destination, missing=True)
    ancestry = _validated_path(destination, directory=True, allow_missing=True)
    if len(ancestry) != len(destination.parents):
        raise BackupError("Backup destination must be new with an existing parent")
    fd = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if _path_id(os.fstat(fd)) != ancestry[-1]:
            raise BackupError("Backup destination parent changed")
        yield fd
    finally:
        os.close(fd)


def backup(ledger: Ledger, destination: Path) -> BackupReceipt:
    """Publish one complete, lease-free snapshot and its exact private authority."""
    try:
        destination = _absolute(destination)
        with (
            _pin_directory(ledger.database_path.parent) as live_store,
            _publication_parent(destination, live_store) as parent,
            _pin_directory(ledger.root) as live,
            TemporaryDirectory(prefix=".usage-backup-", dir=destination.parent) as work,
            _pin_directory(Path(work)) as staging,
        ):
            snapshot = staging.path / "snapshot"
            snapshot.mkdir(mode=0o700)
            store = _private_store(snapshot)
            with _pin_directory(snapshot) as staged, ledger.reader() as reader:
                sequence = _head(reader)
                key = _read_key(
                    ledger.root,
                    ledger.identity.project_id,
                    _state_files(ledger.root)[-1],
                )
                if (
                    _identity(
                        ledger.identity.project_id, key, ledger.identity.schema_version
                    )
                    != ledger.identity
                ):
                    raise BackupError("Backup pseudonym key changed")
                with _create_file(store / KEY_NAME) as output:
                    output.write(ledger.identity.project_id.bytes + key)
                _copy_snapshot(reader, store / DATABASE_NAME)
                live.check()
                staged.check()

            candidate = _candidate(snapshot, ledger.identity)
            view = candidate.as_of()
            if view.sequence != sequence:
                raise BackupError("Backup snapshot cutoff changed")
            names = _authority_names(candidate, view)
            with (
                _pin_directory(snapshot) as staged,
                _pin_directory(store) as staged_store,
            ):
                authority = _authority(live, names)
                _write_authority(staged, authority)
                load_registration(candidate)
                _receipts(candidate, view)
                for suffix in ("-wal", "-shm"):
                    (store / f"{DATABASE_NAME}{suffix}").unlink()
                (snapshot / LOCK_NAME).unlink()
                with (store / DATABASE_NAME).open("rb") as database:
                    os.fsync(database.fileno())
                _sync_directory(store)
                data, receipt = _manifest(
                    candidate,
                    view,
                    {
                        _DATABASE: _file_digest(snapshot / _DATABASE),
                        _KEY: _file_digest(snapshot / _KEY),
                        **_authority_digests(authority),
                    },
                )
                if not _publish(staged, _MANIFEST, data):
                    raise BackupError("Backup manifest staging already exists")
                staging.check()
                staged.check()
                staged_store.check()
                _require_outside(live_store, destination, missing=True)
                if staging.identities[-2] != _path_id(os.fstat(parent)):
                    raise BackupError("Backup destination parent changed")
                try:
                    published = publish_noreplace(
                        staging.fd, "snapshot", parent, destination.name
                    )
                except HostFilesystemError:
                    raise BackupError("Unable to publish private backup") from None
                if not published:
                    raise BackupError("Unable to publish private backup")
                os.fsync(staging.fd)
                os.fsync(parent)
                if (
                    _validated_path(destination, directory=True)[-1]
                    != staged.identities[-1]
                ):
                    raise BackupError("Published backup path changed")
            return receipt
    except BackupError:
        raise
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        raise BackupError("Invalid private backup source or destination") from None


def _verify_bundle(
    source: Path, staging: Path, expected: LedgerIdentity
) -> tuple[Ledger, LedgerView, dict[str, bytes], BackupReceipt]:
    if (
        type(expected.schema_version) is not int
        or expected.schema_version not in SUPPORTED_SCHEMA_VERSIONS
    ):
        raise BackupError("Unsupported restore schema")
    store = _private_store(staging)
    with (
        _pin_directory(_absolute(source)) as bundle,
        _private_child(bundle, STORE_NAME, create=False) as original,
        _pin_directory(staging) as staged,
    ):
        if original is None or set(os.listdir(original.fd)) != {
            DATABASE_NAME,
            KEY_NAME,
        }:
            raise BackupError("Unexpected backup store files")
        files = {
            _DATABASE: _copy_file(original, DATABASE_NAME, store / DATABASE_NAME),
            _KEY: _copy_file(original, KEY_NAME, store / KEY_NAME),
        }
        candidate = _candidate(staging, expected)
        view = candidate.as_of()
        names = _authority_names(candidate, view)
        top_level = {_MANIFEST, STORE_NAME, REGISTRATION_NAME}
        if len(names) > 1:
            top_level.add(ANCHORS_NAME)
            with _private_child(bundle, ANCHORS_NAME, create=False) as anchors:
                if anchors is None or set(os.listdir(anchors.fd)) != {
                    Path(name).name for name in names if name != REGISTRATION_NAME
                }:
                    raise BackupError("Unexpected backup anchor authority")
        if set(os.listdir(bundle.fd)) != top_level:
            raise BackupError("Unexpected backup bundle files")
        authority = _authority(bundle, names)
        manifest, receipt = _manifest(
            candidate, view, {**files, **_authority_digests(authority)}
        )
        # Compare the complete authenticated manifest with the copied bytes.
        # Read by fd, with a bound derived from the expected manifest, so a
        # legitimate project with many accepted anchors can still be restored.
        fd = os.open(
            _MANIFEST, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=bundle.fd
        )
        with os.fdopen(fd, "rb") as stream:
            _private(os.fstat(fd))
            _check_acl(fd)
            if stream.read(len(manifest) + 1) != manifest:
                raise BackupError("Backup manifest does not match its verified bytes")
        _write_authority(staged, authority)
        load_registration(candidate)
        _receipts(candidate, view)
        bundle.check()
        staged.check()
        return candidate, view, authority, receipt


def verify_backup(source: Path, ledger: Ledger) -> BackupReceipt:
    """Verify a retained recovery bundle independently of current live state."""
    try:
        with (
            _pin_directory(ledger.root) as project,
            TemporaryDirectory(prefix=".verify-backup-", dir=project.path) as directory,
        ):
            return _verify_bundle(source, Path(directory), ledger.identity)[3]
    except BackupError:
        raise
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        raise BackupError("Invalid private recovery backup") from None


def _validate_queue(
    project: _PinnedPath,
    inbox: _PinnedPath,
    live: Ledger,
    candidate: Ledger,
    view: LedgerView,
) -> None:
    pending = _read_publications(inbox, candidate)
    if pending.invalid or pending.relationship_halted:
        raise BackupError("Retained pending inbox is unsafe")
    receipts = _receipts(candidate, view)
    queued = {
        publication.command.command_id: publication.command
        for publication in pending.publications
    }
    pending_history = {
        revision.record.acknowledgment
        for revision in view.revisions
        if isinstance(revision.record, CommandReceipt)
        and revision.record.disposition is MarkerDisposition.PENDING
        and revision.record.command == queued.get(revision.record.command.command_id)
    }
    with _private_child(inbox, ACKS_NAME, create=False) as acknowledgments:
        if acknowledgments is not None:
            for name in os.listdir(acknowledgments.fd):
                if name.startswith(".publishing-"):
                    continue
                raw = _read_private(acknowledgments, name)
                try:
                    acknowledgment = _decode(raw, CommandAcknowledgment)
                    receipt = receipts.get(acknowledgment.command_id)
                    if (
                        name == f"{acknowledgment.command_id}.json"
                        and raw
                        == _encode(acknowledgment, CommandAcknowledgment).encode()
                        and receipt is not None
                        and (
                            acknowledgment == receipt.acknowledgment
                            or (
                                acknowledgment in pending_history
                                and receipt.command
                                == queued.get(acknowledgment.command_id)
                                and receipt.digest == acknowledgment.digest
                            )
                        )
                    ):
                        continue
                except (ValueError, TypeError):
                    pass
                raise BackupError("Retained acknowledgment has no exact backup receipt")
    if not pending.publications:
        return

    live_view = live.as_of()
    _, configuration = _authorized_config(candidate, view)
    for publication in pending.publications:
        command = publication.command
        # The normal receipt API also refuses any digest or command conflict.
        candidate_receipt = candidate.command_receipt(command)
        if live.command_receipt(command) != candidate_receipt:
            raise BackupError(
                "Retained pending command conflicts with restored history"
            )
        if (
            candidate_receipt is not None
            and candidate_receipt.disposition is not MarkerDisposition.PENDING
        ):
            continue
        # An uncommitted command can depend on scope, checkpoint, or ordered
        # relationship history. Require unchanged input history for its replay.
        if live_view != view:
            raise BackupError("Retained pending command has a different replay view")
        payload = command.payload
        if isinstance(payload, SourceAnchorCommand) and (
            payload.configuration_ref != configuration.configuration_ref
            or _staged_anchor(live, payload) is None
        ):
            raise BackupError("Retained pending anchor authority is unsafe")
        marker = _marker(command)
        if marker is not None and marker.provider is Provider.CLAUDE:
            with _private_child(
                project, CLAUDE_SESSIONS_NAME, create=False
            ) as sessions:
                if (
                    sessions is None
                    or _read_private(sessions, _session_filename(marker.session_ref))
                    != json.dumps(marker.session_ref.value).encode()
                ):
                    raise BackupError(
                        "Retained pending Claude session authority is unsafe"
                    )


def _swap_store(project: _PinnedPath, staged: _PinnedPath) -> None:
    try:
        exchange_entries(staged.fd, STORE_NAME, project.fd, STORE_NAME)
    except HostFilesystemError:
        raise BackupError("Unable to atomically replace the private store") from None
    os.fsync(staged.fd)
    os.fsync(project.fd)


def restore(
    source: Path,
    destination: Path,
    expected: LedgerIdentity,
) -> RestoreReceipt:
    """Restore a stopped registered project under its lifecycle and writer guards."""
    # Lifecycle operations use this module for snapshots, while the public
    # restore entry point requires the same launchd preflight as the CLI.
    from .install import LaunchControl, restore_for_agent

    try:
        if (
            type(expected.schema_version) is not int
            or expected.schema_version not in SUPPORTED_SCHEMA_VERSIONS
        ):
            raise BackupError("Unsupported restore schema")
        ledger = Ledger.open(_absolute(destination), expected.project_id)
        if ledger.identity != expected:
            raise BackupError("Restore target identity mismatch")
        return restore_for_agent(ledger, source, LaunchControl())
    except (BackupError, WriterActive):
        raise
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        raise BackupError(
            "Restore target is not a stopped compatible project"
        ) from None


def _restore_stopped(
    source: Path, ledger: Ledger, verify_stopped: Callable[[], None]
) -> RestoreReceipt:
    expected = ledger.identity
    try:
        root = ledger.root
        with (
            project_guard(root, expected.project_id) as guard,
            _lease(root / LOCK_NAME) as local,
            _pin_directory(root) as project,
            _pin_directory(root / STORE_NAME) as live_store,
            _pin_directory(_absolute(source)) as bundle,
            TemporaryDirectory(prefix=".usage-restore-", dir=root) as directory,
            _pin_directory(Path(directory)) as staged,
        ):
            verify_stopped()
            _require_outside(live_store, bundle.path)
            live = Ledger.open(root, expected.project_id)
            if live.identity != expected:
                raise BackupError("Restore target identity mismatch")
            live_files = _state_files(root)
            candidate, view, authority, receipt = _verify_bundle(
                source, staged.path, expected
            )
            if _authority(project, tuple(authority)) != authority:
                raise BackupError("Retained private authority differs from the backup")
            with (
                _pin_directory(staged.path / STORE_NAME) as staged_store,
                _private_child(project, INBOX_NAME, create=True) as inbox,
            ):
                assert inbox is not None
                staged_files = _state_files(staged.path)
                with _publication(inbox):
                    _validate_queue(project, inbox, live, candidate, view)
                    if _authority(project, tuple(authority)) != authority:
                        raise BackupError("Retained private authority changed")
                    verify_stopped()
                    for pin in (
                        guard,
                        local,
                        project,
                        live_store,
                        staged,
                        staged_store,
                        inbox,
                        bundle,
                    ):
                        pin.check()
                    if (
                        _state_files(root) != live_files
                        or _state_files(staged.path) != staged_files
                    ):
                        raise BackupError("Private restore store files changed")
                    _require_outside(live_store, bundle.path)
                    _swap_store(project, staged)
            return RestoreReceipt(
                receipt.project_id,
                receipt.key_id,
                receipt.schema_version,
                receipt.sequence,
                receipt.manifest_sha256,
            )
    except (BackupError, WriterActive):
        raise
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        raise BackupError("Invalid private restore bundle or target") from None
