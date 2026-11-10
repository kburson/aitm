"""Private owner-command publication and enqueue-only monitor CLI handlers."""

import argparse
import json
import os
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import MISSING, dataclass, field, fields, replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from . import monitor_registry
from .ledger import (
    ConflictError,
    Ledger,
    LedgerError,
    _ensure_private_directory,
    _path_exists,
    _pin_directory,
    _PinnedPath,
    _project_path,
    _validated_path,
)
from .monitor_registry import (
    AnchorRequest,
    CaptureChange,
    ControlCommand,
    ControlPayload,
    ControlReceipt,
    ControlStatus,
    ProjectRegistrationRequest,
    Registry,
    SourceApprovalRequest,
)
from .monitor_scope import Scope
from .scope_admission import (
    REQUEST_TYPES,
    GrantRole,
    ScopeEnvelope,
    ScopeRequest,
    _witness_for_probe,
    _write_grant,
    adopted_request,
    build_grant,
    check_witness_time,
    open_grant,
    pinned_destination,
    preliminary_grant,
    require_witness,
    seal_request,
    stored_grant,
)
from .scopes import (
    INBOX_NAME,
    MAX_COMMAND_BYTES,
    _filename,
    _private_child,
    _publication,
    _publish,
    _read_private,
)
from .types import (
    InboxCommand,
    ItemKey,
    SourceRef,
    _decode,
    _encode,
    _positive,
    _unique_fields,
)

_InboxCommand = ControlCommand | ScopeEnvelope
_MAX_SCOPE_PENDING = 256


def _command_bytes(command: _InboxCommand) -> bytes:
    data = _encode(command, type(command)).encode("utf-8")
    if len(data) > MAX_COMMAND_BYTES:
        raise ValueError("Monitor command exceeds its size limit")
    return data


@dataclass(frozen=True, slots=True)
class _QueuedCommand:
    command: _InboxCommand
    order: int

    def __post_init__(self) -> None:
        _positive(self.order)


@dataclass(frozen=True, slots=True)
class _LockedInbox:
    directory: _PinnedPath
    captured: dict[UUID, tuple[_InboxCommand, bytes]] = field(default_factory=dict)


def _decode_publication(name: str, data: bytes) -> _QueuedCommand:
    try:
        queued = _decode(data, _QueuedCommand)
        if (
            _filename(queued.command.command_id) == name
            and _encode(queued, _QueuedCommand).encode("utf-8") == data
        ):
            return queued
    except ValueError:
        pass
    raise LedgerError("Invalid private monitor publication")


def _pending(inbox: _PinnedPath) -> dict[int, tuple[_InboxCommand, bytes]]:
    pending = {}
    for name in os.listdir(inbox.fd):
        if name.startswith(".") or not name.endswith(".json"):
            continue
        data = _read_private(inbox, name)
        if data is None:
            raise LedgerError("Private monitor publication disappeared")
        queued = _decode_publication(name, data)
        if queued.order in pending:
            raise LedgerError("Duplicate monitor publication order")
        pending[queued.order] = queued.command, data
    return pending


class ControlInbox:
    """Private queue with a publication lock independent of the coordinator."""

    def __init__(self, root: Path) -> None:
        self.root = _project_path(root)

    @contextmanager
    def publication(self) -> Iterator[_LockedInbox]:
        """Pin and lock the account inbox until the caller completes its updates."""
        try:
            _ensure_private_directory(self.root)
            with _pin_directory(self.root) as root:
                with _private_child(root, INBOX_NAME, create=True) as inbox:
                    assert inbox is not None
                    with _publication(inbox):
                        root.check()
                        yield _LockedInbox(inbox)
                        root.check()
        except OSError:
            raise LedgerError("Private monitor publication failed") from None

    def _check_inbox(self, inbox: _PinnedPath) -> None:
        if inbox.path != self.root / INBOX_NAME:
            raise LedgerError("Private monitor inbox does not match")
        inbox.check()

    def iter_pending(self, locked: _LockedInbox) -> Iterator[_InboxCommand]:
        """Read exact envelopes in submission order under publication()."""
        inbox = locked.directory
        self._check_inbox(inbox)
        for _, (command, data) in sorted(_pending(inbox).items()):
            locked.captured[command.command_id] = command, data
            yield command

    def discard(self, locked: _LockedInbox, command: ControlCommand) -> None:
        """Retire only an exact M06 control with a durable outcome."""
        if not isinstance(command, ControlCommand):
            raise LedgerError("Scope proposal retirement requires its consumer")
        inbox = locked.directory
        self._check_inbox(inbox)
        name = _filename(command.command_id)
        captured = locked.captured.get(command.command_id)
        if (
            captured is None
            or captured[0] != command
            or _read_private(inbox, name) != captured[1]
        ):
            raise ConflictError("Private monitor publication changed")
        os.unlink(name, dir_fd=inbox.fd)
        os.fsync(inbox.fd)
        inbox.check()

    def _enqueue_locked(
        self,
        locked: _LockedInbox,
        command: _InboxCommand,
        data: bytes,
        *,
        before_scope_commit: Callable[[], None] | None = None,
    ) -> ControlReceipt:
        digest = command.payload_digest
        name = _filename(command.command_id)
        receipt = Registry(self.root).command_status(command.command_id)
        if receipt is not None:
            if receipt.payload_digest != digest:
                raise ConflictError("Monitor command ID has conflicting bytes")
            return receipt

        inbox = locked.directory
        previous = _read_private(inbox, name)
        if previous is None:
            pending = _pending(inbox)
            if (
                isinstance(command, ScopeEnvelope)
                and sum(isinstance(item, ScopeEnvelope) for item, _ in pending.values())
                >= _MAX_SCOPE_PENDING
            ):
                raise LedgerError("Scope consumer is unavailable")
            order = max(pending, default=0) + 1
            encoded = _encode(_QueuedCommand(command, order), _QueuedCommand).encode()
            if len(encoded) > MAX_COMMAND_BYTES:
                raise ValueError("Monitor publication exceeds its size limit")
            if not _publish(inbox, name, encoded, before_commit=before_scope_commit):
                previous = _read_private(inbox, name)
                if previous is None:
                    raise ConflictError("Private monitor publication changed")
        if previous is not None:
            queued = _decode_publication(name, previous)
            if (
                type(queued.command) is not type(command)
                or _command_bytes(queued.command) != data
            ):
                raise ConflictError("Monitor command ID has conflicting bytes")
            # A prior publication may have reached rename before directory sync.
            os.fsync(inbox.fd)
        if before_scope_commit is not None:
            before_scope_commit()
        return ControlReceipt(command.command_id, ControlStatus.QUEUED, digest)

    def enqueue(self, command: ControlCommand) -> ControlReceipt:
        """Publish once, or return the recorded receipt for an exact retry."""
        if type(command) is not ControlCommand:
            raise ValueError("Invalid monitor control command")
        data = _command_bytes(command)
        if _decode(data, ControlCommand) != command:
            raise ValueError("Invalid monitor command")
        with self.publication() as locked:
            return self._enqueue_locked(locked, command, data)

    def enqueue_scope(self, request: ScopeRequest) -> bool:
        """Publish a scoped proposal using only pinned, initialized authority."""
        if not preliminary_grant(self.root, request.grant_id):
            return False
        registry = Registry(self.root)
        with (
            self.publication() as locked,
            open_grant(registry, request.grant_id) as (record, recheck_grant, _),
            pinned_destination(registry, request) as recheck_destination,
        ):
            require_witness(registry, record, _scope_now())
            command = seal_request(record, request)
            data = _command_bytes(command)
            if _decode(data, ScopeEnvelope) != command:
                raise ValueError("Invalid scope envelope")

            def recheck() -> None:
                recheck_grant()
                if recheck_destination is not None:
                    recheck_destination()
                check_witness_time(record, _scope_now())

            receipt = self._enqueue_locked(
                locked, command, data, before_scope_commit=recheck
            )
            return receipt.status is ControlStatus.QUEUED

    def status(self, command_id: UUID) -> ControlReceipt | None:
        """Read status without creating state or taking either writer lock."""
        if type(command_id) is not UUID:
            raise ValueError("Expected a monitor command UUID")
        if not _path_exists(self.root):
            _validated_path(self.root, directory=True, allow_missing=True)
            return None
        name = _filename(command_id)
        registry = Registry(self.root)
        try:
            with _pin_directory(self.root) as root:
                receipt = registry.command_status(command_id)
                if receipt is None:
                    queued = _queued_bytes(root, name)
                    # The writer commits the receipt before unlinking the queue entry.
                    receipt = registry.command_status(command_id)
                    if receipt is None and queued is not None:
                        command = _decode_publication(name, queued).command
                        if isinstance(command, ControlCommand):
                            digest = command.payload_digest
                            receipt = ControlReceipt(
                                command_id,
                                ControlStatus.QUEUED,
                                digest,
                                registry.pending_capture_status(command_id, digest),
                            )
                root.check()
                return receipt
        except OSError:
            raise LedgerError("Private monitor publication is unavailable") from None


def _scope_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class _ScopeReaderProof:
    probe: ScopeEnvelope
    revision: int


class ScopeInboxReader:
    """Writer-owned verifier for the typed scope variant of the monitor inbox."""

    def __init__(self, writer: Registry, inbox: ControlInbox) -> None:
        writer.lease
        if writer.root != inbox.root:
            raise LedgerError("Scope reader requires the matching monitor inbox")
        self._writer = writer
        self._inbox = inbox
        self._proofs: dict[UUID, _ScopeReaderProof] = {}

    def register(
        self,
        grant_id: UUID,
        project_id: UUID,
        actions: tuple[str, ...],
        *,
        generation: int = 1,
        role: GrantRole = GrantRole.OPERATOR,
        adoption_id: UUID | None = None,
    ) -> None:
        self._writer.lease
        with self._inbox.publication():
            record = build_grant(
                self._writer,
                grant_id,
                project_id,
                actions,
                generation,
                role,
                adoption_id,
            )
            previous = stored_grant(self._inbox.root, grant_id)
            if previous is not None and previous.grant.generation >= generation:
                raise ConflictError("Scope grant generation must advance")
            _write_grant(self._writer, record, previous)
            self._proofs.pop(grant_id, None)

    def _invalidate(self, grant_id: UUID, *, revoke: bool) -> None:
        self._writer.lease
        with self._inbox.publication():
            record = stored_grant(self._inbox.root, grant_id)
            if record is None or record.revoked:
                raise LedgerError("Scope producer grant is unavailable")
            _write_grant(
                self._writer, replace(record, witness=None, revoked=revoke), record
            )
            self._proofs.pop(grant_id, None)

    def revoke(self, grant_id: UUID) -> None:
        self._invalidate(grant_id, revoke=True)

    def withdraw(self, grant_id: UUID) -> None:
        """Withdraw reader admission without rotating the producer grant."""
        self._invalidate(grant_id, revoke=False)

    def _verify(self, candidate: ScopeEnvelope) -> ScopeEnvelope:
        self._writer.lease
        request = candidate.body.request
        with (
            open_grant(self._writer, request.grant_id) as (record, _, _),
            pinned_destination(self._writer, request),
        ):
            if seal_request(record, request) != candidate:
                raise LedgerError("Scope envelope seal does not match")
        return candidate

    def probe(self, request: ScopeRequest) -> _ScopeReaderProof:
        """Verify a canonical sealed probe through the real queue decoder."""
        self._writer.lease
        with (
            self._inbox.publication(),
            open_grant(self._writer, request.grant_id) as (record, _, revision),
        ):
            signed = seal_request(record, request)
            data = _encode(_QueuedCommand(signed, 1), _QueuedCommand).encode()
            candidate = _decode_publication(_filename(signed.command_id), data).command
            if not isinstance(candidate, ScopeEnvelope):
                raise LedgerError("Scope reader could not decode its protocol")
            proof = _ScopeReaderProof(self._verify(candidate), revision)
            self._proofs[request.grant_id] = proof
            return proof

    def advertise(self, proof: _ScopeReaderProof) -> None:
        self._writer.lease
        if type(proof) is not _ScopeReaderProof:
            raise LedgerError("Scope reader proof is unavailable")
        grant_id = proof.probe.body.request.grant_id
        with (
            self._inbox.publication(),
            open_grant(self._writer, grant_id) as (record, _, revision),
        ):
            if self._proofs.get(grant_id) is not proof or proof.revision != revision:
                raise LedgerError("Scope reader proof is unavailable")
            self._verify(proof.probe)
            witness = _witness_for_probe(
                self._writer, record, _scope_now(), proof.probe
            )
            _write_grant(self._writer, replace(record, witness=witness), record)
            self._proofs.pop(grant_id)

    def iter_verified(self, locked: _LockedInbox) -> Iterator[ScopeEnvelope]:
        self._writer.lease
        for candidate in self._inbox.iter_pending(locked):
            if isinstance(candidate, ScopeEnvelope):
                yield self._verify(candidate)


def enqueue_adopted_scope(
    ledger: Ledger,
    adoption_id: UUID,
    command: InboxCommand,
    claude_session: SourceRef | None,
) -> bool:
    """Submit exactly the verified legacy command without opening a writer lease."""
    try:
        ledger.validate_command(command)
        request = adopted_request(command, adoption_id, claude_session)
        return ControlInbox(monitor_registry.default_monitor_root()).enqueue_scope(
            request
        )
    except (LedgerError, OSError, RecursionError, sqlite3.Error, ValueError):
        return False


def _queued_bytes(root: _PinnedPath, name: str) -> bytes | None:
    with _private_child(root, INBOX_NAME, create=False) as inbox:
        if inbox is None:
            return None
        try:
            data = _read_private(inbox, name)
        except (FileNotFoundError, LedgerError):
            # Retirement may remove the name or drop the opened link count.
            inbox.check()
            try:
                os.stat(name, dir_fd=inbox.fd, follow_symlinks=False)
            except FileNotFoundError:
                return None
            raise
        inbox.check()
        return data


@dataclass(frozen=True, slots=True)
class _AnchorConfig:
    anchor: str


def _owner_document(path: Path) -> dict:
    path = _project_path(path)
    identities = _validated_path(path, directory=False)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as handle:
        pin = _PinnedPath(path, fd, False, identities)
        pin.check()
        raw = handle.read(MAX_COMMAND_BYTES + 1)
        pin.check()
    if len(raw) > MAX_COMMAND_BYTES:
        raise ValueError("Monitor configuration exceeds its size limit")
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_fields)
    if type(data) is not dict:
        raise ValueError("Expected a private configuration object")
    return data


def _owner_config[T](path: Path, model: type[T], **defaults: object) -> T:
    return _decode(json.dumps({**defaults, **_owner_document(path)}), model)


def _scope_defaults(model: type, document: dict) -> dict:
    defaults = {
        item.name: item.default for item in fields(model) if item.default is not MISSING
    }
    return {**defaults, **document}


def _scope_config(path: Path, model: type) -> ScopeRequest:
    document = _scope_defaults(model, _owner_document(path))
    for name in ("scope", "destination"):
        if type(document.get(name)) is dict:
            scope = _scope_defaults(Scope, document[name])
            if type(scope.get("item")) is dict:
                scope["item"] = _scope_defaults(ItemKey, scope["item"])
            document[name] = scope
    request = _decode(json.dumps(document), model)
    if document.get("command_id") != str(request.command_id) or document.get(
        "grant_id"
    ) != str(request.grant_id):
        raise ValueError("Expected canonical scope request identifiers")
    return request


def _uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a UUID") from None


def _print_status(
    args: argparse.Namespace, command_id: UUID, status: str, reason: str | None = None
) -> None:
    if args.json:
        result = {"command_id": str(command_id), "status": status}
        if reason is not None:
            result["reason"] = reason
        print(json.dumps(result))
    else:
        suffix = "" if reason is None else f" {reason}"
        print(f"{command_id} {status}{suffix}")


def _enqueue_command(args: argparse.Namespace) -> int:
    command_id = args.request_id or uuid4()
    try:
        command = ControlCommand(command_id, args.payload_factory(args))
    except (OSError, LedgerError, RecursionError, ValueError):
        _print_status(args, command_id, "invalid-config")
        return 1
    try:
        receipt = ControlInbox(monitor_registry.default_monitor_root()).enqueue(command)
    except ConflictError:
        _print_status(args, command_id, "command-conflict")
        return 1
    except ValueError:
        _print_status(args, command_id, "invalid-config")
        return 1
    except LedgerError:
        _print_status(args, command_id, "state-invalid")
        return 1
    _print_status(args, command_id, receipt.status.value)
    return 0


def _enqueue_scope(args: argparse.Namespace) -> int:
    try:
        request = _scope_config(args.request, args.scope_request)
    except (OSError, LedgerError, RecursionError, ValueError):
        print(json.dumps({"status": "unavailable"}) if args.json else "unavailable")
        return 1
    try:
        queued = ControlInbox(monitor_registry.default_monitor_root()).enqueue_scope(
            request
        )
    except (OSError, LedgerError, RecursionError, sqlite3.Error, ValueError):
        queued = False
    _print_status(args, request.command_id, "queued" if queued else "unavailable")
    return 0 if queued else 1


def _command_status(args: argparse.Namespace) -> int:
    try:
        receipt = ControlInbox(monitor_registry.default_monitor_root()).status(
            args.command_id
        )
    except LedgerError:
        _print_status(args, args.command_id, "state-invalid")
        return 1
    if receipt is None:
        _print_status(args, args.command_id, "unavailable")
        return 1
    reason = receipt.reason if receipt.status is ControlStatus.QUEUED else None
    _print_status(args, args.command_id, receipt.status.value, reason)
    return 0


def _submission(
    parser: argparse.ArgumentParser,
    factory: Callable[[argparse.Namespace], ControlPayload],
    *,
    config: bool = False,
) -> None:
    if config:
        parser.add_argument("--config", type=Path, required=True, metavar="FILE")
    parser.add_argument("--request-id", type=_uuid, metavar="UUID")
    parser.add_argument("--json", action="store_true")
    parser.set_defaults(handler=_enqueue_command, payload_factory=factory)


def configure_monitor_commands(monitor_subparsers: argparse._SubParsersAction) -> None:
    """Register owner submissions and the lease-free status query."""
    project = monitor_subparsers.add_parser("project").add_subparsers(required=True)
    _submission(
        project.add_parser("register"),
        lambda args: _owner_config(
            args.config,
            ProjectRegistrationRequest,
            remote=None,
            anchors=[],
            default_driver=None,
        ),
        config=True,
    )
    anchor = (
        project.add_parser("anchor").add_subparsers(required=True).add_parser("add")
    )
    anchor.add_argument(
        "--project", dest="project_id", type=_uuid, required=True, metavar="UUID"
    )
    _submission(
        anchor,
        lambda args: AnchorRequest(
            args.project_id, _owner_config(args.config, _AnchorConfig).anchor
        ),
        config=True,
    )
    source = monitor_subparsers.add_parser("source").add_subparsers(required=True)
    _submission(
        source.add_parser("approve"),
        lambda args: _owner_config(args.config, SourceApprovalRequest),
        config=True,
    )
    capture = monitor_subparsers.add_parser("capture").add_subparsers(required=True)
    for action in ("enable", "disable"):
        toggle = capture.add_parser(action)
        toggle.add_argument(
            "--project", dest="project_id", type=_uuid, required=True, metavar="UUID"
        )
        toggle.add_argument(
            "--source", dest="source_id", type=_uuid, required=True, metavar="ID"
        )
        toggle.set_defaults(capture_enabled=action == "enable")
        _submission(
            toggle,
            lambda args: CaptureChange(
                args.project_id, args.source_id, args.capture_enabled
            ),
        )
    scope = monitor_subparsers.add_parser("scope").add_subparsers(required=True)
    for action, request in REQUEST_TYPES.items():
        proposal = scope.add_parser(action, allow_abbrev=False)
        proposal.add_argument("--request", type=Path, required=True, metavar="FILE")
        proposal.add_argument("--json", action="store_true")
        proposal.set_defaults(handler=_enqueue_scope, scope_request=request)
    command = monitor_subparsers.add_parser("command").add_subparsers(required=True)
    status = command.add_parser("status")
    status.add_argument(
        "--id", dest="command_id", type=_uuid, required=True, metavar="ID"
    )
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=_command_status)
