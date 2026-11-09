"""Standard public API-equivalent pricing for exact normalized requests."""

from dataclasses import dataclass
from decimal import Context, Decimal, localcontext
from enum import StrEnum
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files

from .types import (
    Availability,
    BoundaryKind,
    Currency,
    ModelLabel,
    PriceResult,
    ProcessingTier,
    Provider,
    RateBasis,
    UsageObservation,
    _decode,
    _encode,
    _positive,
    _rate_version,
)

_DEFAULT_VERSION = "2026-11-09"


class _RateSource(StrEnum):
    ASTRA = "https://developers.openai.com/api/docs/models/gpt-6-astra#pricing"
    SOL = "https://developers.openai.com/api/docs/models/gpt-6.1-sol#pricing"
    OPUS = "https://platform.claude.com/docs/en/models/opus-5-5/overview#pricing"


_MODELS = {
    ModelLabel.GPT_6_ASTRA: (Provider.CODEX, _RateSource.ASTRA),
    ModelLabel.GPT_6_1_SOL: (Provider.CODEX, _RateSource.SOL),
    ModelLabel.CLAUDE_OPUS_5_5: (Provider.CLAUDE, _RateSource.OPUS),
}


def _validate_rate(value: Decimal, places: int) -> None:
    if (
        type(value) is not Decimal
        or not value.is_finite()
        or not 0 < value <= 1_000_000
        or value.as_tuple().exponent < -places
    ):
        raise ValueError("Invalid per-million rate or pricing multiplier")


@dataclass(frozen=True, slots=True)
class _ModelRate:
    model: ModelLabel
    provider: Provider
    source: _RateSource
    uncached_input: Decimal
    cache_read: Decimal
    cache_write: Decimal | None
    cache_write_5m: Decimal | None
    cache_write_1h: Decimal | None
    output: Decimal

    def __post_init__(self) -> None:
        if _MODELS.get(self.model) != (self.provider, self.source):
            raise ValueError("Rate source does not match its model and provider")
        if self.provider is Provider.CODEX:
            if self.cache_write_5m is not None or self.cache_write_1h is not None:
                raise ValueError("Codex rates do not have a write TTL class")
            writes = (self.cache_write,)
        else:
            if self.cache_write is not None:
                raise ValueError("Claude rates require distinct write TTL classes")
            writes = (self.cache_write_5m, self.cache_write_1h)
        for rate in (self.uncached_input, self.cache_read, self.output, *writes):
            _validate_rate(rate, 6)


@dataclass(frozen=True, slots=True)
class _LongContextRate:
    input_threshold: int
    input_multiplier: Decimal
    output_multiplier: Decimal

    def __post_init__(self) -> None:
        _positive(self.input_threshold)
        for factor in (self.input_multiplier, self.output_multiplier):
            _validate_rate(factor, 1)
            if not 1 <= factor <= 10:
                raise ValueError("Invalid long-context pricing multiplier")


@dataclass(frozen=True, slots=True)
class RateCard:
    """Immutable public text rates and the rules used to compute a comparison."""

    version: str
    currency: Currency
    tier: ProcessingTier
    codex_long_context: _LongContextRate
    entries: tuple[_ModelRate, ...]

    def __post_init__(self) -> None:
        _rate_version(self.version)
        if (
            self.currency is not Currency.USD
            or self.tier is not ProcessingTier.STANDARD
        ):
            raise ValueError("Only Standard USD rate cards are supported")
        _encode(self, RateCard)
        if not self.entries or len({row.model for row in self.entries}) != len(
            self.entries
        ):
            raise ValueError("Expected distinct, supported model rates")
        object.__setattr__(
            self,
            "entries",
            tuple(sorted(self.entries, key=lambda row: row.model.value)),
        )

    @classmethod
    def from_json(cls, data: str | bytes) -> "RateCard":
        return _decode(data, cls)

    @property
    @lru_cache(maxsize=8)
    def basis(self) -> RateBasis:
        digest = sha256(_encode(self, RateCard).encode("utf-8")).hexdigest()
        return RateBasis(self.version, digest, self.currency)


def load_rate_card(version: str = _DEFAULT_VERSION) -> RateCard:
    """Load a versioned card from the installed package."""
    _rate_version(version)
    data = files("aitm_usage").joinpath("rates", f"{version}.json").read_bytes()
    card = RateCard.from_json(data)
    if card.version != version:
        raise ValueError("Rate card version does not match its resource")
    return card


def _amount(usage: UsageObservation, rates: RateCard) -> Decimal | None:
    if (
        usage.availability is not Availability.COMPLETE
        or usage.boundary.kind is not BoundaryKind.REQUEST
        or usage.processing_tier is not rates.tier
    ):
        return None

    entry = next(
        (
            row
            for row in rates.entries
            if row.model is usage.model and row.provider is usage.boundary.provider
        ),
        None,
    )
    if entry is None:
        return None

    counts = usage.tokens
    gross, cached, write_5m, write_1h, output = (
        counts.input_tokens,
        counts.cached_input_tokens,
        counts.cache_write_5m_tokens,
        counts.cache_write_1h_tokens,
        counts.output_tokens,
    )
    if None in (gross, cached, write_5m, write_1h, output):
        return None
    context = gross + write_5m + write_1h
    if (
        cached > gross
        or usage.context_tokens != context
        or counts.reasoning_output_tokens is not None
        and counts.reasoning_output_tokens > output
        or counts.total_tokens is not None
        and counts.total_tokens != context + output
    ):
        return None

    # This precision covers all accepted integer counts and decimal rates,
    # independent of the caller's Decimal settings.
    with localcontext(Context(prec=64)):
        inputs = (gross - cached) * entry.uncached_input + cached * entry.cache_read
        outputs = output * entry.output
        if entry.provider is Provider.CODEX:
            if write_5m or write_1h:
                return None
            long = rates.codex_long_context
            if context > long.input_threshold:
                inputs *= long.input_multiplier
                outputs *= long.output_multiplier
        else:
            inputs += write_5m * entry.cache_write_5m + write_1h * entry.cache_write_1h
        return (inputs + outputs).scaleb(-6)


def price(usage: UsageObservation, rates: RateCard) -> PriceResult:
    """Return a public API comparison, or explicit Unknown for insufficient evidence."""
    usd = _amount(usage, rates)
    availability = Availability.UNKNOWN if usd is None else Availability.COMPLETE
    return PriceResult(rates.basis, availability, usd)
