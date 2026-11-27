"""Versioned Git host contracts for remote observations and evidence."""

from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.common import RefObservation
from aitm_core.models.config import Name, Oid
from aitm_core.models.events import DIGEST
from aitm_core.store.gate import RefIdentity


class _HostContract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, revalidate_instances="always"
    )
    version: Literal[1] = 1


class RemoteRef(_HostContract):
    """Permanent repository and ref coordinates with an optional transport name."""

    repository: Name
    ref: RefIdentity
    remote: Name | None = None


_commit_id = TypeAdapter(Oid)


def _check_observed_ref(target: RemoteRef, observation: RefObservation) -> None:
    if observation.ref != target.ref.name:
        raise ValueError("observation does not match the requested ref")
    if observation.remote != (target.remote or target.repository):
        raise ValueError("observation does not match the requested remote")
    if observation.observed_commit is not None:
        _commit_id.validate_python(observation.observed_commit)


class FetchResult(_HostContract):
    target: RemoteRef
    status: Literal["observed", "pending", "unsupported"]
    observation: RefObservation | None = None
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_candidate(self) -> Self:
        if (self.status == "observed") != (self.observation is not None):
            raise ValueError("exactly the observed status requires a ref observation")
        if self.observation is not None:
            _check_observed_ref(self.target, self.observation)
            if self.observation.observed_commit is None and not self.evidence:
                raise ValueError("an observed absent ref requires evidence")
        return self


class PublicationIntent(_HostContract):
    operation_id: Name
    target: RemoteRef
    candidate: Oid


class PublicationResult(_HostContract):
    """Bind observed remote history and containment to the exact operation."""

    intent: PublicationIntent
    status: Literal["verified", "pending", "unsupported"]
    observed: RefObservation | None = None
    contained_operation_id: Name | None = None
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_publication(self) -> Self:
        if self.observed is not None:
            _check_observed_ref(self.intent.target, self.observed)
        if self.status == "verified":
            if (
                self.observed is None
                or self.observed.observed_commit != self.intent.candidate
            ):
                raise ValueError(
                    "verified publication requires the exact candidate tip"
                )
            if (
                self.contained_operation_id != self.intent.operation_id
                or not self.evidence
            ):
                raise ValueError(
                    "verified publication requires a remote containment witness"
                )
        elif self.contained_operation_id is not None:
            raise ValueError("a containment claim requires verified publication")
        return self


class _SourceObservationRequest(_HostContract):
    attempt: Name
    source: SourceSnapshot
    target: RemoteRef
    target_commit: Oid
    policy_digest: DIGEST


class DeliveryRequest(_SourceObservationRequest):
    """The exact source, destination and policy of a delivery observation."""


class ReviewRequest(_SourceObservationRequest):
    """The exact source, destination and policy of a review observation."""


class _SourceObservationResult[Request: _SourceObservationRequest](_HostContract):
    request: Request
    status: Literal["verified", "pending", "rejected", "unsupported"]
    evidence: tuple[Name, ...] = Field(min_length=1)


class DeliveryResult(_SourceObservationResult[DeliveryRequest]):
    """A remote delivery observation bound to its request."""


class ReviewResult(_SourceObservationResult[ReviewRequest]):
    """A remote review observation bound to its request."""


class ProtectionRules(_HostContract):
    allow_deletion: bool = False
    allow_force_push: bool = False
    require_linear_history: bool = True
    require_pull_request: bool = False
    bypass_actors: tuple[Name, ...] = ()


class ProtectResult(_HostContract):
    target: RemoteRef
    rules: ProtectionRules
    status: Literal["applied", "already-protected", "manual", "pending", "unsupported"]
    instructions: tuple[Name, ...] = ()
    settings_url: Name | None = None
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_protection(self) -> Self:
        if self.status == "manual" and not self.instructions:
            raise ValueError("manual protection requires instructions")
        if self.status in ("applied", "already-protected") and not self.evidence:
            raise ValueError("an asserted protection state requires evidence")
        return self


class GitHostProvider(Protocol):
    name: str

    def fetch_candidate(self, ref: RemoteRef) -> FetchResult: ...

    def publish(self, intent: PublicationIntent) -> PublicationResult: ...

    def observe_delivery(self, request: DeliveryRequest) -> DeliveryResult: ...

    def observe_review(self, request: ReviewRequest) -> ReviewResult: ...

    def file_url(self, ref: RemoteRef, path: str) -> str: ...

    def commit_url(self, repository: str, sha: Oid) -> str: ...

    def default_branch(self, repository: str) -> RemoteRef: ...

    def protect_branch(
        self, branch: RemoteRef, rules: ProtectionRules
    ) -> ProtectResult: ...
