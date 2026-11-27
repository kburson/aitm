"""Exercise causal and typed review evidence boundaries without external services."""

from json import dumps, loads

import pytest

from aitm_core.events import core_reducers, fold
from aitm_core.reducers.evidence import EvidenceIntegrityError
from tests.unit.test_c56 import AGENT, DIGEST, LEGACY, STAMP, fact, records

DOCUMENT = {"record_id": "review-1", "level": "sar", "path": "plans/current.md"}
LATER = "2026-11-27T10:00:00Z"
EARLIER = "2026-11-27T08:00:00Z"


def opening(**changes):
    data = {
        **DOCUMENT,
        "raw_digest": DIGEST,
        "content_digest": DIGEST,
        "opened_at": STAMP,
        "opened_by": {"kind": "agent", "harness": "fixture"},
        "source_operation": "op1",
    }
    return fact("doc-review.opened", **(data | changes))


def turn(**changes):
    data = {
        **DOCUMENT,
        "round": 1,
        "role": "reviewer",
        "agent": AGENT,
        "started_at": None,
        "submitted_at": STAMP,
        "start_basis": "unknown",
        "input_digest": DIGEST,
        "response_path": "reviews/response.md",
        "source_digest": DIGEST,
        "finding_ids": [],
        "decision": "pass",
    }
    return fact("doc-review.submitted", **(data | changes))


def completion(**changes):
    data = {
        **DOCUMENT,
        "rounds": 1,
        "outcome": "exhausted",
        "base_digest": DIGEST,
        "final_digest": DIGEST,
        "started_at": STAMP,
        "ended_at": LATER,
        "manifest_path": "reviews/manifest.json",
    }
    return fact("doc-review.completed", **(data | changes))


def test_document_review_opening_must_bind_its_own_operation():
    with pytest.raises(
        EvidenceIntegrityError, match="disagrees with its source operation"
    ):
        fold(records([opening(source_operation="unrelated")]), core_reducers())


def test_a_second_operation_cannot_replace_a_review_opening():
    with pytest.raises(EvidenceIntegrityError, match="competing openings"):
        fold(records([opening()], [opening(source_operation="op2")]), core_reducers())


@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"level": "xpr"}, id="different-review-level"),
        pytest.param({"path": "plans/other.md"}, id="different-document"),
    ],
)
def test_document_review_id_preserves_path_and_level(change):
    with pytest.raises(EvidenceIntegrityError, match="another document or level"):
        fold(records([opening()], [turn(**change)]), core_reducers())


@pytest.mark.parametrize("missing", ["input_digest", "decision"])
def test_reviewer_turn_needs_both_input_and_a_decision(missing):
    with pytest.raises(EvidenceIntegrityError, match="reviewer turn lacks"):
        fold(records([opening()], [turn(**{missing: None})]), core_reducers())


def test_author_turn_needs_a_patch_for_its_output():
    author = turn(role="author", output_digest=DIGEST, decision=None)
    with pytest.raises(EvidenceIntegrityError, match="author turn lacks"):
        fold(records([opening()], [author]), core_reducers())


def test_author_turn_cannot_issue_a_reviewer_decision():
    author = turn(
        role="author", output_digest=DIGEST, patch_path="reviews/update.patch"
    )
    with pytest.raises(EvidenceIntegrityError, match="includes a decision"):
        fold(records([opening()], [author]), core_reducers())


def test_observed_review_start_requires_the_source_reference():
    claimed = turn(start_basis="claim", started_at=EARLIER)
    with pytest.raises(EvidenceIntegrityError, match="lacks evidence for its start"):
        fold(records([opening()], [claimed]), core_reducers())


def test_review_start_cannot_follow_its_submission():
    late = turn(start_basis="claim", started_at=LATER, start_ref="claim-1")
    with pytest.raises(EvidenceIntegrityError, match="turn has an inverted interval"):
        fold(records([opening()], [late]), core_reducers())


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        pytest.param({"base_digest": "b" * 64}, "opening input", id="different-input"),
        pytest.param(
            {"started_at": EARLIER}, "opening time", id="different-opening-time"
        ),
        pytest.param(
            {"ended_at": EARLIER}, "inverted interval", id="end-before-opening"
        ),
    ],
)
def test_completion_cannot_overwrite_opening_evidence(change, reason):
    with pytest.raises(EvidenceIntegrityError, match=reason):
        fold(records([opening()], [completion(**change)]), core_reducers())


def test_completion_must_include_existing_review_rounds():
    with pytest.raises(EvidenceIntegrityError, match="omits retained rounds"):
        fold(records([opening()], [turn(round=2)], [completion()]), core_reducers())


def test_completed_review_cannot_acquire_turns_outside_its_scope():
    with pytest.raises(EvidenceIntegrityError, match="exceeds the recorded completion"):
        fold(records([opening()], [completion()], [turn(round=2)]), core_reducers())


@pytest.mark.parametrize(
    "field",
    ["operation", "policy_digest", "read_set_digest"],
)
def test_guard_fact_must_agree_with_its_enclosing_provenance(field):
    guard = {
        "operation": "op1",
        "read_set_digest": DIGEST,
        "policy_digest": DIGEST,
        "workflow": LEGACY,
        "slot": "ready.enter",
        "guard": "fixture.guard",
        "guard_version": "1",
        "ok": True,
        "code": "validated",
        "mode": "enforce",
    }
    mismatch = "other-operation" if field == "operation" else "b" * 64
    (raw,) = records([fact("guard.evaluated", **(guard | {field: mismatch}))])
    envelope = {**loads(raw), "read_set_digest": DIGEST, "policy_digest": DIGEST}
    with pytest.raises(EvidenceIntegrityError, match="guard provenance"):
        fold([dumps(envelope).encode()], core_reducers())
