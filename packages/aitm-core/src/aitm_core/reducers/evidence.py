"""Fold retained evidence without running guards, actions or verification."""

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import datetime
from json import dumps

from pydantic import BaseModel, TypeAdapter, ValidationError

from aitm_core.events import StoryState
from aitm_core.models.attempts import BindingPurpose, RecoveryBinding
from aitm_core.models.events import EventEnvelope
from aitm_core.models.evidence import (
    ActionCompleted,
    ActionFailed,
    ActionScope,
    ActivityRecorded,
    DeliverableValidated,
    DeliveryVerified,
    DocumentReviewCompleted,
    DocumentReviewFact,
    DocumentReviewOpened,
    DocumentReviewTurn,
    DraftObserved,
    EvidenceSessionStarted,
    ExpansionCustody,
    ExpansionRecorded,
    ExpansionReservationResolved,
    ExpansionReserved,
    ExpansionResolved,
    GuardEvaluated,
    IdeaCreated,
    OutcomeRecorded,
    PivotRecorded,
    ReviewActivated,
    ReviewInvalidated,
    ReviewRecorded,
    SessionEnded,
    SessionStarted,
    TestReceipt,
    TripDecided,
    TripRecorded,
    UsageRecorded,
)
from aitm_core.reducers.attempts import fold_attempt, validate_boundary_batch

_SCHEMAS = {
    "core.idea.created": IdeaCreated,
    "core.draft.created": DraftObserved,
    "core.draft.discarded": DraftObserved,
    "core.guard.evaluated": GuardEvaluated,
    "core.action.pending": ActionScope,
    "core.action.completed": ActionCompleted,
    "core.action.failed": ActionFailed,
    "core.session.started": SessionStarted | EvidenceSessionStarted,
    "core.session.ended": SessionEnded,
    "core.expansion.reserved": ExpansionReserved,
    "core.expansion.reservation-resolved": ExpansionReservationResolved,
    "core.expansion.recorded": ExpansionRecorded,
    "core.expansion.custody-recorded": ExpansionCustody,
    "core.expansion.resolved": ExpansionResolved,
    "core.trip.recorded": TripRecorded,
    "core.trip.decided": TripDecided,
    "core.pivot.recorded": PivotRecorded,
    "core.test.receipt": TestReceipt,
    "core.review.recorded": ReviewRecorded,
    "core.review.activated": ReviewActivated,
    "core.review.invalidated": ReviewInvalidated,
    "core.doc-review.opened": DocumentReviewOpened,
    "core.doc-review.submitted": DocumentReviewTurn,
    "core.doc-review.completed": DocumentReviewCompleted,
    "core.deliverable.validated": DeliverableValidated,
    "core.delivery.verified": DeliveryVerified,
    "core.outcome.recorded": OutcomeRecorded,
    "core.usage.recorded": UsageRecorded,
    "core.activity.recorded": ActivityRecorded,
}
_ADAPTERS = {kind: TypeAdapter(model) for kind, model in _SCHEMAS.items()}


class EvidenceIntegrityError(ValueError):
    """Evidence is malformed or contradicts a retained fact."""


@dataclass(frozen=True, slots=True)
class ObservedFact:
    envelope: EventEnvelope
    payload: BaseModel


@dataclass(frozen=True, slots=True)
class ActionRecord:
    pending: ActionScope
    results: dict[str, ActionCompleted | ActionFailed] = field(default_factory=dict)

    @property
    def result(self) -> ActionCompleted | ActionFailed | None:
        return next(reversed(self.results.values()), None)


@dataclass(frozen=True, slots=True)
class DocumentReview:
    level: str
    path: str
    opening: DocumentReviewOpened | None = None
    turns: dict[tuple[int, str], DocumentReviewTurn] = field(default_factory=dict)
    completion: DocumentReviewCompleted | None = None

    @property
    def started_at(self) -> str | None:
        if self.opening is not None:
            return self.opening.opened_at
        if self.completion is not None and self.completion.start_basis != "unknown":
            return self.completion.started_at
        return None


@dataclass(frozen=True, slots=True)
class EvidenceState:
    story_id: int
    facts: dict[str, tuple[ObservedFact, ...]] = field(default_factory=dict)
    actions: dict[tuple[str, str, str, int], ActionRecord] = field(default_factory=dict)
    reviews: dict[str, ReviewRecorded] = field(default_factory=dict)
    effective_reviews: dict[str, ReviewActivated] = field(default_factory=dict)
    document_reviews: dict[str, DocumentReview] = field(default_factory=dict)
    usage: dict[tuple[str, str], UsageRecorded] = field(default_factory=dict)


def evidence_schemas():
    return _SCHEMAS.copy()


def _decode(event: EventEnvelope) -> BaseModel:
    adapter = _ADAPTERS.get(event.type)
    if adapter is None:
        raise EvidenceIntegrityError(f"event is not owned by evidence: {event.type}")
    try:
        return adapter.validate_json(dumps(event.data, allow_nan=False))
    except (ValidationError, ValueError) as error:
        raise EvidenceIntegrityError(
            f"invalid evidence payload for {event.type}"
        ) from error


def _attempt_binding(event: EventEnvelope) -> EventEnvelope:
    # The C55 observation carries only the binding authority fields. The owning
    # evidence record retains the original envelope and the full session payload.
    return event.model_copy(
        update={
            "data": {name: event.data[name] for name in RecoveryBinding.model_fields}
        }
    )


def _boundary_event(event: EventEnvelope) -> EventEnvelope:
    if (
        event.type == "core.session.started"
        and event.data.get("purpose") == BindingPurpose.EVIDENCE
    ):
        _decode(event)
        return _attempt_binding(event)
    return event


def validate_core_batch(batch: Iterable[EventEnvelope]) -> None:
    validate_boundary_batch(_boundary_event(event) for event in batch)


def _apply_action(
    state: EvidenceState, fact: ActionScope, event: EventEnvelope
) -> EvidenceState:
    key = fact.key
    record = state.actions.get(key)
    scope = ActionScope.model_validate(
        fact.model_dump(include=set(ActionScope.model_fields))
    )
    if type(fact) is ActionScope:
        if (
            fact.origin_operation != event.operation_id
            or record is not None
            and record.pending != scope
        ):
            raise EvidenceIntegrityError(
                "pending action conflicts with its operation or retained scope"
            )
        if record is not None:
            return state
        next_record = ActionRecord(pending=scope)
    else:
        if record is None or record.pending != scope:
            raise EvidenceIntegrityError(
                "action result lacks a matching pending action"
            )
        prior = record.results.get(event.operation_id)
        if prior is not None:
            if prior != fact:
                raise EvidenceIntegrityError("operation has conflicting action results")
            return state
        if isinstance(record.result, ActionCompleted):
            if record.result != fact:
                raise EvidenceIntegrityError(
                    "completed action has a conflicting result"
                )
            return state
        next_record = replace(
            record, results={**record.results, event.operation_id: fact}
        )
    return replace(state, actions={**state.actions, key: next_record})


def _review_scope(fact: ReviewRecorded | ReviewActivated) -> tuple:
    return fact.attempt, fact.generation, fact.source


def _apply_review(
    state: EvidenceState, fact: ReviewRecorded | ReviewActivated
) -> EvidenceState:
    recorded = state.reviews.get(fact.review_id)
    if isinstance(fact, ReviewRecorded):
        if recorded is not None and recorded != fact:
            raise EvidenceIntegrityError("review receipt has conflicting data")
        return replace(state, reviews={**state.reviews, fact.review_id: fact})

    if (
        recorded is None
        or recorded.verdict != "pass"
        or _review_scope(recorded) != _review_scope(fact)
    ):
        raise EvidenceIntegrityError("review change lacks a matching passing receipt")
    effective = state.effective_reviews.copy()
    if isinstance(fact, ReviewInvalidated):
        active = effective.get(fact.review_id)
        if active is None or _review_scope(active) != _review_scope(fact):
            raise EvidenceIntegrityError(
                "review invalidation lacks a matching effective review"
            )
        del effective[fact.review_id]
    else:
        if fact.review_id in effective:
            raise EvidenceIntegrityError("review is already effective")
        effective[fact.review_id] = fact
    return replace(state, effective_reviews=effective)


def _apply_document_review(
    state: EvidenceState, fact: DocumentReviewFact, event: EventEnvelope
) -> EvidenceState:
    review = state.document_reviews.get(
        fact.record_id, DocumentReview(fact.level, fact.path)
    )
    if (review.level, review.path) != (fact.level, fact.path):
        raise EvidenceIntegrityError(
            "document review record identifies another document or level"
        )
    if isinstance(fact, DocumentReviewOpened):
        if fact.source_operation != event.operation_id:
            raise EvidenceIntegrityError(
                "document review opening disagrees with its source operation"
            )
        if review.opening is not None and review.opening != fact:
            raise EvidenceIntegrityError("document review has competing openings")
        if review.completion is not None:
            _check_review_completion(fact, review.completion)
        review = replace(review, opening=fact)
    elif isinstance(fact, DocumentReviewTurn):
        _check_review_turn(fact)
        key = (fact.round, fact.role)
        prior = review.turns.get(key)
        if prior is not None and prior != fact:
            raise EvidenceIntegrityError(
                "document review turn has conflicting source data"
            )
        if review.completion is not None and fact.round > review.completion.rounds:
            raise EvidenceIntegrityError(
                "document review turn exceeds the recorded completion"
            )
        review = replace(review, turns={**review.turns, key: fact})
    elif isinstance(fact, DocumentReviewCompleted):
        if review.completion is not None and review.completion != fact:
            raise EvidenceIntegrityError("document review has competing completions")
        if any(round_no > fact.rounds for round_no, _ in review.turns):
            raise EvidenceIntegrityError(
                "document review completion omits retained rounds"
            )
        _check_review_completion(review.opening, fact)
        review = replace(review, completion=fact)
    return replace(
        state, document_reviews={**state.document_reviews, fact.record_id: review}
    )


def _check_review_turn(fact: DocumentReviewTurn) -> None:
    if fact.role == "reviewer" and (fact.input_digest is None or fact.decision is None):
        raise EvidenceIntegrityError("reviewer turn lacks reviewed input or decision")
    if fact.role == "author" and (
        fact.output_digest is None
        or fact.patch_path is None
        or fact.decision is not None
    ):
        raise EvidenceIntegrityError(
            "author turn lacks output and patch or includes a decision"
        )
    if fact.start_basis != "unknown" and (
        fact.started_at is None or fact.start_ref is None
    ):
        raise EvidenceIntegrityError(
            "document review turn lacks evidence for its start"
        )
    if fact.started_at is not None and datetime.fromisoformat(
        fact.started_at
    ) > datetime.fromisoformat(fact.submitted_at):
        raise EvidenceIntegrityError("document review turn has an inverted interval")


def _check_review_completion(
    opening: DocumentReviewOpened | None, completion: DocumentReviewCompleted
) -> None:
    if opening is not None:
        if completion.base_digest != opening.content_digest:
            raise EvidenceIntegrityError(
                "document review completion does not match its opening input"
            )
        if (
            completion.started_at is not None
            and completion.started_at != opening.opened_at
        ):
            raise EvidenceIntegrityError(
                "document review completion disagrees with its opening time"
            )
    began = opening.opened_at if opening is not None else completion.started_at
    if began is not None and datetime.fromisoformat(began) > datetime.fromisoformat(
        completion.ended_at
    ):
        raise EvidenceIntegrityError(
            "document review completion has an inverted interval"
        )


def _structured_observation(
    state: EvidenceState, fact: BaseModel, event: EventEnvelope
) -> EvidenceState:
    if isinstance(fact, ActionScope):
        return _apply_action(state, fact, event)
    if isinstance(fact, (ReviewRecorded, ReviewActivated)):
        return _apply_review(state, fact)
    if isinstance(fact, DocumentReviewFact):
        return _apply_document_review(state, fact, event)
    if isinstance(fact, UsageRecorded):
        key = (fact.producer, fact.receipt_id)
        prior = state.usage.get(key)
        if prior is not None and prior != fact:
            raise EvidenceIntegrityError("usage receipt has conflicting data")
        return replace(state, usage={**state.usage, key: fact})
    if isinstance(fact, GuardEvaluated) and (
        fact.operation != event.operation_id
        or event.policy_digest not in (None, fact.policy_digest)
        or event.read_set_digest not in (None, fact.read_set_digest)
    ):
        raise EvidenceIntegrityError(
            "guard provenance disagrees with the event envelope"
        )
    return state


def _check_expansion_custody(
    state: StoryState, evidence: EvidenceState, fact: ExpansionCustody
) -> None:
    from aitm_core.models.attempts import AttemptState

    attempts = state.domains.get("attempts")
    active = (
        attempts.attempts.get(fact.attempt)
        if isinstance(attempts, AttemptState)
        else None
    )
    if (
        active is None
        or active.generation != fact.generation
        or active.clock_mode != "terminal-closed"
        or not active.closed
    ):
        raise EvidenceIntegrityError(
            "Expansion custody requires the exact stopped attempt."
        )
    held = [
        row.payload
        for row in evidence.facts.get("core.expansion.reserved", ())
        if row.payload.reservation == fact.reservation
    ]
    if len(held) != 1 or (held[0].attempt, held[0].generation) != (
        fact.attempt,
        fact.generation,
    ):
        raise EvidenceIntegrityError("Expansion custody lacks the exact reservation.")
    previous = [
        row.payload
        for row in evidence.facts.get("core.expansion.custody-recorded", ())
        if row.payload.reservation == fact.reservation
    ]
    if previous and (
        len(previous) != 1
        or previous[0].disposition != "sender-fenced"
        or fact.disposition == "sender-fenced"
        or previous[0].claim != fact.claim
        or previous[0].semantic_key != fact.semantic_key
    ):
        raise EvidenceIntegrityError(
            "Expansion custody conflicts with a retained fact."
        )
    if (
        fact.authority == "provider-claim"
        and fact.disposition == "no-child"
        and (not previous or previous[0].fence != fact.fence)
    ):
        raise EvidenceIntegrityError(
            "Provider absence requires its previously published fence."
        )


def fold_evidence(state: StoryState, event: EventEnvelope) -> StoryState:
    """Fold one C56-owned fact into the evidence projection."""
    current = state.domains.get("evidence", EvidenceState(event.story))
    if not isinstance(current, EvidenceState):
        raise EvidenceIntegrityError("invalid evidence domain")
    if current.story_id != event.story or state.story_id not in (None, event.story):
        raise EvidenceIntegrityError("evidence event belongs to another story")

    fact = _decode(event)
    if isinstance(fact, ExpansionCustody):
        _check_expansion_custody(state, current, fact)
    updated = _structured_observation(current, fact, event)
    row = ObservedFact(event, fact)
    facts = {**updated.facts, event.type: (*updated.facts.get(event.type, ()), row)}
    domains = {**state.domains, "evidence": replace(updated, facts=facts)}
    return replace(state, domains=domains)


def fold_session_started(state: StoryState, event: EventEnvelope) -> StoryState:
    projected = fold_evidence(state, event)
    observed = projected.domains["evidence"].facts[event.type][-1].payload
    if isinstance(observed, EvidenceSessionStarted):
        return fold_attempt(projected, _attempt_binding(event))
    return projected
