"""Validate persisted scope shapes with an in-memory snapshot reader."""

import json
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest

from aitm_usage import monitor_scope
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_scope import (
    AffectedScope,
    HoldState,
    ProofHold,
    ScopePosition,
    ScopeState,
    _HeldRouteTarget,
    _RouteDispositionRecord,
    _ScopeSnapshotV2,
)
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.types import (
    BoundaryKind,
    Provider,
    SourceBoundary,
    SourceCursor,
    _encode,
)

_EVIDENCE = _ServiceEvidence(b"scope-snapshot-unit-test-key")


def reference(label):
    return _EVIDENCE.pseudonymize("fixture", label)


def snapshot_reader(monkeypatch):
    hold_id = UUID(int=0x501)
    seen = datetime(2026, 1, 1, tzinfo=UTC)
    target = SourceBoundary(
        Provider.CODEX,
        reference("stream"),
        reference("session"),
        10,
        BoundaryKind.REQUEST,
        reference("target"),
        receipt_ref=reference("hold-receipt"),
    )
    terminal = replace(
        target,
        ordinal=20,
        kind=BoundaryKind.TURN,
        boundary_ref=reference("terminal"),
        receipt_ref=reference("terminal-receipt"),
    )
    prefix = SourceCursor(
        target.stream_ref,
        reference("locator"),
        reference("incarnation"),
        100,
        reference("anchor"),
    )
    hold = ProofHold(
        hold_id,
        "a" * 64,
        UUID(int=1),
        ScopePosition(
            UUID(int=2),
            NativeSurface.CODEX_DESKTOP_MACOS,
            target.session_ref,
            target.stream_ref,
            target.ordinal,
        ),
        AffectedScope(10, 12),
        seen,
        seen + timedelta(days=1),
    )
    snapshot = _ScopeSnapshotV2(
        (),
        (hold,),
        (),
        (_HeldRouteTarget(hold_id, target, prefix),),
        (
            _RouteDispositionRecord(
                UUID(int=0x503),
                "b" * 64,
                "c" * 64,
                hold_id,
                HoldState.HELD,
                HoldState.GAP,
                terminal,
                replace(prefix, offset=200),
                reference("checkout"),
            ),
        ),
    )
    raw = _encode(snapshot, _ScopeSnapshotV2).encode()
    reader = Mock(return_value=raw)
    monkeypatch.setattr(monitor_scope, "_path_exists", lambda _path: True)
    monkeypatch.setattr(
        monitor_scope, "_pin_directory", lambda _path: nullcontext(object())
    )
    monkeypatch.setattr(monitor_scope, "_read_state", reader)
    state = ScopeState(SimpleNamespace(root=Path("unused"), _writer=None))
    assert state.view().holds == (hold,)
    return json.loads(raw), reader, state


MALFORMED_SNAPSHOT_CASES = (
    "unknown",
    "mixed",
    "missing",
    "extra",
    "nested",
    "hold-digest",
    "command-digest",
    "request-digest",
    "held-state",
    "outcome",
    "resolved-from-gap",
    "duplicate-target",
    "duplicate-disposition",
    "second-disposition",
    "unowned-target",
    "unowned-disposition",
    "terminal-too-early",
    "terminal-reused-receipt",
    "terminal-reused-boundary",
    "empty-span",
    "empty-prefix",
    "same-prefix",
    "changed-stream",
    "changed-locator",
    "changed-incarnation",
    "changed-session",
    "wrong-provider",
    "wrong-target-position",
    "wrong-hold-surface",
)


def assert_rejects_snapshot(snapshot_reader, changed):
    payload, reader, state = snapshot_reader
    target = payload["held_route_targets"][0]
    record = payload["route_dispositions"][0]
    hold = payload["holds"][0]
    boundary, prefix = record["boundary"], record["prefix"]
    other = reference("other").value
    if changed == "unknown":
        payload["format"] = "aitm.usage.monitor-scope/v3"
    elif changed == "mixed":
        payload["format"] = "aitm.usage.monitor-scope/v1"
    elif changed == "missing":
        del payload["held_route_targets"]
    elif changed == "extra":
        payload["extra"] = None
    elif changed == "nested":
        record["extra"] = None
    elif changed == "hold-digest":
        hold["command_digest"] = "X" * 64
    elif changed == "command-digest":
        record["command_digest"] = "A" * 64
    elif changed == "request-digest":
        record["request_digest"] = "a" * 63
    elif changed == "held-state":
        record["hold_state"] = "resolved"
    elif changed == "outcome":
        record["outcome"] = "held"
    elif changed == "resolved-from-gap":
        record["hold_state"], record["outcome"] = "gap", "resolved"
    elif changed == "duplicate-target":
        payload["held_route_targets"].append(target)
    elif changed == "duplicate-disposition":
        payload["route_dispositions"].append(record)
    elif changed == "second-disposition":
        payload["route_dispositions"].append(
            record
            | {
                "command_id": str(UUID(int=0x505)),
                "boundary": boundary | {"receipt_ref": other},
            }
        )
    elif changed == "unowned-target":
        target["hold_id"] = str(UUID(int=0x505))
    elif changed == "unowned-disposition":
        record["hold_id"] = str(UUID(int=0x505))
    elif changed == "terminal-too-early":
        boundary["ordinal"] = hold["affected"]["end"] - 1
    elif changed == "terminal-reused-receipt":
        boundary["receipt_ref"] = target["boundary"]["receipt_ref"]
    elif changed == "terminal-reused-boundary":
        boundary["boundary_ref"] = target["boundary"]["boundary_ref"]
    elif changed == "empty-span":
        hold["affected"]["end"] = hold["affected"]["start"]
    elif changed == "empty-prefix":
        target["prefix"]["offset"] = 0
    elif changed == "same-prefix":
        prefix["offset"] = target["prefix"]["offset"]
    elif changed == "changed-stream":
        prefix["source_ref"] = boundary["stream_ref"] = other
    elif changed == "changed-locator":
        prefix["locator_ref"] = other
    elif changed == "changed-incarnation":
        prefix["incarnation_ref"] = other
    elif changed == "changed-session":
        boundary["session_ref"] = other
    elif changed == "wrong-provider":
        boundary["provider"] = "claude"
    elif changed == "wrong-target-position":
        target["boundary"]["ordinal"] += 1
    else:
        hold["position"]["surface"] = "codex-cli-linux"
    reader.return_value = json.dumps(payload).encode()
    with pytest.raises(LedgerError, match="Invalid private scope"):
        state.view()
