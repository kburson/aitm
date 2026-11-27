"""Fold C55 observations and check durable clock pairings without dispatch."""

from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime
from json import dumps

from pydantic import ValidationError

from aitm_core.events import StoryState
from aitm_core.models.attempts import (
    AttemptBoundary,
    AttemptClosed,
    AttemptRecord,
    AttemptReopened,
    AttemptStarted,
    AttemptState,
    BindingPurpose,
    ClockChanged,
    ClockMode,
    ExecutionRecorded,
    RecoveryBinding,
)
from aitm_core.models.events import EventEnvelope

_SCHEMAS: dict[str, type[AttemptBoundary]] = {
    "core.attempt.started": AttemptStarted,
    "core.attempt.closed": AttemptClosed,
    "core.attempt.reopened": AttemptReopened,
    "core.attempt.clock.changed": ClockChanged,
    "core.execution.recorded": ExecutionRecorded,
}
_EXECUTION_NEXT = {
    None: {"prepared"},
    "prepared": {"admitted"},
    "admitted": {"started", "cancel-requested", "finished", "uncertain"},
    "started": {"cancel-requested", "finished", "uncertain"},
    "cancel-requested": {"finished", "uncertain"},
    "uncertain": {"finished"},
    "finished": set(),
}
_BOUNDARY_TARGETS: dict[str, tuple[ClockMode | None, ClockMode]] = {
    "core.attempt.started": (None, "active"),
    "core.expansion.reserved": ("active", "expansion-paused"),
    "core.expansion.resolved": ("expansion-paused", "active"),
    "core.review.activated": ("active", "review-stopped"),
}
Pair = tuple[ClockMode | None, ClockMode]


class AttemptIntegrityError(ValueError):
    """An attempt fact contradicts its source, generation or causal boundary."""


def attempt_schemas() -> dict[str, type[AttemptBoundary]]:
    """The C55-owned types, for composition by C56."""
    return _SCHEMAS.copy()


def _decode[T: AttemptBoundary](schema: type[T], event: EventEnvelope) -> T:
    try:
        return schema.model_validate_json(dumps(event.data, allow_nan=False))
    except (ValidationError, ValueError) as error:
        raise AttemptIntegrityError(
            f"invalid attempt payload for {event.type}"
        ) from error


def _is_evidence_binding(event: EventEnvelope) -> bool:
    return (
        event.type == "core.session.started"
        and event.data.get("purpose") == BindingPurpose.EVIDENCE
    )


def _pair(event: EventEnvelope) -> Pair | None:
    if event.type == "core.attempt.closed":
        fact = _decode(AttemptClosed, event)
        return (
            None
            if fact.from_clock == "terminal-closed"
            else (fact.from_clock, "terminal-closed")
        )
    if event.type == "core.expansion.reservation-resolved":
        return (
            ("expansion-paused", "active")
            if event.data.get("disposition") == "no-child"
            else None
        )
    if event.type == "core.review.invalidated":
        return (
            ("review-stopped", "active")
            if event.data.get("resumes_execution") is True
            else None
        )
    if _is_evidence_binding(event):
        fact = _decode(RecoveryBinding, event)
        return ("terminal-closed", "active") if fact.needs_verification else None
    return _BOUNDARY_TARGETS.get(event.type)


def validate_boundary_batch(batch: Iterable[EventEnvelope]) -> None:
    """Match each required clock change with its earlier causal event in the operation."""
    pending: dict[str, tuple[EventEnvelope, Pair]] = {}
    seen: set[str] = set()
    for event in batch:
        if event.id in seen:
            raise AttemptIntegrityError(f"duplicate boundary batch event: {event.id}")
        seen.add(event.id)
        if event.type != "core.attempt.clock.changed":
            pair = _pair(event)
            if pair is not None:
                pending[event.id] = event, pair
            continue

        clock = _decode(ClockChanged, event)
        obligation = pending.pop(clock.cause_event_id, None)
        if obligation is None:
            raise AttemptIntegrityError("clock record lacks its earlier causal fact")
        cause, modes = obligation
        generation = cause.data.get("generation")
        if (
            cause.story != event.story
            or cause.operation_id != event.operation_id
            or cause.data.get("attempt") != clock.attempt
            or type(generation) is not int
            or generation != clock.generation
            or modes != (clock.from_mode, clock.to_mode)
            or clock.observed_at != datetime.fromisoformat(cause.ts)
        ):
            raise AttemptIntegrityError("clock record conflicts with its causal fact")
    if pending:
        raise AttemptIntegrityError(f"missing clock records for: {', '.join(pending)}")


def _reopen(record: AttemptRecord, fact: AttemptReopened) -> AttemptRecord:
    last = record.closures[-1] if record.closures else None
    authority = fact.authority
    if (
        not record.closed
        or last is None
        or last.disposition != "unverified"
        or last.reason != fact.closure_reason
        or record.recovery is not None
        or fact.source != record.started.source
        or authority.source != fact.source
        or authority.attempt != fact.attempt
        or authority.ended_generation != record.generation
    ):
        raise AttemptIntegrityError(
            "recovery does not match the ended unverified attempt and source"
        )
    if fact.allowance_millis != record.allowance_millis:
        raise AttemptIntegrityError("recovery cannot change the retained allowance")
    return record.model_copy(update={"recovery": authority, "recovery_bound": False})


def _bind_recovery(record: AttemptRecord, fact: RecoveryBinding) -> AttemptRecord:
    authority = record.recovery
    if (
        authority is None
        or record.recovery_bound
        or not record.closed
        or record.clock_mode != "terminal-closed"
        or fact.generation <= record.generation
        or fact.authority_id != authority.authority_id
        or fact.source != authority.source
        or fact.binding == record.binding
    ):
        raise AttemptIntegrityError(
            "invalid evidence-only recovery binding or generation"
        )
    if fact.needs_verification and "managed-verification" not in authority.allowed:
        raise AttemptIntegrityError("recovery scope excludes managed verification")
    return record.model_copy(
        update={
            "generation": fact.generation,
            "binding": fact.binding,
            "recovery_bound": True,
            "closed": False,
        }
    )


def _record_execution(record: AttemptRecord, fact: ExecutionRecorded) -> AttemptRecord:
    history = record.executions.get(fact.execution_id, ())
    previous = history[-1] if history else None
    if (
        fact.phase not in _EXECUTION_NEXT[previous.phase if previous else None]
        or previous is not None
        and (
            previous.generation != fact.generation
            or previous.request_id != fact.request_id
        )
    ):
        raise AttemptIntegrityError("invalid next execution phase or request identity")
    if fact.phase in {"prepared", "admitted", "started"}:
        if fact.generation != record.generation:
            raise AttemptIntegrityError("attempt generation is stale or unrecognized")
        if record.closed or record.clock_mode != "active" or not record.binding:
            raise AttemptIntegrityError(
                "execution phase lacks the current active binding"
            )
        authority = record.recovery if record.recovery_bound else None
        if fact.recovery_authority_id != (
            authority.authority_id if authority else None
        ):
            raise AttemptIntegrityError(
                "execution phase disagrees with binding authority"
            )
    if fact.source != record.started.source:
        raise AttemptIntegrityError(
            "execution phase disagrees with the retained source"
        )
    if previous and any(
        getattr(fact, field) != getattr(previous, field)
        for field in (
            "action_key",
            "executor",
            "authority_store",
            "authority_ref",
            "expected_prior_version",
            "recovery_authority_id",
        )
    ):
        raise AttemptIntegrityError("execution phase disagrees with retained authority")
    if fact.phase in {"prepared", "admitted"}:
        if fact.admission_commit is not None:
            raise AttemptIntegrityError(
                "preparation or admission cannot name its admission commit"
            )
    elif fact.admission_commit is None or (
        previous and previous.admission_commit not in (None, fact.admission_commit)
    ):
        raise AttemptIntegrityError(
            "execution phase disagrees with its admission commit"
        )
    if fact.phase == "admitted" and not fact.proof:
        raise AttemptIntegrityError("admission requires retained proof")
    if fact.phase in {"finished", "uncertain"} and (not fact.proof or not fact.outcome):
        raise AttemptIntegrityError(
            "execution resulting phase requires outcome and proof"
        )
    return record.model_copy(
        update={
            "executions": {**record.executions, fact.execution_id: (*history, fact)}
        }
    )


def _update(record: AttemptRecord, fact: AttemptBoundary) -> AttemptRecord:
    if isinstance(fact, RecoveryBinding):
        return _bind_recovery(record, fact)
    if isinstance(fact, ExecutionRecorded):
        return _record_execution(record, fact)
    if fact.generation != record.generation:
        raise AttemptIntegrityError("attempt generation is stale or unrecognized")
    match fact:
        case AttemptClosed():
            if record.closed or fact.from_clock != record.clock_mode:
                raise AttemptIntegrityError("closure disagrees with the current clock")
            return record.model_copy(
                update={
                    "closed": True,
                    "closures": (*record.closures, fact),
                    "recovery": None,
                }
            )
        case AttemptReopened():
            return _reopen(record, fact)
        case ClockChanged():
            if fact.from_mode != record.clock_mode or fact.from_mode == fact.to_mode:
                raise AttemptIntegrityError(
                    "clock prior mode disagrees with retained mode"
                )
            if fact.used_millis < record.used_millis:
                raise AttemptIntegrityError("clock change cannot lower retained usage")
            if record.clocks and fact.observed_at < record.clocks[-1].observed_at:
                raise AttemptIntegrityError(
                    "clock boundary precedes the retained boundary"
                )
            return record.model_copy(
                update={
                    "clocks": (*record.clocks, fact),
                    "used_millis": fact.used_millis,
                }
            )
        case _:
            raise AttemptIntegrityError("unsupported attempt fact")


def fold_attempt(state: StoryState, event: EventEnvelope) -> StoryState:
    """Fold one attempt fact from a causally validated batch."""
    schema = (
        RecoveryBinding if _is_evidence_binding(event) else _SCHEMAS.get(event.type)
    )
    if schema is None:
        raise AttemptIntegrityError(
            f"event is not owned or observed by C55: {event.type}"
        )
    if state.story_id not in (None, event.story):
        raise AttemptIntegrityError("attempt fact belongs to another story")
    fact = _decode(schema, event)
    current = state.domains.get("attempts")
    if current is None:
        current = AttemptState(story_id=event.story)
    if not isinstance(current, AttemptState):
        raise AttemptIntegrityError("invalid attempt domain")
    if current.story_id != event.story:
        raise AttemptIntegrityError("attempt fact belongs to another story")
    previous = (
        current.attempts.get(current.current_attempt)
        if current.current_attempt
        else None
    )
    if isinstance(fact, AttemptStarted):
        if (
            fact.attempt in current.attempts
            or previous is not None
            and not previous.closed
        ):
            raise AttemptIntegrityError("attempt start conflicts with retained attempt")
        if not fact.provisional and (
            fact.plan_generation is None or fact.source is None or fact.binding is None
        ):
            raise AttemptIntegrityError("attempt start lacks plan and binding evidence")
        updated = AttemptRecord(
            started=fact,
            generation=fact.generation,
            binding=fact.binding,
            allowance_millis=fact.allowance_millis,
        )
    else:
        if previous is None or current.current_attempt != fact.attempt:
            raise AttemptIntegrityError(
                "attempt fact lacks its current or recoverable attempt"
            )
        updated = _update(previous, fact)
    projection = AttemptState(
        story_id=event.story,
        current_attempt=fact.attempt,
        attempts={**current.attempts, fact.attempt: updated},
    )
    return replace(state, domains={**state.domains, "attempts": projection})
