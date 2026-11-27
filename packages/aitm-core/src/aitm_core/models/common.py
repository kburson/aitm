"""Result, store identity, and ref observation contracts shared by Core commands."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LocalOutcome(StrEnum):
    COMPLETED = "completed"
    REFUSED = "refused"
    CONFLICT = "conflict"
    INTEGRITY_ERROR = "integrity-error"
    UNAVAILABLE = "unavailable"


class PublicationOutcome(StrEnum):
    NOT_APPLICABLE = "not-applicable"
    VERIFIED = "verified"
    PENDING = "pending"


class CommandResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, validate_by_name=True, serialize_by_alias=True
    )

    schema_version: Literal["aitm.command-result/v1"] = Field(
        default="aitm.command-result/v1", alias="schema"
    )
    operation_id: str
    local: LocalOutcome
    publication: PublicationOutcome = PublicationOutcome.NOT_APPLICABLE
    pending: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    recovery: str | None = None

    @property
    def exit_code(self) -> int:
        if self.local == LocalOutcome.COMPLETED:
            return 4 if self.publication == PublicationOutcome.PENDING else 0
        return {
            LocalOutcome.REFUSED: 1,
            LocalOutcome.CONFLICT: 2,
            LocalOutcome.INTEGRITY_ERROR: 3,
            LocalOutcome.UNAVAILABLE: 5,
        }[self.local]


class StoreAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    store_uuid: str
    code_default_ref: str
    planning_ref: str
    planning_remote: str | None
    root_commit: str


class RefObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    ref: str
    observed_commit: str | None
    remote: str | None = None


class RefreshResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    local: RefObservation
    candidate: RefObservation | None = None
    recovery_ref: str | None = None
