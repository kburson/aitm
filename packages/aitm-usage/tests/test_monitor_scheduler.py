"""Observable scheduler behavior and private wake transport."""

import errno
import os
import socket
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

import pytest
from test_monitor_coverage import admitted_sources as admitted_sources
from test_monitor_qualification import qualify
from test_monitor_scope import SOURCE

from aitm_usage import cli, monitor_control, monitor_registry
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_control import WakeIngress
from aitm_usage.monitor_registry import Registry
from aitm_usage.monitor_scheduler import (
    ResolvedWake,
    Scheduler,
    ScheduleState,
    WakeHint,
    WakeResolution,
    WakeResolutionKind,
)
from aitm_usage.monitor_types import MonitorProvider
from aitm_usage.sources.hooks import (
    HookEvent,
    HookSender,
    WakeDisposition,
    WakeKind,
    _parse_frame,
)


class Resolver:
    def __init__(self, writer, hint):
        self.writer = writer
        self.result = WakeResolution(WakeResolutionKind.RESOLVED, hint)
        self.calls = []

    def resolve(self, request, *, lease):
        assert lease is self.writer.lease
        self.calls.append(request)
        return self.result


@pytest.fixture
def wake():
    # Native sun_path is shorter than many pytest basetemp paths.
    with TemporaryDirectory(prefix="aitm-wake-") as temporary:
        with Registry(Path(temporary).resolve() / "m").writer() as writer:
            evidence = writer.source_evidence()
            now = [0.0]
            scheduler = Scheduler(writer, clock=lambda: now[0], lease_ttl=3.0)

            def ref(name):
                return evidence.pseudonymize("wake-test", name)

            facts = ResolvedWake(
                MonitorProvider.CODEX,
                ref("stream"),
                ref("raw-session-canary"),
                ref("raw-turn-canary"),
                ref("project"),
                ref("raw-cursor-canary"),
                current_stop=True,
            )
            resolver = Resolver(writer, facts)
            yield scheduler, resolver, ref, now


def _change(scheduler, resolver, kind=WakeKind.CHANGE):
    return scheduler._admit(
        HookEvent(kind, MonitorProvider.CODEX, "/raw-path-canary"), resolver
    )


def _new_fact(resolver, **changes):
    resolver.result = WakeResolution(
        WakeResolutionKind.RESOLVED, replace(resolver.result.facts, **changes)
    )


def test_park_final_catchup_then_late_write_reopens(wake):
    scheduler, resolver, ref, now = wake
    assert _change(scheduler, resolver)
    (first,) = scheduler.take_due(now[0], 1)
    assert first.state is ScheduleState.ACTIVE
    assert _change(scheduler, resolver, WakeKind.STOP)
    assert not scheduler.finish(first, caught_up=True)
    (last,) = scheduler.take_due(now[0], 1)
    assert last.state is ScheduleState.SETTLING
    assert scheduler.finish(last, caught_up=True)
    assert scheduler.take_due(now[0], 1) == ()
    assert _change(scheduler, resolver)
    assert scheduler.take_due(now[0], 1) == ()
    _new_fact(resolver, fact=ref("native-later"))
    assert _change(scheduler, resolver)
    (reopened,) = scheduler.take_due(now[0], 1)
    assert reopened.state is ScheduleState.ACTIVE
    assert reopened.generation > last.generation


def test_stale_stop_cannot_park_newer_turn(wake):
    scheduler, resolver, ref, now = wake
    assert _change(scheduler, resolver)
    older = resolver.result
    _new_fact(resolver, turn=ref("second-turn"), fact=ref("second-fact"))
    assert _change(scheduler, resolver)
    resolver.result = older
    assert not _change(scheduler, resolver, WakeKind.STOP)
    items = scheduler.take_due(now[0], 2)
    assert len(items) == 2
    assert {item.state for item in items} == {ScheduleState.ACTIVE}
    assert scheduler.park(older.facts.session)
    assert [item.state for item in scheduler.take_due(now[0], 2)] == [
        ScheduleState.SETTLING,
        ScheduleState.SETTLING,
    ]


def test_duplicate_and_missing_hooks_keep_idempotent_progress(wake):
    scheduler, resolver, ref, now = wake
    assert _change(scheduler, resolver)
    assert _change(scheduler, resolver)
    (item,) = scheduler.take_due(now[0], 3)
    assert scheduler.take_due(now[0], 3) == ()
    assert scheduler.finish(item, caught_up=True)
    assert not scheduler.finish(item, caught_up=True)
    assert _change(scheduler, resolver)
    assert scheduler.take_due(now[0], 3) == ()
    # The coordinator's fallback observes native progress without a hook.
    _new_fact(resolver, fact=ref("fallback-observation"))
    assert _change(scheduler, resolver)
    (fallback,) = scheduler.take_due(now[0], 3)
    assert fallback.generation > item.generation


def test_restart_recovers_pending_wake_without_its_old_lease(wake):
    scheduler, resolver, _, now = wake
    assert _change(scheduler, resolver)
    (first,) = scheduler.take_due(now[0], 1)
    restored = Scheduler(resolver.writer, clock=lambda: now[0], lease_ttl=3.0)
    assert not restored.finish(first, caught_up=True)
    (again,) = restored.take_due(now[0], 1)
    assert again.generation == first.generation
    assert again is not first
    now[0] = 3.0
    (retry,) = restored.take_due(now[0], 1)
    assert retry is not again
    assert not restored.finish(again, caught_up=True)
    assert restored.finish(retry, caught_up=False)
    assert restored.take_due(now[0], 1) == ()
    now[0] += 0.25
    assert len(restored.take_due(now[0], 1)) == 1


def test_full_project_does_not_starve_another_due_project(wake):
    scheduler, resolver, ref, now = wake
    assert _change(scheduler, resolver)
    first_project = resolver.result.facts.project
    for label in ("two", "three"):
        _new_fact(
            resolver,
            stream=ref("stream-" + label),
            session=ref(label),
            project=ref("project-" + label),
            fact=ref("fact-" + label),
        )
        assert _change(scheduler, resolver)
    served = []
    for _ in range(3):
        (item,) = scheduler.take_due(now[0], 1)
        served.append(item.project)
        assert scheduler.finish(item, caught_up=item.project != first_project)
    assert len(set(served)) == 3
    assert scheduler.take_due(now[0], 1) == ()


def test_wire_cannot_notify_without_approved_resolution(wake, monkeypatch):
    scheduler, resolver, _, now = wake
    sender = HookSender(resolver.writer.root)
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/raw-path-canary")
    resolver.result = WakeResolution(WakeResolutionKind.UNKNOWN_LOCATOR)
    with WakeIngress(scheduler, resolver).listen() as listener:
        assert sender.notify(event) is WakeDisposition.SENT
        assert not listener.serve_once()
        assert resolver.calls == [event]
        assert scheduler.take_due(now[0], 1) == ()
        monkeypatch.setattr(monitor_control, "_peer_uid", lambda _: os.geteuid() + 1)
        monkeypatch.setattr(
            monitor_control,
            "_read_frame",
            lambda *_: pytest.fail("mismatched peer reached frame parsing"),
        )
        assert sender.notify(event) is WakeDisposition.SENT
        assert not listener.serve_once()
    assert resolver.calls == [event]
    with pytest.raises(LedgerError):
        scheduler.notify(WakeHint())


def test_real_socket_and_park_cli_retain_only_keyed_wake_bytes(
    wake, monkeypatch, capsys
):
    scheduler, resolver, _, now = wake
    sender = HookSender(resolver.writer.root)
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/raw-path-canary")
    monkeypatch.setattr(
        monitor_registry, "default_monitor_root", lambda: resolver.writer.root
    )
    with WakeIngress(scheduler, resolver).listen() as listener:
        assert sender.notify(event) is WakeDisposition.SENT
        assert listener.serve_once()
        session = resolver.result.facts.session.value
        monkeypatch.setattr(
            sys,
            "argv",
            ["aitm-usage", "monitor", "park", "--session-ref", session, "--json"],
        )
        assert cli.main() == 0
        assert "sent" in capsys.readouterr().out
        assert listener.serve_once()
        (item,) = scheduler.take_due(now[0], 1)
        assert item.state is ScheduleState.SETTLING
        assert scheduler.finish(item, caught_up=True)
        assert scheduler.take_due(now[0], 1) == ()
    for path in (resolver.writer.root / "wake").iterdir():
        for raw in (
            b"/raw-path-canary",
            b"raw-session-canary",
            b"raw-turn-canary",
            b"raw-cursor-canary",
        ):
            assert raw not in path.read_bytes()


@pytest.mark.parametrize(
    "raw",
    [
        b'{"kind":"change","locator":"x","provider":"codex","v":true}\n',
        b'{"v":1, "kind":"change", "locator":"x", "provider":"codex"}\n',
        b'{"kind":"change","locator":"\\ud800","provider":"codex","v":1}\n',
        b'{"kind":"change","locator":"x","locator":"x","provider":"codex","v":1}\n',
        b'{"kind":"change","locator":"'
        + b"x" * 1025
        + b'","provider":"codex","v":1}\n',
        b"x" * 2049,
    ],
)
def test_wake_wire_refuses_noncanonical_or_unbounded_frames(raw):
    with pytest.raises(ValueError):
        _parse_frame(raw)


def test_wake_publication_failure_creates_no_memory_only_due_work(wake, monkeypatch):
    from aitm_usage import monitor_scheduler

    scheduler, resolver, _, now = wake
    with monkeypatch.context() as fault:
        fault.setattr(monitor_scheduler, "_publish", lambda *_a, **_k: False)
        with pytest.raises(LedgerError):
            _change(scheduler, resolver)
    assert scheduler.take_due(now[0], 1) == ()
    assert _change(scheduler, resolver)
    assert len(scheduler.take_due(now[0], 1)) == 1


def test_sender_unavailable_and_listener_refuses_an_unsafe_endpoint(wake):
    scheduler, resolver, _, _ = wake
    root = resolver.writer.root
    sender = HookSender(root)
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/unavailable")
    assert sender.notify(event) is WakeDisposition.UNAVAILABLE
    endpoint = root / "wake.sock"
    foreign = root / "foreign"
    foreign.write_text("untouched")
    endpoint.symlink_to(foreign)
    with pytest.raises(LedgerError):
        with WakeIngress(scheduler, resolver).listen():
            pytest.fail("unsafe socket accepted")
    assert endpoint.is_symlink() and foreign.read_text() == "untouched"
    endpoint.unlink()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stale:
        stale.bind(str(endpoint))
        endpoint.chmod(0o644)
    with pytest.raises(LedgerError, match="requires owner removal"):
        with WakeIngress(scheduler, resolver).listen():
            pytest.fail("unverified pre-chmod endpoint was reclaimed")
    endpoint.chmod(0o600)
    assert sender.notify(event) is WakeDisposition.UNAVAILABLE
    with WakeIngress(scheduler, resolver).listen() as listener:
        assert sender.notify(event) is WakeDisposition.SENT
        assert listener.serve_once()


def test_saturated_listener_is_preserved_and_sender_returns(wake, monkeypatch):
    scheduler, resolver, _, _ = wake
    root = resolver.writer.root
    endpoint = root / "wake.sock"
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/backlog")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as occupied:
        occupied.bind(str(endpoint))
        endpoint.chmod(0o600)
        occupied.listen(1)
        inode = endpoint.lstat()

        # Backlog limits vary by kernel. Preserve the real bound inode and
        # make the saturated-connect branch deterministic on every host.
        def saturated(connection, address):
            assert connection.getblocking() is False
            assert address == str(endpoint)
            return errno.EAGAIN

        monkeypatch.setattr(socket.socket, "connect_ex", saturated)
        began = monotonic()
        assert HookSender(root).notify(event) is WakeDisposition.UNAVAILABLE
        assert monotonic() - began < 0.3
        with pytest.raises(LedgerError, match="active or unavailable"):
            with WakeIngress(scheduler, resolver).listen():
                pytest.fail("active endpoint was reclaimed")
        assert os.path.samestat(inode, endpoint.lstat())


def test_wake_socket_refuses_a_path_past_the_native_byte_limit(tmp_path, wake):
    _, resolver, _, _ = wake
    long_root = tmp_path / ("x" * 104)
    with Registry(long_root).writer() as writer:
        writer.source_evidence()
        with pytest.raises(LedgerError, match="address is too long"):
            with WakeIngress(Scheduler(writer), resolver).listen():
                pytest.fail("oversized address was opened")
        assert not (long_root / "wake.sock").exists()


def test_approved_real_locator_can_issue_wake(admitted_sources):
    native, _ = admitted_sources
    with native.registry.writer() as writer:
        qualify(writer)
        evidence = writer.source_evidence()
        locator = native.locator()
        path = str(locator._source._path)
        scheduler = Scheduler(writer)

        class NativeResolver:
            def resolve(self, request, *, lease):
                assert lease is writer.lease
                if request.locator != path:
                    return WakeResolution(WakeResolutionKind.UNKNOWN_LOCATOR)
                _, current, _ = writer._approved_candidate(
                    writer.view(), SOURCE, locator
                )

                def fact(value):
                    return evidence.pseudonymize("wake-native-test", value)

                return WakeResolution(
                    WakeResolutionKind.RESOLVED,
                    ResolvedWake(
                        MonitorProvider.CODEX,
                        current.stream_ref,
                        fact("session"),
                        fact("turn"),
                        None,
                        fact("fact"),
                        current_stop=False,
                    ),
                )

        resolver = NativeResolver()
        assert scheduler._admit(
            HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, path), resolver
        )
        (work,) = scheduler.take_due(monotonic(), 1)
        assert work.stream == locator.stream_ref
