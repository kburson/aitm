"""Typed attempt, execution and clock-boundary facts."""

from datetime import timedelta
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

Text = Annotated[str, Field(min_length=1)]
Positive = Annotated[int, Field(gt=0)]
Nonnegative = Annotated[int, Field(ge=0)]
ObjectId = Annotated[str, Field(pattern=r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")]
ClockMode = Literal["active", "expansion-paused", "review-stopped", "terminal-closed"]
ExecutionPhase = Literal[
    "prepared", "admitted", "started", "cancel-requested", "finished", "uncertain"
]
EvidenceOperation = Literal[
    "managed-verification",
    "review-observation",
    "delivery-observation",
    "proof-reconciliation",
    "signoff",
]


class BindingPurpose(StrEnum):
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    DELIVERABLE = "deliverable"
    EVIDENCE = "evidence"


class AttemptFact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class SourceSnapshot(AttemptFact):
    commit: ObjectId
    tree: ObjectId


class RecoveryAuthority(AttemptFact):
    purpose: Literal[BindingPurpose.EVIDENCE]
    authority_id: Text
    attempt: Text
    ended_generation: Positive
    source: SourceSnapshot
    allowed: Annotated[tuple[EvidenceOperation, ...], Field(min_length=1)]


class AttemptBoundary(AttemptFact):
    attempt: Text
    generation: Positive


class AttemptStarted(AttemptBoundary):
    plan_generation: Positive | None
    source: SourceSnapshot | None
    binding: Text | None
    allowance_millis: Positive
    provisional: bool = False


class AttemptClosed(AttemptBoundary):
    from_clock: ClockMode
    disposition: Literal[
        "unverified",
        "delivered",
        "abandoned",
        "superseded",
        "duplicate",
        "trip",
        "pivot",
    ]
    reason: Text


class AttemptReopened(AttemptBoundary):
    source: SourceSnapshot
    allowance_millis: Positive
    closure_reason: Text
    authority: RecoveryAuthority


class RecoveryBinding(AttemptBoundary):
    """Observed binding data supplied by the later binding owner."""

    purpose: Literal[BindingPurpose.EVIDENCE]
    authority_id: Text
    binding: Text
    source: SourceSnapshot
    needs_verification: bool


class ClockChanged(AttemptBoundary):
    cause_event_id: Text
    from_mode: ClockMode | None = Field(alias="from")
    to_mode: ClockMode = Field(alias="to")
    observed_at: AwareDatetime
    used_millis: Nonnegative

    @field_validator("observed_at")
    @classmethod
    def explicit_utc(cls, value: AwareDatetime) -> AwareDatetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError("clock observation requires UTC")
        return value


class ExecutionRecorded(AttemptBoundary):
    execution_id: Text
    request_id: Text
    action_key: Text
    executor: Text
    authority_store: Text
    authority_ref: Text
    expected_prior_version: ObjectId
    source: SourceSnapshot
    phase: ExecutionPhase
    recovery_authority_id: Text | None = None
    admission_commit: ObjectId | None = None
    outcome: Text | None = None
    proof: Text | None = None


class AttemptRecord(AttemptFact):
    """A retained attempt and its current generation, clock and execution facts."""

    started: AttemptStarted
    generation: Positive
    binding: Text | None
    allowance_millis: Positive
    used_millis: Nonnegative = 0
    clocks: tuple[ClockChanged, ...] = ()
    closures: tuple[AttemptClosed, ...] = ()
    closed: bool = False
    recovery: RecoveryAuthority | None = None
    recovery_bound: bool = False
    recovery_generations: dict[Positive, RecoveryAuthority] = Field(
        default_factory=dict
    )
    executions: dict[str, tuple[ExecutionRecorded, ...]] = Field(default_factory=dict)

    @property
    def clock_mode(self) -> ClockMode | None:
        return self.clocks[-1].to_mode if self.clocks else None


class AttemptState(AttemptFact):
    story_id: Positive
    current_attempt: str | None = None
    attempts: dict[str, AttemptRecord] = Field(default_factory=dict)
