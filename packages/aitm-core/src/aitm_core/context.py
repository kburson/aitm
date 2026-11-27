"""Export discussion context from one pinned planning tree."""

from dataclasses import dataclass
from shlex import join

from aitm_core.index.build import IndexView
from aitm_core.index.query import Query, query
from aitm_core.models.lifecycle import Relationships


@dataclass(frozen=True, slots=True)
class ContextPacket:
    story: int
    title: str
    description: str
    state: str | None
    relationships: Relationships | None
    lessons: tuple[str, ...]
    commit: str
    tree: str
    suggested_invocation: str


def discuss(story: int, snapshot: IndexView) -> ContextPacket:
    """Assemble the packet and command suggestion without executing a harness."""
    if story <= 0:
        raise ValueError("discussion requires a positive story ID")
    rows = query(snapshot, Query(story=story)).rows
    if not rows:
        raise ValueError("story is absent from the pinned discussion snapshot")
    record = rows[0]
    return ContextPacket(
        story=story,
        title=record.title,
        description=record.text,
        state=record.state,
        relationships=record.relationships,
        lessons=record.lessons,
        commit=snapshot.snapshot.revision,
        tree=snapshot.snapshot.tree,
        suggested_invocation=join(
            [
                "codex",
                f"Discuss AITM story {story} using the exported packet "
                f"from planning tree {snapshot.snapshot.tree}.",
            ]
        ),
    )
