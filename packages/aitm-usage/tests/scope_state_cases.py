"""Typed inputs and in-memory publication for scope state policy tests."""

from contextlib import nullcontext
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

from monitor_inbox_cases import MonitorInboxFiles
from qualification_policy_cases import qualification_policy

from aitm_usage import monitor_control, monitor_scope
from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_scope import (
    AffectedScope,
    ScopeAuthority,
    ScopePosition,
    ScopeState,
    VerifiedBoundary,
    _ScopeSnapshot,
)
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.scope_admission import DispositionRequest, MarkRequest
from aitm_usage.sources.adapter import NativeBoundary
from aitm_usage.types import (
    BoundaryKind,
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    Provider,
    SourceBoundary,
    SourceCursor,
)

_EVIDENCE = _ServiceEvidence(b"scope-state-test-fixture")


class MemoryScope:
    def __init__(self, monkeypatch, clock):
        self.state = ScopeState(
            SimpleNamespace(root=Path("/fixture/scope"), lease=object()), clock=clock
        )
        self.snapshot = _ScopeSnapshot()
        self.require_boundary = Mock()
        monkeypatch.setattr(self.state, "_require_boundary", self.require_boundary)
        monkeypatch.setattr(
            self.state, "_snapshot", lambda *, confirm=False: self.snapshot
        )
        monkeypatch.setattr(self.state, "_save", self._publish)

    def _publish(self, snapshot):
        self.snapshot = snapshot

    @staticmethod
    def reference(label):
        return _EVIDENCE.pseudonymize("fixture", label)

    def boundary(self, command, ordinal, *, owner, anchor, checkout):
        session = self.reference("session")
        stream = self.reference("stream")
        position = ScopePosition(
            owner, NativeSurface.CODEX_DESKTOP_MACOS, session, stream, ordinal
        )
        boundary = SourceBoundary(
            Provider.CODEX,
            stream,
            session,
            ordinal,
            BoundaryKind.REQUEST,
            self.reference(f"boundary-{ordinal}"),
            receipt_ref=command.receipt_ref,
        )
        cursor = SourceCursor(
            stream,
            self.reference("locator"),
            self.reference("incarnation"),
            ordinal + 1,
            self.reference(f"prefix-{ordinal}"),
        )
        return VerifiedBoundary(
            command.command_id,
            self.reference(str(command.command_id)).value.split(":")[1],
            position,
            checkout,
            anchor,
            True,
            AffectedScope(ordinal, ordinal + 1, (self.reference(f"usage-{ordinal}"),)),
            boundary,
            SimpleNamespace(
                _grok_strict=False, _admitted={owner}, _native_cursor=cursor
            ),
            ScopeAuthority(owner, "fixture"),
        )


def route_policy_case(monkeypatch, cutoff, *, release, typed_request=False):
    root = qualification_policy(
        monkeypatch,
        UUID(int=2),
        cutoff,
        evidence_key=b"q" * 32 if typed_request else None,
    )
    registry, locator = root.writer, root.locator
    source = locator._source
    evidence = registry.source_evidence()
    owner = root.view.projects[0].project_id
    when = cutoff + timedelta(minutes=1)
    checkout = evidence.pseudonymize("fixture", "checkout")
    hold_id, command_id = UUID(int=0x501), UUID(int=0x503)
    hold_boundary = SourceBoundary(
        Provider.CODEX,
        source.stream_ref,
        source.session_ref,
        10,
        BoundaryKind.REQUEST,
        evidence.pseudonymize("fixture", "held-boundary"),
        receipt_ref=evidence.pseudonymize("scope-receipt", str(hold_id)),
    )
    terminal = replace(
        hold_boundary,
        ordinal=20,
        kind=BoundaryKind.TURN,
        boundary_ref=evidence.pseudonymize("fixture", "terminal-boundary"),
        receipt_ref=evidence.pseudonymize("scope-receipt", str(command_id)),
    )
    held_prefix = SourceCursor(
        source.stream_ref,
        source.locator_ref,
        source.incarnation_ref,
        100,
        evidence.pseudonymize("fixture", "held-prefix"),
    )
    terminal_prefix = replace(
        held_prefix,
        offset=200,
        anchor_ref=evidence.pseudonymize("fixture", "terminal-prefix"),
    )
    position = ScopePosition(
        root.approved.source_id,
        source._native_surface,
        source.session_ref,
        source.stream_ref,
        10,
    )
    hold = monitor_scope.ProofHold(
        hold_id,
        "a" * 64,
        owner,
        position,
        AffectedScope(10, 12),
        cutoff,
        when + timedelta(minutes=2),
    )
    event = monitor_scope._ScopeEvent(
        UUID(int=0x500),
        "b" * 64,
        monitor_scope.Scope(owner),
        replace(position, ordinal=1),
        checkout,
        owner,
        True,
        AffectedScope(1, 2),
        None,
    )
    case = SimpleNamespace(
        when=when,
        hold=hold,
        event=event,
        snapshot=monitor_scope._ScopeSnapshotV2(
            (event,),
            (hold,),
            (),
            (monitor_scope._HeldRouteTarget(hold_id, hold_boundary, held_prefix),),
            (),
        ),
    )
    state = ScopeState(registry, clock=lambda: case.when)
    case.state = state
    case.publish = Mock(
        side_effect=lambda snapshot: setattr(case, "snapshot", snapshot)
    )
    monkeypatch.setattr(state, "_snapshot", lambda **_: case.snapshot)
    monkeypatch.setattr(state, "_save", case.publish)
    monkeypatch.setattr(
        state,
        "_ledger",
        lambda project: SimpleNamespace(
            identity=SimpleNamespace(key_id=evidence.key_id)
        ),
    )
    monkeypatch.setattr(
        state, "_anchor", lambda view, ref: owner if ref == checkout else None
    )
    monkeypatch.setattr(
        registry,
        "span_disposition",
        lambda *args: Eligibility.ELIGIBLE,
    )
    if not typed_request:
        monkeypatch.setattr(
            state, "_route_request", lambda command: nullcontext("c" * 64)
        )
    monkeypatch.setattr(monitor_scope, "_check_capture_root", Mock())

    def capture(native, prior, *, fixed=None):
        assert native is source and prior in (None, held_prefix, terminal_prefix)
        assert fixed == prior
        return SimpleNamespace(cursor=terminal_prefix if fixed is None else fixed)

    monkeypatch.setattr(monitor_scope, "_capture_position", capture)
    target = NativeBoundary(terminal, checkout)
    batch = monitor_scope.VerifiedScopeBatch(
        root.approved.source_id,
        source._native_surface,
        (),
        (NativeBoundary(hold_boundary, checkout), target),
        (
            Diagnostic(
                DiagnosticCode.BOUNDARY_UNVERIFIED,
                when,
                Provider.CODEX,
                source.stream_ref,
            ),
        ),
        None,
        (),
        frozenset((owner,)),
        locator,
        terminal_prefix,
        root.view,
        registry._require_live_source(root.approved),
    )
    state._batches[id(batch)] = batch
    command = monitor_scope.Disposition(
        command_id, owner, hold_id, terminal.receipt_ref, release
    )
    authority = state.operator(owner)
    state.authorize(command, authority)
    case.command = command
    case.terminal = state.verify_boundary(command, authority, batch, target)
    return case


def route_admission_case(monkeypatch, cutoff, *, release=False, wrong_type=False):
    """Issue a native proposal with the real typed request and witness checks."""
    case = route_policy_case(monkeypatch, cutoff, release=release, typed_request=True)
    writer = case.state.registry
    command = case.command
    case.files = MonitorInboxFiles(monkeypatch, command.project_id, writer=writer)
    case.witness_at = case.when
    monkeypatch.setattr(monitor_control, "_scope_now", lambda: case.witness_at)
    monkeypatch.setattr(monitor_scope, "_path_exists", case.files.files.__contains__)
    case.reader = monitor_control.ScopeInboxReader(writer, case.files.inbox)
    grant_id = UUID(int=0x506)
    if wrong_type:
        case.reader.register(grant_id, command.project_id, ("mark",))
        case.request = MarkRequest(
            command.command_id, grant_id, monitor_scope.Scope(command.project_id)
        )
    else:
        case.reader.register(grant_id, command.project_id, ("dispose",))
        case.request = DispositionRequest(
            command.command_id, grant_id, command.project_id, command.hold_id, release
        )
    case.reader.advertise(case.reader.probe(case.request))
    assert case.files.inbox.enqueue_scope(case.request)
    return case
