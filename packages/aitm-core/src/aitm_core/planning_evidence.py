"""Transactional pickup evidence and attempt reconciliation."""

from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256

from pydantic import BaseModel

from aitm_core.attempts import attach_attempt_evidence
from aitm_core.documents import canonicalize
from aitm_core.estimates import observe_estimate
from aitm_core.events import StoryState, UnavailableReducer, core_reducers, fold
from aitm_core.jit import Coverage, prepare_jit
from aitm_core.models.attempts import AttemptState, SourceSnapshot
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventEnvelope
from aitm_core.models.lifecycle import DocumentAcceptance, Estimate, LifecycleState
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
    story_scope,
)
from aitm_core.services import (
    UnavailablePort,
)
from aitm_core.store.backend import Backend, OperationResult, Snapshot


@dataclass(frozen=True, slots=True)
class PlanningContext:
    backend: Backend
    snapshot: Snapshot
    owner: OperationOwner
    policy_digest: str
    operation_id: str
    at: str
    publish: Callable[[Operation, Snapshot], OperationResult]
    scope: StoryRef
    source: SourceSnapshot | None = None


def _result(identity: str, outcome: LocalOutcome, reason: str) -> CommandResult:
    return CommandResult(operation_id=identity, local=outcome, evidence=(reason,))


class PlanningRefusal(ValueError):
    """The bound planning evidence is insufficient for this operation."""


def _state(context: PlanningContext) -> tuple[bytes, StoryState, LifecycleState]:
    path = story_event_path(context.scope.story)
    raw = context.backend.read(context.snapshot, (path,))[path]
    if not raw:
        raise PlanningRefusal("No story history.")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    lifecycle = state.domains.get("lifecycle")
    if state.story_id != context.scope.story or not isinstance(
        lifecycle, LifecycleState
    ):
        raise PlanningRefusal("No current story lifecycle.")
    return raw, state, lifecycle


def _document(
    context: PlanningContext, accepted: DocumentAcceptance | None
) -> ReadExpectation:
    if accepted is None or accepted.policy_digest != context.policy_digest:
        raise PlanningRefusal("No current accepted document.")
    if story_scope(accepted.path) != context.scope.story:
        raise ValueError("Accepted document belongs to another story.")
    raw = context.backend.read(context.snapshot, (accepted.path,))[accepted.path]
    if not raw:
        raise PlanningRefusal("Accepted document is unavailable.")
    identity = canonicalize(raw, DocumentSchema())
    if identity.canonical_sha256 != accepted.canonical_digest:
        raise PlanningRefusal("Accepted document content changed.")
    return ReadExpectation(path=accepted.path, digest=identity.raw_sha256)


def _persist(
    context: PlanningContext,
    raw: bytes,
    state: StoryState,
    intent: str,
    event_type: str,
    fact: BaseModel,
    *extra_reads: ReadExpectation,
    already_retained: bool = False,
) -> OperationResult:
    story = context.scope.story
    event = (
        EventEnvelope(
            v=1,
            id=f"{context.operation_id}:planning",
            ts=context.at,
            type=event_type,
            story=story,
            actor=context.owner.actor,
            operation_id=context.operation_id,
            sequence=state.next_sequence,
            prior_log_digest=state.prior_log_digest,
            data=fact.model_dump(mode="json"),
            policy_digest=context.policy_digest,
        )
        .model_dump_json(exclude_none=True)
        .encode()
    )
    reads = (
        ReadExpectation(path=story_event_path(story), digest=sha256(raw).hexdigest()),
        *extra_reads,
    )
    operation = Operation(
        operation_id=context.operation_id,
        owner=context.owner,
        policy_digest=context.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind=intent,
            version=1,
            related_preconditions=reads,
            payload=fact.model_dump_json().encode(),
        ),
        change=RelatedWriteSet(
            read_set=reads,
            events=()
            if already_retained
            else (EventAppend(story=story, records=(event,)),),
        ),
    )
    return context.publish(operation, context.snapshot)


def _refuse(context: PlanningContext, error: Exception) -> OperationResult:
    command = _error(context.operation_id, error)
    return OperationResult(command, context.snapshot, str(error))


def reconcile_attempt(
    context: PlanningContext, *, attempt: str, generation: int
) -> OperationResult:
    """Attach evidence through normal preflight and CAS."""
    try:
        raw, state, lifecycle = _state(context)
        attempts = state.domains.get("attempts")
        if (
            not isinstance(attempts, AttemptState)
            or attempts.current_attempt != attempt
            or context.owner.binding is None
            or context.source is None
        ):
            raise PlanningRefusal("No current bound attempt.")
        plan = lifecycle.accepted_documents.get("plan")
        proof = _document(context, plan)
        assert plan is not None
        current = attempts.attempts[attempt]
        try:
            attached = attach_attempt_evidence(
                current,
                attempt=attempt,
                generation=generation,
                plan_generation=plan.plan_generation,
                source=context.source,
                binding=context.owner.binding,
            )
        except ValueError as error:
            raise PlanningRefusal(str(error)) from error
        fact = attached.reconciliation
        assert fact is not None
        return _persist(
            context,
            raw,
            state,
            "attempt.reconcile",
            "core.attempt.reconciled",
            fact,
            proof,
            already_retained=fact == current.reconciliation,
        )
    except (UnavailableReducer, ValueError) as error:
        return _refuse(context, error)


def record_jit(context: PlanningContext, coverage: Coverage) -> OperationResult:
    try:
        raw, state, lifecycle = _state(context)
        plan = lifecycle.accepted_documents.get("plan")
        proof = _document(context, plan)
        assert plan is not None
        if context.source != coverage.baseline.snapshot:
            raise PlanningRefusal("JIT baseline disagrees with the observed source.")
        attempts = state.domains.get("attempts")
        if isinstance(attempts, AttemptState) and attempts.current_attempt:
            current = attempts.attempts[attempts.current_attempt]
            if current.closed or (
                attempts.current_attempt,
                current.generation,
            ) != (coverage.attempt, coverage.attempt_generation):
                raise PlanningRefusal("JIT names a stale attempt or generation.")
        try:
            fact = prepare_jit(coverage, plan)
        except ValueError as error:
            raise PlanningRefusal(str(error)) from error
        return _persist(
            context,
            raw,
            state,
            "jit.record",
            "core.jit.recorded",
            fact,
            proof,
            already_retained=fact == lifecycle.jit,
        )
    except (UnavailableReducer, ValueError) as error:
        return _refuse(context, error)


def run_estimate(
    context: PlanningContext,
    estimate: Estimate,
    *,
    source: str,
    rationale: str,
) -> OperationResult:
    try:
        raw, state, lifecycle = _state(context)
        proof = (
            (_document(context, lifecycle.accepted_documents.get("design")),)
            if estimate.phase == "refine"
            else ()
        )
        try:
            fact = observe_estimate(
                lifecycle.estimates,
                estimate,
                kind=lifecycle.kind,
                design_accepted=bool(proof),
                source=source,
                rationale=rationale,
            )[estimate.phase]
        except ValueError as error:
            raise PlanningRefusal(str(error)) from error
        return _persist(
            context, raw, state, "estimate.record", "core.estimate.set", fact, *proof
        )
    except (PlanningRefusal, UnavailableReducer, ValueError) as error:
        return _refuse(context, error)


def _error(identity: str, error: Exception) -> CommandResult:
    if isinstance(error, PlanningRefusal):
        outcome = LocalOutcome.REFUSED
    elif isinstance(error, (UnavailableReducer, UnavailablePort)):
        outcome = LocalOutcome.UNAVAILABLE
    else:
        outcome = LocalOutcome.INTEGRITY_ERROR
    return _result(identity, outcome, str(error))
