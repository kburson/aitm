"""Private registry identity, native capture epochs and command custody."""

import os
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from uuid import UUID

import pytest
from test_codex import AFTER, SESSION, begin, counter, end, response, usage
from test_monitor_adapters import _adapter, _restart_rows, _write
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


def _native_fixture(tmp_path, monkeypatch, source, *, service=True):
    module = _module()
    _, reader, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    if service:
        with module.Registry(tmp_path / "monitor").writer() as writer:
            root = replace(root, evidence=writer.source_evidence())
    rows, _ = _restart_rows("desktop", checkout)
    turn = UUID(int=0x200)
    time = AFTER + timedelta(seconds=2)
    previous = rows[-2]["payload"]["info"]["total_token_usage"]
    delta = usage(3, 2)
    total = usage(
        previous["input_tokens"] + 3,
        previous["output_tokens"] + 2,
        cache=previous["cached_input_tokens"],
        reasoning=previous["reasoning_output_tokens"],
    )
    rows.extend(
        [
            *begin(checkout, turn, time=time),
            response("third-response", total, delta, time=time, turn=turn),
            counter(total, delta, time=time),
            end(turn, time=time),
        ]
    )
    _write(directory / "live.jsonl", rows)
    (locator,) = reader.discover(root)
    batch = reader.read_delta(locator, None)
    boundaries = tuple(item.usage.boundary for item in batch.observations)
    assert len(boundaries) == 3
    return module, reader, root, locator, boundaries


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


def _proofs(writer, locator, boundaries):
    return tuple(
        writer.verify_boundary(SOURCE, locator, item.boundary_ref)
        for item in boundaries
    )


def test_disable_reenable_excludes_late_disabled_interval(
    tmp_path, monkeypatch, source
):
    module, reader, root, locator, native = _native_fixture(
        tmp_path, monkeypatch, source
    )
    registry = module.Registry(tmp_path / "monitor")
    request = _request(module, tmp_path)
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        writer.register_project(request)
        _approve(writer, module, root)
        start, stop, restart = _proofs(writer, locator, native)
        first = writer.set_permission(change, start)
        assert writer.set_permission(change, start) == first
        with pytest.raises(LedgerError):
            writer.set_permission(change, replace(start))
        with pytest.raises(LedgerError):
            writer.set_permission(change, replace(start, ordinal=stop.ordinal))
        writer.set_permission(replace(change, enabled=False), stop)
        writer.set_permission(change, restart)
        with pytest.raises(ConflictError):
            writer.set_permission(replace(change, enabled=False), start)

    def decide(start, end):
        return registry.span_disposition(
            PROJECT_A, SOURCE, locator.stream_ref, start, end
        )

    assert decide(start.ordinal, stop.ordinal) is Eligibility.ELIGIBLE
    assert decide(stop.ordinal, restart.ordinal) is Eligibility.EXCLUDED
    assert decide(stop.ordinal - 1, stop.ordinal + 1) is Eligibility.UNKNOWN
    assert decide(restart.ordinal, restart.ordinal + 1) is Eligibility.ELIGIBLE


def test_revoked_root_is_not_reread_for_prior_revision(tmp_path, monkeypatch, source):
    module, reader, root, locator, native = _native_fixture(
        tmp_path, monkeypatch, source
    )
    registry = module.Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start, stop, _ = _proofs(writer, locator, native)
        writer.set_permission(module.CaptureChange(PROJECT_A, SOURCE, True), start)
    assert registry.source_read_allowed(PROJECT_A, SOURCE)
    root.path.rename(root.path.with_name("moved-root"))
    root.path.mkdir()
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, locator.stream_ref, start.ordinal, stop.ordinal
        )
        is Eligibility.ELIGIBLE
    )
    with registry.writer() as writer, pytest.raises(LedgerError):
        writer.verify_boundary(SOURCE, locator, native[1].boundary_ref)


def test_shared_installation_keeps_project_permissions_independent(
    tmp_path, monkeypatch, source
):
    module, reader, root, locator, native = _native_fixture(
        tmp_path, monkeypatch, source
    )
    registry = module.Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        writer.register_project(_request(module, tmp_path, PROJECT_B))
        _approve(writer, module, root)
        start, stop, _ = _proofs(writer, locator, native)
        writer.set_permission(module.CaptureChange(PROJECT_A, SOURCE, True), start)
        writer.set_permission(module.CaptureChange(PROJECT_B, SOURCE, True), start)
        writer.set_permission(module.CaptureChange(PROJECT_A, SOURCE, False), stop)
        with pytest.raises(LedgerError):
            writer.set_permission(
                module.CaptureChange(PROJECT_B, SOURCE, False), native[1]
            )
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    assert registry.source_read_allowed(PROJECT_B, SOURCE)


def test_destination_key_cannot_issue_a_native_capture_boundary(
    tmp_path, monkeypatch, source
):
    module, reader, root, locator, native = _native_fixture(
        tmp_path, monkeypatch, source, service=False
    )
    registry = module.Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        _approve(writer, module, root)
        with pytest.raises(LedgerError):
            writer.verify_boundary(SOURCE, locator, native[0].boundary_ref)


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


def test_source_wide_change_waits_for_native_stream_boundary(
    tmp_path, monkeypatch, source
):
    from aitm_usage.monitor_control import ControlInbox

    module, reader, root, locator, native = _native_fixture(
        tmp_path, monkeypatch, source
    )
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    command = module.ControlCommand(UUID(int=300), disable)
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start, stop, _ = _proofs(writer, locator, native)
        writer.set_permission(enable, start)
        assert inbox.enqueue(command).status is module.ControlStatus.QUEUED
        assert writer.apply_pending(inbox, writer.lease, None) == ()
        assert inbox.status(command.command_id).status is module.ControlStatus.QUEUED
        assert registry.source_read_allowed(PROJECT_A, SOURCE)
        (receipt,) = writer.apply_pending(inbox, writer.lease, lambda _: (stop,))
        assert receipt.status is module.ControlStatus.APPLIED
    assert inbox.status(command.command_id) == receipt
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)


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
    module, reader, root, first, native = _native_fixture(tmp_path, monkeypatch, source)
    second_path = root.path / "second.jsonl"
    second_path.write_bytes(
        (root.path / "live.jsonl")
        .read_bytes()
        .replace(str(SESSION).encode(), str(UUID(int=999)).encode())
    )
    second = next(
        locator
        for locator in reader.discover(root)
        if locator.stream_ref != first.stream_ref
    )
    boundary = reader.read_delta(second, None).observations[0].usage.boundary
    registry = module.Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        writer.register_project(_request(module, tmp_path))
        _approve(writer, module, root)
        start = writer.verify_boundary(SOURCE, first, native[0].boundary_ref)
        another = writer.verify_boundary(SOURCE, second, boundary.boundary_ref)
        with pytest.raises(ConflictError, match="disabled"):
            writer.enroll_stream(PROJECT_A, SOURCE, another)
        writer.set_permission(module.CaptureChange(PROJECT_A, SOURCE, True), start)
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
        epoch = writer.enroll_stream(PROJECT_A, SOURCE, another)
        assert writer.enroll_stream(PROJECT_A, SOURCE, another) == epoch
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, second.stream_ref, another.ordinal, another.ordinal + 1
        )
        is Eligibility.ELIGIBLE
    )
