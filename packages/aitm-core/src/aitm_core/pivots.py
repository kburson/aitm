"""Apply a cooperative human scope pivot within the configured workflow."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from aitm_core.models.evidence import PivotRecorded
from aitm_core.relationships import EventContext, StoryGraph
from aitm_core.rules.trips import (
    _operation,
    _stop_rows,
    admission_commit,
    current_attempt,
    disposition_change,
    expansion_child,
    expansion_disposition,
)


@dataclass(frozen=True, slots=True)
class HumanContext:
    interactive: bool
    known_agent: bool
    requested_override: bool = False


def pivot(
    context: HumanContext,
    graph: StoryGraph,
    profile,
    mode,
    owner,
    digest,
    origin,
    reason,
    scope_change,
    expansion=None,
    *,
    at=None,
    repository=None,
    snapshot=None,
):
    """Fence the selected scope and record the human decision independently of trips."""
    if (
        not context.interactive
        or context.known_agent
        or context.requested_override
        or owner.actor.kind != "human"
    ):
        raise ValueError("Pivot requires a cooperative interactive human request.")
    if not reason.strip() or not scope_change.strip():
        raise ValueError("Pivot requires a reason and an explicit scope change.")
    state = graph.states.get(origin)
    if state is None:
        raise ValueError("The pivot story is unavailable.")
    active = current_attempt(state)
    if active is None or active.closed:
        raise ValueError("Pivot requires a current unfenced implementation attempt.")
    child = expansion_child(state, active.started.attempt)
    events = EventContext(
        uuid4().hex, owner, (at or datetime.now(UTC)).isoformat(), digest
    )
    fact = PivotRecorded(by=owner.actor, reason=reason, scope_change=scope_change)
    additions = {origin: [("core.pivot.recorded", fact, "pivot")]}

    def resolve_admission(number, execution):
        if repository is None or snapshot is None:
            return None
        return admission_commit(repository, snapshot, graph, number, execution)

    for number in (origin, child):
        if number is None:
            continue
        attempt = current_attempt(graph.states[number])
        if attempt is None or attempt.closed:
            continue
        life = graph.stories[number]
        rows = additions.setdefault(number, [])
        rows.extend(
            _stop_rows(events, number, attempt, reason, "pivot", resolve_admission)
        )
        next_state = profile.recovery.scope_pivot
        if life.workflow_state.state_id != next_state and (
            number == origin or expansion == "continue"
        ):
            rows.append(
                (
                    "core.state.changed",
                    disposition_change(
                        profile,
                        life,
                        next_state,
                        reason,
                        attempt.started.attempt,
                    ).model_copy(update={"mode": mode}),
                    "pivot-destination",
                )
            )
    expansion_disposition(
        graph, profile, origin, child, mode, expansion, reason, additions
    )
    return _operation(
        events, graph, "core.attempt.pivot", fact.model_dump_json().encode(), additions
    )
