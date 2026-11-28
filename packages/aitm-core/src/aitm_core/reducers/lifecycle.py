"""Reduce C54 facts without dispatching operations or making eligibility decisions."""

from dataclasses import replace
from json import dumps

from pydantic import ValidationError

from aitm_core.events import StoryState
from aitm_core.models.events import EventEnvelope
from aitm_core.models.lifecycle import (
    Deliverable,
    Description,
    DocumentAcceptance,
    Estimate,
    Graduation,
    JitEvidence,
    KindSplit,
    LifecycleFact,
    LifecycleState,
    LinkChange,
    Relationships,
    Signoff,
    StateChange,
)

_SCHEMAS: dict[str, type[LifecycleFact]] = {
    "core.story.graduated": Graduation,
    "core.kind.changed": KindSplit,
    "core.state.changed": StateChange,
    "core.link.changed": LinkChange,
    "core.description.set": Description,
    "core.estimate.set": Estimate,
    "core.doc.accepted": DocumentAcceptance,
    "core.jit.recorded": JitEvidence,
    "core.deliverable.added": Deliverable,
    "core.signoff.recorded": Signoff,
}
_REPLACEMENT_DISPOSITIONS = {"superseded", "duplicate"}


class LifecycleIntegrityError(ValueError):
    """A lifecycle fact has invalid typed data or contradicts the retained state."""


def lifecycle_schemas() -> dict[str, type[LifecycleFact]]:
    """Return the C54-owned models for later composition."""
    return _SCHEMAS.copy()


def _relationships(story: int, relationships: Relationships) -> None:
    parent = relationships.parent
    groups = (relationships.children, relationships.blocked_by, relationships.blocking)
    if parent == story or any(story in group for group in groups):
        raise LifecycleIntegrityError("self-relationship")
    if any(len(set(group)) != len(group) for group in groups):
        raise LifecycleIntegrityError("duplicate relationship")
    if parent in relationships.children or set(relationships.blocking) & set(
        relationships.blocked_by
    ):
        raise LifecycleIntegrityError("contradictory local relationships")


def _transition(state: LifecycleState, fact: StateChange, story: int) -> LifecycleState:
    source, target, edge = fact.from_state, fact.to_state, fact.edge
    if source != state.workflow_state:
        raise LifecycleIntegrityError(
            "prior workflow observation disagrees with current state"
        )
    if (
        edge.source != source.state_id
        or edge.target != target.state_id
        or edge.workflow_id != source.workflow_id
        or edge.workflow_id != target.workflow_id
        or edge.revision != target.revision
    ):
        raise LifecycleIntegrityError("workflow edge disagrees with recorded endpoints")
    if (
        (edge.kind == "reopen") != source.terminal
        or source.terminal
        and target.terminal
    ):
        raise LifecycleIntegrityError("invalid recorded reopen edge")
    if (edge.kind == "terminal") != target.terminal or target.terminal != (
        fact.disposition is not None
    ):
        raise LifecycleIntegrityError("invalid recorded terminal disposition")
    if (fact.disposition in _REPLACEMENT_DISPOSITIONS) != (
        fact.replacement_story is not None
    ):
        raise LifecycleIntegrityError("disposition disagrees with replacement presence")
    if fact.replacement_story == story:
        raise LifecycleIntegrityError("a replacement must name a different story")
    return state.model_copy(update={"transitions": (*state.transitions, fact)})


def _split(state: LifecycleState, fact: KindSplit) -> LifecycleState:
    if (
        state.kind != fact.from_kind
        or state.workflow_state.terminal
        or not fact.decomposition_required
    ):
        raise LifecycleIntegrityError("invalid recorded bounded kind split")
    digests = sorted(
        item.canonical_digest for item in state.accepted_documents.values()
    )
    if sorted(fact.invalidated_acceptances) != digests or sorted(
        fact.invalidated_estimates
    ) != sorted(state.estimates):
        raise LifecycleIntegrityError(
            "kind split disagrees with acceptance or estimate invalidations"
        )
    return state.model_copy(
        update={
            "kind": fact.to_kind,
            "split": fact,
            "accepted_documents": {},
            "estimates": {},
            "jit": None,
        }
    )


def _update(
    state: LifecycleState, fact: LifecycleFact, event: EventEnvelope
) -> LifecycleState:
    match fact:
        case KindSplit():
            return _split(state, fact)
        case StateChange():
            return _transition(state, fact, event.story)
        case LinkChange():
            if fact.before != state.relationships:
                raise LifecycleIntegrityError(
                    "prior relationship snapshot disagrees with current state"
                )
            _relationships(event.story, fact.after)
            return state.model_copy(update={"relationships": fact.after})
        case Description():
            return state.model_copy(update={"description": fact})
        case Estimate():
            return state.model_copy(
                update={"estimates": {**state.estimates, fact.phase: fact}}
            )
        case DocumentAcceptance():
            updates = {
                "accepted_documents": {**state.accepted_documents, fact.role: fact}
            }
            if fact.role == "plan" and fact != state.accepted_documents.get("plan"):
                updates["jit"] = None
            return state.model_copy(update=updates)
        case JitEvidence():
            plan = state.accepted_documents.get("plan")
            if plan is None or (plan.canonical_digest, plan.plan_generation) != (
                fact.plan_digest,
                fact.plan_generation,
            ):
                raise LifecycleIntegrityError(
                    "JIT evidence disagrees with the current accepted plan"
                )
            return state.model_copy(
                update={"jit": fact if fact.outcome == "accepted" else None}
            )
        case Deliverable():
            previous = state.deliverables.get(fact.deliverable_id)
            if previous is not None and previous != fact:
                raise LifecycleIntegrityError(
                    "deliverable identity reused with a different binding"
                )
            return state.model_copy(
                update={
                    "deliverables": {**state.deliverables, fact.deliverable_id: fact}
                }
            )
        case Signoff():
            return state.model_copy(update={"signoffs": (*state.signoffs, fact)})
        case _:
            raise LifecycleIntegrityError("unsupported lifecycle fact")


def fold_lifecycle(state: StoryState, event: EventEnvelope) -> StoryState:
    """Fold one owned event while preserving the other domains and stream prefix."""
    schema = _SCHEMAS.get(event.type)
    if schema is None:
        raise LifecycleIntegrityError(f"event is not owned by lifecycle: {event.type}")
    if state.story_id not in (None, event.story):
        raise LifecycleIntegrityError("lifecycle event belongs to another story")
    try:
        fact = schema.model_validate_json(dumps(event.data, allow_nan=False))
    except (ValidationError, ValueError) as error:
        raise LifecycleIntegrityError(
            f"invalid lifecycle payload for {event.type}"
        ) from error

    current = state.domains.get("lifecycle")
    if isinstance(fact, Graduation):
        if current is not None or fact.initial_state.terminal:
            raise LifecycleIntegrityError("invalid recorded story graduation")
        relationships = Relationships(parent=fact.parent)
        _relationships(event.story, relationships)
        updated = LifecycleState(
            story_id=event.story,
            graduation=fact,
            kind=fact.kind,
            relationships=relationships,
        )
    else:
        if not isinstance(current, LifecycleState):
            raise LifecycleIntegrityError(
                "lifecycle fact requires a recorded graduation"
            )
        if current.story_id != event.story:
            raise LifecycleIntegrityError("lifecycle event belongs to another story")
        updated = _update(current, fact, event)
    return replace(state, domains={**state.domains, "lifecycle": updated})
