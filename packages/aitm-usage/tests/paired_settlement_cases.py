"""Run paired settlement against pinned transcript bytes and a transaction spy."""

import json
import os
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from adapter_frame_cases import AdapterFrames
from scanner_policy_cases import scanner
from test_codex import CUTOFF, SESSION
from test_monitor_scope import _completion_policy_input, _damage_completion_rows

from aitm_usage import monitor_journal, monitor_scope
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.scopes import session_reference
from aitm_usage.sources import codex
from aitm_usage.sources.adapter import (
    NativeBoundary,
    SourceLocator,
    SourceRoot,
    StreamCursor,
)
from aitm_usage.types import (
    ClientVersion,
    Eligibility,
    ItemKey,
    ItemKind,
    Provider,
    SourceCheckpoint,
)


def _bytes(rows):
    return b"".join((json.dumps(row) + "\n").encode() for row in rows)


def _capture_inputs(monkeypatch, contents):
    """Substitute filesystem reads while retaining native prefix authentication."""
    identity = ((1, 2), (1, 3))

    descriptors = {}

    class Descriptor(BytesIO):
        def fileno(self):
            return id(self)

    def pread(descriptor, size, offset):
        return descriptors[descriptor][offset : offset + size]

    monkeypatch.setattr(
        scanner, "os", SimpleNamespace(pread=pread, fsencode=os.fsencode)
    )

    def snapshot_for(path):
        snapshot = Mock(
            identity=identity, stat=SimpleNamespace(st_size=len(contents[path]))
        )
        snapshot.same_path.return_value = True
        return snapshot

    @contextmanager
    def open_snapshot(path, *, identity_prefix):
        assert identity_prefix == identity
        with Descriptor(contents[path]) as descriptor:
            handle = descriptor.fileno()
            descriptors[handle] = contents[path]
            try:
                yield descriptor, snapshot_for(path)
            finally:
                del descriptors[handle]

    monkeypatch.setattr(scanner, "_open_snapshot", open_snapshot)
    monkeypatch.setattr(scanner, "_reprobe", snapshot_for)
    monkeypatch.setattr(scanner, "_verify_snapshot", Mock())
    return identity


def _read_completion(fixture, rows, stream, checkout):
    frames = fixture.batch(rows)
    evidence = fixture.ledger
    shared_frames = tuple(
        replace(row, stream_ref=stream, anchor_ref=checkout) for row in frames.frames
    )
    frames = replace(
        frames,
        frames=shared_frames,
        commit_frames=shared_frames,
        cursor=replace(frames.cursor, source_ref=stream),
    )
    witnesses = []
    result, *_ = codex._read_codex(
        frames,
        codex.CodexState(evidence, neutral_markers=True),
        Eligibility.ELIGIBLE,
        _completion_witnesses=witnesses,
    )
    return result, witnesses


def _build_side(project, session, registry, contents, identity, monkeypatch):
    rows, when, turn, total = _completion_policy_input()
    seed_command = UUID(int=0x902)
    command_id = UUID(int=seed_command.int + project.int - 1)
    rows = json.loads(
        json.dumps(rows)
        .replace(str(SESSION), str(session))
        .replace(str(seed_command), str(command_id))
    )
    fixture = AdapterFrames(
        Provider.CODEX, ClientVersion.CODEX_0_167_0_ALPHA_3_2, session, CUTOFF
    )
    evidence = fixture.ledger
    session_ref = session_reference(evidence, Provider.CODEX, str(session))
    stream = evidence.pseudonymize("codex-stream", session_ref.value)
    checkout = evidence.pseudonymize("fixture", str(project))
    result, witnesses = _read_completion(fixture, rows, stream, checkout)
    (witness,) = witnesses
    hold_id = UUID(int=0x800 + project.int)
    command = monitor_scope.Disposition(
        command_id, project, hold_id, witness.request.receipt_ref, True
    )
    target = NativeBoundary(witness.request, checkout)
    origin = Path("/fixture/transcripts")
    path = origin / f"{project}.jsonl"
    root = SourceRoot(origin, CUTOFF, (), evidence)
    source = scanner.CandidateSource(
        Provider.CODEX,
        target.boundary.session_ref,
        stream,
        scanner._locator_reference(evidence, path),
        scanner._incarnation_reference(evidence, identity[-1]),
        path,
        identity,
        root,
        evidence,
        _native_surface=NativeSurface.CODEX_DESKTOP_MACOS,
        _monitor=True,
    )

    contents[path] = _bytes(rows[:5])
    fixed_hold = scanner._capture_position(source, None).cursor
    contents[path] = _bytes(rows)
    fixed_batch = scanner._capture_position(source, None).cursor
    position = monitor_scope.ScopePosition(
        project, source._native_surface, source.session_ref, stream, 4
    )
    hold_boundary = replace(
        target.boundary,
        ordinal=4,
        receipt_ref=evidence.pseudonymize("scope-receipt", str(hold_id)),
    )
    hold = monitor_scope.ProofHold(
        hold_id,
        "a" * 64,
        project,
        position,
        monitor_scope.AffectedScope(4, 5),
        when - timedelta(minutes=1),
        when + timedelta(minutes=14),
    )
    event = monitor_scope._ScopeEvent(
        UUID(int=project.int + 40),
        "b" * 64,
        monitor_scope.Scope(project),
        replace(position, ordinal=1),
        checkout,
        project,
        True,
        monitor_scope.AffectedScope(1, 2),
        None,
    )
    held_target = monitor_scope._HeldRouteTarget(hold_id, hold_boundary, fixed_hold)
    cursor = StreamCursor(SourceCheckpoint(fixed_batch, witness._checkpoint))
    batch = monitor_scope.VerifiedScopeBatch(
        project,
        source._native_surface,
        (),
        (NativeBoundary(hold_boundary, checkout), target),
        result.diagnostics,
        cursor,
        (),
        frozenset({project}),
        SourceLocator(source),
        fixed_batch,
        None,
        None,
        _completion_witnesses=tuple(witnesses),
        _completion_progress=monitor_scope._CompletionProgress(cursor, ()),
    )
    issuer = monitor_scope.ScopeState(registry, clock=lambda: when)
    monkeypatch.setattr(issuer, "_require_authority", Mock())
    monkeypatch.setattr(
        issuer,
        "_require_batch_qualification",
        Mock(return_value=SimpleNamespace(directory=origin)),
    )
    monkeypatch.setattr(
        issuer, "_anchor", lambda view, ref: project if ref == checkout else None
    )
    monkeypatch.setattr(issuer, "_eligible", lambda admitted, position, end: admitted)
    authority = monitor_scope.ScopeAuthority(project, evidence.key_id)
    issuer._authorized[command.command_id] = (monitor_scope._digest(command), authority)

    return SimpleNamespace(
        rows=rows,
        fixture=fixture,
        when=when,
        turn=turn,
        total=total,
        path=path,
        event=event,
        hold=hold,
        held_target=held_target,
        issuer=issuer,
        command=command,
        authority=authority,
        batch=batch,
        target=target,
        request=monitor_scope._TypedDisposition("c" * 64, project),
    )


def _issued_pair(monkeypatch):
    contents = {}
    identity = _capture_inputs(monkeypatch, contents)
    registry = SimpleNamespace(lease=object())
    carriers = [
        _build_side(
            UUID(int=index),
            UUID(int=0x100 + index),
            registry,
            contents,
            identity,
            monkeypatch,
        )
        for index in (1, 2)
    ]
    registry.source_evidence = lambda: carriers[0].batch._locator._source._ledger
    monkeypatch.setattr(monitor_scope, "_check_capture_root", Mock())
    snapshot = monitor_scope._ScopeSnapshotV2(
        tuple(item.event for item in carriers),
        tuple(item.hold for item in carriers),
        (),
        tuple(item.held_target for item in carriers),
        (),
    )
    case = SimpleNamespace(
        snapshot=snapshot,
        registry=registry,
        contents=contents,
        carriers=carriers,
        publish=Mock(
            side_effect=AssertionError("rejected pair reached scope publication")
        ),
    )
    requests = {id(item.command): item.request for item in carriers}
    confirm_requests = Mock()

    def route_requests(commands):
        return nullcontext(
            (tuple(requests[id(command)] for command in commands), confirm_requests)
        )

    for item in carriers:
        item.batch = replace(item.batch, _completion_scope=snapshot)
        item.issuer._batches[id(item.batch)] = item.batch
        monkeypatch.setattr(item.issuer, "_snapshot", lambda **options: case.snapshot)
        monkeypatch.setattr(item.issuer, "_save", case.publish)
        monkeypatch.setattr(item.issuer, "_route_requests", route_requests)

    case.proofs = tuple(
        item.issuer.verify_settlement_side(
            item.command, item.authority, item.batch, item.target
        )
        for item in carriers
    )
    case.confirm_requests = confirm_requests
    return case


def assert_pair_refuses_changed_completion(monkeypatch, side, disproof):
    case = _issued_pair(monkeypatch)
    carriers, contents, proofs = case.carriers, case.contents, case.proofs
    bad, good = carriers[side], carriers[1 - side]
    _damage_completion_rows(
        bad.rows,
        disproof,
        bad.when,
        bad.turn,
        other_checkout=Path("/fixture/other-worktree"),
        total=bad.total,
    )
    contents[bad.path] = _bytes(bad.rows)
    _, changed_witnesses = _read_completion(
        bad.fixture,
        bad.rows,
        bad.batch._locator._source.stream_ref,
        bad.target.project_context,
    )
    assert changed_witnesses == []
    reread = replace(bad.batch, _completion_witnesses=tuple(changed_witnesses))
    bad.issuer._batches[id(reread)] = reread
    assert (
        bad.issuer.completion_witness(bad.command, bad.authority, reread, bad.target)
        is None
    )

    current_good = good.issuer.verify_settlement_side(
        good.command, good.authority, good.batch, good.target
    )
    assert current_good.hold == proofs[1 - side].hold
    assert current_good.progress.cursor == proofs[1 - side].progress.cursor
    assert (
        bad.issuer.completion_witness(bad.command, bad.authority, bad.batch, bad.target)
        is None
    )
    _assert_pair_refuses_before_write(
        monkeypatch, case, proofs, "current owned completion proof"
    )


def assert_pair_refuses_changed_authority(monkeypatch, side, failure):
    case = _issued_pair(monkeypatch)
    proofs = list(case.proofs)
    carrier = case.carriers[side]
    message = "current owned completion proof"
    if failure == "copy":
        proofs[side] = replace(proofs[side])
        message = "current settlement side from its scope writer"
    elif failure == "expired-hold":
        monkeypatch.setattr(carrier.issuer, "_clock", lambda: carrier.hold.expires_at)
        good = case.carriers[1 - side]
        assert good.issuer.completion_witness(
            good.command, good.authority, good.batch, good.target
        )
    else:
        changed = replace(
            carrier.event,
            scope=replace(carrier.event.scope, item=ItemKey(ItemKind.ISSUE, 999)),
        )
        case.snapshot = replace(
            case.snapshot,
            events=tuple(
                changed if event is carrier.event else event
                for event in case.snapshot.events
            ),
        )
        message = "current owned completion proof|scope snapshot changed"

    snapshot = case.snapshot
    _assert_pair_refuses_before_write(monkeypatch, case, proofs, message)
    assert case.snapshot is snapshot


def assert_committed_release_conflict_is_local(monkeypatch, conflict):
    case = _issued_pair(monkeypatch)
    owner, rival = case.proofs

    def committed_release(proof):
        terminal = proof._terminal
        assert terminal.project_context is not None
        checkpoint = proof.progress.cursor.checkpoint
        assert type(checkpoint) is SourceCheckpoint
        return monitor_scope._JournalScopeRelease(
            proof.hold,
            proof._original,
            proof.command.command_id,
            terminal.project_context,
            proof._prior_route,
            terminal.boundary,
            checkpoint.provider.ordinal,
            checkpoint.cursor,
            monitor_scope.HoldState.RESOLVED,
        )

    releases = tuple(committed_release(proof) for proof in case.proofs)

    def project(snapshot, proof):
        source = proof._batch._locator._source
        verify = Mock(
            wraps=lambda prefix: scanner._capture_position(source, prefix, fixed=prefix)
        )
        return verify, lambda: monitor_scope._project_journal_releases(
            snapshot, proof._batch, releases, frozenset(), verify
        )

    verify, read = project(case.snapshot, owner)
    holds, terminals = read()
    assert holds == (
        replace(owner.hold, state=monitor_scope.HoldState.RESOLVED),
        rival.hold,
    )
    assert terminals == ((releases[0].terminal, releases[0].completion_ordinal),)
    verify.assert_called_once_with(releases[0].terminal_prefix)

    state = case.snapshot
    if conflict == "changed-route":
        owner_event, rival_event = state.events
        changed = replace(
            owner_event,
            scope=replace(owner_event.scope, item=ItemKey(ItemKind.ISSUE, 999)),
        )
        state = replace(state, events=(changed, rival_event))
    elif conflict == "changed-hold":
        changed = replace(
            owner.hold, expires_at=owner.hold.expires_at + timedelta(seconds=1)
        )
        state = replace(state, holds=(changed, rival.hold))
    else:
        changed = replace(owner.hold, state=monitor_scope.HoldState.RESOLVED)
        resolution = monitor_scope._Resolution(UUID(int=0xA22), "a" * 64, changed)
        state = replace(state, holds=(changed, rival.hold), resolutions=(resolution,))

    verify, read = project(state, owner)
    with pytest.raises(
        LedgerError, match="Committed settlement conflicts with scope history"
    ):
        read()
    verify.assert_not_called()
    verify, read = project(state, rival)
    holds, terminals = read()
    assert holds == (
        state.holds[0],
        replace(rival.hold, state=monitor_scope.HoldState.RESOLVED),
    )
    assert terminals == ((releases[1].terminal, releases[1].completion_ordinal),)
    verify.assert_called_once_with(releases[1].terminal_prefix)
    _, read = project(case.snapshot, owner)
    assert read() == (
        (replace(owner.hold, state=monitor_scope.HoldState.RESOLVED), rival.hold),
        ((releases[0].terminal, releases[0].completion_ordinal),),
    )


def _assert_pair_refuses_before_write(monkeypatch, case, proofs, message):
    registry = case.registry
    case.confirm_requests.reset_mock()

    transaction = Mock(return_value=nullcontext(object()))
    monkeypatch.setattr(
        monitor_journal,
        "JournalStore",
        Mock(return_value=SimpleNamespace(transaction=transaction)),
    )
    journal = monitor_journal.RoutingJournal(registry, case.carriers[0].issuer)
    write = Mock(side_effect=AssertionError("stale proof reached settlement writes"))
    monkeypatch.setattr(journal, "_build_settlement_change", write)
    with pytest.raises(LedgerError, match=message):
        journal.settle_disposition(
            registry.source_evidence().pseudonymize("fixture", "dispute"), *proofs
        )
    transaction.assert_called_once_with(write=True)
    write.assert_not_called()
    case.publish.assert_not_called()
    case.confirm_requests.assert_not_called()
