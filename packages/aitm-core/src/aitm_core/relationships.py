"""Build reciprocal relationship edits from a pinned planning graph."""

from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aitm_core.events import StoryState, core_reducers, fold
from aitm_core.models.events import EventEnvelope
from aitm_core.models.lifecycle import (
    LifecycleFact,
    LifecycleState,
    LinkChange,
    Relationships,
)
from aitm_core.models.operations import (
    EventAppend,
    OperationOwner,
    Positive,
    story_event_path,
    story_scope,
)
from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import Repository
from aitm_core.store.validation import _entries


class GraphConflict(ValueError):
    """A related-story request conflicts with the pinned graph."""


class LinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    story: Positive
    other: Positive
    relation: Literal["parent", "blocked-by"]
    remove: bool = False


@dataclass(frozen=True, slots=True)
class StoryGraph:
    stories: dict[int, LifecycleState]
    states: dict[int, StoryState]
    logs: dict[str, bytes | None]


def read_graph(repo: Repository, snapshot: Snapshot) -> StoryGraph:
    paths = []
    for path in _entries(repo, snapshot):
        if path.endswith("/events.jsonl"):
            story = story_scope(path)
            if story is not None and path == story_event_path(story):
                paths.append(path)
    logs = dict(repo.read_blobs(snapshot.tree, tuple(sorted(paths))))
    states = {}
    stories = {}
    for path, raw in logs.items():
        if not raw:
            continue
        state = fold(raw.splitlines(keepends=True), core_reducers())
        assert state.story_id is not None
        life = state.domains.get("lifecycle")
        if isinstance(life, LifecycleState):
            stories[state.story_id] = life
            states[state.story_id] = state
    return StoryGraph(stories, states, logs)


def validate_graph(
    relations: dict[int, Relationships],
    kinds: dict[int, str],
    replacements: dict[int, int],
) -> None:
    parents = {}
    prerequisites = {}
    for number, facts in relations.items():
        associated = (*facts.children, *facts.blocking, *facts.blocked_by)
        if facts.parent is not None:
            associated = (*associated, facts.parent)
        if number in associated or replacements.get(number) == number:
            raise GraphConflict("A story cannot link to itself.")
        if any(target not in relations for target in associated):
            raise GraphConflict("A related story has no initialized identity.")
        if facts.parent is not None and (
            kinds[facts.parent] != "epic"
            or number not in relations[facts.parent].children
        ):
            raise GraphConflict("An epic parent requires a reciprocal child link.")
        for child in facts.children:
            if relations[child].parent != number:
                raise GraphConflict("An epic child requires a reciprocal parent link.")
        if any(
            number not in relations[target].blocking for target in facts.blocked_by
        ) or any(
            number not in relations[target].blocked_by for target in facts.blocking
        ):
            raise GraphConflict("A dependency requires its reciprocal link.")
        parents[number] = () if facts.parent is None else (facts.parent,)
        replacement = replacements.get(number)
        if replacement is not None and replacement not in relations:
            raise GraphConflict("A replacement must name an initialized story.")
        prerequisites[number] = facts.blocked_by + (
            () if replacement is None else (replacement,)
        )
    for graph, kind in (
        (parents, "parent"),
        (prerequisites, "dependency or replacement"),
    ):
        try:
            tuple(TopologicalSorter(graph).static_order())
        except CycleError as error:
            raise GraphConflict(f"The {kind} graph contains a cycle.") from error


def checked_relations(
    graph: StoryGraph,
    changes: dict[int, Relationships],
    new: tuple[int, str] | None = None,
) -> None:
    relations = {number: life.relationships for number, life in graph.stories.items()}
    kinds = {number: life.kind for number, life in graph.stories.items()}
    replacements = {
        number: last.replacement_story
        for number, life in graph.stories.items()
        if life.transitions
        and (last := life.transitions[-1]).replacement_story is not None
    }
    relations.update(changes)
    if new is not None:
        kinds[new[0]] = new[1]
    validate_graph(relations, kinds, replacements)


def link_changes(graph: StoryGraph, request: LinkRequest) -> dict[int, Relationships]:
    number, other = request.story, request.other
    if number == other:
        raise GraphConflict("A story cannot link to itself.")
    if number not in graph.stories or other not in graph.stories:
        raise GraphConflict("Both relationship endpoints must be initialized stories.")
    left = graph.stories[number].relationships
    right = graph.stories[other].relationships
    changes = {}

    def amend(values: tuple[int, ...], member: int, remove: bool) -> tuple[int, ...]:
        return tuple(
            sorted(set(values) - {member} if remove else set(values) | {member})
        )

    if request.relation == "parent":
        if request.remove and left.parent != other:
            raise GraphConflict("The selected epic is not the current parent.")
        if left.parent is not None and left.parent != other:
            previous = graph.stories[left.parent].relationships
            changes[left.parent] = previous.model_copy(
                update={"children": amend(previous.children, number, True)}
            )
        changes[number] = left.model_copy(
            update={"parent": None if request.remove else other}
        )
        changes[other] = right.model_copy(
            update={"children": amend(right.children, number, request.remove)}
        )
    else:
        changes[number] = left.model_copy(
            update={"blocked_by": amend(left.blocked_by, other, request.remove)}
        )
        changes[other] = right.model_copy(
            update={"blocking": amend(right.blocking, number, request.remove)}
        )
    checked_relations(graph, changes)
    return {
        key: after
        for key, after in changes.items()
        if after != graph.stories[key].relationships
    }


@dataclass(frozen=True, slots=True)
class EventContext:
    operation: str
    owner: OperationOwner
    stamp: str
    policy_digest: str

    def encode(
        self, story: int, name: str, state: StoryState, fact: LifecycleFact, label: str
    ) -> bytes:
        return (
            EventEnvelope(
                v=1,
                id=f"{self.operation}:{label}:{story}",
                ts=self.stamp,
                type=name,
                story=story,
                actor=self.owner.actor,
                operation_id=self.operation,
                sequence=state.next_sequence,
                prior_log_digest=state.prior_log_digest,
                policy_digest=self.policy_digest,
                data=fact.model_dump(mode="json", by_alias=True, exclude_none=True),
            )
            .model_dump_json(exclude_none=True)
            .encode()
        )


def reciprocal_events(
    graph: StoryGraph, changes: dict[int, Relationships], context: EventContext
) -> tuple[EventAppend, ...]:
    return tuple(
        EventAppend(
            story=number,
            records=(
                context.encode(
                    number,
                    "core.link.changed",
                    graph.states[number],
                    LinkChange(before=graph.stories[number].relationships, after=after),
                    "links",
                ),
            ),
        )
        for number, after in sorted(changes.items())
    )
