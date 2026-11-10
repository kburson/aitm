import json
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal, localcontext
from hashlib import sha256
from importlib.resources import files
from uuid import UUID

import pytest

from aitm_usage import monitor_types, pricing
from aitm_usage.export import export_as_of
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    LedgerView,
    ModelLabel,
    ProcessingTier,
    Provider,
    Revision,
    SourceBoundary,
    SourceRef,
    TokenCounts,
    UsageObservation,
    _decode,
    _encode,
)

NOW = datetime(2026, 11, 10, 18, tzinfo=UTC)


def _monitor_card():
    loader = getattr(pricing, "load_monitor_rate_card", None)
    assert loader is not None, "Missing M05 monitor rate card"
    return loader()


def _grok_usage(**token_changes):
    model = monitor_types
    tokens = model.GrokTokenCounts(100, 400, 0, 200, 150, 700)
    return model.GrokObservation(
        model.MonitorProvider.GROK,
        model.NativeSurface.GROK_BUILD_MACOS,
        NOW,
        model.ObservationTimeBasis.NATIVE_COMPLETION,
        replace(tokens, **token_changes),
        Availability.COMPLETE,
        model.MonitorModel.GROK_4_7,
        model.ProviderCostEvidence(123456),
    )


def test_grok_rate_classes_do_not_use_claude_defaults():
    card = _monitor_card()
    (entry,) = card.entries
    assert (entry.uncached_input, entry.cache_read, entry.output) == (
        Decimal("2.00"),
        Decimal("0.50"),
        Decimal("6.00"),
    )
    assert entry.cache_creation is None
    assert entry.source == "https://docs.x.ai/developers/models/grok-4.7.md"
    assert entry.source_retrieved == "2026-11-10"
    assert entry.source_sha256 == (
        "cf323be0bbc5ccf47c3b50b9f5f4cbcf481584f446cdc79d677d3beaf483c440"
    )
    with localcontext(prec=2):
        result = pricing.price_grok(_grok_usage(), card)
    assert result.usd == Decimal("0.0016")
    assert result.availability is Availability.COMPLETE
    assert result.currency == "USD"
    assert result.basis == card.basis

    # 150 reasoning tokens are already in output. Cached input counts toward
    # the full-turn bound even when the uncached portion is below it.
    for cache_read, expected in [(199899, Decimal("0.1013495")), (199900, None)]:
        near_limit = _grok_usage(cache_read_tokens=cache_read, total_tokens=None)
        assert pricing.price_grok(near_limit, card).usd == expected
    zero = _grok_usage(
        uncached_input_tokens=0,
        cache_read_tokens=0,
        output_tokens=0,
        reasoning_output_tokens=0,
        total_tokens=0,
    )
    assert pricing.price_grok(zero, card).usd == Decimal(0)


def test_unknown_grok_rate_and_provider_ticks_remain_separate():
    card = _monitor_card()
    usage = _grok_usage()
    (entry,) = card.entries
    unknown_cases = [
        (replace(usage, model=monitor_types.MonitorModel.GROK_4_7_BUILD), card),
        (replace(usage, model=monitor_types.MonitorModel.UNKNOWN), card),
        (replace(usage, coverage=Availability.PARTIAL), card),
        (usage, replace(card, entries=())),
        (_grok_usage(cache_creation_tokens=1, total_tokens=701), card),
        (_grok_usage(cache_read_tokens=199901, total_tokens=None), card),
    ]
    for field in (
        "uncached_input_tokens",
        "cache_read_tokens",
        "cache_creation_tokens",
        "output_tokens",
    ):
        unknown_cases.append((_grok_usage(**{field: None}), card))
    for field in ("uncached_input", "cache_read", "output"):
        altered = replace(card, entries=(replace(entry, **{field: None}),))
        assert altered.basis != card.basis
        unknown_cases.append((usage, altered))
    for observation, selected in unknown_cases:
        result = pricing.price_grok(observation, selected)
        assert result.usd is None
        assert result.availability is Availability.UNKNOWN
        assert result.basis == selected.basis
        assert observation.provider_cost.ticks == 123456

    assert pricing.price_grok(replace(usage, provider_cost=None), card) == (
        pricing.price_grok(usage, card)
    )


def test_grok_card_rejects_unproven_rate_classes_and_models():
    card = _monitor_card()
    payload = json.loads(_encode(card, type(card)))
    (entry,) = payload["entries"]
    for change in (
        {"cache_write_5m": "5"},
        {"cache_creation": "5"},
        {"model": "grok-4.7-build"},
        {"provider": "claude"},
        {"source": "https://example.invalid/"},
        {"source_retrieved": "2026-11-31"},
        {"source_sha256": "bad"},
        {"input_threshold": 200001},
        {"output": "0"},
        {"cache_read": "0.0000001"},
    ):
        changed = dict(payload, entries=[dict(entry, **change)])
        with pytest.raises(ValueError):
            type(card).from_json(json.dumps(changed))


def _legacy_revision(provider, model, version, token_counts, context, tag):
    def ref(digit):
        return SourceRef(f"hmac-sha256:{tag * 63}{digit}:{'a' * 64}")

    return Revision(
        ref("1"),
        1,
        UsageObservation(
            SourceBoundary(
                provider, ref("2"), ref("3"), 1, BoundaryKind.REQUEST, ref("4")
            ),
            NOW,
            version,
            1,
            token_counts,
            Availability.COMPLETE,
            model=model,
            processing_tier=ProcessingTier.STANDARD,
            context_tokens=context,
        ),
    )


def _legacy_view():
    codex = _legacy_revision(
        Provider.CODEX,
        ModelLabel.GPT_6_ASTRA,
        ClientVersion.CODEX_0_167_0_ALPHA_3_2,
        TokenCounts(500, 400, 0, 0, 200, 150, 700),
        500,
        "1",
    )
    claude = _legacy_revision(
        Provider.CLAUDE,
        ModelLabel.CLAUDE_OPUS_5_5,
        ClientVersion.CLAUDE_2_1_318,
        TokenCounts(500, 400, 50, 30, 200, None, 780),
        580,
        "2",
    )
    return LedgerView(UUID(int=115), 2, (codex, claude), ())


def test_grok_preserves_legacy_rate_digest_and_fixed_export(tmp_path):
    raw = files("aitm_usage").joinpath("rates", "2026-11-09.json").read_bytes()
    assert sha256(raw).hexdigest() == (
        "c65f2cb5ea797331862746a30fe71c88a4d906f35ca0cc27f7fa327fb583623e"
    )
    card = pricing.load_rate_card()
    assert card.version == "2026-11-09"
    assert card.basis.sha256 == (
        "cc98b8b92c0ecafb7d6c563e26752ea43ccc0f16b11a8db6199a6a8d70ac3e42"
    )
    destination = tmp_path / "legacy"
    export_as_of(_legacy_view(), card, destination)
    # Freeze both files against a deterministic two-provider export at #114's head.
    assert (
        sha256((destination / "usage.jsonl").read_bytes()).hexdigest()
        == "7b17b824c000e9e74e805cb00d562067ec9da8c66e745be55b474d5eb1c72e9a"
    )
    assert (
        sha256((destination / "manifest.json").read_bytes()).hexdigest()
        == "e8d98a3e15772c17886f93a410b91a3615bcee2876456f30a6e6fdb07d76d575"
    )


def test_legacy_v1_revision_refuses_grok_provider():
    codex = _legacy_view().revisions[0]
    raw = _encode(codex, Revision)
    assert _decode(raw, Revision) == codex
    with pytest.raises(ValueError):
        _decode(raw.replace('"provider":"codex"', '"provider":"grok"'), Revision)
