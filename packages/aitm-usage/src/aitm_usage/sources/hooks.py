"""Bounded, best-effort wake messages for the private local monitor."""

import errno
import json
import os
import select
import socket
import stat
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from time import monotonic

from .. import monitor_registry
from ..ledger import LedgerError, _pin_directory, _PinnedPath
from ..monitor_types import MonitorProvider
from ..types import SourceRef

_SOCKET = "wake.sock"
_ADDRESS_BYTES = 103
_FRAME_BYTES = 2048
_LOCATOR_BYTES = 1024
_SOCKET_SECONDS = 0.03
_PENDING = {errno.EINPROGRESS, errno.EALREADY, errno.EAGAIN, errno.EWOULDBLOCK}


class WakeKind(StrEnum):
    CHANGE = "change"
    STOP = "stop"
    PARK = "park"


class WakeDisposition(StrEnum):
    SENT = "sent"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class HookEvent:
    kind: WakeKind
    provider: MonitorProvider | None = None
    locator: str | None = None
    session: SourceRef | None = None


def _frame(event: HookEvent) -> bytes:
    if type(event) is not HookEvent or type(event.kind) is not WakeKind:
        raise ValueError("Invalid wake frame")
    data = {"v": 1, "kind": event.kind.value}
    if event.kind is WakeKind.PARK:
        if (
            type(event.session) is not SourceRef
            or event.provider is not None
            or event.locator is not None
        ):
            raise ValueError("Invalid park frame")
        data["session"] = event.session.value
    else:
        if (
            type(event.provider) is not MonitorProvider
            or type(event.locator) is not str
            or not event.locator
            or "\0" in event.locator
            or len(event.locator.encode("utf-8")) > _LOCATOR_BYTES
            or event.session is not None
        ):
            raise ValueError("Invalid wake locator")
        data.update(provider=event.provider.value, locator=event.locator)
    frame = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    encoded = frame.encode("ascii") + b"\n"
    if len(encoded) > _FRAME_BYTES:
        raise ValueError("Wake frame is too large")
    return encoded


def _parse_frame(raw: bytes) -> HookEvent:
    if len(raw) > _FRAME_BYTES or not raw.endswith(b"\n"):
        raise ValueError("Invalid wake frame")
    try:
        data = json.loads(raw.decode("utf-8"))
    except RecursionError:
        raise ValueError("Invalid wake frame") from None
    if type(data) is not dict or type(data.get("v")) is not int or data["v"] != 1:
        raise ValueError("Invalid wake frame")
    try:
        kind = WakeKind(data["kind"])
        event = (
            HookEvent(kind, session=SourceRef(data["session"]))
            if kind is WakeKind.PARK
            else HookEvent(kind, MonitorProvider(data["provider"]), data["locator"])
        )
        if _frame(event) != raw:
            raise ValueError("Wake frame is not canonical")
        return event
    except (KeyError, TypeError, ValueError):
        raise ValueError("Invalid wake frame") from None


def _endpoint(directory: _PinnedPath) -> str:
    address = str(directory.path / _SOCKET)
    if len(os.fsencode(address)) > _ADDRESS_BYTES:
        raise LedgerError("Private wake socket address is too long")
    return address


def _socket_entry(directory: _PinnedPath) -> os.stat_result:
    directory.check()
    info = os.stat(_SOCKET, dir_fd=directory.fd, follow_symlinks=False)
    if (
        not stat.S_ISSOCK(info.st_mode)
        or info.st_uid != os.geteuid()
        or not os.path.samestat(info, os.lstat(_endpoint(directory)))
    ):
        raise LedgerError("Private wake socket identity is unavailable")
    return info


def _read_frame(fd: int, deadline: float) -> bytes:
    data = bytearray()
    while (remaining := deadline - monotonic()) > 0:
        if not select.select([fd], [], [], remaining)[0]:
            break
        try:
            part = os.read(fd, _FRAME_BYTES + 1 - len(data))
        except BlockingIOError:
            continue
        if not part:
            return bytes(data)
        data.extend(part)
        if len(data) > _FRAME_BYTES:
            raise ValueError("Wake frame is too large")
    raise ValueError("Wake frame deadline expired")


class HookSender:
    """Send a bounded wake without waiting for processing or provider output."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = monitor_registry.default_monitor_root() if root is None else root

    def notify(self, event: HookEvent) -> WakeDisposition:
        try:
            data = _frame(event)
            with (
                _pin_directory(self._root) as directory,
                socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection,
            ):
                info = _socket_entry(directory)
                if stat.S_IMODE(info.st_mode) != 0o600:
                    return WakeDisposition.UNAVAILABLE
                deadline = monotonic() + _SOCKET_SECONDS
                connection.setblocking(False)
                result = connection.connect_ex(_endpoint(directory))
                if result in _PENDING:
                    if not self._writable(connection, deadline):
                        return WakeDisposition.UNAVAILABLE
                    result = connection.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if result or not os.path.samestat(info, _socket_entry(directory)):
                    return WakeDisposition.UNAVAILABLE
                pending = memoryview(data)
                while pending:
                    if not self._writable(connection, deadline):
                        return WakeDisposition.UNAVAILABLE
                    try:
                        sent = connection.send(pending)
                    except BlockingIOError:
                        continue
                    if sent == 0:
                        return WakeDisposition.UNAVAILABLE
                    pending = pending[sent:]
                if monotonic() > deadline:
                    return WakeDisposition.UNAVAILABLE
                connection.shutdown(socket.SHUT_WR)
                return WakeDisposition.SENT
        except (LedgerError, OSError, ValueError):
            return WakeDisposition.UNAVAILABLE

    @staticmethod
    def _writable(connection: socket.socket, deadline: float) -> bool:
        remaining = deadline - monotonic()
        return remaining > 0 and bool(select.select([], [connection], [], remaining)[1])


def main() -> int:
    try:
        event = _parse_frame(
            _read_frame(sys.stdin.fileno(), monotonic() + _SOCKET_SECONDS)
        )
    except (OSError, ValueError):
        return 0
    HookSender().notify(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
