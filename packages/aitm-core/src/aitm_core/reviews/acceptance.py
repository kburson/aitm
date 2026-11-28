"""Evaluate current authored content and append qualified acceptance through C09."""

from dataclasses import dataclass, replace
from hashlib import sha256
from json import dumps
from pathlib import PurePosixPath
from typing import Literal, Protocol
from urllib.parse import urlencode

from pydantic import ValidationError

from aitm_core.documents import _parse, canonicalize
from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.models.binding import StoryRef, allows_authored
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.config import ReviewPolicy
from aitm_core.models.documents import ContentIdentity, DocumentSchema
from aitm_core.models.events import EventEnvelope, validate_envelope
from aitm_core.models.evidence import ReviewLevel
from aitm_core.models.lifecycle import (
    DocumentAcceptance,
    DocumentRole,
    Graduation,
    LifecycleState,
)
from aitm_core.models.operations import (
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    ReadExpectation,
    RelatedWriteSet,
    repository_path,
    story_event_path,
)
from aitm_core.reducers.evidence import DocumentReview
from aitm_core.reviews.policy import ValidatedReview
from aitm_core.reviews.turns import ReviewContext, _reviews
from aitm_core.services import UnavailablePort
from aitm_core.store.backend import OperationResult


@dataclass(frozen=True, slots=True)
class DocumentInput:
    story: int
    path: str
    role: DocumentRole
    raw: bytes


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    record_id: str
    review: ValidatedReview


@dataclass(frozen=True, slots=True)
class AcceptanceResult:
    outcome: LocalOutcome
    canonical_digest: str | None = None
    required_levels: tuple[ReviewLevel, ...] = ()
    missing_levels: tuple[ReviewLevel, ...] = ()
    review_refs: tuple[str, ...] = ()
    reason: str | None = None

    @property
    def accepted(self) -> bool:
        return self.outcome is LocalOutcome.COMPLETED


@dataclass(frozen=True, slots=True)
class ApplicabilityResult:
    """The C72 decision and exact reads that substantiate it."""

    status: Literal["current", "stale", "unavailable"]
    reads: tuple[ReadExpectation, ...] = ()
    reason: str | None = None


class PlanEntryApplicability(Protocol):
    def __call__(
        self, context: ReviewContext, graduation: Graduation, document: DocumentInput
    ) -> ApplicabilityResult: ...


def _content(doc: DocumentInput) -> ContentIdentity:
    path = PurePosixPath(repository_path(doc.path))
    if (
        doc.role not in ("design", "plan")
        or len(path.parts) < 6
        or path.parts[4] != doc.role
        or not allows_authored(StoryRef(story=doc.story), doc.path)
    ):
        raise ValueError("acceptance requires an authored design or plan of this story")
    header = _parse(doc.raw).header
    if (header.get("story"), header.get("role")) != (doc.story, doc.role):
        raise ValueError(
            "authored document identity disagrees with the acceptance target"
        )
    return canonicalize(doc.raw, DocumentSchema())


def _matches(doc: DocumentInput, item: ReviewRecord, digest: str) -> bool:
    review = item.review
    record = review.record
    manifest = record.manifest
    if (
        (manifest.story, manifest.artifact_path) != (doc.story, doc.path)
        or manifest.level != review.level
        or manifest.outcome != "exhausted"
    ):
        return False
    try:
        reviewed = _content(replace(doc, raw=record.final_bytes))
    except ValueError:
        return False
    return reviewed.canonical_sha256 == digest


def evaluate_acceptance(
    doc: DocumentInput, policy: ReviewPolicy, records: tuple[ReviewRecord, ...]
) -> AcceptanceResult:
    """Find qualified proof for every explicit level on the same current content."""
    try:
        digest = _content(doc).canonical_sha256
    except ValueError as error:
        return AcceptanceResult(LocalOutcome.INTEGRITY_ERROR, reason=str(error))
    try:
        policy = ReviewPolicy.model_validate(policy.model_dump(by_alias=True))
    except (AttributeError, ValidationError):
        return AcceptanceResult(
            LocalOutcome.UNAVAILABLE,
            digest,
            reason="unsupported document review policy",
        )
    levels = policy.documents.design if doc.role == "design" else policy.documents.plan
    if not levels or len(set(levels)) != len(levels):
        return AcceptanceResult(
            LocalOutcome.UNAVAILABLE,
            digest,
            reason="explicit unique review levels are required",
        )

    retained: dict[str, ReviewRecord] = {}
    for item in records:
        if not item.record_id.strip() or (
            item.record_id in retained and retained[item.record_id] != item
        ):
            return AcceptanceResult(
                LocalOutcome.INTEGRITY_ERROR,
                digest,
                levels,
                reason="review record identity is empty or conflicting",
            )
        retained[item.record_id] = item

    matching: dict[ReviewLevel, list[str]] = {level: [] for level in levels}
    for identity, item in sorted(retained.items()):
        if (
            item.review.level in matching
            and item.review.assurance in policy.documents.assurances
            and _matches(doc, item, digest)
        ):
            matching[item.review.level].append(identity)
    refs = tuple(identity for group in matching.values() for identity in group)
    missing = tuple(level for level, group in matching.items() if not group)
    reason = (
        f"missing review levels for {digest}: {', '.join(missing)}" if missing else None
    )
    # The committed schema identifies exception authority. It supplies no grant,
    # so ordinary exact-content obligations apply even when exceptions are enabled.
    return AcceptanceResult(
        LocalOutcome.REFUSED if missing else LocalOutcome.COMPLETED,
        digest,
        levels,
        missing,
        refs,
        reason,
    )


def _finish(
    context: ReviewContext,
    outcome: LocalOutcome,
    reason: str | None = None,
) -> OperationResult:
    return OperationResult(
        CommandResult(
            operation_id=context.operation_id,
            local=outcome,
            evidence=(reason,) if reason else (),
        ),
        context.snapshot,
        reason,
    )


def _applicability(
    context: ReviewContext,
    graduation: Graduation,
    doc: DocumentInput,
    applicability: PlanEntryApplicability | None,
) -> ApplicabilityResult:
    if graduation.source_kind == "draft":
        return ApplicabilityResult("current")
    if applicability is None:
        return ApplicabilityResult(
            "unavailable", reason="plan-entry applicability is unavailable"
        )
    decision = applicability(context, graduation, doc)
    if not isinstance(decision, ApplicabilityResult) or (
        decision.status == "current" and not decision.reads
    ):
        return ApplicabilityResult(
            "unavailable", reason="plan-entry applicability lacks pinned proof"
        )
    return decision


def _proofs(
    doc: DocumentInput,
    completed: dict[str, DocumentReview],
    evaluation: AcceptanceResult,
    records: tuple[ReviewRecord, ...],
) -> tuple[tuple[str, ...], dict[str, bytes]]:
    by_id = {item.record_id: item.review for item in records}
    capsule = PurePosixPath(story_event_path(doc.story)).parent / "evidence" / "reviews"
    manifests = []
    originals: dict[str, bytes] = {}
    for identity in evaluation.review_refs:
        entry = completed.get(identity)
        completion = entry.completion if entry is not None else None
        review = by_id[identity]
        if completion is None or (
            completion.level,
            completion.path,
            completion.outcome,
            completion.final_digest,
            completion.base_digest,
            completion.rounds,
        ) != (
            review.level,
            doc.path,
            "exhausted",
            evaluation.canonical_digest,
            canonicalize(review.record.base_bytes, DocumentSchema()).canonical_sha256,
            review.record.manifest.rounds,
        ):
            raise ValueError("acceptance requires matching retained review completion")
        assert entry is not None
        if PurePosixPath(identity).parts != (identity,):
            raise ValueError("invalid review capsule identity")
        manifest = repository_path(f"{capsule}/{identity}/review-manifest.md")
        if manifest != completion.manifest_path:
            raise ValueError("review completion manifest is outside its capsule")
        manifests.append(manifest)
        for original in review.record.originals:
            name = repository_path(original.name)
            path = f"{PurePosixPath(manifest).parent}/{name}"
            if path in originals:
                raise ValueError("acceptance review originals overlap")
            originals[path] = original.raw
        if manifest not in originals:
            raise ValueError("acceptance review lacks its original manifest")
        for turn in entry.turns.values():
            response = originals.get(turn.response_path)
            if response is None or sha256(response).hexdigest() != turn.source_digest:
                raise ValueError(
                    "review response disagrees with retained turn provenance"
                )
    return tuple(manifests), originals


def _generation(
    role: DocumentRole,
    path: str,
    digest: str,
    lifecycle: LifecycleState,
    raw_log: bytes,
) -> int:
    plan = lifecycle.accepted_documents.get("plan")
    if role == "design":
        return plan.plan_generation if plan is not None else 1
    if plan is not None and (plan.path, plan.canonical_digest) == (path, digest):
        return plan.plan_generation
    # A kind split clears effective acceptance but retains earlier generations.
    generations = (
        event.data["plan_generation"]
        for line in raw_log.splitlines(keepends=True)
        if (event := validate_envelope(line)).type == "core.doc.accepted"
        and event.data["role"] == "plan"
    )
    return max(generations, default=0) + 1


def accept_document(
    role: DocumentRole,
    records: tuple[ReviewRecord, ...],
    expected_doc: DocumentInput,
    policy: ReviewPolicy,
    *,
    context: ReviewContext,
    proof_paths: tuple[str, ...],
    applicability: PlanEntryApplicability | None = None,
    identity_mapping: bytes | None = None,
    legacy_session_namespace: str | None = None,
) -> OperationResult:
    """Persist one acceptance fact without modifying authored content or evidence."""
    doc = expected_doc
    if role != doc.role:
        return _finish(
            context,
            LocalOutcome.INTEGRITY_ERROR,
            "acceptance role differs from document",
        )
    evaluation = evaluate_acceptance(doc, policy, records)
    if not evaluation.accepted:
        return _finish(context, evaluation.outcome, evaluation.reason)
    event_path = story_event_path(doc.story)
    try:
        base = context.backend.read(context.snapshot, (event_path, doc.path))
        if base[doc.path] != doc.raw:
            return _finish(context, LocalOutcome.CONFLICT, "authored document changed")
        raw_log = base[event_path]
        if raw_log is None:
            return _finish(
                context, LocalOutcome.UNAVAILABLE, "story event stream is unavailable"
            )
        state = fold(raw_log.splitlines(keepends=True), core_reducers())
        lifecycle = state.domains.get("lifecycle")
        if state.story_id != doc.story or not isinstance(lifecycle, LifecycleState):
            raise ValueError("acceptance requires an initialized story")
        applicability_result = _applicability(
            context, lifecycle.graduation, doc, applicability
        )
        if applicability_result.status != "current":
            outcome = (
                LocalOutcome.REFUSED
                if applicability_result.status == "stale"
                else LocalOutcome.UNAVAILABLE
            )
            return _finish(
                context,
                outcome,
                applicability_result.reason
                or "plan-entry applicability is not current",
            )
        review_refs, originals = _proofs(doc, _reviews(state), evaluation, records)
        mapping_path = None
        payload = {}
        if identity_mapping is not None:
            mapping_digest = sha256(identity_mapping).hexdigest()
            story_root = PurePosixPath(event_path).parent
            mapping_path = (
                f"{story_root}/evidence/review-identities/{mapping_digest}.json"
            )
            mapping_ref = mapping_path
            payload["identity_mapping"] = {
                "path": mapping_path,
                "sha256": mapping_digest,
            }
            if legacy_session_namespace is not None:
                metadata = {"legacy_session_namespace": legacy_session_namespace}
                mapping_ref = f"{mapping_path}#{urlencode(metadata)}"
                payload["identity_mapping"].update(metadata)
            review_refs = (*review_refs, mapping_ref)
        elif legacy_session_namespace is not None:
            raise ValueError(
                "legacy session namespace requires retained identity mapping"
            )
        paths = tuple(
            dict.fromkeys(
                (
                    event_path,
                    doc.path,
                    *map(repository_path, proof_paths),
                    *originals,
                    *((mapping_path,) if mapping_path else ()),
                    *(read.path for read in applicability_result.reads),
                )
            )
        )
        blobs = context.backend.read(context.snapshot, paths)
        if any(blobs[path] != raw for path, raw in (base | originals).items()):
            return _finish(context, LocalOutcome.CONFLICT, "acceptance inputs changed")
        if any(blobs[path] is None for path in proof_paths):
            return _finish(
                context, LocalOutcome.UNAVAILABLE, "an acceptance proof is unavailable"
            )
        reads = {
            path: ReadExpectation(
                path=path,
                digest=sha256(raw).hexdigest()
                if (raw := blobs[path]) is not None
                else None,
            )
            for path in paths
        }
        if any(reads[read.path] != read for read in applicability_result.reads):
            return _finish(
                context,
                LocalOutcome.CONFLICT,
                "plan-entry applicability inputs changed",
            )
        writes = ()
        if mapping_path is not None:
            previous_mapping = blobs[mapping_path]
            if previous_mapping is None:
                writes = (BlobWrite(path=mapping_path, content=identity_mapping),)
            elif previous_mapping != identity_mapping:
                return _finish(
                    context,
                    LocalOutcome.CONFLICT,
                    "retained identity mapping differs from its content address",
                )
        digest = evaluation.canonical_digest
        assert digest is not None
        fact = DocumentAcceptance(
            role=role,
            path=doc.path,
            canonical_version="aitm.authored-content/v1",
            canonical_digest=digest,
            raw_digest=sha256(doc.raw).hexdigest(),
            review_refs=review_refs,
            levels=evaluation.required_levels,
            policy_digest=context.policy_digest,
            source_planning_sha=context.snapshot.revision,
            plan_generation=_generation(role, doc.path, digest, lifecycle, raw_log),
        )
        previous = lifecycle.accepted_documents.get(role)
        if previous is not None and previous == fact.model_copy(
            update={
                "raw_digest": previous.raw_digest,
                "source_planning_sha": previous.source_planning_sha,
                "plan_generation": previous.plan_generation
                if role == "design"
                else fact.plan_generation,
            }
        ):
            if writes:
                return _finish(
                    context,
                    LocalOutcome.CONFLICT,
                    "accepted identity mapping is missing",
                )
            if context.backend.snapshot() != context.snapshot:
                return _finish(
                    context, LocalOutcome.CONFLICT, "acceptance snapshot changed"
                )
            return _finish(context, LocalOutcome.COMPLETED)

        change = RelatedWriteSet(read_set=tuple(reads.values()))
        event = (
            EventEnvelope(
                v=1,
                id=f"{context.operation_id}:accepted",
                type="core.doc.accepted",
                story=doc.story,
                ts=context.at,
                recorded_at=context.at,
                actor=context.owner.actor,
                operation_id=context.operation_id,
                sequence=state.next_sequence,
                prior_log_digest=state.prior_log_digest,
                policy_digest=context.policy_digest,
                read_set_digest=change.read_set_digest,
                data=fact.model_dump(mode="json"),
            )
            .model_dump_json(exclude_none=True)
            .encode()
        )
        change = RelatedWriteSet(
            read_set=change.read_set,
            events=(EventAppend(story=doc.story, records=(event,)),),
            writes=writes,
        )
    except (UnavailablePort, UnavailableReducer) as error:
        return _finish(context, LocalOutcome.UNAVAILABLE, str(error))
    except ValueError as error:
        return _finish(context, LocalOutcome.INTEGRITY_ERROR, str(error))
    return context.publish(
        Operation(
            operation_id=context.operation_id,
            owner=context.owner,
            policy_digest=context.policy_digest,
            category=OperationCategory.NORMAL,
            intent=FinalizationIntent(
                kind=f"{role}.accept",
                version=1,
                related_preconditions=change.read_set,
                payload=dumps(payload, separators=(",", ":")).encode(),
            ),
            change=change,
        ),
        context.snapshot,
    )
