"""Dormant native metadata watch hints for explicitly admitted roots."""

import ctypes as ct
import errno
import os
import platform
import select
import struct
from collections.abc import Callable
from contextlib import ExitStack, suppress
from ctypes.util import find_library
from dataclasses import dataclass, field
from enum import StrEnum
from math import ceil, isfinite
from pathlib import Path
from threading import Condition, Event, Lock, Thread
from time import monotonic

from .sources.scan import _directory
from .types import SourceRef

_DARWIN_RECHECK = 0x20 | 0x40 | 0x80
_DARWIN_RESCAN = 0x01 | 0x02 | 0x04 | 0x08
_DARWIN_KNOWN_FLAGS = 0x00FFFFFF
_DARWIN_WATCH_ROOT = 0x04
_DARWIN_FILE_EVENTS = 0x10
_LINUX_STRUCT = struct.Struct("=iIII")
_LINUX_OVERFLOW = 0x00004000
_LINUX_ROOT_FLAGS = 0x00000400 | 0x00000800 | 0x00002000 | 0x00008000
_LINUX_DIRECTORY = 0x40000000
_LINUX_ENROLL = 0x80 | 0x100
_LINUX_RETIRE = 0x40 | 0x200
_LINUX_ONLYDIR = 0x01000000
_LINUX_MASK = (
    _LINUX_ONLYDIR
    | _LINUX_ROOT_FLAGS
    | _LINUX_ENROLL
    | _LINUX_RETIRE
    | 0x02
    | 0x04
    | 0x08
)
_MAX_ROOTS = 32
_MAX_WAIT = 30
_START_TIMEOUT = 2
_CLOSE_TIMEOUT = 2


class WatchError(RuntimeError):
    """The watcher could not prove its startup or resource custody."""


class WatchKind(StrEnum):
    CHANGED = "changed"
    RECONCILE = "reconcile"
    ROOT_LOST = "root-lost"
    ROOT_REPLACED = "root-replaced"


@dataclass(frozen=True, slots=True)
class WatchRoot:
    key: SourceRef
    path: Path = field(repr=False)
    identity: tuple[int, int]

    def __post_init__(self) -> None:
        if (
            type(self.key) is not SourceRef
            or not isinstance(self.path, Path)
            or not self.path.is_absolute()
            or ".." in self.path.parts
            or "\0" in str(self.path)
            or type(self.identity) is not tuple
            or len(self.identity) != 2
            or not all(type(part) is int and part >= 0 for part in self.identity)
        ):
            raise WatchError("Invalid authorized watch root")


@dataclass(frozen=True, slots=True)
class WatchEvent:
    key: SourceRef
    kind: WatchKind
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class _Root:
    root: WatchRoot
    chain: tuple[tuple[int, int, int], ...]

    def check(self) -> WatchKind | None:
        try:
            with _directory(self.root.path) as (_, chain, __):
                if chain != self.chain:
                    return WatchKind.ROOT_REPLACED
        except OSError as error:
            if error.errno in (errno.ELOOP, errno.ENOTDIR):
                return WatchKind.ROOT_REPLACED
            return WatchKind.ROOT_LOST
        return None


def _accepted_roots(roots: tuple[WatchRoot, ...]) -> dict[SourceRef, _Root]:
    if type(roots) is not tuple or not 0 < len(roots) <= _MAX_ROOTS:
        raise WatchError("Expected bounded authorized watch roots")
    result = {}
    physical = set()
    for root in roots:
        if (
            type(root) is not WatchRoot
            or root.key in result
            or root.identity in physical
        ):
            raise WatchError("Duplicate or invalid authorized watch root")
        try:
            with _directory(root.path) as (_, chain, __):
                if chain[-1][:2] != root.identity:
                    raise WatchError("Authorized watch root identity changed")
                result[root.key] = _Root(root, chain)
        except OSError:
            raise WatchError("Authorized watch root is unavailable") from None
        physical.add(root.identity)
    return result


def _bind(library, name, result, *arguments):
    function = getattr(library, name)
    function.argtypes = arguments
    function.restype = result
    return function


def _native_error() -> OSError:
    return OSError(ct.get_errno(), "Native watcher is unavailable")


class _Linux:
    def __init__(
        self,
        roots: dict[SourceRef, _Root],
        per_root: int,
        directory_limit: int,
        entry_limit: int,
    ) -> None:
        self.roots = roots
        self.per_root = per_root
        self.directory_limit = directory_limit
        self.entry_limit = entry_limit
        self.fallback: set[SourceRef] = set()
        self.watches: dict[int, dict[SourceRef, tuple[int, int, int]]] = {}
        self.identities: set[tuple[int, int, int]] = set()
        self.fd = -1
        try:
            library = ct.CDLL(None, use_errno=True)
            self._init = _bind(library, "inotify_init1", ct.c_int, ct.c_int)
            self._add = _bind(
                library,
                "inotify_add_watch",
                ct.c_int,
                ct.c_int,
                ct.c_char_p,
                ct.c_uint32,
            )
            self._remove = _bind(
                library, "inotify_rm_watch", ct.c_int, ct.c_int, ct.c_int
            )
        except (AttributeError, OSError):
            self.fallback.update(roots)
        else:
            try:
                self.rebuild()
            except BaseException:
                self.close()
                raise

    def _new_fd(self) -> None:
        fd = self._init(os.O_NONBLOCK | os.O_CLOEXEC)
        if fd < 0:
            raise _native_error()
        self.fd = fd

    def close(self) -> None:
        if self.fd >= 0:
            fd, self.fd = self.fd, -1
            os.close(fd)
        self.watches.clear()
        self.identities.clear()

    def drop(self, key: SourceRef) -> None:
        self.fallback.discard(key)
        for watch, members in tuple(self.watches.items()):
            identity = members.pop(key, None)
            if identity is None or members:
                continue
            del self.watches[watch]
            self.identities.discard(identity)
            if self._remove(self.fd, watch) < 0 and ct.get_errno() != errno.EINVAL:
                self.close()
                self.fallback.update(self.roots)
                return

    def rebuild(self) -> None:
        self.close()
        try:
            self._new_fd()
        except OSError:
            self.fallback.update(self.roots)
            return
        deadline = monotonic() + _START_TIMEOUT
        for key in self.roots:
            if monotonic() >= deadline:
                self.fallback.add(key)
            elif key not in self.fallback:
                self.enroll(key, deadline=deadline)

    def enroll(self, key: SourceRef, *, deadline: float | None = None) -> None:
        self.drop(key)
        root = self.roots[key]
        pending = [root.root.path]
        walked = entries = 0
        slice_deadline = monotonic() + 0.5
        deadline = slice_deadline if deadline is None else min(deadline, slice_deadline)
        if self.fd < 0:
            self.fallback.add(key)
            return
        try:
            while pending:
                path = pending.pop()
                walked += 1
                if walked > self.per_root or monotonic() >= deadline:
                    raise WatchError("Watch directory bound exceeded")
                with _directory(path) as (fd, chain, _):
                    if chain[: len(root.chain)] != root.chain:
                        raise WatchError("Watch directory moved")
                    identity = chain[-1]
                    if (
                        identity not in self.identities
                        and len(self.watches) >= self.directory_limit
                    ):
                        raise WatchError("Watch descriptor bound exceeded")
                    watch = self._add(
                        self.fd, os.fsencode(f"/proc/self/fd/{fd}"), _LINUX_MASK
                    )
                    if watch < 0:
                        raise _native_error()
                    self.watches.setdefault(watch, {})[key] = identity
                    self.identities.add(identity)
                    with _directory(path) as (_, current, __):
                        if chain != current:
                            raise WatchError("Watch directory moved during enrollment")
                    with os.scandir(fd) as children:
                        for child in children:
                            entries += 1
                            if entries > self.entry_limit or monotonic() >= deadline:
                                raise WatchError("Watch metadata scan bound exceeded")
                            if child.is_dir(follow_symlinks=False):
                                if len(pending) + walked >= self.per_root:
                                    raise WatchError("Watch directory bound exceeded")
                                pending.append(path / child.name)
        except (OSError, WatchError):
            self.drop(key)
            self.fallback.add(key)

    def read(self) -> tuple[tuple[int, int], ...]:
        try:
            data = os.read(self.fd, 65536)
        except BlockingIOError:
            return ()
        if not data:
            return ((-1, _LINUX_OVERFLOW),)
        offset = 0
        results = []
        while offset < len(data):
            if len(data) - offset < _LINUX_STRUCT.size:
                return ((-1, _LINUX_OVERFLOW),)
            watch, mask, _, length = _LINUX_STRUCT.unpack_from(data, offset)
            offset += _LINUX_STRUCT.size + length
            if offset > len(data) or mask & _LINUX_OVERFLOW:
                return ((-1, _LINUX_OVERFLOW),)
            results.append((watch, mask))
        return tuple(results)


_CALLBACK = ct.CFUNCTYPE(
    None,
    ct.c_void_p,
    ct.c_void_p,
    ct.c_size_t,
    ct.POINTER(ct.c_char_p),
    ct.POINTER(ct.c_uint32),
    ct.POINTER(ct.c_uint64),
)


class _Darwin:
    def __init__(
        self,
        roots: dict[SourceRef, _Root],
        receive: Callable[[SourceRef, int], None],
    ) -> None:
        self.roots = roots
        self.receive = receive
        self.stop = Event()
        self.ready = Event()
        self.started = False
        self._ownership = Lock()
        self._loop = None
        self._retired: set[SourceRef] = set()
        self._callbacks = []
        foundation = find_library("CoreFoundation")
        services = find_library("CoreServices")
        if not foundation or not services:
            raise OSError("FSEvents runtime is unavailable")
        cf, fs = ct.CDLL(foundation), ct.CDLL(services)
        ptr = ct.c_void_p
        self._get_loop = _bind(cf, "CFRunLoopGetCurrent", ptr)
        self._wake = _bind(cf, "CFRunLoopWakeUp", None, ptr)
        self._run = _bind(
            cf, "CFRunLoopRunInMode", ct.c_int32, ptr, ct.c_double, ct.c_bool
        )
        self._retain = _bind(cf, "CFRetain", ptr, ptr)
        self._release = _bind(cf, "CFRelease", None, ptr)
        self._string = _bind(
            cf, "CFStringCreateWithCString", ptr, ptr, ct.c_char_p, ct.c_uint32
        )
        self._array = _bind(
            cf, "CFArrayCreate", ptr, ptr, ct.POINTER(ptr), ct.c_long, ptr
        )
        self._mode = ptr.in_dll(cf, "kCFRunLoopDefaultMode")
        self._create = _bind(
            fs,
            "FSEventStreamCreate",
            ptr,
            ptr,
            _CALLBACK,
            ptr,
            ptr,
            ct.c_uint64,
            ct.c_double,
            ct.c_uint32,
        )
        self._schedule = _bind(
            fs, "FSEventStreamScheduleWithRunLoop", None, ptr, ptr, ptr
        )
        self._start = _bind(fs, "FSEventStreamStart", ct.c_bool, ptr)
        self._stop_stream = _bind(fs, "FSEventStreamStop", None, ptr)
        self._invalidate = _bind(fs, "FSEventStreamInvalidate", None, ptr)
        self._release_stream = _bind(fs, "FSEventStreamRelease", None, ptr)
        self._thread = Thread(target=self._work, daemon=True, name="aitm-fsevents")
        self._thread.start()
        if not self.ready.wait(_START_TIMEOUT) or not self.started:
            self.close()
            raise WatchError("FSEvents did not start")

    def _notify(self) -> None:
        if self._loop is not None:
            self._wake(self._loop)

    def drop(self, key: SourceRef) -> None:
        with self._ownership:
            self._retired.add(key)
            self._notify()

    def close(self) -> None:
        self.stop.set()
        with self._ownership:
            self._notify()
        self._thread.join(_CLOSE_TIMEOUT)
        if self._thread.is_alive():
            raise WatchError("FSEvents owner did not retire")
        self._callbacks.clear()

    def alive(self) -> bool:
        return self._thread.is_alive()

    def _watch(self, root: _Root, loop, cleanup: ExitStack):
        key = root.root.key

        @_CALLBACK
        def callback(_stream, _info, count, _paths, flags, _ids):
            try:
                if count == 0:
                    return
                if not flags or count > 4096:
                    self.receive(key, _DARWIN_RESCAN)
                    return
                combined = 0
                for index in range(count):
                    combined |= flags[index]
                self.receive(key, combined)
            except Exception:
                # No exception may escape the native callback boundary.
                with suppress(Exception):
                    self.receive(key, _DARWIN_RESCAN)

        self._callbacks.append(callback)
        path = self._string(None, os.fsencode(root.root.path), 0x08000100)
        if not path:
            raise WatchError("FSEvents path creation failed")
        cleanup.callback(self._release, path)
        array = self._array(None, (ct.c_void_p * 1)(path), 1, None)
        if not array:
            raise WatchError("FSEvents path array creation failed")
        cleanup.callback(self._release, array)
        stream = self._create(
            None,
            callback,
            None,
            array,
            (1 << 64) - 1,
            0.05,
            _DARWIN_WATCH_ROOT | _DARWIN_FILE_EVENTS,
        )
        if not stream:
            raise WatchError("FSEvents stream creation failed")
        cleanup.callback(self._release_stream, stream)
        self._schedule(stream, loop, self._mode)
        cleanup.callback(self._invalidate, stream)
        if not self._start(stream):
            raise WatchError("FSEvents stream start failed")
        cleanup.callback(self._stop_stream, stream)

    def _work(self) -> None:
        owned: dict[SourceRef, ExitStack] = {}
        try:
            loop = self._get_loop()
            if not loop:
                return
            with self._ownership:
                self._loop = self._retain(loop)
            if not self._loop:
                return
            for key, root in self.roots.items():
                stack = owned[key] = ExitStack()
                self._watch(root, loop, stack)
                if root.check() is not None:
                    raise WatchError("FSEvents root changed during startup")
            self.started = True
            self.ready.set()
            while not self.stop.is_set():
                self._run(self._mode, 0.05, False)
                with self._ownership:
                    retired, self._retired = self._retired, set()
                for key in retired:
                    if stack := owned.pop(key, None):
                        stack.close()
        except (WatchError, OSError, ValueError):
            for key in self.roots:
                self.receive(key, _DARWIN_RESCAN)
        finally:
            for stack in owned.values():
                stack.close()
            with self._ownership:
                if self._loop:
                    self._release(self._loop)
                    self._loop = None
            self.ready.set()


class WatchSet:
    """Report transient watch hints. One consumer calls events at a time."""

    def __init__(
        self,
        roots: tuple[WatchRoot, ...],
        *,
        max_events: int = 256,
        max_directories_per_root: int = 1024,
        max_directories: int = 4096,
        max_scan_entries: int = 32768,
        fallback_interval: float = 1.0,
    ) -> None:
        limits = (
            (max_events, 256),
            (max_directories_per_root, 1024),
            (max_directories, 4096),
            (max_scan_entries, 32768),
        )
        if any(
            type(value) is not int or not 0 < value <= cap for value, cap in limits
        ) or (
            type(fallback_interval) not in (float, int)
            or not isfinite(fallback_interval)
            or not 0 < fallback_interval <= _MAX_WAIT
        ):
            raise WatchError("Invalid watch resource bounds")
        self._roots = _accepted_roots(roots)
        self._max_events = max_events
        self._fallback_interval = fallback_interval
        self._next_fallback = monotonic() + fallback_interval
        self._condition = Condition()
        self._consumer = Lock()
        self._shutdown = Lock()
        self._closing = Event()
        self._callback_pressure = Event()
        self._startup = tuple(
            WatchEvent(key, WatchKind.RECONCILE, "startup") for key in self._roots
        )
        self._hints: dict[SourceRef, WatchEvent] = {}
        self._priority: dict[SourceRef, WatchEvent] = {}
        self._lost: set[SourceRef] = set()
        self._fallback: set[SourceRef] = set()
        self._linux = None
        self._darwin = None
        self._wake_fds: tuple[int, int] | None = None
        system = platform.system()
        if system == "Linux":
            self._wake_fds = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
            try:
                self._linux = _Linux(
                    self._roots,
                    max_directories_per_root,
                    max_directories,
                    max_scan_entries,
                )
            except BaseException:
                self.close()
                raise
        elif system == "Darwin":
            try:
                self._darwin = _Darwin(self._roots.copy(), self._darwin_hint)
            except (AttributeError, OSError):
                self._fallback.update(self._roots)
        else:
            raise WatchError("Native watch platform is unsupported")

    def __enter__(self) -> "WatchSet":
        return self

    def __exit__(self, *_exception) -> None:
        self.close()

    def _enqueue(self, event: WatchEvent, *, callback: bool = False) -> None:
        key = event.key
        if not self._condition.acquire(blocking=not callback):
            self._callback_pressure.set()
            return
        try:
            if key in self._lost or self._closing.is_set():
                return
            if event.kind in (WatchKind.ROOT_LOST, WatchKind.ROOT_REPLACED):
                self._lost.add(key)
            if event.kind is not WatchKind.CHANGED:
                self._hints.pop(key, None)
                self._priority[key] = event
            elif key not in self._priority:
                if key in self._hints or len(self._hints) < self._max_events:
                    self._hints[key] = event
                else:
                    self._priority[key] = WatchEvent(
                        key, WatchKind.RECONCILE, "queue-bound"
                    )
            self._condition.notify_all()
        finally:
            self._condition.release()

    def _darwin_hint(self, key: SourceRef, flags: int) -> None:
        if flags & (_DARWIN_RECHECK | _DARWIN_RESCAN) or flags & ~_DARWIN_KNOWN_FLAGS:
            event = WatchEvent(key, WatchKind.RECONCILE, "native-rescan")
        else:
            event = WatchEvent(key, WatchKind.CHANGED)
        self._enqueue(event, callback=True)

    def _check(self) -> None:
        for key, root in tuple(self._roots.items()):
            if (status := root.check()) is None:
                continue
            self._startup = tuple(event for event in self._startup if event.key != key)
            self._enqueue(WatchEvent(key, status))
            del self._roots[key]
            if self._linux is not None:
                self._linux.drop(key)
            if self._darwin is not None:
                self._darwin.drop(key)
            self._fallback.discard(key)

    def _drain(self) -> tuple[WatchEvent, ...]:
        with self._condition:
            if self._callback_pressure.is_set():
                self._callback_pressure.clear()
                for key in self._roots:
                    self._priority.setdefault(
                        key, WatchEvent(key, WatchKind.RECONCILE, "callback-pressure")
                    )
                    self._hints.pop(key, None)
            result = (*self._startup, *self._priority.values(), *self._hints.values())
            self._startup = ()
            self._priority.clear()
            self._hints.clear()
            return result

    def _deadlines(self, deadline: float) -> float:
        if self._darwin is not None and not self._darwin.alive():
            self._fallback.update(self._roots)
        fallback = self._linux.fallback if self._linux is not None else self._fallback
        if not fallback:
            return deadline
        now = monotonic()
        if now >= self._next_fallback:
            for key in fallback:
                self._enqueue(WatchEvent(key, WatchKind.RECONCILE, "fallback"))
            self._next_fallback = now + self._fallback_interval
        return min(deadline, self._next_fallback)

    def _linux_wait(self, timeout: float) -> None:
        native = self._linux
        assert native is not None and self._wake_fds is not None
        waiter = select.poll()
        waiter.register(self._wake_fds[0], select.POLLIN)
        if native.fd >= 0:
            waiter.register(native.fd, select.POLLIN)
        ready = waiter.poll(ceil(timeout * 1000))
        if self._closing.is_set() or native.fd < 0:
            return
        if not any(fd == native.fd for fd, _ in ready):
            return
        try:
            changes = native.read()
        except OSError:
            changes = ((-1, _LINUX_OVERFLOW),)
        self._check()
        enroll = set()
        for watch, flags in changes:
            if flags & _LINUX_OVERFLOW:
                native.rebuild()
                for key in self._roots:
                    self._enqueue(WatchEvent(key, WatchKind.RECONCILE, "overflow"))
                return
            for key in native.watches.get(watch, ()):
                if (
                    flags & _LINUX_ROOT_FLAGS
                    or flags & _LINUX_DIRECTORY
                    and flags & (_LINUX_ENROLL | _LINUX_RETIRE)
                ):
                    enroll.add(key)
                else:
                    self._enqueue(WatchEvent(key, WatchKind.CHANGED))
        for key in enroll:
            native.enroll(key)
            self._enqueue(WatchEvent(key, WatchKind.RECONCILE, "enrollment"))

    def events(self, timeout: float) -> tuple[WatchEvent, ...]:
        if type(timeout) not in (float, int) or not isfinite(timeout) or timeout < 0:
            raise WatchError("Invalid watch wait")
        with self._consumer:
            if self._closing.is_set():
                return ()
            deadline = monotonic() + min(timeout, _MAX_WAIT)
            self._check()
            until = self._deadlines(deadline)
            if hints := self._drain():
                return hints
            delay = max(0.0, until - monotonic())
            if self._linux is not None:
                self._linux_wait(delay)
            else:
                with self._condition:
                    while not (
                        self._closing.is_set()
                        or self._priority
                        or self._hints
                        or self._callback_pressure.is_set()
                    ):
                        remaining = until - monotonic()
                        if remaining <= 0:
                            break
                        self._condition.wait(min(remaining, 0.1))
            if self._closing.is_set():
                return ()
            self._check()
            self._deadlines(deadline)
            return self._drain()

    def close(self) -> None:
        with self._shutdown:
            self._closing.set()
            with self._condition:
                self._condition.notify_all()
            if self._wake_fds is not None:
                with suppress(OSError):
                    os.write(self._wake_fds[1], b"\x00")
            with self._consumer:
                if self._linux is not None:
                    self._linux.close()
                if self._wake_fds is not None:
                    for fd in self._wake_fds:
                        os.close(fd)
                    self._wake_fds = None
                if self._darwin is not None:
                    self._darwin.close()
                    self._darwin = None
