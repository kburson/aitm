"""Opt-in checks for the macOS FSEvents backend and its native ownership."""

import platform
from threading import Event, Thread

import pytest
from test_host_watch import _next, _root, _startup

from aitm_usage import host_watch
from aitm_usage.host_watch import WatchError, WatchKind, WatchSet

pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin", reason="requires FSEvents"
)


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


def test_darwin_join_timeout_keeps_callback_until_verified_close(tmp_path, monkeypatch):
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


def test_darwin_last_lost_root_retires_native_owner_without_waiting_for_close(
    tmp_path,
):
    watched = tmp_path / "watched"
    watched.mkdir()
    root = _root(watched)
    with WatchSet((root,)) as watches:
        _startup(watches, root)
        backend = watches._darwin
        assert backend is not None
        watched.rename(tmp_path / "moved")
        _next(watches, lambda item: item.kind is WatchKind.ROOT_LOST)
        backend._thread.join(1)
        assert not backend.alive()
