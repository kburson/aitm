"""Provider-neutral backlog observations and identity authority contracts."""

from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, model_validator

from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.config import BacklogIssuer, Name, Oid
from aitm_core.models.events import DIGEST
from aitm_core.models.operations import FinalizationIntent, Positive


class _BacklogContract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, revalidate_instances="always"
    )
    version: Literal[1] = 1


class IssueRef(_BacklogContract):
    issuer: BacklogIssuer
    number: Positive


class BacklogObservation(_BacklogContract):
    issue: IssueRef
    status: Literal["present", "absent", "pending", "unsupported"]
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_observation(self) -> Self:
        if self.status in ("present", "absent") and not self.evidence:
            raise ValueError("a conclusive issue observation requires evidence")
        return self

    @property
    def is_present(self) -> bool | None:
        if self.status in ("pending", "unsupported"):
            return None
        return self.status == "present"


class GraduationIntent(_BacklogContract):
    operation_id: Name
    source_kind: Literal["draft", "plan-entry"]
    source_id: Name
    source_digest: DIGEST
    issuer: BacklogIssuer
    shared: bool


class IdentityReservation(_BacklogContract):
    """Bind an external correlation key to the frozen intent and issuer."""

    intent: GraduationIntent
    key: Name


class IdentityResult(_BacklogContract):
    """An external observation that has yet to finalize a Core story."""

    reservation: IdentityReservation
    status: Literal[
        "reserved", "issued", "uncertain", "absent-with-proof", "failed", "unsupported"
    ]
    issue: IssueRef | None = None
    absence_proof: Name | None = None
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_issuance(self) -> Self:
        if (self.status == "issued") != (self.issue is not None):
            raise ValueError("exactly the issued status requires an issue reference")
        if (
            self.issue is not None
            and self.issue.issuer != self.reservation.intent.issuer
        ):
            raise ValueError("the issued identity must match the reserved issuer")
        if (self.status == "absent-with-proof") != (self.absence_proof is not None):
            raise ValueError(
                "exactly the absent-with-proof status requires absence proof"
            )
        return self

    @property
    def pending_finalization(self) -> bool:
        return self.status == "issued"


class GraduationResult(_BacklogContract):
    """Expose a permanent local identity only after authoritative finalization."""

    intent: GraduationIntent
    command: CommandResult
    issue: IssueRef | None = None

    @model_validator(mode="after")
    def check_finalization(self) -> Self:
        if self.command.operation_id != self.intent.operation_id:
            raise ValueError("the command result must match the graduation operation")
        completed = self.command.local == LocalOutcome.COMPLETED
        publication = self.command.publication
        if (
            self.intent.shared
            and completed
            and publication == PublicationOutcome.NOT_APPLICABLE
        ):
            raise ValueError("shared graduation requires a publication outcome")
        authoritative_publication = (
            PublicationOutcome.VERIFIED
            if self.intent.shared
            else PublicationOutcome.NOT_APPLICABLE
        )
        finalized = completed and publication == authoritative_publication
        if finalized != (self.issue is not None):
            raise ValueError(
                "permanent local identity requires authoritative finalization"
            )
        if self.issue is not None and self.issue.issuer != self.intent.issuer:
            raise ValueError("the finalized identity must match the selected issuer")
        return self


class PublishedStory(_BacklogContract):
    issue: IssueRef
    planning_commit: Oid


class ActionKey(_BacklogContract):
    operation_id: Name
    action_id: Name


class ActionResult(_BacklogContract):
    publication: PublishedStory
    action: ActionKey
    status: Literal["completed", "pending", "failed", "unsupported"]
    evidence: tuple[Name, ...] = ()


class BacklogProvider(Protocol):
    name: str

    def observe_issue(self, issue: IssueRef) -> BacklogObservation: ...

    def prepare_identity(self, operation: GraduationIntent) -> IdentityReservation: ...

    def create_or_reconcile(self, reservation: IdentityReservation) -> IdentityResult:
        """Reconcile the same key after uncertainty and preserve any issued identity."""
        ...

    def project_latest(
        self, publication: PublishedStory, action: ActionKey
    ) -> ActionResult: ...

    def issue_url(self, ref: IssueRef) -> str: ...


class LocalGraduationAuthority(Protocol):
    def graduate(
        self, intent: GraduationIntent, finalization: FinalizationIntent
    ) -> GraduationResult: ...
