"""Clone-local binding identities and authority-neutral receipts."""

from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aitm_core.models.attempts import BindingPurpose, EvidenceOperation, SourceSnapshot
from aitm_core.models.common import StoreAnchor
from aitm_core.models.events import DIGEST
from aitm_core.models.operations import repository_path, story_scope
from aitm_core.store.validation import PlanningPath, classify_planning_path

Name = Annotated[str, Field(min_length=1, pattern=r"\S")]
Positive = Annotated[int, Field(gt=0)]


class BindingFact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class StoryRef(BindingFact):
    kind: Literal["story"] = "story"
    story: Positive


class EntityRef(BindingFact):
    kind: Literal["entity"] = "entity"
    identity: Name
    document: str

    @model_validator(mode="after")
    def check_document(self):
        parts = PurePosixPath(repository_path(self.document)).parts
        is_idea = len(parts) == 4 and parts[:2] == (".aitm", "ideas")
        is_draft = (
            len(parts) == 5
            and parts[:2] == (".aitm", "drafts")
            and parts[-1] == "draft.md"
        )
        if (
            not (is_idea or is_draft)
            or classify_planning_path(self.document) != PlanningPath.DATA
        ):
            raise ValueError(
                "An entity binding requires a canonical idea or draft document."
            )
        return self


ScopeRef = Annotated[StoryRef | EntityRef, Field(discriminator="kind")]


def allows_authored(scope: StoryRef | EntityRef, path: str) -> bool:
    try:
        parts = PurePosixPath(repository_path(path)).parts
        role = classify_planning_path(path)
    except ValueError:
        return False
    if role != PlanningPath.DATA:
        return False
    if isinstance(scope, StoryRef):
        if story_scope(path) != scope.story:
            return False
        tail = parts[4:]
        return tail == ("draft.md",) or (
            len(tail) > 1
            and tail[0] in {"design", "plan", "attachments"}
            and not any(part in {"reviews", "review"} for part in tail[:-1])
        )
    document = PurePosixPath(scope.document)
    if parts == document.parts:
        return True
    return document.name == "draft.md" and parts[: len(document.parts)] == (
        *document.parts[:-1],
        "attachments",
    )


class BoundPath(BindingFact):
    path: str
    digest: DIGEST | None


class Binding(BindingFact):
    identity: Name
    generation: Positive
    anchor: StoreAnchor
    scope: ScopeRef
    purpose: BindingPurpose
    session: Name
    worktree: Name
    git_directory: Name
    planning: SourceSnapshot
    paths: tuple[BoundPath, ...]
    attempt: Name | None = None
    branch: str | None = None
    source: SourceSnapshot | None = None
    recovery_authority: Name | None = None
    capabilities: tuple[EvidenceOperation, ...] = ()
    active: bool = True
