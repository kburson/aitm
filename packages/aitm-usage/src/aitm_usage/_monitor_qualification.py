"""Private contracts used to consume live-source authorization."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from .ledger import LedgerError, _PinnedPath
from .types import SourceRef

if TYPE_CHECKING:
    from .monitor_registry import ApprovedSource, _PhysicalDirectory


_TARGETS = {
    ("codex", "codex-desktop-macos", "Darwin", "arm64"),
    ("codex", "codex-cli-linux", "Linux", "arm64"),
    ("codex", "codex-cli-linux", "Linux", "aarch64"),
    ("codex", "codex-cli-linux", "Linux", "x86_64"),
    ("grok", "grok-build-macos", "Darwin", "arm64"),
    ("grok", "grok-build-linux", "Linux", "arm64"),
    ("grok", "grok-build-linux", "Linux", "aarch64"),
    ("grok", "grok-build-linux", "Linux", "x86_64"),
}


@dataclass(frozen=True, slots=True)
class _LiveSourceTuple:
    provider: str
    surface: str
    system: str
    architecture: str
    build: str
    format_version: int

    def supported(self) -> bool:
        return (self.provider, self.surface, self.system, self.architecture) in _TARGETS

    @classmethod
    def from_approval(cls, source: ApprovedSource) -> _LiveSourceTuple:
        request = source.approval
        return cls(
            request.provider,
            request.surface,
            request.platform,
            request.architecture,
            request.client_version,
            request.format_version,
        )


@dataclass(frozen=True, slots=True)
class _InstallationProof:
    directory: _PhysicalDirectory = field(repr=False)
    source: _LiveSourceTuple
    executable: SourceRef = field(repr=False)


@dataclass(frozen=True, slots=True)
class _LiveProfile:
    root: _PhysicalDirectory = field(repr=False)
    lease: _PinnedPath = field(repr=False)
    generation: SourceRef
    installations: tuple[_InstallationProof, ...]
    current: Callable[[_InstallationProof], bool] | None = field(repr=False)


@dataclass(frozen=True, slots=True)
class _LiveSourceProof:
    profile: _LiveProfile = field(repr=False)
    installation: _InstallationProof = field(repr=False)


@dataclass(frozen=True, slots=True)
class _LiveExclusion:
    source_id: UUID
    generation: SourceRef
    installation: SourceRef


class _LiveSourceUnavailable(LedgerError):
    def __init__(self, decision: _LiveExclusion | None = None) -> None:
        super().__init__("Live source qualification is unavailable")
        self.decision = decision
