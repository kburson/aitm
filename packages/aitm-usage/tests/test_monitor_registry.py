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

    def append(self, turns=1):
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
                    end(turn, time=time),
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


def test_source_wide_change_waits_for_native_stream_boundaries_across_restart(
    tmp_path, monkeypatch, source
):
    from aitm_usage.monitor_control import ControlInbox

    module, reader, root, first_log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    command = module.ControlCommand(UUID(int=300), disable)
    first = _locate(reader, root)
    second_log, second = _second_log(first_log, reader, root, first)
    streams = frozenset({first.stream_ref, second.stream_ref})

    def locate(change, known_streams):
        assert change == disable
        assert known_streams == streams
        return tuple(reader.discover(root))

    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start = _advance(writer, enable, first_log, reader, root, first.stream_ref)
        writer.set_permission(enable, start)
        second_start = _advance(
            writer, enable, second_log, reader, root, second.stream_ref
        )
        writer.enroll_stream(PROJECT_A, SOURCE, second_start)
        admitted_epochs = writer.view().epochs
        first_log.append(2)
        second_log.append(2)
        assert inbox.enqueue(command).status is module.ControlStatus.QUEUED
        assert writer.apply_pending(inbox, writer.lease, None) == ()
        assert writer.apply_pending(inbox, writer.lease, locate) == ()

    registry = module.Registry(registry.root)
    first_log.append(2)
    first_fresh, first_later = _boundaries(
        reader, _locate(reader, root, first.stream_ref)
    )[-2:]
    with registry.writer() as writer:
        assert writer.apply_pending(inbox, writer.lease, locate) == ()
    assert inbox.status(command.command_id).status is module.ControlStatus.QUEUED
    assert registry.source_read_allowed(PROJECT_A, SOURCE)
    assert registry.view().epochs == admitted_epochs

    second_log.append(2)
    second_fresh, second_later = _boundaries(
        reader, _locate(reader, root, second.stream_ref)
    )[-2:]
    with registry.writer() as writer:
        (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert receipt.status is module.ControlStatus.APPLIED
    assert inbox.status(command.command_id) == receipt
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    fences = {
        epoch.stream_ref: epoch.boundary_ref
        for epoch in registry.view().epochs
        if not epoch.enabled
    }
    assert fences == {
        first.stream_ref: first_fresh.boundary_ref,
        second.stream_ref: second_fresh.boundary_ref,
    }
    for stream, began, stopped, later in (
        (first.stream_ref, start, first_fresh, first_later),
        (second.stream_ref, second_start, second_fresh, second_later),
    ):
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, stream, began.ordinal, stopped.ordinal
            )
            is Eligibility.ELIGIBLE
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, stream, stopped.ordinal, later.ordinal
            )
            is Eligibility.EXCLUDED
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
