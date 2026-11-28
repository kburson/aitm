"""C94 separates local JIT detail from material changes to reviewed scope."""

from dataclasses import replace
from hashlib import sha256

import pytest
import rfc8785

from aitm_core.machine.jit_scope import (
    AcceptedEntry,
    AcceptedReconciliation,
    JitScopeRecord,
    OwnerDecision,
    ReconciledPlan,
    ScopeReviews,
    evaluate_jit_scope,
)
from aitm_core.models.decomposition import PlanEntry
from aitm_core.models.identity import PlanEntrySource, SourceDescription
from aitm_core.models.lifecycle import DocumentAcceptance

PLAN = "a" * 64
NEW_PLAN = "b" * 64
POLICY = "c" * 64
PATH = ".aitm/stories/004/478/plan/slice.md"
PARENT = PlanEntry(
    kind="story",
    description=SourceDescription(title="C94", scope="Material changes"),
    agent_hours=4,
    size="S",
    priority="P1",
    deliverable="Required scope evaluation",
    verification="Unit scope matrix",
    acceptance_criteria=("Current review required",),
    dependencies=("c93",),
    cross_child_commitments=("preserve-c93-pin",),
)
ENTRY = PlanEntrySource(
    parent=478,
    entry_key="c94",
    design_digest="d" * 64,
    plan_digest=PLAN,
    entry_digest=PARENT.digest,
    descriptor=PARENT.description,
)
ACCEPTED = AcceptedEntry(ENTRY, PARENT, PATH, 1, POLICY, "plan-owner")
RECORD = JitScopeRecord(ENTRY, PARENT, "Use the existing typed acceptance result.")


def test_recorded_in_scope_detail_needs_no_second_plan_review():
    adjusted = replace(RECORD, proposed=PARENT.model_copy(update={"agent_hours": 3.5}))
    result = evaluate_jit_scope(ACCEPTED, adjusted, ScopeReviews())
    assert result.status == "current"
    assert not result.changes
    assert not result.review_refs
    assert (
        evaluate_jit_scope(
            replace(ACCEPTED, plan_path=".aitm/stories/004/477/plan/foreign.md"),
            adjusted,
            ScopeReviews(),
        ).status
        == "hold"
    )

    legacy = PARENT.model_copy(update={"cross_child_commitments": ()})
    original_fields = legacy.model_dump(
        mode="json", exclude={"cross_child_commitments"}
    )
    assert legacy.digest == sha256(rfc8785.dumps(original_fields)).hexdigest()


@pytest.mark.parametrize(
    ("field", "value", "category"),
    [
        ("deliverable", "Different output", "scope"),
        ("acceptance_criteria", ("Require something else",), "criteria"),
        ("dependencies", ("c72",), "commitments"),
        ("cross_child_commitments", ("new downstream promise",), "commitments"),
    ],
)
def test_each_material_change_holds_for_peer_review(field, value, category):
    proposed = PARENT.model_copy(update={field: value})
    result = evaluate_jit_scope(
        ACCEPTED, replace(RECORD, proposed=proposed), ScopeReviews()
    )
    assert result.status == "hold"
    assert result.changes == (category,)


def test_ambiguity_requires_current_plan_owner_resolution():
    record = replace(RECORD, ambiguous=True)
    result = evaluate_jit_scope(ACCEPTED, record, ScopeReviews())
    assert result.status == "hold"
    assert result.changes == ("ambiguity",)
    decision = OwnerDecision(
        "plan-owner", record.digest, POLICY, "in-scope", "decision-1"
    )
    assert (
        evaluate_jit_scope(
            ACCEPTED, record, ScopeReviews(owner_decision=decision)
        ).status
        == "current"
    )
    for invalid in (
        replace(decision, owner="unknown"),
        replace(decision, adjustment_digest="a" * 64),
    ):
        assert (
            evaluate_jit_scope(
                ACCEPTED, record, ScopeReviews(owner_decision=invalid)
            ).status
            == "hold"
        )
    changed_record = replace(record, checklist="Different adjustment")
    assert (
        evaluate_jit_scope(
            ACCEPTED, changed_record, ScopeReviews(owner_decision=decision)
        ).status
        == "hold"
    )


def test_material_change_requires_peer_acceptance_of_exact_reconciliation():
    proposed = PARENT.model_copy(update={"deliverable": "Reconciled output"})
    reconciled = ReconciledPlan(NEW_PLAN, 2)
    record = replace(RECORD, proposed=proposed, reconciliation=reconciled)
    source = ENTRY.model_copy(
        update={"plan_digest": NEW_PLAN, "entry_digest": proposed.digest}
    )
    review = DocumentAcceptance(
        role="plan",
        path=PATH,
        canonical_version="aitm.authored-content/v1",
        canonical_digest=NEW_PLAN,
        raw_digest="e" * 64,
        review_refs=("peer-2",),
        levels=("xpr",),
        policy_digest=POLICY,
        source_planning_sha="f" * 40,
        plan_generation=2,
    )
    evidence = AcceptedReconciliation(source, review)
    result = evaluate_jit_scope(ACCEPTED, record, ScopeReviews((evidence,)))
    assert result.status == "current"
    assert result.changes == ("scope",)
    assert result.review_refs == ("peer-2",)
    for invalid in (
        replace(
            evidence, accepted_plan=review.model_copy(update={"canonical_digest": PLAN})
        ),
        replace(
            evidence, accepted_plan=review.model_copy(update={"plan_generation": 1})
        ),
        replace(evidence, accepted_plan=review.model_copy(update={"levels": ("sar",)})),
        replace(
            evidence,
            accepted_plan=review.model_copy(update={"policy_digest": "e" * 64}),
        ),
        replace(evidence, entry=source.model_copy(update={"entry_key": "foreign"})),
        replace(
            evidence, entry=source.model_copy(update={"entry_digest": PARENT.digest})
        ),
    ):
        assert (
            evaluate_jit_scope(ACCEPTED, record, ScopeReviews((invalid,))).status
            == "hold"
        )
