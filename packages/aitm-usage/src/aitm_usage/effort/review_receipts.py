"""Reconcile independent AIPR seals and native usage from verified evidence."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from ..types import SourceRef
from .receipts import Enrollment, Role, UsageReceipt, require_digest
from .store import EffortError, Snapshot


class Verdict(StrEnum):
    ACCEPTED = "reviewer-accepted"
    REVISIONS_REQUESTED = "reviewer-revisions-requested"


@dataclass(frozen=True, slots=True)
class ReviewIdentity:
    """Caller-verified participant and artifact for the enrolled review round."""

    enrollment: Enrollment
    reviewer: SourceRef
    artifact_sha256: str

    def __post_init__(self) -> None:
        if self.enrollment.role is not Role.REVIEWER or self.enrollment.review is None:
            raise EffortError("Expected an enrolled reviewer with a review round")
        if not isinstance(self.reviewer, SourceRef):
            raise EffortError("Expected an opaque verified reviewer reference")
        require_digest(self.artifact_sha256)


@dataclass(frozen=True, slots=True)
class ReviewAttempt:
    """An assigned review round and optional verified native observation ID."""

    identity: ReviewIdentity
    observation_id: str | None = None

    def __post_init__(self) -> None:
        if self.observation_id is not None:
            require_digest(self.observation_id)


@dataclass(frozen=True, slots=True)
class SealedDecision:
    """Evidence from authenticated AIPR readback.

    The caller verifies the event, artifact and response bytes against AIPR's
    existing authority and normalizes its participant and stable event refs.
    The portable reconciliation layer validates the binding to the attempt.
    """

    identity: ReviewIdentity
    verdict: Verdict
    response_sha256: str
    seal: SourceRef

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, Verdict) or not isinstance(
            self.seal, SourceRef
        ):
            raise EffortError("Expected an opaque AIPR seal and sealed verdict")
        require_digest(self.response_sha256)


@dataclass(frozen=True, slots=True)
class ReviewCompanion:
    attempt: ReviewAttempt
    decision: SealedDecision | None
    usage: UsageReceipt | None
    pending_usage_revisions: int


def reconcile_review_receipts(
    snapshot: Snapshot,
    attempts: Iterable[ReviewAttempt],
    decisions: Iterable[SealedDecision],
) -> tuple[ReviewCompanion, ...]:
    """Join effective usage and AIPR evidence by exact immutable identity.

    The caller establishes the review participant mapping and authenticates the
    native observation link. The fixed snapshot supplies usage lineage and
    attribution. Decisions and observations retain independent availability.
    Neither input grants authority to submit or alter an AIPR decision.
    """
    enrolled = {row.attempt_id: row for row in snapshot.enrollments}
    effective = {row.enrollment.attempt_id: row.receipt for row in snapshot.attributed}
    native_owners = {
        receipt.observation_id: attempt for attempt, receipt in effective.items()
    }
    pending = Counter(
        (receipt.attempt_id, receipt.observation_id) for receipt in snapshot.pending
    )
    selected: dict[UUID, ReviewAttempt] = {}
    for attempt in attempts:
        enrollment = attempt.identity.enrollment
        key = enrollment.attempt_id
        if (
            enrollment.project_id != snapshot.project_id
            or enrolled.get(key) != enrollment
        ):
            raise EffortError("Review attempt does not match the project enrollment")
        if selected.setdefault(key, attempt) != attempt:
            raise EffortError("Conflicting review attempt bindings")

        observation = attempt.observation_id
        if observation is not None:
            if native_owners.setdefault(observation, key) != key or (
                key in effective and effective[key].observation_id != observation
            ):
                raise EffortError(
                    "Review attempt does not match its native observation"
                )

    attached: dict[UUID, SealedDecision] = {}
    sealed_rounds = {}
    seals = {}
    for decision in decisions:
        enrollment = decision.identity.enrollment
        key = enrollment.attempt_id
        attempt = selected.get(key)
        if attempt is None or attempt.identity != decision.identity:
            raise EffortError("AIPR decision binding does not match the review attempt")
        if (
            attached.setdefault(key, decision) != decision
            or sealed_rounds.setdefault(enrollment.review, key) != key
            or seals.setdefault(decision.seal, key) != key
        ):
            raise EffortError("Review has conflicting sealed AIPR decisions")

    return tuple(
        ReviewCompanion(
            attempt,
            attached.get(key),
            effective.get(key) if attempt.observation_id is not None else None,
            pending[key, attempt.observation_id],
        )
        for key, attempt in sorted(selected.items())
    )
