"""Report elapsed response work from explicitly covered review-turn intervals."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from aitm_core.models.evidence import DocumentReviewTurn, ReviewParticipant

type Interval = tuple[datetime, datetime]
type ReviewGroup = tuple[str, str, str, str]  # Level, role, provider, model.
type Attribution = tuple[str | None, str | None, str | None, str | None, str | None]
type Session = tuple[str, str, str, str]
type Actor = str | Session
type TimingCategory = Literal["qualified", "interrupted", "excluded", "unknown"]
_ZERO = timedelta()


@dataclass(frozen=True, slots=True)
class TurnTimingEvidence:
    """A validated turn with observed response coverage and any known gaps.

    Coverage windows must come from evidence about this exact turn. A session
    registration or a pair of start/end timestamps alone supplies no coverage.
    An explicit actor ID can link sessions belonging to the same participant.
    """

    turn: DocumentReviewTurn
    covered: tuple[Interval, ...] = ()
    interrupted: tuple[Interval, ...] = ()
    excluded: tuple[Interval, ...] = ()
    actor_id: str | None = None


@dataclass(frozen=True, slots=True)
class StateWindow:
    """One state interval supported by observed workflow boundaries."""

    state: str
    interval: Interval


@dataclass(frozen=True, slots=True)
class TurnTiming:
    evidence: TurnTimingEvidence
    bound: Interval | None
    qualified: tuple[Interval, ...]
    interrupted: tuple[Interval, ...]
    excluded: tuple[Interval, ...]
    unknown: tuple[Interval, ...]
    response_duration: timedelta | None
    by_state: dict[str | None, dict[TimingCategory, timedelta]]

    @property
    def turn(self) -> DocumentReviewTurn:
        return self.evidence.turn


@dataclass(frozen=True, slots=True)
class ReviewTimingSummary:
    """Per-turn evidence and elapsed totals over the qualified portions.

    Attribution is keyed by state, level, role, provider and model. A missing
    component identifies a dimension where the evidence cannot allocate time.
    """

    turns: tuple[TurnTiming, ...]
    basis_counts: dict[str, int]
    actor_time: timedelta | None
    wall_time: timedelta | None
    unallocated_actor_wall_time: timedelta | None
    attributed_time: dict[Attribution, timedelta]


def _check_interval(interval: Interval) -> None:
    start, end = interval
    if start.utcoffset() != _ZERO or end.utcoffset() != _ZERO or start >= end:
        raise ValueError("review timing evidence requires a positive UTC interval")


def _partition[Label](
    intervals: Iterable[tuple[Interval, Label]],
) -> Iterator[tuple[Interval, frozenset[Label]]]:
    changes: dict[datetime, Counter[Label]] = defaultdict(Counter)
    for (start, end), label in intervals:
        _check_interval((start, end))
        changes[start][label] += 1
        changes[end][label] -= 1
    active: Counter[Label] = Counter()
    times = sorted(changes)
    for start, end in zip(times, times[1:]):
        for label, change in changes[start].items():
            active[label] += change
            if not active[label]:
                del active[label]
        if active:
            yield (start, end), frozenset(active)


def _duration(intervals: Iterable[Interval]) -> timedelta:
    return sum((end - start for start, end in intervals), _ZERO)


def _union_time(intervals: list[Interval]) -> timedelta | None:
    if not intervals:
        return None
    return _duration(span for span, _ in _partition((span, True) for span in intervals))


def _turn_bound(turn: DocumentReviewTurn, submitted: datetime) -> Interval | None:
    if turn.start_basis == "unknown" or not turn.started_at or not turn.start_ref:
        return None
    start = datetime.fromisoformat(turn.started_at)
    return (start, submitted) if start <= submitted else None


def _add_span(spans: list[Interval], span: Interval) -> None:
    start, end = span
    if spans and spans[-1][1] == start:
        spans[-1] = spans[-1][0], end
    else:
        spans.append(span)


def _turn_timing(
    evidence: TurnTimingEvidence, states: tuple[StateWindow, ...]
) -> TurnTiming:
    turn = evidence.turn
    submitted = datetime.fromisoformat(turn.submitted_at)
    bound = _turn_bound(turn, submitted)
    proxy = turn.start_basis == "prior-submit"
    inputs = [
        *((span, "covered") for span in evidence.covered),
        *((span, "interrupted") for span in evidence.interrupted),
        *((span, "excluded") for span in evidence.excluded),
    ]
    if bound and bound[0] < bound[1]:
        inputs.append((bound, "bound"))
    portions: dict[TimingCategory, list[Interval]] = defaultdict(list)
    for (start, end), labels in _partition(inputs):
        if start >= submitted or (bound is not None and "bound" not in labels):
            continue
        category: TimingCategory
        if "excluded" in labels:
            category = "excluded"
        elif "interrupted" in labels:
            category = "interrupted"
        elif "covered" in labels:
            category = "qualified"
        elif bound is not None:
            category = "unknown"
        else:
            continue
        _add_span(portions[category], (start, min(end, submitted)))
    qualified = tuple(portions["qualified"])
    unknown = tuple(portions["unknown"])
    duration = None if bound is None or proxy or unknown else _duration(qualified)
    by_state: dict[str | None, dict[TimingCategory, timedelta]] = {}
    labeled = (
        (span, category) for category, spans in portions.items() for span in spans
    )
    for (start, end), state, categories in _with_states(labeled, states):
        state_totals = by_state.setdefault(state, {})
        for category in categories:
            state_totals[category] = state_totals.get(category, _ZERO) + end - start
    return TurnTiming(
        evidence,
        bound,
        qualified,
        tuple(portions["interrupted"]),
        tuple(portions["excluded"]),
        unknown,
        duration,
        by_state,
    )


def _session(participant: ReviewParticipant) -> Session | None:
    if participant.session_id is None or participant.session_id_kind == "unknown":
        return None
    return (
        participant.host,
        participant.provider,
        participant.session_id_kind,
        participant.session_id,
    )


def _only[Value](values: Iterable[Value]) -> Value | None:
    distinct = set(values)
    return distinct.pop() if len(distinct) == 1 else None


def _with_states[Label](
    spans: Iterable[tuple[Interval, Label]], states: tuple[StateWindow, ...]
) -> Iterator[tuple[Interval, str | None, tuple[Label, ...]]]:
    tagged: list[tuple[Interval, Label | StateWindow]] = [*spans]
    tagged.extend((window.interval, window) for window in states)
    for span, labels in _partition(tagged):
        evidence = tuple(
            label for label in labels if not isinstance(label, StateWindow)
        )
        if evidence:
            state = _only(
                label.state for label in labels if isinstance(label, StateWindow)
            )
            yield span, state, evidence


def _attribute(
    spans: list[tuple[Interval, ReviewGroup]],
    states: tuple[StateWindow, ...],
    totals: dict[Attribution, timedelta],
) -> None:
    for (start, end), state, groups in _with_states(spans, states):
        level, role, provider, model = zip(*groups, strict=True)
        key = state, _only(level), _only(role), _only(provider), _only(model)
        totals[key] += end - start


def summarize_review_timing(
    evidence: Iterable[TurnTimingEvidence], *, states: Iterable[StateWindow] = ()
) -> ReviewTimingSummary:
    """Combine validated turn evidence without inferring work from outer bounds.

    Independent exact-turn coverage can establish partial elapsed work even
    when a sourced start is missing or the only start is a fallback proxy.
    """
    windows = tuple(states)
    for window in windows:
        _check_interval(window.interval)

    turns: dict[tuple[str, int, str], TurnTiming] = {}
    known_actors: dict[Session, str] = {}
    for entry in evidence:
        turn = entry.turn
        identity = turn.record_id, turn.round, turn.role
        if identity in turns:
            if turns[identity].evidence != entry:
                raise ValueError(f"conflicting timing evidence for turn {identity!r}")
            continue
        turns[identity] = _turn_timing(entry, windows)
        session = _session(turn.agent)
        if session is not None and entry.actor_id is not None:
            if known_actors.setdefault(session, entry.actor_id) != entry.actor_id:
                raise ValueError(
                    f"conflicting actor identities for session {session!r}"
                )

    by_actor: dict[Actor, list[tuple[Interval, ReviewGroup]]] = defaultdict(list)
    wall = []
    unknown_actor = []
    for timing in turns.values():
        if not timing.qualified:
            continue
        wall.extend(timing.qualified)
        turn = timing.turn
        session = _session(turn.agent)
        actor: Actor | None = timing.evidence.actor_id or session
        if session in known_actors:
            actor = known_actors[session]
        if actor is None:
            unknown_actor.extend(timing.qualified)
            continue
        group = turn.level, turn.role, turn.agent.provider, turn.agent.model_id
        by_actor[actor].extend((span, group) for span in timing.qualified)

    totals: dict[Attribution, timedelta] = defaultdict(timedelta)
    for spans in by_actor.values():
        _attribute(spans, windows, totals)
    return ReviewTimingSummary(
        tuple(turns.values()),
        dict(Counter(timing.turn.start_basis for timing in turns.values())),
        sum(totals.values(), _ZERO) if totals else None,
        _union_time(wall),
        _union_time(unknown_actor),
        dict(totals),
    )
