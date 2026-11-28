"""Atomic terminal outcomes for explicit non-delivery routes."""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel

from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.machine.obligations import validate_profile
from aitm_core.machine.transitions import (
    TransitionRequest,
    _read,
    _snapshot,
    event_records,
)
from aitm_core.models.attempts import (
    AttemptClosed,
    AttemptRecord,
    AttemptState,
    ClockChanged,
)
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.lifecycle import (
    LifecycleState,
    StateChange,
    WorkflowEdge,
    WorkflowObservation,
)
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.services import UnavailablePort
from aitm_core.splitting import _pending_authority
from aitm_core.store.backend import OperationResult

type NonDelivery = Literal["abandoned", "superseded", "duplicate", "unverified"]


@dataclass(frozen=True, slots=True)
class DispositionRequest:
    transition: TransitionRequest
    disposition: NonDelivery
    reason: str
    replacement: int | None = None


class DispositionRefusal(ValueError):
    """A non-delivery request lacks authority or conflicts with current facts."""


def _replacement(request: DispositionRequest, snapshot) -> tuple[ReadExpectation, ...]:
    transition = request.transition
    number = request.replacement
    if request.disposition in {"superseded", "duplicate"}:
        if type(number) is not int or number <= 0 or number == transition.story:
            raise DispositionRefusal(
                "A distinct permanent replacement story is required."
            )
        path = story_event_path(number)
        raw = transition.backend.read(snapshot, (path,))[path]
        if raw is None:
            raise DispositionRefusal("The replacement story is unavailable.")
        state = fold(raw.splitlines(keepends=True), core_reducers())
        if state.story_id != number or not isinstance(
            state.domains.get("lifecycle"), LifecycleState
        ):
            raise ValueError("The replacement history identifies a different story.")
        return (ReadExpectation(path=path, digest=sha256(raw).hexdigest()),)
    if number is not None:
        raise DispositionRefusal("This disposition does not take a replacement story.")
    return ()


def _closure(request: DispositionRequest, active: AttemptRecord | None):
    if active is None or active.closed:
        return []
    if active.clock_mode is None:
        raise ValueError("The current attempt lacks its atomic clock.")
    clock = active.clock_mode
    context = request.transition
    identity = f"{context.operation_id}:close-attempt"
    result: list[tuple[str, str, BaseModel]] = [
        (
            "core.attempt.closed",
            identity,
            AttemptClosed(
                attempt=active.started.attempt,
                generation=active.generation,
                from_clock=clock,
                disposition=request.disposition,
                reason=request.reason,
            ),
        )
    ]
    if clock != "terminal-closed":
        result.append(
            (
                "core.attempt.clock.changed",
                f"{context.operation_id}:clock",
                ClockChanged(
                    attempt=active.started.attempt,
                    generation=active.generation,
                    cause_event_id=identity,
                    **{"from": clock, "to": "terminal-closed"},
                    observed_at=datetime.fromisoformat(context.at),
                    used_millis=active.used_millis,
                ),
            )
        )
    return result


def dispose(request: DispositionRequest) -> OperationResult:
    """Record one explicit outcome, with no delivery authority or dependent status side effect."""
    context = request.transition
    snapshot = _snapshot(context)
    try:
        path, raw, state, story = _read(context, snapshot)
        profile = context.profile
        if (
            not validate_profile(profile, context.registry, context.contract).valid
            or story.workflow_state.workflow_id != profile.id
            or story.workflow_state.revision != profile.source.digest
        ):
            raise ValueError("The story requires a valid current workflow profile.")
        if request.disposition not in {
            "abandoned",
            "superseded",
            "duplicate",
            "unverified",
        }:
            raise DispositionRefusal(
                "This command admits only explicit non-delivery outcomes."
            )
        if not request.reason.strip():
            raise DispositionRefusal(
                "Record a reason for the non-delivery disposition."
            )
        current = story.workflow_state
        if current.terminal:
            raise DispositionRefusal(
                "The current story already has a terminal disposition."
            )
        if request.disposition == "unverified" and (
            context.mode != "advisory" or current.state_id != context.contract.review
        ):
            raise DispositionRefusal(
                "Unverified closure requires the explicit advisory route from Review."
            )
        target = profile.lifecycle.non_delivery
        if context.target not in (None, target):
            raise DispositionRefusal(
                "The target differs from the configured terminal destination."
            )
        attempts, evidence = (
            state.domains.get("attempts"),
            state.domains.get("evidence"),
        )
        active = (
            attempts.attempts.get(attempts.current_attempt)
            if isinstance(attempts, AttemptState)
            and attempts.current_attempt is not None
            else None
        )
        if isinstance(evidence, EvidenceState) and any(
            active is None or row.envelope.data.get("attempt") == active.started.attempt
            for row in evidence.facts.get("core.delivery.verified", ())
        ):
            raise DispositionRefusal(
                "Verified delivery requires the dedicated closeout route."
            )
        pending = active is not None and any(
            operations[-1].phase != "finished"
            for operations in active.executions.values()
        )
        if pending or _pending_authority(state):
            raise DispositionRefusal(
                "Unresolved execution or identity authority fences non-delivery."
            )
        reads = (
            ReadExpectation(path=path, digest=sha256(raw).hexdigest()),
            *_replacement(request, snapshot),
        )
        target_state = next(item for item in profile.states if item.id == target)
        destination = WorkflowObservation(
            workflow_id=profile.id,
            revision=profile.source.digest,
            state_id=target,
            label=target_state.label,
            terminal=True,
        )
        move = StateChange(
            **{"from": current, "to": destination},
            edge=WorkflowEdge(
                id=f"state.{request.disposition}",
                workflow_id=profile.id,
                revision=profile.source.digest,
                source=current.state_id,
                target=target,
                kind="terminal",
            ),
            mode=context.mode,
            reason=request.reason,
            disposition=request.disposition,
            attempt=active.started.attempt
            if active is not None and not active.closed
            else None,
            replacement_story=request.replacement,
        )
        facts = _closure(request, active)
        facts.append(("core.state.changed", f"{context.operation_id}:terminal", move))
        digest = RelatedWriteSet(read_set=reads).read_set_digest
        operation = Operation(
            operation_id=context.operation_id,
            owner=context.owner,
            policy_digest=context.policy_digest,
            category=OperationCategory.NORMAL,
            intent=FinalizationIntent(
                kind="state.non-delivery",
                version=1,
                related_preconditions=reads,
                payload=move.model_dump_json(by_alias=True).encode(),
            ),
            change=RelatedWriteSet(
                read_set=reads,
                events=(
                    EventAppend(
                        story=context.story,
                        records=event_records(context, raw, state, digest, facts),
                    ),
                ),
            ),
        )
        return (context.transact or context.backend.transact)(operation, snapshot)
    except DispositionRefusal as error:
        outcome, message = LocalOutcome.REFUSED, str(error)
    except (UnavailablePort, UnavailableReducer) as error:
        outcome, message = LocalOutcome.UNAVAILABLE, str(error)
    except ValueError as error:
        outcome, message = LocalOutcome.INTEGRITY_ERROR, str(error)
    return OperationResult(
        CommandResult(
            operation_id=context.operation_id, local=outcome, evidence=(message,)
        ),
        snapshot,
        message,
    )
