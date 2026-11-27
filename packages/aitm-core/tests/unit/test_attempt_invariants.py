"""Exercise the causal execution reducer at retained identity and proof boundaries."""

import pytest

from aitm_core.events import StoryState
from aitm_core.reducers.attempts import AttemptIntegrityError, fold_attempt
from tests.unit.test_c55 import (
    SOURCE,
    START,
    clock,
    execution,
    fact,
    records,
    replay,
    start_clock,
)


@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"action_key": "publish"}, id="different-action"),
        pytest.param({"executor": "runner-2"}, id="different-executor"),
        pytest.param({"authority_store": "other-store"}, id="different-store"),
        pytest.param({"expected_prior_version": "e" * 40}, id="different-version"),
    ],
)
def test_execution_cannot_rebind_admitted_authority(change):
    with pytest.raises(
        AttemptIntegrityError, match="disagrees with retained authority"
    ):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", proof="bound-admission")],
            [execution("started", **change)],
        )


def test_execution_cannot_replace_retained_request_id():
    with pytest.raises(AttemptIntegrityError, match="request identity"):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", request_id="different", proof="admission")],
        )


def test_execution_cannot_change_source_before_start():
    foreign = {**SOURCE, "tree": "f" * 40}
    with pytest.raises(
        AttemptIntegrityError, match="disagrees with the retained source"
    ):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", proof="admission")],
            [execution("started", source=foreign)],
        )


def test_execution_cannot_cite_recovery_authority_on_an_ordinary_generation():
    with pytest.raises(AttemptIntegrityError, match="no retained recovery authority"):
        replay(start_clock(), [execution("prepared", recovery_authority_id="missing")])


def test_execution_cannot_prepare_under_stale_generation():
    with pytest.raises(AttemptIntegrityError, match="generation is stale"):
        replay(start_clock(), [execution("prepared", generation=2)])


def test_preparation_cannot_claim_a_future_admission_commit():
    with pytest.raises(AttemptIntegrityError, match="cannot name its admission commit"):
        replay(start_clock(), [execution("prepared", admission_commit="d" * 40)])


def test_admission_cannot_advance_without_retained_proof():
    with pytest.raises(
        AttemptIntegrityError, match="admission requires retained proof"
    ):
        replay(start_clock(), [execution("prepared")], [execution("admitted")])


@pytest.mark.parametrize(
    "result",
    [
        pytest.param({"proof": "result-proof", "outcome": None}, id="missing-outcome"),
        pytest.param({"proof": None, "outcome": "completed"}, id="missing-proof"),
    ],
)
def test_terminal_execution_requires_both_outcome_and_proof(result):
    with pytest.raises(AttemptIntegrityError, match="requires outcome and proof"):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", proof="admission")],
            [execution("started")],
            [execution("finished", **result)],
        )


def test_result_cannot_replace_the_admission_commit_used_for_dispatch():
    with pytest.raises(
        AttemptIntegrityError, match="disagrees with its admission commit"
    ):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", proof="admission")],
            [execution("started")],
            [execution("finished", admission_commit="e" * 40, proof="result")],
        )


@pytest.mark.parametrize("missing", ["plan_generation", "source", "binding"])
def test_active_attempt_requires_all_launch_authority(missing):
    event, data = START
    _, boundary = start_clock()
    with pytest.raises(AttemptIntegrityError, match="lacks plan and binding evidence"):
        replay(((event, {**data, missing: None}), boundary))


def test_open_attempt_cannot_be_replaced_by_another_start():
    event, data = START
    new_attempt = event, {**data, "attempt": "a2"}
    start_boundary = clock("e3", None, "active")
    kind, boundary = start_boundary
    with pytest.raises(
        AttemptIntegrityError, match="start conflicts with retained attempt"
    ):
        replay(start_clock(), (new_attempt, (kind, {**boundary, "attempt": "a2"})))


def test_execution_cannot_prepare_after_its_attempt_is_closed():
    closure = [
        fact(
            "core.attempt.closed",
            from_clock="active",
            disposition="delivered",
            reason="accepted",
        ),
        clock("e3", "active", "terminal-closed", used=40),
    ]
    with pytest.raises(AttemptIntegrityError, match="lacks the current active binding"):
        replay(start_clock(), closure, [execution("prepared")])


def test_clock_boundary_cannot_move_back_before_the_retained_timestamp():
    start, first_clock, pause, stale_resume = records(
        start_clock(),
        [
            clock(
                "earlier-cause",
                "active",
                "review-stopped",
                used=20,
                observed_at="2026-11-27T09:00:00Z",
            )
        ],
        [
            clock(
                "later-cause",
                "review-stopped",
                "active",
                used=20,
                observed_at="2026-11-27T08:59:00Z",
            )
        ],
    )
    # This tests the reducer's cross-operation order independently of the
    # per-operation cause and timestamp agreement already checked by the batch.
    state = fold_attempt(StoryState(), start)
    state = fold_attempt(state, first_clock)
    state = fold_attempt(state, pause)
    with pytest.raises(
        AttemptIntegrityError, match="boundary precedes the retained boundary"
    ):
        fold_attempt(state, stale_resume)
