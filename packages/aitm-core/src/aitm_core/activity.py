"""Qualify provider observations without changing recorded history."""

from collections.abc import Iterable
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

from aitm_core.ext.api import ProducerRef

if TYPE_CHECKING:
    from aitm_core.models.evidence import ActivityRecorded


@dataclass(frozen=True, slots=True)
class ActivityObservation:
    source_id: str
    actor: str
    actor_kind: Literal["agent", "human", "tool"]
    session: str
    attempt: str
    generation: int
    binding: str
    observed_at: datetime
    recorded_at: datetime
    ended_at: datetime | None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ActivityEvidence:
    producer: ProducerRef
    observation: ActivityObservation
    qualified: bool
    reason: str | None


@dataclass(frozen=True, slots=True)
class EventBatch:
    records: tuple[ActivityEvidence, ...]


def ingest_activity(
    producer: ProducerRef, observations: Iterable[ActivityObservation]
) -> EventBatch:
    """Attach a registry-resolved producer and retain first occurrence in input order.

    The caller supplies the result of Registry.register_activity. Qualification
    here checks the producer's observation contract. Attempt binding, clock
    windows and the report's recording cutoff are evaluated by the consumer.
    """
    seen: dict[str, ActivityObservation] = {}
    records: list[ActivityEvidence] = []
    for observation in observations:
        source = observation.source_id
        if isinstance(source, str):
            previous = seen.get(source)
            if previous is not None:
                if not _same_observation(previous, observation):
                    raise ValueError(f"conflicting activity observation for {source!r}")
                continue
            seen[source] = observation
        reason = _ineligibility(producer, observation)
        records.append(ActivityEvidence(producer, observation, reason is None, reason))
    return EventBatch(tuple(records))


def retained_activity(record: "ActivityRecorded") -> ActivityEvidence | None:
    """Re-qualify a durable observation using its exact original producer and proof."""
    proof = record.provenance
    if (
        proof is None
        or record.session is None
        or record.attempt is None
        or record.recorded_at is None
    ):
        return None
    producer = ProducerRef(
        id=record.producer,
        version=proof.producer_version,
        measurement_contract=proof.measurement_contract,
        coverage_class=record.coverage,
    )
    observation = ActivityObservation(
        source_id=proof.source_id,
        actor=proof.actor,
        actor_kind=proof.actor_kind,
        session=record.session,
        attempt=record.attempt,
        generation=proof.generation,
        binding=proof.binding,
        observed_at=datetime.fromisoformat(record.observed_at),
        recorded_at=datetime.fromisoformat(record.recorded_at),
        ended_at=datetime.fromisoformat(record.ended_at)
        if record.ended_at is not None
        else None,
        evidence=proof.proof_refs,
    )
    return ingest_activity(producer, (observation,)).records[0]


def _same_observation(left: ActivityObservation, right: ActivityObservation) -> bool:
    for field in fields(ActivityObservation):
        original = getattr(left, field.name)
        replay = getattr(right, field.name)
        if type(original) is not type(replay):
            return False
        if isinstance(original, datetime):
            # Datetime equality alone can equate an invalid offset with a UTC fact.
            if (
                original.replace(tzinfo=None) != replay.replace(tzinfo=None)
                or original.tzinfo != replay.tzinfo
                or original.fold != replay.fold
            ):
                return False
        elif original != replay:
            return False
    return True


def _present(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc(value: object) -> bool:
    if not isinstance(value, datetime):
        return False
    try:
        return value.utcoffset() == timedelta(0)
    except (ValueError, TypeError, OverflowError, NotImplementedError):
        return False


def _ineligibility(
    producer: ProducerRef, observation: ActivityObservation
) -> str | None:
    for field in ("source_id", "actor", "session", "attempt", "binding"):
        if not _present(getattr(observation, field)):
            return f"missing or invalid {field}"
    if type(observation.generation) is not int or observation.generation <= 0:
        return "invalid binding generation"

    start = observation.observed_at
    end = observation.ended_at
    recorded = observation.recorded_at
    if not (_utc(start) and _utc(recorded) and (end is None or _utc(end))):
        return "activity timestamps must be UTC"
    if recorded < start or (end is not None and (end <= start or end > recorded)):
        return "invalid activity timestamp order"

    evidence = observation.evidence
    if not isinstance(evidence, tuple) or not all(map(_present, evidence)):
        return "invalid evidence references"

    match producer.measurement_contract, producer.coverage_class:
        case "engaged-interval/v1", "measured-engagement":
            if observation.actor_kind != "agent" or end is None:
                return "measured engagement requires an agent interval"
            if not evidence:
                return "measured engagement requires source evidence"
        case "tool-interval/v1", "tool-duration":
            if observation.actor_kind != "tool" or end is None:
                return "tool duration requires a tool interval"
        case "cli-gap/v1", "gap-estimate":
            if observation.actor_kind != "agent" or end is not None:
                return "gap estimation requires an agent point"
        case _:
            return "unsupported activity measurement contract"
    return None
