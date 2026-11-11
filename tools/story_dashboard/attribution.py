"""Attribute admitted timing evidence before projecting story metrics."""

import hashlib
import json
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta

from .evidence import (
    LEGACY_PATH,
    LEGACY_SHA256,
    TIMING_SCHEMA,
    Gap,
    PlanningTree,
    Receipt,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_MILLISECOND = timedelta(milliseconds=1)
_BOUNDARY_KINDS = {
    "owner-request",
    "owner-response",
    "workflow-start",
    "workflow-delivered",
}
Identity = tuple[str, ...]
Span = tuple[int, int]


@dataclass(frozen=True)
class TimingScope:
    story: int
    project: str | None
    actor: str
    phase: str | None = None
    role: str | None = None
    attempt: str | None = None

    @property
    def actor_key(self) -> tuple[str | None, str]:
        """Legacy and current actor identifiers are in separate namespaces."""
        return self.project, self.actor


@dataclass(frozen=True)
class TimingSource:
    receipt_path: str
    receipt_sha256: str
    ref: str | None = None
    source_sha256: str | None = None
    recorded_at: datetime | None = None
    checkpoint_at: datetime | None = None
    reason: str | None = None


@dataclass(frozen=True)
class TimingObservation:
    identity: Identity
    scope: TimingScope
    kind: str
    start_ms: int | None
    end_ms: int | None
    turn: str | None
    coverage: str
    basis: str
    missing_reason: str | None
    sources: tuple[TimingSource, ...]

    @property
    def recorded_at(self) -> datetime | None:
        return min(
            (s.recorded_at for s in self.sources if s.recorded_at is not None),
            default=None,
        )

    @property
    def evidence_through(self) -> datetime | None:
        bounds = [
            _EPOCH + ms * _MILLISECOND
            for ms in (self.start_ms, self.end_ms)
            if ms is not None
        ]
        checkpoints = [
            s.checkpoint_at for s in self.sources if s.checkpoint_at is not None
        ]
        return max(bounds + checkpoints, default=None)


@dataclass(frozen=True)
class TimingGap:
    story: int
    code: str
    scope: TimingScope | None = None
    identity: Identity = ()
    start_ms: int | None = None
    end_ms: int | None = None
    sources: tuple[TimingSource, ...] = ()


@dataclass(frozen=True)
class ScopeEvidence:
    """Coverage of supplied observations in this scope, not lifecycle completeness."""

    coverage: str
    evidence_through: datetime | None
    bases: tuple[str, ...]


@dataclass(frozen=True)
class LegacyReadback:
    """Historical verification targets, never contributions."""

    direct_ms: int
    inclusive_ms: int
    counted_children: tuple[int, ...]
    evidence_through: datetime


@dataclass(frozen=True)
class TimingFacts:
    observations: tuple[TimingObservation, ...]
    gaps: tuple[TimingGap, ...]
    scopes: dict[TimingScope, ScopeEvidence]
    legacy_readback: dict[int, LegacyReadback]
    input_gaps: tuple[Gap, ...]


def _milliseconds(value: str | None) -> int | None:
    if value is None:
        return None
    return (datetime.fromisoformat(value) - _EPOCH) // _MILLISECOND


def _v1(receipt: Receipt, story_path: str) -> list[TimingObservation]:
    claim = receipt.registration
    result = []
    for row in receipt.observations:
        recording = row.get("recorded_at_utc")
        recorded_at = (
            datetime.fromisoformat(recording) if recording else receipt.recorded_at
        )
        source = row.get("source", receipt.source)
        result.append(
            TimingObservation(
                ("v1", claim.project, row["observation_id"]),
                TimingScope(
                    claim.story,
                    claim.project,
                    row["actor"],
                    row["phase"],
                    row["role"],
                    row.get("attempt"),
                ),
                row["kind"],
                _milliseconds(row["start_utc"]),
                _milliseconds(row["end_utc"]),
                row.get("turn"),
                row["coverage"],
                row["basis"],
                row.get("missing_reason"),
                (
                    TimingSource(
                        f"{story_path.rsplit('/', 1)[0]}/{claim.path}",
                        claim.sha256,
                        source.get("ref"),
                        source.get("sha256"),
                        recorded_at,
                        recorded_at
                        if recording and row["kind"] == "pending-wait"
                        else None,
                    ),
                ),
            )
        )
    return result


def _legacy_stamp(value: str) -> datetime:
    stamp = datetime.fromisoformat(value)
    if stamp.utcoffset() != timedelta(0):
        raise ValueError("legacy timestamp is not UTC")
    return stamp.astimezone(UTC)


def _legacy(
    tree: PlanningTree,
) -> tuple[list[TimingObservation], dict[int, LegacyReadback], list[TimingGap]]:
    if tree.legacy_seed is None:
        return [], {}, []
    source_path = f".aitm/stories/001/181/{LEGACY_PATH}"
    try:
        if hashlib.sha256(tree.legacy_seed).hexdigest() != LEGACY_SHA256:
            raise ValueError("legacy digest mismatch")
        seed = json.loads(tree.legacy_seed)
        if seed["schema"] != "aitm.story-actual-backfill/v0" or seed["story"] != 181:
            raise ValueError("unsupported legacy timing format")
        watermark = _legacy_stamp(seed["evidence_through_utc"])
        if watermark > tree.as_of:
            raise ValueError("legacy timing watermark exceeds cutoff")
        observations, readback, gaps = [], {}, []
        for story_key, entry in seed["entries"].items():
            story = int(story_key)
            if story <= 0 or str(story) != story_key or entry["coverage"] != "Partial":
                raise ValueError("invalid legacy story or coverage")
            if story not in tree.stories:
                gaps.append(TimingGap(story, "legacy-story-missing"))
                continue
            readback[story] = LegacyReadback(
                entry["direct"]["milliseconds"],
                entry["milliseconds"],
                tuple(entry["counted_children"]),
                watermark,
            )
            for row in entry["direct_intervals"]:
                start, end = _legacy_stamp(row["start"]), _legacy_stamp(row["end"])
                if not start < end <= watermark or any(
                    t.microsecond % 1000 for t in (start, end)
                ):
                    raise ValueError("invalid legacy timing bounds")
                left, right = (
                    (start - _EPOCH) // _MILLISECOND,
                    (end - _EPOCH) // _MILLISECOND,
                )
                if right - left != row["milliseconds"]:
                    raise ValueError("legacy interval duration disagrees")
                actor, turn = row["actor"], row["turn"]
                if not all(
                    isinstance(row[key], str) and row[key]
                    for key in ("actor", "turn", "source", "reason")
                ):
                    raise ValueError("missing legacy attribution or provenance")
                observations.append(
                    TimingObservation(
                        ("legacy", actor, turn, str(left), str(right)),
                        TimingScope(story, None, actor),
                        "agent-turn",
                        left,
                        right,
                        turn,
                        "partial",
                        row["source"],
                        None,
                        (
                            TimingSource(
                                source_path,
                                LEGACY_SHA256,
                                checkpoint_at=watermark,
                                reason=row["reason"],
                            ),
                        ),
                    )
                )
        return observations, dict(sorted(readback.items())), gaps
    except (AttributeError, KeyError, TypeError, ValueError, RecursionError):
        return (
            [],
            {},
            [
                TimingGap(
                    181,
                    "invalid-legacy-seed",
                    sources=(TimingSource(source_path, LEGACY_SHA256),),
                )
            ],
        )


def _source_order(source: TimingSource) -> tuple:
    return (
        source.receipt_path,
        source.receipt_sha256,
        source.ref or "",
        source.source_sha256 or "",
        source.recorded_at or _EPOCH,
        source.checkpoint_at or _EPOCH,
        source.reason or "",
    )


def _scope_order(scope: TimingScope) -> tuple:
    return (
        scope.story,
        scope.project or "",
        scope.actor,
        scope.phase or "",
        scope.role or "",
        scope.attempt or "",
    )


def _observation_order(observation: TimingObservation) -> tuple:
    return (
        _scope_order(observation.scope),
        observation.identity,
        observation.start_ms if observation.start_ms is not None else float("-inf"),
        observation.end_ms if observation.end_ms is not None else float("-inf"),
    )


def _gap(
    observation: TimingObservation, code: str, span: Span | None = None
) -> TimingGap:
    start, end = (
        span if span is not None else (observation.start_ms, observation.end_ms)
    )
    return TimingGap(
        observation.scope.story,
        code,
        observation.scope,
        observation.identity,
        start,
        end,
        observation.sources,
    )


def _admit_v1(tree: PlanningTree) -> tuple[list[TimingObservation], list[TimingGap]]:
    receipts = [receipt for receipt in tree.receipts if receipt.schema == TIMING_SCHEMA]
    held = set()
    for receipt in receipts:
        if receipt.supersedes is not None:
            claim = receipt.registration
            held.add((claim.project, claim.story, claim.sha256))
            held.add((claim.project, claim.story, receipt.supersedes))
    rows = []
    held_assignments = set()
    for receipt in receipts:
        claim = receipt.registration
        normalized = _v1(receipt, tree.stories[claim.story].path)
        rows.extend(normalized)
        if (claim.project, claim.story, claim.sha256) in held:
            held_assignments.update(
                (row.scope.story, row.identity) for row in normalized
            )

    observations, gaps = [], []
    for row in rows:
        if (row.scope.story, row.identity) in held_assignments:
            gaps.append(_gap(row, "unsupported-revision"))
        else:
            observations.append(row)
    return observations, gaps


def _resolve_identity(
    claims: list[TimingObservation],
) -> tuple[list[TimingObservation], list[TimingObservation], list[TimingGap]]:
    by_identity = defaultdict(lambda: defaultdict(set))
    for claim in claims:
        by_identity[claim.identity][replace(claim, sources=())].update(claim.sources)
    admitted, held, gaps = [], [], []
    for signatures in by_identity.values():
        variants = [
            replace(row, sources=tuple(sorted(sources, key=_source_order)))
            for row, sources in signatures.items()
        ]
        if len(variants) == 1:
            admitted.extend(variants)
            continue
        held.extend(variants)
        by_scope = defaultdict(set)
        for row in variants:
            by_scope[row.scope].update(row.sources)
        for scope, sources in by_scope.items():
            gaps.append(
                TimingGap(
                    scope.story,
                    "identity-conflict",
                    scope,
                    variants[0].identity,
                    sources=tuple(sorted(sources, key=_source_order)),
                )
            )
    return admitted, held, gaps


def _overlap_windows(spans: list[tuple[int, int, int]]) -> list[Span]:
    changes = defaultdict(Counter)
    for start, end, participant in spans:
        changes[start][participant] += 1
        changes[end][participant] -= 1
    active = Counter()
    windows = []
    previous = None
    for point, delta in sorted(changes.items()):
        if previous is not None and len(active) >= 2:
            if windows and windows[-1][1] == previous:
                windows[-1] = (windows[-1][0], point)
            else:
                windows.append((previous, point))
        for participant, count in delta.items():
            active[participant] += count
            if not active[participant]:
                del active[participant]
        previous = point
    return windows


def _positive_turn(row: TimingObservation) -> bool:
    return (
        row.kind == "agent-turn" and row.start_ms is not None and row.end_ms is not None
    )


def _conflict_windows(observations: list[TimingObservation]) -> tuple[dict, dict]:
    actor_spans, story_spans = defaultdict(list), defaultdict(list)
    for row in observations:
        if _positive_turn(row):
            actor_spans[row.scope.actor_key].append(
                (row.start_ms, row.end_ms, row.scope.story)
            )
            story_spans[row.scope.story].append(
                (row.start_ms, row.end_ms, int(row.scope.project is None))
            )
    return (
        {actor: _overlap_windows(spans) for actor, spans in actor_spans.items()},
        {story: _overlap_windows(spans) for story, spans in story_spans.items()},
    )


def _intersections(start: int, end: int, windows: list[Span]) -> list[Span]:
    result = []
    first = bisect_right(windows, start, key=lambda span: span[1])
    for index in range(first, len(windows)):
        left, right = windows[index]
        if left >= end:
            break
        result.append((max(start, left), min(end, right)))
    return result


def _split_conflicts(
    observations: list[TimingObservation], held: list[TimingObservation]
) -> tuple[list[TimingObservation], list[TimingGap]]:
    by_actor, by_story = _conflict_windows(observations + held)
    retained, gaps = [], []
    for row in observations:
        if not _positive_turn(row):
            retained.append(row)
            if (
                row.kind == "missing"
                or (row.start_ms is None and row.end_ms is None)
                or (
                    row.kind not in _BOUNDARY_KINDS | {"pending-wait"}
                    and (row.start_ms is None or row.end_ms is None)
                )
            ):
                gaps.append(_gap(row, "missing-evidence"))
            continue
        cuts = []
        for code, windows in (
            ("cross-story-overlap", by_actor[row.scope.actor_key]),
            ("legacy-overlap", by_story[row.scope.story]),
        ):
            intersections = _intersections(row.start_ms, row.end_ms, windows)
            cuts.extend(intersections)
            gaps.extend(_gap(row, code, span) for span in intersections)
        if not cuts:
            retained.append(row)
            continue
        cursor = row.start_ms
        for left, right in sorted(cuts):
            if left > cursor:
                retained.append(
                    replace(row, start_ms=cursor, end_ms=left, coverage="partial")
                )
            cursor = max(cursor, right)
        if cursor < row.end_ms:
            retained.append(replace(row, start_ms=cursor, coverage="partial"))
    return retained, gaps


def _scope_evidence(
    observations: list[TimingObservation], gaps: list[TimingGap]
) -> dict[TimingScope, ScopeEvidence]:
    grouped = defaultdict(list)
    for row in observations:
        grouped[row.scope].append(row)
    held = {gap.scope for gap in gaps if gap.scope is not None}
    result = {}
    for scope in sorted(grouped.keys() | held, key=_scope_order):
        rows = grouped[scope]
        declared = {row.coverage for row in rows}
        if not declared or declared == {"unknown"}:
            coverage = "unknown"
        elif declared == {"complete"} and scope not in held:
            coverage = "complete"
        else:
            coverage = "partial"
        result[scope] = ScopeEvidence(
            coverage,
            max(
                (bound for row in rows if (bound := row.evidence_through) is not None),
                default=None,
            ),
            tuple(sorted({row.basis for row in rows})),
        )
    return result


def resolve_timing(tree: PlanningTree) -> TimingFacts:
    """Return direct observations and attribution gaps from one pinned tree."""
    current, gaps = _admit_v1(tree)
    historical, readback, historical_gaps = _legacy(tree)
    admitted, held, identity_gaps = _resolve_identity(current + historical)
    retained, overlap_gaps = _split_conflicts(admitted, held)
    all_gaps = gaps + historical_gaps + identity_gaps + overlap_gaps
    return TimingFacts(
        tuple(sorted(retained, key=_observation_order)),
        tuple(
            sorted(
                set(all_gaps),
                key=lambda gap: (
                    gap.story,
                    gap.code,
                    _scope_order(gap.scope) if gap.scope is not None else (),
                    gap.identity,
                    gap.start_ms if gap.start_ms is not None else float("-inf"),
                    gap.end_ms if gap.end_ms is not None else float("-inf"),
                    tuple(map(_source_order, gap.sources)),
                ),
            )
        ),
        _scope_evidence(retained, all_gaps),
        readback,
        tree.gaps,
    )
