"""Native watch hints, resource lifetimes and the metadata-only boundary."""

import errno
import json
import os
import platform
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from threading import Event, Thread
from time import monotonic

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


def test_native_watch_reports_change_and_retires_resources(tmp_path):
    root = _root(tmp_path)
    payload = root.path / "transcript.jsonl"
    payload.write_text("initial")
    with WatchSet((root,)) as watches:
        _startup(watches, root)
        payload.write_text("same length, changed content")
        event = _next(watches, lambda event: event.kind is WatchKind.CHANGED)
        assert event.key == root.key
    watches.close()
    assert watches.events(0) == ()


@pytest.mark.parametrize(
    "replacement",
    [None, "directory", "symlink"],
)
def test_root_loss_and_replacement_are_terminal(tmp_path, replacement):
    watched = tmp_path / "watched"
    watched.mkdir()
    root = _root(watched)
    other = tmp_path / "previous"
    with WatchSet((root,)) as watches:
        _startup(watches, root)
        watched.rename(other)
        if replacement == "directory":
            watched.mkdir()
        elif replacement == "symlink":
            watched.symlink_to(other, target_is_directory=True)
        expected = WatchKind.ROOT_REPLACED if replacement else WatchKind.ROOT_LOST
        item = _next(watches, lambda event: event.kind is expected)
        assert item.key == root.key
        (other / "late.jsonl").touch()
        assert watches.events(0.10) == ()


def test_unsafe_and_duplicate_roots_refuse(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(WatchError):
        WatchSet((root, _root(tmp_path, "another")))
    actual = tmp_path / "actual"
    actual.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    with pytest.raises(WatchError):
        WatchSet((WatchRoot(root.key, alias, _root(actual).identity),))


def test_close_wakes_blocked_consumer(tmp_path):
    root = _root(tmp_path)
    with WatchSet((root,)) as watches:
        _startup(watches, root)
        active = Event()
        results = []

        def consume():
            active.set()
            results.append(watches.events(20.0))

        reader = Thread(target=consume, daemon=True)
        reader.start()
        assert active.wait(1)
        assert reader.is_alive()
        watches.close()
        reader.join(1)
        assert not reader.is_alive()
        assert results == [()]


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


# Each host collects its own native ABI cases. Both hosts run the shared cases.
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

    def test_linux_registration_bound_falls_back_for_one_root(tmp_path):
        crowded, quiet = (tmp_path / name for name in ("crowded", "quiet"))
        crowded.mkdir()
        quiet.mkdir()
        (crowded / "nested").mkdir()
        first, second = _root(crowded, "first"), _root(quiet, "second")
        with WatchSet(
            (first, second), max_directories_per_root=1, fallback_interval=0.05
        ) as watches:
            initial = watches.events(0)
            assert {item.key for item in initial if item.reason == "startup"} == {
                first.key,
                second.key,
            }
            assert (
                _next(watches, lambda item: item.reason == "fallback").key == first.key
            )
            (quiet / "file.jsonl").touch()
            assert (
                _next(watches, lambda item: item.kind is WatchKind.CHANGED).key
                == second.key
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

    def test_linux_kernel_capacity_retires_partial_root_only(tmp_path, monkeypatch):
        limited, healthy = (tmp_path / name for name in ("limited", "healthy"))
        limited.mkdir()
        healthy.mkdir()
        refused = limited / "nested"
        refused.mkdir()
        first, second = _root(limited, "first"), _root(healthy, "second")
        denied = refused.stat()
        bind = host_watch._bind

        def inject_limit(library, name, result, *arguments):
            native = bind(library, name, result, *arguments)
            if name != "inotify_add_watch":
                return native

            def add(fd, path, mask):
                if os.path.samestat(denied, os.stat(path)):
                    host_watch.ct.set_errno(errno.ENOSPC)
                    return -1
                return native(fd, path, mask)

            return add

        monkeypatch.setattr(host_watch, "_bind", inject_limit)
        with WatchSet((first, second), fallback_interval=0.02) as watches:
            initial = watches.events(0)
            assert {item.key for item in initial} == {first.key, second.key}
            backend = watches._linux
            assert backend is not None
            assert all(first.key not in members for members in backend.watches.values())
            assert (
                _next(watches, lambda item: item.reason == "fallback").key == first.key
            )
            (healthy / "available.jsonl").touch()
            assert (
                _next(watches, lambda item: item.kind is WatchKind.CHANGED).key
                == second.key
            )


if platform.system() == "Darwin":

    @pytest.mark.parametrize(
        "flags", [0x01, 0x02, 0x04, 0x08, 0x20, 0x40, 0x80, 0x80000000]
    )
    def test_darwin_drop_wrap_and_mount_flags_reconcile(tmp_path, flags):
        root = _root(tmp_path)
        with WatchSet((root,)) as watches:
            _startup(watches, root)
            watches._darwin_hint(root.key, flags)
            assert (
                _next(watches, lambda event: event.reason == "native-rescan").key
                == root.key
            )

    def test_darwin_start_failure_retires_owned_resources(tmp_path, monkeypatch):
        root = _root(tmp_path)
        bind = host_watch._bind
        retired = []

        def fail_start(library, name, result, *arguments):
            native = bind(library, name, result, *arguments)
            if name == "FSEventStreamStart":
                return lambda _: False
            if name not in {
                "FSEventStreamInvalidate",
                "FSEventStreamRelease",
                "CFRelease",
            }:
                return native

            def cleanup(handle):
                native(handle)
                retired.append(name)

            return cleanup

        monkeypatch.setattr(host_watch, "_bind", fail_start)
        with pytest.raises(WatchError, match="did not start"):
            WatchSet((root,))
        assert retired == [
            "FSEventStreamInvalidate",
            "FSEventStreamRelease",
            "CFRelease",
            "CFRelease",
            "CFRelease",
        ]

    def test_darwin_join_timeout_keeps_callback_until_verified_close(
        tmp_path, monkeypatch
    ):
        root = _root(tmp_path)
        with WatchSet((root,)) as watches:
            backend = watches._darwin
            assert backend is not None and backend._callbacks
            with monkeypatch.context() as patch:
                patch.setattr(backend._thread, "join", lambda _: None)
                patch.setattr(backend._thread, "is_alive", lambda: True)
                with pytest.raises(WatchError, match="owner did not retire"):
                    watches.close()
                assert watches._darwin is backend and backend._callbacks
            watches.close()
            assert not backend._callbacks and not backend.alive()

    def test_darwin_busy_consumer_coalesces_without_blocking_callback(tmp_path):
        root = _root(tmp_path)
        with WatchSet((root,)) as watches:
            _startup(watches, root)
            returned = Event()

            def deliver():
                watches._darwin_hint(root.key, 0x02)
                returned.set()

            sender = Thread(target=deliver, daemon=True)
            with watches._condition:
                sender.start()
                assert returned.wait(1)
            sender.join(1)
            assert (
                _next(watches, lambda item: item.reason == "callback-pressure").key
                == root.key
            )
