"""Allocate and finalize local backlog identity in the governed planning order."""

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, Literal
from uuid import uuid4

from aitm_core.graduation import (
    GraduatedRecord,
    GraduationConflict,
    GraduationService,
    _check_finalization,
    completed_record,
    graduation_path,
    ordinary_finalization,
    validate_graduated_record,
)
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.identity import DraftSource, IdentityFact
from aitm_core.models.operations import (
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
    story_scope,
)
from aitm_core.providers.backlog import (
    ActionKey,
    ActionResult,
    GraduationIntent,
    GraduationResult,
    IssueRef,
    PublishedStory,
)
from aitm_core.providers.identity import reservation_root
from aitm_core.services import stage_shared_graduation
from aitm_core.store.backend import Snapshot
from aitm_core.store.validation import _entries
from aitm_core.store.workspace import BindingConflict, Workspace


def next_number(paths: Iterable[str]) -> int:
    """Keep imported and locally issued IDs reserved through every numbered path."""
    return (
        max(
            (number for path in paths if (number := story_scope(path)) is not None),
            default=0,
        )
        + 1
    )


class ProjectionRecord(IdentityFact):
    schema_version: Literal["aitm.local-projection/v1"] = "aitm.local-projection/v1"
    result: ActionResult


@dataclass(frozen=True, slots=True)
class LocalBacklog:
    service: GraduationService

    @property
    def installation(self):
        return self.service.installation

    @property
    def repo(self):
        return self.installation.repository

    def _check_intent(self, intent: GraduationIntent) -> None:
        if (
            intent.issuer.backlog != "local"
            or intent.issuer != self.installation.issuer
            or intent.shared != (self.installation.store.planning_remote is not None)
            or intent.source is None
        ):
            raise GraduationConflict(
                "The intent has no matching prepared local authority."
            )

    def _intent_ref(self, operation: str) -> str:
        digest = sha256(
            f"{self.installation.store.store_uuid}\0{operation}".encode()
        ).hexdigest()
        return f"refs/aitm/local-graduation-intents/{digest}"

    def _retained_intent(self, operation: str) -> GraduationIntent | None:
        ref = self._intent_ref(operation)
        found = self.repo._run("rev-parse", "--verify", "--quiet", ref)
        if found.returncode == 1:
            return None
        if found.returncode:
            raise GraduationConflict("Cannot verify the retained graduation request.")
        raw = self.repo._git("cat-file", "blob", found.stdout.decode().strip())
        intent = GraduationIntent.model_validate_json(raw)
        if intent.operation_id != operation:
            raise GraduationConflict("The retained operation identity does not match.")
        return intent

    def _retain_intent(self, intent: GraduationIntent) -> None:
        existing = self._retained_intent(intent.operation_id)
        if existing == intent:
            return
        if existing is not None:
            raise GraduationConflict(
                "The local operation identity is already bound to another intent."
            )
        data = intent.model_dump_json().encode()
        oid = self.repo._git("hash-object", "-w", "--stdin", data=data).decode().strip()
        result = self.repo._run(
            "update-ref",
            "--no-deref",
            self._intent_ref(intent.operation_id),
            oid,
            "0" * self.repo.oid_length,
        )
        if result.returncode and self._retained_intent(intent.operation_id) != intent:
            raise GraduationConflict("Cannot retain the exact local graduation intent.")

    def _success(
        self, intent: GraduationIntent, record: GraduatedRecord, snapshot: Snapshot
    ) -> GraduationResult:
        assert record.intent.source is not None
        path = self._projection_path(record.intent.source)
        raw = self.repo.read_blobs(snapshot.tree, (path,))[path]
        pending = (
            (f"project-backlog:{record.intent.operation_id}",) if raw is None else ()
        )
        return GraduationResult(
            intent=intent,
            command=CommandResult(
                operation_id=intent.operation_id,
                local=LocalOutcome.COMPLETED,
                publication=PublicationOutcome.VERIFIED
                if intent.shared
                else PublicationOutcome.NOT_APPLICABLE,
                pending=pending,
                evidence=("Observed the authoritative numbered story.",),
            ),
            issue=record.issue,
        )

    def _pending(
        self, intent: GraduationIntent, message: str, recovery: str | None = None
    ) -> GraduationResult:
        return GraduationResult(
            intent=intent,
            command=CommandResult(
                operation_id=intent.operation_id,
                local=LocalOutcome.UNAVAILABLE,
                publication=PublicationOutcome.PENDING
                if intent.shared
                else PublicationOutcome.NOT_APPLICABLE,
                evidence=(message,),
                recovery=recovery,
            ),
        )

    def graduate(
        self, intent: GraduationIntent, finalization: FinalizationIntent
    ) -> GraduationResult:
        return self.graduate_local(intent, finalization)

    def graduate_local(
        self, intent: GraduationIntent, finalization: FinalizationIntent
    ) -> GraduationResult:
        self._check_intent(intent)
        _check_finalization(intent, finalization)
        source = intent.source
        assert source is not None
        recovery = None
        workspace = Workspace(self.installation)
        for _attempt in range(3):
            try:
                prepared = self.service.policy()
                snapshot = self.service.snapshot(prepared)
            except GraduationConflict as error:
                return self._pending(intent, str(error), recovery)
            existing = completed_record(self.repo, snapshot, source)
            if existing is not None:
                if existing.intent.model_dump(
                    exclude={"operation_id"}
                ) != intent.model_dump(exclude={"operation_id"}):
                    raise GraduationConflict(
                        "The source graduated against another frozen intent."
                    )
                return self._success(intent, existing, snapshot)
            reservation = f"{reservation_root(source.semantic_key)}/reservation.json"
            if (
                self.repo.read_blobs(snapshot.tree, (reservation,))[reservation]
                is not None
            ):
                raise GraduationConflict(
                    "The source already has an external identity reservation."
                )
            try:
                with workspace.lock():
                    if self.repo.tip() != snapshot:
                        return self._pending(
                            intent,
                            "Local planning contains a different pending operation.",
                            recovery,
                        )
                    issue = IssueRef(
                        issuer=intent.issuer,
                        number=next_number(_entries(self.repo, snapshot)),
                    )
                    operation = self.service.build(
                        intent,
                        issue,
                        snapshot,
                        prepared,
                        finalization,
                        workspace,
                        operation=uuid4().hex,
                        authority_paths=(reservation,),
                    )
                    self._retain_intent(intent)
                    if intent.shared:
                        staged = stage_shared_graduation(
                            self.installation,
                            operation,
                            snapshot,
                            ports=self.service.commit_ports(operation),
                        )
                    else:
                        staged = self.service.commit(operation, snapshot)
            except BindingConflict as error:
                raise GraduationConflict(str(error)) from error
            recovery = staged.command.recovery or recovery
            if not intent.shared and staged.command.local == LocalOutcome.COMPLETED:
                record = completed_record(self.repo, staged.snapshot, source)
                if record is None:
                    raise GraduationConflict(
                        "Local finalization lacks its durable semantic receipt."
                    )
                return self._success(intent, record, staged.snapshot)
        try:
            verified = self.service.snapshot(self.service.policy())
            record = completed_record(self.repo, verified, source)
            if record is not None:
                if record.intent.model_dump(
                    exclude={"operation_id"}
                ) != intent.model_dump(exclude={"operation_id"}):
                    raise GraduationConflict(
                        "The source graduated against another frozen intent."
                    )
                return self._success(intent, record, verified)
        except GraduationConflict as error:
            return self._pending(intent, str(error), recovery)
        return self._pending(
            intent,
            "The proposed number has not been verified in planning history.",
            recovery,
        )

    def _records(self, snapshot: Snapshot) -> tuple[GraduatedRecord, ...]:
        paths = tuple(
            path
            for path in _entries(self.repo, snapshot)
            if path.startswith(".aitm/identity/") and path.endswith("/graduated.json")
        )
        records = []
        for path, raw in self.repo.read_blobs(snapshot.tree, paths).items():
            assert raw is not None
            validate_graduated_record(path, raw)
            record = GraduatedRecord.model_validate_json(raw)
            if record.issue.issuer == self.installation.issuer:
                records.append(record)
        return tuple(records)

    def resume(
        self, handle: str, *, source_handle: bool = False
    ) -> GraduationResult | None:
        intent = None if source_handle else self._retained_intent(handle)
        try:
            snapshot = self.service.snapshot(self.service.policy())
        except GraduationConflict as error:
            if intent is not None:
                return self._pending(intent, str(error))
            raise
        for record in self._records(snapshot):
            source = record.intent.source
            matches = (
                isinstance(source, DraftSource)
                and handle in {source.identity, source.entity.document}
                if source_handle
                else handle == record.intent.operation_id
            )
            if matches:
                return self._success(record.intent, record, snapshot)
        if intent is None:
            return None
        finalization = (
            intent.finalization.to_intent()
            if intent.finalization
            else ordinary_finalization()
        )
        return self.graduate(intent, finalization)

    def project_latest(
        self, publication: PublishedStory, key: ActionKey
    ) -> ActionResult:
        if (
            publication.issue.issuer != self.installation.issuer
            or key.action_id != "project-backlog"
        ):
            return ActionResult(
                publication=publication, action=key, status="unsupported"
            )
        prepared = self.service.policy()
        assert prepared.policy is not None
        snapshot = self.service.snapshot(prepared)
        if self.repo._run(
            "merge-base",
            "--is-ancestor",
            publication.planning_commit,
            snapshot.revision,
        ).returncode:
            return ActionResult(publication=publication, action=key, status="pending")
        for record in self._records(snapshot):
            if (
                record.issue == publication.issue
                and record.intent.operation_id == key.operation_id
            ):
                assert record.intent.source is not None
                source = graduation_path(record.intent.source)
                origin = self.repo.record_origin(snapshot, source)
                if self.repo._run(
                    "merge-base",
                    "--is-ancestor",
                    origin.revision,
                    publication.planning_commit,
                ).returncode:
                    break
                return self._record_projection(
                    record, publication, key, snapshot, prepared.policy.source.digest
                )
        return ActionResult(publication=publication, action=key, status="pending")

    @staticmethod
    def _projection_path(source) -> str:
        return f"{reservation_root(source.semantic_key)}/projection.json"

    def _record_projection(
        self, record, publication, key, snapshot, policy
    ) -> ActionResult:
        assert record.intent.source is not None
        marker = graduation_path(record.intent.source)
        path = self._projection_path(record.intent.source)
        stream = story_event_path(record.issue.number)
        bodies = self.repo.read_blobs(snapshot.tree, (marker, path, stream))
        if bodies[path] is not None:
            receipt = ProjectionRecord.model_validate_json(bodies[path])
            if (
                receipt.result.action == key
                and receipt.result.publication.issue == publication.issue
            ):
                return receipt.result
            raise GraduationConflict(
                "The local projection receipt belongs to another action."
            )
        result = ActionResult(
            publication=publication,
            action=key,
            status="completed",
            evidence=("The configured local backlog has no remote projection effect.",),
        )
        raw = ProjectionRecord(result=result).model_dump_json().encode()
        reads = tuple(
            ReadExpectation(
                path=key, digest=sha256(raw).hexdigest() if raw is not None else None
            )
            for key, raw in bodies.items()
        )
        operation = Operation(
            operation_id=uuid4().hex,
            owner=self.service.owner,
            category=OperationCategory.NORMAL,
            policy_digest=policy,
            intent=FinalizationIntent(
                kind="core.local.projection",
                version=1,
                related_preconditions=reads,
                payload=raw,
            ),
            change=RelatedWriteSet(
                read_set=reads, writes=(BlobWrite(path=path, content=raw),)
            ),
        )
        committed = self.service.commit(operation, snapshot).command
        expected = (
            PublicationOutcome.VERIFIED
            if record.intent.shared
            else PublicationOutcome.NOT_APPLICABLE
        )
        if (
            committed.local != LocalOutcome.COMPLETED
            or committed.publication != expected
        ):
            return ActionResult(publication=publication, action=key, status="pending")
        return result
