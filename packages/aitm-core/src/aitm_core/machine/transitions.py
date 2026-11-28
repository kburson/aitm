"""Resolve and record a configured transition against one pinned read set."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
from json import dumps
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel

from aitm_core.events import StoryState, UnavailableReducer, core_reducers, fold
from aitm_core.ext.api import DirectiveRegistration
from aitm_core.ext.registry import Registry
from aitm_core.machine.guards import (
    GuardCall,
    GuardDecision,
    GuardPhase,
    ImplementationBinding,
)
from aitm_core.machine.obligations import (
    HOSTED_DELIVERY,
    DeliveryContract,
    validate_profile,
)
from aitm_core.machine.profile import WorkflowEdge, WorkflowProfile
from aitm_core.models.attempts import (
    AttemptStarted,
    AttemptState,
    ClockChanged,
    SourceSnapshot,
)
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.events import EventEnvelope, validate_envelope
from aitm_core.models.evidence import ActionScope, GuardEvaluated
from aitm_core.models.lifecycle import LifecycleState, StateChange, WorkflowObservation
from aitm_core.models.lifecycle import WorkflowEdge as RecordedEdge
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.services import ServicePorts, UnavailablePort
from aitm_core.store.backend import (
    Backend,
    OperationContext,
    OperationResult,
    Snapshot,
    _preflight,
)

TRANSITION_INTENT = "state.transition"
type GuardMode = Literal["enforce", "advisory"]
type Direction = Literal["forward", "rework"]
type Phase = Callable[[], CommandResult | None]


@dataclass(frozen=True, slots=True)
class TransitionRequest:
    story: int
    operation_id: str
    owner: OperationOwner
    at: str
    backend: Backend
    profile: WorkflowProfile
    registry: Registry
    policy_digest: str
    mode: GuardMode
    guard: Callable[[GuardCall], GuardDecision]
    allowance_millis: int
    contract: DeliveryContract = HOSTED_DELIVERY
    direction: Direction = "forward"
    target: str | None = None
    reason: str | None = None
    source: SourceSnapshot | None = None
    binding_ref: str | None = None
    binding_attempt: str | None = None
    latest_snapshot: Callable[[], Snapshot] | None = None
    before_sync: Phase | None = None
    sync: Phase | None = None
    transact: Callable[[Operation, Snapshot], OperationResult] | None = None


@dataclass(frozen=True, slots=True)
class TransitionExplanation:
    snapshot: Snapshot
    source: str | None = None
    target: str | None = None
    operation: str | None = None
    guards: tuple[GuardEvaluated, ...] = ()
    outcome: LocalOutcome = LocalOutcome.COMPLETED
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class _Evaluation:
    details: TransitionExplanation
    edge: WorkflowEdge | None = None
    operation: Operation | None = None


def _read(request: TransitionRequest, snapshot: Snapshot):
    path = story_event_path(request.story)
    raw = request.backend.read(snapshot, (path,))[path]
    if not raw:
        raise ValueError("story history is missing")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    lifecycle = state.domains.get("lifecycle")
    if state.story_id != request.story or not isinstance(lifecycle, LifecycleState):
        raise ValueError("story lifecycle is invalid")
    return path, raw, state, lifecycle


def _snapshot(request: TransitionRequest) -> Snapshot:
    return (request.latest_snapshot or request.backend.snapshot)()


def _find_edge(request: TransitionRequest, current: str) -> WorkflowEdge | None:
    edges = (
        request.profile.ordinary_edges
        if request.direction == "forward"
        else (edge for edge in request.profile.transitions if edge.kind == "rework")
    )
    eligible = [
        edge
        for edge in edges
        if edge.source == current
        and (request.target is None or edge.target == request.target)
    ]
    return eligible[0] if len(eligible) == 1 else None


def _facts(request, snapshot, lifecycle, edge, raw, path, attempt):
    source, target = edge.source, edge.target
    profile_states = {entry.id: entry for entry in request.profile.states}
    related = tuple(
        dict.fromkeys(
            (
                *(story_event_path(n) for n in lifecycle.relationships.blocked_by),
                *(entry.path for entry in lifecycle.accepted_documents.values()),
            )
        )
    )
    inputs = {**request.backend.read(snapshot, related), path: raw}
    pinned_blobs = MappingProxyType(inputs)
    initial_reads = tuple(
        ReadExpectation(
            path=name, digest=sha256(blob).hexdigest() if blob is not None else None
        )
        for name, blob in inputs.items()
    )
    reads_by_path = {read.path: read for read in initial_reads}
    plan_generation = None
    binding = None
    phases: tuple[tuple[GuardPhase, tuple[str, ...]], ...] = (
        ("onExit", profile_states[source].on_exit if edge.kind != "rework" else ()),
        ("prepare", edge.prepare),
        ("edge", edge.guards),
        ("onEnter", profile_states[target].on_enter),
    )
    observation = WorkflowObservation(
        workflow_id=request.profile.id,
        revision=request.profile.source.digest,
        state_id=target,
        label=profile_states[target].label,
        terminal=target == request.profile.lifecycle.terminal,
    )
    observations = []
    for phase, identifiers in phases:
        for identifier in identifiers:
            registration = request.registry.resolve(identifier).registration
            slot = (
                registration.slot
                if isinstance(registration, DirectiveRegistration)
                else registration
            )
            if (
                slot is not None
                and slot.scope.story_kinds
                and lifecycle.kind not in slot.scope.story_kinds
            ):
                continue
            if slot is None:
                decision = GuardDecision("unavailable", "guard-unavailable", identifier)
                version = "unavailable"
            else:
                call = GuardCall(
                    identifier,
                    slot.version,
                    phase,
                    snapshot,
                    lifecycle,
                    edge,
                    pinned_blobs,
                    request.policy_digest,
                )
                try:
                    decision = request.guard(call)
                except UnavailablePort as error:
                    decision = GuardDecision(
                        "unavailable", "guard-unavailable", str(error)
                    )
                if not isinstance(decision, GuardDecision) or decision.status not in {
                    "pass",
                    "blocked",
                    "unavailable",
                }:
                    raise ValueError("configured guard returned an invalid result")
                version = str(slot.version)
            if decision.reads:
                found = request.backend.read(
                    snapshot, tuple(item.path for item in decision.reads)
                )
                for read in decision.reads:
                    blob = found[read.path]
                    current = sha256(blob).hexdigest() if blob is not None else None
                    if read.digest != current:
                        raise ValueError(
                            f"guard read does not match pinned evidence: {read.path}"
                        )
                    reads_by_path[read.path] = read
            if (
                identifier == request.contract.pickup_guard
                and decision.status == "pass"
            ):
                if decision.source is not None and decision.source != request.source:
                    raise ValueError("pickup authority identifies a different source")
                if decision.plan_generation is not None:
                    if (
                        type(decision.plan_generation) is not int
                        or decision.plan_generation <= 0
                    ):
                        raise ValueError(
                            "pickup authority has an invalid plan generation"
                        )
                    if plan_generation not in (None, decision.plan_generation):
                        raise ValueError(
                            "pickup authorities disagree on the plan generation"
                        )
                    plan_generation = decision.plan_generation
            if (
                identifier == request.contract.binding_guard
                and decision.status == "pass"
            ):
                candidate = decision.binding
                valid = (
                    isinstance(candidate, ImplementationBinding)
                    and candidate.snapshot == snapshot
                    and candidate.story == lifecycle.story_id
                    and candidate.identity == request.owner.binding
                    and candidate.generation == request.owner.generation
                    and candidate.branch == request.binding_ref
                    and candidate.branch.startswith("refs/heads/")
                    and candidate.source == request.source
                    and lifecycle.graduation.delivery_target is not None
                    and candidate.target == lifecycle.graduation.delivery_target
                    and candidate.branch != candidate.target.ref
                    and candidate.attempt == request.binding_attempt
                    and bool(candidate.attempt.strip())
                    and (attempt is None or candidate.attempt == attempt)
                )
                if valid:
                    binding = candidate
                    decision = replace(
                        decision,
                        reason=(
                            f"Binding {candidate.identity} generation {candidate.generation} "
                            f"at {candidate.branch} and {candidate.source.commit} "
                            f"for attempt {candidate.attempt} targets "
                            f"{candidate.target.repository}:{candidate.target.ref}."
                        ),
                    )
                else:
                    decision = GuardDecision(
                        "unavailable", "implementation-binding-unqualified"
                    )
            observations.append(
                GuardEvaluated(
                    operation=request.operation_id,
                    read_set_digest="0" * 64,
                    policy_digest=request.policy_digest,
                    workflow=lifecycle.workflow_state
                    if phase != "onEnter"
                    else observation,
                    slot=phase,
                    guard=identifier,
                    guard_version=version,
                    ok=decision.status == "pass",
                    code=decision.code
                    if decision.status == "pass"
                    else f"{decision.status}:{decision.code}",
                    reason=decision.reason,
                    mode=request.mode,
                )
            )
    reads = tuple(reads_by_path.values())
    read_digest = RelatedWriteSet(read_set=reads).read_set_digest
    guards = tuple(
        row.model_copy(update={"read_set_digest": read_digest}) for row in observations
    )
    return reads, read_digest, observation, guards, plan_generation, binding


def _result(
    detail: TransitionExplanation, request: TransitionRequest
) -> OperationResult:
    return OperationResult(
        CommandResult(
            operation_id=request.operation_id,
            local=detail.outcome,
            evidence=(detail.reason,) if detail.reason else (),
        ),
        detail.snapshot,
        detail.reason,
        detail.guards,
    )


def event_records(
    request: TransitionRequest,
    raw: bytes,
    state: StoryState,
    read_digest: str,
    events: list[tuple[str, str, BaseModel]],
) -> tuple[bytes, ...]:
    """Serialize a typed event batch against the exact existing log prefix."""
    digest = sha256(raw if raw.endswith(b"\n") else raw + b"\n")
    records = []
    for sequence, (kind, identity, record) in enumerate(events, state.next_sequence):
        event = (
            EventEnvelope(
                v=1,
                id=identity,
                ts=request.at,
                type=kind,
                story=request.story,
                actor=request.owner.actor,
                operation_id=request.operation_id,
                sequence=sequence,
                prior_log_digest=digest.hexdigest(),
                policy_digest=request.policy_digest,
                read_set_digest=read_digest,
                data=record.model_dump(mode="json", by_alias=True),
            )
            .model_dump_json(exclude_none=True)
            .encode()
        )
        digest.update(event + b"\n")
        records.append(event)

    return tuple(records)


def _make_operation(
    request,
    edge,
    state,
    lifecycle,
    raw,
    reads,
    read_digest,
    observation,
    guards,
    plan_generation,
    binding,
):
    failed = any(not guard.ok for guard in guards)
    if any(not guard.ok and guard.slot == "prepare" for guard in guards):
        return (
            None,
            LocalOutcome.UNAVAILABLE,
            "prepared transition evidence is unavailable",
        )
    if observation.terminal or edge.kind == "rework":
        return (
            None,
            LocalOutcome.UNAVAILABLE,
            "dedicated transition operation is unavailable",
        )
    if edge.operation not in (None, request.contract.start):
        return (
            None,
            LocalOutcome.UNAVAILABLE,
            "configured edge operation is unavailable",
        )

    append: list[tuple[str, str, BaseModel]] = []
    attempts = state.domains.get("attempts")
    current = (
        attempts.attempts.get(attempts.current_attempt)
        if isinstance(attempts, AttemptState) and attempts.current_attempt is not None
        else None
    )
    attempt = (
        current.started.attempt if current is not None and not current.closed else None
    )
    transition_allowed = request.mode == "advisory" or not failed
    if edge.operation == request.contract.start and transition_allowed:
        if attempt is not None:
            return (
                None,
                LocalOutcome.REFUSED,
                "existing attempt requires qualified recovery",
            )
        plan = lifecycle.accepted_documents.get("plan")
        if (
            plan_generation is None
            and plan is not None
            and plan.policy_digest == request.policy_digest
        ):
            plan_generation = plan.plan_generation
        if not (plan_generation and binding) and request.mode == "enforce":
            return (
                None,
                LocalOutcome.UNAVAILABLE,
                "current plan and implementation binding are required",
            )
        attempt = binding.attempt if binding else f"{request.operation_id}:attempt"
        if isinstance(attempts, AttemptState) and attempt in attempts.attempts:
            return (
                None,
                LocalOutcome.REFUSED,
                "prepared attempt identity already exists",
            )
        started_id = f"{request.operation_id}:started"
        append.append(
            (
                "core.attempt.started",
                started_id,
                AttemptStarted(
                    attempt=attempt,
                    generation=1,
                    plan_generation=plan_generation,
                    binding=binding.identity if binding else None,
                    source=request.source,
                    allowance_millis=request.allowance_millis,
                    provisional=failed or not (plan_generation and binding),
                ),
            )
        )
        append.append(
            (
                "core.attempt.clock.changed",
                f"{request.operation_id}:clock",
                ClockChanged(
                    attempt=attempt,
                    generation=1,
                    cause_event_id=started_id,
                    **{"from": None, "to": "active"},
                    observed_at=datetime.fromisoformat(request.at),
                    used_millis=0,
                ),
            )
        )

    change = StateChange(
        **{"from": lifecycle.workflow_state, "to": observation},
        edge=RecordedEdge(
            id=f"{edge.source}->{edge.target}",
            workflow_id=request.profile.id,
            revision=observation.revision,
            source=edge.source,
            target=edge.target,
            kind=edge.kind,
        ),
        mode=request.mode,
        reason=request.reason,
        attempt=attempt,
    )
    pending = []
    if transition_allowed:
        for index, guard in enumerate(guards):
            append.append(
                ("core.guard.evaluated", f"{request.operation_id}:guard:{index}", guard)
            )
        append.append(("core.state.changed", f"{request.operation_id}:state", change))
        if not failed:
            target = next(
                item for item in request.profile.states if item.id == edge.target
            )
            for identifier in target.action:
                registration = request.registry.resolve(identifier).registration
                if registration is None:
                    return (
                        None,
                        LocalOutcome.UNAVAILABLE,
                        f"action unavailable: {identifier}",
                    )
                if isinstance(registration, DirectiveRegistration):
                    continue
                if (
                    registration.scope.story_kinds
                    and lifecycle.kind not in registration.scope.story_kinds
                ):
                    continue
                if registration.execution != "queued":
                    continue
                identity = f"{request.operation_id}:action:{identifier}"
                pending.append(identity)
                append.append(
                    (
                        "core.action.pending",
                        identity,
                        ActionScope(
                            origin_operation=request.operation_id,
                            owner=identifier.split(".", 1)[0],
                            action_id=identifier,
                            target_version=registration.version,
                            owner_version=str(registration.version),
                            attempt=attempt,
                            workflow=observation,
                        ),
                    )
                )

    records = event_records(request, raw, state, read_digest, append)

    operation = Operation(
        operation_id=request.operation_id,
        owner=request.owner,
        policy_digest=request.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind=TRANSITION_INTENT,
            version=1,
            related_preconditions=reads,
            payload=change.model_dump_json(by_alias=True).encode(),
        ),
        change=RelatedWriteSet(
            read_set=reads,
            events=(EventAppend(story=request.story, records=tuple(records)),)
            if records
            else (),
        ),
        guards=guards,
        pending_actions=tuple(pending),
    )
    outcome = LocalOutcome.COMPLETED if transition_allowed else LocalOutcome.REFUSED
    return operation, outcome, None if transition_allowed else "guard-refused"


def _evaluate(request: TransitionRequest, snapshot: Snapshot) -> _Evaluation:
    try:
        path, raw, state, lifecycle = _read(request, snapshot)
        current = lifecycle.workflow_state
        for line in reversed(raw.splitlines()):
            event = validate_envelope(line)
            if (
                event.operation_id != request.operation_id
                or event.type != "core.state.changed"
            ):
                continue
            retained = StateChange.model_validate_json(dumps(event.data))
            expected_direction = (
                "rework" if retained.edge.kind == "rework" else "forward"
            )
            matches = (
                event.actor == request.owner.actor
                and event.policy_digest == request.policy_digest
                and retained.to_state.revision == request.profile.source.digest
                and retained.mode == request.mode
                and expected_direction == request.direction
                and retained.reason == request.reason
                and (
                    request.target is None
                    or retained.to_state.state_id == request.target
                )
            )
            return _Evaluation(
                TransitionExplanation(
                    snapshot,
                    retained.from_state.state_id,
                    retained.to_state.state_id,
                    outcome=LocalOutcome.COMPLETED
                    if matches
                    else LocalOutcome.INTEGRITY_ERROR,
                    reason="transition-already-recorded"
                    if matches
                    else "operation-identity-reused",
                )
            )
        validation = validate_profile(
            request.profile, request.registry, request.contract
        )
        if not validation.valid:
            return _Evaluation(
                TransitionExplanation(
                    snapshot,
                    current.state_id,
                    outcome=LocalOutcome.INTEGRITY_ERROR,
                    reason="invalid-configured-profile",
                )
            )
        if (
            current.workflow_id != request.profile.id
            or current.revision != request.profile.source.digest
        ):
            return _Evaluation(
                TransitionExplanation(
                    snapshot,
                    current.state_id,
                    outcome=LocalOutcome.UNAVAILABLE,
                    reason="workflow reconciliation is required",
                )
            )
        edge = _find_edge(request, current.state_id)
        if edge is None:
            return _Evaluation(
                TransitionExplanation(
                    snapshot,
                    current.state_id,
                    outcome=LocalOutcome.REFUSED,
                    reason="configured edge is unavailable",
                )
            )
        attempts = state.domains.get("attempts")
        attempt = (
            attempts.current_attempt if isinstance(attempts, AttemptState) else None
        )
        if attempt is not None and attempts.attempts[attempt].closed:
            attempt = None
        reads, digest, observation, guards, generation, binding = _facts(
            request, snapshot, lifecycle, edge, raw, path, attempt
        )
        operation, outcome, reason = _make_operation(
            request,
            edge,
            state,
            lifecycle,
            raw,
            reads,
            digest,
            observation,
            guards,
            generation,
            binding,
        )
        return _Evaluation(
            TransitionExplanation(
                snapshot,
                edge.source,
                edge.target,
                edge.operation,
                guards,
                outcome,
                reason,
            ),
            edge,
            operation,
        )
    except (UnavailablePort, UnavailableReducer) as error:
        return _Evaluation(
            TransitionExplanation(
                snapshot, outcome=LocalOutcome.UNAVAILABLE, reason=str(error)
            )
        )
    except ValueError as error:
        return _Evaluation(
            TransitionExplanation(
                snapshot, outcome=LocalOutcome.INTEGRITY_ERROR, reason=str(error)
            )
        )


def explain(request: TransitionRequest) -> TransitionExplanation:
    """Read the same pinned evaluation as mutation without performing any phase or write."""

    return _evaluate(request, _snapshot(request)).details


def preflight_transition(
    request: TransitionRequest, port: object
) -> CommandResult | None:
    """Fence an already-open attempt before the independent authored-sync operation."""
    snapshot = _snapshot(request)
    path, raw, state, lifecycle = _read(request, snapshot)
    attempts = state.domains.get("attempts")
    if not isinstance(attempts, AttemptState) or attempts.current_attempt is None:
        return None
    read = ReadExpectation(path=path, digest=sha256(raw).hexdigest())
    operation = Operation(
        operation_id=request.operation_id,
        owner=request.owner,
        policy_digest=request.policy_digest,
        category=OperationCategory.NORMAL,
        change=RelatedWriteSet(read_set=(read,)),
        intent=FinalizationIntent(
            kind=TRANSITION_INTENT,
            version=1,
            related_preconditions=(read,),
            payload=lifecycle.workflow_state.model_dump_json().encode(),
        ),
    )
    result = _preflight(
        OperationContext(
            operation, snapshot, (attempts.attempts[attempts.current_attempt],)
        ),
        ServicePorts(attempt_preflight=port),
    )
    if result.outcome in (PreflightOutcome.BLOCKED, PreflightOutcome.UNAVAILABLE):
        return CommandResult(
            operation_id=request.operation_id,
            local=LocalOutcome.REFUSED
            if result.outcome == PreflightOutcome.BLOCKED
            else LocalOutcome.UNAVAILABLE,
            evidence=(result.reason or "attempt-preflight-refused",),
        )
    return None


def transition(request: TransitionRequest) -> OperationResult:
    """Preflight, persist authored input independently, then evaluate and CAS."""

    preparation = []

    def include_preparation(result: OperationResult) -> OperationResult:
        if not preparation:
            return result
        command = result.command
        return replace(
            result,
            command=command.model_copy(
                update={"evidence": (*preparation, *command.evidence)}
            ),
        )

    for phase in (request.before_sync, request.sync):
        if phase is None:
            continue
        receipt = phase()
        if receipt is None:
            continue
        if (
            receipt.local != LocalOutcome.COMPLETED
            or receipt.publication == PublicationOutcome.PENDING
        ):
            return OperationResult(
                receipt, _snapshot(request), "transition preparation did not finish"
            )
        preparation.append(
            f"Completed transition prerequisite operation {receipt.operation_id}."
        )
        preparation.extend(receipt.evidence)

    apply = request.transact or request.backend.transact
    pinned_edge = None
    for _ in range(3):
        evaluation = _evaluate(request, _snapshot(request))
        if evaluation.operation is None:
            return include_preparation(_result(evaluation.details, request))
        if pinned_edge is None:
            pinned_edge = evaluation.edge
        elif evaluation.edge != pinned_edge:
            return include_preparation(
                _result(
                    replace(
                        evaluation.details,
                        outcome=LocalOutcome.CONFLICT,
                        reason="selected edge changed",
                    ),
                    request,
                )
            )
        outcome = apply(evaluation.operation, evaluation.details.snapshot)
        if outcome.command.local != LocalOutcome.CONFLICT:
            return include_preparation(outcome)
    return include_preparation(outcome)
