"""Aggregate effective project evidence with explicit clock and coverage gaps."""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from ..types import Availability, SourceRef
from .assignments import MarkerKind, ScopeMarker
from .receipts import Role, UsageScope, require_item
from .store import EffortError, Snapshot, StoryObservation

SessionKey = tuple[str, SourceRef, SourceRef]
ClockDomain = SourceRef | str
Interval = tuple[datetime, datetime]


@dataclass(frozen=True, slots=True)
class RollupTarget:
    """Select a story, an inclusive epic, or the project's unattached pool."""

    project_id: UUID
    epic: int | None = None
    story: int | None = None

    def __post_init__(self) -> None:
        require_item(self.epic)
        require_item(self.story)

    def contains(self, row: StoryObservation) -> bool:
        return self.selects(row.story, row.epic)

    def selects(self, story: int | None, epic: int | None) -> bool:
        if self.story is not None:
            return story == self.story and (self.epic is None or self.epic == epic)
        if self.epic is not None:
            return epic == self.epic
        return story is None and epic is None


@dataclass(frozen=True, slots=True)
class WorkflowWindow:
    """An independently verified first-to-last workflow boundary on one clock."""

    clock: SourceRef
    started_at: datetime
    ended_at: datetime

    def __post_init__(self) -> None:
        start, end = self.started_at, self.ended_at
        if start.utcoffset() is None or end.utcoffset() is None:
            raise EffortError("Workflow boundaries require timezone-aware timestamps")
        start, end = start.astimezone(UTC), end.astimezone(UTC)
        if end < start:
            raise EffortError("Workflow end precedes start")
        object.__setattr__(self, "started_at", start)
        object.__setattr__(self, "ended_at", end)


@dataclass(frozen=True, slots=True)
class EffortTotals:
    observations: int
    observed_tokens: int | None
    usage_gaps: int
    inclusive_observations: int
    engaged: timedelta | None
    working_wall: timedelta | None
    workflow_elapsed: timedelta | None
    clock_gaps: int
    clock_domains: int
    boundary_gaps: int
    grok_cost_usd_ticks: int | None
    price_gaps: int


@dataclass(frozen=True, slots=True)
class EffortRollup:
    total: EffortTotals
    by_role: Mapping[Role, EffortTotals]
    by_provider: Mapping[str, EffortTotals]
    unassigned_observations: int
    unsettled_attempts: int


def _union(intervals: list[Interval]) -> timedelta:
    total = timedelta()
    end = intervals[0][0]
    for start, stop in intervals:
        if stop > end:
            total += stop - max(start, end)
            end = stop
    return total


def _totals(
    rows: list[StoryObservation],
    invalid_boundaries: set[str],
    clocks: Mapping[str, SourceRef],
    workflow: WorkflowWindow | None = None,
) -> EffortTotals:
    tokens, prices = [], []
    usage_gaps = inclusive = price_gaps = clock_gaps = boundary_gaps = 0
    sessions: dict[SessionKey, dict[ClockDomain, list[Interval]]] = defaultdict(
        lambda: defaultdict(list)
    )
    wall: dict[ClockDomain, list[Interval]] = defaultdict(list)
    for row in rows:
        receipt = row.receipt
        is_inclusive = receipt.scope == UsageScope.INCLUSIVE
        boundary_invalid = receipt.observation_id in invalid_boundaries
        boundary_gaps += boundary_invalid
        bounded = receipt.scope == UsageScope.BOUNDED and not boundary_invalid
        token_count = receipt.tokens.total_tokens if bounded else None
        price = receipt.grok_cost_usd_ticks if bounded else None
        if token_count is not None and receipt.coverage != Availability.UNKNOWN:
            tokens.append(token_count)
        if price is not None and receipt.coverage != Availability.UNKNOWN:
            prices.append(price)
        usage_gaps += token_count is None or receipt.coverage != Availability.COMPLETE
        price_gaps += price is None or receipt.coverage != Availability.COMPLETE
        inclusive += is_inclusive

        # Usage coverage and the native engagement interval are independent.
        start, end = receipt.started_at, receipt.ended_at
        timed = (bounded or is_inclusive) and not boundary_invalid
        if not timed or start is None or end is None:
            clock_gaps += 1
            continue
        session = receipt.turn.session_key
        domain = clocks.get(receipt.observation_id, receipt.observation_id)
        sessions[session][domain].append((start, end))
        wall[domain].append((start, end))

    engaged = None
    if sessions and all(len(domains) == 1 for domains in sessions.values()):
        engaged = sum(
            (
                _union(sorted(intervals))
                for domains in sessions.values()
                for intervals in domains.values()
            ),
            timedelta(),
        )
    working_wall = _union(sorted(next(iter(wall.values())))) if len(wall) == 1 else None
    workflow_elapsed = None
    if workflow is not None:
        if any(domain != workflow.clock for domain in wall):
            raise EffortError("Workflow and engagement clocks are incomparable")
        if any(
            start < workflow.started_at or end > workflow.ended_at
            for start, end in wall.get(workflow.clock, ())
        ):
            raise EffortError(
                "Workflow boundaries do not contain the engagement intervals"
            )
        workflow_elapsed = workflow.ended_at - workflow.started_at

    return EffortTotals(
        len(rows),
        sum(tokens) if tokens else None,
        usage_gaps,
        inclusive,
        engaged,
        working_wall,
        workflow_elapsed,
        clock_gaps,
        len(wall),
        boundary_gaps,
        sum(prices) if prices else None,
        price_gaps,
    )


def _invalid_boundaries(
    snapshot: Snapshot, clocks: Mapping[str, SourceRef]
) -> set[str]:
    starts: dict[str, ScopeMarker] = {}
    ends: dict[str, ScopeMarker] = {}
    for marker in snapshot.markers:
        markers = starts if marker.kind == MarkerKind.START else ends
        markers[marker.turn.identity] = marker
    invalid = set(starts) - set(ends)
    for row in snapshot.attributed:
        receipt = row.receipt
        observation = receipt.observation_id
        start, end = starts.get(observation), ends.get(observation)
        if start is None or end is None or clocks.get(observation) != start.clock:
            continue
        if any(
            timestamp is not None and not start.at <= timestamp <= end.at
            for timestamp in (receipt.started_at, receipt.ended_at)
        ):
            invalid.add(observation)
    return invalid


def rollup(
    snapshot: Snapshot,
    target: RollupTarget,
    *,
    clocks: Mapping[str, SourceRef] | None = None,
    workflow: WorkflowWindow | None = None,
) -> EffortRollup:
    """Sum known disjoint totals from a fixed project snapshot.

    A caller can attest that exact observation IDs share a clock domain.
    Each unlisted observation is comparable only with itself. Missing or
    incomparable intervals and partial usage leave gaps beside known amounts.
    """
    if target.project_id != snapshot.project_id:
        raise EffortError("Rollup target belongs to another project")
    clock_domains = clocks if clocks is not None else {}
    invalid = _invalid_boundaries(snapshot, clock_domains)

    rows = [row for row in snapshot.attributed if target.contains(row)]
    roles: dict[Role, list[StoryObservation]] = defaultdict(list)
    providers: dict[str, list[StoryObservation]] = defaultdict(list)
    for row in rows:
        roles[row.enrollment.role].append(row)
        providers[row.receipt.turn.provider].append(row)
    attempts = {row.enrollment.attempt_id for row in snapshot.attributed}
    selected_enrollments = {
        enrollment.attempt_id
        for enrollment in snapshot.enrollments
        if target.selects(enrollment.story, enrollment.epic)
    }
    unassigned = sum(
        row.enrollment.attempt_id in selected_enrollments
        and row.story is None
        and row.epic is None
        for row in snapshot.attributed
        if row.receipt.scope != UsageScope.BOUNDED
        or row.receipt.observation_id in invalid
    )
    return EffortRollup(
        _totals(rows, invalid, clock_domains, workflow),
        {role: _totals(roles[role], invalid, clock_domains) for role in sorted(roles)},
        {
            provider: _totals(providers[provider], invalid, clock_domains)
            for provider in sorted(providers)
        },
        unassigned,
        len(selected_enrollments - attempts),
    )
