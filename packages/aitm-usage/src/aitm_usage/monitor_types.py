"""Versioned monitor payloads kept separate from the legacy usage codec."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .types import (
    Availability,
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


class MonitorModel(StrEnum):
    UNKNOWN = ModelLabel.UNKNOWN
    GPT_6_ASTRA = ModelLabel.GPT_6_ASTRA
    GPT_6_1_SOL = ModelLabel.GPT_6_1_SOL
    CLAUDE_OPUS_5_5 = ModelLabel.CLAUDE_OPUS_5_5


class NativeSurface(StrEnum):
    CODEX_DESKTOP_MACOS = "codex-desktop-macos"
    CODEX_CLI_LINUX = "codex-cli-linux"
    CLAUDE_CODE_MACOS = "claude-code-macos"
    CLAUDE_CODE_LINUX = "claude-code-linux"


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
        if (self.observed_at is None) != (
            self.time_basis is ObservationTimeBasis.UNKNOWN
        ):
            raise ValueError("Monitor observation time and time basis disagree")


@dataclass(frozen=True, slots=True)
class MonitorRevision:
    key: SourceRef
    revision: int
    observation: MonitorObservation
    format: str = _REVISION_FORMAT

    def __post_init__(self) -> None:
        _positive(self.revision)
        if self.format != _REVISION_FORMAT:
            raise ValueError("Unsupported monitor revision format")


@dataclass(frozen=True, slots=True)
class MonitorLedgerView:
    legacy: LedgerView
    revisions: tuple[MonitorRevision, ...]
