"""An explicit, auditable link from one bounded observation to a story."""

from dataclasses import dataclass
from uuid import UUID

from ..types import SourceRef
from .receipts import require_digest, require_item


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
