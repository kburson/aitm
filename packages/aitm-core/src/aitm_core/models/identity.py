"""Typed source and delivery coordinates prepared before graduation authority."""

from hashlib import sha256
from typing import Annotated, Literal, Self

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, model_validator

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.binding import EntityRef
from aitm_core.models.config import Name, Oid
from aitm_core.models.events import DIGEST
from aitm_core.models.operations import Positive


class IdentityFact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SourceDescription(IdentityFact):
    title: Name
    scope: Name
    actor: Name | None = None
    want: Name | None = None
    so_that: Name | None = None


class DeliveryTarget(IdentityFact):
    repository: Name
    ref: Annotated[str, Field(pattern=r"^refs/heads/[^\s]+$")]


class DraftSource(IdentityFact):
    kind: Literal["draft"] = "draft"
    entity: EntityRef
    snapshot: SourceSnapshot
    draft_tree: Oid
    document_digest: DIGEST

    @model_validator(mode="after")
    def check_draft(self) -> Self:
        if not self.entity.document.startswith(".aitm/drafts/"):
            raise ValueError("a draft source requires a draft document")
        return self

    @property
    def identity(self) -> str:
        return self.entity.identity

    @property
    def digest(self) -> str:
        return self.document_digest

    @property
    def semantic_key(self) -> str:
        return sha256(rfc8785.dumps([self.kind, self.entity.identity])).hexdigest()


class PlanEntrySource(IdentityFact):
    kind: Literal["plan-entry"] = "plan-entry"
    parent: Positive
    entry_key: Name
    design_digest: DIGEST
    plan_digest: DIGEST
    entry_digest: DIGEST
    descriptor: SourceDescription

    @property
    def identity(self) -> str:
        return f"{self.parent}:{self.entry_key}"

    @property
    def digest(self) -> str:
        return self.entry_digest

    @property
    def semantic_key(self) -> str:
        return sha256(
            rfc8785.dumps([self.kind, self.parent, self.entry_key])
        ).hexdigest()


FrozenSource = Annotated[DraftSource | PlanEntrySource, Field(discriminator="kind")]
