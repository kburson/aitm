"""Project the Cost evidence for one fixed usage report in a pinned planning tree."""

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, fields
from datetime import UTC, datetime
from decimal import Context, Decimal
from typing import Literal

from . import evidence
from .evidence import Event, Gap, PlanningTree, Receipt, Registration, Story

_USAGE_KIND = "story-usage-receipt"
_CLOCK_FIELDS = ("window_start_utc", "window_end_utc", "cutoff_utc")
_ANCESTRY_GAPS = {
    "ancestry-conflict",
    "ancestry-cycle",
    "ancestry-missing",
    "ineligible-header",
    "invalid-ancestry",
}
_USAGE_INPUT_GAPS = {
    "future-receipt",
    "invalid-receipt",
    "invalid-registration",
    "receipt-blob",
    "receipt-digest",
    "receipt-missing",
    "registration-conflict",
}


@dataclass(frozen=True)
class ReportSelector:
    project: str
    report_id: str
    window_start_utc: datetime
    window_end_utc: datetime
    cutoff_utc: datetime
    rate_card: str
    pricing_basis: str

    def __post_init__(self):
        for identity in (
            self.project,
            self.report_id,
            self.rate_card,
            self.pricing_basis,
        ):
            if not evidence._pattern(identity, evidence.TOKEN):
                raise ValueError("invalid usage report identity or pricing basis")
        start, end, cutoff = (getattr(self, key) for key in _CLOCK_FIELDS)
        if any(
            not isinstance(value, datetime) or value.utcoffset() != UTC.utcoffset(value)
            for value in (start, end, cutoff)
        ):
            raise ValueError("expected UTC usage report timestamps")
        if not start < end <= cutoff:
            raise ValueError("invalid usage report window")

    @classmethod
    def from_dict(cls, value: object) -> "ReportSelector":
        if not isinstance(value, dict) or value.keys() != {
            field.name for field in fields(cls)
        }:
            raise ValueError("missing or unsupported usage report selector fields")
        parsed = value | {key: evidence._stamp(value[key]) for key in _CLOCK_FIELDS}
        return cls(**parsed)

    def to_dict(self) -> dict[str, str]:
        value = {}
        for field in fields(self):
            item = getattr(self, field.name)
            value[field.name] = (
                item.astimezone(UTC).isoformat().removesuffix("+00:00") + "Z"
                if field.name in _CLOCK_FIELDS
                else item
            )
        return value


@dataclass(frozen=True)
class UsageMeasure:
    priced_usd: Decimal | None = None
    coverage: Literal["complete", "partial", "unknown"] = "unknown"
    basis: str | None = None
    evidence_through: datetime | None = None
    receipt_digests: tuple[str, ...] = ()
    gaps: tuple[Gap, ...] = ()


@dataclass(frozen=True)
class StoryUsage:
    direct: UsageMeasure
    inclusive: UsageMeasure


@dataclass(frozen=True)
class UsageView:
    selector: ReportSelector | None
    source_sha256: str | None
    resolved_receipt_digests: tuple[str, ...]
    stories: dict[int, StoryUsage]


def _full_path(story: Story, relative: str) -> str:
    return story.path.rsplit("/", 1)[0] + "/" + relative


def _ordered_gaps(gaps: list[Gap] | tuple[Gap, ...]) -> tuple[Gap, ...]:
    return tuple(sorted(set(gaps), key=lambda gap: (gap.story, gap.code, gap.source)))


def _scoped_gaps(
    tree: PlanningTree, events: dict[str, Event], project: str
) -> tuple[dict[int, list[Gap]], dict[int, list[Gap]]]:
    usage_events, usage_paths = set(), set()
    for event in events.values():
        scope = event.data.get("scope")
        if (
            event.kind != "core.evidence.recorded"
            or event.data.get("kind") != _USAGE_KIND
            or not isinstance(scope, dict)
            or scope.get("project") != project
        ):
            continue
        usage_events.add(event.source)
        relative = event.data.get("path")
        if evidence._pattern(relative, evidence.RECEIPT_PATH):
            usage_paths.add(_full_path(tree.stories[event.story], relative))

    direct, ancestry = defaultdict(list), defaultdict(list)
    for gap in tree.gaps:
        if gap.code in _ANCESTRY_GAPS:
            ancestry[gap.story].append(gap)
        if gap.code not in _USAGE_INPUT_GAPS:
            continue
        if gap.source in usage_events or gap.source in usage_paths:
            direct[gap.story].append(gap)
        elif gap.code == "registration-conflict":
            # A01 records the first claim's location, which can belong to timing.
            event = events.get(gap.source)
            relative = event.data.get("path") if event else None
            if evidence._pattern(relative, evidence.RECEIPT_PATH) and (
                _full_path(tree.stories[gap.story], relative) in usage_paths
            ):
                direct[gap.story].append(gap)
    return direct, ancestry


def _verified_source(
    receipt: Receipt,
    selector: ReportSelector,
    registrations: set[Registration],
    events: dict[str, Event],
) -> str | None:
    claim = receipt.registration
    record = receipt.verification
    event = events.get(claim.source)
    if (
        claim not in registrations
        or claim.kind != _USAGE_KIND
        or claim.project != selector.project
        or record is None
        or event is None
        or receipt.usage is None
    ):
        return None
    try:
        if evidence._registration(event) != claim:
            return None
        verified_at = evidence._stamp(record.get("verified_at_utc"))
    except ValueError:
        return None
    operator = record.get("operator_ref")
    source_digest = receipt.source.get("sha256")
    if (
        not evidence._pattern(operator, evidence.TOKEN)
        or (event.actor or {}).get("on-behalf-of") != operator
        or not evidence._pattern(source_digest, evidence.SHA256)
        or record.get("source_sha256") != source_digest
        or record.get("source_report_id") != selector.report_id
        or type(record.get("verified_story")) is not int
        or record["verified_story"] != claim.story
        or record.get("selector") != receipt.selector
        or record.get("pricing_basis") != selector.pricing_basis
        or record.get("coverage") != receipt.coverage
        or not selector.cutoff_utc
        <= verified_at
        <= receipt.recorded_at
        <= claim.recorded_at
    ):
        return None
    payload = json.dumps(
        receipt.usage, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    if hashlib.sha256(payload).hexdigest() != record.get("sanitized_data_sha256"):
        return None
    return source_digest


def _effective_receipt(rows: dict[str, Receipt]) -> Receipt | None:
    """Return the terminal revision of one connected, chronological chain."""
    heads = rows.keys() - {row.supersedes for row in rows.values()}
    if len(heads) != 1:
        return None
    head = current = rows[next(iter(heads))]
    seen = {head.registration.sha256}
    while current.supersedes is not None:
        previous = rows.get(current.supersedes)
        if (
            previous is None
            or current.supersedes in seen
            or previous.recorded_at > current.recorded_at
            or previous.registration.recorded_at > current.registration.recorded_at
        ):
            return None
        seen.add(current.supersedes)
        current = previous
    return head if len(seen) == len(rows) else None


def _direct(
    story: Story,
    selector: ReportSelector,
    rows: dict[str, Receipt],
    verified: dict[str, str],
    source_conflict: bool,
    gaps: list[Gap],
) -> UsageMeasure:
    gaps = list(gaps)
    if not rows:
        gaps.append(Gap(story.id, "missing-usage-receipt", story.path))
        return UsageMeasure(gaps=_ordered_gaps(gaps))
    if source_conflict:
        gaps.append(Gap(story.id, "conflicting-usage-source", story.path))
    gaps.extend(
        Gap(story.id, "unverified-usage", row.registration.source)
        for digest, row in rows.items()
        if digest not in verified
    )
    if source_conflict or not rows.keys() <= verified.keys():
        return UsageMeasure(gaps=_ordered_gaps(gaps))
    effective = _effective_receipt(rows)
    if effective is None:
        gaps.append(Gap(story.id, "conflicting-usage-receipts", story.path))
        return UsageMeasure(gaps=_ordered_gaps(gaps))

    claim = effective.registration
    price = (effective.usage or {}).get("priced_usd")
    if price is None or effective.coverage == "unknown":
        code = "unpriced-usage" if price is None else "unknown-usage-coverage"
        gaps.append(Gap(story.id, code, claim.source))
        return UsageMeasure(receipt_digests=(claim.sha256,), gaps=_ordered_gaps(gaps))
    if effective.coverage == "partial":
        gaps.append(Gap(story.id, "partial-usage-coverage", claim.source))
    return UsageMeasure(
        Decimal(price),
        "partial" if gaps else "complete",
        selector.pricing_basis,
        selector.cutoff_utc,
        (claim.sha256,),
        _ordered_gaps(gaps),
    )


def _inclusive(
    rows: list[UsageMeasure], ancestry: list[Gap], selector: ReportSelector
) -> UsageMeasure:
    if len(rows) == 1 and not ancestry:
        return rows[0]
    prices = [row.priced_usd for row in rows if row.priced_usd is not None]
    digests = tuple(sorted({digest for row in rows for digest in row.receipt_digests}))
    gaps = _ordered_gaps(ancestry + [gap for row in rows for gap in row.gaps])
    if not prices:
        return UsageMeasure(receipt_digests=digests, gaps=gaps)
    # A01 bounds each amount to 20 whole and 18 fractional digits.
    arithmetic = Context(prec=38 + len(str(len(prices))))
    total = Decimal(0)
    for price in prices:
        total = arithmetic.add(total, price)
    coverage = (
        "partial"
        if ancestry or any(row.coverage != "complete" for row in rows)
        else "complete"
    )
    return UsageMeasure(
        total, coverage, selector.pricing_basis, selector.cutoff_utc, digests, gaps
    )


def select_usage(tree: PlanningTree, selector: ReportSelector | None) -> UsageView:
    """Resolve one immutable report, then sum its direct scopes over A01 ancestry."""
    if selector is None or selector.cutoff_utc > tree.as_of:
        code = (
            "usage-report-not-selected"
            if selector is None
            else "usage-cutoff-after-as-of"
        )
        stories = {}
        for story_id, story in sorted(tree.stories.items()):
            unknown = UsageMeasure(gaps=(Gap(story_id, code, story.path),))
            stories[story_id] = StoryUsage(unknown, unknown)
        return UsageView(selector, None, (), stories)

    events = {event.source: event for event in tree.events}
    registrations = set(tree.registrations)
    receipt_gaps, graph_gaps = _scoped_gaps(tree, events, selector.project)
    candidates: dict[int, dict[str, Receipt]] = defaultdict(dict)
    verified: dict[str, str] = {}
    for receipt in tree.receipts:
        claim = receipt.registration
        if (
            receipt.schema != evidence.USAGE_SCHEMA
            or claim.story not in tree.stories
            or ReportSelector.from_dict(receipt.selector) != selector
            or claim.sha256 in candidates[claim.story]
        ):
            continue
        candidates[claim.story][claim.sha256] = receipt
        source = _verified_source(receipt, selector, registrations, events)
        if source is not None:
            verified[claim.sha256] = source

    sources = set(verified.values())
    direct = {
        story_id: _direct(
            story,
            selector,
            candidates[story_id],
            verified,
            len(sources) > 1,
            receipt_gaps[story_id],
        )
        for story_id, story in sorted(tree.stories.items())
    }
    stories = {}
    for story_id, measure in direct.items():
        scope = sorted({story_id, *tree.descendants.get(story_id, ())})
        inclusive = _inclusive(
            [direct[member] for member in scope],
            [gap for member in scope for gap in graph_gaps[member]],
            selector,
        )
        stories[story_id] = StoryUsage(measure, inclusive)
    digests = tuple(
        sorted({digest for row in direct.values() for digest in row.receipt_digests})
    )
    return UsageView(
        selector, verified[digests[0]] if digests else None, digests, stories
    )
