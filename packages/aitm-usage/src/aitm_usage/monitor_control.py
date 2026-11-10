"""Private owner-command publication and enqueue-only monitor CLI handlers."""

import argparse
import json
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from . import monitor_registry
from .ledger import (
    ConflictError,
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
from .scopes import (
    INBOX_NAME,
    MAX_COMMAND_BYTES,
    _filename,
    _private_child,
    _publication,
    _publish,
    _read_private,
)
from .types import _decode, _encode, _positive, _unique_fields


def _command_bytes(command: ControlCommand) -> bytes:
    data = _encode(command, ControlCommand).encode("utf-8")
    if len(data) > MAX_COMMAND_BYTES:
        raise ValueError("Monitor command exceeds its size limit")
    return data


@dataclass(frozen=True, slots=True)
class _QueuedCommand:
    command: ControlCommand
    order: int

    def __post_init__(self) -> None:
        _positive(self.order)


@dataclass(frozen=True, slots=True)
class _LockedInbox:
    directory: _PinnedPath
    captured: dict[UUID, tuple[ControlCommand, bytes]] = field(default_factory=dict)


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


def _pending(inbox: _PinnedPath) -> dict[int, tuple[ControlCommand, bytes]]:
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

    def iter_pending(self, locked: _LockedInbox) -> Iterator[ControlCommand]:
        """Read exact envelopes in submission order under publication()."""
        inbox = locked.directory
        self._check_inbox(inbox)
        for _, (command, data) in sorted(_pending(inbox).items()):
            locked.captured[command.command_id] = command, data
            yield command

    def discard(self, locked: _LockedInbox, command: ControlCommand) -> None:
        """Retire only the exact command whose outcome is already durable."""
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

    def enqueue(self, command: ControlCommand) -> ControlReceipt:
        """Publish once, or return the recorded receipt for an exact retry."""
        data = _command_bytes(command)
        digest = command.payload_digest
        name = _filename(command.command_id)
        # Validate constructors on the decoded side as well as the encoded shape.
        if _decode(data, ControlCommand) != command:
            raise ValueError("Invalid monitor command")
        with self.publication() as locked:
            receipt = Registry(self.root).command_status(command.command_id)
            if receipt is not None:
                if receipt.payload_digest != digest:
                    raise ConflictError("Monitor command ID has conflicting bytes")
                return receipt

            inbox = locked.directory
            previous = _read_private(inbox, name)
            if previous is None:
                order = max(_pending(inbox), default=0) + 1
                publication = _encode(_QueuedCommand(command, order), _QueuedCommand)
                encoded = publication.encode("utf-8")
                if len(encoded) > MAX_COMMAND_BYTES:
                    raise ValueError("Monitor publication exceeds its size limit")
                if not _publish(inbox, name, encoded):
                    previous = _read_private(inbox, name)
                    if previous is None:
                        raise ConflictError("Private monitor publication changed")
            if previous is not None:
                queued = _decode_publication(name, previous)
                if _command_bytes(queued.command) != data:
                    raise ConflictError("Monitor command ID has conflicting bytes")
                # The prior publication may have reached rename before its sync failed.
                os.fsync(inbox.fd)
            return ControlReceipt(command.command_id, ControlStatus.QUEUED, digest)

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
                        receipt = ControlReceipt(
                            command_id, ControlStatus.QUEUED, command.payload_digest
                        )
                root.check()
                return receipt
        except OSError:
            raise LedgerError("Private monitor publication is unavailable") from None


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


def _owner_config[T](path: Path, model: type[T], **defaults: object) -> T:
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
    return _decode(json.dumps({**defaults, **data}), model)


def _uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a UUID") from None


def _print_status(args: argparse.Namespace, command_id: UUID, status: str) -> None:
    if args.json:
        print(json.dumps({"command_id": str(command_id), "status": status}))
    else:
        print(f"{command_id} {status}")


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
    _print_status(args, args.command_id, receipt.status.value)
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
    command = monitor_subparsers.add_parser("command").add_subparsers(required=True)
    status = command.add_parser("status")
    status.add_argument(
        "--id", dest="command_id", type=_uuid, required=True, metavar="ID"
    )
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=_command_status)
