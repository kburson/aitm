"""Project attributed story evidence into independent workflow timing measures."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from .attribution import Span, TimingFacts, TimingObservation, TimingScope, TimingSource
from .evidence import STATES, TOKEN, Event, PlanningTree

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_MS = timedelta(milliseconds=1)
_WAIT_KINDS = {"owner-wait", "owner-request", "owner-response", "pending-wait"}
_WORKFLOW_KINDS = {"workflow-start", "workflow-delivered"}
_GRAPH_GAPS = {
    "invalid-ancestry",
    "ancestry-missing",
    "ancestry-conflict",
    "ancestry-cycle",
}
_EVENT_GAPS = {"invalid-event", "future-event", "invalid-journal", "missing-journal"}
_WORK_ONLY_GAPS = {
    "cross-story-overlap",
    "legacy-overlap",
    "legacy-story-missing",
    "invalid-legacy-seed",
    "legacy-conflict",
    "legacy-blob",
}
_IMPLEMENTATION_STATES = {
    "develop",
    "test",
    "review",
    "rework",
    "retro",
    "blocked",
    "on-hold",
}
_OPEN_STATES = _IMPLEMENTATION_STATES | {
    "draft",
    "backlog",
    "refine",
    "ready-for-plan",
    "plan",
    "ready-for-dev",
}
_RESET_STATES = {
    "draft",
    "backlog",
    "refine",
    "ready-for-plan",
    "plan",
    "ready-for-dev",
    "cancelled",
}


@dataclass(frozen=True)
class EvidenceReference:
    path: str
    receipt_sha256: str | None = None
    source_ref: str | None = None
    source_sha256: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class DurationMeasure:
    milliseconds: int | None
    coverage: str
    evidence_through: datetime | None
    bases: tuple[str, ...]
    sources: tuple[EvidenceReference, ...]
    reasons: tuple[str, ...]
    pending: bool = False


@dataclass(frozen=True)
class WorkContribution:
    scope: TimingScope
    milliseconds: int


@dataclass(frozen=True)
class Calibration:
    eligible: bool
    estimate_source: str | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class StoryTiming:
    direct_actual: DurationMeasure
    descendant_actual: DurationMeasure
    actual: DurationMeasure
    working_wall: DurationMeasure
    direct_owner_wait: DurationMeasure
    owner_wait: DurationMeasure
    all_phase_elapsed: DurationMeasure
    implementation_elapsed: DurationMeasure
    all_phase_age: DurationMeasure
    implementation_age: DurationMeasure
    contributions: tuple[WorkContribution, ...]
    calibration: Calibration


def _millis(stamp: datetime) -> int:
    return (stamp - _EPOCH) // _MS


def _stamp(ms: int) -> datetime:
    return _EPOCH + ms * _MS


def _ref(source: TimingSource) -> EvidenceReference:
    return EvidenceReference(
        source.receipt_path,
        source.receipt_sha256,
        source.ref,
        source.source_sha256,
        source.reason,
    )


def _order_ref(source: EvidenceReference) -> tuple[str, ...]:
    return (
        source.path,
        source.receipt_sha256 or "",
        source.source_ref or "",
        source.source_sha256 or "",
        source.reason or "",
    )


@dataclass
class _Evidence:
    evidence_through: datetime | None = None
    bases: set[str] = field(default_factory=set)
    sources: set[EvidenceReference] = field(default_factory=set)
    reasons: set[str] = field(default_factory=set)
    pending: bool = False

    def advance(self, stamp: datetime | None) -> None:
        if stamp is not None and (
            self.evidence_through is None or stamp > self.evidence_through
        ):
            self.evidence_through = stamp

    def observe(self, row: TimingObservation, as_of: datetime) -> None:
        if row.coverage != "unknown" and row.evidence_through is not None:
            self.advance(min(row.evidence_through, as_of))
        self.bases.add(row.basis)
        self.sources.update(map(_ref, row.sources))
        if row.coverage != "complete":
            self.reasons.add(row.missing_reason or "incomplete-observation")

    def event(self, event: Event, basis: str) -> None:
        self.advance(event.timestamp)
        self.bases.add(basis)
        self.sources.add(EvidenceReference(event.source))

    def absorb(self, other: "_Evidence") -> None:
        self.advance(other.evidence_through)
        self.bases.update(other.bases)
        self.sources.update(other.sources)
        self.reasons.update(other.reasons)
        self.pending |= other.pending

    def measure(
        self, milliseconds: int | None, *, require_complete_zero=False
    ) -> DurationMeasure:
        if milliseconds == 0 and require_complete_zero and self.reasons:
            milliseconds = None
        coverage = (
            "unknown"
            if milliseconds is None
            else "partial"
            if self.reasons
            else "complete"
        )
        return DurationMeasure(
            milliseconds,
            coverage,
            self.evidence_through,
            tuple(sorted(self.bases)),
            tuple(sorted(self.sources, key=_order_ref)),
            tuple(sorted(self.reasons)),
            self.pending,
        )


def _union(spans: Iterable[Span]) -> list[Span]:
    merged: list[Span] = []
    for left, right in sorted(spans):
        if merged and left <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(merged[-1][1], right)
        else:
            merged.append((left, right))
    return merged


def _total(spans: Iterable[Span]) -> int:
    return sum(right - left for left, right in spans)


def _intersects(first: Span, second: Span) -> bool:
    return first[0] < second[1] and second[0] < first[1]


def _subtract(span: Span, cuts: Iterable[Span]) -> Iterable[Span]:
    cursor, end = span
    for left, right in _union(cuts):
        if cursor < left:
            yield cursor, left
        cursor = max(cursor, right)
    if cursor < end:
        yield cursor, end


def _bounded(row: TimingObservation, cutoff: int) -> Span | None:
    if (
        row.coverage != "unknown"
        and row.start_ms is not None
        and row.end_ms is not None
    ):
        end = min(row.end_ms, cutoff)
        if row.start_ms < end:
            return row.start_ms, end
    return None


def _boundary(row: TimingObservation, cutoff: int) -> int | None:
    bounds = {bound for bound in (row.start_ms, row.end_ms) if bound is not None}
    if row.coverage != "unknown" and len(bounds) == 1:
        (bound,) = bounds
        if bound <= cutoff:
            return bound
    return None


def _exclusion_matches(exclusion: TimingScope, work: TimingScope) -> bool | None:
    pairs = (
        (exclusion.phase, work.phase),
        (exclusion.role, work.role),
        (exclusion.attempt, work.attempt),
    )
    if any(
        cut is not None and active is not None and cut != active
        for cut, active in pairs
    ):
        return False
    if any(cut is not None and active is None for cut, active in pairs):
        return None
    return True


def _scope_order(scope: TimingScope) -> tuple[int, str, str, str, str, str]:
    return (
        scope.story,
        scope.project or "",
        scope.actor,
        scope.phase or "",
        scope.role or "",
        scope.attempt or "",
    )


def _agreed_scope(scopes: Iterable[TimingScope]) -> TimingScope:
    first, *rest = scopes
    phase, role, attempt = first.phase, first.role, first.attempt
    for scope in rest:
        if scope.phase != phase:
            phase = None
        if scope.role != role:
            role = None
        if scope.attempt != attempt:
            attempt = None
    return TimingScope(first.story, first.project, first.actor, phase, role, attempt)


@dataclass
class _Wait:
    spans: list[Span] = field(default_factory=list)
    exclusions: list[tuple[TimingScope, Span, tuple[TimingObservation, ...]]] = field(
        default_factory=list
    )
    evidence: _Evidence = field(default_factory=_Evidence)
    uncertain: list[TimingObservation] = field(default_factory=list)
    measured: bool = False

    def add(
        self, scope: TimingScope, span: Span, rows: tuple[TimingObservation, ...]
    ) -> None:
        self.measured = True
        if span[0] < span[1]:
            self.spans.append(span)
            self.exclusions.append((scope, span, rows))

    def hold(self, rows: Iterable[TimingObservation], reason: str) -> None:
        self.uncertain.extend(rows)
        self.evidence.reasons.add(reason)


def _request_scope(rows: tuple[TimingObservation, ...]) -> TimingScope | None:
    fields = ("phase", "role", "attempt")
    dimensions = [
        {getattr(row.scope, name) for row in rows} - {None} for name in fields
    ]
    if any(len(values) > 1 for values in dimensions):
        return None
    first = rows[0].scope
    return TimingScope(
        first.story,
        first.project,
        first.actor,
        *(next(iter(values), None) for values in dimensions),
    )


def _request_wait(
    wait: _Wait,
    rows: list[TimingObservation],
    as_of: datetime,
) -> None:
    cutoff = _millis(as_of)
    requests = [row for row in rows if row.kind == "owner-request"]
    responses = [row for row in rows if row.kind == "owner-response"]
    confirmations = [row for row in rows if row.kind == "pending-wait"]
    # Once there is a response, the request and response carry the effective
    # evidence. Older pending observations cannot make a closed wait pending.
    effective = tuple(requests + responses if requests and responses else rows)
    for row in effective:
        wait.evidence.observe(row, as_of)
    scope = _request_scope(effective)
    if scope is None:
        wait.hold(effective, "owner-request-scope-conflict")
        return

    starts = {_boundary(row, cutoff) for row in requests}
    starts.update(
        row.start_ms
        for row in confirmations
        if row.coverage != "unknown" and row.start_ms is not None
    )
    if None in starts or len(starts) != 1:
        wait.evidence.pending |= bool(confirmations and not responses)
        wait.hold(effective, "unresolved-owner-request")
        return

    (start,) = starts
    if responses:
        ends = {_boundary(row, cutoff) for row in responses}
        if None in ends or len(ends) != 1 or min(ends) < start:
            wait.hold(effective, "unresolved-owner-response")
            return
        (end,) = ends
        wait.add(scope, (start, end), effective)
        return

    if not confirmations:
        wait.hold(effective, "missing-owner-response")
        return

    wait.evidence.pending = True
    wait.evidence.reasons.add("pending-owner-response")
    positive = [row for row in confirmations if row.coverage != "unknown"]
    checkpoints = [
        _millis(source.checkpoint_at)
        for row in positive
        for source in row.sources
        if source.checkpoint_at is not None
    ]
    checkpoints.extend(row.end_ms for row in positive if row.end_ms is not None)
    if not checkpoints or min(max(checkpoints), cutoff) < start:
        wait.hold(effective, "missing-pending-checkpoint")
        return
    end = min(max(checkpoints), cutoff)
    wait.add(scope, (start, end), effective)


def _owner_wait(rows: list[TimingObservation], as_of: datetime) -> _Wait:
    wait = _Wait()
    cutoff = _millis(as_of)
    groups = defaultdict(list)
    for row in rows:
        if row.kind not in _WAIT_KINDS:
            continue
        if row.kind == "owner-wait":
            wait.evidence.observe(row, as_of)
            span = _bounded(row, cutoff)
            if span is None:
                wait.hold((row,), "missing-owner-wait-boundary")
            else:
                wait.add(row.scope, span, (row,))
        elif row.turn is not None or row.kind == "pending-wait":
            # A standalone pending confirmation may prove its own request start.
            groups[row.scope.actor_key, row.turn or row.identity].append(row)
        else:
            wait.evidence.observe(row, as_of)
            wait.hold((row,), "unbound-owner-request")
    for group in groups.values():
        _request_wait(wait, group, as_of)
    if not wait.measured:
        wait.evidence.reasons.add("missing-owner-wait-evidence")
    return wait


@dataclass
class _Work:
    spans: list[Span] = field(default_factory=list)
    contributions: dict[TimingScope, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    evidence: _Evidence = field(default_factory=_Evidence)
    measured: bool = False
    basis: set[str] = field(default_factory=set)

    def add(self, span: Span, scopes: Iterable[TimingScope]) -> None:
        self.spans.append(span)
        self.contributions[_agreed_scope(scopes)] += span[1] - span[0]


def _may_overlap(row: TimingObservation, span: Span, cutoff: int) -> bool:
    start, end = row.start_ms, row.end_ms
    if row.kind == "owner-request":
        start, end = _boundary(row, cutoff), None
    elif row.kind == "owner-response":
        start, end = None, _boundary(row, cutoff)
    return (end is None or end > span[0]) and (start is None or start < span[1])


def _fold_actor(
    work: _Work,
    rows: list[TimingObservation],
    exclusions: list[tuple[TimingScope, Span, tuple[TimingObservation, ...]]],
    uncertain: list[TimingObservation],
    as_of: datetime,
) -> None:
    cutoff = _millis(as_of)
    changes = defaultdict(list)
    turns = defaultdict(list)
    for index, row in enumerate(rows):
        if row.kind != "agent-turn":
            continue
        work.evidence.observe(row, as_of)
        span = _bounded(row, cutoff)
        if span is None:
            work.evidence.reasons.add("missing-turn-boundary")
            continue
        work.measured = True
        for missing in uncertain:
            if _exclusion_matches(
                missing.scope, row.scope
            ) is not False and _may_overlap(missing, span, cutoff):
                work.evidence.observe(missing, as_of)
                work.evidence.reasons.add("unresolved-work-exclusion")
        cuts = []
        for scope, cut, sources in exclusions:
            if not _intersects(span, cut):
                continue
            matches = _exclusion_matches(scope, row.scope)
            if matches is False:
                continue
            for source in sources:
                work.evidence.observe(source, as_of)
                if source.kind == "pending-wait":
                    work.evidence.reasons.add("pending-owner-response")
            if matches is None:
                work.evidence.reasons.add("unresolved-work-exclusion-scope")
            else:
                cuts.append((max(span[0], cut[0]), min(span[1], cut[1])))
        for left, right in _subtract(span, cuts):
            work.basis.add(row.basis)
            changes[left].append((index, True))
            changes[right].append((index, False))
            turns[row.turn, row.scope].append((left, right))

    active: dict[int, TimingScope] = {}
    previous = None
    for point, delta in sorted(changes.items()):
        if active:
            work.add((previous, point), active.values())
        for index, starts in delta:
            if starts:
                active[index] = rows[index].scope
            else:
                del active[index]
        previous = point

    for row in rows:
        if row.kind != "tool" or row.turn is None:
            continue
        span = _bounded(row, cutoff)
        if span is None:
            continue
        through = max(
            (
                min(span[1], turn[1])
                for turn in turns[row.turn, row.scope]
                if _intersects(span, turn)
            ),
            default=None,
        )
        if through is not None:
            work.evidence.observe(row, _stamp(through))


def _working(rows: list[TimingObservation], wait: _Wait, as_of: datetime) -> _Work:
    work = _Work()
    actors = defaultdict(list)
    exclusions, uncertain = defaultdict(list), defaultdict(list)
    for row in wait.uncertain:
        uncertain[row.scope.actor_key].append(row)
    for scope, span, sources in wait.exclusions:
        exclusions[scope.actor_key].append((scope, span, sources))
    for row in rows:
        if row.kind in {"agent-turn", "tool"}:
            actors[row.scope.actor_key].append(row)
        elif row.kind == "idle":
            span = _bounded(row, _millis(as_of))
            if span is not None:
                exclusions[row.scope.actor_key].append((row.scope, span, (row,)))
            else:
                uncertain[row.scope.actor_key].append(row)
    for actor, actor_rows in actors.items():
        _fold_actor(work, actor_rows, exclusions[actor], uncertain[actor], as_of)
    if not work.measured:
        work.evidence.reasons.add("missing-work-evidence")
    return work


@dataclass(frozen=True)
class _Mark:
    ms: int
    attempt: str | None
    evidence: _Evidence


def _event_mark(event: Event, basis: str) -> _Mark:
    raw_attempt = event.data.get("attempt")
    attempt = str(raw_attempt) if type(raw_attempt) in {str, int} else None
    evidence = _Evidence()
    evidence.event(event, basis)
    return _Mark(_millis(event.timestamp), attempt, evidence)


def _workflow_marks(
    rows: list[TimingObservation],
    phase: str,
    as_of: datetime,
) -> tuple[list[_Mark], list[_Mark], _Evidence]:
    starts, finishes = [], []
    unproved = _Evidence()
    for row in rows:
        if row.kind not in _WORKFLOW_KINDS or row.scope.phase != phase:
            continue
        bound = _boundary(row, _millis(as_of))
        evidence = _Evidence()
        evidence.observe(row, as_of)
        if bound is None:
            evidence.reasons.add("missing-workflow-boundary")
            unproved.absorb(evidence)
            continue
        mark = _Mark(bound, row.scope.attempt, evidence)
        (starts if row.kind == "workflow-start" else finishes).append(mark)
    return (
        sorted(starts, key=lambda mark: mark.ms),
        sorted(finishes, key=lambda mark: mark.ms),
        unproved,
    )


def _state_marks(
    events: list[Event],
) -> tuple[_Mark | None, _Mark | None, int | None, int | None]:
    start = done = None
    reopened = reset = None
    for event in events:
        if event.kind != "core.state.entered":
            continue
        state = event.data.get("state")
        if not isinstance(state, str) or state not in STATES:
            continue
        if done is not None and state != "done":
            reopened = reset = _millis(event.timestamp)
            start = done = None
        if state in _RESET_STATES:
            reset = _millis(event.timestamp)
            start = None
        elif state == "develop":
            mark = _event_mark(event, "workflow-develop")
            if (
                start is None
                or mark.attempt is not None
                and mark.attempt != start.attempt
            ):
                start = mark
        elif state == "done" and done is None:
            done = _event_mark(event, "workflow-done")
    return start, done, reopened, reset


def _elapsed_pair(
    start: _Mark | None,
    finish: _Mark | None,
    open_scope: bool,
    as_of: datetime,
    evidence: _Evidence,
    *,
    check_attempt=False,
) -> tuple[DurationMeasure, DurationMeasure]:
    elapsed, age = _Evidence(), _Evidence()
    elapsed.absorb(evidence)
    age.absorb(evidence)
    if start is not None:
        elapsed.absorb(start.evidence)
        age.absorb(start.evidence)
    if finish is not None:
        elapsed.absorb(finish.evidence)
    value = age_value = None
    if start is None:
        elapsed.reasons.add("missing-elapsed-start")
        age.reasons.add("missing-elapsed-start")
    elif finish is not None:
        if finish.ms < start.ms or check_attempt and start.attempt != finish.attempt:
            elapsed.reasons.add("incompatible-elapsed-boundaries")
        else:
            value = finish.ms - start.ms
    elif open_scope:
        age_value = _millis(as_of) - start.ms
        elapsed.reasons.add("open-elapsed-scope")
    else:
        elapsed.reasons.add("missing-elapsed-finish")
    return elapsed.measure(value), age.measure(age_value)


@dataclass(frozen=True)
class _Workflow:
    all_phase_elapsed: DurationMeasure
    implementation_elapsed: DurationMeasure
    all_phase_age: DurationMeasure
    implementation_age: DurationMeasure
    completed_attempt: tuple[_Mark, _Mark] | None


def _coalesce_marks(
    marks: list[_Mark],
    evidence: _Evidence,
    conflict_reason: str,
) -> tuple[_Mark | None, bool]:
    if not marks:
        return None, False
    merged = _Evidence()
    for mark in marks:
        merged.absorb(mark.evidence)
    if len({mark.ms for mark in marks}) > 1:
        evidence.absorb(merged)
        evidence.reasons.add(conflict_reason)
        return None, True
    return _Mark(marks[0].ms, marks[0].attempt, merged), False


def _implementation_marks(
    develop: _Mark | None,
    done: _Mark | None,
    starts: list[_Mark],
    finishes: list[_Mark],
    open_scope: bool,
    evidence: _Evidence,
) -> tuple[_Mark | None, _Mark | None, bool]:
    explicit_start = starts[-1] if starts else None
    if explicit_start is not None and (
        develop is None
        or explicit_start.ms >= develop.ms
        and explicit_start.attempt != develop.attempt
    ):
        develop, conflict = _coalesce_marks(
            [mark for mark in starts if mark.attempt == explicit_start.attempt],
            evidence,
            "conflicting-implementation-start",
        )
        if conflict:
            return None, None, True
    if develop is None:
        return None, done or (finishes[-1] if finishes else None), False

    finish, conflict = _coalesce_marks(
        [
            mark
            for mark in finishes
            if mark.ms >= develop.ms and mark.attempt == develop.attempt
        ],
        evidence,
        "conflicting-implementation-finish",
    )
    if conflict:
        return develop, None, True
    if done is not None and done.ms >= develop.ms and done.attempt == develop.attempt:
        return develop, done, False
    if finish is not None or open_scope:
        return develop, finish, False
    return develop, done or (finishes[-1] if finishes else None), False


def _workflow(
    story: int,
    rows: list[TimingObservation],
    events: list[Event],
    tree: PlanningTree,
    event_gaps: _Evidence,
) -> _Workflow:
    state = tree.stories[story].state
    develop, done, reopened, reset = _state_marks(events)
    all_starts, all_finishes, all_gaps = _workflow_marks(rows, "all-phase", tree.as_of)
    impl_starts, impl_finishes, impl_gaps = _workflow_marks(
        rows, "implement", tree.as_of
    )
    all_gaps.absorb(event_gaps)
    impl_gaps.absorb(event_gaps)

    all_finishes.extend(
        _event_mark(event, "workflow-delivery-verified")
        for event in events
        if event.kind == "core.delivery.verified"
    )
    if reopened is not None:
        all_finishes = [mark for mark in all_finishes if mark.ms >= reopened]
    if reset is not None:
        impl_starts = [mark for mark in impl_starts if mark.ms > reset]
        impl_finishes = [mark for mark in impl_finishes if mark.ms > reset]
    all_elapsed, all_age = _elapsed_pair(
        all_starts[0] if all_starts else None,
        max(all_finishes, key=lambda mark: mark.ms, default=done),
        state in _OPEN_STATES,
        tree.as_of,
        all_gaps,
    )
    implementation_open = state in _IMPLEMENTATION_STATES
    develop, done, conflict = _implementation_marks(
        develop, done, impl_starts, impl_finishes, implementation_open, impl_gaps
    )
    impl_elapsed, impl_age = _elapsed_pair(
        develop,
        done,
        implementation_open and not conflict,
        tree.as_of,
        impl_gaps,
        check_attempt=True,
    )
    completed_attempt = (
        (develop, done)
        if develop is not None
        and done is not None
        and impl_elapsed.coverage == "complete"
        else None
    )
    return _Workflow(all_elapsed, impl_elapsed, all_age, impl_age, completed_attempt)


def _calibration(
    story: int,
    tree: PlanningTree,
    events: list[Event],
    work: _Work,
    actual: DurationMeasure,
    completed_attempt: tuple[_Mark, _Mark] | None,
    *,
    has_descendants: bool,
) -> Calibration:
    estimate = tree.estimates.get(story)
    reasons = set()
    if estimate is None or estimate.agent_hours is None:
        reasons.add("missing-estimate")
    if actual.coverage != "complete":
        reasons.add("incomplete-actual")
    if has_descendants:
        reasons.add("estimate-ancestry-scope-unproved")
    if estimate is None or not work.contributions:
        return Calibration(
            False,
            estimate.source if estimate is not None else None,
            tuple(sorted(reasons or {"missing-actual-scope"})),
        )

    scopes = work.contributions
    if estimate.phase is None or {scope.phase for scope in scopes} != {estimate.phase}:
        reasons.add("estimate-phase-mismatch")
    if estimate.roles is None or {scope.role for scope in scopes} != set(
        estimate.roles
    ):
        reasons.add("estimate-role-mismatch")

    source = next(
        (
            event
            for event in events
            if event.kind == "core.estimate.set" and event.source == estimate.source
        ),
        None,
    )
    work_start = min(start for start, _ in work.spans)
    work_end = max(end for _, end in work.spans)
    if source is None or _millis(source.timestamp) > work_start:
        reasons.add("estimate-revision-unproved")
    scope = source.data.get("scope") if source is not None else None
    scope = scope if isinstance(scope, dict) else {}
    actors, attempt, basis = (
        scope.get("actors"),
        scope.get("attempt"),
        scope.get("basis"),
    )
    if (
        not isinstance(actors, list)
        or not all(
            isinstance(actor, str) and TOKEN.fullmatch(actor) for actor in actors
        )
        or set(actors) != {scope.actor for scope in scopes}
        or len({scope.project for scope in scopes}) != 1
    ):
        reasons.add("estimate-actor-scope-unproved")
    if not isinstance(attempt, str) or {scope.attempt for scope in scopes} != {attempt}:
        reasons.add("estimate-attempt-scope-unproved")
    if completed_attempt is None:
        reasons.add("completed-attempt-unproved")
    else:
        start, finish = completed_attempt
        if (
            start.attempt != attempt
            or not start.ms <= work_start <= work_end <= finish.ms
        ):
            reasons.add("actual-outside-estimate-attempt")
    if not isinstance(basis, str) or work.basis != {basis}:
        reasons.add("estimate-basis-unproved")
    return Calibration(not reasons, estimate.source, tuple(sorted(reasons)))


@dataclass
class _Direct:
    work: _Work
    wait: _Wait
    workflow: _Workflow


def _usage_sources(tree: PlanningTree) -> set[str]:
    timing_kind, usage_kind = "story-timing-receipt", "story-usage-receipt"
    kinds_by_path = defaultdict(set)
    source_paths = {}
    for event in tree.events:
        if event.kind != "core.evidence.recorded":
            continue
        kind = event.data.get("kind")
        if kind not in (timing_kind, usage_kind):
            continue
        path = event.data.get("path")
        if isinstance(path, str) and event.story in tree.stories:
            root = tree.stories[event.story].path.rsplit("/", 1)[0]
            full_path = f"{root}/{path}"
        else:
            full_path = event.source
        kinds_by_path[full_path].add(kind)
        source_paths[event.source] = full_path
    usage_paths = {
        path for path, kinds in kinds_by_path.items() if kinds == {usage_kind}
    }
    return usage_paths | {
        source for source, path in source_paths.items() if path in usage_paths
    }


def _gap_evidence(
    tree: PlanningTree, facts: TimingFacts
) -> tuple[dict, dict, dict, dict]:
    work, wait, workflow, graph = (defaultdict(_Evidence) for _ in range(4))
    kinds = {(row.scope.story, row.identity): row.kind for row in facts.observations}
    usage_sources = _usage_sources(tree)
    for gap in facts.input_gaps:
        if gap.source in usage_sources:
            continue
        if gap.code in _GRAPH_GAPS:
            targets = (graph,)
        elif gap.code in _WORK_ONLY_GAPS:
            targets = (work,)
        elif gap.code in _EVENT_GAPS:
            targets = (work, wait, workflow)
        elif gap.code in {"invalid-state", "unbound-draft-event"}:
            targets = (workflow,)
        elif "receipt" in gap.code or "registration" in gap.code:
            targets = (work, wait, workflow)
        else:
            targets = ()
        for target in targets:
            target[gap.story].reasons.add(gap.code)
            target[gap.story].sources.add(EvidenceReference(gap.source))
    for gap in facts.gaps:
        kind = kinds.get((gap.story, gap.identity))
        if gap.code in _WORK_ONLY_GAPS:
            targets = (work,)
        elif kind in _WAIT_KINDS:
            targets = (wait,)
        elif kind in _WORKFLOW_KINDS:
            targets = (workflow,)
        elif kind is None or kind == "missing":
            targets = (work, wait, workflow)
        else:
            targets = (work,)
        for target in targets:
            target[gap.story].reasons.add(gap.code)
            target[gap.story].sources.update(map(_ref, gap.sources))
    return work, wait, workflow, graph


def _aggregate_work(
    direct: dict[int, _Direct],
    ids: tuple[int, ...],
    graph: _Evidence,
) -> tuple[int | None, int | None, _Evidence, tuple[WorkContribution, ...]]:
    evidence = _Evidence()
    evidence.absorb(graph)
    spans, contributions = [], {}
    measured = False
    for story in ids:
        if story not in direct:
            evidence.reasons.add("unmeasured-descendant")
            continue
        work = direct[story].work
        evidence.absorb(work.evidence)
        measured |= work.measured
        spans.extend(work.spans)
        contributions.update(work.contributions)
    return (
        sum(contributions.values()) if measured else None,
        _total(_union(spans)) if measured else None,
        evidence,
        tuple(
            WorkContribution(scope, contributions[scope])
            for scope in sorted(contributions, key=_scope_order)
        ),
    )


def _aggregate_wait(
    direct: dict[int, _Direct],
    ids: tuple[int, ...],
    graph: _Evidence,
) -> DurationMeasure:
    evidence = _Evidence()
    evidence.absorb(graph)
    spans = []
    measured = False
    for story in ids:
        if story not in direct:
            evidence.reasons.add("unmeasured-descendant")
            continue
        wait = direct[story].wait
        evidence.absorb(wait.evidence)
        measured |= wait.measured
        spans.extend(wait.spans)
    return evidence.measure(
        _total(_union(spans)) if measured else None, require_complete_zero=True
    )


def project_timing(tree: PlanningTree, facts: TimingFacts) -> dict[int, StoryTiming]:
    """Calculate effort, wait, wall time, and workflow clocks at the fixed cutoff."""
    by_story, events = defaultdict(list), defaultdict(list)
    for row in facts.observations:
        by_story[row.scope.story].append(row)
    for event in tree.events:
        events[event.story].append(event)
    work_gaps, wait_gaps, workflow_gaps, graph_gaps = _gap_evidence(tree, facts)
    direct = {}
    for story in sorted(tree.stories):
        rows = by_story[story]
        wait = _owner_wait(rows, tree.as_of)
        work = _working(rows, wait, tree.as_of)
        wait.evidence.absorb(wait_gaps[story])
        work.evidence.absorb(work_gaps[story])
        workflow = _workflow(story, rows, events[story], tree, workflow_gaps[story])
        direct[story] = _Direct(work, wait, workflow)

    results = {}
    for story, row in direct.items():
        children = tuple(sorted(set(tree.descendants.get(story, ())) - {story}))
        ids = (story, *children)
        ancestry = _Evidence()
        for member in ids:
            ancestry.absorb(graph_gaps[member])
        graph = _Evidence()
        graph.absorb(ancestry)
        if any(
            child not in direct or not direct[child].work.measured for child in children
        ):
            graph.reasons.add("unmeasured-descendant")
        legacy = facts.legacy_readback.get(story)
        if legacy is not None and tuple(
            child for child in children if child in facts.legacy_readback
        ) != tuple(sorted(legacy.counted_children)):
            graph.reasons.add("legacy-descendants-changed")
            graph.sources.update(row.work.evidence.sources)
        direct_value = (
            sum(row.work.contributions.values()) if row.work.measured else None
        )
        actual, wall, evidence, contributions = _aggregate_work(direct, ids, graph)
        child_value, _, child_evidence, _ = _aggregate_work(direct, children, graph)
        result_actual = evidence.measure(actual)
        results[story] = StoryTiming(
            direct_actual=row.work.evidence.measure(direct_value),
            descendant_actual=child_evidence.measure(child_value),
            actual=result_actual,
            working_wall=evidence.measure(wall),
            direct_owner_wait=_aggregate_wait(direct, (story,), _Evidence()),
            owner_wait=_aggregate_wait(direct, ids, ancestry),
            all_phase_elapsed=row.workflow.all_phase_elapsed,
            implementation_elapsed=row.workflow.implementation_elapsed,
            all_phase_age=row.workflow.all_phase_age,
            implementation_age=row.workflow.implementation_age,
            contributions=contributions,
            calibration=_calibration(
                story,
                tree,
                events[story],
                row.work,
                result_actual,
                row.workflow.completed_attempt,
                has_descendants=bool(children),
            ),
        )
    return results
