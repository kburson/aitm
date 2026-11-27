"""Ownership and content-identity types for v1 authored documents."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SEMANTIC_TYPES = Literal[
    "array", "boolean", "integer", "null", "number", "object", "string"
]
DOCUMENT_SCHEMA = "aitm.doc/v1"
CANONICAL_SCHEMA = "aitm.authored-content/v1"


class DocumentSchema(BaseModel):
    """Select the fixed v1 contract and any explicitly declared semantic keys."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    name: Literal["aitm.doc/v1"] = DOCUMENT_SCHEMA
    semantic_fields: dict[str, SEMANTIC_TYPES] = Field(default_factory=dict)


class Metadata(BaseModel):
    """A partial update to generated keys. An explicit null removes its field."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, validate_by_name=True
    )

    created: str | None = None
    updated: str | None = None
    last_branch: str | None = Field(default=None, alias="last-branch")
    last_worktree: str | None = Field(default=None, alias="last-worktree")
    status: str | None = None


class ContentIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["aitm.authored-content/v1"] = CANONICAL_SCHEMA
    canonical_sha256: str
    raw_sha256: str
