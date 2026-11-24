import json
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from test_ledger import _LedgerRows, _memory_ledger

from aitm_usage import accounting, pricing
from aitm_usage import ledger as store
from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.rollup import PriceProjection, rollup
from aitm_usage.types import (
    AdapterResult,
    Availability,
    BoundaryKind,
    ClientVersion,
    Currency,
    Diagnostic,
    DiagnosticCode,
    ItemKey,
    ItemKind,
    LedgerBatch,
    ModelLabel,
    ProcessingTier,
    Provider,
    ProviderCheckpoint,
    QuotaBucket,
    QuotaEvidence,
    QuotaSource,
    Revision,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    TokenCounts,
    UsageObservation,
    _decode,
    _encode,
)

NOW = datetime(2026, 11, 9, 18, tzinfo=UTC)
PROJECT = UUID(int=90)
ITEM = ItemKey(ItemKind.ISSUE, 90)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_control_root", lambda: tmp_path / "control")
    return Ledger.initialize(tmp_path / "project", PROJECT)


@pytest.fixture
def pricing_evidence():
    return _memory_ledger(store, PROJECT, b"pricing-policy-test")


@pytest.fixture
def accounting_rows(pricing_evidence, monkeypatch):
    rows = _LedgerRows(pricing_evidence.identity, store.APPLICATION_ID, ())
    writer = replace(
        pricing_evidence,
        _writer=object(),
        _write_paths=SimpleNamespace(check=lambda: None),
    )

    @contextmanager
    def transaction(ledger, *, write):
        assert ledger is writer
        with rows.connect(write=write) as connection:
            yield connection

    monkeypatch.setattr(
        Ledger, "reader", lambda ledger: transaction(ledger, write=False)
    )
    monkeypatch.setattr(
        Ledger, "_write_transaction", lambda ledger: transaction(ledger, write=True)
    )
    return writer, rows


@pytest.fixture(scope="module")
def reference_rates():
    """Freeze the v2026-11-09 inputs used by the arithmetic examples."""
    return pricing.RateCard(
        "2026-11-09",
        Currency.USD,
        ProcessingTier.STANDARD,
        pricing._LongContextRate(272000, Decimal("2"), Decimal("1.5")),
        (
            pricing._ModelRate(
                ModelLabel.GPT_6_ASTRA,
                Provider.CODEX,
                pricing._RateSource.ASTRA,
                uncached_input=Decimal("10"),
                cache_read=Decimal("1"),
                cache_write=Decimal("12.5"),
                cache_write_5m=None,
                cache_write_1h=None,
                output=Decimal("50"),
            ),
            pricing._ModelRate(
                ModelLabel.GPT_6_1_SOL,
                Provider.CODEX,
                pricing._RateSource.SOL,
                uncached_input=Decimal("2"),
                cache_read=Decimal("0.1"),
                cache_write=Decimal("2.5"),
                cache_write_5m=None,
                cache_write_1h=None,
                output=Decimal("10"),
            ),
            pricing._ModelRate(
                ModelLabel.CLAUDE_OPUS_5_5,
                Provider.CLAUDE,
                pricing._RateSource.OPUS,
                uncached_input=Decimal("4"),
                cache_read=Decimal("0.2"),
                cache_write=None,
                cache_write_5m=Decimal("5"),
                cache_write_1h=Decimal("8"),
                output=Decimal("20"),
            ),
        ),
    )


def usage(project, model=ModelLabel.GPT_6_ASTRA, *, revision=1):
    claude = model is ModelLabel.CLAUDE_OPUS_5_5
    provider = Provider.CLAUDE if claude else Provider.CODEX
    request = project.pseudonymize("test-request", provider.value)
    return Revision(
        project.pseudonymize("test-usage", provider.value),
        revision,
        UsageObservation(
            SourceBoundary(
                provider,
                project.pseudonymize("test-stream", provider.value),
                project.pseudonymize("test-session", provider.value),
                1,
                BoundaryKind.REQUEST,
                request,
            ),
            NOW,
            ClientVersion.CLAUDE_2_1_318
            if claude
            else ClientVersion.CODEX_0_167_0_ALPHA_3_2,
            1,
            TokenCounts(500, 400, 50 if claude else 0, 30 if claude else 0, 200, 150),
            Availability.COMPLETE,
            request_ref=request,
            model=model,
            processing_tier=ProcessingTier.STANDARD,
            context_tokens=580 if claude else 500,
        ),
    )


def quota(project, *, provider=Provider.CODEX):
    return QuotaEvidence(
        provider,
        project.pseudonymize("test-account", f"{provider.value}:account-canary"),
        QuotaBucket.SEVEN_DAY,
        NOW,
        5_000,
        0,
        QuotaSource.CODEX_INLINE
        if provider is Provider.CODEX
        else QuotaSource.CLAUDE_RATE_LIMIT_EVENT,
        NOW + timedelta(days=5),
        604800,
    )


def test_standard_rates_and_account_only_evidence(accounting_rows):
    project, persisted_rows = accounting_rows
    card = pricing.load_rate_card()
    observation = usage(project)
    reading = quota(project)
    later = replace(reading, observed_at=NOW + timedelta(minutes=1), percent_milli=6000)
    batch = AdapterResult((observation,), quota=(reading, later))

    projected = accounting.account_observations(batch, card, ledger=project)
    checkpoint = SourceCheckpoint(
        SourceCursor(
            observation.record.boundary.stream_ref,
            project.pseudonymize("test-locator", "codex"),
            project.pseudonymize("test-incarnation", "codex"),
            1000,
            project.pseudonymize("test-anchor", "codex"),
        ),
        ProviderCheckpoint(Provider.CODEX),
    )
    before = project.apply(replace(projected, checkpoint=checkpoint))
    view = project.as_of(before)
    prices = [
        rev.record for rev in view.current if isinstance(rev.record, PriceProjection)
    ]
    snapshots = [
        rev.record
        for rev in view.current
        if isinstance(rev.record, accounting.AccountObservation)
    ]
    spends = [
        rev.record
        for rev in view.current
        if isinstance(rev.record, accounting.SpendObservation)
    ]

    assert len(prices) == 1
    assert prices[0].usd == Decimal("0.0114")
    assert prices[0].currency == "USD"
    assert prices[0].availability is Availability.COMPLETE
    assert len(spends) == 1
    assert spends[0].availability is Availability.UNKNOWN
    assert spends[0].observation_key == observation.key
    assert sorted(sample.percent_milli for sample in snapshots) == [5000, 6000]
    assert {sample.reset_at for sample in snapshots} == {reading.reset_at}
    assert {sample.window_seconds for sample in snapshots} == {604800}
    assert {sample.account_ref for sample in snapshots} == {reading.account_ref}
    assert {sample.source for sample in snapshots} == {QuotaSource.CODEX_INLINE}
    assert {sample.precision for sample in snapshots} == {0}
    assert {sample.task_burn_availability for sample in snapshots} == {
        Availability.UNKNOWN
    }
    assert projected.checkpoint is None and projected.prior_checkpoint is None
    committed = persisted_rows.history
    assert accounting.account_observations(batch, card, ledger=project) == projected
    assert project.apply(replace(projected, checkpoint=checkpoint)) == before
    assert persisted_rows.history == committed
    assert view.checkpoints == (checkpoint,)
    assert project.as_of() == view
    totals = rollup(ITEM, view).unattributed
    assert totals.known_usd == Decimal("0.0114")
    assert totals.observation_count == 1
    assert totals.unknown_price_count == 0
    assert totals.tokens["input_tokens"] == 500
    assert totals.tokens["reasoning_output_tokens"] == 150


@pytest.mark.parametrize(
    ("model", "gross", "expected"),
    [
        (ModelLabel.GPT_6_ASTRA, 272000, "0.970000"),
        (ModelLabel.GPT_6_ASTRA, 272001, "1.915020"),
        (ModelLabel.GPT_6_1_SOL, 272000, "0.174000"),
        (ModelLabel.GPT_6_1_SOL, 272001, "0.343004"),
    ],
)
def test_openai_long_context_threshold_prices_full_request(
    pricing_evidence, reference_rates, model, gross, expected
):
    observation = replace(
        usage(pricing_evidence, model).record,
        tokens=TokenCounts(gross, 200000, 0, 0, 1000, 750, gross + 1000),
        context_tokens=gross,
    )
    with localcontext(prec=2):
        result = pricing.price(observation, reference_rates)
    assert result.usd == Decimal(expected)


def test_opus_counts_cache_ttls_once_and_allows_absent_thinking_subset(
    pricing_evidence, reference_rates
):
    obs = usage(pricing_evidence, ModelLabel.CLAUDE_OPUS_5_5).record
    obs = replace(
        obs, tokens=replace(obs.tokens, total_tokens=780, reasoning_output_tokens=None)
    )
    assert pricing.price(obs, reference_rates).usd == Decimal("0.004970")


@pytest.mark.parametrize(
    ("change", "value"),
    [
        ("model", ModelLabel.UNKNOWN),
        ("model", ModelLabel.CLAUDE_OPUS_5_5),
        ("processing_tier", None),
        ("processing_tier", ProcessingTier.FAST),
        ("processing_tier", "standard"),
        ("availability", Availability.PARTIAL),
        ("availability", Availability.UNKNOWN),
        ("context_tokens", None),
        ("context_tokens", 499),
        ("context_tokens", 272001),
        ("tokens", TokenCounts(500, None, 0, 0, 200)),
        ("tokens", TokenCounts(500, 400, None, 0, 200)),
        ("tokens", TokenCounts(500, 501, 0, 0, 200)),
        ("tokens", TokenCounts(500, 400, 0, 0, None)),
        ("tokens", TokenCounts(500, 400, 0, 0, 200, 201)),
        ("tokens", TokenCounts(500, 400, 0, 0, 200, 150, 850)),
    ],
)
def test_insufficient_or_inconsistent_usage_has_unknown_price(
    pricing_evidence, reference_rates, change, value
):
    obs = replace(usage(pricing_evidence).record, **{change: value})
    result = pricing.price(obs, reference_rates)
    assert result.usd is None
    assert result.availability is Availability.UNKNOWN
    assert result.currency == "USD"


def test_codex_never_prices_nonzero_write_ttl_even_with_coherent_context(
    pricing_evidence, reference_rates
):
    obs = replace(
        usage(pricing_evidence).record,
        tokens=TokenCounts(500, 400, 0, 1, 200, 150, 701),
        context_tokens=501,
    )
    assert pricing.price(obs, reference_rates).usd is None


def test_opus_context_includes_cache_writes_and_total_excludes_thinking(
    pricing_evidence, reference_rates
):
    obs = usage(pricing_evidence, ModelLabel.CLAUDE_OPUS_5_5).record
    rates = reference_rates
    assert pricing.price(replace(obs, context_tokens=500), rates).usd is None
    assert (
        pricing.price(
            replace(obs, tokens=replace(obs.tokens, total_tokens=930)), rates
        ).usd
        is None
    )


def test_priced_zero_is_distinct_from_missing_tokens(pricing_evidence, reference_rates):
    obs = replace(
        usage(pricing_evidence).record,
        tokens=TokenCounts(0, 0, 0, 0, 0, total_tokens=0),
        context_tokens=0,
    )
    assert pricing.price(obs, reference_rates).usd == Decimal(0)


def test_exact_usage_revision_controls_price_and_preserves_as_of(
    accounting_rows, reference_rates
):
    project, _ = accounting_rows
    card = reference_rates
    partial = usage(project, ModelLabel.CLAUDE_OPUS_5_5)
    partial = replace(
        partial, record=replace(partial.record, availability=Availability.PARTIAL)
    )
    complete = usage(project, ModelLabel.CLAUDE_OPUS_5_5, revision=2)
    diagnostic = Diagnostic(
        DiagnosticCode.COVERAGE_GAP,
        NOW,
        Provider.CLAUDE,
        partial.record.boundary.stream_ref,
        1,
    )
    earlier = accounting.account_observations(
        AdapterResult((partial,), (diagnostic,)), card, ledger=project
    )
    earlier_seq = project.apply(earlier)
    assert rollup(ITEM, project.as_of()).unattributed.unknown_price_count == 1
    assert rollup(ITEM, project.as_of()).unattributed.tokens["input_tokens"] == 500

    updated = accounting.account_observations(
        AdapterResult((complete,), quota=(quota(project, provider=Provider.CLAUDE),)),
        card,
        ledger=project,
    )
    later_seq = project.apply(updated)
    latest = project.as_of(later_seq)
    known = rollup(ITEM, latest).unattributed
    assert known.known_usd == Decimal("0.004970")
    assert known.observation_count == 1
    assert known.unknown_price_count == 0
    assert (
        rollup(ITEM, project.as_of(earlier_seq)).unattributed.unknown_price_count == 1
    )
    assert project.apply(earlier) == later_seq
    assert [
        entry.record for entry in latest.current if isinstance(entry.record, Diagnostic)
    ] == [diagnostic]
    spend_revisions = {
        entry.record.observation_revision
        for entry in latest.current
        if isinstance(entry.record, accounting.SpendObservation)
    }
    assert spend_revisions == {1, 2}

    changed_card = replace(card, version="2026-11-10")
    rebased = accounting.account_observations(
        AdapterResult((complete,)), changed_card, ledger=project
    )
    newest_seq = project.apply(rebased)
    projections = [
        entry.record
        for entry in project.as_of(newest_seq).current
        if isinstance(entry.record, PriceProjection)
        and entry.record.observation_revision == 2
    ]
    assert len({record.rate_basis for record in projections}) == 2
    assert rollup(ITEM, project.as_of(later_seq)).unattributed == known
    # U13 does not silently select one of two bases for a single usage revision.
    assert rollup(ITEM, project.as_of(newest_seq)).unattributed.unknown_price_count == 1


def test_accounting_rejects_foreign_reference_through_ledger_admission(
    accounting_rows, reference_rates, monkeypatch
):
    project, rows = accounting_rows
    other = _memory_ledger(store, UUID(int=91), project._key)
    writer = Mock(side_effect=AssertionError("Foreign data reached the writer"))
    monkeypatch.setattr(Ledger, "writer", writer)
    card = reference_rates
    sample = quota(project)
    with pytest.raises(LedgerError):
        accounting.account_observations(
            AdapterResult(quota=(quota(other),)), card, ledger=project
        )
    saved = accounting.account_observations(
        AdapterResult(quota=(sample,)), card, ledger=project
    )
    with pytest.raises(LedgerError):
        other.apply(saved)
    account = saved.revisions[0]
    with pytest.raises(LedgerError):
        project.apply(
            LedgerBatch(
                (replace(account, record=accounting.quota_snapshot(quota(other))),)
            )
        )
    assert project.as_of().sequence == 0
    assert rows.writes == []
    writer.assert_not_called()


def test_same_snapshot_identity_does_not_replace_conflicting_payload(
    accounting_rows, reference_rates
):
    project, rows = accounting_rows
    sample = quota(project)
    card = reference_rates
    accepted = accounting.account_observations(
        AdapterResult(quota=(sample,)), card, ledger=project
    )
    seq = project.apply(accepted)
    conflict = accounting.account_observations(
        AdapterResult(quota=(replace(sample, percent_milli=6000),)),
        card,
        ledger=project,
    )
    assert conflict.revisions[0].key == accepted.revisions[0].key
    before = rows.history
    with pytest.raises(ConflictError, match="Immutable revision payload conflict"):
        project.apply(conflict)
    assert project.as_of().sequence == seq
    assert project.as_of().current == accepted.revisions
    assert rows.history == before


def test_wire_values_are_canonical_closed_and_private(accounting_rows, reference_rates):
    project, committed = accounting_rows
    batch = accounting.account_observations(
        AdapterResult((usage(project),), quota=(quota(project),)),
        reference_rates,
        ledger=project,
    )
    assert project.apply(batch) == 1
    rows = [payload for _, _, _, payload in committed.history[1]]
    payloads = {json.loads(row)["record"]["kind"]: row for row in rows}
    raw_price = payloads["api-equivalent-price"]
    raw_quota = payloads["account-observation"]
    raw_spend = payloads["actual-spend"]
    assert "account-canary" not in "".join(rows)
    for row in (raw_price, raw_quota, raw_spend):
        assert _encode(_decode(row, Revision), Revision) == row
    for malformed in (
        raw_price.replace('"0.0114"', '"1.14e-2"'),
        raw_price.replace('"0.0114"', '"0.01140"'),
        raw_price.replace('"0.0114"', "0.0114"),
        raw_price.replace('"0.0114"', '"-0.0114"'),
        raw_price.replace('"USD"', '"unknown-currency-canary"'),
        raw_quota.replace('"seven-day"', '"monthly"'),
        raw_quota.replace('"percent_milli":5000', '"percent_milli":true'),
        raw_quota.replace('"precision":0', '"precision":0,"task_debit":5000'),
        raw_spend.replace('"unknown"', '"complete"'),
    ):
        assert malformed not in rows
        with pytest.raises(ValueError):
            _decode(malformed, Revision)


def test_rate_card_content_is_versioned_validated_and_immutable(
    pricing_evidence, reference_rates, monkeypatch
):
    raw = _encode(reference_rates, pricing.RateCard).encode()
    resources = Mock()
    resources.return_value.joinpath.return_value.read_bytes.return_value = raw
    monkeypatch.setattr(pricing, "files", resources)
    card = pricing.load_rate_card("2026-11-09")
    assert card == reference_rates
    resources.assert_called_once_with("aitm_usage")
    resources.return_value.joinpath.assert_called_once_with("rates", "2026-11-09.json")
    rates = json.loads(raw)
    assert pricing.RateCard.from_json(json.dumps(rates, sort_keys=True)) == card
    assert card.basis.version == "2026-11-09"
    obs = usage(pricing_evidence).record
    assert pricing.price(obs, card).usd == Decimal("0.0114")
    alternate = next(
        entry for entry in rates["entries"] if entry["model"] == "gpt-6-astra"
    )
    alternate["uncached_input"] = "12"
    edited = pricing.RateCard.from_json(json.dumps(rates))
    assert edited.basis != card.basis
    assert pricing.price(obs, edited).usd == Decimal("0.0116")
    assert pricing.price(obs, card).usd == Decimal("0.0114")
    alternate["source"] = "https://example.invalid/private-source"
    with pytest.raises(ValueError):
        pricing.RateCard.from_json(json.dumps(rates))
    alternate["source"] = next(
        entry["source"] for entry in rates["entries"] if entry["model"] == "gpt-6.1-sol"
    )
    with pytest.raises(ValueError):
        pricing.RateCard.from_json(json.dumps(rates))


def test_accounting_revision_cannot_overwrite_an_immutable_record(
    accounting_rows, reference_rates
):
    project, rows = accounting_rows
    original = usage(project)
    batch = accounting.account_observations(
        AdapterResult((original,), quota=(quota(project),)),
        reference_rates,
        ledger=project,
    )
    first = project.apply(batch)
    rows.writes.clear()
    for entry in batch.revisions[1:]:
        with pytest.raises(ValueError, match="Accounting records are immutable"):
            project.apply(LedgerBatch((replace(entry, revision=2),)))
    assert project.as_of().sequence == first
    assert rows.writes == []


@pytest.mark.parametrize(
    ("model", "requests", "totals", "expected"),
    [
        (ModelLabel.GPT_6_ASTRA, 17, (11589, 3815040, 0, 0, 19495), "4.90568"),
        (ModelLabel.GPT_6_1_SOL, 31, (164654, 3494912, 0, 0, 12790), "0.8066992"),
        (ModelLabel.GPT_6_ASTRA, 41, (127449, 5355520, 0, 0, 44520), "8.85601"),
        (ModelLabel.CLAUDE_OPUS_5_5, 45, (90, 8545714, 0, 294663, 59787), "5.2625468"),
    ],
)
def test_sanitized_spike_token_totals_at_standard_rates(
    pricing_evidence, reference_rates, model, requests, totals, expected
):
    template = usage(pricing_evidence, model).record
    priced = Decimal(0)
    # Distribute the recorded aggregate into sanitized request-sized vectors.
    # All four reported sets used Standard rates without a long-context premium.
    for index in range(requests):
        uncached, cached, write_5m, write_1h, output = (
            total // requests + (index < total % requests) for total in totals
        )
        gross = uncached + cached
        context = gross + write_5m + write_1h
        tokens = TokenCounts(
            gross, cached, write_5m, write_1h, output, total_tokens=context + output
        )
        obs = replace(template, tokens=tokens, context_tokens=context)
        priced += pricing.price(obs, reference_rates).usd
    assert priced == Decimal(expected)
