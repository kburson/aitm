"""Evaluate a prospective child JIT change against current accepted scope."""

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

import rfc8785

from aitm_core.models.binding import StoryRef, allows_authored
from aitm_core.models.decomposition import PlanEntry
from aitm_core.models.identity import PlanEntrySource
from aitm_core.models.lifecycle import DocumentAcceptance

Change = Literal["scope", "criteria", "commitments", "ambiguity"]


@dataclass(frozen=True, slots=True)
class AcceptedEntry:
    """Frozen parent entry and the current plan's acceptance coordinates."""

    source: PlanEntrySource
    entry: PlanEntry
    plan_path: str
    plan_generation: int
    policy_digest: str
    scope_owner: str | None = None


@dataclass(frozen=True, slots=True)
class ReconciledPlan:
    digest: str
    generation: int


@dataclass(frozen=True, slots=True)
class JitScopeRecord:
    basis: PlanEntrySource
    proposed: PlanEntry
    checklist: str
    ambiguous: bool = False
    reconciliation: ReconciledPlan | None = None

    @property
    def digest(self) -> str:
        target = self.reconciliation
        return sha256(
            rfc8785.dumps(
                {
                    "basis": self.basis.model_dump(mode="json"),
                    "proposed": self.proposed.digest,
                    "checklist": self.checklist,
                    "ambiguous": self.ambiguous,
                    "reconciliation": [target.digest, target.generation]
                    if target
                    else None,
                }
            )
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class OwnerDecision:
    """A recorded decision supplied by the authorized scope-owner reader."""

    owner: str
    adjustment_digest: str
    policy_digest: str
    decision: Literal["in-scope", "material"]
    evidence_ref: str


@dataclass(frozen=True, slots=True)
class AcceptedReconciliation:
    """Pinned C26 acceptance and the entry from that same reviewed plan."""

    entry: PlanEntrySource
    accepted_plan: DocumentAcceptance


@dataclass(frozen=True, slots=True)
class ScopeReviews:
    """Qualified observations from the planning store and scope authority."""

    accepted: tuple[AcceptedReconciliation, ...] = ()
    owner_decision: OwnerDecision | None = None


@dataclass(frozen=True, slots=True)
class ScopeResult:
    status: Literal["current", "hold"]
    changes: tuple[Change, ...] = ()
    review_refs: tuple[str, ...] = ()
    owner_ref: str | None = None
    reason: str | None = None


def _material_changes(before: PlanEntry, after: PlanEntry) -> tuple[Change, ...]:
    changes: list[Change] = []
    if (before.kind, before.description, before.deliverable) != (
        after.kind,
        after.description,
        after.deliverable,
    ):
        changes.append("scope")
    if (before.acceptance_criteria, before.verification) != (
        after.acceptance_criteria,
        after.verification,
    ):
        changes.append("criteria")
    if (before.dependencies, before.cross_child_commitments) != (
        after.dependencies,
        after.cross_child_commitments,
    ):
        changes.append("commitments")
    return tuple(changes)


def _qualifies(
    parent: AcceptedEntry, record: JitScopeRecord, review: AcceptedReconciliation
) -> bool:
    target = record.reconciliation
    if target is None:
        return False
    accepted = review.accepted_plan
    entry = review.entry
    return (
        target.digest != parent.source.plan_digest
        and target.generation > parent.plan_generation
        and accepted.role == "plan"
        and accepted.path == parent.plan_path
        and accepted.canonical_digest == target.digest == entry.plan_digest
        and accepted.plan_generation == target.generation
        and accepted.policy_digest == parent.policy_digest
        and bool(set(accepted.levels) & {"spr", "xpr"})
        and all(ref.strip() for ref in accepted.review_refs)
        and entry.parent == parent.source.parent
        and entry.entry_key == parent.source.entry_key
        and entry.entry_digest == record.proposed.digest
        and entry.descriptor == record.proposed.description
    )


def evaluate_jit_scope(
    parent_entry: AcceptedEntry,
    jit_record: JitScopeRecord,
    reviews: ScopeReviews,
) -> ScopeResult:
    """Hold material changes pending peer acceptance of the exact reconciled plan."""
    parent = parent_entry
    if (
        jit_record.basis != parent.source
        or parent.source.entry_digest != parent.entry.digest
        or parent.source.descriptor != parent.entry.description
        or not allows_authored(StoryRef(story=parent.source.parent), parent.plan_path)
        or parent.plan_path.split("/")[4] != "plan"
        or not jit_record.checklist.strip()
    ):
        return ScopeResult(
            "hold", reason="JIT is missing its exact accepted entry or checklist"
        )
    changes = _material_changes(parent.entry, jit_record.proposed)
    owner_ref = None
    if jit_record.ambiguous:
        decision = reviews.owner_decision
        if (
            decision is None
            or parent.scope_owner is None
            or not parent.scope_owner.strip()
            or decision.owner != parent.scope_owner
            or decision.policy_digest != parent.policy_digest
            or decision.adjustment_digest != jit_record.digest
            or not decision.evidence_ref.strip()
            or decision.decision not in ("in-scope", "material")
        ):
            return ScopeResult(
                "hold",
                (*changes, "ambiguity"),
                reason="current plan-owner decision is required",
            )
        owner_ref = decision.evidence_ref
        if decision.decision == "material" and not changes:
            changes = ("ambiguity",)
    if not changes:
        return ScopeResult("current", owner_ref=owner_ref)
    for review in reviews.accepted:
        if _qualifies(parent, jit_record, review):
            return ScopeResult(
                "current", changes, review.accepted_plan.review_refs, owner_ref
            )
    return ScopeResult(
        "hold",
        changes,
        owner_ref=owner_ref,
        reason="peer acceptance of the exact reconciled parent plan is required",
    )
