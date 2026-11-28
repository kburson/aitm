"""Join current local verification with an authenticated hosted observation."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Literal

from aitm_core.events import core_reducers, fold
from aitm_core.machine.guards import GuardCall, GuardDecision
from aitm_core.models.attempts import ExecutionCandidate, SourceSnapshot
from aitm_core.models.operations import ReadExpectation, story_event_path
from aitm_core.rules.trips import current_attempt, expansion_child

type Observation = Literal["passed", "failed", "pending"]


@dataclass(frozen=True, slots=True)
class HostedCandidate:
    repository: str
    pull_request: int
    target: str
    base: str
    source: SourceSnapshot
    tested: SourceSnapshot


@dataclass(frozen=True, slots=True)
class VerificationBasis:
    story: int
    attempt: str
    generation: int
    candidate: ExecutionCandidate
    policy: str
    source_proof: Literal["story-tagged", "composed"] | None
    expansion_resolved: bool
    hosted: HostedCandidate | None = None


@dataclass(frozen=True, slots=True)
class LocalCandidateProof:
    story: int
    attempt: str
    generation: int
    candidate: ExecutionCandidate
    policy: str
    outcome: Observation


type LocalVerificationPort = Callable[[VerificationBasis], LocalCandidateProof | None]
type AuthenticatedHostedPort = Callable[
    [HostedCandidate], tuple[HostedCandidate, Observation] | None
]


def candidate_guard(
    current: VerificationBasis,
    local: LocalVerificationPort | None,
    hosted: AuthenticatedHostedPort | None,
) -> GuardDecision:
    """Require exact proof before pre-Review or final closeout."""
    if current.source_proof not in ("story-tagged", "composed"):
        return GuardDecision("blocked", "candidate-source-proof-missing")
    if not current.expansion_resolved:
        return GuardDecision("blocked", "candidate-expansion-unresolved")
    if current.candidate.capture_manifest is None:
        return GuardDecision("blocked", "candidate-capture-unavailable")
    receipt = local(current) if local is not None else None
    if receipt is None or receipt.outcome == "pending":
        return GuardDecision("unavailable", "local-verification-pending")
    expected = LocalCandidateProof(
        current.story,
        current.attempt,
        current.generation,
        current.candidate,
        current.policy,
        "passed",
    )
    if receipt != expected:
        return GuardDecision("blocked", "local-verification-failed-or-stale")

    target = current.hosted
    if target is None or hosted is None:
        return GuardDecision("unavailable", "hosted-verification-unavailable")
    if target.source != current.candidate.source:
        return GuardDecision("blocked", "hosted-candidate-stale")
    check = hosted(target)
    if check is None or check[1] == "pending":
        return GuardDecision("unavailable", "hosted-verification-pending")
    if check != (target, "passed"):
        return GuardDecision("blocked", "hosted-verification-failed-or-stale")
    return GuardDecision("pass", "exact-candidate-verification-current")


@dataclass(frozen=True, slots=True)
class CandidateVerification:
    """Compose qualified source, local execution, and hosted evidence readers."""

    basis: Callable[[GuardCall], VerificationBasis | None]
    local: LocalVerificationPort
    hosted: AuthenticatedHostedPort

    def __call__(self, call: GuardCall) -> GuardDecision:
        path = story_event_path(call.story.story_id)
        raw = call.blobs.get(path)
        if raw is None:
            return GuardDecision("unavailable", "candidate-attempt-unavailable")
        state = fold(raw.splitlines(keepends=True), core_reducers())
        active = current_attempt(state)
        current = self.basis(call)
        if active is None or active.closed or current is None:
            return GuardDecision("unavailable", "candidate-attempt-unavailable")
        if (
            current.story != state.story_id
            or current.attempt != active.started.attempt
            or current.generation != active.generation
            or current.policy != call.policy_digest
            or expansion_child(state, current.attempt) is not None
        ):
            return GuardDecision("blocked", "candidate-attempt-or-expansion-stale")
        decision = candidate_guard(current, self.local, self.hosted)
        if decision.status != "pass":
            return decision
        read = ReadExpectation(path=path, digest=sha256(raw).hexdigest())
        return replace(decision, reads=(*decision.reads, read))
