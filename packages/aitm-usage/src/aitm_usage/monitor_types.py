"""Versioned monitor payloads kept separate from the legacy usage codec."""

from dataclasses import dataclass, fields
from datetime import datetime
from enum import StrEnum

from .types import (
    Availability,
    BoundaryKind,
    DiagnosticCode,
    LedgerView,
    ModelLabel,
    SourceRef,
    TokenCounts,
    _nonnegative,
    _positive,
)


class MonitorProvider(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"
    GROK = "grok"


class MonitorModel(StrEnum):
    UNKNOWN = ModelLabel.UNKNOWN
    GPT_6_ASTRA = ModelLabel.GPT_6_ASTRA
    GPT_6_1_SOL = ModelLabel.GPT_6_1_SOL
    CLAUDE_OPUS_5_5 = ModelLabel.CLAUDE_OPUS_5_5
    GROK_4_7 = "grok-4.7"
    GROK_4_7_BUILD = "grok-4.7-build"


class NativeSurface(StrEnum):
    CODEX_DESKTOP_MACOS = "codex-desktop-macos"
    CODEX_CLI_LINUX = "codex-cli-linux"
    CLAUDE_CODE_MACOS = "claude-code-macos"
    CLAUDE_CODE_LINUX = "claude-code-linux"
    GROK_BUILD_MACOS = "grok-build-macos"


class ObservationTimeBasis(StrEnum):
    NATIVE_START = "native-start"
    NATIVE_COMPLETION = "native-completion"
    NATIVE_USAGE_EVENT = "native-usage-event"
    UNKNOWN = "unknown"


_SURFACE_PROVIDER = {
    NativeSurface.CODEX_DESKTOP_MACOS: MonitorProvider.CODEX,
    NativeSurface.CODEX_CLI_LINUX: MonitorProvider.CODEX,
    NativeSurface.CLAUDE_CODE_MACOS: MonitorProvider.CLAUDE,
    NativeSurface.CLAUDE_CODE_LINUX: MonitorProvider.CLAUDE,
}
_REVISION_FORMAT = "aitm.usage.monitor-revision/v1"


@dataclass(frozen=True, slots=True)
class ProviderCostEvidence:
    """Provider-reported ticks, separate from monetary estimates and spend."""

    ticks: int

    def __post_init__(self) -> None:
        _nonnegative(self.ticks)


@dataclass(frozen=True, slots=True)
class MonitorObservation:
    provider: MonitorProvider
    native_surface: NativeSurface
    observed_at: datetime | None
    time_basis: ObservationTimeBasis
    tokens: TokenCounts
    coverage: Availability
    model: MonitorModel = MonitorModel.UNKNOWN
    provider_cost: ProviderCostEvidence | None = None

    def __post_init__(self) -> None:
        if _SURFACE_PROVIDER.get(self.native_surface) is not self.provider:
            raise ValueError("Monitor provider and native surface disagree")
        if self.model in (MonitorModel.GROK_4_7, MonitorModel.GROK_4_7_BUILD):
            raise ValueError("Grok requires a Grok observation")
        if (self.observed_at is None) != (
            self.time_basis is ObservationTimeBasis.UNKNOWN
        ):
            raise ValueError("Monitor observation time and time basis disagree")


@dataclass(frozen=True, slots=True)
class GrokTokenCounts:
    """Disjoint Grok input buckets and reasoning included within output."""

    uncached_input_tokens: int | None = None
    cache_read_tokens: int | None = None
    cache_creation_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                _nonnegative(value)
        priced = (
            self.uncached_input_tokens,
            self.cache_read_tokens,
            self.cache_creation_tokens,
            self.output_tokens,
        )
        if self.total_tokens is not None and None not in priced:
            if sum(priced) != self.total_tokens:
                raise ValueError("Grok token total disagrees with its categories")
        if self.reasoning_output_tokens is not None and self.output_tokens is not None:
            if self.reasoning_output_tokens > self.output_tokens:
                raise ValueError("Grok reasoning exceeds its output")


@dataclass(frozen=True, slots=True)
class GrokObservation:
    provider: MonitorProvider
    native_surface: NativeSurface
    observed_at: datetime | None
    time_basis: ObservationTimeBasis
    tokens: GrokTokenCounts
    coverage: Availability
    model: MonitorModel = MonitorModel.UNKNOWN
    provider_cost: ProviderCostEvidence | None = None

    def __post_init__(self) -> None:
        if (
            self.provider is not MonitorProvider.GROK
            or self.native_surface is not NativeSurface.GROK_BUILD_MACOS
            or self.model
            not in (
                MonitorModel.UNKNOWN,
                MonitorModel.GROK_4_7,
                MonitorModel.GROK_4_7_BUILD,
            )
        ):
            raise ValueError("Invalid Grok provider, surface or model")
        if self.time_basis is ObservationTimeBasis.NATIVE_COMPLETION:
            if (
                self.observed_at is not None
                and self.observed_at.utcoffset() is not None
            ):
                return
        if self.time_basis is ObservationTimeBasis.UNKNOWN and self.observed_at is None:
            return
        raise ValueError("Grok observation time and time basis disagree")


@dataclass(frozen=True, slots=True)
class GrokBoundary:
    stream_ref: SourceRef
    session_ref: SourceRef
    ordinal: int
    boundary_ref: SourceRef
    receipt_ref: SourceRef

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)

    @property
    def provider(self) -> MonitorProvider:
        return MonitorProvider.GROK

    @property
    def kind(self) -> BoundaryKind:
        return BoundaryKind.TURN


@dataclass(frozen=True, slots=True)
class GrokDiagnostic:
    code: DiagnosticCode
    observed_at: datetime
    source_ref: SourceRef
    observation_key: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class GrokCompletion:
    key: SourceRef
    ordinal: int
    observed_at: datetime
    observation: GrokObservation | None
    native_content_ref: SourceRef | None
    receipt_ref: SourceRef | None

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)
        if self.observation is None:
            if self.native_content_ref is not None or self.receipt_ref is not None:
                raise ValueError("Excluded Grok completion can retain only lineage")
        elif (
            self.observation.observed_at != self.observed_at
            or self.native_content_ref is None
        ):
            raise ValueError("Grok completion evidence disagrees with its observation")


@dataclass(frozen=True, slots=True)
class GrokCheckpoint:
    stream_ref: SourceRef
    incarnation_ref: SourceRef
    offset: int
    prefix_ref: SourceRef
    completions: tuple[GrokCompletion, ...]

    def __post_init__(self) -> None:
        _nonnegative(self.offset)


@dataclass(frozen=True, slots=True)
class MonitorRevision:
    key: SourceRef
    revision: int
    observation: MonitorObservation | GrokObservation
    format: str = _REVISION_FORMAT

    def __post_init__(self) -> None:
        _positive(self.revision)
        if self.format != _REVISION_FORMAT:
            raise ValueError("Unsupported monitor revision format")


@dataclass(frozen=True, slots=True)
class MonitorLedgerView:
    legacy: LedgerView
    revisions: tuple[MonitorRevision, ...]
