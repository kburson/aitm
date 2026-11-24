"""Native watch hints, resource lifetimes and the metadata-only boundary."""

import errno
import json
import os
import platform
import subprocess
import sys
from contextlib import nullcontext
from hashlib import sha256
from pathlib import Path
from threading import Event, Thread
from time import monotonic
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from aitm_usage import host_watch
from aitm_usage.host_watch import WatchError, WatchKind, WatchRoot, WatchSet
from aitm_usage.types import SourceRef


def _root(path, label="root"):
    path = path.resolve()
    info = path.stat()
    key = SourceRef(f"hmac-sha256:{'a' * 64}:{sha256(label.encode()).hexdigest()}")
    return WatchRoot(key, path, (info.st_dev, info.st_ino))


def _next(watches, predicate, *, timeout=4.0):
    deadline = monotonic() + timeout
    while (remaining := deadline - monotonic()) > 0:
        for event in watches.events(min(remaining, 0.25)):
            if predicate(event):
                return event
    pytest.fail("Expected watch event was not observed")


def _startup(watches, root):
    assert any(
        item.key == root.key
        and item.kind is WatchKind.RECONCILE
        and item.reason == "startup"
        for item in watches.events(0)
    )


def test_native_watch_reports_change_and_retires_resources(tmp_path, monkeypatch):
    watched, lost, healthy, linked = (
        tmp_path / name for name in ("watched", "lost", "healthy", "linked")
    )
    for path in (watched, lost, healthy, linked):
        path.mkdir()
    root, lost_root, healthy_root, linked_root = (
        _root(path, path.name) for path in (watched, lost, healthy, linked)
    )
    payload = root.path / "transcript.jsonl"
    payload.write_text("initial")
    roots = (root, lost_root, healthy_root, linked_root)
    with WatchSet(roots) as watches:
        assert {item.key for item in watches.events(0) if item.reason == "startup"} == {
            item.key for item in roots
        }
        payload.write_text("same length, changed content")
        event = _next(watches, lambda event: event.kind is WatchKind.CHANGED)
        assert event.key == root.key
        retired = watched.rename(tmp_path / "retired")
        watched.mkdir()
        terminal = _next(watches, lambda event: event.kind is WatchKind.ROOT_REPLACED)
        assert terminal.key == root.key

        lost.rename(tmp_path / "moved")
        assert (
            _next(watches, lambda event: event.kind is WatchKind.ROOT_LOST).key
            == lost_root.key
        )
        (healthy / "active.jsonl").touch()
        assert (
            _next(
                watches,
                lambda event: (
                    event.kind is WatchKind.CHANGED and event.key == healthy_root.key
                ),
            ).key
            == healthy_root.key
        )

        previous = linked.rename(tmp_path / "previous")
        linked.symlink_to(previous, target_is_directory=True)
        assert (
            _next(watches, lambda event: event.kind is WatchKind.ROOT_REPLACED).key
            == linked_root.key
        )
        (retired / "late.jsonl").touch()
        (previous / "late.jsonl").touch()
        assert not {root.key, linked_root.key}.intersection(
            event.key for event in watches.events(0.10)
        )

        healthy.rename(tmp_path / "last-retired")
        assert (
            _next(watches, lambda event: event.kind is WatchKind.ROOT_LOST).key
            == healthy_root.key
        )
        if watches._darwin is not None:
            watches._darwin._thread.join(1)
            assert not watches._darwin.alive()
        assert watches.events(0) == ()
    watches.close()
    assert watches.events(0) == ()

    # A fresh, quiet root guarantees the reader reaches its actual native wait.
    quiet = tmp_path / "quiet"
    quiet.mkdir()
    quiet_root = _root(quiet)
    with WatchSet((quiet_root,)) as waiting:
        _startup(waiting, quiet_root)
        _assert_close_wakes_consumer(waiting, monkeypatch)


@pytest.mark.parametrize(
    "replacement",
    [None, "directory", "symlink"],
)
def test_root_loss_and_replacement_are_terminal(monkeypatch, replacement):
    observed = _observed_watch(monkeypatch, "root")
    (root,) = observed.roots
    with observed.watches as watches:
        _startup(watches, root)
        observed.notify(root.key, 0)
        if replacement == "directory":
            chain = observed.directories[root.path]
            observed.directories[root.path] = (*chain[:-1], (1, 100, 0))
        else:
            error = errno.ELOOP if replacement == "symlink" else errno.ENOENT
            observed.directories[root.path] = OSError(
                error, "observed unavailable root"
            )
        expected = (
            WatchKind.ROOT_LOST if replacement is None else WatchKind.ROOT_REPLACED
        )

        (terminal,) = watches.events(0)
        assert (terminal.key, terminal.kind) == (root.key, expected)
        observed.native.drop.assert_called_once_with(root.key)
        observed.notify(root.key, 0)
        assert watches.events(0) == ()
    observed.native.close.assert_called_once_with()


def _observed_watch(monkeypatch, *names):
    roots = tuple(
        WatchRoot(
            SourceRef(f"hmac-sha256:{'a' * 64}:{sha256(name.encode()).hexdigest()}"),
            Path("/fixture") / name,
            (1, index),
        )
        for index, name in enumerate(names, start=2)
    )
    directories = {root.path: ((1, 1, 0), (*root.identity, 0)) for root in roots}
    native = Mock()
    native.alive.return_value = True
    backend = Mock(return_value=native)

    def directory(selected):
        observation = directories[selected]
        if isinstance(observation, OSError):
            raise observation
        return nullcontext((90, observation, ()))

    monkeypatch.setattr(host_watch, "_directory", directory)
    monkeypatch.setattr(host_watch, "_Darwin", backend)
    monkeypatch.setattr(
        host_watch, "platform", SimpleNamespace(system=lambda: "Darwin")
    )
    watches = WatchSet(roots)
    return SimpleNamespace(
        roots=roots,
        directories=directories,
        native=native,
        watches=watches,
        notify=backend.call_args.args[1],
    )


def test_losing_one_root_preserves_other_watch_events(monkeypatch):
    observed = _observed_watch(monkeypatch, "lost", "healthy")
    first, second = observed.roots
    with observed.watches as watches:
        assert {event.key for event in watches.events(0)} == {first.key, second.key}
        observed.directories[first.path] = FileNotFoundError(errno.ENOENT, "root moved")
        (terminal,) = watches.events(0)
        assert (terminal.key, terminal.kind) == (first.key, WatchKind.ROOT_LOST)
        observed.native.drop.assert_called_once_with(first.key)
        observed.notify(first.key, 0)
        observed.notify(second.key, 0)
        (active,) = watches.events(0)
        assert (active.key, active.kind) == (second.key, WatchKind.CHANGED)


def test_unsafe_and_duplicate_roots_refuse(monkeypatch):
    path = Path("/fixture/watch")
    alias = path.with_name("alias")
    root = WatchRoot(SourceRef(f"hmac-sha256:{'a' * 64}:{'b' * 64}"), path, (1, 2))
    duplicate = WatchRoot(
        SourceRef(f"hmac-sha256:{'a' * 64}:{'c' * 64}"), path, root.identity
    )

    def observed_directory(selected):
        if selected == alias:
            raise OSError(errno.ELOOP, "observed no-follow rejection for the alias")
        assert selected == path
        return nullcontext((90, ((1, 1, 0), (*root.identity, 0)), ()))

    directory = Mock(side_effect=observed_directory)
    platform = Mock(side_effect=AssertionError("Unsafe roots reached a watch backend"))
    monkeypatch.setattr(host_watch, "_directory", directory)
    monkeypatch.setattr(host_watch, "platform", SimpleNamespace(system=platform))

    with pytest.raises(WatchError, match="Duplicate or invalid authorized watch root"):
        WatchSet((root, duplicate))
    directory.assert_called_once_with(path)
    directory.reset_mock()
    with pytest.raises(WatchError, match="Authorized watch root is unavailable"):
        WatchSet((WatchRoot(root.key, alias, root.identity),))
    directory.assert_called_once_with(alias)
    platform.assert_not_called()


def _assert_close_wakes_consumer(watches, monkeypatch):
    active = Event()
    if watches._linux is not None:
        parent, operation = watches, "_linux_wait"
    else:
        parent, operation = watches._condition, "wait"
    actual_wait = getattr(parent, operation)

    def wait(timeout):
        active.set()
        return actual_wait(timeout)

    results = []

    def consume():
        results.append(watches.events(20.0))

    with monkeypatch.context() as observe:
        observe.setattr(parent, operation, wait)
        reader = Thread(target=consume, daemon=True)
        reader.start()
        assert active.wait(1)
        assert reader.is_alive()
        watches.close()
        reader.join(1)
        assert not reader.is_alive()
        assert results == [()]


def test_close_wakes_blocked_consumer(monkeypatch):
    observed = _observed_watch(monkeypatch, "root")
    (root,) = observed.roots
    with observed.watches as watches:
        _startup(watches, root)
        _assert_close_wakes_consumer(watches, monkeypatch)
        observed.native.close.assert_called_once_with()


def test_native_watch_opens_directories_and_no_payloads(tmp_path):
    root = _root(tmp_path)
    payload = root.path / "transcript.jsonl"
    payload.write_text("initial")
    child = r"""
import json, os, sys
from pathlib import Path
from time import monotonic
from aitm_usage.host_watch import WatchKind, WatchRoot, WatchSet
from aitm_usage.types import SourceRef

path = Path(sys.argv[1])
stat = path.stat()
root = WatchRoot(SourceRef(sys.argv[2]), path, (stat.st_dev, stat.st_ino))
directory_opens = []
other_opens = []

def audit(event, data):
    if event != "open":
        return
    name, _, flags = data
    if flags & os.O_DIRECTORY:
        directory_opens.append(str(name) != "transcript.jsonl")
    else:
        other_opens.append(str(name))

sys.addaudithook(audit)
with WatchSet((root,)) as watches:
    watches.events(0)
    print("READY", flush=True)
    deadline = monotonic() + 4
    observed = False
    while not observed and monotonic() < deadline:
        observed = any(item.kind is WatchKind.CHANGED for item in watches.events(0.10))
print(json.dumps({"observed": observed,
                  "directory_opens": bool(directory_opens) and all(directory_opens),
                  "other_opens": len(other_opens)}))
"""
    with subprocess.Popen(
        [sys.executable, "-c", child, str(root.path), root.key.value],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        try:
            assert process.stdout is not None
            assert process.stdout.readline().strip() == "READY"
            payload.write_text("changed outside the audited child")
            output, errors = process.communicate(timeout=6)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
        assert process.returncode == 0, errors
        assert json.loads(output) == {
            "observed": True,
            "directory_opens": True,
            "other_opens": 0,
        }


# The inotify-specific cases apply when the Linux backend is available.
if platform.system() == "Linux":

    def test_linux_new_and_moved_directories_reconcile(tmp_path):
        watched = tmp_path / "watched"
        watched.mkdir()
        root = _root(watched)
        target = root.path / "nested"
        with WatchSet((root,)) as watches:
            _startup(watches, root)
            target.mkdir()
            _next(watches, lambda item: item.reason == "enrollment")
            (target / "native.jsonl").touch()
            assert (
                _next(watches, lambda item: item.kind is WatchKind.CHANGED).key
                == root.key
            )
            outside = tmp_path / "moved-out"
            target.rename(outside)
            _next(watches, lambda item: item.reason == "enrollment")
            (outside / "outside.jsonl").touch()
            assert not any(
                item.kind is WatchKind.CHANGED for item in watches.events(0.05)
            )
            restored = root.path / "moved-in"
            outside.rename(restored)
            _next(watches, lambda item: item.reason == "enrollment")
            (restored / "moved.jsonl").touch()
            assert (
                _next(watches, lambda item: item.kind is WatchKind.CHANGED).key
                == root.key
            )

    def test_linux_reports_real_queue_overflow_and_rebuilds(tmp_path):
        maximum = int(Path("/proc/sys/fs/inotify/max_queued_events").read_text())
        assert 0 < maximum <= 65536
        root = _root(tmp_path)
        path = root.path / "churn"
        with WatchSet((root,)) as watches:
            _startup(watches, root)
            limit = monotonic() + 8
            for _ in range(maximum // 2 + 16):
                assert monotonic() < limit
                path.touch()
                path.unlink()
            overflow = _next(watches, lambda item: item.reason == "overflow")
            assert overflow.key == root.key
            path.touch()
            assert (
                _next(watches, lambda item: item.kind is WatchKind.CHANGED).key
                == root.key
            )

    @pytest.fixture
    def linux_watch_descriptors(monkeypatch):
        crowded, quiet = Path("/fixture/crowded"), Path("/fixture/quiet")
        nested = crowded / "nested"
        directories = {
            crowded: (20, ((1, 1, 0), (1, 20, 0))),
            nested: (21, ((1, 1, 0), (1, 20, 0), (1, 21, 0))),
            quiet: (22, ((1, 1, 0), (1, 22, 0))),
        }
        roots = tuple(
            WatchRoot(
                SourceRef(
                    f"hmac-sha256:{'a' * 64}:{sha256(path.name.encode()).hexdigest()}"
                ),
                path,
                directories[path][1][-1][:2],
            )
            for path in (crowded, quiet)
        )
        clock = Mock(return_value=0.0)
        pending = []
        api = SimpleNamespace(refuse_nested=False, roots=roots, clock=clock, removed=[])
        event_fd, wake_read, wake_write = 30, 31, 32

        def directory(path):
            fd, chain = directories[path]
            return nullcontext((fd, chain, ()))

        def scandir(fd):
            children = (
                (SimpleNamespace(name=nested.name, is_dir=Mock(return_value=True)),)
                if fd == directories[crowded][0]
                else ()
            )
            return nullcontext(children)

        def add(fd, path, mask):
            assert fd == event_fd and mask == host_watch._LINUX_MASK
            descriptor = int(path.removeprefix(b"/proc/self/fd/"))
            assert descriptor in {value[0] for value in directories.values()}
            if descriptor == directories[nested][0] and api.refuse_nested:
                return -1
            return descriptor

        def remove(fd, watch):
            assert fd == event_fd
            api.removed.append(watch)
            return 0

        def read(fd, count):
            assert fd == event_fd and count >= host_watch._LINUX_STRUCT.size
            return pending.pop(0)

        def poll():
            reader = Mock()
            reader.poll.return_value = ((event_fd, 1),) if pending else ()
            return reader

        def change_quiet():
            pending.append(
                host_watch._LINUX_STRUCT.pack(directories[quiet][0], 0x02, 0, 0)
            )

        api.change_quiet = change_quiet
        native = {
            "inotify_init1": Mock(return_value=event_fd),
            "inotify_add_watch": add,
            "inotify_rm_watch": remove,
        }
        monkeypatch.setattr(host_watch, "_bind", lambda _, name, *__: native[name])
        monkeypatch.setattr(host_watch, "_directory", directory)
        monkeypatch.setattr(host_watch, "monotonic", clock)
        monkeypatch.setattr(host_watch, "select", SimpleNamespace(poll=poll, POLLIN=1))
        monkeypatch.setattr(
            host_watch,
            "ct",
            SimpleNamespace(
                CDLL=Mock(),
                c_int=host_watch.ct.c_int,
                c_char_p=host_watch.ct.c_char_p,
                c_uint32=host_watch.ct.c_uint32,
                get_errno=lambda: errno.ENOSPC,
            ),
        )
        monkeypatch.setattr(
            host_watch,
            "os",
            SimpleNamespace(
                O_NONBLOCK=os.O_NONBLOCK,
                O_CLOEXEC=os.O_CLOEXEC,
                pipe2=Mock(return_value=(wake_read, wake_write)),
                fsencode=os.fsencode,
                scandir=scandir,
                read=read,
                write=Mock(),
                close=Mock(),
            ),
        )
        return api

    def test_linux_registration_bound_falls_back_for_one_root(linux_watch_descriptors):
        native = linux_watch_descriptors
        first, second = native.roots
        with WatchSet(
            (first, second), max_directories_per_root=1, fallback_interval=0.05
        ) as watches:
            initial = watches.events(0)
            assert {item.key for item in initial if item.reason == "startup"} == {
                first.key,
                second.key,
            }
            assert watches.events(0) == ()
            native.clock.return_value = 0.05
            assert watches.events(0) == (
                host_watch.WatchEvent(first.key, WatchKind.RECONCILE, "fallback"),
            )
            native.change_quiet()
            assert watches.events(0) == (
                host_watch.WatchEvent(second.key, WatchKind.CHANGED),
            )

    def test_linux_overlapping_roots_share_descriptor_without_weakening_mask(
        tmp_path, monkeypatch
    ):
        inner = tmp_path / "inner"
        inner.mkdir()
        outer, child = _root(tmp_path, "outer"), _root(inner, "inner")
        bind = host_watch._bind
        registrations = []

        def inspect_registration(library, name, result, *arguments):
            native = bind(library, name, result, *arguments)
            if name != "inotify_add_watch":
                return native

            def add(fd, path, mask):
                info = os.stat(path)
                watch = native(fd, path, mask)
                registrations.append((info.st_ino, path, mask, watch))
                return watch

            return add

        monkeypatch.setattr(host_watch, "_bind", inspect_registration)
        with WatchSet((outer, child)) as watches:
            watches.events(0)
            inside = [
                record for record in registrations if record[0] == child.identity[1]
            ]
            assert len(inside) == 2 and inside[0][3] == inside[1][3]
            assert all(path.startswith(b"/proc/self/fd/") for _, path, _, _ in inside)
            masks = {mask for _, _, mask, _ in inside}
            assert len(masks) == 1
            (mask,) = masks
            assert mask & 0x01000000 and not mask & 0x02000000
            (inner / "both.jsonl").touch()
            assert {item.key for item in watches.events(1)} == {outer.key, child.key}
            backend = watches._linux
            assert backend is not None
            descriptors = (backend.fd, *watches._wake_fds)
        for fd in descriptors:
            with pytest.raises(OSError) as retired:
                os.fstat(fd)
            assert retired.value.errno == errno.EBADF

    def test_linux_kernel_capacity_retires_partial_root_only(linux_watch_descriptors):
        native = linux_watch_descriptors
        native.refuse_nested = True
        first, second = native.roots
        with WatchSet((first, second), fallback_interval=0.02) as watches:
            initial = watches.events(0)
            assert {item.key for item in initial} == {first.key, second.key}
            backend = watches._linux
            assert backend is not None
            assert all(first.key not in members for members in backend.watches.values())
            assert native.removed == [first.identity[1]]
            native.clock.return_value = 0.02
            assert watches.events(0) == (
                host_watch.WatchEvent(first.key, WatchKind.RECONCILE, "fallback"),
            )
            native.change_quiet()
            assert watches.events(0) == (
                host_watch.WatchEvent(second.key, WatchKind.CHANGED),
            )
