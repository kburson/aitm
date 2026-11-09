"""Project provider usage into independent price, quota and spend records."""

import json
from dataclasses import fields
from datetime import UTC

from .ledger import Ledger
from .pricing import RateCard, price
from .types import (
    AccountObservation,
    AdapterResult,
    Diagnostic,
    LedgerBatch,
    PriceObservation,
    QuotaEvidence,
    Revision,
    SpendObservation,
    UsageObservation,
    _encode,
)


def quota_snapshot(raw: QuotaEvidence) -> AccountObservation:
    """Retain one account-window sample without assigning it to a request."""
    if type(raw) is not QuotaEvidence:
        raise ValueError("Expected structured quota evidence")
    return AccountObservation(
        **{field.name: getattr(raw, field.name) for field in fields(QuotaEvidence)}
    )


def _identity(*parts: str | int | None) -> str:
    return json.dumps(parts, separators=(",", ":"))


def account_observations(
    batch: AdapterResult, rates: RateCard, *, ledger: Ledger
) -> LedgerBatch:
    """Return a revisions-only batch for atomic apply with the scanner checkpoint."""
    revisions = list(batch.revisions)
    for source in batch.revisions:
        if not isinstance(source.record, UsageObservation):
            continue
        ledger.validate_source_ref(source.key)
        result = price(source.record, rates)
        observation = PriceObservation(source.key, source.revision, result)
        price_ref = ledger.pseudonymize(
            "api-equivalent-price",
            _identity(source.key.value, source.revision, observation.rate_basis),
        )
        spend_ref = ledger.pseudonymize(
            "actual-spend", _identity(source.key.value, source.revision)
        )
        revisions.extend(
            (
                Revision(price_ref, 1, observation),
                Revision(spend_ref, 1, SpendObservation(source.key, source.revision)),
            )
        )

    for evidence in batch.quota:
        ledger.validate_quota(evidence)
        snapshot = quota_snapshot(evidence)
        reset = snapshot.reset_at
        key = ledger.pseudonymize(
            "account-observation",
            _identity(
                snapshot.provider.value,
                snapshot.account_ref.value,
                snapshot.bucket.value,
                snapshot.source.value,
                snapshot.observed_at.astimezone(UTC).isoformat(),
                reset.astimezone(UTC).isoformat() if reset is not None else None,
                snapshot.window_seconds,
            ),
        )
        revisions.append(Revision(key, 1, snapshot))

    for diagnostic in batch.diagnostics:
        payload = _encode(
            diagnostic, Diagnostic, validate_ref=ledger.validate_source_ref
        )
        key = ledger.pseudonymize("accounting-diagnostic", payload)
        revisions.append(Revision(key, 1, diagnostic))

    return LedgerBatch(tuple(revisions))
