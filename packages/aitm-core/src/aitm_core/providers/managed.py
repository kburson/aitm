"""Versioned managed Git host port and evidence-bound capability selection."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aitm_core.config import PolicySnapshot
from aitm_core.models.common import RefObservation
from aitm_core.models.config import Name, Oid
from aitm_core.models.operations import Positive
from aitm_core.providers.githost import GitHostProvider, RemoteRef, _check_observed_ref

if TYPE_CHECKING:
    from aitm_core.ext.registry import Registry

type Evidence = Annotated[tuple[Name, ...], Field(min_length=1)]


class ManagedOperation(StrEnum):
    PROVISION = "provision"
    OBSERVE = "observe"
    READINESS = "readiness"
    DELIVER = "deliver"
    RETIRE = "retire"


class _ManagedContract(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, revalidate_instances="always"
    )
    schema_version: Literal[1] = 1


class ManagedRequest(_ManagedContract):
    operation: ManagedOperation = Field(strict=False)
    provider: Name
    capability_version: Positive
    operation_id: Name
    story: Positive
    role: Name
    incarnation: Name
    source: RemoteRef
    target: RemoteRef
    source_head: Oid
    target_base: Oid
    pull_request: Name | None = None
    draft: bool | None = None

    @model_validator(mode="after")
    def check_scope(self) -> Self:
        if (
            self.source.repository != self.target.repository
            or self.source.ref == self.target.ref
        ):
            raise ValueError(
                "managed source and target require distinct refs in one repository"
            )
        if (
            self.operation is ManagedOperation.PROVISION
            and self.pull_request is not None
        ):
            raise ValueError(
                "provisioning takes a new PR identity from verified readback"
            )
        if (
            self.operation
            in (
                ManagedOperation.READINESS,
                ManagedOperation.DELIVER,
                ManagedOperation.RETIRE,
            )
            and self.pull_request is None
        ):
            raise ValueError("managed operation requires the exact pull request")
        if (self.operation is ManagedOperation.READINESS) != (self.draft is not None):
            raise ValueError("only readiness requests specify the desired draft flag")
        return self


class ManagedQualification(_ManagedContract):
    provider: Name
    repository: Name
    operation: ManagedOperation = Field(strict=False)
    version: Positive
    evidence: Evidence


class ManagedReceipt(_ManagedContract):
    request: ManagedRequest
    source: RefObservation
    target: RefObservation
    pull_request: Name | None = None
    draft: bool | None = None
    protected: bool | None = None
    landed_commit: Oid | None = None
    evidence: Evidence

    @model_validator(mode="after")
    def check_readback(self) -> Self:
        request = self.request
        _check_observed_ref(request.source, self.source)
        _check_observed_ref(request.target, self.target)
        if (
            request.pull_request is not None
            and self.pull_request != request.pull_request
        ):
            raise ValueError("readback belongs to a different pull request")

        operation = request.operation
        if operation is ManagedOperation.RETIRE:
            if self.source.observed_commit is not None:
                raise ValueError("retirement requires positive source-ref absence")
        elif self.source.observed_commit != request.source_head:
            raise ValueError("source readback differs from the exact requested head")

        if operation is ManagedOperation.DELIVER:
            if (
                self.landed_commit is None
                or self.landed_commit != self.target.observed_commit
            ):
                raise ValueError("delivery requires the exact landed target commit")
        elif (
            self.landed_commit is not None
            or self.target.observed_commit != request.target_base
        ):
            raise ValueError("target readback differs from the exact requested base")

        if operation is ManagedOperation.PROVISION and (
            self.pull_request is None
            or self.draft is not True
            or self.protected is not True
        ):
            raise ValueError(
                "provisioning requires the draft PR and protected-source readback"
            )
        if operation is ManagedOperation.READINESS and self.draft != request.draft:
            raise ValueError("readiness requires the requested draft flag readback")
        return self


class ManagedResult(_ManagedContract):
    request: ManagedRequest
    status: Literal["verified", "pending", "unsupported", "refused"]
    receipt: ManagedReceipt | None = None
    reason: Name | None = None
    evidence: tuple[Name, ...] = ()

    @model_validator(mode="after")
    def check_outcome(self) -> Self:
        if self.status == "verified":
            if self.receipt is None or self.receipt.request != self.request:
                raise ValueError(
                    "verified outcome requires a receipt for the exact request"
                )
        elif self.receipt is not None or self.reason is None:
            raise ValueError(
                "unverified outcome requires a reason and carries no verified receipt"
            )
        return self


class ManagedGitHostProvider(GitHostProvider, Protocol):
    def perform_managed(
        self, request: ManagedRequest, qualification: ManagedQualification
    ) -> ManagedResult: ...


class ManagedProviderRegistration(_ManagedContract):
    factory: Callable[[], ManagedGitHostProvider]
    capabilities: Annotated[
        tuple[tuple[ManagedOperation, Positive], ...], Field(min_length=1)
    ]

    @model_validator(mode="after")
    def check_capabilities(self) -> Self:
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("duplicate managed capability and version")
        return self


@dataclass(frozen=True, slots=True)
class ManagedAvailability:
    status: Literal["available", "unavailable"]
    reason: str | None = None
    factory: Callable[[], ManagedGitHostProvider] | None = None
    qualification: ManagedQualification | None = None


def resolve_managed(
    policy: PolicySnapshot,
    registry: "Registry",
    request: ManagedRequest,
    qualification: ManagedQualification | None,
) -> ManagedAvailability:
    """Select a qualified declared port without instantiating the provider."""
    if (
        request.provider == "none"
        or policy.config.providers.githost != request.provider
    ):
        return ManagedAvailability("unavailable", reason="Git host is not selected")
    if request.target.repository != policy.routing.code_repository:
        return ManagedAvailability(
            "unavailable", reason="repository differs from the routing anchor"
        )
    if policy.writes_fenced and request.operation is not ManagedOperation.OBSERVE:
        return ManagedAvailability(
            "unavailable", reason="managed mutation is blocked by the routing fence"
        )
    declared = registry.extension_status(request.provider)
    manifest = declared.registration
    if manifest is None:
        return ManagedAvailability("unavailable", reason=declared.reason)
    if request.provider not in policy.config.extensions.enabled:
        return ManagedAvailability(
            "unavailable", reason="Git host is disabled by committed policy"
        )
    port = manifest.managed_provider
    if port is None:
        return ManagedAvailability(
            "unavailable", reason="managed Git host is unsupported"
        )
    if (request.operation, request.capability_version) not in port.capabilities:
        return ManagedAvailability(
            "unavailable", reason="managed capability version is unsupported"
        )
    if qualification is None or (
        qualification.provider,
        qualification.repository,
        qualification.operation,
        qualification.version,
    ) != (
        request.provider,
        request.target.repository,
        request.operation,
        request.capability_version,
    ):
        return ManagedAvailability(
            "unavailable", reason="exact scope requires a matching qualification"
        )
    return ManagedAvailability(
        "available", factory=port.factory, qualification=qualification
    )
