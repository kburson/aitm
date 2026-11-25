"""Verified assignment boundaries and auditable links for effort evidence."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from ..types import SourceRef
from .receipts import NativeTurn, require_digest, require_item


@dataclass(frozen=True, slots=True)
class Attribution:
    project_id: UUID
    observation_id: str
    epic: int | None
    story: int
    authorization: SourceRef

    def __post_init__(self) -> None:
        require_digest(self.observation_id)
        require_item(self.epic)
        require_item(self.story)
        if self.story is None:
            raise ValueError("A late attribution requires a story")


class MarkerKind(StrEnum):
    START = "start"
    END = "end"


@dataclass(frozen=True, slots=True)
class ScopeMarker:
    """Trusted caller evidence for one exact native turn and enrolled attempt."""

    project_id: UUID
    attempt_id: UUID
    turn: NativeTurn
    kind: MarkerKind
    clock: SourceRef
    at: datetime
    proof: SourceRef

    def __post_init__(self) -> None:
        if self.at.utcoffset() is None or not isinstance(self.kind, MarkerKind):
            raise ValueError("Expected a timezone-aware start or end marker")
        object.__setattr__(self, "at", self.at.astimezone(UTC))


@dataclass(frozen=True, slots=True)
class Handoff:
    """A verified detach at the predecessor end and attach at the successor start."""

    project_id: UUID
    predecessor: NativeTurn
    successor: NativeTurn
    proof: SourceRef

    def __post_init__(self) -> None:
        if self.predecessor.session_key == self.successor.session_key:
            raise ValueError("A handoff requires a different native session")
