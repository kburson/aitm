"""Immutable inputs for pinned, typed planning-store operations."""

from enum import StrEnum
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Annotated, Self

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from aitm_core.models.events import DIGEST, EventActor
from aitm_core.models.evidence import GuardEvaluated

Nonempty = Annotated[str, Field(min_length=1)]
Positive = Annotated[int, Field(gt=0)]


class OperationCategory(StrEnum):
    NORMAL = "normal"
    AUTHORED_SYNC = "authored_sync"
    STOP_RECONCILIATION = "stop_reconciliation"
    RECOVERY = "recovery"


class AuthorityOrigin(StrEnum):
    FIXTURE = "fixture"
    REGISTERED = "registered"


class PreflightOutcome(StrEnum):
    NOT_APPLICABLE = "not-applicable"
    PASSED = "passed"
    BLOCKED = "blocked"
    UNAVAILABLE = "unavailable"


class OperationFact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        ser_json_bytes="base64",
        revalidate_instances="always",
    )


class PreflightResult(OperationFact):
    outcome: PreflightOutcome
    origin: AuthorityOrigin | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def check_provenance(self) -> Self:
        if self.outcome == PreflightOutcome.PASSED and self.origin is None:
            raise ValueError(
                "passing preflight requires registered or fixture provenance"
            )
        return self


class WriteAuthorization(OperationFact):
    allowed: bool
    origin: AuthorityOrigin
    reason: str | None = None


class OperationOwner(OperationFact):
    actor: EventActor
    binding: Nonempty | None = None
    generation: Positive | None = None

    @model_validator(mode="after")
    def check_binding(self) -> Self:
        if (self.binding is None) != (self.generation is None):
            raise ValueError(
                "binding identity and generation must be supplied together"
            )
        return self


def repository_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not path.parts
        or path.is_absolute()
        or path.as_posix() != value
        or ".." in path.parts
        or any(character in value for character in ("\0", "\r", "\n", "\\"))
    ):
        raise ValueError("expected a normalized repository-relative file path")
    return value


def story_event_path(story: int) -> str:
    return f".aitm/stories/{story // 100:03d}/{story}/events.jsonl"


def story_scope(path: str) -> int | None:
    parts = PurePosixPath(path).parts
    if parts[:2] != (".aitm", "stories"):
        return None
    if len(parts) < 5 or not parts[3].isascii() or not parts[3].isdecimal():
        raise ValueError("expected a numbered story path")
    story = int(parts[3])
    if story <= 0 or parts[3] != str(story) or parts[2] != f"{story // 100:03d}":
        raise ValueError("invalid story path identity")
    return story


class ReadExpectation(OperationFact):
    path: Nonempty
    digest: DIGEST | None

    _path = field_validator("path")(repository_path)


class BlobWrite(OperationFact):
    path: Nonempty
    content: bytes | None

    _path = field_validator("path")(repository_path)


class EventAppend(OperationFact):
    story: Positive
    records: Annotated[tuple[bytes, ...], Field(min_length=1)]

    @property
    def path(self) -> str:
        return story_event_path(self.story)


class RelatedWriteSet(OperationFact):
    read_set: tuple[ReadExpectation, ...]
    writes: tuple[BlobWrite, ...] = ()
    events: tuple[EventAppend, ...] = ()

    @model_validator(mode="after")
    def check_coverage(self) -> Self:
        reads = {item.path for item in self.read_set}
        if len(reads) != len(self.read_set):
            raise ValueError("duplicate read expectation")
        changes = [item.path for item in (*self.writes, *self.events)]
        if len(set(changes)) != len(changes):
            raise ValueError("duplicate write destination")
        if not set(changes).issubset(reads):
            raise ValueError("each write requires a pinned precondition")
        for write in self.writes:
            story = story_scope(write.path)
            if story is None:
                continue
            event_path = story_event_path(story)
            if write.path == event_path:
                raise ValueError("story events require an append operation")
            if event_path not in reads:
                raise ValueError("story writes require the pinned attempt stream")
        return self

    @property
    def read_set_digest(self) -> str:
        values = [item.model_dump(mode="json") for item in self.read_set]
        return sha256(
            rfc8785.dumps(sorted(values, key=lambda row: row["path"]))
        ).hexdigest()


class FinalizationIntent(OperationFact):
    kind: Nonempty
    version: Positive
    related_preconditions: tuple[ReadExpectation, ...]
    payload: bytes


class Operation(OperationFact):
    operation_id: Nonempty
    owner: OperationOwner
    policy_digest: DIGEST
    category: OperationCategory
    intent: FinalizationIntent
    change: RelatedWriteSet
    guards: tuple[GuardEvaluated, ...] = ()
    pending_actions: tuple[Nonempty, ...] = ()

    @model_validator(mode="after")
    def check_related_preconditions(self) -> Self:
        reads = {item.path: item.digest for item in self.change.read_set}
        for item in self.intent.related_preconditions:
            if item.path not in reads or reads[item.path] != item.digest:
                raise ValueError("related precondition is not pinned in the read set")
        if len(set(self.pending_actions)) != len(self.pending_actions):
            raise ValueError("duplicate pending action identity")
        return self

    @property
    def request_digest(self) -> str:
        return sha256(rfc8785.dumps(self.model_dump(mode="json"))).hexdigest()
