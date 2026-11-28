"""Create unnumbered entities and discard a whole draft in one planning operation."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps
from pathlib import PurePosixPath
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from aitm_core.documents import DocumentError, _parse
from aitm_core.entities import (
    ENTITY_SCHEMA,
    BindingDisposition,
    finalize_entity_binding,
)
from aitm_core.models.binding import EntityRef
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
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
    story_event_path,
    story_scope,
)
from aitm_core.paths import intake_location, intake_slug, vacant_path
from aitm_core.services import ServicePorts, mutate, preflight_policy
from aitm_core.store.backend import Blobs, OperationResult, Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.git_backend import _Record, _record_path
from aitm_core.store.installation import Installation
from aitm_core.store.objects import Repository
from aitm_core.store.validation import _entries
from aitm_core.store.workspace import BindingConflict, Workspace

_DISCARDED = ".aitm/drafts/discarded"
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
    draft_tree: str
    attachments: dict[str, str]
    binding_disposition: BindingDisposition | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


def _read_tombstones(
    repository: Repository, snapshot: Snapshot, occupied: Iterable[str]
) -> Iterator[tuple[str, Tombstone]]:
    paths = tuple(path for path in occupied if path.startswith(_DISCARDED + "/"))
    for path, raw in repository.read_blobs(snapshot.tree, paths).items():
        assert raw is not None
        yield path, Tombstone.model_validate_json(raw)


def _graduated(
    repository: Repository, snapshot: Snapshot, identity: str, occupied: Iterable[str]
) -> bool:
    paths = tuple(
        path
        for path in occupied
        if path.endswith("/events.jsonl")
        and (story := story_scope(path)) is not None
        and path == story_event_path(story)
    )
    for raw in repository.read_blobs(snapshot.tree, paths).values():
        assert raw is not None
        for record in raw.splitlines(keepends=True):
            event = validate_envelope(record)
            if event.type == "core.story.graduated":
                source = Graduation.model_validate_json(dumps(event.data))
                if source.source_kind == "draft" and source.source_id == identity:
                    return True
    return False


def draft_replay_conflict(
    repository: Repository, snapshot: Snapshot, operation: Operation
) -> str | None:
    """Check the draft namespace facts which cannot be expressed as blob reads."""
    occupied = _entries(repository, snapshot)
    if operation.intent.kind == "core.draft.created":
        (write,) = operation.change.writes
        folder = str(PurePosixPath(write.path).parent)
        if folder in occupied or any(
            path.startswith(folder + "/") for path in occupied
        ):
            return "the draft creation folder is occupied"
        if any(
            tombstone.entity.document == write.path
            for _, tombstone in _read_tombstones(repository, snapshot, occupied)
        ):
            return "the draft document path has been retired"
        return None

    tombstone = Tombstone.model_validate_json(operation.intent.payload)
    folder = str(PurePosixPath(tombstone.entity.document).parent)
    paths = {path for path in occupied if path.startswith(folder + "/")}
    if paths != {tombstone.entity.document, *tombstone.attachments}:
        return "the draft folder manifest changed"
    draft_tree = (
        repository._git("rev-parse", f"{snapshot.tree}:{folder}").decode().strip()
    )
    if draft_tree != tombstone.draft_tree:
        return "the draft folder contents changed"
    if _graduated(repository, snapshot, tombstone.entity.identity, occupied):
        return "the draft has graduated"
    return None


@dataclass(frozen=True, slots=True)
class _LiveEntity:
    ref: EntityRef
    title: str
    slug: str


def _ambiguous(kind: EntityKind, candidates: tuple[_LiveEntity, ...]) -> str:
    choices = ", ".join(
        f"{entity.ref.identity} ({entity.ref.document})" for entity in candidates
    )
    return f"Ambiguous {kind} handle. Choose {choices}."


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
            retired = {
                tombstone.entity.document
                for _, tombstone in _read_tombstones(
                    self.repository, self.snapshot, occupied
                )
            }
            folder = vacant_path(root, stem, "", occupied.keys() | retired)
            document = f"{folder}/draft.md"
        identity = uuid4().hex
        metadata = {
            "schema": ENTITY_SCHEMA,
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
            and path.count("/") == (3 if kind == "idea" else 4)
            and path.endswith(".md" if kind == "idea" else "/draft.md")
        )
        entities = []
        for path, raw in self._blobs(documents).items():
            assert raw is not None
            try:
                header = _parse(raw).header
            except DocumentError:
                continue
            if header.get("schema") != ENTITY_SCHEMA:
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

    def _matching(
        self, kind: EntityKind, handle: str, occupied: Iterable[str]
    ) -> tuple[_LiveEntity, ...]:
        entities = self._live(kind, occupied)
        exact = tuple(
            entity
            for entity in entities
            if handle in (entity.ref.identity, entity.ref.document)
        )
        return exact or tuple(entity for entity in entities if entity.slug == handle)

    def resolve_entity(self, kind: EntityKind, handle: str) -> EntityRef:
        candidates = self._matching(
            kind, handle, _entries(self.repository, self.snapshot)
        )
        if len(candidates) > 1:
            raise BindingConflict(_ambiguous(kind, candidates))
        if not candidates:
            raise BindingConflict(f"No live {kind} matches that handle.")
        return candidates[0].ref

    def _failure(
        self, outcome: LocalOutcome, reason: str, identity: str | None = None
    ) -> OperationResult:
        command = CommandResult(
            operation_id=identity or uuid4().hex, local=outcome, evidence=(reason,)
        )
        return OperationResult(command, self.snapshot, reason)

    def _retry(
        self, handle: str, reason: str, occupied: Iterable[str]
    ) -> OperationResult | None:
        from aitm_core.cli.dispatch import publish

        for path, tombstone in _read_tombstones(
            self.repository, self.snapshot, occupied
        ):
            if handle not in {
                tombstone.entity.identity,
                tombstone.entity.document,
                tombstone.operation_id,
            }:
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
                prepared = preflight_policy(self.installation)
                shared = prepared.views.shared
                # A fresh clone lacks the original outbound request. The validated
                # shared history can independently prove publication of its receipt.
                if (
                    prepared.outcome == LocalOutcome.COMPLETED
                    and shared is not None
                    and shared.status == ContinuityStatus.VERIFIED
                    and shared.valid_tip is not None
                    and self.repository._run(
                        "merge-base", "--is-ancestor", origin.revision, shared.valid_tip
                    ).returncode
                    == 0
                ):
                    command = command.model_copy(
                        update={"publication": PublicationOutcome.VERIFIED}
                    )
                else:
                    command = publish(self.installation, identity)
                    if (
                        command.publication == PublicationOutcome.PENDING
                        and command.recovery
                        and self.snapshot == origin
                        and prepared.policy is not None
                        and shared is not None
                        and shared.status == ContinuityStatus.VERIFIED
                        and shared.valid_tip is not None
                    ):
                        replacement = self._retry_tombstone_collision(
                            path,
                            tombstone,
                            receipt,
                            origin,
                            shared.valid_tip,
                            prepared.policy.source.digest,
                            command.recovery,
                        )
                        if replacement is not None:
                            return replacement
            return OperationResult(command, origin)
        return None

    def _retry_tombstone_collision(
        self,
        path: str,
        tombstone: Tombstone,
        receipt: _Record,
        origin: Snapshot,
        shared_tip: str,
        policy_digest: str,
        recovery: str,
    ) -> OperationResult | None:
        from aitm_core.store.publication import Publisher
        from aitm_core.store.reconcile import Resolution, reconcile

        shared = self.repository.read_tree(shared_tip)
        occupied = self.repository.read_blobs(shared.tree, (path,))[path]
        # Preserve any additional unpublished work. Only the one competing
        # discard can be replaced automatically after selecting the shared tip.
        if (
            occupied is None
            or Tombstone.model_validate_json(occupied).entity.identity
            == tombstone.entity.identity
            or self.repository._run(
                "merge-base", "--is-ancestor", receipt.base, shared_tip
            ).returncode
            != 0
        ):
            return None
        original = Publisher(self.installation).request(tombstone.operation_id)
        if draft_replay_conflict(self.repository, shared, original) is not None:
            return None
        selected = reconcile(
            self.installation,
            tombstone.operation_id,
            Resolution(origin.revision, shared_tip),
        )
        if selected.command.local != LocalOutcome.COMPLETED:
            return selected
        result = replace(
            self, snapshot=shared, policy_digest=policy_digest
        )._discard_draft(
            tombstone.entity.identity, tombstone.reason, Workspace(self.installation)
        )
        return replace(
            result,
            command=result.command.model_copy(
                update={"recovery": result.command.recovery or recovery}
            ),
        )

    def discard_draft(self, handle: str, reason: str) -> OperationResult:
        workspace = Workspace(self.installation)
        with workspace.lock():
            return self._discard_draft(handle, reason, workspace)

    def _discard_draft(
        self, handle: str, reason: str, workspace: Workspace
    ) -> OperationResult:
        reason = reason.strip()
        if not reason:
            raise ValueError("discard requires a nonempty reason")
        occupied = _entries(self.repository, self.snapshot)
        retained = self._retry(handle, reason, occupied)
        if retained is not None:
            return retained
        candidates = self._matching("draft", handle, occupied)
        if len(candidates) > 1:
            return self._failure(LocalOutcome.CONFLICT, _ambiguous("draft", candidates))
        entity = candidates[0] if candidates else None
        if _graduated(
            self.repository,
            self.snapshot,
            entity.ref.identity if entity else handle,
            occupied,
        ):
            return self._failure(LocalOutcome.REFUSED, "The draft has graduated.")
        if entity is None:
            return self._failure(
                LocalOutcome.REFUSED, "No live draft matches that handle."
            )

        folder = str(PurePosixPath(entity.ref.document).parent)
        blobs = self._blobs(path for path in occupied if path.startswith(folder + "/"))
        _, stem = intake_location(self.stamp, entity.slug)
        path = vacant_path(_DISCARDED, stem, ".json", occupied)
        # Only the committed tombstone fixes the operation ID. A lost CAS can
        # leave an outbound request retained without a matching store receipt.
        identity = f"draft-discard-{entity.ref.identity}-{uuid4().hex}"
        disposition = finalize_entity_binding(
            workspace, entity.ref, "discarded", self.snapshot, operation_id=identity
        )
        tombstone = Tombstone(
            entity=entity.ref,
            binding_disposition=disposition,
            title=entity.title,
            reason=reason,
            discarded_by=self.owner.actor,
            discarded_at=self.stamp.astimezone(UTC),
            operation_id=identity,
            prior_tree=self.snapshot.tree,
            draft_tree=self.repository._git(
                "rev-parse", f"{self.snapshot.tree}:{folder}"
            )
            .decode()
            .strip(),
            attachments={
                name: sha256(raw).hexdigest()
                for name, raw in blobs.items()
                if raw is not None and name != entity.ref.document
            },
        )
        raw = tombstone.model_dump_json().encode()
        result = self._apply(
            identity,
            tombstone.event,
            raw,
            {**blobs, path: None},
            {**dict.fromkeys(blobs), path: raw},
        )
        if disposition is not None and disposition.recovery:
            location = (
                workspace.state
                / "sync-recovery"
                / disposition.binding
                / disposition.recovery
            )
            return replace(
                result,
                command=result.command.model_copy(
                    update={
                        "evidence": (
                            *result.command.evidence,
                            f"Retained unsynced entity edits at {location}.",
                        ),
                        "recovery": result.command.recovery or str(location),
                    }
                ),
            )
        return result
