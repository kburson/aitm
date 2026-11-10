"""Private registry identity, native capture epochs and command custody."""

import json
import os
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from uuid import UUID

import pytest
from test_codex import AFTER, SESSION, begin, counter, end, response, usage
from test_monitor_adapters import _adapter, _restart_rows
from test_monitor_adapters import source as source

from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.types import Eligibility

PROJECT_A = UUID(int=116)
PROJECT_B = UUID(int=117)
SOURCE = UUID(int=118)


def _module():
    from aitm_usage import monitor_registry

    return monitor_registry


def _directory(root, name, *, mode=0o700):
    path = root / name
    path.mkdir(mode=mode)
    return path


def _request(module, root, project=PROJECT_A, *, anchors=()):
    state = _directory(root, f"state-{project.int}")
    return module.ProjectRegistrationRequest(
        project, str(state), f"Project {project.int}", anchors=tuple(map(str, anchors))
    )


def test_monitor_registry_can_be_opened_without_creating_state(tmp_path):
    module = _module()
    missing = tmp_path / "monitor"
    assert module.Registry(missing).view().projects == ()
    assert not missing.exists()


def test_two_clones_share_identity_but_nested_foreign_anchor_fails(tmp_path):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    first = _directory(tmp_path, "first")
    clone = _directory(tmp_path, "clone")
    nested = _directory(clone, "nested")
    request = _request(module, tmp_path, anchors=(first, clone))
    other = _request(module, tmp_path, PROJECT_B, anchors=(nested,))
    with registry.writer() as writer:
        project = writer.register_project(request)
        renamed = writer.register_project(
            replace(request, display_name="Renamed", remote="new-origin")
        )
        assert project.project_id == renamed.project_id == PROJECT_A
        assert project.anchors == renamed.anchors and len(project.anchors) == 2
        with pytest.raises(ConflictError):
            writer.register_project(other)
        with pytest.raises(ConflictError):
            writer.register_project(replace(other, anchors=(str(tmp_path),)))
        alias = tmp_path / "alias"
        alias.symlink_to(clone, target_is_directory=True)
        with pytest.raises(ConflictError):
            writer.register_project(replace(other, anchors=(str(alias),)))
    assert registry.view().projects == (renamed,)


class _DesktopLog:
    def __init__(self, path, checkout, *, session=SESSION):
        self.path = path
        self.checkout = checkout
        self.session = session
        self.turns = 2
        rows, _ = _restart_rows("desktop", checkout)
        self.total = rows[-2]["payload"]["info"]["total_token_usage"]
        self._emit(rows, mode="w")

    def _emit(self, rows, *, mode):
        with self.path.open(mode, encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row).replace(str(SESSION), str(self.session)))
                stream.write("\n")

    def append(self, turns=1, *, complete=True):
        for _ in range(turns):
            self.turns += 1
            turn = UUID(int=0x200 + self.turns)
            time = AFTER + timedelta(seconds=self.turns)
            delta = usage(3, 2)
            self.total = usage(
                self.total["input_tokens"] + 3,
                self.total["output_tokens"] + 2,
                cache=self.total["cached_input_tokens"],
                reasoning=self.total["reasoning_output_tokens"],
            )
            self._emit(
                [
                    *begin(self.checkout, turn, time=time),
                    response(
                        f"response-{self.turns}",
                        self.total,
                        delta,
                        time=time,
                        turn=turn,
                    ),
                    counter(self.total, delta, time=time),
                    *([end(turn, time=time)] if complete else []),
                ],
                mode="a",
            )


def _native_fixture(tmp_path, monkeypatch, source, *, service=True):
    module = _module()
    _, reader, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    if service:
        with module.Registry(tmp_path / "monitor").writer() as writer:
            root = replace(root, evidence=writer.source_evidence())
    return module, reader, root, _DesktopLog(directory / "live.jsonl", checkout)


def _locate(reader, root, stream_ref=None):
    (locator,) = (
        item
        for item in reader.discover(root)
        if stream_ref is None or item.stream_ref == stream_ref
    )
    return locator


def _second_log(first_log, reader, root, first):
    log = _DesktopLog(
        root.path / "second.jsonl", first_log.checkout, session=UUID(int=999)
    )
    (locator,) = (
        item for item in reader.discover(root) if item.stream_ref != first.stream_ref
    )
    return log, locator


def _boundaries(reader, locator):
    return tuple(
        item.usage.boundary for item in reader.read_delta(locator, None).observations
    )


def _advance(writer, change, log, reader, root, stream_ref=None):
    frontier = writer.capture_frontier(change, _locate(reader, root, stream_ref))
    log.append()
    return writer.verify_boundary(change, _locate(reader, root, stream_ref), frontier)


def _approve(writer, module, root):
    return writer.approve_source(
        module.SourceApprovalRequest(
            SOURCE,
            "codex",
            "codex-desktop-macos",
            "Darwin",
            "arm64",
            "0.167.0-alpha.3.2",
            1,
            str(root.path),
        )
    )


def test_disable_reenable_excludes_late_disabled_interval(
    tmp_path, monkeypatch, source
):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    stream = _locate(reader, root).stream_ref
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)

    def decide(start, end):
        return registry.span_disposition(PROJECT_A, SOURCE, stream, start, end)

    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start = _advance(writer, enable, log, reader, root)
        first = writer.set_permission(enable, start)
        assert writer.set_permission(enable, start) == first
        with pytest.raises(LedgerError):
            writer.set_permission(enable, replace(start))
        with pytest.raises(LedgerError):
            writer.set_permission(enable, replace(start, ordinal=start.ordinal + 1))

        stop = _advance(writer, disable, log, reader, root)
        writer.set_permission(disable, stop)

        log.append(2)
        first_disabled, last_disabled = _boundaries(reader, _locate(reader, root))[-2:]
        reenable = writer.capture_frontier(enable, _locate(reader, root))
        with pytest.raises(module.BoundaryUnavailable):
            writer.verify_boundary(enable, _locate(reader, root), reenable)

        log.append(2)
        first_fresh, later_fresh = _boundaries(reader, _locate(reader, root))[-2:]
        restart = writer.verify_boundary(enable, _locate(reader, root), reenable)
        assert restart.boundary_ref == first_fresh.boundary_ref
        assert last_disabled.ordinal < restart.ordinal < later_fresh.ordinal
        writer.set_permission(enable, restart)
        with pytest.raises(LedgerError):
            writer.set_permission(enable, start)

    assert decide(start.ordinal, stop.ordinal) is Eligibility.ELIGIBLE
    assert decide(stop.ordinal, restart.ordinal) is Eligibility.EXCLUDED
    assert (
        decide(first_disabled.ordinal, last_disabled.ordinal + 1)
        is Eligibility.EXCLUDED
    )
    assert decide(stop.ordinal - 1, stop.ordinal + 1) is Eligibility.UNKNOWN
    assert decide(restart.ordinal, restart.ordinal + 1) is Eligibility.ELIGIBLE


def test_revoked_root_is_not_reread_for_prior_revision(tmp_path, monkeypatch, source):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start = _advance(writer, enable, log, reader, root)
        writer.set_permission(enable, start)
    locator = _locate(reader, root)
    assert registry.source_read_allowed(PROJECT_A, SOURCE)
    root.path.rename(root.path.with_name("moved-root"))
    root.path.mkdir()
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, locator.stream_ref, start.ordinal, start.ordinal + 1
        )
        is Eligibility.ELIGIBLE
    )

    def forbidden_read(*args, **kwargs):
        pytest.fail("The replaced native source was read")

    monkeypatch.setattr(type(reader), "read_delta", forbidden_read)
    with registry.writer() as writer, pytest.raises(LedgerError):
        writer.capture_frontier(enable, locator)


def test_shared_installation_keeps_project_permissions_independent(
    tmp_path, monkeypatch, source
):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    enable_a = module.CaptureChange(PROJECT_A, SOURCE, True)
    enable_b = replace(enable_a, project_id=PROJECT_B)
    disable_a = replace(enable_a, enabled=False)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        writer.register_project(_request(module, tmp_path, PROJECT_B))
        _approve(writer, module, root)
        locator = _locate(reader, root)
        front_a = writer.capture_frontier(enable_a, locator)
        front_b = writer.capture_frontier(enable_b, locator)
        log.append()
        locator = _locate(reader, root)
        start_a = writer.verify_boundary(enable_a, locator, front_a)
        start_b = writer.verify_boundary(enable_b, locator, front_b)
        assert start_a.boundary_ref == start_b.boundary_ref
        writer.set_permission(enable_a, start_a)
        writer.set_permission(enable_b, start_b)
        stop = _advance(writer, disable_a, log, reader, root)
        with pytest.raises(LedgerError):
            writer.set_permission(replace(disable_a, project_id=PROJECT_B), stop)
        writer.set_permission(disable_a, stop)
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    assert registry.source_read_allowed(PROJECT_B, SOURCE)


def test_destination_key_cannot_issue_a_native_capture_boundary(
    tmp_path, monkeypatch, source
):
    module, reader, root, _ = _native_fixture(
        tmp_path, monkeypatch, source, service=False
    )
    registry = module.Registry(tmp_path / "monitor")
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        with pytest.raises(LedgerError, match="monitor source namespace"):
            writer.capture_frontier(change, _locate(reader, root))


def test_adopted_path_and_key_are_pinned(tmp_path, monkeypatch):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    monkeypatch.setattr(module, "default_monitor_root", lambda: registry.root)
    monkeypatch.setattr(
        "aitm_usage.ledger._control_root", lambda: tmp_path / "legacy-guard"
    )
    request = _request(module, tmp_path)
    state = Path(request.state_dir)
    ledger = Ledger.initialize(state, PROJECT_A)
    with registry.writer() as writer:
        registered = writer.register_project(request)
        module.check_legacy_mutation(state)
        view = writer.view()
        writer._save(
            replace(
                view,
                projects=(replace(registered, adopted_key_id=ledger.identity.key_id),),
            )
        )
    with pytest.raises(module.ProjectAdopted):
        module.check_legacy_mutation(state)
    state.rename(state.with_name("moved-state"))
    os.mkdir(state, 0o700)
    with pytest.raises(LedgerError) as caught:
        module.check_legacy_mutation(state)
    assert not isinstance(caught.value, module.ProjectAdopted)


def test_lease_free_snapshot_read_survives_atomic_replacement(tmp_path, monkeypatch):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    request = _request(module, tmp_path)
    with registry.writer() as writer:
        old = writer.register_project(request)
        next_view = replace(writer.view(), projects=(replace(old, display_name="New"),))
        open_file = os.open

        def replace_after_open(path, *args, **kwargs):
            fd = open_file(path, *args, **kwargs)
            if path == module._STATE_FILE:
                writer._save(next_view)
            return fd

        with monkeypatch.context() as patch:
            patch.setattr(os, "open", replace_after_open)
            assert registry.view().projects == (old,)
        assert registry.view() == next_view


def _physical_ordinal(log):
    return log.path.read_bytes().count(b"\n")


class _QueuedDisable:
    def __init__(self, tmp_path, monkeypatch, source):
        from aitm_usage.monitor_control import ControlInbox

        self.module, self.reader, self.root, self.log = _native_fixture(
            tmp_path, monkeypatch, source
        )
        self.registry = self.module.Registry(tmp_path / "monitor")
        self.inbox = ControlInbox(self.registry.root)
        self.enable = self.module.CaptureChange(PROJECT_A, SOURCE, True)
        self.disable = replace(self.enable, enabled=False)
        self.command = self.module.ControlCommand(UUID(int=300), self.disable)
        self.stream = _locate(self.reader, self.root).stream_ref
        with self.registry.writer() as writer:
            writer.register_project(_request(self.module, tmp_path))
            _approve(writer, self.module, self.root)
            self.start = _advance(writer, self.enable, self.log, self.reader, self.root)
            writer.set_permission(self.enable, self.start)
        self.streams = {self.stream}

    def enroll_second(self):
        first = _locate(self.reader, self.root, self.stream)
        log, second = _second_log(self.log, self.reader, self.root, first)
        with self.registry.writer() as writer:
            proof = _advance(
                writer, self.enable, log, self.reader, self.root, second.stream_ref
            )
            writer.enroll_stream(PROJECT_A, SOURCE, proof)
        self.streams.add(second.stream_ref)
        return log, proof

    def locate(self, change, known):
        assert change == self.disable
        assert known == frozenset(self.streams)
        return tuple(self.reader.discover(self.root))

    def submit(self):
        return self.inbox.enqueue(self.command)

    def poll(self, locate=None, *, progress=()):
        registry = self.module.Registry(self.registry.root)
        with registry.writer() as writer:
            return writer.apply_pending(
                self.inbox,
                writer.lease,
                self.locate if locate is None else locate,
                progress=progress,
            )

    def status(self):
        return self.inbox.status(self.command.command_id).status

    def decide(self, stream, start, end):
        return self.registry.span_disposition(PROJECT_A, SOURCE, stream, start, end)


@pytest.fixture
def queued_disable(tmp_path, monkeypatch, source):
    return _QueuedDisable(tmp_path, monkeypatch, source)


@pytest.mark.parametrize("quiet", ["idle", "removed", "removed-after-arm"])
def test_source_wide_disable_reaches_a_quiet_stream_after_restart(
    queued_disable, quiet
):
    scenario = queued_disable
    second_log, second_start = scenario.enroll_second()
    second_prefix = _physical_ordinal(second_log)
    scenario.log.append(2)
    first_history_end = _physical_ordinal(scenario.log)
    with scenario.log.path.open("ab") as stream:
        stream.write(b"malformed physical row\n")
    first_fence = _physical_ordinal(scenario.log)
    first_bytes = scenario.log.path.stat().st_size
    second_log.append(2)
    second_fence = _physical_ordinal(second_log)
    if quiet == "removed":
        second_log.path.unlink()

    status = scenario.module.ControlStatus
    assert scenario.submit().status is status.QUEUED
    assert scenario.poll() == ()
    assert scenario.status() is status.QUEUED
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)

    # The first arm survives writer restart and additional rows on only one stream.
    scenario.log.append(2)
    if quiet == "removed-after-arm":
        second_log.path.unlink()
    bound = scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream)
    assert (bound.ordinal, bound.cursor.offset) == (first_fence, first_bytes)
    second_limit = second_prefix if quiet == "removed" else second_fence
    assert (
        scenario.registry.capture_read_limit(
            PROJECT_A, SOURCE, second_start.stream_ref
        ).ordinal
        == second_limit
    )
    (receipt,) = scenario.poll()
    assert receipt.status is status.APPLIED
    assert scenario.status() is status.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream).ordinal
        == 0
    )
    fences = {
        epoch.stream_ref: epoch.ordinal
        for epoch in scenario.registry.view().epochs
        if not epoch.enabled
    }
    assert fences[scenario.stream] == first_fence
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, first_history_end)
        is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(scenario.stream, first_fence, first_fence + 1)
        is Eligibility.EXCLUDED
    )

    second_stream = second_start.stream_ref
    end = second_prefix if quiet == "removed" else second_fence
    assert (
        scenario.decide(second_stream, second_start.ordinal, end)
        is Eligibility.ELIGIBLE
    )
    if quiet != "idle":
        assert scenario.decide(second_stream, end, end + 1) is Eligibility.UNKNOWN
    else:
        assert fences[second_stream] == second_fence
        assert scenario.decide(second_stream, end, end + 1) is Eligibility.EXCLUDED


def test_returning_original_stream_needs_prospective_enrollment(
    queued_disable, tmp_path
):
    scenario = queued_disable
    log, start = scenario.enroll_second()
    stream = start.stream_ref
    prefix = _physical_ordinal(log)
    log.append(2)
    stored = tmp_path / "temporarily-offline.jsonl"
    log.path.rename(stored)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED

    stored.rename(log.path)
    assert _locate(scenario.reader, scenario.root, stream).stream_ref == stream
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    repeated_disable = scenario.module.ControlCommand(UUID(int=199), scenario.disable)
    scenario.inbox.enqueue(repeated_disable)
    assert scenario.poll() == ()
    (repeat,) = scenario.poll()
    assert repeat.status is scenario.module.ControlStatus.APPLIED

    scenario.log.append()
    reenable = scenario.module.ControlCommand(UUID(int=200), scenario.enable)
    assert (
        scenario.inbox.enqueue(reenable).status is scenario.module.ControlStatus.QUEUED
    )

    def locate_enable(change, known):
        assert change == scenario.enable
        assert known == frozenset(scenario.streams)
        return (_locate(scenario.reader, scenario.root, scenario.stream),)

    assert scenario.poll(locate_enable) == ()
    (receipt,) = scenario.poll(locate_enable)
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.registry.capture_read_limit(PROJECT_A, SOURCE, stream).ordinal == 0
    assert scenario.decide(stream, prefix, prefix + 1) is Eligibility.UNKNOWN

    with scenario.registry.writer() as writer:
        fresh = _advance(
            writer, scenario.enable, log, scenario.reader, scenario.root, stream
        )
        writer.enroll_stream(PROJECT_A, SOURCE, fresh)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert scenario.decide(stream, prefix, fresh.ordinal) is Eligibility.UNKNOWN
    assert (
        scenario.decide(stream, fresh.ordinal, fresh.ordinal + 1)
        is Eligibility.ELIGIBLE
    )


@pytest.mark.parametrize("locators", ["omitted", "duplicate"])
def test_ambiguous_current_locator_keeps_existing_stream_queued(
    queued_disable, locators
):
    scenario = queued_disable
    second_log, _ = scenario.enroll_second()
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    admitted = scenario.registry.view().epochs

    def incomplete(change, known):
        candidates = scenario.locate(change, known)
        return candidates[:1] if locators == "omitted" else (*candidates, candidates[0])

    assert second_log.path.is_file()
    assert scenario.poll(incomplete) == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert scenario.registry.view().epochs == admitted
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED


def test_pending_disable_prevents_new_enrollment_and_ignores_unrelated_locator(
    queued_disable,
):
    scenario = queued_disable
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    new_log, second = _second_log(
        scenario.log,
        scenario.reader,
        scenario.root,
        _locate(scenario.reader, scenario.root, scenario.stream),
    )
    assert (
        scenario.registry.capture_read_limit(
            PROJECT_A, SOURCE, second.stream_ref
        ).ordinal
        == 0
    )
    with scenario.registry.writer() as writer:
        proof = _advance(
            writer,
            scenario.enable,
            new_log,
            scenario.reader,
            scenario.root,
            second.stream_ref,
        )
        with pytest.raises(ConflictError):
            writer.enroll_stream(PROJECT_A, SOURCE, proof)

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert {epoch.stream_ref for epoch in scenario.registry.view().epochs} == {
        scenario.stream
    }
    assert scenario.decide(second.stream_ref, proof.ordinal, proof.ordinal + 1) is (
        Eligibility.EXCLUDED
    )


@pytest.mark.parametrize("tail", ["open-turn", "partial", "completed-after-arm"])
def test_unfinished_codex_tail_fences_without_new_native_completion(
    queued_disable, tail
):
    scenario = queued_disable
    first_held = _physical_ordinal(scenario.log)
    if tail == "open-turn":
        scenario.log.append(complete=False)
        expected = _physical_ordinal(scenario.log)
    else:
        with scenario.log.path.open("ab") as stream:
            stream.write(b'{"type":"private-test"')
        expected = first_held + 1

    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    if tail == "completed-after-arm":
        with scenario.log.path.open("ab") as stream:
            stream.write(b"}\n")
        scenario.log.append()

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    (epoch,) = (epoch for epoch in scenario.registry.view().epochs if not epoch.enabled)
    assert epoch.ordinal == expected
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, first_held)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, first_held, expected) is Eligibility.UNKNOWN
    assert (
        scenario.decide(scenario.stream, first_held - 1, expected + 1)
        is Eligibility.UNKNOWN
    )
    assert (
        scenario.decide(scenario.stream, expected, expected + 1) is Eligibility.EXCLUDED
    )


def test_replay_syncs_existing_registry_receipt_before_retiring_queue(
    tmp_path, monkeypatch
):
    from aitm_usage.monitor_control import ControlInbox

    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    command = module.ControlCommand(UUID(int=301), _request(module, tmp_path))
    with registry.writer() as writer:
        inbox.enqueue(command)
        registry_identity = registry.root.stat()
        original_sync = os.fsync
        original_discard = inbox.discard
        synced = False

        def fail_after_replace(fd):
            if os.path.samestat(os.fstat(fd), registry_identity):
                raise OSError("injected registry directory sync failure")
            original_sync(fd)

        with monkeypatch.context() as patch:
            patch.setattr(os, "fsync", fail_after_replace)
            with pytest.raises(LedgerError, match="Private monitor publication failed"):
                writer.apply_pending(inbox, writer.lease, None)
        assert registry.view().receipts[0].status is module.ControlStatus.APPLIED

        def record_sync(fd):
            nonlocal synced
            original_sync(fd)
            if os.path.samestat(os.fstat(fd), registry_identity):
                synced = True

        def discard_after_sync(*args):
            assert synced
            return original_discard(*args)

        with monkeypatch.context() as patch:
            patch.setattr(os, "fsync", record_sync)
            patch.setattr(inbox, "discard", discard_after_sync)
            assert writer.apply_pending(inbox, writer.lease, None) == ()
    assert inbox.status(command.command_id).status is module.ControlStatus.APPLIED
    assert len(registry.view().projects) == 1


def test_new_stream_enrolls_only_while_source_permission_is_enabled(
    tmp_path, monkeypatch, source
):
    module, reader, root, first_log = _native_fixture(tmp_path, monkeypatch, source)
    first = _locate(reader, root)
    second_log, second = _second_log(first_log, reader, root, first)
    registry = module.Registry(tmp_path / "monitor")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        another = _advance(writer, enable, second_log, reader, root, second.stream_ref)
        with pytest.raises(ConflictError, match="disabled"):
            writer.enroll_stream(PROJECT_A, SOURCE, another)
        with pytest.raises(ConflictError, match="unadmitted"):
            wrong_stream = _advance(
                writer, disable, second_log, reader, root, second.stream_ref
            )
            writer.set_permission(disable, wrong_stream)
        start = _advance(writer, enable, first_log, reader, root, first.stream_ref)
        writer.set_permission(enable, start)
        assert (
            registry.span_disposition(
                PROJECT_A,
                SOURCE,
                second.stream_ref,
                another.ordinal,
                another.ordinal + 1,
            )
            is Eligibility.EXCLUDED
        )
        fresh = _advance(writer, enable, second_log, reader, root, second.stream_ref)
        epoch = writer.enroll_stream(PROJECT_A, SOURCE, fresh)
        assert writer.enroll_stream(PROJECT_A, SOURCE, fresh) == epoch
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, second.stream_ref, fresh.ordinal, fresh.ordinal + 1
        )
        is Eligibility.ELIGIBLE
    )


def test_historical_boundary_cannot_disable_previously_admitted_usage(
    tmp_path, monkeypatch, source
):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    stream = _locate(reader, root).stream_ref
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        early_frontier = writer.capture_frontier(enable, _locate(reader, root))
        log.append()
        start = writer.verify_boundary(enable, _locate(reader, root), early_frontier)
        writer.set_permission(enable, start)

        log.append(2)
        admitted, newest = _boundaries(reader, _locate(reader, root))[-2:]
        current_frontier = writer.capture_frontier(disable, _locate(reader, root))
        with pytest.raises(LedgerError):
            writer.verify_boundary(disable, _locate(reader, root), early_frontier)
        with pytest.raises(module.BoundaryUnavailable):
            writer.verify_boundary(disable, _locate(reader, root), current_frontier)

        log.append()
        stop = writer.verify_boundary(disable, _locate(reader, root), current_frontier)
        assert newest.ordinal < stop.ordinal
        writer.set_permission(disable, stop)

    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, stream, admitted.ordinal, stop.ordinal
        )
        is Eligibility.ELIGIBLE
    )


@pytest.mark.parametrize("failure", ["io", "proof"])
def test_transient_native_read_failure_leaves_capture_command_queued(
    tmp_path, monkeypatch, source, failure
):
    from aitm_usage.monitor_control import ControlInbox

    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    command = module.ControlCommand(UUID(int=303), disable)

    def unavailable(_change, _known):
        if failure == "io":
            raise OSError("native file is temporarily unavailable")
        raise module.BoundaryUnavailable("native boundary is temporarily unavailable")

    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        writer.set_permission(enable, _advance(writer, enable, log, reader, root))
        inbox.enqueue(command)
        assert writer.apply_pending(inbox, writer.lease, unavailable) == ()
    assert inbox.status(command.command_id).status is module.ControlStatus.QUEUED
    assert registry.source_read_allowed(PROJECT_A, SOURCE)


def test_capture_frontier_waits_for_complete_native_tail(tmp_path, monkeypatch, source):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        complete_size = log.path.stat().st_size
        with log.path.open("ab") as stream:
            stream.write(b'{"type":"event_msg"')
        with pytest.raises(module.BoundaryUnavailable):
            writer.capture_frontier(enable, _locate(reader, root))
        with log.path.open("r+b") as stream:
            stream.truncate(complete_size)
        proof = _advance(writer, enable, log, reader, root)
        assert writer.set_permission(enable, proof).enabled


def test_rearming_a_capture_change_invalidates_earlier_native_proof(
    tmp_path, monkeypatch, source
):
    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        old_proof = _advance(writer, change, log, reader, root)
        log.append()
        current = writer.capture_frontier(change, _locate(reader, root))
        with pytest.raises(LedgerError):
            writer.set_permission(change, old_proof)
        with pytest.raises(LedgerError):
            writer.verify_boundary(change, _locate(reader, root), replace(current))
        with pytest.raises(module.BoundaryUnavailable):
            writer.verify_boundary(change, _locate(reader, root), current)

        log.append()
        fresh = writer.verify_boundary(change, _locate(reader, root), current)
        assert fresh.ordinal > old_proof.ordinal
        assert writer.set_permission(change, fresh).enabled


@pytest.mark.parametrize(
    "interruption", ["root-replacement", "platform", "native-version", "truncated"]
)
def test_disable_commits_with_last_verified_prefix_when_source_changes(
    queued_disable, monkeypatch, interruption
):
    scenario = queued_disable
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append(2)
    original = scenario.log.path.read_bytes()
    locator = _locate(scenario.reader, scenario.root)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED

    def locate(_change, known):
        assert known == frozenset({scenario.stream})
        return (locator,)

    with monkeypatch.context() as patch:
        if interruption == "root-replacement":
            path = scenario.root.path
            moved = path.with_name("original-approved-root")
            path.rename(moved)
            path.mkdir()
            scenario.log.path.write_bytes(original)

            def unexpected_discovery(*args):
                pytest.fail("The replacement root was read")

            patch.setattr(type(scenario.reader), "discover", unexpected_discovery)
        elif interruption == "platform":
            patch.setattr(scenario.module.platform, "machine", lambda: "unsupported")
        elif interruption == "native-version":
            changed = original.replace(b"0.167.0-alpha.3.2", b"0.167.0-alpha.3.9", 1)
            assert changed != original
            scenario.log.path.write_bytes(changed)
        else:
            scenario.log.path.write_bytes(b"")

        applied = scenario.poll(locate)
        if not applied:
            applied = scenario.poll(locate)
        (receipt,) = applied
        assert receipt.status is scenario.module.ControlStatus.APPLIED
        assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)

    if interruption == "root-replacement":
        scenario.log.path.unlink()
        path.rmdir()
        moved.rename(path)
    if interruption in {"truncated", "native-version"}:
        scenario.log.path.write_bytes(original)

    assert scenario.status() is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


def test_armed_prefix_mutation_gaps_only_the_unverified_tail(queued_disable):
    scenario = queued_disable
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append(2)
    before = scenario.log.path.read_bytes()
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()

    # Preserve inode, size, native startup, and session while changing bytes
    # covered by the persisted physical arm.
    after = before.replace(b"response-4", b"modified-4", 1)
    assert after != before and len(after) == len(before)
    scenario.log.path.write_bytes(after)
    (receipt,) = scenario.poll()

    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


@pytest.mark.parametrize("unfinished", ["quiet", "streamed", "tool", "abandoned"])
def test_queued_claude_disable_uses_the_physical_tail(
    tmp_path, monkeypatch, source, unfinished
):
    from test_claude import request as claude_request
    from test_claude import user as claude_user
    from test_claude import write as write_claude

    from aitm_usage.monitor_control import ControlInbox

    module = _module()
    _, reader, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    path = directory / "claude.jsonl"
    rows, _ = _restart_rows("streamed", checkout)
    write_claude(path, rows[:1])
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    command = module.ControlCommand(UUID(int=330), disable)

    def append_request(turn, *, stop, content=()):
        prompt = str(UUID(int=500 + 2 * turn))
        reply = str(UUID(int=501 + 2 * turn))
        time = AFTER + timedelta(seconds=10 + turn)
        write_claude(
            path,
            [
                claude_user(checkout, time=time, uuid=prompt, isSidechain=False),
                claude_request(
                    checkout,
                    time=time,
                    uuid=reply,
                    parentUuid=prompt,
                    req=f"test-request-{turn}",
                    msg=f"test-message-{turn}",
                    stop=stop,
                    content=content,
                    isSidechain=False,
                ),
            ],
            append=True,
        )

    def locate(change, known):
        assert change in (disable, enable)
        assert known == frozenset({start.stream_ref})
        return tuple(reader.discover(root))

    with registry.writer() as writer:
        root = replace(root, evidence=writer.source_evidence())
        writer.register_project(_request(module, tmp_path))
        writer.approve_source(
            module.SourceApprovalRequest(
                SOURCE,
                "claude",
                "claude-code-macos",
                "Darwin",
                "arm64",
                "2.1.318",
                1,
                str(root.path),
            )
        )
        frontier = writer.capture_frontier(enable, _locate(reader, root))
        write_claude(path, rows[1:], append=True)
        start = writer.verify_boundary(enable, _locate(reader, root), frontier)
        writer.set_permission(enable, start)
        append_request(2, stop="end_turn")
        admitted_end = path.read_bytes().count(b"\n")
        if unfinished in {"streamed", "abandoned"}:
            append_request(3, stop=None)
        if unfinished == "abandoned":
            completed_start = path.read_bytes().count(b"\n")
            append_request(4, stop="end_turn")
            append_request(5, stop="end_turn")
        if unfinished == "tool":
            append_request(
                3,
                stop="tool_use",
                content=[
                    {
                        "type": "tool_use",
                        "id": "agent-open",
                        "name": "Agent",
                        "input": {},
                    }
                ],
            )
        expected = path.read_bytes().count(b"\n")
        assert inbox.enqueue(command).status is module.ControlStatus.QUEUED
        assert writer.apply_pending(inbox, writer.lease, locate) == ()

    with registry.writer() as writer:
        (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert receipt.status is module.ControlStatus.APPLIED
    assert registry.view().epochs[-1].ordinal == expected
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, start.stream_ref, start.ordinal, admitted_end
        )
        is Eligibility.ELIGIBLE
    )
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, start.stream_ref, expected, expected + 1
        )
        is Eligibility.EXCLUDED
    )
    if unfinished in {"streamed", "tool"}:
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, admitted_end + 1, expected
            )
            is Eligibility.UNKNOWN
        )
    if unfinished == "abandoned":
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, completed_start, expected
            )
            is Eligibility.ELIGIBLE
        )
        append_request(6, stop="end_turn")
        append_request(7, stop=None)
        enabled_at = path.read_bytes().count(b"\n")
        resume = module.ControlCommand(UUID(int=331), enable)
        assert inbox.enqueue(resume).status is module.ControlStatus.QUEUED
        with registry.writer() as writer:
            assert writer.apply_pending(inbox, writer.lease, lambda *_: ()) == ()
        assert inbox.status(resume.command_id).status is module.ControlStatus.QUEUED
        with registry.writer() as writer:
            assert writer.apply_pending(inbox, writer.lease, locate) == ()
        with registry.writer() as writer:
            (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
        assert (receipt.command_id, receipt.status) == (
            resume.command_id,
            module.ControlStatus.APPLIED,
        )
        assert registry.view().epochs[-1].ordinal == enabled_at
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, completed_start, expected
            )
            is Eligibility.ELIGIBLE
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, expected, enabled_at
            )
            is Eligibility.EXCLUDED
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, enabled_at, enabled_at + 1
            )
            is Eligibility.ELIGIBLE
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, enabled_at - 1, enabled_at + 1
            )
            is Eligibility.UNKNOWN
        )


def test_reappearing_stream_invalidates_an_earlier_absence(queued_disable, tmp_path):
    scenario = queued_disable
    log, start = scenario.enroll_second()
    prefix = _physical_ordinal(log)
    log.append()
    returned_fence = _physical_ordinal(log)
    stored = tmp_path / "briefly-offline.jsonl"
    log.path.rename(stored)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()

    stored.rename(log.path)
    assert scenario.poll() == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert (
        scenario.registry.capture_read_limit(
            PROJECT_A, SOURCE, start.stream_ref
        ).ordinal
        == returned_fence
    )

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert (
        scenario.decide(start.stream_ref, start.ordinal, prefix) is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(start.stream_ref, prefix, returned_fence) is Eligibility.UNKNOWN
    )
    assert (
        scenario.decide(start.stream_ref, returned_fence, returned_fence + 1)
        is Eligibility.EXCLUDED
    )


def test_native_parser_valueerror_keeps_disable_queued_with_prior_read_bound(
    queued_disable, monkeypatch
):
    scenario = queued_disable
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append()
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED

    def failed_parse(*args, **kwargs):
        raise ValueError("native parse is temporarily unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(type(scenario.reader), "_capture_gap_start", failed_parse)
        assert scenario.poll() == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert (
        scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream).ordinal
        == prefix
    )

    scenario.log.append()
    late_fence = _physical_ordinal(scenario.log)
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert scenario.decide(scenario.stream, prefix, late_fence) is Eligibility.UNKNOWN
    assert (
        scenario.decide(scenario.stream, late_fence, late_fence + 1)
        is Eligibility.EXCLUDED
    )


def test_later_enable_obeys_durable_submission_order(queued_disable):
    scenario = queued_disable
    disable_fence = _physical_ordinal(scenario.log)
    reenable = scenario.module.ControlCommand(UUID(int=200), scenario.enable)
    status = scenario.module.ControlStatus
    assert scenario.submit().status is status.QUEUED
    assert scenario.inbox.enqueue(reenable).status is status.QUEUED

    def locate(change, known):
        assert change in (scenario.disable, scenario.enable)
        assert known == frozenset({scenario.stream})
        return tuple(scenario.reader.discover(scenario.root))

    assert scenario.poll(locate) == ()
    scenario.log.append()
    enable_fence = _physical_ordinal(scenario.log)
    (first,) = scenario.poll(locate)
    assert (first.command_id, first.status) == (
        scenario.command.command_id,
        status.APPLIED,
    )
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.inbox.status(reenable.command_id).status is status.QUEUED

    applied = scenario.poll(locate)
    if not applied:
        applied = scenario.poll(locate)
    (second,) = applied
    assert (second.command_id, second.status) == (reenable.command_id, status.APPLIED)
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, disable_fence, enable_fence)
        is Eligibility.EXCLUDED
    )
    assert (
        scenario.decide(scenario.stream, enable_fence, enable_fence + 1)
        is Eligibility.ELIGIBLE
    )


def test_persisted_collection_progress_survives_a_later_truncation(queued_disable):
    scenario = queued_disable
    scenario.log.append()
    retained = scenario.log.path.read_bytes()
    scenario.log.append(2)
    locator = _locate(scenario.reader, scenario.root, scenario.stream)
    checkpoint = scenario.reader.read_delta(locator, None).cursor.checkpoint
    with scenario.registry.writer() as writer:
        progress = writer.capture_progress(scenario.enable, locator, checkpoint)
    assert progress.ordinal == _physical_ordinal(scenario.log)
    scenario.log.path.write_bytes(retained)

    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    forged = replace(progress, ordinal=progress.ordinal + 1)
    assert scenario.poll(progress=(forged,)) == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert scenario.poll(progress=(progress,)) == ()
    bound = scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream)
    assert (bound.ordinal, bound.cursor) == (progress.ordinal, progress.cursor)

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, progress.ordinal)
        is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(scenario.stream, progress.ordinal, progress.ordinal + 1)
        is Eligibility.UNKNOWN
    )


def test_capture_disable_detects_an_in_place_native_session_replacement(queued_disable):
    scenario = queued_disable
    prefix = _physical_ordinal(scenario.log)
    original = scenario.log.path.read_bytes()
    rewritten = original.replace(str(SESSION).encode(), str(UUID(int=999)).encode())
    assert len(rewritten) == len(original) and rewritten != original
    scenario.log.path.write_bytes(rewritten)
    assert _locate(scenario.reader, scenario.root).stream_ref != scenario.stream

    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


def test_disable_future_enrollment_while_approved_root_is_unavailable(
    queued_disable, tmp_path
):
    scenario = queued_disable
    other = _request(scenario.module, tmp_path, PROJECT_B)
    enable = replace(scenario.enable, project_id=PROJECT_B)
    disable = replace(enable, enabled=False)
    scenario.inbox.enqueue(scenario.module.ControlCommand(UUID(int=401), other))
    scenario.inbox.enqueue(scenario.module.ControlCommand(UUID(int=402), enable))
    with scenario.registry.writer() as writer:
        assert len(writer.apply_pending(scenario.inbox, writer.lease, None)) == 2
    assert scenario.registry.source_read_allowed(PROJECT_B, SOURCE)
    displaced = tmp_path / "temporarily-unavailable"
    scenario.root.path.rename(displaced)
    scenario.inbox.enqueue(scenario.module.ControlCommand(UUID(int=403), disable))
    with scenario.registry.writer() as writer:
        (receipt,) = writer.apply_pending(scenario.inbox, writer.lease, None)
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    displaced.rename(scenario.root.path)
    assert not scenario.registry.source_read_allowed(PROJECT_B, SOURCE)


@pytest.mark.parametrize("callback", ["supplied", "omitted"])
@pytest.mark.parametrize("timing", ["before-arm", "after-arm"])
@pytest.mark.parametrize("reuse_name", [False, True], ids=["vacant", "occupied"])
def test_moved_enrolled_stream_does_not_stall_disable(
    queued_disable, callback, timing, reuse_name
):
    scenario = queued_disable
    log, start = scenario.enroll_second()
    prefix = _physical_ordinal(log)
    stream = start.stream_ref
    scenario.log.append(2)
    log.append(2)
    healthy_fence = _physical_ordinal(scenario.log)
    archive = scenario.root.path / "archive"
    archive.mkdir()
    old_path = log.path
    original = old_path.stat()

    def archive_stream():
        log.path = old_path.rename(archive / old_path.name)
        assert os.path.samestat(log.path.stat(), original)
        if reuse_name:
            replacement = _DesktopLog(old_path, log.checkout, session=UUID(int=1000))
            assert not os.path.samestat(replacement.path.stat(), original)
        assert _locate(scenario.reader, scenario.root, stream)._source._path == log.path

    def locate(change, known):
        assert change in (scenario.disable, scenario.enable)
        assert known == frozenset(scenario.streams)
        candidates = tuple(scenario.reader.discover(scenario.root))
        if callback == "supplied":
            return candidates
        return tuple(item for item in candidates if item.stream_ref != stream)

    if timing == "before-arm":
        archive_stream()
    status = scenario.module.ControlStatus
    assert scenario.submit().status is status.QUEUED
    if timing == "after-arm":
        assert scenario.poll() == ()
        archive_stream()
    else:
        assert scenario.poll(locate) == ()
    assert scenario.status() is status.QUEUED
    (disabled,) = scenario.poll(locate)
    assert disabled.status is status.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert scenario.decide(stream, prefix, prefix + 1) is Eligibility.UNKNOWN

    scenario.log.append()
    enabled_at = _physical_ordinal(scenario.log)
    resume = scenario.module.ControlCommand(UUID(int=322), scenario.enable)
    assert scenario.inbox.enqueue(resume).status is status.QUEUED
    assert scenario.poll(locate) == ()
    (enabled,) = scenario.poll(locate)
    assert (enabled.command_id, enabled.status) == (resume.command_id, status.APPLIED)
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.registry.capture_read_limit(PROJECT_A, SOURCE, stream).ordinal == 0
    assert scenario.decide(scenario.stream, healthy_fence, enabled_at) is (
        Eligibility.EXCLUDED
    )
    assert scenario.decide(scenario.stream, enabled_at, enabled_at + 1) is (
        Eligibility.ELIGIBLE
    )

    with scenario.registry.writer() as writer, pytest.raises(LedgerError):
        moved_proof = _advance(
            writer, scenario.enable, log, scenario.reader, scenario.root, stream
        )
        writer.enroll_stream(PROJECT_A, SOURCE, moved_proof)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert (
        scenario.decide(stream, prefix, _physical_ordinal(log)) is Eligibility.UNKNOWN
    )
