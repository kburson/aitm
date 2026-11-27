"""Append-order validation and explicitly registered event reduction."""

from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from hashlib import sha256
from itertools import groupby
from typing import Self

from aitm_core.models.events import EventEnvelope, validate_envelope

EMPTY_LOG_DIGEST = sha256(b"").hexdigest()


class FoldIntegrityError(ValueError):
    """The records cannot belong to one valid story stream."""


class UnavailableReducer(LookupError):
    """A required event has no installed reducer."""


@dataclass(frozen=True, slots=True)
class StoryState:
    """Structural replay state with a projection for owning domain reducers."""

    story_id: int | None = None
    next_sequence: int = 1
    prior_log_digest: str = EMPTY_LOG_DIGEST
    opaque_events: tuple[bytes, ...] = ()
    domains: Mapping[str, object] = field(default_factory=dict)


Reducer = Callable[[StoryState, EventEnvelope], StoryState]
BatchValidator = Callable[[Iterable[EventEnvelope]], None]


class ReducerRegistry:
    def __init__(
        self,
        *,
        required_namespaces: Iterable[str] = (),
        batch_validator: BatchValidator | None = None,
    ) -> None:
        self._required = frozenset(required_namespaces) | {"core"}
        self._reducers: dict[str, Reducer] = {}
        self.batch_validator = batch_validator

    def register(self, event_type: str, reducer: Reducer) -> Self:
        if event_type in self._reducers:
            raise ValueError(f"event reducer is already registered: {event_type}")
        self._reducers[event_type] = reducer
        return self

    def resolve(self, event: EventEnvelope) -> Reducer | None:
        reducer = self._reducers.get(event.type)
        if reducer is None and event.namespace in self._required:
            raise UnavailableReducer(
                f"required event reducer is unavailable: {event.type}"
            )
        return reducer


def _validated_records(
    events: Iterable[bytes | EventEnvelope],
) -> Iterator[tuple[EventEnvelope, str]]:
    prefix = sha256()
    seen: dict[str, bytes] = {}
    story_id = None
    next_sequence = 1
    for item in events:
        raw = item.raw_record if isinstance(item, EventEnvelope) else item
        event = validate_envelope(raw)
        first = seen.get(event.id)
        if first is not None:
            if first != raw:
                raise FoldIntegrityError(
                    f"event identity has different bytes: {event.id}"
                )
            continue
        if story_id is not None and event.story != story_id:
            raise FoldIntegrityError(f"event belongs to another story: {event.story}")
        if event.sequence != next_sequence:
            raise FoldIntegrityError(f"unexpected event sequence: {event.sequence}")
        if event.prior_log_digest != prefix.hexdigest():
            raise FoldIntegrityError(
                f"prior log digest disagrees at sequence {event.sequence}"
            )

        prefix.update(raw.removesuffix(b"\n") + b"\n")
        seen[event.id] = raw
        story_id = event.story
        next_sequence += 1
        yield event, prefix.hexdigest()


def _validated_batches(
    records: Iterable[tuple[EventEnvelope, str]], validate: BatchValidator
) -> Iterator[tuple[EventEnvelope, str]]:
    for _, operation in groupby(records, lambda record: record[0].operation_id):
        batch = tuple(operation)
        validate(event for event, _ in batch)
        yield from batch


def fold(
    events: Iterable[bytes | EventEnvelope], reducers: ReducerRegistry
) -> StoryState:
    """Replay unique events in supplied order, validating their committed prefix."""
    records = _validated_records(events)
    if reducers.batch_validator is not None:
        records = _validated_batches(records, reducers.batch_validator)

    state = StoryState()
    opaque: list[bytes] = []
    for event, digest in records:
        state = replace(
            state,
            story_id=event.story,
            next_sequence=event.sequence + 1,
            prior_log_digest=digest,
        )
        reducer = reducers.resolve(event)
        if reducer is None:
            opaque.append(event.raw_record)
        else:
            projection = reducer(state, event)
            state = replace(state, domains=projection.domains)
    return replace(state, opaque_events=tuple(opaque))


def _core_domains():
    from aitm_core.reducers.attempts import attempt_schemas, fold_attempt
    from aitm_core.reducers.evidence import evidence_schemas, fold_evidence
    from aitm_core.reducers.lifecycle import fold_lifecycle, lifecycle_schemas

    return (
        (lifecycle_schemas(), fold_lifecycle),
        (attempt_schemas(), fold_attempt),
        (evidence_schemas(), fold_evidence),
    )


def core_reducers() -> ReducerRegistry:
    """Compose the owning reducers and validate each operation before replay."""
    from aitm_core.reducers.evidence import fold_session_started, validate_core_batch

    registry = ReducerRegistry(batch_validator=validate_core_batch)
    for schemas, reducer in _core_domains():
        for event_type in schemas:
            owning_reducer = (
                fold_session_started
                if event_type == "core.session.started"
                else reducer
            )
            registry.register(event_type, owning_reducer)
    return registry


def core_event_schema() -> dict[str, object]:
    """Export a draft 2020-12 schema of the installed Core envelope and payloads."""
    from pydantic import TypeAdapter

    schemas = {}
    for domain, _ in _core_domains():
        for event_type, schema in domain.items():
            if event_type in schemas:
                raise ValueError(f"event schema is already registered: {event_type}")
            schemas[event_type] = schema
    keys = sorted(schemas)
    adapters = [(key, "validation", TypeAdapter(schemas[key])) for key in keys]
    adapters.append(("envelope", "validation", TypeAdapter(EventEnvelope)))
    definitions, document = TypeAdapter.json_schemas(adapters)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AITM Core event v1",
        **definitions["envelope", "validation"],
        **document,
        "oneOf": [
            {
                "properties": {
                    "type": {"const": key},
                    "data": definitions[key, "validation"],
                }
            }
            for key in keys
        ],
    }
