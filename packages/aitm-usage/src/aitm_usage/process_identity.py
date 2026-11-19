"""Native process observations for the externally started Grok scope hook."""

import ctypes
import os
import stat
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cache
from pathlib import Path
from uuid import UUID

_PROC = Path("/proc")
_NAMESPACES = ("ns/pid", "ns/time")
_READ_ERRORS = (AttributeError, OSError, ValueError, OverflowError, RuntimeError)


@dataclass(frozen=True, slots=True)
class ProcessIdentity:
    pid: int
    started: datetime
    executable: Path


class _BSDProcessInfo(ctypes.Structure):
    # Darwin sys/proc_info.h, PROC_PIDTBSDINFO.
    _fields_ = [
        ("flags", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("xstatus", ctypes.c_uint32),
        ("pid", ctypes.c_uint32),
        ("parent_pid", ctypes.c_uint32),
        ("uid", ctypes.c_uint32),
        ("credentials", ctypes.c_uint32 * 6),
        ("command", ctypes.c_char * 16),
        ("name", ctypes.c_char * 32),
        ("terminal_and_priority", ctypes.c_uint32 * 6),
        ("start_seconds", ctypes.c_uint64),
        ("start_microseconds", ctypes.c_uint64),
    ]


@cache
def _libproc() -> ctypes.CDLL:
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    library.proc_pidinfo.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    library.proc_pidinfo.restype = ctypes.c_int
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    return library


def _darwin_hop(pid: int) -> tuple[int, datetime] | None:
    info = _BSDProcessInfo()
    size = ctypes.sizeof(info)
    if (
        _libproc().proc_pidinfo(pid, 3, 0, ctypes.byref(info), size) != size
        or info.pid != pid
        or info.uid != os.geteuid()
        or info.status == 5  # SZOMB
        or not info.start_seconds
        or info.start_microseconds >= 1_000_000
    ):
        return None
    return info.parent_pid, datetime.fromtimestamp(info.start_seconds, UTC).replace(
        microsecond=info.start_microseconds
    )


def _darwin_executable(
    pid: int,
) -> tuple[bytes, Path, tuple[int, int, int, int]] | None:
    buffer = ctypes.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
    length = _libproc().proc_pidpath(pid, buffer, len(buffer))
    raw = buffer.value
    if length != len(raw) or not 0 < length < len(buffer) - 1:
        return None
    path = Path(os.fsdecode(raw))
    if not path.is_absolute():
        return None
    resolved = path.resolve(strict=True)
    info = resolved.stat(follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode):
        return None
    return raw, resolved, (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def _linux_context() -> tuple[str, str]:
    return tuple(os.readlink(_PROC / "self" / name) for name in _NAMESPACES)


def process_reference_domain() -> str:
    """Scope Linux PIDs and boot-relative clock ticks to their originating host."""
    if sys.platform != "linux":
        return ""
    boot = UUID((_PROC / "sys/kernel/random/boot_id").read_text().strip())
    pid_namespace, time_namespace = _linux_context()
    return f"linux:{boot}:{pid_namespace}:{time_namespace}:"


def _read_proc(fd: int, name: str) -> bytes:
    with os.fdopen(
        os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd), "rb"
    ) as entry:
        return entry.read()


def _linux_hop(fd: int, pid: int) -> tuple[int, int] | None:
    if tuple(os.readlink(name, dir_fd=fd) for name in _NAMESPACES) != _linux_context():
        return None
    # comm is parenthesized and can contain spaces, newlines and closing parens.
    prefix, closing, tail = _read_proc(fd, "stat").rpartition(b")")
    fields = tail.split()
    if (
        not closing
        or not prefix.startswith(f"{pid} (".encode())
        or len(fields) < 20
        or fields[0] in (b"Z", b"X", b"x")
    ):
        return None
    uid = next(
        (
            line.split()[1:]
            for line in _read_proc(fd, "status").splitlines()
            if line.startswith(b"Uid:")
        ),
        (),
    )
    if len(uid) != 4 or int(uid[1]) != os.geteuid():
        return None
    # fields begins with state (field 3), followed by ppid (4) and starttime (22).
    parent, ticks = int(fields[1]), int(fields[19])
    return (parent, ticks) if parent >= 0 and ticks > 0 else None


def _linux_started(ticks: int) -> datetime:
    hz = os.sysconf("SC_CLK_TCK")
    with (_PROC / "stat").open("rb") as boot_stat:
        for line in boot_stat:
            if line.startswith(b"btime "):
                epoch = int(line.split()[1])
                seconds, fraction = divmod(ticks, hz)
                return datetime.fromtimestamp(epoch + seconds, UTC) + timedelta(
                    microseconds=fraction * 1_000_000 // hz
                )
    raise ValueError("Linux process boot time unavailable")


def _linux_executable(fd: int) -> tuple[Path, tuple[int, int, int, int]] | None:
    path = Path(os.readlink("exe", dir_fd=fd))
    if not path.is_absolute():
        return None
    path = path.resolve(strict=True)
    info = os.stat("exe", dir_fd=fd)
    if not os.path.samestat(info, path.stat()):
        return None
    return path, (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def _linux_observation(
    pid: int, *, include_image: bool
) -> tuple[int, datetime, Path | None] | None:
    if os.readlink(_PROC / "self") != str(os.getpid()):
        return None  # /proc must use the caller's PID namespace.
    # The descriptor keeps these reads on one proc entry even if the PID is reused.
    fd = os.open(_PROC / str(pid), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        before = _linux_hop(fd, pid)
        if before is None:
            return None
        image = _linux_executable(fd) if include_image else None
        started = _linux_started(before[1])
        if include_image and (image is None or _linux_executable(fd) != image):
            return None
        if _linux_hop(fd, pid) == before:
            return before[0], started, image[0] if image is not None else None
        return None
    finally:
        os.close(fd)


def read_process_hop(pid: int) -> tuple[int, datetime] | None:
    """Read a same-user parent PID and birth time."""
    if type(pid) is not int or not 1 < pid < 2**31:
        return None
    try:
        if sys.platform == "darwin":
            return _darwin_hop(pid)
        if sys.platform == "linux":
            observed = _linux_observation(pid, include_image=False)
            if observed is not None:
                return observed[0], observed[1]
    except _READ_ERRORS:
        pass
    return None


def read_process_identity(pid: int) -> ProcessIdentity | None:
    """Observe a same-user process and its executable without crossing incarnations."""
    if type(pid) is not int or not 1 < pid < 2**31:
        return None
    try:
        if sys.platform == "darwin":
            before = _darwin_hop(pid)
            image = _darwin_executable(pid) if before is not None else None
            if (
                before is not None
                and image is not None
                and _darwin_executable(pid) == image
                and _darwin_hop(pid) == before
            ):
                return ProcessIdentity(pid, before[1], image[1])
        if sys.platform == "linux":
            observed = _linux_observation(pid, include_image=True)
            if observed is not None and observed[2] is not None:
                return ProcessIdentity(pid, observed[1], observed[2])
    except _READ_ERRORS:
        pass
    return None
