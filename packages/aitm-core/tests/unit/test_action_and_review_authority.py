"""Pin action scope and effective-review identity in the evidence reducer."""

import pytest

from aitm_core.events import ReducerRegistry, fold
from aitm_core.reducers.evidence import EvidenceIntegrityError, fold_evidence
from tests.unit.test_c56 import DIGEST, LEGACY, SOURCE, fact, records

SCOPE = {
    "origin_operation": "op1",
    "owner": "board",
    "action_id": "sync",
    "target_version": 1,
    "owner_version": "3",
    "attempt": None,
    "workflow": LEGACY,
}
REVIEW = {
    "review_id": "source-review",
    "attempt": "a1",
    "generation": 1,
    "source": SOURCE,
}


def pending(**changes):
    return fact("action.pending", **(SCOPE | changes))


def completed(**changes):
    return fact(
        "action.completed",
        **(SCOPE | {"outcome": "completed", "proof_refs": ["proof-1"]} | changes),
    )


def recorded(**changes):
    return fact(
        "review.recorded",
        **(
            REVIEW
            | {"verdict": "pass", "reviewer_ref": "reviewer", "proof_refs": ["receipt"]}
            | changes
        ),
    )


def activated(**changes):
    return fact(
        "review.activated",
        **(
            REVIEW
            | {
                "policy_digest": DIGEST,
                "proof_refs": ["tested-source"],
                "reason": "qualified",
            }
            | changes
        ),
    )


def invalidated():
    event, data = activated()
    assert event == "core.review.activated"
    return fact("review.invalidated", **data, resumes_execution=False)


def replay_evidence(*events):
    # The separate attempt suite checks each clock-boundary pair. Isolate the
    # evidence reducer's authority here while still replaying its causal stream.
    registry = ReducerRegistry()
    for kind in dict.fromkeys(kind for kind, _ in events):
        registry.register(kind, fold_evidence)
    return fold(records(*([event] for event in events)), registry).domains["evidence"]


def test_pending_action_must_originate_in_its_enclosing_operation():
    with pytest.raises(EvidenceIntegrityError, match="conflicts with its operation"):
        replay_evidence(pending(origin_operation="op-other"))


def test_action_result_requires_a_retained_pending_action():
    with pytest.raises(EvidenceIntegrityError, match="lacks a matching pending action"):
        replay_evidence(completed())


@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"owner_version": "4"}, id="different-owner-version"),
        pytest.param({"target_version": 2}, id="different-target-version"),
        pytest.param({"attempt": "unrelated-attempt"}, id="different-attempt"),
        pytest.param(
            {"workflow": {**LEGACY, "state_id": "unrelated-state"}},
            id="different-workflow-state",
        ),
    ],
)
def test_action_result_cannot_use_scope_from_another_pending_action(change):
    with pytest.raises(EvidenceIntegrityError, match="lacks a matching pending action"):
        replay_evidence(pending(), completed(**change))


def test_receipt_id_cannot_replace_original_review_participant():
    with pytest.raises(EvidenceIntegrityError, match="receipt has conflicting data"):
        replay_evidence(recorded(), recorded(reviewer_ref="later-reviewer"))


def test_source_review_cannot_activate_without_retained_receipt():
    with pytest.raises(EvidenceIntegrityError, match="matching passing receipt"):
        replay_evidence(activated())


def test_changes_required_receipt_cannot_become_effective():
    with pytest.raises(EvidenceIntegrityError, match="matching passing receipt"):
        replay_evidence(recorded(verdict="changes"), activated())


def test_source_review_cannot_activate_for_another_attempt_generation():
    with pytest.raises(EvidenceIntegrityError, match="matching passing receipt"):
        replay_evidence(recorded(), activated(generation=2))


def test_effective_review_requires_explicit_invalidation_before_reactivation():
    with pytest.raises(EvidenceIntegrityError, match="already effective"):
        replay_evidence(recorded(), activated(), activated())


def test_review_invalidation_requires_an_effective_receipt():
    with pytest.raises(
        EvidenceIntegrityError, match="lacks a matching effective review"
    ):
        replay_evidence(recorded(), invalidated())
