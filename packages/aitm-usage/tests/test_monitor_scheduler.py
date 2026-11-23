"""Observable scheduler behavior and private wake transport."""

import errno
import os
import socket
import stat
import sys
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call

import pytest
from delivery_policy_cases import delivery_destinations, delivery_journal_rows
from test_monitor_delivery import _journal, _reserve
from test_monitor_journal import (
    COPY,
    LIVE,
    A,
    B,
    _MemoryJournalTranscripts,
)

from aitm_usage import cli, monitor_control, monitor_registry, monitor_scheduler
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_control import WakeIngress
from aitm_usage.monitor_registry import Registry, RegistryView, _ServiceEvidence
from aitm_usage.monitor_scheduler import (
    ResolvedWake,
    Scheduler,
    ScheduleState,
    WakeHint,
    WakeResolution,
    WakeResolutionKind,
)
from aitm_usage.monitor_types import MonitorProvider
from aitm_usage.monitor_writer import ProjectDelivery
from aitm_usage.sources import hooks
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
            yield _wake_context(writer)


def _wake_context(writer):
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
    return scheduler, Resolver(writer, facts), ref, now


@pytest.fixture
def wake_policy(monkeypatch):
    evidence = _ServiceEvidence(b"wake-policy-fixture")
    view = RegistryView(source_key_id=evidence.key_id)
    writer = SimpleNamespace(
        root=Path("/fixture/monitor"),
        lease=Mock(),
        view=lambda: view,
        source_evidence=lambda: evidence,
    )
    _attach_wake_files(monkeypatch)
    return _wake_context(writer)


def _attach_wake_files(monkeypatch):
    files = {}
    root = SimpleNamespace(check=Mock())
    directory = SimpleNamespace(fd=7, check=Mock())

    def read(location, filename):
        assert location is directory
        return files.get(filename)

    def publish(location, filename, data, *, replace_pending):
        assert location is directory
        assert replace_pending == (filename in files)
        files[filename] = data
        return True

    monkeypatch.setattr(
        monitor_scheduler, "_pin_directory", lambda path: nullcontext(root)
    )
    monkeypatch.setattr(
        monitor_scheduler, "_private_child", lambda *args, **_: nullcontext(directory)
    )
    monkeypatch.setattr(monitor_scheduler, "_publication", nullcontext)
    monkeypatch.setattr(
        monitor_scheduler,
        "os",
        SimpleNamespace(listdir=lambda fd: tuple(files), fsync=Mock()),
    )
    monkeypatch.setattr(monitor_scheduler, "_read_private", read)
    monkeypatch.setattr(monitor_scheduler, "_publish", publish)


@pytest.fixture
def listener_policy(wake_policy, monkeypatch):
    scheduler, resolver, _, now = wake_policy
    directory = SimpleNamespace(path=resolver.writer.root, fd=7, check=Mock())
    endpoint = directory.path / "wake.sock"
    uid = 501
    info = os.stat_result((stat.S_IFSOCK | 0o600, 9, 1, 1, uid, 0, 0, 0, 0, 0))
    queued = []
    received = []
    client = MagicMock(spec=socket.socket)
    client.fileno.return_value = 27

    def stat_socket(name, *, dir_fd, follow_symlinks):
        assert (name, dir_fd, follow_symlinks) == (endpoint.name, directory.fd, False)
        return info

    def lstat_socket(path):
        assert path == str(endpoint)
        return info

    def accept():
        received[:] = [queued.pop(0), b""]
        return client, None

    def read(fd, size):
        assert fd == 27
        data = received.pop(0)
        assert size >= len(data)
        return data

    def readable(readers, write, errors, remaining):
        assert (readers, write, errors) == ([27], [], [])
        assert remaining > 0
        return readers, [], []

    monkeypatch.setattr(
        hooks,
        "os",
        SimpleNamespace(
            fsencode=os.fsencode,
            path=os.path,
            geteuid=lambda: uid,
            stat=stat_socket,
            lstat=lstat_socket,
            read=read,
        ),
    )
    monkeypatch.setattr(hooks, "select", SimpleNamespace(select=readable))
    monkeypatch.setattr(
        monitor_control, "os", SimpleNamespace(path=os.path, geteuid=lambda: uid)
    )
    monkeypatch.setattr(monitor_control, "_peer_uid", lambda _: uid)
    server = SimpleNamespace(accept=accept)
    listener = monitor_control._WakeListener(
        scheduler, resolver, directory, server, info
    )

    def send(event):
        queued.append(hooks._frame(event))

    return scheduler, resolver, now, listener, send, uid


def _change(scheduler, resolver, kind=WakeKind.CHANGE):
    return scheduler._admit(
        HookEvent(kind, MonitorProvider.CODEX, "/raw-path-canary"), resolver
    )


def _new_fact(resolver, **changes):
    resolver.result = WakeResolution(
        WakeResolutionKind.RESOLVED, replace(resolver.result.facts, **changes)
    )


def test_park_final_catchup_then_late_write_reopens(wake_policy):
    scheduler, resolver, ref, now = wake_policy
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


def test_stale_stop_cannot_park_newer_turn(wake_policy):
    scheduler, resolver, ref, now = wake_policy
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


def test_verified_stop_only_new_turn_gets_exactly_one_catchup(wake_policy):
    scheduler, resolver, ref, now = wake_policy
    assert _change(scheduler, resolver)
    assert _change(scheduler, resolver, WakeKind.STOP)
    (first,) = scheduler.take_due(now[0], 1)
    assert scheduler.finish(first, caught_up=True)

    _new_fact(resolver, turn=ref("stop-only-turn"), fact=ref("stop-only-fact"))
    assert _change(scheduler, resolver, WakeKind.STOP)
    (second,) = scheduler.take_due(now[0], 1)
    assert second.turn != first.turn
    assert second.generation > first.generation
    assert second.state is ScheduleState.SETTLING
    assert scheduler.finish(second, caught_up=True)
    assert _change(scheduler, resolver, WakeKind.STOP)
    restored = Scheduler(resolver.writer, clock=lambda: now[0])
    assert restored.take_due(now[0], 2) == ()
    states = {wake.facts.turn: wake.state for wake in restored._records.values()}
    assert states == {
        first.turn: ScheduleState.PARKED,
        second.turn: ScheduleState.PARKED,
    }


def test_duplicate_and_missing_hooks_keep_idempotent_progress(wake_policy):
    scheduler, resolver, ref, now = wake_policy
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


def test_restart_recovers_pending_wake_without_its_old_lease(wake_policy):
    scheduler, resolver, _, now = wake_policy
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


def test_full_project_does_not_starve_another_due_project(wake_policy):
    scheduler, resolver, ref, now = wake_policy
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


def test_due_turns_rotate_by_stream_inside_one_project(wake_policy):
    scheduler, resolver, ref, now = wake_policy
    original = resolver.result.facts.stream
    assert _change(scheduler, resolver)
    now[0] += 1
    _new_fact(resolver, turn=ref("second-turn"), fact=ref("second-fact"))
    assert _change(scheduler, resolver)
    now[0] += 1
    other = ref("other-stream")
    _new_fact(
        resolver,
        stream=other,
        session=ref("other-session"),
        turn=ref("other-turn"),
        fact=ref("other-fact"),
    )
    assert _change(scheduler, resolver)
    first, second, third = (scheduler.take_due(now[0], 1)[0] for _ in range(3))
    assert {first.stream, second.stream} == {original, other}
    assert third.stream == original


def test_delivery_hold_retries_its_exact_cursor_while_other_project_can_ack(
    monkeypatch,
):
    native = _MemoryJournalTranscripts(
        monkeypatch, competing=True, independent_copy=True
    )
    _attach_wake_files(monkeypatch)
    store = delivery_journal_rows(monkeypatch, native.registry)
    with native.registry.writer() as writer:
        journal = _journal(writer, cap=1)
        open_destination = delivery_destinations(monkeypatch, journal, A, B)
        (original,) = _reserve(native, journal)
        store.delivery_enabled = True
        prior = journal.cursor_for(LIVE, native.locator(LIVE))
        native.append(LIVE, native.turn(3))
        now = [0.0]
        scheduler = Scheduler(writer, clock=lambda: now[0])

        def wake_source(source, project):
            def ref(kind, value):
                return native.evidence.pseudonymize(kind, str(value))

            facts = ResolvedWake(
                MonitorProvider.CODEX,
                native.locator(source).stream_ref,
                ref("wake-test-session", source),
                None,
                ref("wake-test-project", project),
                ref("wake-test-fact", source),
                current_stop=False,
            )
            assert _change(scheduler, Resolver(writer, facts))
            (item,) = scheduler.take_due(now[0], 1)
            assert item.stream == facts.stream
            return item

        blocked = wake_source(LIVE, A)
        held = _reserve(native, journal)[-1]
        assert held.status == "held"
        assert journal.cursor_for(LIVE, native.locator(LIVE)) == prior
        assert scheduler.finish(blocked, caught_up=False)

        independent_item = wake_source(COPY, B)
        (other,) = _reserve(native, journal, COPY)
        assert (other.status, other.project_id) == ("pending", B)
        with open_destination(B) as destination:
            delivery = ProjectDelivery.attach(journal, destination)
            ticket = journal.reserve_delivery(other.key, 1)
            result = delivery.commit(ticket)
            ack = journal.ack(delivery, ticket, result)
            assert journal.ack(delivery, ticket, result) == ack
            assert len(destination.monitor_as_of(result.sequence).revisions) == 1
        assert scheduler.finish(independent_item, caught_up=True)
        assert journal.cursor_for(LIVE, native.locator(LIVE)) == prior
        assert scheduler.take_due(now[0], 1) == ()

        with open_destination(A) as destination:
            delivery = ProjectDelivery.attach(journal, destination)
            original_ticket = journal.reserve_delivery(original.key, 1)
            journal.ack(delivery, original_ticket, delivery.commit(original_ticket))
        now[0] += 0.25
        (retry,) = scheduler.take_due(now[0], 1)
        assert (retry.stream, retry.generation) == (blocked.stream, blocked.generation)
        (settled,) = (
            item for item in _reserve(native, journal) if item.key == held.key
        )
        assert settled.status == "pending"
        assert journal.cursor_for(LIVE, native.locator(LIVE)) != prior
        assert scheduler.finish(retry, caught_up=True)


def test_wire_cannot_notify_without_approved_resolution(listener_policy, monkeypatch):
    scheduler, resolver, now, listener, send, uid = listener_policy
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/raw-path-canary")
    resolver.result = WakeResolution(WakeResolutionKind.UNKNOWN_LOCATOR)
    send(event)
    assert not listener.serve_once()
    assert resolver.calls == [event]
    assert scheduler.take_due(now[0], 1) == ()
    monkeypatch.setattr(monitor_control, "_peer_uid", lambda _: uid + 1)
    monkeypatch.setattr(
        monitor_control,
        "_read_frame",
        lambda *_: pytest.fail("mismatched peer reached frame parsing"),
    )
    send(event)
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
        reopened = Scheduler(resolver.writer, clock=lambda: now[0])
        assert not reopened.finish(item, caught_up=True)
        (recovered,) = reopened.take_due(now[0], 1)
        assert (recovered.stream, recovered.generation, recovered.state) == (
            item.stream,
            item.generation,
            item.state,
        )
        assert reopened.finish(recovered, caught_up=True)
        assert reopened.take_due(now[0], 1) == ()
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


def test_decoder_failure_refuses_wake_and_keeps_listener_live(
    listener_policy, monkeypatch
):
    scheduler, resolver, now, listener, send, _ = listener_policy
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/raw-path-canary")

    def exhausted_decoder(*args, **kwargs):
        raise RecursionError("decoder exhausted")

    with monkeypatch.context() as patch:
        patch.setattr(hooks.json, "loads", exhausted_decoder)
        send(event)
        assert not listener.serve_once()
    assert resolver.calls == []
    assert scheduler.take_due(now[0], 1) == ()
    send(event)
    assert listener.serve_once()
    assert len(scheduler.take_due(now[0], 1)) == 1


def test_wake_publication_failure_creates_no_memory_only_due_work(
    wake_policy, monkeypatch
):
    scheduler, resolver, _, now = wake_policy
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


@pytest.mark.parametrize("replace_root", [False, True], ids=["socket", "root"])
def test_replaced_endpoint_is_refused_and_preserved(request, monkeypatch, replace_root):
    if replace_root:
        scheduler, resolver, now, listener, _, _ = request.getfixturevalue(
            "listener_policy"
        )
        changed = LedgerError("Private ledger path identity changed")
        listener.directory.check.side_effect = changed
        accept = Mock(side_effect=AssertionError("Changed root accepted a connection"))
        unlink, sync = Mock(), Mock()
        monkeypatch.setattr(listener.server, "accept", accept)
        monkeypatch.setattr(monitor_control.os, "unlink", unlink, raising=False)
        monkeypatch.setattr(monitor_control.os, "fsync", sync, raising=False)
        assert not listener.serve_once()
        assert resolver.calls == []
        WakeIngress._retire(listener.directory, scheduler.lease, listener.identity)
        accept.assert_not_called()
        unlink.assert_not_called()
        sync.assert_not_called()
        lease = scheduler.lease
        lease.check.reset_mock()
        lease.check.side_effect = changed
        scheduler._writer = Registry(resolver.writer.root, lease)
        with pytest.raises(LedgerError, match="Private ledger path"):
            scheduler.take_due(now[0], 1)
        lease.check.assert_called_once_with()
        return

    wake = request.getfixturevalue("wake")
    scheduler, resolver, _, now = wake
    root = resolver.writer.root
    endpoint = root / "wake.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as foreign:
        with WakeIngress(scheduler, resolver).listen() as listener:
            endpoint.unlink()
            foreign.bind(str(endpoint))
            endpoint.chmod(0o600)
            replacement = endpoint.lstat()
            assert not listener.serve_once()
            assert resolver.calls == []
        assert os.path.samestat(replacement, endpoint.lstat())
    assert scheduler.take_due(now[0], 1) == ()


def test_saturated_listener_is_preserved_and_sender_returns(
    listener_policy, monkeypatch
):
    scheduler, resolver, _, listener, _, _ = listener_policy
    root = resolver.writer.root
    endpoint = root / "wake.sock"
    event = HookEvent(WakeKind.CHANGE, MonitorProvider.CODEX, "/backlog")
    directory = listener.directory
    sender, server, probe = (Mock(spec=socket.socket) for _ in range(3))
    for connection in (sender, probe):
        connection.connect_ex.return_value = errno.EAGAIN
    pin = Mock(side_effect=lambda path: nullcontext(directory))
    opened = Mock(side_effect=map(nullcontext, (sender, server, probe, sender)))
    for module in (hooks, monitor_control):
        monkeypatch.setattr(module, "_pin_directory", pin)
        monkeypatch.setattr(
            module,
            "socket",
            SimpleNamespace(
                socket=opened,
                AF_UNIX=socket.AF_UNIX,
                SOCK_STREAM=socket.SOCK_STREAM,
                SOL_SOCKET=socket.SOL_SOCKET,
                SO_ERROR=socket.SO_ERROR,
            ),
        )
    unlink, fsync = Mock(), Mock()
    monkeypatch.setattr(monitor_control.os, "unlink", unlink, raising=False)
    monkeypatch.setattr(monitor_control.os, "fsync", fsync, raising=False)
    writable = Mock(return_value=([], [], []))
    monkeypatch.setattr(hooks.select, "select", writable)
    monkeypatch.setattr(hooks, "monotonic", lambda: 0.0)

    assert HookSender(root).notify(event) is WakeDisposition.UNAVAILABLE
    writable.assert_called_once_with([], [sender], [], 0.03)
    sender.send.assert_not_called()
    with pytest.raises(LedgerError, match="active or unavailable"):
        with WakeIngress(scheduler, resolver).listen():
            pytest.fail("active endpoint was reclaimed")
    for connection in (sender, probe):
        assert connection.method_calls == [
            call.setblocking(False),
            call.connect_ex(str(endpoint)),
        ]
    assert pin.call_args_list == [call(root), call(root)]
    server.bind.assert_not_called()
    unlink.assert_not_called()
    fsync.assert_not_called()

    writable.reset_mock()
    writable.side_effect = [([], [sender], []), ([], [sender], []), ([], [], [])]
    sender.getsockopt.return_value = 0
    sender.send.side_effect = BlockingIOError
    assert HookSender(root).notify(event) is WakeDisposition.UNAVAILABLE
    sender.getsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_ERROR)
    sender.send.assert_called_once()
    assert bytes(sender.send.call_args.args[0]) == hooks._frame(event)
    assert writable.call_count == 3


def test_wake_socket_refuses_a_path_past_the_native_byte_limit(
    wake_policy, monkeypatch
):
    scheduler, resolver, _, _ = wake_policy
    long_root = Path("/fixture") / ("x" * 104)
    resolver.writer.root = long_root
    directory = SimpleNamespace(path=long_root)
    pin = Mock(return_value=nullcontext(directory))
    server = Mock()
    open_socket = Mock(return_value=nullcontext(server))
    monkeypatch.setattr(monitor_control, "_pin_directory", pin)
    monkeypatch.setattr(
        monitor_control,
        "socket",
        SimpleNamespace(
            socket=open_socket, AF_UNIX=socket.AF_UNIX, SOCK_STREAM=socket.SOCK_STREAM
        ),
    )
    with pytest.raises(LedgerError, match="address is too long"):
        with WakeIngress(scheduler, resolver).listen():
            pytest.fail("oversized address was opened")
    pin.assert_called_once_with(long_root)
    open_socket.assert_called_once_with(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind.assert_not_called()


def test_approved_real_locator_can_issue_wake(monkeypatch):
    native = _MemoryJournalTranscripts(monkeypatch)
    _attach_wake_files(monkeypatch)
    with native.registry.writer() as writer:
        evidence = writer.source_evidence()
        locator = native.locator()
        path = str(locator._source._path)
        scheduler = Scheduler(writer)

        class NativeResolver:
            def resolve(self, request, *, lease):
                assert lease is writer.lease
                if request.locator != path:
                    return WakeResolution(WakeResolutionKind.UNKNOWN_LOCATOR)
                _, current, _ = writer._approved_candidate(writer.view(), LIVE, locator)

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
