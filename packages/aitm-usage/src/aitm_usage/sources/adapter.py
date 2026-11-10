"""Read-only, service-keyed provider evidence for the monitor."""

import platform
from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from uuid import UUID

from ..monitor_types import (
    GrokBoundary,
    GrokCheckpoint,
    GrokDiagnostic,
    GrokObservation,
    NativeSurface,
    ObservationTimeBasis,
)
from ..types import (
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    Provider,
    SourceBoundary,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
)
from .claude import ClaudeState, read_claude, retains_streamed_prefix
from .codex import CodexState, read_codex
from .scan import CandidateSource, SourceEvidence, _discover_sources, _Snapshot, scan


@dataclass(frozen=True, slots=True)
class SourceRoot:
    """One approved root and a pinned, service-scoped evidence view."""

    path: Path = field(repr=False)
    cutoff: datetime
    checkout_anchors: tuple[Path, ...] = field(repr=False)
    evidence: SourceEvidence = field(repr=False)

    @property
    def project_id(self) -> UUID:
        # The existing scanner calls this its namespace. In the monitor it
        # identifies the service evidence, without identifying a destination.
        return self.evidence.as_of().project_id

    @property
    def source_roots(self) -> tuple[Path, ...]:
        return (self.path,)


@dataclass(frozen=True, slots=True)
class GrokOrigin:
    """Transient writer and lineage proof supplied by the approved source context."""

    session_id: str = field(repr=False)
    system: str
    architecture: str
    version: str
    build: str
    executable_digest: str
    format_version: int
    lineage_id: str | None = field(repr=False)
    incarnation: SourceRef
    checkout: SourceRef | None = None
    inherited_prompt_ids: frozenset[str] = field(default=frozenset(), repr=False)


@dataclass(frozen=True, slots=True)
class _GrokSource:
    path: Path = field(repr=False)
    origin: GrokOrigin | None = field(repr=False)
    root: SourceRoot = field(repr=False)
    snapshot: _Snapshot = field(repr=False)
    stream_ref: SourceRef


@dataclass(frozen=True, slots=True)
class SourceLocator:
    """Transient scanner handle. Persist its keyed stream reference instead."""

    _source: CandidateSource | _GrokSource = field(repr=False)

    @property
    def stream_ref(self) -> SourceRef:
        return self._source.stream_ref


@dataclass(frozen=True, slots=True)
class StreamCursor:
    """Persist the entire checkpoint with the accepted frontier in one write."""

    checkpoint: SourceCheckpoint | GrokCheckpoint


@dataclass(frozen=True, slots=True)
class NativeObservation:
    key: SourceRef
    revision: int
    usage: UsageObservation | GrokObservation
    native_surface: NativeSurface
    time_basis: ObservationTimeBasis
    project_context: SourceRef | None


@dataclass(frozen=True, slots=True)
class NativeBoundary:
    """Linked native evidence. Match repeats by boundary identity on replay."""

    boundary: SourceBoundary | GrokBoundary
    project_context: SourceRef | None


@dataclass(frozen=True, slots=True)
class AdapterBatch:
    """Evidence only. A missing cursor supplies no new checkpoint."""

    observations: tuple[NativeObservation, ...] = ()
    boundaries: tuple[NativeBoundary, ...] = ()
    diagnostics: tuple[Diagnostic | GrokDiagnostic, ...] = ()
    cursor: StreamCursor | None = None


class ProviderAdapter:
    """Bridge the qualified macOS Codex Desktop and Claude Code surfaces."""

    def discover(self, root: SourceRoot) -> Iterator[SourceLocator]:
        for candidate in _discover_sources(root, root.evidence):
            yield SourceLocator(replace(candidate, _monitor=True))

    def read_delta(
        self, locator: SourceLocator, cursor: StreamCursor | None
    ) -> AdapterBatch:
        source = locator._source
        if not isinstance(source, CandidateSource):
            return AdapterBatch()
        checkpoint = cursor.checkpoint if cursor is not None else None
        if checkpoint is not None and not isinstance(checkpoint, SourceCheckpoint):
            return AdapterBatch()
        surface = source._native_surface
        cutoff = source._registration.cutoff
        if surface is None or (platform.system(), platform.machine()) != (
            "Darwin",
            "arm64",
        ):
            return AdapterBatch(
                diagnostics=(
                    Diagnostic(
                        DiagnosticCode.UNSUPPORTED_FORMAT,
                        cutoff,
                        source.provider,
                        source.stream_ref,
                    ),
                )
            )

        frames = scan(source, checkpoint, cutoff)
        if frames.cursor is None:
            return AdapterBatch(diagnostics=frames.diagnostics)
        if source.provider is Provider.CODEX:
            result = read_codex(
                frames,
                CodexState(source._ledger, neutral_markers=True),
                Eligibility.ELIGIBLE,
            )
            retains_prefix = True
        else:
            state = ClaudeState(source._ledger, neutral_markers=True)
            result = read_claude(frames, state, Eligibility.ELIGIBLE)
            retains_prefix = (
                result.provider_checkpoint is not None
                and retains_streamed_prefix(frames, state, result.provider_checkpoint)
            )

        boundaries = tuple(
            NativeBoundary(proof.boundary, proof.anchor_ref)
            for boundary in result.boundaries
            if (proof := frames.scope_evidence(boundary)) is not None
        )
        if not retains_prefix or result.provider_checkpoint is None:
            return AdapterBatch(
                boundaries=boundaries,
                diagnostics=(
                    *result.diagnostics,
                    Diagnostic(
                        DiagnosticCode.BOUNDARY_UNVERIFIED,
                        cutoff,
                        source.provider,
                        source.stream_ref,
                    ),
                ),
                cursor=cursor,
            )

        prior_checkout = dict(frames._prior_checkout)
        observations = []
        for revision in result.revisions:
            usage = revision.record
            if not isinstance(usage, UsageObservation):
                continue
            boundary = usage.boundary
            proof = frames.scope_evidence(boundary)
            context = proof.anchor_ref if proof is not None else None
            if proof is None and source._matches(boundary):
                context = prior_checkout.get(boundary.ordinal)
            observations.append(
                NativeObservation(
                    revision.key,
                    revision.revision,
                    usage,
                    surface,
                    ObservationTimeBasis.NATIVE_USAGE_EVENT,
                    context,
                )
            )
        return AdapterBatch(
            tuple(observations),
            boundaries,
            result.diagnostics,
            StreamCursor(SourceCheckpoint(frames.cursor, result.provider_checkpoint)),
        )
