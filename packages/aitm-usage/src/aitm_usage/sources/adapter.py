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
    AdapterResult,
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    Provider,
    Revision,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    UsageObservation,
    _encode,
    _nonnegative,
)
from .claude import (
    _EMPTY,
    ClaudeState,
    _ClaudeRevisionKind,
    _first_unretained_request,
    _read_claude,
    _RevisionRecorder,
    read_claude,
    retains_streamed_prefix,
)
from .codex import CodexState, _CodexCompletionWitness, _read_codex
from .scan import (
    CandidateSource,
    FrameBatch,
    SidebandFrame,
    SourceEvidence,
    SourceFrame,
    _discover_sources,
    _Snapshot,
    scan,
)


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
class NativePosition:
    """Service-keyed position evidenced by the native stream."""

    session_ref: SourceRef
    stream_ref: SourceRef
    ordinal: int

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)


@dataclass(frozen=True, slots=True)
class NativeObservation:
    key: SourceRef
    revision: int
    usage: UsageObservation | GrokObservation
    native_surface: NativeSurface
    time_basis: ObservationTimeBasis
    project_context: SourceRef | None
    position: NativePosition | None = None
    span_end: int | None = None


@dataclass(frozen=True, slots=True)
class _NativeRevisionWitness:
    predecessor: NativeObservation
    predecessor_material: SourceRef
    successor_material: SourceRef
    predecessor_ordinal: int
    later_ordinal: int
    prefix_ref: SourceRef
    kind: _ClaudeRevisionKind
    terminal_contributor_spans: tuple[tuple[int, int], ...]


@dataclass(frozen=True, slots=True)
class _ClaudeReadRevision:
    predecessor_id: int
    predecessor_ordinal: int
    later_ordinal: int
    prefix_ref: SourceRef
    kind: _ClaudeRevisionKind
    terminal_contributor_spans: tuple[tuple[int, int], ...]


def _claude_revision_material(
    evidence: SourceEvidence, observation: NativeObservation
) -> SourceRef:
    if not isinstance(observation.usage, UsageObservation):
        raise ValueError("Expected native Claude usage")
    revision = Revision(observation.key, observation.revision, observation.usage)
    return evidence.pseudonymize(
        "claude-revision-material", _encode(revision, Revision)
    )


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


def _read_usage(
    source: CandidateSource,
    frames: FrameBatch,
    record_revision: _RevisionRecorder | None,
    completion_witnesses: list[_CodexCompletionWitness] | None = None,
) -> tuple[AdapterResult, dict[SourceRef, int], bool]:
    if source.provider is Provider.CODEX:
        result, _, span_ends = _read_codex(
            frames,
            CodexState(source._ledger, neutral_markers=True),
            Eligibility.ELIGIBLE,
            _completion_witnesses=completion_witnesses,
        )
        return result, span_ends, True
    state = ClaudeState(source._ledger, neutral_markers=True)
    if record_revision is None:
        result = read_claude(frames, state, Eligibility.ELIGIBLE)
    else:
        result, _, _ = _read_claude(
            frames, state, Eligibility.ELIGIBLE, record_revision
        )
    retains_prefix = result.provider_checkpoint is not None and retains_streamed_prefix(
        frames, state, result.provider_checkpoint
    )
    return result, {}, retains_prefix


class ProviderAdapter:
    """Bridge the qualified macOS Codex Desktop and Claude Code surfaces."""

    def discover(self, root: SourceRoot) -> Iterator[SourceLocator]:
        for candidate in _discover_sources(root, root.evidence):
            yield SourceLocator(replace(candidate, _monitor=True))

    def _capture_gap_start(
        self,
        locator: SourceLocator,
        prior: SourceCheckpoint,
        *,
        first_unverified: int,
        limit: SourceCursor,
    ) -> int | None:
        """Return the first native ordinal still unsettled at a capture fence."""
        source = locator._source
        if not isinstance(source, CandidateSource):
            raise ValueError("Expected a capture-qualified native locator")
        # A registry fence has native evidence only. Claude's incremental walk
        # requires prior revisions, so rebuild them transiently from this exact prefix.
        cursor = prior if source.provider is Provider.CODEX else None
        batch = scan(source, cursor, source._registration.cutoff, _capture_limit=limit)
        if batch.cursor is None:
            raise ValueError(
                "Native capture scan could not authenticate its fixed prefix"
            )
        held = [frame.ordinal for frame in batch.frames[len(batch.commit_frames) :]]
        if source.provider is Provider.CODEX:
            _, unsettled, _ = _read_codex(
                batch,
                CodexState(source._ledger, neutral_markers=True),
                Eligibility.ELIGIBLE,
            )
            if unsettled is not None:
                held.append(unsettled)
        else:
            state = ClaudeState(source._ledger, neutral_markers=True)
            result, observed, unsettled = _read_claude(
                batch, state, Eligibility.ELIGIBLE
            )
            if observed is None:
                held.append(first_unverified)
            else:
                native_requests = {
                    item.record.request_ref
                    for item in result.revisions
                    if isinstance(item.record, UsageObservation)
                    and item.record.boundary.stream_ref == source.stream_ref
                }
                requests = tuple(
                    item
                    for item in observed.request_prefix
                    if item.request_ref in native_requests and item.tokens != _EMPTY
                )
                last_complete = max(
                    (item.ordinal for item in requests if item.complete),
                    default=first_unverified - 1,
                )
                # A later completed request closes an abandoned provisional suffix.
                start = max(first_unverified, last_complete + 1)
                if unsettled is not None and unsettled >= first_unverified:
                    held.append(unsettled)
                unretained = _first_unretained_request(
                    batch, state, observed, start=start
                )
                if unretained is not None:
                    held.append(unretained)
                held.extend(
                    item.ordinal
                    for item in requests
                    if not item.complete and item.ordinal >= start
                )
        return min(held, default=None)

    def read_delta(
        self,
        locator: SourceLocator,
        cursor: StreamCursor | None,
        *,
        _scope_boundaries: tuple[SourceBoundary, ...] = (),
        _capture_limit: SourceCursor | None = None,
        _revision_witnesses: list[tuple[NativeObservation, _NativeRevisionWitness]]
        | None = None,
        _completion_witnesses: list[_CodexCompletionWitness] | None = None,
    ) -> AdapterBatch:
        if _completion_witnesses is not None:
            _completion_witnesses.clear()
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

        read_revisions: dict[int, _ClaudeReadRevision] = {}

        def record_revision(
            predecessor: Revision,
            successor: Revision,
            prior_ordinal: int,
            frame: SourceFrame | SidebandFrame,
            terminal_contributors: tuple[tuple[int, int], ...],
        ) -> None:
            kind = (
                _ClaudeRevisionKind.COST_STATE
                if isinstance(frame, SidebandFrame)
                else _ClaudeRevisionKind(frame.row["type"])
            )
            prefix_ref = source._ledger.pseudonymize(
                "claude-revision-prefix",
                f"{frame.stream_ref.value}:{frame.ordinal}:{frame._prefix}",
            )
            read_revisions[id(successor)] = _ClaudeReadRevision(
                id(predecessor),
                prior_ordinal,
                frame.ordinal,
                prefix_ref,
                kind,
                terminal_contributors,
            )

        recorder = record_revision if _revision_witnesses is not None else None
        frames = scan(source, checkpoint, cutoff, _capture_limit=_capture_limit)
        if frames.cursor is None:
            return AdapterBatch(diagnostics=frames.diagnostics)
        completion = [] if _completion_witnesses is not None else None
        result, span_ends, retains_prefix = _read_usage(
            source, frames, recorder, completion
        )
        scope_verified = True
        if _scope_boundaries:
            requested = set(_scope_boundaries)
            selected = {
                boundary: frame._prefix
                for boundary in result.boundaries
                if boundary in requested
                and boundary.receipt_ref is not None
                and (frame := frames._matching_frame(boundary)) is not None
                and frame.anchor_ref is None
            }
            if selected:
                read_revisions.clear()
                if completion is not None:
                    completion.clear()
                for boundary, prefix in selected.items():
                    source = source._select_boundary(boundary, prefix, None)
                frames = scan(source, checkpoint, cutoff, _capture_limit=_capture_limit)
                if frames.cursor is None:
                    return AdapterBatch(diagnostics=frames.diagnostics, cursor=cursor)
                result, span_ends, retains_prefix = _read_usage(
                    source, frames, recorder, completion
                )
                scope_verified = all(
                    boundary in result.boundaries
                    and (frame := frames._matching_frame(boundary)) is not None
                    and frame.anchor_ref is None
                    and frame._prefix == prefix
                    for boundary, prefix in selected.items()
                )

        boundaries = tuple(
            NativeBoundary(proof.boundary, proof.anchor_ref)
            for boundary in result.boundaries
            if (proof := frames.scope_evidence(boundary)) is not None
        )
        if (
            not scope_verified
            or not retains_prefix
            or result.provider_checkpoint is None
        ):
            if (
                _completion_witnesses is not None
                and completion is not None
                and len(completion) == 1
                and scope_verified
                and result.provider_checkpoint is None
                and not result.diagnostics
                and _capture_limit is not None
                and frames.cursor == _capture_limit
            ):
                witness = completion[0]
                if any(
                    item.boundary == witness.request
                    and item.project_context == witness.checkout
                    for item in boundaries
                ):
                    _completion_witnesses.append(witness)
            return AdapterBatch(
                boundaries=boundaries if scope_verified else (),
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
        observations: dict[int, NativeObservation] = {}
        for revision in result.revisions:
            usage = revision.record
            if not isinstance(usage, UsageObservation):
                continue
            boundary = usage.boundary
            proof = frames.scope_evidence(boundary)
            context = proof.anchor_ref if proof is not None else None
            if proof is None and source._matches(boundary):
                context = prior_checkout.get(boundary.ordinal)
            observations[id(revision)] = NativeObservation(
                revision.key,
                revision.revision,
                usage,
                surface,
                ObservationTimeBasis.NATIVE_USAGE_EVENT,
                context,
                span_end=span_ends.get(revision.key),
            )
        batch = AdapterBatch(
            tuple(observations.values()),
            boundaries,
            result.diagnostics,
            StreamCursor(SourceCheckpoint(frames.cursor, result.provider_checkpoint)),
        )
        if _revision_witnesses is not None:
            witnesses = []
            for successor_id, edge in read_revisions.items():
                predecessor = observations.get(edge.predecessor_id)
                successor = observations.get(successor_id)
                if predecessor is not None and successor is not None:
                    witnesses.append(
                        (
                            successor,
                            _NativeRevisionWitness(
                                predecessor,
                                _claude_revision_material(source._ledger, predecessor),
                                _claude_revision_material(source._ledger, successor),
                                edge.predecessor_ordinal,
                                edge.later_ordinal,
                                edge.prefix_ref,
                                edge.kind,
                                edge.terminal_contributor_spans,
                            ),
                        )
                    )
            _revision_witnesses.extend(witnesses)
        return batch
