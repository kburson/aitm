"""Coverage and read-only arithmetic for one pinned story report."""

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Context, Decimal, localcontext
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

from ..pricing import _validate_rate
from ..types import _unique_fields
from .export import render_export
from .receipts import require_digest
from .rollup import _union
from .store import EffortError

if TYPE_CHECKING:
    from .pinned_inputs import PinnedInputs

_RATE_SCHEMA = "aitm.story-effort-comparison-rates/v1"
_SOL_MODEL = "gpt-6.2-sol"
_SOL_RATE_SOURCE = "https://developers.openai.com/api/docs/models/gpt-6.2-sol#pricing"
_PRICE_BASIS = "standard-api-equivalent"
_MAX_RATE_BYTES = 2 << 20
_COUNTERS = ("cached_input", "new_input", "output")
_STATES = ("missing", "unavailable", "withdrawn", "disputed")
_INVALID_TIMING = "timing-evidence-invalid"
_US = timedelta(microseconds=1)


@dataclass(frozen=True, slots=True)
class ComparisonRates:
    """A digest-verified Standard card, distinct from the monitor's rate basis."""

    version: str
    sha256: str
    source_sha256: str
    uncached_input: Decimal
    cached_input: Decimal
    output: Decimal
    long_threshold: int
    long_input_multiplier: Decimal
    long_output_multiplier: Decimal


def _rate(raw: str, places: int) -> Decimal:
    if not isinstance(raw, str) or not re.fullmatch(
        r"(0|[1-9][0-9]{0,6})(\.[0-9]{1,6})?", raw
    ):
        raise ValueError("Invalid decimal rate")
    value = Decimal(raw)
    _validate_rate(value, places)
    return value


def _day(raw: str) -> date:
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw):
        raise ValueError("Invalid rate date")
    return date.fromisoformat(raw)


def load_comparison_rates(path: Path, expected_sha256: str) -> ComparisonRates:
    """Verify canonical rate-card bytes against the caller's reviewed digest."""
    try:
        require_digest(expected_sha256)
        with path.open("rb") as stream:
            raw = stream.read(_MAX_RATE_BYTES + 1)
        if len(raw) > _MAX_RATE_BYTES or sha256(raw).hexdigest() != expected_sha256:
            raise ValueError("Unexpected rate-card bytes")
        fields = json.loads(raw, object_pairs_hook=_unique_fields)
        if not isinstance(fields, dict) or render_export(fields).encode() != raw:
            raise ValueError("Expected canonical rate card")
        fixed = {
            "schema": _RATE_SCHEMA,
            "currency": "USD",
            "provider": "codex",
            "model": _SOL_MODEL,
            "tier": "standard",
            "source_url": _SOL_RATE_SOURCE,
        }
        keys = {
            "version",
            "source_observed_on",
            "source_sha256",
            "uncached_input_per_million",
            "cached_input_per_million",
            "output_per_million",
            "long_context_input_threshold",
            "long_context_input_multiplier",
            "long_context_output_multiplier",
        }
        if fields.keys() != fixed.keys() | keys or any(
            fields[key] != value for key, value in fixed.items()
        ):
            raise ValueError("Unsupported rate-card shape or comparison basis")
        if _day(fields["source_observed_on"]) > _day(fields["version"]):
            raise ValueError("Rate source postdates its version")
        require_digest(fields["source_sha256"])
        threshold = fields["long_context_input_threshold"]
        if type(threshold) is not int or not 0 < threshold < 2**63:
            raise ValueError("Invalid rate threshold")
        input_multiplier = _rate(fields["long_context_input_multiplier"], 1)
        output_multiplier = _rate(fields["long_context_output_multiplier"], 1)
        if not all(
            1 <= factor <= 10 for factor in (input_multiplier, output_multiplier)
        ):
            raise ValueError("Invalid long-context pricing multiplier")
        return ComparisonRates(
            fields["version"],
            expected_sha256,
            fields["source_sha256"],
            _rate(fields["uncached_input_per_million"], 6),
            _rate(fields["cached_input_per_million"], 6),
            _rate(fields["output_per_million"], 6),
            threshold,
            input_multiplier,
            output_multiplier,
        )
    except (KeyError, OSError, RecursionError, TypeError, ValueError):
        raise EffortError("Invalid pinned comparison rate card") from None


def _token_columns(receipt: dict) -> dict[str, int | None]:
    counts = receipt["tokens"]
    gross, cached = counts["input_tokens"], counts["cached_input_tokens"]
    output, reasoning = counts["output_tokens"], counts["reasoning_output_tokens"]
    if gross is not None and cached is not None and cached > gross:
        cached = None
    if output is not None and reasoning is not None and reasoning > output:
        output = None
    fresh = None
    if gross is not None and cached is not None:
        short, long = counts["cache_write_5m_tokens"], counts["cache_write_1h_tokens"]
        if receipt["provider"] == "claude":
            if short is not None and long is not None:
                fresh = gross - cached + short + long
        elif short in (None, 0) and long in (None, 0):
            # Grok normalization has already included native creation in gross.
            fresh = gross - cached
    return {"cached_input": cached, "new_input": fresh, "output": output}


def _request_counts(tokens: dict) -> tuple[int, int, int] | None:
    gross, cached, output = (
        tokens["input_tokens"],
        tokens["cached_input_tokens"],
        tokens["output_tokens"],
    )
    if None in (gross, cached, output) or cached > gross:
        return None
    if any(
        tokens[key] not in (None, 0)
        for key in ("cache_write_5m_tokens", "cache_write_1h_tokens")
    ):
        return None
    reasoning = tokens["reasoning_output_tokens"]
    if reasoning is not None and reasoning > output:
        return None
    if tokens["total_tokens"] not in (None, gross + output):
        return None
    return gross, cached, output


def _price(receipt: dict, rates: ComparisonRates) -> tuple[Decimal | None, str | None]:
    if receipt["provider"] != "codex" or receipt["model"] != _SOL_MODEL:
        return None, "unsupported-rate-model"
    requests = receipt["rate_inputs"]
    if not requests:
        return None, "missing-request-inputs"
    if any(
        row[key] not in (None, 0)
        for row in (receipt["tokens"], *requests)
        for key in ("cache_write_5m_tokens", "cache_write_1h_tokens")
    ):
        return None, "unsupported-cache-write-basis"
    totals = _request_counts(receipt["tokens"])
    counts = [_request_counts(row) for row in requests]
    if totals is None or None in counts:
        return None, "invalid-request-counters"
    if tuple(map(sum, zip(*counts, strict=True))) != totals:
        return None, "request-counter-mismatch"
    reasoning = receipt["tokens"]["reasoning_output_tokens"]
    request_reasoning = [row["reasoning_output_tokens"] for row in requests]
    if reasoning is not None and (
        None in request_reasoning or sum(request_reasoning) != reasoning
    ):
        return None, "request-counter-mismatch"
    total = Decimal(0)
    for gross, cached, output in counts:
        inputs = (gross - cached) * rates.uncached_input + cached * rates.cached_input
        outputs = output * rates.output
        if gross > rates.long_threshold:
            inputs *= rates.long_input_multiplier
            outputs *= rates.long_output_multiplier
        total += inputs + outputs
    return total.scaleb(-6), None


def _decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _status(known: int, complete: bool) -> dict:
    status = "complete" if complete else "partial" if known else "unknown"
    return {"known_turns": known, "status": status}


def _interval(start: str | None, end: str | None):
    if start is None or end is None:
        return None
    left, right = datetime.fromisoformat(start), datetime.fromisoformat(end)
    if left.utcoffset() != UTC.utcoffset(left) or right.utcoffset() != UTC.utcoffset(
        right
    ):
        return None
    return (left, right) if left <= right else None


def _engagement(
    receipts: list[dict], timing: tuple[dict, ...]
) -> tuple[int | None, int]:
    native_intervals = {
        row["attempt"]: _interval(row["started_at"], row["ended_at"])
        if row["time_basis"] == "native"
        else None
        for row in receipts
    }
    actors = defaultdict(list)
    clocks = {}
    waits = defaultdict(list)
    matched = set()
    for row in timing:
        attempt = row["attempt"]
        if attempt not in native_intervals:
            continue
        active = _interval(row["start"], row["end"])
        actor, clock = row["actor"], row["clock"]
        if (
            attempt in matched
            or active is None
            or active != native_intervals[attempt]
            or clocks.setdefault(actor, clock) != clock
        ):
            return None, 0
        owner_waits = [
            _interval(wait["start"], wait["end"]) for wait in row["owner_waits"]
        ]
        if any(
            wait is None or not active[0] <= wait[0] <= wait[1] <= active[1]
            for wait in owner_waits
        ):
            return None, 0
        matched.add(attempt)
        actors[actor].append(active)
        waits[actor].extend(owner_waits)
    if not actors or matched != native_intervals.keys():
        return None, 0
    total = sum(
        (
            _union(sorted(spans))
            - (_union(sorted(waits[actor])) if waits[actor] else timedelta())
            for actor, spans in actors.items()
        ),
        timedelta(),
    )
    return total // _US, len(matched)


def _roster(inputs: "PinnedInputs") -> tuple[dict, dict, set[str]]:
    record = inputs.coverage
    rows = [] if record is None else record["attempts"]
    expected = {row["attempt"]: row["state"] for row in rows}
    counts = Counter(row["state"] for row in rows)
    admission = "unknown" if record is None else record["admission"]
    unattributed = None if record is None else record["unattributed"]
    reasons = set(inputs.gaps) - {_INVALID_TIMING}
    if record is None:
        reasons.add("missing-coverage-record")
    elif admission != "closed":
        reasons.add("open-admission")
    if unattributed != 0:
        reasons.add(
            "unknown-unattributed-coverage"
            if unattributed is None
            else "unattributed-coverage"
        )
    if len(expected) != len(rows):
        reasons.add("duplicate-roster-attempt")
    pending = sum(
        count for state, count in counts.items() if state.startswith("pending")
    )
    if pending:
        reasons.add("pending-attempts")
    reasons.update(f"{state}-attempts" for state in _STATES if counts[state])
    coverage = {
        "admission": admission,
        "expected_turns": len(expected) if admission == "closed" else None,
        "sampled_attempts": len(expected) if record is not None else None,
        "pending": pending if record is not None else None,
        "unattributed": unattributed,
        **{state: counts[state] if record is not None else None for state in _STATES},
    }
    return coverage, expected, reasons


def _excluded(
    receipt: dict,
    expected: dict,
    closed: bool,
    attempts: Counter,
    identities: Counter,
) -> str | None:
    attempt = receipt["attempt"]
    if attempts[attempt] > 1 or identities[receipt["identity"]] > 1:
        return "duplicate-usage-evidence"
    if attempt in expected and expected[attempt] != "observed":
        return "unreconciled-attempt"
    if closed and attempt not in expected:
        return "unmatched-receipt"
    if receipt["usage_scope"] != "bounded":
        return "unproved-disjoint-scope"
    return None


def _turn(
    receipt: dict,
    tokens: dict,
    price: Decimal | None,
    price_gap: str | None,
    exclusion: str | None,
) -> dict:
    result = {
        key: receipt[key]
        for key in (
            "attempt",
            "identity",
            "revision",
            "provider",
            "role",
            "model",
            "time_basis",
            "started_at",
            "ended_at",
            "usage_scope",
            "coverage",
            "outcome",
        )
    }
    interval = _interval(receipt["started_at"], receipt["ended_at"])
    duration = (
        (interval[1] - interval[0]) // _US
        if interval is not None and receipt["time_basis"] == "native"
        else None
    )
    return result | {
        "native_duration_us": duration,
        "tokens": tokens,
        "api_estimate_usd": _decimal(price),
        "api_estimate_gap": price_gap,
        "exclusion": exclusion,
    }


def summarize(inputs: "PinnedInputs", rates: ComparisonRates) -> dict:
    """Keep observed subtotals, independent authorities, and projection gates distinct."""
    coverage, expected, reasons = _roster(inputs)
    closed = coverage["admission"] == "closed"
    attempts = Counter(row["attempt"] for row in inputs.receipts)
    identities = Counter(row["identity"] for row in inputs.receipts)
    if any(
        expected[attempt] == "observed" for attempt in expected.keys() - attempts.keys()
    ):
        reasons.add("expected-receipt-missing")
    no_work = (
        closed
        and not expected
        and not inputs.receipts
        and not reasons
        and inputs.coverage.get("verified_no_work") is True
    )
    if closed and not expected and not no_work:
        reasons.add("unproved-empty-admission")
        coverage["expected_turns"] = None

    sums = Counter()
    known = Counter()
    complete_tokens = Counter()
    prices, reported, selected, turns = [], [], [], []
    complete_prices = measured = grok_turns = grok_complete = 0
    with localcontext(Context(prec=64)):
        for receipt in inputs.receipts:
            exclusion = _excluded(receipt, expected, closed, attempts, identities)
            if exclusion is not None:
                reasons.add(exclusion)
            available = exclusion is None and receipt["coverage"] != "unknown"
            tokens = _token_columns(receipt) if available else dict.fromkeys(_COUNTERS)
            amount, price_gap = (
                _price(receipt, rates)
                if available
                else (None, exclusion or "unavailable-usage")
            )
            turns.append(_turn(receipt, tokens, amount, price_gap, exclusion))
            if exclusion is None:
                selected.append(receipt)
            finished = (
                receipt["coverage"] == "complete" and receipt["outcome"] == "completed"
            )
            if available and any(value is not None for value in tokens.values()):
                measured += 1
            for key, value in tokens.items():
                if value is not None:
                    sums[key] += value
                    known[key] += 1
                    complete_tokens[key] += finished
            if receipt["provider"] == "grok":
                grok_turns += 1
                if available and receipt["reported_grok_usd_ticks"] is not None:
                    reported.append(receipt["reported_grok_usd_ticks"])
                    grok_complete += finished
            if amount is not None:
                prices.append(amount)
                complete_prices += finished
        estimate = sum(prices, Decimal(0)) if prices or no_work else None

    coverage["measured_turns"] = measured
    reconciled = closed and not reasons
    total_rows = len(inputs.receipts)
    usage_complete = {
        key: reconciled and (no_work or complete_tokens[key] == total_rows)
        for key in _COUNTERS
    }
    price_complete = reconciled and (no_work or complete_prices == total_rows)
    if not all(usage_complete.values()):
        reasons.add("incomplete-usage")
    if not price_complete:
        reasons.add("incomplete-pricing")
    engagement, known_timed = (
        (None, 0)
        if _INVALID_TIMING in inputs.gaps
        else _engagement(selected, inputs.timing)
    )
    return {
        "tokens": {
            key: sums[key] if known[key] or no_work else None for key in _COUNTERS
        },
        "token_coverage": {
            key: _status(known[key], usage_complete[key]) for key in _COUNTERS
        },
        "api_estimate_usd": _decimal(estimate),
        "api_estimate_coverage": _status(len(prices), price_complete),
        "api_price_basis": _PRICE_BASIS,
        "provider_reported_grok_usd_ticks": sum(reported) if reported else None,
        "provider_reported_grok_coverage": _status(
            len(reported), reconciled and grok_turns > 0 and grok_complete == grok_turns
        ),
        "verified_billed_usd": None,
        "verified_billed_coverage": _status(0, False),
        "coverage": coverage,
        "engagement_us": engagement,
        "engagement_coverage": _status(
            known_timed, reconciled and engagement is not None
        ),
        "turns": turns,
        "cost_eligible": not reasons,
        "cost_hold_reasons": sorted(reasons),
    }
