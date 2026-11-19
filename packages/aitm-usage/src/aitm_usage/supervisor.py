"""Own the installed service child across lifecycle commands."""

import fcntl
import os
import plistlib
import pwd
import re
import signal
import socket
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from secrets import token_hex
from tempfile import TemporaryDirectory

from .ledger import (
    LedgerError,
    WriterActive,
    _check_acl,
    _ensure_private_directory,
    _guard_path,
    _lease,
    _path_exists,
    _pin_directory,
    _PinnedPath,
    _validated_path,
)
from .monitor_control import _peer_uid
from .scopes import _publish, _read_private
from .types import _decode, _encode

_STOP_WAIT = 8
_INTERVAL = 0.1
_ENVIRONMENT = {"LC_ALL": "C", "PATH": "/usr/bin:/bin"}
_OWNER_ENTRY = """
import sys
sys.path.insert(0, sys.argv.pop(1))
from aitm_usage.supervisor import _own_child
_own_child(sys.argv[1], sys.argv[2], int(sys.argv[3]))
"""


class InstallError(LedgerError):
    """A sanitized lifecycle failure suitable for a CLI status."""

    def __init__(self, message: str, *, status: str | None = None):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True, slots=True)
class ServiceJob:
    label: str
    plist: Path
    program: Path
    arguments: tuple[str, ...]
    pid: int | None


@dataclass(frozen=True, slots=True)
class ManagedProcess:
    pid: int
    started: datetime
    executable: Path


@dataclass(frozen=True, slots=True)
class _Launch:
    incarnation: str
    arguments: tuple[str, ...]
    interpreter: str
    endpoint: str | None = None
    pid: int | None = None
    started: datetime | None = None

    @classmethod
    def read(cls, directory: _PinnedPath, label: str) -> "_Launch | None":
        raw = _read_private(directory, f"{label}.pid.json")
        if raw is None:
            return None
        try:
            record = _decode(raw, cls)
            if (
                _encode(record, cls).encode() != raw
                or not re.fullmatch(r"[0-9a-f]{32}", record.incarnation)
                or len(record.arguments) != 5
                or not Path(record.arguments[0]).is_absolute()
                or not Path(record.interpreter).is_absolute()
                or (record.pid is None) != (record.started is None)
                or record.pid is not None
                and record.pid <= 1
            ):
                raise ValueError
        except (TypeError, ValueError, RecursionError):
            raise InstallError("Invalid private service PID record") from None
        return record

    def publish(self, directory: _PinnedPath, label: str, *, replace_pending=False):
        if not _publish(
            directory,
            f"{label}.pid.json",
            _encode(self, type(self)).encode(),
            replace_pending=replace_pending,
        ):
            raise InstallError("A service PID record already exists")


def _owner_lease(directory: Path, label: str) -> Path:
    return directory / f"{label}.owner.lock"


def _remove(directory: _PinnedPath, name: str) -> None:
    directory.check()
    try:
        os.unlink(name, dir_fd=directory.fd)
    except FileNotFoundError:
        return
    os.fsync(directory.fd)


class ServiceSupervisor:
    """Operate one project's child through its private lifetime lease and mailbox."""

    activation_timeout = 120

    def __init__(self, ledger):
        self.label = f"org.aitm.usage.{ledger.identity.project_id}"
        self.plist_directory = (
            _guard_path(ledger.root, ledger.identity.project_id).parent / "services"
        )

    def _legacy_registration(self) -> Path | None:
        if sys.platform == "darwin":
            try:
                home = Path(pwd.getpwuid(os.geteuid()).pw_dir)
            except (KeyError, OSError):
                raise InstallError(
                    "Cannot locate the legacy LaunchAgent registration"
                ) from None
            if not home.is_absolute():
                raise InstallError("Cannot locate the legacy LaunchAgent registration")
            return home / "Library" / "LaunchAgents" / f"{self.label}.plist"
        return None

    def _check_label(self, label: str) -> None:
        if label != self.label:
            raise InstallError("Service label does not match the project")
        legacy = self._legacy_registration()
        if legacy is not None and _path_exists(legacy):
            raise InstallError(
                "Unload and retire the legacy LaunchAgent before using the supervisor",
                status="legacy-launchagent",
            )

    def _record(self, label: str) -> _Launch | None:
        self._check_label(label)
        if not _path_exists(self.plist_directory):
            return None
        lease = _owner_lease(self.plist_directory, label)
        with _pin_directory(self.plist_directory) as directory:
            if not _path_exists(lease):
                if _Launch.read(directory, label) is None:
                    return None
            else:
                for attempt in range(4):
                    try:
                        with _lease(lease):
                            if _Launch.read(directory, label) is None:
                                return None
                        break
                    except WriterActive:
                        try:
                            record = _Launch.read(directory, label)
                        except InstallError:
                            raise
                        except (LedgerError, OSError):
                            if attempt == 3:
                                raise
                        else:
                            if record is not None:
                                return record
                            if attempt == 3:
                                raise InstallError(
                                    "Service owner has no PID record"
                                ) from None
                        # The owner may be publishing a new inode or releasing the lease.
                        time.sleep(_INTERVAL)
        raise InstallError("Service PID record is stale", status="recovery-required")

    def job(self, label: str) -> ServiceJob | None:
        record = self._record(label)
        if record is None:
            return None
        return ServiceJob(
            label,
            self.plist_directory / f"{label}.plist",
            Path(record.arguments[0]),
            record.arguments,
            record.pid,
        )

    def process(self, pid: int) -> ManagedProcess | None:
        record = self._record(self.label)
        if (
            record is None
            or record.pid != pid
            or record.started is None
            or record.endpoint is None
            or not _confirms_live_child(record)
        ):
            return None
        return ManagedProcess(pid, record.started, Path(record.interpreter))

    def is_disabled(self, label: str) -> bool:
        self._check_label(label)
        if not _path_exists(self.plist_directory):
            return False
        with _pin_directory(self.plist_directory) as directory:
            return _read_private(directory, f"{label}.disabled") is not None

    def disable(self, label: str) -> None:
        self._check_label(label)
        _ensure_private_directory(self.plist_directory)
        with _pin_directory(self.plist_directory) as directory:
            _publish(directory, f"{label}.disabled", b"disabled\n")

    def enable(self, label: str) -> None:
        self._check_label(label)
        with _pin_directory(self.plist_directory) as directory:
            _remove(directory, f"{label}.disabled")

    def bootstrap(self, registration: Path, interpreter: Path) -> None:
        label = self.label
        self._check_label(label)
        if registration != self.plist_directory / f"{label}.plist":
            raise InstallError("Unexpected service registration path")
        with (
            _pin_directory(self.plist_directory) as directory,
            _lease(_owner_lease(directory.path, label), create=True) as lease,
        ):
            raw = _read_private(directory, registration.name)
            if raw is None or _read_private(directory, f"{label}.disabled") is not None:
                raise InstallError("Service registration is absent or disabled")
            if _Launch.read(directory, label) is not None:
                raise InstallError(
                    "Service PID record is stale", status="recovery-required"
                )
            value = plistlib.loads(raw)
            record = _Launch(
                token_hex(16), tuple(value["ProgramArguments"]), str(interpreter)
            )
            record.publish(directory, label)
            try:
                subprocess.Popen(
                    [
                        sys.executable,
                        "-I",
                        "-c",
                        _OWNER_ENTRY,
                        str(Path(__file__).resolve().parents[1]),
                        str(directory.path),
                        label,
                        str(lease.fd),
                    ],
                    env=_ENVIRONMENT,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    pass_fds=(lease.fd,),
                )
            except OSError:
                _remove(directory, f"{label}.pid.json")
                raise

    def bootout(self, label: str) -> None:
        record = self._record(label)
        if record is None:
            return
        with _pin_directory(self.plist_directory) as directory:
            _publish(
                directory,
                f"{label}.stop",
                record.incarnation.encode(),
                replace_pending=True,
            )
            deadline = time.monotonic() + _STOP_WAIT
            while True:
                try:
                    with _lease(_owner_lease(directory.path, label)):
                        if _Launch.read(directory, label) is None:
                            return
                        raise InstallError(
                            "Service owner vanished before reaping its child"
                        )
                except WriterActive:
                    if time.monotonic() >= deadline:
                        raise InstallError(
                            "Service owner did not confirm shutdown"
                        ) from None
                    time.sleep(_INTERVAL)


def _confirms_live_child(record: _Launch) -> bool:
    assert record.endpoint is not None
    endpoint = Path(record.endpoint)
    try:
        with (
            _pin_directory(endpoint.parent) as directory,
            socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection,
        ):
            expected = endpoint.lstat()
            if (
                not stat.S_ISSOCK(expected.st_mode)
                or stat.S_IMODE(expected.st_mode) != 0o600
                or expected.st_uid != os.geteuid()
            ):
                return False
            _check_acl(endpoint)
            connection.settimeout(1)
            connection.connect(str(endpoint))
            if _peer_uid(connection) != os.geteuid():
                return False
            payload = _encode(record, _Launch).encode()
            with connection.makefile("rb") as response:
                observed = response.read(len(payload) + 1)
            directory.check()
            return observed == payload and os.path.samestat(expected, endpoint.lstat())
    except (LedgerError, OSError):
        return False


def _respond(server: socket.socket, child, running: _Launch | None) -> None:
    try:
        connection, _ = server.accept()
    except TimeoutError:
        return
    with connection:
        try:
            connection.settimeout(_INTERVAL)
            if _peer_uid(connection) == os.geteuid() and child is not None:
                if child.poll() is None and running is not None:
                    connection.sendall(_encode(running, _Launch).encode())
        except (LedgerError, OSError):
            pass


def _own_child(path: str, label: str, lease_fd: int) -> None:
    directory_path = Path(path)
    lease_path = _owner_lease(directory_path, label)
    lease = _PinnedPath(
        lease_path, lease_fd, False, _validated_path(lease_path, directory=False)
    )
    lease.check()
    fcntl.flock(lease_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.set_inheritable(lease_fd, False)
    with _pin_directory(directory_path) as directory:
        record = _Launch.read(directory, label)
        if record is None or record.pid is not None:
            raise InstallError("Missing service launch reservation")
        name = f"{label}.plist"
        registration = _read_private(directory, name)
        if (
            registration is None
            or tuple(plistlib.loads(registration)["ProgramArguments"])
            != record.arguments
        ):
            raise InstallError("Service registration changed during startup")
        stop_name = f"{label}.stop"
        stop_token = record.incarnation.encode()
        stopping = False

        def request_shutdown(_signal, _frame):
            nonlocal stopping
            stopping = True

        signal.signal(signal.SIGTERM, request_shutdown)
        signal.signal(signal.SIGINT, request_shutdown)
        child = None
        running = None
        try:
            with (
                TemporaryDirectory(
                    prefix="aitm-owner-", dir=Path("/tmp").resolve()
                ) as scratch,
                socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server,
            ):
                endpoint = Path(scratch, "owner")
                server.bind(str(endpoint))
                endpoint.chmod(0o600)
                server.listen(4)
                server.settimeout(_INTERVAL)
                record = replace(record, endpoint=str(endpoint))
                while (
                    not stopping and _read_private(directory, stop_name) != stop_token
                ):
                    lease.check()
                    if child is not None and child.poll() is not None:
                        child = None
                        running = None
                        record.publish(directory, label, replace_pending=True)
                        time.sleep(0.4)
                        continue
                    if (
                        child is None
                        and _read_private(directory, f"{label}.disabled") is None
                    ):
                        if _read_private(directory, name) != registration:
                            raise InstallError(
                                "Service registration changed before restart"
                            )
                        started = datetime.now(UTC)
                        child = subprocess.Popen(
                            record.arguments, env=_ENVIRONMENT, stdin=subprocess.DEVNULL
                        )
                        running = replace(record, pid=child.pid, started=started)
                        running.publish(directory, label, replace_pending=True)
                    _respond(server, child, running)
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            lease.check()
            current = _Launch.read(directory, label)
            if current is None or current.incarnation != record.incarnation:
                raise InstallError("Service PID record changed before retirement")
            _remove(directory, stop_name)
            _remove(directory, f"{label}.pid.json")
