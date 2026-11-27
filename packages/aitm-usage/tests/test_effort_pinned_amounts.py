from hashlib import sha256
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

_CARD = (
    Path(__file__).parents[1]
    / "src/aitm_usage/rates/effort/2026-11-25-sol-standard.json"
)
_START = "2026-11-25T01:00:00Z"
_STOP = "2026-11-25T01:00:10Z"


def _rates():
    from aitm_usage.effort.pinned_amounts import load_comparison_rates

    return load_comparison_rates(_CARD, sha256(_CARD.read_bytes()).hexdigest())


def _tokens(gross=100, cached=10, output=20, *, reasoning=5, short=None, long=None):
    return {
        "input_tokens": gross,
        "cached_input_tokens": cached,
        "output_tokens": output,
        "reasoning_output_tokens": reasoning,
        "cache_write_5m_tokens": short,
        "cache_write_1h_tokens": long,
        "total_tokens": None
        if gross is None or output is None
        else gross + output + (short or 0) + (long or 0),
    }


def _turn(
    number=1, *, tokens=None, requests=None, start=_START, end=_STOP, **overrides
):
    counts = tokens if tokens is not None else _tokens()
    return {
        "attempt": f"{number:064x}",
        "identity": f"{100 + number:064x}",
        "revision": 1,
        "role": "worker",
        "provider": "codex",
        "model": "gpt-6.2-sol",
        "coverage": "complete",
        "outcome": "completed",
        "usage_scope": "bounded",
        "time_basis": "native",
        "started_at": start,
        "ended_at": end,
        "tokens": counts,
        "rate_inputs": requests if requests is not None else [counts],
        "reported_grok_usd_ticks": None,
    } | overrides


def _coverage(turns=(), **overrides):
    return {
        "admission": "closed",
        "attempts": [{"attempt": row["attempt"], "state": "observed"} for row in turns],
        "unattributed": 0,
        "verified_no_work": False,
    } | overrides


def _summarize(turns=(), *, coverage=None, gaps=(), timing=()):
    from aitm_usage.effort.pinned_amounts import summarize

    return summarize(
        SimpleNamespace(receipts=turns, coverage=coverage, gaps=gaps, timing=timing),
        _rates(),
    )


class RateCard:
    def __init__(self, raw):
        self.raw = raw

    def open(self, mode):
        assert mode == "rb"
        return BytesIO(self.raw)


def test_pinned_card_requires_expected_digest_and_canonical_bytes():
    from aitm_usage.effort.pinned_amounts import load_comparison_rates

    raw = _CARD.read_bytes()
    digest = sha256(raw).hexdigest()
    card = RateCard(raw)
    rates = load_comparison_rates(card, digest)
    assert rates.sha256 == digest
    source = _CARD.with_name("2026-11-25-sol-standard-source.json")
    assert rates.source_sha256 == sha256(source.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        load_comparison_rates(card, "1" * 64)
    tampered = raw + b"\n"
    with pytest.raises(ValueError):
        load_comparison_rates(RateCard(tampered), sha256(tampered).hexdigest())


def test_pinned_card_rejects_unsupported_tier_and_unqualified_provider():
    from aitm_usage.effort.pinned_amounts import load_comparison_rates

    original = _CARD.read_bytes()
    for old, new in ((b'"standard"', b'"fast"'), (b'"codex"', b'"other"')):
        raw = original.replace(old, new)
        assert raw != original
        with pytest.raises(ValueError):
            load_comparison_rates(RateCard(raw), sha256(raw).hexdigest())


@pytest.mark.parametrize(
    ("input_tokens", "expected"), [(272000, "0.54481"), (272001, "1.089124")]
)
def test_context_threshold_applies_to_full_request(input_tokens, expected):
    turn = _turn(tokens=_tokens(input_tokens, 100, 100))
    result = _summarize((turn,), coverage=_coverage((turn,)))
    assert result["api_estimate_usd"] == expected
    assert result["cost_eligible"] is True
    assert result["engagement_us"] is None
    assert result["turns"][0]["native_duration_us"] == 10_000_000


def test_two_short_requests_are_not_priced_as_one_long_request():
    request = _tokens(150000, 100, 100)
    turn = _turn(
        tokens=_tokens(300000, 200, 200, reasoning=10), requests=[request, request]
    )
    assert _summarize((turn,))["api_estimate_usd"] == "0.60162"


@pytest.mark.parametrize(
    "overrides",
    [
        {"model": "gpt-6.2-astra"},
        {"rate_inputs": []},
        {"rate_inputs": [_tokens(99, 10, 20)]},
        {"rate_inputs": [_tokens(100, 10, 20, short=1)]},
        {"rate_inputs": [_tokens(100, 10, 20, reasoning=21)]},
        {"rate_inputs": [_tokens(100, 101, 20)]},
        {"rate_inputs": [_tokens(100, 10, 20) | {"total_tokens": 121}]},
    ],
)
def test_unqualified_rate_inputs_hold_complete_cost(overrides):
    turn = _turn(**overrides)
    result = _summarize((turn,), coverage=_coverage((turn,)))
    assert result["api_estimate_usd"] is None
    assert result["cost_eligible"] is False
    assert "incomplete-pricing" in result["cost_hold_reasons"]
    assert result["turns"][0]["api_estimate_gap"] in {
        "unsupported-rate-model",
        "missing-request-inputs",
        "unsupported-cache-write-basis",
        "invalid-request-counters",
        "request-counter-mismatch",
    }


def test_partial_turn_retains_known_columns_and_native_interval():
    complete = _turn()
    interrupted = _turn(
        2,
        tokens=_tokens(None, 7, None, reasoning=None),
        coverage="partial",
        outcome="interrupted",
    )
    result = _summarize(
        (complete, interrupted), coverage=_coverage((complete, interrupted))
    )
    assert result["tokens"] == {"cached_input": 17, "new_input": 90, "output": 20}
    assert result["token_coverage"]["cached_input"]["status"] == "partial"
    assert result["token_coverage"]["output"]["known_turns"] == 1
    assert result["api_estimate_usd"] == "0.000381"
    assert result["api_estimate_coverage"]["status"] == "partial"
    assert result["cost_eligible"] is False
    assert [row["native_duration_us"] for row in result["turns"]] == [10_000_000] * 2


def test_cache_creation_is_counted_exactly_once_across_provider_dialects():
    claude = _turn(
        1, provider="claude", model="claude-sonnet-5-5", tokens=_tokens(short=3, long=4)
    )
    grok = _turn(
        2,
        provider="grok",
        model="grok-4.7-build-fast",
        reported_grok_usd_ticks=72,
        grok_cache_creation_tokens=7,
    )
    result = _summarize((claude, grok), coverage=_coverage((claude, grok)))
    assert result["tokens"] == {"cached_input": 20, "new_input": 187, "output": 40}
    assert result["provider_reported_grok_usd_ticks"] == 72
    assert result["provider_reported_grok_coverage"]["status"] == "complete"
    assert result["api_estimate_usd"] is None
    assert result["verified_billed_usd"] is None
    assert result["cost_eligible"] is False


def test_older_without_roster_keeps_measured_numerator_and_holds_cost():
    result = _summarize((_turn(),))
    assert result["coverage"]["expected_turns"] is None
    assert result["coverage"]["measured_turns"] == 1
    assert result["api_estimate_usd"] == "0.000381"
    assert result["cost_eligible"] is False


def test_verified_no_work_differs_from_absent_evidence_and_empty_admission():
    for coverage in (None, _coverage()):
        result = _summarize(coverage=coverage)
        assert result["api_estimate_usd"] is None
        assert result["tokens"] == {
            "cached_input": None,
            "new_input": None,
            "output": None,
        }
        assert result["cost_eligible"] is False
    result = _summarize(coverage=_coverage(verified_no_work=True))
    assert (
        result["coverage"]["expected_turns"]
        == result["coverage"]["measured_turns"]
        == 0
    )
    assert result["tokens"] == {"cached_input": 0, "new_input": 0, "output": 0}
    assert result["api_estimate_usd"] == "0"
    assert result["cost_eligible"] is True


def test_gaps_dispute_inclusive_scope_and_duplicate_attempt_exclude_same_quantity():
    normal = _turn()
    disputed = _turn(2)
    inclusive = _turn(3, usage_scope="inclusive")
    duplicate = _turn(4)
    duplicate_copy = _turn(4, identity=f"{1000:064x}")
    rows = (normal, disputed, inclusive, duplicate, duplicate_copy)
    coverage = _coverage(rows[:-1])
    coverage["attempts"][1]["state"] = "disputed"
    result = _summarize(rows, coverage=coverage, gaps=("cutoff-lineage",))
    assert result["coverage"]["measured_turns"] == 1
    assert result["coverage"]["disputed"] == 1
    assert result["tokens"] == {"cached_input": 10, "new_input": 90, "output": 20}
    assert result["api_estimate_usd"] == "0.000381"
    assert result["cost_eligible"] is False


def test_qualified_timing_unions_by_actor_and_subtracts_evidenced_owner_wait():
    first = _turn()
    middle = _turn(2, start="2026-11-25T01:00:05Z", end="2026-11-25T01:00:15Z")
    other = _turn(3, start="2026-11-25T01:00:07Z", end="2026-11-25T01:00:09Z")
    rows = (first, middle, other)
    timing = tuple(
        {
            "attempt": row["attempt"],
            "actor": "actor-b" if row is other else "actor-a",
            "clock": "project-clock",
            "start": row["started_at"],
            "end": row["ended_at"],
            "owner_waits": (
                [{"start": "2026-11-25T01:00:06Z", "end": "2026-11-25T01:00:08Z"}]
                if row is middle
                else []
            ),
        }
        for row in rows
    )
    assert (
        _summarize(rows, coverage=_coverage(rows), timing=timing)["engagement_us"]
        == 15_000_000
    )
    unaligned = (timing[0], timing[1] | {"clock": "other-clock"}, timing[2])
    assert (
        _summarize(rows, coverage=_coverage(rows), timing=unaligned)["engagement_us"]
        is None
    )


def test_invalid_timing_evidence_holds_engagement_independently_of_cost():
    turn = _turn()
    rows = (turn,)
    timing = (
        {
            "attempt": turn["attempt"],
            "actor": "actor-a",
            "clock": "project-clock",
            "start": _START,
            "end": _STOP,
            "owner_waits": [],
        },
    )
    summary = _summarize(
        rows,
        coverage=_coverage(rows),
        gaps=("timing-evidence-invalid",),
        timing=timing,
    )
    assert summary["cost_eligible"] is True
    assert summary["api_estimate_usd"] == "0.000381"
    assert summary["engagement_us"] is None
    assert summary["engagement_coverage"]["status"] == "unknown"
