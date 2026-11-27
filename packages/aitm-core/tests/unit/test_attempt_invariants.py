"""Exercise the causal execution reducer at retained identity and proof boundaries."""

import pytest

from aitm_core.reducers.attempts import AttemptIntegrityError
from tests.unit.test_c55 import SOURCE, START, execution, replay, start_clock


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
