"""Qualify response intervals and attribute their elapsed time without double counting."""

from datetime import UTC, datetime, timedelta

import pytest

from aitm_core.models.evidence import DocumentReviewTurn, ReviewParticipant
from aitm_core.reviews import timing


def _start(second):
    return datetime(2026, 11, 27, 12, 0, second, tzinfo=UTC)


def _interval(start, end):
    return _start(start), _start(end)


def _turn(start, end, *, round_no=1, session="session", basis="recorded", **changes):
    return DocumentReviewTurn(
        **(
            {
                "record_id": "review",
                "level": "sar",
                "path": "plans/plan.md",
                "round": round_no,
                "role": "reviewer",
                "agent": ReviewParticipant(
                    host="host",
                    provider="provider",
                    model_id="model",
                    effort=None,
                    session_id=session,
                    session_id_kind="native" if session else "unknown",
                ),
                "started_at": _start(start).isoformat() if start is not None else None,
                "submitted_at": _start(end).isoformat(),
                "start_basis": basis,
                "start_ref": "evidence.json" if basis != "unknown" else None,
                "input_digest": "a" * 64,
                "response_path": f"review/response-{round_no}.md",
                "source_digest": "b" * 64,
                "finding_ids": (),
                "decision": "pass",
            }
            | changes
        )
    )


def test_explicit_coverage_subtracts_exclusions_and_interruptions():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(
                _turn(2, 17),
                covered=(_interval(0, 21),),
                excluded=(_interval(0, 4), _interval(16, 21)),
                interrupted=(_interval(9, 11),),
            )
        ]
    )
    (turn,) = result.turns
    assert turn.response_duration == timedelta(seconds=10)
    assert turn.qualified == (_interval(4, 9), _interval(11, 16))
    assert turn.excluded == (_interval(2, 4), _interval(16, 17))
    assert turn.interrupted == (_interval(9, 11),)
    assert turn.unknown == ()
    assert result.actor_time == result.wall_time == timedelta(seconds=10)


@pytest.mark.parametrize(
    ("basis", "start", "changes", "expected_bound"),
    [
        ("prior-submit", 0, {}, _interval(0, 10)),
        ("unknown", None, {}, None),
        ("recorded", 0, {"start_ref": None}, None),
        ("claim", 11, {}, None),
    ],
)
def test_unqualified_anchors_never_become_measured(
    basis, start, changes, expected_bound
):
    result = timing.summarize_review_timing(
        [timing.TurnTimingEvidence(_turn(start, 10, basis=basis, **changes))]
    )
    (turn,) = result.turns
    assert turn.bound == expected_bound
    assert turn.response_duration is None
    assert turn.qualified == ()
    assert turn.turn.submitted_at == _start(10).isoformat()
    assert result.basis_counts == {basis: 1}
    assert result.actor_time is None
    assert result.wall_time is None


def test_partial_claim_coverage_retains_unknown_without_counting_it():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(
                _turn(0, 14, basis="claim"),
                covered=(_interval(4, 8),),
                interrupted=(_interval(10, 12),),
            )
        ]
    )
    (turn,) = result.turns
    assert turn.response_duration is None
    assert turn.unknown == (_interval(0, 4), _interval(8, 10), _interval(12, 14))
    assert result.actor_time == result.wall_time == timedelta(seconds=4)


def test_overlapping_sessions_and_concurrent_actors_yield_distinct_totals():
    first = timing.TurnTimingEvidence(_turn(0, 10), covered=(_interval(0, 10),))
    result = timing.summarize_review_timing(
        [
            first,
            first,
            timing.TurnTimingEvidence(
                _turn(5, 12, round_no=2), covered=(_interval(5, 12),)
            ),
            timing.TurnTimingEvidence(
                _turn(8, 14, round_no=3, session="parallel"),
                covered=(_interval(8, 14),),
            ),
        ],
        states=[timing.StateWindow("Plan", _interval(0, 9))],
    )
    assert result.basis_counts == {"recorded": 3}
    assert result.actor_time == timedelta(seconds=18)
    assert result.wall_time == timedelta(seconds=14)
    assert result.attributed_time == {
        ("Plan", "sar", "reviewer", "provider", "model"): timedelta(seconds=10),
        (None, "sar", "reviewer", "provider", "model"): timedelta(seconds=8),
    }


def test_overlapping_state_evidence_leaves_conflicts_and_gaps_unallocated():
    result = timing.summarize_review_timing(
        [timing.TurnTimingEvidence(_turn(0, 16), covered=(_interval(0, 16),))],
        states=[
            timing.StateWindow("Refine", _interval(0, 5)),
            timing.StateWindow("Refine", _interval(2, 4)),
            timing.StateWindow("Plan", _interval(5, 13)),
            timing.StateWindow("Review", _interval(11, 14)),
        ],
    )
    assert result.attributed_time == {
        ("Refine", "sar", "reviewer", "provider", "model"): timedelta(seconds=5),
        ("Plan", "sar", "reviewer", "provider", "model"): timedelta(seconds=6),
        ("Review", "sar", "reviewer", "provider", "model"): timedelta(seconds=1),
        (None, "sar", "reviewer", "provider", "model"): timedelta(seconds=4),
    }


def test_overlap_across_review_labels_is_unallocated_in_the_breakdown():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(_turn(0, 8), covered=(_interval(0, 8),)),
            timing.TurnTimingEvidence(
                _turn(5, 12, record_id="other", level="xpr"),
                covered=(_interval(5, 12),),
            ),
        ]
    )
    assert result.actor_time == timedelta(seconds=12)
    assert result.attributed_time == {
        (None, "sar", "reviewer", "provider", "model"): timedelta(seconds=5),
        (None, None, "reviewer", "provider", "model"): timedelta(seconds=3),
        (None, "xpr", "reviewer", "provider", "model"): timedelta(seconds=4),
    }


def test_explicit_actor_combines_sessions_without_losing_same_session_overlap():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(_turn(0, 5), covered=(_interval(0, 5),)),
            timing.TurnTimingEvidence(
                _turn(2, 8, round_no=2), covered=(_interval(2, 8),), actor_id="actor"
            ),
            timing.TurnTimingEvidence(
                _turn(5, 12, round_no=3, session="other"),
                covered=(_interval(5, 12),),
                actor_id="actor",
            ),
        ]
    )
    assert result.actor_time == result.wall_time == timedelta(seconds=12)


def test_missing_session_keeps_covered_time_unallocated_by_actor():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(
                _turn(0, 10, session=None), covered=(_interval(0, 10),)
            )
        ]
    )
    assert result.turns[0].response_duration == timedelta(seconds=10)
    assert result.actor_time is None
    assert result.wall_time == timedelta(seconds=10)
    assert result.unallocated_actor_wall_time == timedelta(seconds=10)


def test_conflicting_evidence_for_the_same_turn_requires_reconciliation():
    with pytest.raises(ValueError, match="conflicting timing evidence"):
        timing.summarize_review_timing(
            [
                timing.TurnTimingEvidence(_turn(0, 8)),
                timing.TurnTimingEvidence(_turn(0, 9)),
            ]
        )


def test_inexact_evidence_interval_cannot_be_counted():
    with pytest.raises(ValueError, match="positive UTC interval"):
        timing.summarize_review_timing(
            [timing.TurnTimingEvidence(_turn(0, 8), covered=(_interval(9, 2),))]
        )


def test_turn_breakdown_keeps_excluded_interrupted_and_unknown_time_visible():
    result = timing.summarize_review_timing(
        [
            timing.TurnTimingEvidence(
                _turn(0, 14),
                covered=(_interval(3, 8),),
                excluded=(_interval(0, 2),),
                interrupted=(_interval(7, 10),),
            )
        ],
        states=[
            timing.StateWindow("Refine", _interval(0, 5)),
            timing.StateWindow("Plan", _interval(5, 14)),
        ],
    )
    assert result.turns[0].by_state == {
        "Refine": {
            "excluded": timedelta(seconds=2),
            "unknown": timedelta(seconds=1),
            "qualified": timedelta(seconds=2),
        },
        "Plan": {
            "qualified": timedelta(seconds=2),
            "interrupted": timedelta(seconds=3),
            "unknown": timedelta(seconds=4),
        },
    }
