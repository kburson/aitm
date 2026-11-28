"""Evaluate attempted work against current trip evidence and construct its stop."""

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps
from typing import Literal
from uuid import uuid4

from aitm_core.activity import ActivityEvidence
from aitm_core.events import StoryState, validate_envelope
from aitm_core.machine.profile import WorkflowProfile
from aitm_core.models.attempts import (
    AttemptClosed,
    AttemptRecord,
    AttemptState,
    ClockChanged,
)
from aitm_core.models.evidence import PivotRecorded, TripDecided, TripRecorded
from aitm_core.models.lifecycle import (
    LinkChange,
    StateChange,
    WorkflowEdge,
    WorkflowObservation,
)
from aitm_core.models.operations import (
    AuthorityOrigin,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
    story_scope,
)
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.relationships import EventContext, StoryGraph
from aitm_core.rules.expansion import ExpansionAuthority
from aitm_core.rules.timing import engagement
from aitm_core.store.backend import OperationContext

type Cause = Literal["second-expansion", "nested-expansion", "time-limit"]
type Mode = Literal["advisory", "enforce"]
STOP_CATEGORIES = {
    (kind, 1): OperationCategory.STOP_RECONCILIATION
    for kind in ("core.attempt.trip", "core.trip.decide", "core.attempt.pivot")
}


_STOP_MARKERS = {
    "core.attempt.trip": ("core.trip.recorded", TripRecorded),
    "core.trip.decide": ("core.trip.decided", TripDecided),
    "core.attempt.pivot": ("core.pivot.recorded", PivotRecorded),
}
_STOP_ROWS = {
    "core.attempt.closed",
    "core.attempt.clock.changed",
    "core.execution.recorded",
    "core.state.changed",
    "core.link.changed",
}


def qualified_stop(operation: Operation) -> bool:
    """Keep the stop/reconciliation exception limited to its typed event packet."""
    if operation.change.writes or operation.pending_actions or operation.guards:
        return False
    name, schema = _STOP_MARKERS[operation.intent.kind]
    try:
        cause = schema.model_validate_json(operation.intent.payload)
        events = [
            validate_envelope(raw)
            for append in operation.change.events
            for raw in append.records
        ]
        markers = [event for event in events if event.type == name]
        return (
            len(markers) == 1
            and schema.model_validate_json(dumps(markers[0].data)) == cause
            and all(event.type in _STOP_ROWS or event.type == name for event in events)
            and (name != "core.pivot.recorded" or operation.owner.actor.kind == "human")
        )
    except ValueError:
        return False


@dataclass(frozen=True, slots=True)
class TripResult:
    preflight: PreflightResult
    origin: int | None = None
    cause: Cause | None = None
    child: int | None = None
    measured_millis: int | None = None
    proof: tuple[str, ...] = ()


def current_attempt(state: StoryState) -> AttemptRecord | None:
    domain = state.domains.get("attempts")
    if not isinstance(domain, AttemptState) or domain.current_attempt is None:
        return None
    return domain.attempts[domain.current_attempt]


def facts(state: StoryState, name: str) -> tuple:
    evidence = state.domains.get("evidence")
    if not isinstance(evidence, EvidenceState):
        return ()
    return tuple(item.payload for item in evidence.facts.get(name, ()))


def expansion_child(state: StoryState, attempt: str) -> int | None:
    resolved = {item.child for item in facts(state, "core.expansion.resolved")}
    continued = {
        item.attempt
        for item in facts(state, "core.trip.decided")
        if item.expansion_disposition == "continue"
    }
    links = state.domains["lifecycle"].relationships.blocked_by
    children = [
        item.child
        for item in facts(state, "core.expansion.recorded")
        if item.child not in resolved
        and (
            item.attempt == attempt or item.attempt in continued and item.child in links
        )
    ]
    return children[-1] if children else None


def _scope(context: OperationContext, graph: StoryGraph) -> tuple[int, ...]:
    operation = context.operation
    targets = {
        number
        for item in (*operation.change.events, *operation.change.writes)
        if (number := story_scope(item.path)) is not None
    }
    if not targets:
        reads = {story_scope(item.path) for item in operation.change.read_set}
        if len(reads - {None}) == 1:
            targets = reads - {None}
    if not targets and operation.owner.binding is not None:
        targets = {
            story
            for story, state in graph.states.items()
            if (attempt := current_attempt(state)) is not None
            and attempt.binding == operation.owner.binding
        }
    return tuple(sorted(targets & graph.states.keys()))


def _preflight(outcome: PreflightOutcome, reason: str | None = None) -> PreflightResult:
    return PreflightResult(
        outcome=outcome, origin=AuthorityOrigin.REGISTERED, reason=reason
    )


def preflight_attempt(
    context: OperationContext,
    graph: StoryGraph,
    observations: tuple[ActivityEvidence, ...] | None,
    at: datetime,
    mode: Mode,
) -> TripResult:
    """Classify only confirmed findings, preserving unknown activity separately."""
    if context.operation.category == OperationCategory.STOP_RECONCILIATION:
        return TripResult(_preflight(PreflightOutcome.PASSED))
    proposed = None
    if context.operation.intent.kind == "expand":
        proposed = ExpansionAuthority.model_validate_json(
            context.operation.intent.payload
        )
    scope = _scope(context, graph) if proposed is None else (proposed.origin,)
    for story in scope:
        state = graph.states[story]
        attempt = current_attempt(state)
        if attempt is None:
            continue
        key = attempt.started.attempt
        if proposed is not None:
            for origin, origin_state in sorted(graph.states.items()):
                origin_attempt = current_attempt(origin_state)
                if (
                    origin_attempt is not None
                    and not origin_attempt.closed
                    and expansion_child(origin_state, origin_attempt.started.attempt)
                    == story
                ):
                    return TripResult(
                        _preflight(
                            PreflightOutcome.BLOCKED
                            if mode == "enforce"
                            else PreflightOutcome.PASSED,
                            "nested-expansion",
                        ),
                        origin,
                        "nested-expansion",
                        story,
                        proof=(f"planning:{context.snapshot.revision}",),
                    )
            reservations = tuple(
                item
                for item in facts(state, "core.expansion.reserved")
                if item.attempt == key
            )
            if any(
                item.reservation != proposed.reservation for item in reservations
            ) or (not reservations and expansion_child(state, key) is not None):
                return TripResult(
                    _preflight(
                        PreflightOutcome.BLOCKED
                        if mode == "enforce"
                        else PreflightOutcome.PASSED,
                        "second-expansion",
                    ),
                    story,
                    "second-expansion",
                    expansion_child(state, key),
                    proof=(f"planning:{context.snapshot.revision}",),
                )
        if attempt.closed:
            if (
                context.operation.owner.binding == attempt.binding
                and attempt.binding is not None
            ):
                return TripResult(
                    _preflight(
                        PreflightOutcome.BLOCKED, "The attempt generation is fenced."
                    )
                )
            continue
        if observations is not None:
            measured = engagement(attempt, observations, as_of=at)
            if measured.confirmed_overrun:
                proof = tuple(
                    item.observation.source_id
                    for item in observations
                    if item.qualified
                    and item.observation.attempt == key
                    and item.observation.generation == attempt.generation
                )
                return TripResult(
                    _preflight(
                        PreflightOutcome.BLOCKED
                        if mode == "enforce"
                        else PreflightOutcome.PASSED,
                        "time-limit",
                    ),
                    story,
                    "time-limit",
                    expansion_child(state, key),
                    measured.measured_millis,
                    proof,
                )
        if (
            attempt.clock_mode == "expansion-paused"
            and context.operation.intent.kind
            not in {
                "expand",
                "expand.resolve",
                "core.graduated",
            }
            and mode == "enforce"
        ):
            return TripResult(
                _preflight(PreflightOutcome.BLOCKED, "Expansion resolution is pending.")
            )
    open_scope = [
        number
        for number in scope
        if (attempt := current_attempt(graph.states[number])) is not None
        and not attempt.closed
    ]
    if (
        observations is None
        and open_scope
        and not any(
            facts(graph.states[number], "core.expansion.reserved")
            for number in open_scope
        )
    ):
        return TripResult(
            _preflight(PreflightOutcome.UNAVAILABLE, "attempt-preflight-unavailable")
        )
    return TripResult(_preflight(PreflightOutcome.PASSED))


def _append(
    events: EventContext,
    state: StoryState,
    raw: bytes,
    rows: list[tuple[str, object, str]],
) -> EventAppend:
    assert state.story_id is not None
    digest = sha256(raw if raw.endswith(b"\n") else raw + b"\n")
    records = []
    for event, payload, label in rows:
        wire = events.encode(state.story_id, event, state, payload, label)
        records.append(wire)
        digest.update(wire + b"\n")
        state = replace(
            state,
            next_sequence=state.next_sequence + 1,
            prior_log_digest=digest.hexdigest(),
        )
    return EventAppend(story=state.story_id, records=tuple(records))


def disposition_change(
    profile, lifecycle, destination, reason, attempt, *, terminal=False
):
    source = lifecycle.workflow_state
    if (
        source.terminal
        or source.workflow_id != profile.id
        or source.revision != profile.source.digest
    ):
        raise ValueError("Recovery requires the retained configured workflow revision.")
    target = next(state for state in profile.states if state.id == destination)
    return StateChange(
        **{
            "from": source,
            "to": WorkflowObservation(
                workflow_id=profile.id,
                revision=profile.source.digest,
                state_id=target.id,
                label=target.label,
                terminal=terminal,
            ),
        },
        edge=WorkflowEdge(
            id="core.attempt.recovery",
            workflow_id=profile.id,
            revision=profile.source.digest,
            source=source.state_id,
            target=target.id,
            kind="terminal" if terminal else "rework",
        ),
        mode="enforce",
        reason=reason,
        attempt=attempt,
        disposition="abandoned" if terminal else None,
    )


def admission_commit(repository, snapshot, graph, story, execution):
    """Find the commit that first retained the exact admitted execution envelope."""
    path = story_event_path(story)
    retained = [
        event
        for line in graph.logs[path].splitlines(keepends=True)
        if (event := validate_envelope(line)).type == "core.execution.recorded"
        and event.data.get("phase") == "admitted"
        and event.data.get("execution_id") == execution.execution_id
        and event.data.get("request_id") == execution.request_id
        and event.data.get("attempt") == execution.attempt
        and event.data.get("generation") == execution.generation
    ]
    if len(retained) != 1:
        raise ValueError(
            "The admitted execution does not have a unique retained envelope."
        )
    event = retained[0]
    commits = (
        repository._git(
            "log",
            "--first-parent",
            "--format=%H",
            "-S",
            event.id,
            snapshot.revision,
            "--",
            path,
        )
        .decode()
        .splitlines()
    )
    for commit in reversed(commits):
        current = repository.read_tree(commit)
        raw = repository.read_blobs(current.tree, (path,))[path]
        if raw and event.raw_record.removesuffix(b"\n") in raw.splitlines():
            return commit
    raise ValueError("The admitted execution's authoritative commit is unavailable.")


def _stop_rows(events, number, active, reason, kind, resolve_admission=None):
    clock = active.clock_mode
    if clock is None:
        raise ValueError("The current attempt lacks its retained clock.")
    key = active.started.attempt
    closure = AttemptClosed(
        attempt=key,
        generation=active.generation,
        from_clock=clock,
        disposition=kind,
        reason=reason,
    )
    rows = [("core.attempt.closed", closure, "stop")]
    if clock != "terminal-closed":
        rows.append(
            (
                "core.attempt.clock.changed",
                ClockChanged(
                    attempt=key,
                    generation=active.generation,
                    cause_event_id=f"{events.operation}:stop:{number}",
                    **{"from": clock, "to": "terminal-closed"},
                    observed_at=datetime.fromisoformat(events.stamp),
                    used_millis=active.used_millis,
                ),
                "clock-stopped",
            )
        )
    for execution, history in sorted(active.executions.items()):
        last = history[-1]
        if last.phase in {"admitted", "started"}:
            commit = last.admission_commit
            if commit is None and resolve_admission is not None:
                commit = resolve_admission(number, last)
            if commit is None:
                raise ValueError(
                    "Cancellation requires the witnessed admission commit."
                )
            rows.append(
                (
                    "core.execution.recorded",
                    last.model_copy(
                        update={
                            "phase": "cancel-requested",
                            "admission_commit": commit,
                            "outcome": None,
                            "proof": None,
                        }
                    ),
                    f"cancel-{execution}",
                )
            )
    return rows


def _operation(events, graph, kind, payload, additions, *, extra_reads=None):
    bodies = {**graph.logs, **(extra_reads or {})}
    reads = tuple(
        ReadExpectation(
            path=path, digest=sha256(raw).hexdigest() if raw is not None else None
        )
        for path, raw in sorted(bodies.items())
    )
    appends = tuple(
        _append(events, graph.states[story], graph.logs[story_event_path(story)], rows)
        for story, rows in sorted(additions.items())
    )
    return Operation(
        operation_id=events.operation,
        owner=events.owner,
        policy_digest=events.policy_digest,
        category=OperationCategory.STOP_RECONCILIATION,
        intent=FinalizationIntent(
            kind=kind, version=1, payload=payload, related_preconditions=reads
        ),
        change=RelatedWriteSet(read_set=reads, events=appends),
    )


def record_trip(
    context,
    result: TripResult,
    graph,
    profile: WorkflowProfile,
    mode: Mode,
    at: datetime,
    *,
    repository=None,
):
    """Create one scoped operation that fences the affected attempts and no authored data."""
    if result.origin is None or result.cause is None:
        raise ValueError("A trip requires a confirmed origin and cause.")
    origin = result.origin
    active = current_attempt(graph.states[origin])
    if active is None or active.closed:
        return None
    if any(
        item.attempt == active.started.attempt and item.cause == result.cause
        for item in facts(graph.states[origin], "core.trip.recorded")
    ):
        return None
    child = (
        current_attempt(graph.states[result.child])
        if result.child is not None
        else None
    )
    events = EventContext(
        uuid4().hex,
        context.operation.owner,
        at.isoformat(),
        context.operation.policy_digest,
    )
    fact = TripRecorded(
        attempt=active.started.attempt,
        generation=active.generation,
        cause=result.cause,
        child_attempt=child.started.attempt if child else None,
        observed_hours=result.measured_millis / 3_600_000
        if result.measured_millis is not None
        else None,
        coverage="measured"
        if result.measured_millis is not None
        else "qualified-expansion",
        detected_at=events.stamp,
        proof_refs=result.proof,
    )
    additions = {origin: [("core.trip.recorded", fact, "trip")]}

    def resolve_admission(number, execution):
        if repository is None:
            return None
        return admission_commit(repository, context.snapshot, graph, number, execution)

    if mode == "enforce":
        for number in (origin, result.child):
            if number is None:
                continue
            current = current_attempt(graph.states[number])
            if current is None or current.closed:
                continue
            rows = additions.setdefault(number, [])
            rows.extend(
                _stop_rows(
                    events, number, current, result.cause, "trip", resolve_admission
                )
            )
            life = graph.stories[number]
            if life.workflow_state.state_id != profile.recovery.trip:
                rows.append(
                    (
                        "core.state.changed",
                        disposition_change(
                            profile,
                            life,
                            profile.recovery.trip,
                            result.cause,
                            current.started.attempt,
                        ),
                        "trip-destination",
                    )
                )
    return _operation(
        events, graph, "core.attempt.trip", fact.model_dump_json().encode(), additions
    )


def expansion_disposition(
    graph, profile, origin, child, mode, action, rationale, additions
):
    """Resolve only the expansion dependency for an explicit terminal disposition."""
    if child is None:
        if action is not None:
            raise ValueError("There is no expansion child to disposition.")
        return
    if action not in {"continue", "fold", "abandon"}:
        raise ValueError("Record an explicit disposition for the expansion child.")
    if action == "continue":
        return
    origin_life = graph.stories[origin]
    child_life = graph.stories[child]
    left, right = origin_life.relationships, child_life.relationships
    if child not in left.blocked_by or origin not in right.blocking:
        raise ValueError("The expansion dependency is not reciprocal.")
    additions.setdefault(origin, []).append(
        (
            "core.link.changed",
            LinkChange(
                before=left,
                after=left.model_copy(
                    update={
                        "blocked_by": tuple(
                            number for number in left.blocked_by if number != child
                        )
                    },
                ),
            ),
            "remove-expansion-child",
        )
    )
    child_rows = additions.setdefault(child, [])
    child_rows.append(
        (
            "core.link.changed",
            LinkChange(
                before=right,
                after=right.model_copy(
                    update={
                        "blocking": tuple(
                            number for number in right.blocking if number != origin
                        )
                    },
                ),
            ),
            "remove-expansion-origin",
        )
    )
    if not child_life.workflow_state.terminal:
        child_rows.append(
            (
                "core.state.changed",
                disposition_change(
                    profile,
                    child_life,
                    profile.lifecycle.non_delivery,
                    f"Expansion {action}: {rationale}",
                    None,
                    terminal=True,
                ).model_copy(update={"mode": mode}),
                "finish-expansion-child",
            )
        )


def decide_trip(
    repository,
    snapshot,
    graph,
    profile,
    mode,
    owner,
    digest,
    origin,
    decision,
    analysis,
    rationale,
    expansion=None,
    *,
    at=None,
):
    """Retain an exact authored analysis and disposition on the stopped attempt."""
    active = current_attempt(graph.states[origin])
    if (
        active is None
        or not active.closed
        or not facts(graph.states[origin], "core.trip.recorded")
    ):
        raise ValueError("The selected story has no recorded stopped trip.")
    key = active.started.attempt
    if not any(
        item.attempt == key
        for item in facts(graph.states[origin], "core.trip.recorded")
    ):
        raise ValueError("The trip does not belong to the current stopped attempt.")
    if any(
        item.attempt == key for item in facts(graph.states[origin], "core.trip.decided")
    ):
        raise ValueError("The stopped attempt already has a decision.")
    if not rationale.strip() or not analysis.startswith(
        f".aitm/stories/{origin // 100:03d}/{origin}/plan/"
    ):
        raise ValueError(
            "Supply a rationale and an analysis in the affected story's plan."
        )
    fact = TripDecided(
        attempt=key,
        generation=active.generation,
        decision=decision,
        rationale=rationale,
        analysis_path=analysis,
        expansion_disposition=expansion,
    )
    pinned = repository.read_blobs(snapshot.tree, (analysis,))
    if not pinned[analysis]:
        raise ValueError(
            "The trip analysis is absent from the pinned planning history."
        )
    child = expansion_child(graph.states[origin], key)
    held = [
        row
        for row in facts(graph.states[origin], "core.expansion.reserved")
        if row.attempt == key
    ]
    retired = {
        row.reservation
        for row in facts(graph.states[origin], "core.expansion.reservation-resolved")
    }
    if child is None and any(row.reservation not in retired for row in held):
        raise ValueError(
            "Reconcile the still-pending identity before deciding child scope."
        )
    events = EventContext(
        uuid4().hex, owner, (at or datetime.now(UTC)).isoformat(), digest
    )
    additions = {origin: [("core.trip.decided", fact, "decision")]}
    expansion_disposition(
        graph, profile, origin, child, mode, expansion, rationale, additions
    )
    return _operation(
        events,
        graph,
        "core.trip.decide",
        fact.model_dump_json().encode(),
        additions,
        extra_reads=pinned,
    )
