"""Isolated policy checks for scope projection and journal revision selection."""

import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

from aitm_usage.monitor_journal import (
    _distinct_accepted_child,
    _RevisionPayload,
    _StoredRevision,
)
from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_scope import (
    AffectedScope,
    HandoffStatus,
    Scope,
    ScopePosition,
    _ScopeEvent,
    _timeline,
)
from aitm_usage.monitor_types import NativeSurface, ObservationTimeBasis
from aitm_usage.sources.adapter import NativeObservation, _claude_revision_material
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    Provider,
    SourceBoundary,
    TokenCounts,
    UsageObservation,
    _encode,
)

EVIDENCE = _ServiceEvidence(b"monitor-policy-unit-test-key")


def test_earlier_handoff_holds_later_handoff_with_stale_generation():
    origin, early_owner, late_owner = (UUID(int=value) for value in (1, 2, 3))
    checkout = EVIDENCE.pseudonymize("fixture", "checkout")
    position = ScopePosition(
        UUID(int=4),
        NativeSurface.CODEX_DESKTOP_MACOS,
        EVIDENCE.pseudonymize("fixture", "session"),
        EVIDENCE.pseudonymize("fixture", "stream"),
        10,
    )
    earlier = _ScopeEvent(
        command_id=UUID(int=5),
        digest="a" * 64,
        scope=Scope(early_owner),
        position=position,
        checkout=checkout,
        anchor_project=origin,
        eligible=True,
        affected=AffectedScope(10, 11),
        native_boundary=None,
        current_project=origin,
        before_generation=0,
        retained_checkout=checkout,
    )
    later = replace(
        earlier,
        command_id=UUID(int=6),
        digest="b" * 64,
        scope=Scope(late_owner),
        position=replace(position, ordinal=20),
        affected=AffectedScope(20, 21),
    )

    route, outcomes = _timeline((later,), later.position)
    assert route.scope == Scope(late_owner)
    assert outcomes[later.command_id].status is HandoffStatus.APPLIED

    route, outcomes = _timeline((later, earlier), later.position)
    assert route.scope == Scope(early_owner)
    assert route.generation == 1
    assert late_owner in route.held
    assert outcomes[earlier.command_id].status is HandoffStatus.APPLIED
    assert outcomes[later.command_id].status is HandoffStatus.HELD


@pytest.mark.parametrize(
    ("stored_outputs", "accepted_output"),
    [
        pytest.param((7,), 7, id="one-child"),
        pytest.param((9,), None, id="equal-usage"),
        pytest.param((7, 8), None, id="ambiguous-children"),
    ],
)
def test_content_dispute_requires_one_distinct_accepted_child(
    stored_outputs, accepted_output
):
    common = EVIDENCE.pseudonymize("fixture", "common")
    key = EVIDENCE.pseudonymize("fixture", "observation")
    boundary = SourceBoundary(
        Provider.CLAUDE,
        EVIDENCE.pseudonymize("fixture", "stream"),
        EVIDENCE.pseudonymize("fixture", "session"),
        10,
        BoundaryKind.REQUEST,
        EVIDENCE.pseudonymize("fixture", "boundary"),
    )
    contender = UsageObservation(
        boundary,
        datetime(2026, 1, 1, tzinfo=UTC),
        ClientVersion.UNKNOWN,
        1,
        TokenCounts(output_tokens=9),
        Availability.COMPLETE,
    )
    rows = []
    revisions = {}
    for sequence, output in enumerate(stored_outputs, start=1):
        usage = replace(contender, tokens=TokenCounts(output_tokens=output))
        native = NativeObservation(
            key,
            2,
            usage,
            NativeSurface.CLAUDE_CODE_MACOS,
            ObservationTimeBasis.NATIVE_USAGE_EVENT,
            None,
        )
        material = _claude_revision_material(EVIDENCE, native)
        payload = _RevisionPayload(
            usage,
            2,
            EVIDENCE.pseudonymize("fixture", f"prefix-{output}"),
            EVIDENCE.pseudonymize("fixture", "locator"),
            EVIDENCE.pseudonymize("fixture", "incarnation"),
        )
        ordinal = boundary.ordinal + sequence
        revisions[output] = _StoredRevision(
            sequence, ordinal, material, common, payload
        )
        encoded = _encode(
            payload, _RevisionPayload, validate_ref=EVIDENCE.validate_source_ref
        ).encode()
        rows.append((sequence, ordinal, material.value, common.value, encoded))

    connection = Mock(spec=sqlite3.Connection)
    connection.execute.return_value = rows

    assert _distinct_accepted_child(connection, key, common, contender, EVIDENCE) == (
        revisions.get(accepted_output)
    )
    [(sql, params)] = [call.args for call in connection.execute.call_args_list]
    assert "WHERE key = ?" in sql
    assert params == (key.value,)
