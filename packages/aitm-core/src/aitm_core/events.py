"""Append-order validation and explicitly registered event reduction."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from hashlib import sha256
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


class ReducerRegistry:
    def __init__(self, *, required_namespaces: Iterable[str] = ()) -> None:
        self._required = frozenset(required_namespaces) | {"core"}
        self._reducers: dict[str, Reducer] = {}

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


def fold(
    events: Iterable[bytes | EventEnvelope],
    reducers: ReducerRegistry,
) -> StoryState:
    """Replay unique events in supplied order, validating the committed prefix."""

    state = StoryState()
    prefix = sha256()
    seen: dict[str, bytes] = {}
    opaque: list[bytes] = []
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
        if state.story_id is not None and event.story != state.story_id:
            raise FoldIntegrityError(f"event belongs to another story: {event.story}")
        if event.sequence != state.next_sequence:
            raise FoldIntegrityError(f"unexpected event sequence: {event.sequence}")
        if event.prior_log_digest != state.prior_log_digest:
            raise FoldIntegrityError(
                f"prior log digest disagrees at sequence {event.sequence}"
            )

        prefix.update(raw.removesuffix(b"\n") + b"\n")
        seen[event.id] = raw
        state = replace(
            state,
            story_id=event.story,
            next_sequence=event.sequence + 1,
            prior_log_digest=prefix.hexdigest(),
        )
        reducer = reducers.resolve(event)
        if reducer is None:
            opaque.append(raw)
        else:
            projection = reducer(state, event)
            state = replace(state, domains=projection.domains)
    return replace(state, opaque_events=tuple(opaque))
