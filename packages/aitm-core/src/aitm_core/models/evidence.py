"""Typed evidence and provenance payloads for the installed Core event registry."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from aitm_core.models.attempts import (
    BindingPurpose,
    RecoveryBinding,
    SourceSnapshot,
)
from aitm_core.models.events import UTC_TIMESTAMP, EventActor
from aitm_core.models.lifecycle import (
    Commit,
    Digest,
    Positive,
    RepositoryPath,
    Text,
    WorkflowObservation,
)


def _utc(value: str) -> str:
    if not UTC_TIMESTAMP.fullmatch(value):
        raise ValueError("an explicit UTC timestamp is required")
    datetime.fromisoformat(value)
    return value


UtcText = Annotated[str, AfterValidator(_utc)]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Count = Annotated[int, Field(ge=0)]
Proofs = Annotated[tuple[Text, ...], Field(min_length=1)]
ReviewLevel = Literal["sar", "spr", "xpr"]
Result = Literal["pass", "fail", "unavailable", "uncertain"]


class EvidenceFact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class IdeaCreated(EvidenceFact):
    path: RepositoryPath
    tags: tuple[Text, ...] = ()


class DraftObserved(EvidenceFact):
    path: RepositoryPath
    reason: Text | None = None


class GuardEvaluated(EvidenceFact):
    operation: Text
    read_set_digest: Digest
    policy_digest: Digest
    workflow: WorkflowObservation
    slot: Text
    guard: Text
    guard_version: Text
    ok: bool
    code: Text
    reason: Text | None = None
    mode: Literal["enforce", "advisory"]


class ActionScope(EvidenceFact):
    origin_operation: Text
    owner: Text
    action_id: Text
    target_version: Positive
    owner_version: Text
    attempt: Text | None
    workflow: WorkflowObservation

    @property
    def key(self) -> tuple[str, str, str, int]:
        return self.origin_operation, self.owner, self.action_id, self.target_version


class ActionCompleted(ActionScope):
    outcome: Literal["completed"]
    proof_refs: Proofs


class ActionFailed(ActionScope):
    outcome: Literal["failed", "unavailable", "uncertain"]
    proof_refs: Proofs


class SessionStarted(EvidenceFact):
    session: Text
    generation: Positive
    attempt: Text | None
    purpose: Literal[
        BindingPurpose.PLANNING,
        BindingPurpose.IMPLEMENTATION,
        BindingPurpose.DELIVERABLE,
    ]
    binding: Text
    worktree: Text
    branch: Text | None
    head: Commit
    allowed_paths: tuple[RepositoryPath, ...]


class EvidenceSessionStarted(RecoveryBinding):
    session: Text
    worktree: Text
    branch: Text | None
    allowed_paths: tuple[RepositoryPath, ...]


class SessionEnded(EvidenceFact):
    session: Text
    generation: Positive
    attempt: Text | None
    binding: Text
    reason: Text


class AttemptObservation(EvidenceFact):
    attempt: Text
    generation: Positive


class ExpansionReserved(AttemptObservation):
    reservation: Text
    intent: Text
    holder: Text
    dependency: Positive | None = None


class ExpansionReservationResolved(AttemptObservation):
    reservation: Text
    disposition: Literal["linked", "no-child"]
    child: Positive | None = None
    proof_refs: Proofs


class ExpansionCustody(AttemptObservation):
    reservation: Text
    semantic_key: Digest
    disposition: Literal["sender-fenced", "issued", "no-child"]
    authority: Literal["local-allocation", "protocol-no-send", "provider-claim"]
    verified_at: Commit
    claim: Text | None = None
    issue: Positive | None = None
    fence: Text | None = None
    absence: Text | None = None
    proof_refs: Proofs

    @model_validator(mode="after")
    def exact_proof_shape(self) -> Self:
        if self.authority != "provider-claim":
            valid = self.disposition == "no-child" and all(
                field is None
                for field in (self.claim, self.issue, self.fence, self.absence)
            )
        elif self.claim is None:
            valid = False
        elif self.disposition == "issued":
            valid = (
                self.issue is not None and self.fence is None and self.absence is None
            )
        elif self.disposition == "sender-fenced":
            valid = (
                self.issue is None and self.fence is not None and self.absence is None
            )
        else:
            valid = (
                self.issue is None
                and self.fence is not None
                and self.absence is not None
            )
        proof = {
            "local-allocation": f"local-allocation-fenced:{self.verified_at}",
            "protocol-no-send": f"protocol-no-send:{self.verified_at}",
            "provider-claim": {
                "sender-fenced": f"provider-fence:{self.fence}",
                "issued": f"issued-ownership:{self.verified_at}",
                "no-child": f"ordered-provider-observation:{self.verified_at}",
            }[self.disposition],
        }[self.authority]
        if not valid or self.proof_refs != (proof,):
            raise ValueError("The custody disposition and authority proof disagree.")
        return self


class ExpansionRecorded(AttemptObservation):
    reservation: Text
    child: Positive
    kind: Literal["defect", "story"]
    reason: Text


class ExpansionResolved(AttemptObservation):
    child: Positive
    disposition: Text
    dependency: Positive
    proof_refs: Proofs


class TripRecorded(AttemptObservation):
    cause: Literal["second-expansion", "nested-expansion", "time-limit"]
    child_attempt: Text | None = None
    observed_hours: Nonnegative | None = None
    coverage: Text
    detected_at: UtcText
    proof_refs: Proofs


class TripDecided(AttemptObservation):
    decision: Literal["scrap", "refactor"]
    rationale: Text
    analysis_path: RepositoryPath
    expansion_disposition: Text | None = None


class PivotRecorded(EvidenceFact):
    by: EventActor
    reason: Text
    scope_change: Text


class SourceObservation(AttemptObservation):
    source: SourceSnapshot


class TestReceipt(SourceObservation):
    receipt_id: Text
    source_ref: Text
    clean_input: bool
    command: Annotated[tuple[Text, ...], Field(min_length=1)]
    policy_digest: Digest
    lane: Text
    assurance: Text
    started_at: UtcText | None
    ended_at: UtcText | None
    result: Result
    output_digest: Digest | None


class ReviewRecorded(SourceObservation):
    review_id: Text
    verdict: Literal["pass", "changes"]
    reviewer_ref: Text
    proof_refs: Proofs


class ReviewActivated(SourceObservation):
    review_id: Text
    policy_digest: Digest
    proof_refs: Proofs
    reason: Text


class ReviewInvalidated(ReviewActivated):
    resumes_execution: bool


class DocumentReviewFact(EvidenceFact):
    record_id: Text
    level: ReviewLevel
    path: RepositoryPath


class DocumentReviewOpened(DocumentReviewFact):
    raw_digest: Digest
    content_digest: Digest
    opened_at: UtcText
    opened_by: EventActor
    source_operation: Text


class ReviewParticipant(EvidenceFact):
    host: Text
    provider: Text
    model_id: Text
    effort: Text | None
    session_id: Text | None
    session_id_kind: Literal["native", "adapter", "unknown"]


class DocumentReviewTurn(DocumentReviewFact):
    round: Positive
    role: Literal["reviewer", "author"]
    agent: ReviewParticipant
    started_at: UtcText | None
    submitted_at: UtcText
    start_basis: Literal["recorded", "claim", "prior-submit", "unknown"]
    start_ref: Text | None = None
    input_digest: Digest | None = None
    output_digest: Digest | None = None
    patch_path: RepositoryPath | None = None
    response_path: RepositoryPath
    source_digest: Digest
    finding_ids: tuple[Text, ...]
    decision: Literal["pass", "changes", "round-cap"] | None = None


class DocumentReviewCompleted(DocumentReviewFact):
    rounds: Positive
    outcome: Literal["exhausted", "round-cap"]
    base_digest: Digest
    final_digest: Digest
    started_at: UtcText | None
    start_basis: Literal["recorded", "claim", "prior-submit", "unknown"] = "unknown"
    ended_at: UtcText
    manifest_path: RepositoryPath


class DeliverableValidated(AttemptObservation):
    deliverable_id: Text
    deliverable_digest: Digest
    input_baseline: Commit
    check_policy: Digest
    result: Result
    proof_refs: Proofs


class DeliveryVerified(AttemptObservation):
    source: SourceSnapshot | None
    deliverable_digest: Digest | None
    target: Text
    result_ref: Text
    result_digest: Digest
    method: Text
    proof_refs: Proofs


class OutcomeRecorded(EvidenceFact):
    phase: Literal["refine", "plan", "close"]
    workflow: WorkflowObservation
    disposition: Text
    actual_agent_hours: Nonnegative | None
    qualification: Literal["observed", "estimated", "partial", "unknown"]
    lessons: tuple[Text, ...] = ()
    proof_refs: tuple[Text, ...]


class UsageRecorded(EvidenceFact):
    producer: Text
    receipt_id: Text
    unit: Text
    quantity: Count | Nonnegative | None
    availability: Literal["observed", "estimated", "unknown"]
    proof_refs: tuple[Text, ...]


class ActivityRecorded(EvidenceFact):
    producer: Text
    session: Text | None
    attempt: Text | None
    observed_at: UtcText
    ended_at: UtcText | None
    recorded_at: UtcText | None
    coverage: Text
    freshness: Text
