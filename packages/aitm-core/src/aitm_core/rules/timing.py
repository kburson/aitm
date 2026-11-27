"""Compute implementation engagement from retained, qualified observations."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta

from aitm_core.activity import ActivityEvidence, _same_observation, _utc
from aitm_core.models.attempts import AttemptRecord

type Interval = tuple[datetime, datetime]
_GAP_LIMIT = timedelta(minutes=15)


@dataclass(frozen=True, slots=True)
class CoverageReport:
    measured_millis: int | None
    tool_millis: int | None
    estimated_millis: int | None
    confirmed_overrun: bool
    unknown: tuple[str, ...]


def _active_windows(state: AttemptRecord, as_of: datetime) -> tuple[Interval, ...]:
    clocks = [
        boundary
        for boundary in state.clocks
        if boundary.attempt == state.started.attempt
        and boundary.generation == state.generation
        and boundary.observed_at < as_of
    ]
    return tuple(
        (boundary.observed_at, end)
        for boundary, end in zip(
            clocks, [*(item.observed_at for item in clocks[1:]), as_of]
        )
        if boundary.to_mode == "active" and boundary.observed_at < end
    )


def _intersect(
    start: datetime, end: datetime, windows: Iterable[Interval]
) -> list[Interval]:
    result = []
    for left, right in windows:
        beginning, finish = max(start, left), min(end, right)
        if beginning < finish:
            result.append((beginning, finish))
    return result


def _covered(spans: Iterable[Interval]) -> timedelta:
    ordered = sorted(spans)
    if not ordered:
        return timedelta(0)
    start, end = ordered[0]
    duration = timedelta(0)
    for next_start, next_end in ordered[1:]:
        if next_start > end:
            duration += end - start
            start, end = next_start, next_end
        else:
            end = max(end, next_end)
    return duration + end - start


def _millis(coverage: dict[str, list[Interval]]) -> int | None:
    nonempty = [_covered(spans) for spans in coverage.values() if spans]
    if not nonempty:
        return None
    return sum(nonempty, timedelta(0)) // timedelta(milliseconds=1)


def _has_unmeasured_window(
    measured: dict[str, list[Interval]], windows: tuple[Interval, ...]
) -> bool:
    active = _covered(windows)
    return any(_covered(spans) < active for spans in measured.values())


def _unique(records: Iterable[ActivityEvidence]) -> Iterable[ActivityEvidence]:
    by_source: dict[tuple[str, int, str], ActivityEvidence] = {}
    for record in records:
        obs = record.observation
        if not isinstance(obs.source_id, str):
            yield record
            continue
        key = record.producer.id, record.producer.version, obs.source_id
        prior = by_source.get(key)
        if prior is not None:
            if prior.producer != record.producer or not _same_observation(
                prior.observation, obs
            ):
                raise ValueError(f"conflicting activity source {obs.source_id}")
        else:
            by_source[key] = record
            yield record


def engagement(
    state: AttemptRecord,
    observations: Iterable[ActivityEvidence],
    *,
    as_of: datetime,
) -> CoverageReport:
    """Fold only facts known at the as-of boundary into the pinned active windows."""
    if not _utc(as_of):
        raise ValueError("engagement requires an explicit UTC as-of time")

    windows = _active_windows(state, as_of)
    unknown = []
    measured: dict[str, list[Interval]] = defaultdict(list)
    tools: dict[str, list[Interval]] = defaultdict(list)
    estimated: dict[str, list[Interval]] = defaultdict(list)
    points: dict[tuple[str, int, str, str], set[datetime]] = defaultdict(set)
    visible = []
    for record in observations:
        obs = record.observation
        if _utc(obs.recorded_at) and obs.recorded_at > as_of:
            unknown.append(f"{obs.source_id}: recorded after the as-of boundary")
        else:
            visible.append(record)
    for record in _unique(visible):
        obs = record.observation
        if not record.qualified or not _utc(obs.recorded_at):
            unknown.append(
                f"{obs.source_id}: {record.reason or 'unqualified observation'}"
            )
            continue
        if (obs.attempt, obs.generation, obs.binding) != (
            state.started.attempt,
            state.generation,
            state.binding,
        ):
            unknown.append(f"{obs.source_id}: different attempt, generation or binding")
            continue
        coverage = record.producer.coverage_class
        if coverage == "gap-estimate":
            identity = (
                record.producer.id,
                record.producer.version,
                obs.actor,
                obs.session,
            )
            points[identity].add(obs.observed_at)
        elif obs.ended_at is not None:
            lane = measured if coverage == "measured-engagement" else tools
            lane[obs.actor].extend(_intersect(obs.observed_at, obs.ended_at, windows))

    for (_producer, _version, actor, session), observed in points.items():
        ordered = sorted(observed)
        if len(ordered) < 2:
            unknown.append(f"{actor}/{session}: gap needs successive observations")
        for before, after in zip(ordered, ordered[1:]):
            if after - before > _GAP_LIMIT:
                unknown.append(f"{actor}/{session}: gap exceeds the eligible limit")
            else:
                estimated[actor].extend(_intersect(before, after, windows))

    lower = _millis(measured)
    if lower is None:
        unknown.append("no qualified measured implementation engagement")
    elif _has_unmeasured_window(measured, windows):
        unknown.append("active intervals remain without measured coverage")
    return CoverageReport(
        measured_millis=lower,
        tool_millis=_millis(tools),
        estimated_millis=_millis(estimated),
        confirmed_overrun=lower is not None and lower > state.allowance_millis,
        unknown=tuple(unknown),
    )
