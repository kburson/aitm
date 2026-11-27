"""Build the typed operation that owns structured story descriptions."""

from dataclasses import dataclass
from hashlib import sha256
from json import dumps

from pydantic import BaseModel, ConfigDict, field_validator

from aitm_core.documents import canonicalize
from aitm_core.events import core_reducers, fold
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventEnvelope, validate_envelope
from aitm_core.models.lifecycle import Description, LifecycleState
from aitm_core.models.operations import (
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.store.backend import Blobs


class DescriptionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    title: str
    actor: str
    want: str
    so_that: str
    scope: str

    @field_validator("title", "actor", "want", "so_that", "scope")
    @classmethod
    def require_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("structured description fields require content")
        return value


@dataclass(frozen=True, slots=True)
class DescriptionTarget:
    story_id: int
    blobs: Blobs
    owner: OperationOwner
    policy_digest: str
    operation_id: str
    timestamp: str


def description_path(story_id: int) -> str:
    return f".aitm/stories/{story_id // 100:03d}/{story_id}/description.md"


def describe(story: DescriptionTarget, fields: DescriptionInput) -> Operation:
    """Build one atomic write from a pinned story stream and document read set."""
    event_path = story_event_path(story.story_id)
    document_path = description_path(story.story_id)
    prior_log = story.blobs[event_path]
    if prior_log is None:
        raise ValueError("the description target story has no initialized event stream")
    state = fold(prior_log.splitlines(keepends=True), core_reducers())
    if state.story_id != story.story_id or not isinstance(
        state.domains.get("lifecycle"), LifecycleState
    ):
        raise ValueError("the description target must be an initialized story")

    schema = DocumentSchema()
    header = dumps(
        {
            "schema": schema.name,
            "role": "description",
            "story": story.story_id,
            "title": fields.title,
        },
        ensure_ascii=False,
    )
    body = (
        f"As {fields.actor}\n\nI want {fields.want}\n\nSo that {fields.so_that}"
        f"\n\n## Scope\n\n{fields.scope}"
    )
    document = f"---\n{header}\n---\n{body}".encode()
    description = Description(
        title=fields.title,
        **{"as": fields.actor},
        want=fields.want,
        so_that=fields.so_that,
        scope=fields.scope,
        content_hash=canonicalize(document, schema).canonical_sha256,
    )
    read_set = tuple(
        ReadExpectation(
            path=path, digest=sha256(raw).hexdigest() if raw is not None else None
        )
        for path, raw in (
            (event_path, prior_log),
            (document_path, story.blobs[document_path]),
        )
    )
    event = (
        EventEnvelope(
            v=1,
            id=f"{story.operation_id}:description",
            ts=story.timestamp,
            type="core.description.set",
            story=story.story_id,
            actor=story.owner.actor,
            operation_id=story.operation_id,
            sequence=state.next_sequence,
            prior_log_digest=state.prior_log_digest,
            policy_digest=story.policy_digest,
            data=description.model_dump(mode="json", by_alias=True),
        )
        .model_dump_json(exclude_none=True)
        .encode()
    )
    validate_envelope(event)
    return Operation(
        operation_id=story.operation_id,
        owner=story.owner,
        policy_digest=story.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind="story.describe",
            version=1,
            related_preconditions=read_set,
            payload=b"{}",
        ),
        change=RelatedWriteSet(
            read_set=read_set,
            events=(EventAppend(story=story.story_id, records=(event,)),),
            writes=(BlobWrite(path=document_path, content=document),),
        ),
    )
