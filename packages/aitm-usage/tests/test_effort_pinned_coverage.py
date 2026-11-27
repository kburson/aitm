from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_effort_session import CHILD, OWNER, PROJECT, REMOTE, SESSION, layout
from test_effort_session import session_api as session_api

from aitm_usage.effort.pinned_coverage import (
    canonical,
    export_coverage,
    validate_coverage,
)
from aitm_usage.effort.receipts import (
    Outcome,
    TimeBasis,
    UsageReceipt,
    UsageScope,
)
from aitm_usage.effort.session import SessionStore, validate_public_receipt
from aitm_usage.effort.store import EffortError
from aitm_usage.types import Availability, TokenCounts

WINDOW = {
    "window_start_utc": "2026-11-25T00:00:00Z",
    "window_end_utc": "2026-11-25T01:00:00Z",
    "cutoff_utc": "2026-11-25T02:00:00Z",
}


def authority(attempts, **changes):
    return {
        "schema": "aitm.story-effort-admission/v1",
        "project": str(PROJECT),
        "story": 457,
        "window": WINDOW,
        "sessions": [str(SESSION)],
        "attempts": [str(attempt) for attempt in attempts],
        "missing": [],
        "unattributed": 0,
        "verified_no_work": False,
        "source_sha256": "d" * 64,
    } | changes


def test_export_preserves_attempt_identity_through_story_switch(session_api, tmp_path):
    store, launch, turn = layout(session_api, tmp_path / "store.sqlite")
    store.bind(SESSION, CHILD, launch, turn)
    store.accept(
        SESSION,
        UsageReceipt(
            PROJECT,
            CHILD,
            turn,
            "a" * 64,
            datetime(2026, 11, 25, 1, tzinfo=UTC),
            1,
            Availability.COMPLETE,
            Outcome.COMPLETED,
            TokenCounts(
                input_tokens=0, cached_input_tokens=0, output_tokens=0, total_tokens=0
            ),
            scope=UsageScope.BOUNDED,
            started_at=datetime(2026, 11, 25, 0, 5, tzinfo=UTC),
            ended_at=datetime(2026, 11, 25, 0, 6, tzinfo=UTC),
            time_basis=TimeBasis.NATIVE,
        ),
    )
    store.select(SESSION, 458, REMOTE)
    reopened = SessionStore(tmp_path / "store.sqlite", PROJECT)
    raw = export_coverage(
        reopened, [SESSION], 457, WINDOW, "closed", authority([OWNER, CHILD])
    )
    data = validate_coverage(raw)
    (public,) = reopened.public_receipts(SESSION)
    opaque = validate_public_receipt(public)["attempt"]
    assert {r["state"] for r in data["attempts"]} == {"pending-binding", "observed"}
    assert {"attempt": opaque, "state": "observed"} in data["attempts"]
    assert all(
        s.encode() not in raw for s in ("private-canary", str(SESSION), str(OWNER))
    )
    assert raw == export_coverage(
        reopened, [SESSION], 457, WINDOW, "closed", authority([OWNER, CHILD])
    )


def test_zero_length_at_window_open_is_an_enrolled_attempt(session_api, tmp_path):
    store, launch, turn = layout(session_api, tmp_path / "store.sqlite")
    store.bind(SESSION, CHILD, launch, turn)
    start = datetime(2026, 11, 25, tzinfo=UTC)
    store.accept(
        SESSION,
        UsageReceipt(
            PROJECT,
            CHILD,
            turn,
            "a" * 64,
            datetime(2026, 11, 25, 1, tzinfo=UTC),
            1,
            Availability.COMPLETE,
            Outcome.COMPLETED,
            TokenCounts(input_tokens=0),
            scope=UsageScope.BOUNDED,
            started_at=start,
            ended_at=start,
            time_basis=TimeBasis.NATIVE,
        ),
    )
    states, _ = store.coverage_snapshot([SESSION], 457, WINDOW)
    assert states[CHILD] == "observed"
    with pytest.raises(EffortError, match="session"):
        export_coverage(store, [SESSION, UUID(int=5)], 457, WINDOW, "open")


class CoverageStore:
    project_id = PROJECT

    def __init__(self, attempts=None, unresolved=0):
        self.attempts = {} if attempts is None else attempts
        self.unresolved = unresolved

    def coverage_snapshot(self, sessions, story, window):
        if sessions != [SESSION]:
            raise EffortError("Unknown effort session")
        assert (story, window) == (457, WINDOW)
        return self.attempts.copy(), self.unresolved

    @staticmethod
    def public_attempt(attempt):
        return f"{attempt.int:064x}"


def test_closed_evidence_must_match_store_and_explicit_zero():
    store = CoverageStore()
    with pytest.raises(EffortError, match="admission"):
        export_coverage(store, [SESSION], 457, WINDOW, "closed")
    with pytest.raises(EffortError, match="no-work"):
        export_coverage(store, [SESSION], 457, WINDOW, "closed", authority([]))
    zero = export_coverage(
        store, [SESSION], 457, WINDOW, "closed", authority([], verified_no_work=True)
    )
    assert validate_coverage(zero)["attempts"] == []
    store = CoverageStore({OWNER: "pending-binding"})
    with pytest.raises(EffortError, match="attempt"):
        export_coverage(
            store,
            [SESSION],
            457,
            WINDOW,
            "closed",
            authority([], verified_no_work=True),
        )
    # An explicitly unselected session also makes the independently supplied
    # admission roster inapplicable.
    with pytest.raises(EffortError, match="scope"):
        export_coverage(
            store,
            [SESSION],
            457,
            WINDOW,
            "closed",
            authority([OWNER], sessions=[str(UUID(int=5))]),
        )


def test_explicit_missing_and_unassigned_remain_visible():
    store = CoverageStore({OWNER: "pending-binding", CHILD: "pending-binding"}, 1)
    open_record = validate_coverage(
        export_coverage(store, [SESSION], 457, WINDOW, "open")
    )
    assert open_record["unattributed"] == 1
    assert len(open_record["attempts"]) == 2
    closed = export_coverage(
        store,
        [SESSION],
        457,
        WINDOW,
        "closed",
        authority([OWNER, CHILD], missing=[str(CHILD)], unattributed=1),
    )
    assert {item["state"] for item in validate_coverage(closed)["attempts"]} == {
        "pending-binding",
        "missing",
    }
    tampered = validate_coverage(closed) | {"unexpected": "secret"}
    with pytest.raises(EffortError, match="coverage"):
        validate_coverage(canonical(tampered))


def test_scope_correction_and_conflict_are_not_complete(session_api):
    from test_effort_trail import evidence

    _, native = evidence("receipt-conflict")
    initial = replace(
        native, project_id=PROJECT, attempt_id=CHILD, coverage=Availability.PARTIAL
    )
    conflict = replace(initial, source_sha256="b" * 64)

    def execute(query, arguments):
        assert "FROM conflicts" in query and arguments == (str(CHILD),)
        return [(conflict.to_json(),)]

    state = session_api._coverage_state(
        SimpleNamespace(execute=execute), str(CHILD), initial.turn, initial, None
    )
    store = CoverageStore({OWNER: "pending-binding", CHILD: state})
    data = validate_coverage(export_coverage(store, [SESSION], 457, WINDOW, "open"))
    assert {row["state"] for row in data["attempts"]} == {"pending-binding", "disputed"}
