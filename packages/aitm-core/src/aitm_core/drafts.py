"""Create unnumbered entities and discard a whole draft in one planning operation."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps
from pathlib import PurePosixPath
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from aitm_core.documents import DocumentError, _parse
from aitm_core.models.binding import EntityRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import EventActor, validate_envelope
from aitm_core.models.lifecycle import Graduation
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
)
from aitm_core.paths import intake_location, intake_slug, vacant_path
from aitm_core.services import ServicePorts, mutate
from aitm_core.store.backend import Blobs, OperationResult, Snapshot
from aitm_core.store.git_backend import _Record, _record_path
from aitm_core.store.installation import Installation
from aitm_core.store.objects import Repository
from aitm_core.store.validation import _entries

_DISCARDED = ".aitm/drafts/discarded"
_ENTITY_SCHEMA = "aitm.intake/v1"
type EntityKind = Literal["idea", "draft"]


@dataclass(frozen=True, slots=True)
class CreateEntity:
    title: str
    body: str = ""
    tags: tuple[str, ...] = ()


class CreatedEntity(EntityRef):
    command: CommandResult


class CreationFailed(ValueError):
    def __init__(self, command: CommandResult) -> None:
        self.command = command
        super().__init__("entity creation did not complete")


class Tombstone(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["aitm.draft-discard/v1"] = "aitm.draft-discard/v1"
    event: Literal["core.draft.discarded"] = "core.draft.discarded"
    entity: EntityRef
    title: str
    reason: str
    discarded_by: EventActor
    discarded_at: datetime
    operation_id: str
    prior_tree: str
    attachments: dict[str, str]


@dataclass(frozen=True, slots=True)
class _LiveEntity:
    ref: EntityRef
    title: str
    slug: str


@dataclass(frozen=True, slots=True)
class Intake:
    installation: Installation
    snapshot: Snapshot
    policy_digest: str
    owner: OperationOwner
    stamp: datetime

    @property
    def repository(self) -> Repository:
        return self.installation.repository

    def _blobs(self, paths: Iterable[str]) -> Blobs:
        return self.repository.read_blobs(self.snapshot.tree, tuple(paths))

    def _apply(
        self, identity: str, event: str, payload: bytes, before: Blobs, writes: Blobs
    ) -> OperationResult:
        reads = tuple(
            ReadExpectation(
                path=path, digest=sha256(raw).hexdigest() if raw is not None else None
            )
            for path, raw in before.items()
        )
        operation = Operation(
            operation_id=identity,
            owner=self.owner,
            category=OperationCategory.NORMAL,
            policy_digest=self.policy_digest,
            intent=FinalizationIntent(
                kind=event, version=1, related_preconditions=reads, payload=payload
            ),
            change=RelatedWriteSet(
                read_set=reads,
                writes=tuple(
                    BlobWrite(path=path, content=raw) for path, raw in writes.items()
                ),
            ),
        )

        def authorize(
            owner: OperationOwner, change: RelatedWriteSet
        ) -> WriteAuthorization:
            return WriteAuthorization(
                allowed=owner == self.owner and change == operation.change,
                origin=AuthorityOrigin.REGISTERED,
            )

        return mutate(
            self.installation,
            operation,
            self.snapshot,
            ports=ServicePorts(write_authorization=authorize),
        )

    def create_idea(self, request: CreateEntity) -> CreatedEntity:
        return self._create("idea", request)

    def create_draft(self, request: CreateEntity) -> CreatedEntity:
        return self._create("draft", request)

    def _create(self, kind: EntityKind, request: CreateEntity) -> CreatedEntity:
        title = request.title.strip()
        if not title or any(not tag.strip() for tag in request.tags):
            raise ValueError("a title and nonempty tags are required")
        slug = intake_slug(title)
        month, stem = intake_location(self.stamp, slug)
        occupied = _entries(self.repository, self.snapshot)
        root = f".aitm/{kind}s/{month}"
        if kind == "idea":
            document = vacant_path(root, stem, ".md", occupied)
        else:
            folder = vacant_path(root, stem, "", occupied)
            document = f"{folder}/draft.md"
        identity = uuid4().hex
        metadata = {
            "schema": _ENTITY_SCHEMA,
            "event": f"core.{kind}.created",
            "identity": identity,
            "title": title,
            "slug": slug,
            "created": self.stamp.astimezone(UTC).isoformat(),
            "tags": request.tags,
        }
        content = f"---\n{dumps(metadata)}\n---\n{request.body}".encode()
        operation = self._apply(
            identity,
            f"core.{kind}.created",
            dumps({"path": document, "tags": request.tags}).encode(),
            {document: None},
            {document: content},
        )
        if operation.command.local != LocalOutcome.COMPLETED:
            raise CreationFailed(operation.command)
        return CreatedEntity(
            identity=identity, document=document, command=operation.command
        )

    def _live(
        self, kind: EntityKind, occupied: Iterable[str]
    ) -> tuple[_LiveEntity, ...]:
        documents = (
            path
            for path in sorted(occupied)
            if path.startswith(f".aitm/{kind}s/")
            and path.endswith(".md" if kind == "idea" else "/draft.md")
        )
        entities = []
        for path, raw in self._blobs(documents).items():
            assert raw is not None
            try:
                header = _parse(raw).header
            except DocumentError:
                continue
            if header.get("schema") != _ENTITY_SCHEMA:
                continue
            identity, title, slug = (
                header.get(key) for key in ("identity", "title", "slug")
            )
            if (
                not isinstance(identity, str)
                or not isinstance(title, str)
                or not isinstance(slug, str)
            ):
                raise ValueError(f"Incomplete intake metadata at {path}.")
            entities.append(
                _LiveEntity(EntityRef(identity=identity, document=path), title, slug)
            )
        return tuple(entities)

    def list_entities(self, kind: EntityKind) -> tuple[EntityRef, ...]:
        return tuple(
            entity.ref
            for entity in self._live(kind, _entries(self.repository, self.snapshot))
        )

    def _graduated(self, handle: str, occupied: Iterable[str]) -> bool:
        paths = (
            path
            for path in occupied
            if path.startswith(".aitm/stories/") and path.endswith("/events.jsonl")
        )
        for raw in self._blobs(paths).values():
            assert raw is not None
            # A typed story's initial event records the permanent draft source.
            records = raw.splitlines()
            if records:
                event = validate_envelope(records[0])
                if event.type == "core.story.graduated":
                    source = Graduation.model_validate_json(dumps(event.data))
                    if source.source_kind == "draft" and source.source_id == handle:
                        return True
        return False

    def _failure(
        self, outcome: LocalOutcome, reason: str, identity: str | None = None
    ) -> OperationResult:
        command = CommandResult(
            operation_id=identity or uuid4().hex, local=outcome, evidence=(reason,)
        )
        return OperationResult(command, self.snapshot, reason)

    def _retry(
        self, handle: str, reason: str, occupied: Mapping[str, object]
    ) -> OperationResult:
        from aitm_core.cli.dispatch import publish

        for path, raw in self._blobs(
            path for path in occupied if path.startswith(_DISCARDED + "/")
        ).items():
            assert raw is not None
            tombstone = Tombstone.model_validate_json(raw)
            if handle not in {tombstone.entity.identity, tombstone.operation_id}:
                continue
            identity = tombstone.operation_id
            if tombstone.reason != reason:
                return self._failure(
                    LocalOutcome.CONFLICT,
                    "The retained discard has a different reason.",
                    identity,
                )
            record_path = _record_path(identity)
            record = self._blobs((record_path,))[record_path]
            origin = self.repository.record_origin(self.snapshot, path)
            if (
                record is None
                or self.repository.record_origin(self.snapshot, record_path) != origin
            ):
                raise ValueError(
                    "Discard tombstone does not share the operation receipt's commit."
                )
            receipt = _Record.model_validate_json(record)
            if (
                receipt.command.operation_id != identity
                or receipt.command.local != LocalOutcome.COMPLETED
            ):
                raise ValueError(
                    "Discard tombstone has an inconsistent operation receipt."
                )
            command = receipt.command
            if self.installation.store.planning_remote is not None:
                command = publish(self.installation, identity)
            return OperationResult(command, origin)
        return self._failure(LocalOutcome.REFUSED, "No live draft matches that handle.")

    def discard_draft(self, handle: str, reason: str) -> OperationResult:
        reason = reason.strip()
        if not reason:
            raise ValueError("discard requires a nonempty reason")
        occupied = _entries(self.repository, self.snapshot)
        live = self._live("draft", occupied)
        candidates = tuple(
            e for e in live if handle in (e.ref.identity, e.ref.document)
        )
        if not candidates:
            candidates = tuple(e for e in live if e.slug == handle)
        if len(candidates) > 1:
            choices = ", ".join(
                f"{e.ref.identity} ({e.ref.document})" for e in candidates
            )
            return self._failure(
                LocalOutcome.CONFLICT, f"Ambiguous draft handle. Choose {choices}."
            )
        entity = candidates[0] if candidates else None
        if self._graduated(entity.ref.identity if entity else handle, occupied):
            return self._failure(LocalOutcome.REFUSED, "The draft has graduated.")
        if entity is None:
            return self._retry(handle, reason, occupied)

        folder = str(PurePosixPath(entity.ref.document).parent)
        blobs = self._blobs(path for path in occupied if path.startswith(folder + "/"))
        _, stem = intake_location(self.stamp, entity.slug)
        path = vacant_path(_DISCARDED, stem, ".json", occupied)
        identity = f"draft-discard-{entity.ref.identity}"
        tombstone = Tombstone(
            entity=entity.ref,
            title=entity.title,
            reason=reason,
            discarded_by=self.owner.actor,
            discarded_at=self.stamp.astimezone(UTC),
            operation_id=identity,
            prior_tree=self.snapshot.tree,
            attachments={
                name: sha256(raw).hexdigest()
                for name, raw in blobs.items()
                if raw is not None and name != entity.ref.document
            },
        )
        raw = tombstone.model_dump_json().encode()
        return self._apply(
            identity,
            tombstone.event,
            raw,
            {**blobs, path: None},
            {**dict.fromkeys(blobs), path: raw},
        )
