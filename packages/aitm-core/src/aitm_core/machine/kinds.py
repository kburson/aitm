"""Kind policy resolves source, aggregate, and deliverable evidence separately."""

from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from typing import Literal, Protocol

from aitm_core.decomposition import DecompositionUnavailable, pin_accepted_document
from aitm_core.events import core_reducers, fold
from aitm_core.machine.guards import GuardCall, GuardDecision
from aitm_core.models.attempts import AttemptState, BindingPurpose, SourceSnapshot
from aitm_core.models.decomposition import DecompositionMap
from aitm_core.models.evidence import DeliverableValidated, DeliveryVerified
from aitm_core.models.lifecycle import LifecycleState, StoryKind
from aitm_core.models.operations import ReadExpectation, story_event_path
from aitm_core.reducers.evidence import EvidenceState

type Slot = Literal["admission", "implementation", "candidate", "closeout"]

KIND_EXIT_RULES = frozenset(
    {
        "core.dev.review-candidate-current",
        "core.closeout.complete",
        "core.closeout.terminal-disposition-valid",
        "core.delivery.verified",
    }
)


@dataclass(frozen=True, slots=True)
class Requirements:
    binding: BindingPurpose | None
    attempt: bool
    evidence: Literal["source", "deliverable", "aggregate"]


def kind_requirements(kind: StoryKind, slot: Slot) -> Requirements:
    """Select applicable evidence and authority for a configured boundary."""
    if kind == "epic":
        return Requirements(None, False, "aggregate")
    purpose = (
        BindingPurpose.DELIVERABLE if kind == "spike" else BindingPurpose.IMPLEMENTATION
    )
    return Requirements(
        purpose if slot == "implementation" else None,
        slot == "implementation",
        "deliverable" if kind == "spike" else "source",
    )


class AggregateEvidence(Protocol):
    def __call__(self, request: GuardCall) -> GuardDecision: ...


def _plan(call: GuardCall):
    plan = call.story.accepted_documents.get("plan")
    if plan is None or plan.policy_digest != call.policy_digest:
        raise DecompositionUnavailable("Current accepted plan is unavailable.")
    header, read = pin_accepted_document(
        call.story.story_id, plan, call.blobs.get(plan.path)
    )
    return plan, header, read


def _aggregate_scope(call: GuardCall) -> GuardDecision:
    story = call.story
    design = story.accepted_documents.get("design")
    if design is None or design.policy_digest != call.policy_digest:
        return GuardDecision("unavailable", "aggregate-design-unavailable")
    _, design_read = pin_accepted_document(
        story.story_id, design, call.blobs.get(design.path)
    )
    _, header, plan_read = _plan(call)
    entries = header.get("decomposition")
    if entries is None:
        return GuardDecision("unavailable", "accepted-decomposition-unavailable")
    accepted = DecompositionMap.model_validate_json(dumps(entries)).root
    if not accepted or not story.relationships.children:
        return GuardDecision("blocked", "accepted-child-scope-empty")
    found = set()
    reads = [design_read, plan_read]
    for child in story.relationships.children:
        path = story_event_path(child)
        raw = call.blobs.get(path)
        if raw is None:
            return GuardDecision(
                "unavailable", "child-evidence-unavailable", str(child)
            )
        record = fold(raw.splitlines(keepends=True), core_reducers())
        lifecycle = record.domains.get("lifecycle")
        if record.story_id != child or not isinstance(lifecycle, LifecycleState):
            raise ValueError("Child event stream has another identity.")
        graduate = lifecycle.graduation
        parent, separator, key = graduate.source_id.partition(":")
        entry = accepted.get(key)
        if (
            not separator
            or parent != str(story.story_id)
            or graduate.source_kind != "plan-entry"
            or graduate.parent != story.story_id
            or lifecycle.relationships.parent != story.story_id
            or entry is None
            or key in found
            or graduate.source_digest != entry.digest
        ):
            return GuardDecision("blocked", "stale-child-scope", str(child))
        found.add(key)
        reads.append(ReadExpectation(path=path, digest=sha256(raw).hexdigest()))
    if found != accepted.keys():
        return GuardDecision("blocked", "accepted-child-scope-incomplete")
    return GuardDecision("pass", "accepted-child-scope-current", reads=tuple(reads))


def _spike_exit(call: GuardCall) -> GuardDecision:
    raw = call.blobs.get(story_event_path(call.story.story_id))
    if not raw:
        return GuardDecision("unavailable", "deliverable-history-unavailable")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    attempts, evidence = state.domains.get("attempts"), state.domains.get("evidence")
    if (
        not isinstance(attempts, AttemptState)
        or attempts.current_attempt is None
        or not isinstance(evidence, EvidenceState)
    ):
        return GuardDecision("unavailable", "deliverable-attempt-unavailable")
    active = attempts.attempts[attempts.current_attempt]
    current = [
        item
        for item in call.story.deliverables.values()
        if item.attempt == attempts.current_attempt
    ]
    if active.closed or len(current) != 1 or active.source is None:
        return GuardDecision("unavailable", "current-deliverable-unavailable")
    deliverable = current[0]
    content = call.blobs.get(deliverable.path)
    if (
        content is None
        or sha256(content).hexdigest() != deliverable.raw_digest
        or deliverable.source_snapshot != active.source.commit
    ):
        return GuardDecision("blocked", "deliverable-content-drifted")

    def current_attempt(item):
        return (
            item.attempt == active.started.attempt
            and item.generation == active.generation
        )

    for row in reversed(evidence.facts.get("core.deliverable.validated", ())):
        check = row.payload
        if (
            isinstance(check, DeliverableValidated)
            and current_attempt(check)
            and check.deliverable_id == deliverable.deliverable_id
        ):
            if (
                check.result != "pass"
                or check.deliverable_digest != deliverable.canonical_digest
                or check.input_baseline != deliverable.source_snapshot
                or check.check_policy != call.policy_digest
            ):
                return GuardDecision(
                    "blocked", "deliverable-validation-stale-or-failed"
                )
            break
    else:
        return GuardDecision("unavailable", "deliverable-validation-unavailable")
    if call.identifier == "core.dev.review-candidate-current":
        return GuardDecision("pass", "validated-deliverable-current")
    digest = deliverable.canonical_digest
    reviews = {}
    for label in ("core.review.activated", "core.review.invalidated"):
        for row in evidence.facts.get(label, ()):
            item = row.payload
            if current_attempt(item) and (
                item.review_id not in reviews
                or row.envelope.sequence > reviews[item.review_id].envelope.sequence
            ):
                reviews[item.review_id] = row
    if not any(
        row.envelope.type == "core.review.activated"
        and row.payload.source == active.source
        and row.payload.policy_digest == call.policy_digest
        and digest in row.payload.proof_refs
        for row in reviews.values()
    ):
        return GuardDecision("unavailable", "current-deliverable-review-unavailable")
    archived = any(
        isinstance(row.payload, DeliveryVerified)
        and current_attempt(row.payload)
        and row.payload.source is None
        and row.payload.deliverable_digest == digest
        and (row.envelope.policy_digest == call.policy_digest)
        for row in evidence.facts.get("core.delivery.verified", ())
    )
    return GuardDecision(
        "pass" if archived else "unavailable",
        "deliverable-archive-current"
        if archived
        else "deliverable-archive-unavailable",
    )


def evaluate_kind_guard(
    call: GuardCall,
    *,
    source: SourceSnapshot | None,
    aggregate: AggregateEvidence | None,
) -> GuardDecision:
    """Read domain evidence while leaving uninstalled authorities explicitly unavailable."""
    kind = kind_requirements(call.story.kind, "implementation")
    if call.identifier == "core.plan.admission-ready":
        return GuardDecision("pass", "kind-applicable-to-plan")
    try:
        if call.identifier == "core.plan.pickup-basis-current":
            if kind.evidence == "aggregate":
                return _aggregate_scope(call)
            if call.story.graduation.source_kind == "plan-entry":
                return GuardDecision(
                    "unavailable", "qualified-child-jit-port-unavailable"
                )
            plan, header, read = _plan(call)
            if (
                source is None
                or header.get("source")
                != f"{kind.evidence}:{source.commit}:{source.tree}"
            ):
                return GuardDecision("blocked", "accepted-plan-source-drifted")
            return GuardDecision(
                "pass",
                "accepted-pickup-basis-current",
                reads=(read,),
                plan_generation=plan.plan_generation,
                source=source,
            )
        if kind.evidence == "aggregate" and call.identifier in KIND_EXIT_RULES:
            scope = _aggregate_scope(call)
            if scope.status != "pass":
                return scope
            if aggregate is None:
                return GuardDecision(
                    "unavailable", "aggregate-evidence-port-unavailable"
                )
            return aggregate(call)
        if kind.evidence == "deliverable" and call.identifier in KIND_EXIT_RULES:
            return _spike_exit(call)
    except DecompositionUnavailable as error:
        return GuardDecision("unavailable", "kind-evidence-unavailable", str(error))
    return GuardDecision("unavailable", "kind-capability-unavailable", call.identifier)
