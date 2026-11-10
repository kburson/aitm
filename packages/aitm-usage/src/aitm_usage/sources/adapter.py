"""Read-only, service-keyed provider evidence for the monitor."""

import platform
from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path

from ..monitor_types import NativeSurface, ObservationTimeBasis
from ..types import (
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    Provider,
    Registration,
    SourceBoundary,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
)
from .claude import ClaudeState, read_claude, retains_streamed_prefix
from .codex import CodexState, read_codex
from .scan import CandidateSource, SourceEvidence, _discover_sources, scan


@dataclass(frozen=True, slots=True)
class SourceRoot:
    """One approved root and a pinned, service-scoped evidence view."""

    path: Path = field(repr=False)
    cutoff: datetime
    checkout_anchors: tuple[Path, ...] = field(repr=False)
    evidence: SourceEvidence = field(repr=False)


@dataclass(frozen=True, slots=True)
class SourceLocator:
    """Transient scanner handle. Persist its keyed stream reference instead."""

    _source: CandidateSource = field(repr=False)

    @property
    def stream_ref(self) -> SourceRef:
        return self._source.stream_ref


@dataclass(frozen=True, slots=True)
class StreamCursor:
    """Persist the entire checkpoint with the accepted frontier in one write."""

    checkpoint: SourceCheckpoint


@dataclass(frozen=True, slots=True)
class NativeObservation:
    key: SourceRef
    revision: int
    usage: UsageObservation
    native_surface: NativeSurface
    time_basis: ObservationTimeBasis
    project_context: SourceRef | None


@dataclass(frozen=True, slots=True)
class NativeBoundary:
    """Linked native evidence. Scope authorization belongs to the router."""

    boundary: SourceBoundary
    project_context: SourceRef | None


@dataclass(frozen=True, slots=True)
class AdapterBatch:
    observations: tuple[NativeObservation, ...] = ()
    boundaries: tuple[NativeBoundary, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    cursor: StreamCursor | None = None


class ProviderAdapter:
    """Bridge the qualified macOS Codex Desktop and Claude Code surfaces."""

    def discover(self, root: SourceRoot) -> Iterator[SourceLocator]:
        registration = Registration(
            root.evidence.as_of().project_id,
            root.path,
            (root.path,),
            root.checkout_anchors,
            root.cutoff,
        )
        for candidate in _discover_sources(registration, root.evidence):
            yield SourceLocator(replace(candidate, _monitor=True))

    def read_delta(
        self, locator: SourceLocator, cursor: StreamCursor | None
    ) -> AdapterBatch:
        source = locator._source
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

        frames = scan(source, cursor.checkpoint if cursor is not None else None, cutoff)
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

        observations = []
        for revision in result.revisions:
            usage = revision.record
            if not isinstance(usage, UsageObservation):
                continue
            proof = frames.scope_evidence(usage.boundary)
            observations.append(
                NativeObservation(
                    revision.key,
                    revision.revision,
                    usage,
                    surface,
                    ObservationTimeBasis.NATIVE_USAGE_EVENT,
                    proof.anchor_ref if proof is not None else None,
                )
            )
        return AdapterBatch(
            tuple(observations),
            boundaries,
            result.diagnostics,
            StreamCursor(SourceCheckpoint(frames.cursor, result.provider_checkpoint)),
        )
