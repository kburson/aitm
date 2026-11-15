"""Writer-bound private routing claims and native replay checkpoints."""

import hmac
import json
import re
import sqlite3
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from itertools import chain
from typing import TYPE_CHECKING
from uuid import UUID
from weakref import WeakValueDictionary

from ._monitor_journal_store import (
    _CONTENT_DISPUTE_SCHEMA_VERSION,
    _COVERAGE_SCHEMA_VERSION,
    _DELIVERY_SCHEMA_VERSION,
    _PAIRED_SCHEMA_VERSION,
    JournalStore,
)
from ._monitor_qualification import _LiveExclusion, _LiveSourceUnavailable
from .ledger import ConflictError, LedgerError, _DeliveryReceipt
from .monitor_registry import (
    Registry,
    RegistryView,
    _grok_records,
    _GrokEpoch,
    _ServiceEvidence,
)
from .monitor_scope import (
    HandoffStatus,
    HoldState,
    RouteDecision,
    RouteStatus,
    Scope,
    ScopePosition,
    ScopeState,
    ScopeView,
    VerifiedRouteDisposition,
    VerifiedScopeBatch,
    _GrokAdmission,
    _JournalScopeRelease,
    _ObservationProof,
    _RouteDispositionRecord,
    _timeline,
    _VerifiedSettlementSide,
    resolve_route,
)
from .monitor_scope import (
    _digest as _scope_command_digest,
)
from .monitor_scope import (
    _stream as _scope_stream,
)
from .monitor_types import (
    GrokBoundary,
    GrokCheckpoint,
    GrokObservation,
    NativeSurface,
    ObservationTimeBasis,
)
from .sources.adapter import (
    NativeObservation,
    SourceLocator,
    StreamCursor,
    _claude_revision_material,
    _GrokSource,
    _NativeRevisionWitness,
)
from .sources.codex import codex_request_boundary_reference
from .sources.grok import _VerifiedGrokHookless, _VerifiedGrokMark
from .sources.scan import CandidateSource, _capture_position, _CaptureDiscontinuity
from .types import (
    BoundaryKind,
    Eligibility,
    Provider,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    UsageObservation,
    _decode,
    _encode,
    _nonnegative,
    _positive,
)

if TYPE_CHECKING:
    from .monitor_writer import ProjectDelivery


_Stream = tuple[str, str, str, str, str]
_DELIVERY_ACK_ROWS = (
    "SELECT a.project,a.destination_key,a.claim_key,a.revision,a.claim_sequence,"
    " a.ack_sequence,a.payload,a.seal,c.sequence,t.sequence FROM delivery_acks a"
    " LEFT JOIN commits c ON c.sequence=a.ack_sequence"
    " LEFT JOIN commits t ON t.sequence=a.claim_sequence"
)
_DISPOSITION_ROWS = (
    "SELECT d.command,d.hold,d.sequence,c.sequence,d.payload"
    " FROM route_dispositions d LEFT JOIN commits c ON c.sequence=d.sequence"
)


_COVERAGE_ROWS = (
    "SELECT s.identity,s.sequence,c.sequence,s.payload,s.seal"
    " FROM source_coverage s LEFT JOIN commits c ON c.sequence=s.sequence"
)


_OWNERSHIP_DISPUTE_ROWS = (
    "SELECT d.key,d.contender,c.project,d.digest,d.evidence,d.sequence,c.payload,c.digest"
    " FROM disputes d LEFT JOIN claims c ON c.key=d.key"
)
_CONTENT_DISPUTE_ROWS = (
    "SELECT d.key,c.project,c.payload,c.digest,d.sequence,d.payload"
    " FROM content_disputes d LEFT JOIN claims c ON c.key=d.key"
)


class _StaleLiveExclusion(LedgerError):
    """A previously observed policy refusal no longer grants coverage."""


class ClaimStatus(StrEnum):
    PENDING = "pending"
    REPLAY = "replay"
    HELD = "held"
    DISPUTED = "disputed"


@dataclass(frozen=True, slots=True)
class ClaimDisposition:
    status: ClaimStatus
    key: SourceRef
    project_id: UUID
    sequence: int


@dataclass(frozen=True, slots=True)
class ClaimEvidence:
    source_id: UUID
    surface: NativeSurface
    session_ref: SourceRef
    stream_ref: SourceRef
    start: int
    end: int
    capture_generation: int
    capture_boundary: SourceRef

    def __post_init__(self) -> None:
        _nonnegative(self.start)
        _positive(self.capture_generation)
        if type(self.end) is not int or self.end <= self.start:
            raise ValueError("Journal claim requires a nonempty native span")


@dataclass(frozen=True, slots=True)
class _UsageMaterial:
    usage: UsageObservation | GrokObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis


@dataclass(frozen=True, slots=True)
class _ClaimPayload:
    material: _UsageMaterial
    evidence: ClaimEvidence


@dataclass(frozen=True, slots=True)
class _RevisionPayload:
    usage: UsageObservation
    revision: int
    prefix_ref: SourceRef
    locator_ref: SourceRef
    incarnation_ref: SourceRef

    def __post_init__(self) -> None:
        if type(self.revision) is not int or self.revision < 2:
            raise ValueError("Expected a successor journal revision")


@dataclass(frozen=True, slots=True)
class _StoredRevision:
    sequence: int
    ordinal: int
    material: SourceRef
    predecessor: SourceRef
    payload: _RevisionPayload


@dataclass(frozen=True, slots=True)
class _ContentEdge:
    material: SourceRef
    origin: ClaimEvidence
    later_ordinal: int
    prefix_ref: SourceRef
    locator_ref: SourceRef
    incarnation_ref: SourceRef

    def __post_init__(self) -> None:
        _nonnegative(self.later_ordinal)


@dataclass(frozen=True, slots=True)
class _ContentDisputePayload:
    common: SourceRef
    accepted: _ContentEdge
    contender: _ContentEdge


@dataclass(frozen=True, slots=True)
class PendingClaim:
    key: SourceRef
    project_id: UUID
    usage: UsageObservation | GrokObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis
    evidence: ClaimEvidence
    sequence: int
    revision: int = 1


@dataclass(frozen=True, slots=True)
class _DeliveryClaim:
    claim: PendingClaim
    service_key: str
    digest: str


@dataclass(frozen=True, slots=True)
class _DeliveryAck:
    claim_key: SourceRef
    receipt: _DeliveryReceipt
    sequence: int


class _DeliveryRefused(LedgerError):
    """No current, authenticated destination delivery can be acknowledged."""


@dataclass(frozen=True, slots=True)
class OwnershipDispute:
    key: SourceRef
    contender: UUID
    evidence: ClaimEvidence
    sequence: int


@dataclass(frozen=True, slots=True)
class ContentDispute:
    key: SourceRef
    project_id: UUID
    common: SourceRef
    accepted: _ContentEdge
    contender: _ContentEdge
    sequence: int


@dataclass(frozen=True, slots=True)
class _JournalDispositionPayload:
    project_id: UUID
    position: ScopePosition
    start: int
    end: int
    hold_digest: str
    record: _RouteDispositionRecord


@dataclass(frozen=True, slots=True)
class _SettledSide:
    release: _JournalScopeRelease
    command_digest: str
    request_digest: str
    grant_id: UUID
    cursor: StreamCursor
    claim: ClaimEvidence
    claim_digest: str
    claim_sequence: int


@dataclass(frozen=True, slots=True)
class _PairedSettlement:
    key: SourceRef
    owner: _SettledSide
    rival: _SettledSide


@dataclass(frozen=True, slots=True)
class _StoredSettlement:
    pair: _PairedSettlement
    identity: SourceRef


class _CoverageReason(StrEnum):
    UNQUALIFIED_SOURCE = "UNQUALIFIED_SOURCE"


class _CoverageExtent(StrEnum):
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class _CoverageIdentity:
    reason: _CoverageReason
    installation: SourceRef
    generation: SourceRef
    extent: _CoverageExtent


@dataclass(frozen=True, slots=True)
class JournalCoverage(_CoverageIdentity):
    """Sanitized coverage evidence available to the private journal writer."""

    observed_at: datetime


class _CandidateBasis(StrEnum):
    COVERAGE = "coverage"
    OWNERSHIP = "ownership"
    CONTENT = "content"


@dataclass(frozen=True, slots=True)
class _JournalDispute:
    record: OwnershipDispute | ContentDispute
    identity: SourceRef
    original_project: UUID
    row_digest: str

    def __post_init__(self) -> None:
        if type(self.record) not in (OwnershipDispute, ContentDispute):
            raise ValueError("Expected one routing journal dispute")


@dataclass(frozen=True, slots=True)
class PublicationCandidate:
    """A private verified journal-only candidate awaiting the recovery fence."""

    sequence: int
    basis: _CandidateBasis
    identity: SourceRef


@dataclass(frozen=True, slots=True)
class JournalChange:
    sequence: int
    disposition: _JournalDispositionPayload | None = None
    paired: _PairedSettlement | None = None
    coverage: JournalCoverage | None = None
    dispute: _JournalDispute | None = None

    def __post_init__(self) -> None:
        if self.coverage is not None and (
            self.disposition is not None or self.paired is not None
        ):
            raise ValueError("Coverage must be a distinct journal change")
        if self.dispute is not None and any(
            item is not None for item in (self.coverage, self.disposition, self.paired)
        ):
            raise ValueError("A dispute must be a distinct journal change")


@dataclass(frozen=True, slots=True)
class JournalChangeProjection:
    change: JournalChange
    affected: tuple[SourceRef, ...]


@dataclass(frozen=True, slots=True)
class JournalView:
    sequence: int
    claims: tuple[PendingClaim, ...]
    disputes: tuple[OwnershipDispute, ...]
    content_disputes: tuple[ContentDispute, ...] = ()
    dispositions: tuple[JournalChangeProjection, ...] = ()
    settlements: tuple[JournalChange, ...] = ()


@dataclass(frozen=True, slots=True)
class _Read:
    batch: VerifiedScopeBatch = field(repr=False)
    stream: _Stream = field(repr=False)
    prior: StreamCursor | None = field(repr=False)
    progress: StreamCursor = field(repr=False)
    grok: _GrokAdmission | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class RoutedRevision:
    """One exact observation and route prepared by the owning journal."""

    observation: NativeObservation
    route: RouteDecision
    _read: _Read = field(repr=False)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class PreparedRouting:
    candidates: tuple[RoutedRevision, ...]
    progress: StreamCursor
    _read: _Read = field(repr=False)


def _stream(source_id: UUID, locator: SourceLocator) -> _Stream:
    source = locator._source
    if (
        type(source) is not CandidateSource
        or source.session_ref is None
        or source._native_surface is None
    ):
        raise LedgerError("Journal source has no verified native session")
    return (
        str(source_id),
        source._native_surface.value,
        source.stream_ref.value,
        source.locator_ref.value,
        source.incarnation_ref.value,
    )


@dataclass(frozen=True, slots=True)
class _GrokProgress:
    checkpoint: GrokCheckpoint
    locator: SourceRef
    seal: SourceRef


def _grok_stream(admitted: _GrokAdmission, evidence: _ServiceEvidence) -> _Stream:
    approved = admitted.approved
    source = admitted.current._source
    origin = source.origin
    if (
        type(source) is not _GrokSource
        or origin is None
        or approved.approval.surface != NativeSurface.GROK_BUILD_MACOS
        or source.root.evidence != evidence
    ):
        raise LedgerError("Journal has no verified Grok stream")
    locator = evidence.pseudonymize(
        "grok-journal-locator-v1",
        json.dumps(
            [
                str(admitted.source_id),
                approved.directory.identity,
                source.path.relative_to(source.root.path).as_posix(),
                source.snapshot.identity,
            ],
            separators=(",", ":"),
        ),
    )
    return (
        str(admitted.source_id),
        approved.approval.surface,
        source.stream_ref.value,
        locator.value,
        origin.incarnation.value,
    )


def _grok_checkpoint(progress: StreamCursor, stream: _Stream) -> GrokCheckpoint:
    key = progress.checkpoint
    if (
        type(key) is not GrokCheckpoint
        or stream[1] != NativeSurface.GROK_BUILD_MACOS
        or (key.stream_ref.value, key.incarnation_ref.value) != (stream[2], stream[4])
    ):
        raise LedgerError("Verified Grok checkpoint changed its native stream")
    return key


def _grok_progress(
    progress: StreamCursor, stream: _Stream, evidence: _ServiceEvidence
) -> _GrokProgress:
    checkpoint = _grok_checkpoint(progress, stream)
    locator = SourceRef(stream[3])
    evidence.validate_source_ref(locator)
    raw = _encode(checkpoint, GrokCheckpoint, validate_ref=evidence.validate_source_ref)
    seal = evidence.pseudonymize(
        "grok-journal-progress-v1", json.dumps([stream, raw], separators=(",", ":"))
    )
    return _GrokProgress(checkpoint, locator, seal)


def _source_checkpoint(progress: StreamCursor) -> SourceCheckpoint:
    if type(progress.checkpoint) is not SourceCheckpoint:
        raise LedgerError("Journal requires a verified native cursor")
    return progress.checkpoint


def _settlement_stream(side: _SettledSide) -> _Stream:
    position = side.release.hold.position
    cursor = _source_checkpoint(side.cursor).cursor
    return (
        str(position.source_id),
        position.surface.value,
        position.stream_ref.value,
        cursor.locator_ref.value,
        cursor.incarnation_ref.value,
    )


def _settlement_identity(
    sequence: int, pair: _PairedSettlement, evidence: _ServiceEvidence
) -> SourceRef:
    data = _encode(pair, _PairedSettlement, validate_ref=evidence.validate_source_ref)
    return evidence.pseudonymize("journal-paired-settlement", f"{sequence}:{data}")


def _validate_settled_side(
    side: _SettledSide, sequence: int, evidence: _ServiceEvidence
) -> None:
    release, claim = side.release, side.claim
    hold, boundary, target = release.hold, release.terminal, release.original
    position = hold.position
    checkpoint = _source_checkpoint(side.cursor)
    cursor = checkpoint.cursor
    if (
        release.outcome is not HoldState.RESOLVED
        or hold.state is not HoldState.HELD
        or release.prior_route.scope is None
        or release.prior_route.scope.project_id != hold.project_id
        or release.prior_route.checkout != release.checkout
        or release.prior_route.held
        or hold.first_seen >= hold.expires_at
        or hold.command_id != target.hold_id
        or hold.command_id == release.command_id
        or not all(
            re.fullmatch(r"[0-9a-f]{64}", digest)
            for digest in (
                hold.command_digest,
                side.command_digest,
                side.request_digest,
                side.claim_digest,
            )
        )
        or not 0 < side.claim_sequence < sequence
        or (claim.source_id, claim.surface, claim.session_ref, claim.stream_ref)
        != _scope_stream(position)
        or position.surface is not NativeSurface.CODEX_DESKTOP_MACOS
        or checkpoint.provider.provider is not Provider.CODEX
        or not hold.affected.start <= claim.start < claim.end <= hold.affected.end
        or not position.ordinal < hold.affected.end <= boundary.ordinal
        or not boundary.ordinal
        < release.completion_ordinal
        == checkpoint.provider.ordinal
        or boundary.kind is not BoundaryKind.REQUEST
        or boundary.provider is not Provider.CODEX
        or (boundary.session_ref, boundary.stream_ref)
        != (position.session_ref, position.stream_ref)
        or boundary.receipt_ref
        != evidence.pseudonymize("scope-receipt", str(release.command_id))
        or boundary.boundary_ref
        != codex_request_boundary_reference(
            evidence, position.session_ref, release.command_id
        )
        or (
            target.boundary.provider,
            target.boundary.session_ref,
            target.boundary.stream_ref,
            target.boundary.ordinal,
        )
        != (Provider.CODEX, position.session_ref, position.stream_ref, position.ordinal)
        or target.boundary.receipt_ref
        != evidence.pseudonymize("scope-receipt", str(hold.command_id))
        or cursor.source_ref != position.stream_ref
        or release.terminal_prefix != cursor
        or (
            target.prefix.source_ref,
            target.prefix.locator_ref,
            target.prefix.incarnation_ref,
        )
        != (cursor.source_ref, cursor.locator_ref, cursor.incarnation_ref)
        or not 0 < target.prefix.offset < cursor.offset
    ):
        raise LedgerError("Invalid stored paired settlement side")


def _check_distinct_sides(pair: _PairedSettlement) -> None:
    owner, rival = pair.owner, pair.rival
    a, b = owner.release, rival.release
    first, second = _settlement_stream(owner), _settlement_stream(rival)
    if (
        a.hold.project_id == b.hold.project_id
        or owner.grant_id == rival.grant_id
        or first[0] == second[0]
        or first[3] == second[3]
        or first[4] == second[4]
        or len({a.command_id, b.command_id, a.hold.command_id, b.hold.command_id}) != 4
        or owner.claim_sequence >= rival.claim_sequence
    ):
        raise LedgerError(
            "Paired settlement requires independent owner and rival evidence"
        )


def _tip(connection: sqlite3.Connection) -> int:
    return connection.execute(
        "SELECT coalesce(max(sequence), 0) FROM commits"
    ).fetchone()[0]


def _coverage_key(value: _CoverageIdentity, evidence: _ServiceEvidence) -> SourceRef:
    identity = _CoverageIdentity(
        value.reason, value.installation, value.generation, value.extent
    )
    encoded = _encode(
        identity, _CoverageIdentity, validate_ref=evidence.validate_source_ref
    )
    return evidence.pseudonymize("journal-coverage-key-v1", encoded)


def _coverage_seal(sequence: int, raw: bytes, evidence: _ServiceEvidence) -> SourceRef:
    return evidence.pseudonymize("journal-coverage-seal-v1", f"{sequence}:{raw.hex()}")


def _stored_coverage(
    row: tuple[str, int, int | None, bytes, str], evidence: _ServiceEvidence
) -> JournalChange:
    key, sequence, commit, raw, seal = row
    try:
        _positive(sequence)
        payload = _decode(
            raw, JournalCoverage, validate_ref=evidence.validate_source_ref
        )
        canonical = _encode(
            payload, JournalCoverage, validate_ref=evidence.validate_source_ref
        ).encode()
        if (
            sequence != commit
            or canonical != raw
            or _coverage_key(payload, evidence).value != key
            or _coverage_seal(sequence, raw, evidence).value != seal
        ):
            raise ValueError("Unverified coverage row")
    except (LedgerError, ValueError):
        raise LedgerError("Invalid private journal coverage") from None
    return JournalChange(sequence, coverage=payload)


def _evidence(
    proof: _ObservationProof, project: UUID, registry: RegistryView
) -> ClaimEvidence:
    position = proof.position
    epochs = tuple(
        epoch
        for epoch in registry.epochs
        if epoch.project_id == project
        and epoch.source_id == position.source_id
        and epoch.stream_ref == position.stream_ref
        and epoch.ordinal <= position.ordinal
    )
    if not epochs or not epochs[-1].enabled or project not in proof.eligible_projects:
        raise LedgerError("Journal claim has no admitted capture epoch")
    epoch = epochs[-1]
    return ClaimEvidence(
        position.source_id,
        position.surface,
        position.session_ref,
        position.stream_ref,
        position.ordinal,
        proof.end,
        epoch.generation,
        epoch.boundary_ref,
    )


def _claim_digest(material: _UsageMaterial) -> str:
    return sha256(_encode(material, _UsageMaterial).encode()).hexdigest()


def _stored_claim(data: bytes, digest: str) -> _ClaimPayload:
    claim = _decode(data, _ClaimPayload)
    if _claim_digest(claim.material) != digest:
        raise LedgerError("Stored first claim material changed")
    return claim


def _stored_revision(
    row: tuple, key: SourceRef, evidence: _ServiceEvidence
) -> _StoredRevision:
    sequence, ordinal, material, predecessor, data = row
    _positive(sequence)
    _nonnegative(ordinal)
    material_ref, predecessor_ref = SourceRef(material), SourceRef(predecessor)
    evidence.validate_source_ref(material_ref)
    evidence.validate_source_ref(predecessor_ref)
    payload = _decode(data, _RevisionPayload, validate_ref=evidence.validate_source_ref)
    observation = NativeObservation(
        key,
        payload.revision,
        payload.usage,
        NativeSurface.CLAUDE_CODE_MACOS,
        ObservationTimeBasis.NATIVE_USAGE_EVENT,
        None,
    )
    if material_ref != _claude_revision_material(evidence, observation):
        raise LedgerError("Stored journal revision material changed")
    return _StoredRevision(sequence, ordinal, material_ref, predecessor_ref, payload)


def _revision_head(
    connection: sqlite3.Connection,
    key: SourceRef,
    sequence: int,
    evidence: _ServiceEvidence,
) -> _StoredRevision | None:
    row = connection.execute(
        "SELECT sequence,later_ordinal,material,predecessor,payload"
        " FROM claim_revisions WHERE key = ? AND sequence <= ?"
        " ORDER BY sequence DESC, later_ordinal DESC LIMIT 1",
        (key.value, sequence),
    ).fetchone()
    return None if row is None else _stored_revision(row, key, evidence)


def _revision_by_material(
    connection: sqlite3.Connection,
    key: SourceRef,
    material: SourceRef,
    evidence: _ServiceEvidence,
) -> _StoredRevision | None:
    row = connection.execute(
        "SELECT sequence,later_ordinal,material,predecessor,payload"
        " FROM claim_revisions WHERE key = ? AND material = ?",
        (key.value, material.value),
    ).fetchone()
    return None if row is None else _stored_revision(row, key, evidence)


def _same_revision(revision: _StoredRevision, witness: _NativeRevisionWitness) -> bool:
    return (
        revision.material == witness.successor_material
        and revision.predecessor == witness.predecessor_material
        and revision.ordinal == witness.later_ordinal
        and revision.payload.prefix_ref == witness.prefix_ref
    )


def _distinct_accepted_child(
    connection: sqlite3.Connection,
    key: SourceRef,
    common: SourceRef,
    usage: UsageObservation,
    evidence: _ServiceEvidence,
) -> _StoredRevision | None:
    child = None
    rows = connection.execute(
        "SELECT sequence,later_ordinal,material,predecessor,payload"
        " FROM claim_revisions WHERE key = ?",
        (key.value,),
    )
    for row in rows:
        revision = _stored_revision(row, key, evidence)
        if usage == revision.payload.usage:
            return None
        if revision.predecessor == common:
            if child is not None:
                return None
            child = revision
    return child


def _claim_span(origin: ClaimEvidence) -> tuple:
    return (
        origin.surface,
        origin.session_ref,
        origin.stream_ref,
        origin.start,
        origin.end,
    )


def _stored_disposition(
    row: tuple[str, str, int, int | None, bytes], evidence: _ServiceEvidence
) -> JournalChange:
    command, hold, sequence, commit, raw = row
    try:
        _positive(sequence)
        payload = _decode(
            raw, _JournalDispositionPayload, validate_ref=evidence.validate_source_ref
        )
        _nonnegative(payload.start)
        _nonnegative(payload.end)
    except (TypeError, ValueError):
        raise LedgerError("Invalid stored routing journal disposition") from None
    record, position = payload.record, payload.position
    boundary = record.boundary
    if (
        sequence != commit
        or (command, hold) != (str(record.command_id), str(record.hold_id))
        or record.command_id == record.hold_id
        or payload.start >= payload.end
        or not all(
            re.fullmatch(r"[0-9a-f]{64}", digest)
            for digest in (
                payload.hold_digest,
                record.command_digest,
                record.request_digest,
            )
        )
        or position.surface is not NativeSurface.CODEX_DESKTOP_MACOS
        or boundary.provider is not Provider.CODEX
        or boundary.kind is not BoundaryKind.TURN
        or (boundary.session_ref, boundary.stream_ref)
        != (position.session_ref, position.stream_ref)
        or boundary.ordinal <= position.ordinal
        or boundary.ordinal < payload.end
        or boundary.receipt_ref != evidence.pseudonymize("scope-receipt", command)
        or record.prefix.source_ref != position.stream_ref
        or record.prefix.offset <= 0
        or record.hold_state not in (HoldState.HELD, HoldState.GAP)
        or record.outcome not in (HoldState.GAP, HoldState.RESOLVED)
        or (
            record.outcome is HoldState.RESOLVED
            and record.hold_state is not HoldState.HELD
        )
        or _encode(
            payload,
            _JournalDispositionPayload,
            validate_ref=evidence.validate_source_ref,
        ).encode("utf-8")
        != raw
    ):
        raise LedgerError("Invalid stored routing journal disposition")
    return JournalChange(sequence, payload)


def _affected_disposition_keys(
    payload: _JournalDispositionPayload,
    claims: list[PendingClaim],
    disputes: list[OwnershipDispute],
    content_disputes: list[ContentDispute],
) -> tuple[SourceRef, ...]:
    position = payload.position
    target = (
        payload.project_id,
        position.source_id,
        position.surface,
        position.session_ref,
        position.stream_ref,
    )
    origins = chain(
        ((claim.key, claim.project_id, claim.evidence) for claim in claims),
        ((dispute.key, dispute.contender, dispute.evidence) for dispute in disputes),
        (
            (dispute.key, dispute.project_id, edge.origin)
            for dispute in content_disputes
            for edge in (dispute.accepted, dispute.contender)
        ),
    )
    return tuple(
        sorted(
            {
                key
                for key, project_id, origin in origins
                if (
                    project_id,
                    origin.source_id,
                    origin.surface,
                    origin.session_ref,
                    origin.stream_ref,
                )
                == target
                and origin.start < payload.end
                and payload.start < origin.end
            },
            key=lambda key: key.value,
        )
    )


def _accepted_edge(revision: _StoredRevision, origin: ClaimEvidence) -> _ContentEdge:
    return _ContentEdge(
        revision.material,
        origin,
        revision.ordinal,
        revision.payload.prefix_ref,
        revision.payload.locator_ref,
        revision.payload.incarnation_ref,
    )


def _stored_content_dispute(
    connection: sqlite3.Connection,
    key: SourceRef,
    original: ClaimEvidence,
    sequence: int,
    data: bytes,
    evidence: _ServiceEvidence,
) -> _ContentDisputePayload:
    _positive(sequence)
    payload = _decode(
        data, _ContentDisputePayload, validate_ref=evidence.validate_source_ref
    )
    accepted, contender = payload.accepted, payload.contender
    common = _revision_by_material(connection, key, payload.common, evidence)
    child = _revision_by_material(connection, key, accepted.material, evidence)
    if (
        common is None
        or child is None
        or not common.sequence <= child.sequence <= sequence
        or child.predecessor != common.material
        or accepted != _accepted_edge(child, original)
        or _claim_span(contender.origin) != _claim_span(original)
        or contender.origin.source_id == original.source_id
        or contender.incarnation_ref == accepted.incarnation_ref
        or contender.material in (common.material, accepted.material)
        or contender.prefix_ref == accepted.prefix_ref
        or not common.ordinal < min(accepted.later_ordinal, contender.later_ordinal)
    ):
        raise LedgerError("Stored content dispute does not match durable claim history")
    return payload


def _matches_content_edge(
    edge: _ContentEdge, common: SourceRef, witness: _NativeRevisionWitness
) -> bool:
    return (
        witness.predecessor_material == common
        and witness.successor_material == edge.material
        and witness.later_ordinal == edge.later_ordinal
        and witness.prefix_ref == edge.prefix_ref
    )


def _physical_stream(cursor: SourceCursor) -> tuple[SourceRef, SourceRef, SourceRef]:
    return cursor.source_ref, cursor.locator_ref, cursor.incarnation_ref


def _original_capture(
    batch: VerifiedScopeBatch,
    owner: UUID,
    original: ClaimEvidence,
    registry: RegistryView,
) -> bool:
    epochs = tuple(
        epoch
        for epoch in registry.epochs
        if epoch.project_id == owner
        and epoch.source_id == original.source_id
        and epoch.stream_ref == original.stream_ref
        and epoch.generation == original.capture_generation
        and epoch.boundary_ref == original.capture_boundary
        and epoch.enabled
        and epoch.ordinal <= original.start
    )
    cursor = batch._native_cursor
    source = batch._locator._source
    if len(epochs) != 1 or cursor is None or type(source) is not CandidateSource:
        return False
    (epoch,) = epochs
    historical = epoch.position or epoch.observed.checkpoint.cursor
    if _physical_stream(cursor) != _physical_stream(historical):
        return False
    try:
        _capture_position(source, historical, fixed=historical)
    except (_CaptureDiscontinuity, OSError, ValueError):
        return False
    return True


def _publication_reference(
    evidence: _ServiceEvidence, namespace: str, *fields: object
) -> SourceRef:
    canonical = json.dumps(
        fields, ensure_ascii=True, separators=(",", ":"), allow_nan=False
    )
    return evidence.pseudonymize(namespace, canonical)


def _dispute_original(
    values: tuple[str | None, bytes | None, str | None], evidence: _ServiceEvidence
) -> tuple[UUID, ClaimEvidence]:
    project, payload, digest = values
    if project is None or payload is None or digest is None:
        raise LedgerError("Stored dispute is missing its first claim")
    project_id = UUID(project)
    if project != str(project_id):
        raise ValueError("Noncanonical original project")
    original = _stored_claim(payload, digest)
    _encode(original, _ClaimPayload, validate_ref=evidence.validate_source_ref)
    return project_id, original.evidence


def _verified_ownership_change(row: tuple, evidence: _ServiceEvidence) -> JournalChange:
    key, contender, project, digest, raw, sequence, first, first_digest = row
    _positive(sequence)
    key = SourceRef(key)
    evidence.validate_source_ref(key)
    contender_id = UUID(contender)
    if contender != str(contender_id) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Noncanonical stored ownership dispute")
    project_id, _ = _dispute_original((project, first, first_digest), evidence)
    captured = _decode(raw, ClaimEvidence, validate_ref=evidence.validate_source_ref)
    if (
        _encode(
            captured, ClaimEvidence, validate_ref=evidence.validate_source_ref
        ).encode()
        != raw
    ):
        raise ValueError("Noncanonical stored dispute evidence")
    identity = _publication_reference(
        evidence,
        "monitor-journal-dispute-row-v1",
        _CandidateBasis.OWNERSHIP,
        sequence,
        key.value,
        str(project_id),
        str(contender_id),
        digest,
        raw.hex(),
    )
    dispute = OwnershipDispute(key, contender_id, captured, sequence)
    return JournalChange(
        sequence, dispute=_JournalDispute(dispute, identity, project_id, digest)
    )


def _verified_content_change(
    connection: sqlite3.Connection, row: tuple, evidence: _ServiceEvidence
) -> JournalChange:
    key, project, first, first_digest, sequence, raw = row
    key = SourceRef(key)
    evidence.validate_source_ref(key)
    project_id, original = _dispute_original((project, first, first_digest), evidence)
    payload = _stored_content_dispute(
        connection, key, original, sequence, raw, evidence
    )
    if (
        _encode(
            payload, _ContentDisputePayload, validate_ref=evidence.validate_source_ref
        ).encode()
        != raw
    ):
        raise ValueError("Noncanonical stored content dispute")
    digest = sha256(raw).hexdigest()
    identity = _publication_reference(
        evidence,
        "monitor-journal-dispute-row-v1",
        _CandidateBasis.CONTENT,
        sequence,
        key.value,
        str(project_id),
        digest,
        raw.hex(),
    )
    dispute = ContentDispute(
        key, project_id, payload.common, payload.accepted, payload.contender, sequence
    )
    return JournalChange(
        sequence, dispute=_JournalDispute(dispute, identity, project_id, digest)
    )


class RoutingJournal:
    """Stage exact observations under the existing coordinator writer lease."""

    def __init__(
        self, writer: Registry, scopes: ScopeState, *, pending_per_project: int = 64
    ) -> None:
        if type(pending_per_project) is not int or pending_per_project <= 0:
            raise ValueError("Expected a positive destination capacity")
        self._pending_per_project = pending_per_project
        writer.lease
        if scopes.registry is not writer:
            raise LedgerError("Journal and scope state require the same coordinator")
        self._writer = writer
        self._scopes = scopes
        self._store = JournalStore(writer)
        self._candidates: WeakValueDictionary[int, RoutedRevision] = (
            WeakValueDictionary()
        )
        self._batches: WeakValueDictionary[int, PreparedRouting] = WeakValueDictionary()

    def _cursor(
        self, connection: sqlite3.Connection, stream: _Stream
    ) -> StreamCursor | None:
        row = connection.execute(
            "SELECT cursor FROM progress WHERE (source,surface,stream,locator,incarnation)"
            " = (?,?,?,?,?) ORDER BY sequence DESC LIMIT 1",
            stream,
        ).fetchone()
        if row is None:
            return None
        evidence = self._store.evidence
        if stream[1] == NativeSurface.GROK_BUILD_MACOS:
            saved = _decode(
                row[0], _GrokProgress, validate_ref=evidence.validate_source_ref
            )
            cursor = StreamCursor(saved.checkpoint)
            if _grok_progress(cursor, stream, evidence) != saved:
                raise LedgerError("Stored Grok progress seal changed")
            return cursor
        cursor = _decode(
            row[0], StreamCursor, validate_ref=evidence.validate_source_ref
        )
        checkpoint = _source_checkpoint(cursor).cursor
        if (
            checkpoint.source_ref.value,
            checkpoint.locator_ref.value,
            checkpoint.incarnation_ref.value,
        ) != stream[2:]:
            raise LedgerError("Stored journal cursor changed its native stream")
        return cursor

    def cursor_for(
        self, source_id: UUID, locator: SourceLocator
    ) -> StreamCursor | None:
        stream = _stream(source_id, locator)
        with self._store.transaction() as connection:
            return self._cursor(connection, stream)

    def prepare(self, source_id: UUID, locator: SourceLocator) -> PreparedRouting:
        """Read current native evidence from the journal's exact prior checkpoint."""
        self._writer.lease
        grok = None
        try:
            if type(locator._source) is _GrokSource:
                grok = self._scopes._grok_admission(
                    self._writer.view(), source_id, locator
                )
                stream = _grok_stream(grok, self._store.evidence)
                if not any(
                    type(epoch) is _GrokEpoch
                    and epoch.identity.source_id == source_id
                    and epoch.identity.stream.value == stream[2]
                    and epoch.identity
                    == self._scopes._grok_identity(grok, epoch.identity.project_id)
                    for epoch in _grok_records(grok.view)
                ):
                    raise LedgerError("Journal source has no verified native session")
                with self._store.transaction() as connection:
                    prior = self._cursor(connection, stream)
                batch = self._scopes.read_source(
                    source_id, locator, cursor=prior, _grok_admission=grok
                )
            else:
                stream = _stream(source_id, locator)
                prior = self.cursor_for(source_id, locator)
                batch = self._scopes.read_source(source_id, locator, cursor=prior)
        except _LiveSourceUnavailable as refusal:
            decision = refusal.decision
            if type(decision) is _LiveExclusion and decision.source_id == source_id:
                try:
                    self._record_live_exclusion(source_id, locator, decision)
                except _StaleLiveExclusion:
                    pass
            raise
        finally:
            if grok is not None and self._scopes._grok_admissions.get(id(grok)) is grok:
                del self._scopes._grok_admissions[id(grok)]
        progress = batch.cursor
        if progress is None:
            raise LedgerError("Native read did not provide a verified journal cursor")
        if batch.source_id != source_id or batch.surface.value != stream[1]:
            raise LedgerError("Native read changed the journal cursor identity")
        if grok is not None:
            if (
                type(batch) is not VerifiedScopeBatch
                or not batch._grok_strict
                or batch.surface is not NativeSurface.GROK_BUILD_MACOS
            ):
                raise LedgerError(
                    "Grok journal source has no verified capture interval"
                )
            _grok_checkpoint(progress, stream)
        else:
            checkpoint = _source_checkpoint(progress).cursor
            if (
                checkpoint.source_ref.value,
                checkpoint.locator_ref.value,
                checkpoint.incarnation_ref.value,
            ) != stream[2:]:
                raise LedgerError("Native read changed the journal cursor identity")
        read = _Read(batch, stream, prior, progress, grok)
        with self._store.transaction() as connection:
            if self._cursor(connection, stream) != prior:
                raise ConflictError("Journal cursor changed during preparation")
            view, registry = self._fresh_view(connection, read, confirm=False)
            if grok is not None and grok.view != registry:
                raise ConflictError("Grok admission changed during journal preparation")
            settled = 0 if grok is not None else self._paired_frontier(view)
            candidates = tuple(
                RoutedRevision(proof.observation, route, read)
                for proof in view._proofs
                if proof.end > settled
                and (route := resolve_route(proof.observation, registry, view)).status
                is RouteStatus.ROUTED
            )
        for candidate in candidates:
            self._candidates[id(candidate)] = candidate
        prepared = PreparedRouting(candidates, progress, read)
        self._batches[id(prepared)] = prepared
        return prepared

    def _record_live_exclusion(
        self, source_id: UUID, locator: SourceLocator, decision: _LiveExclusion
    ) -> None:
        identity = _CoverageIdentity(
            _CoverageReason.UNQUALIFIED_SOURCE,
            decision.installation,
            decision.generation,
            _CoverageExtent.UNKNOWN,
        )
        with self._store.transaction(write=True) as connection:
            self._writer.lease
            if not self._scopes._confirm_live_exclusion(source_id, locator, decision):
                raise _StaleLiveExclusion()
            self._store._enable_coverage(connection)
            evidence = self._store.evidence
            key = _coverage_key(identity, evidence).value
            prior = connection.execute(
                _COVERAGE_ROWS + " WHERE s.identity=?", (key,)
            ).fetchone()
            if prior is None:
                sequence = _tip(connection) + 1
                payload = JournalCoverage(
                    identity.reason,
                    identity.installation,
                    identity.generation,
                    identity.extent,
                    datetime.now(UTC),
                )
                raw = _encode(
                    payload, JournalCoverage, validate_ref=evidence.validate_source_ref
                ).encode()
                seal = _coverage_seal(sequence, raw, evidence).value
                self._record_sequence(connection, sequence)
                connection.execute(
                    "INSERT INTO source_coverage VALUES (?,?,?,?)",
                    (key, sequence, raw, seal),
                )
            else:
                _stored_coverage(prior, evidence)
            if not self._scopes._confirm_live_exclusion(source_id, locator, decision):
                raise _StaleLiveExclusion()
            self._writer.lease

    def coverage_changes(self, after_sequence: int) -> tuple[JournalChange, ...]:
        """Read verified sanitized coverage in private journal commit order."""
        with self._store.transaction() as connection:
            if type(after_sequence) is not int or not 0 <= after_sequence <= _tip(
                connection
            ):
                raise ValueError("Journal coverage sequence is unavailable")
            if self._store._current_version(connection) < _COVERAGE_SCHEMA_VERSION:
                return ()
            evidence = self._store.evidence
            return tuple(
                _stored_coverage(row, evidence)
                for row in connection.execute(
                    _COVERAGE_ROWS + " WHERE s.sequence>? ORDER BY s.sequence",
                    (after_sequence,),
                )
            )

    def _dispute_changes_in(
        self,
        connection: sqlite3.Connection,
        sequence: int,
        key: SourceRef | None = None,
    ) -> tuple[JournalChange, ...]:
        if (
            not _CONTENT_DISPUTE_SCHEMA_VERSION
            <= self._store._current_version(connection)
            <= _DELIVERY_SCHEMA_VERSION
        ):
            raise LedgerError("Routing journal dispute schema is unavailable")
        evidence = self._store.evidence
        where, args = (
            (" WHERE d.sequence > ?", (sequence,))
            if key is None
            else (" WHERE d.sequence=? AND d.key=?", (sequence, key.value))
        )
        ownership = connection.execute(
            _OWNERSHIP_DISPUTE_ROWS
            + where
            + " ORDER BY d.sequence,d.key,d.contender,d.digest,d.evidence",
            args,
        )
        content = connection.execute(
            _CONTENT_DISPUTE_ROWS + where + " ORDER BY d.sequence,d.key", args
        )
        return tuple(
            sorted(
                chain(
                    (_verified_ownership_change(row, evidence) for row in ownership),
                    (
                        _verified_content_change(connection, row, evidence)
                        for row in content
                    ),
                ),
                key=lambda change: change.sequence,
            )
        )

    def dispute_changes(self, after_sequence: int) -> tuple[JournalChange, ...]:
        """Read exact stored disputes while preserving the public historical projection."""
        with self._store.transaction() as connection:
            try:
                if type(after_sequence) is not int or not 0 <= after_sequence <= _tip(
                    connection
                ):
                    raise ValueError("Invalid journal watermark")
                return self._dispute_changes_in(connection, after_sequence)
            except (ValueError, LedgerError):
                raise LedgerError(
                    "Verified journal-only publication is unavailable"
                ) from None

    def publication_candidate(self, change: JournalChange) -> PublicationCandidate:
        """Issue a stable reference after private committed-change verification."""
        with self._store.transaction() as connection:
            try:
                if (
                    type(change) is not JournalChange
                    or type(change.sequence) is not int
                    or not 0 < change.sequence <= _tip(connection)
                    or change.disposition is not None
                    or change.paired is not None
                    or (change.coverage is None) == (change.dispute is None)
                ):
                    raise ValueError("Invalid publication change")
                evidence = self._store.evidence
                if type(change.coverage) is JournalCoverage:
                    if (
                        self._store._current_version(connection)
                        < _COVERAGE_SCHEMA_VERSION
                    ):
                        raise ValueError("Coverage schema is unavailable")
                    (row,) = connection.execute(
                        _COVERAGE_ROWS + " WHERE s.sequence=?", (change.sequence,)
                    ).fetchall()
                    verified = _stored_coverage(row, evidence)
                    if verified != change or _encode(
                        change.coverage,
                        JournalCoverage,
                        validate_ref=evidence.validate_source_ref,
                    ) != _encode(
                        verified.coverage,
                        JournalCoverage,
                        validate_ref=evidence.validate_source_ref,
                    ):
                        raise ValueError("Coverage differs from its durable row")
                    basis = _CandidateBasis.COVERAGE
                    material = (
                        _encode(
                            verified.coverage,
                            JournalCoverage,
                            validate_ref=evidence.validate_source_ref,
                        )
                        .encode()
                        .hex()
                    )
                elif type(change.dispute) is _JournalDispute:
                    dispute = change.dispute
                    evidence.validate_source_ref(dispute.record.key)
                    evidence.validate_source_ref(dispute.identity)
                    (verified,) = (
                        stored
                        for stored in self._dispute_changes_in(
                            connection, change.sequence, dispute.record.key
                        )
                        if stored == change
                    )
                    if _encode(
                        dispute,
                        _JournalDispute,
                        validate_ref=evidence.validate_source_ref,
                    ) != _encode(
                        verified.dispute,
                        _JournalDispute,
                        validate_ref=evidence.validate_source_ref,
                    ):
                        raise ValueError("Dispute differs from its durable row")
                    basis = (
                        _CandidateBasis.OWNERSHIP
                        if type(verified.dispute.record) is OwnershipDispute
                        else _CandidateBasis.CONTENT
                    )
                    material = verified.dispute.identity.value
                else:
                    raise ValueError("Unexpected journal change type")
                identity = _publication_reference(
                    evidence,
                    "monitor-journal-publication-v1",
                    basis,
                    change.sequence,
                    material,
                )
                return PublicationCandidate(change.sequence, basis, identity)
            except (ValueError, LedgerError):
                raise LedgerError(
                    "Verified journal-only publication is unavailable"
                ) from None

    def enable_delivery(self, expected_tip: int) -> None:
        """Explicitly opt the current coordinator journal into destination delivery."""
        with self._store.transaction(write=True) as conn:
            if type(expected_tip) is not int or expected_tip != _tip(conn):
                raise ConflictError("Journal changed before delivery schema upgrade")
            self._store._enable_delivery(conn)

    def _require_delivery_schema(self, conn: sqlite3.Connection) -> None:
        if self._store._current_version(conn) != _DELIVERY_SCHEMA_VERSION:
            raise _DeliveryRefused("Destination delivery is unavailable")

    def _delivery_claim(
        self, conn: sqlite3.Connection, key: SourceRef, revision: int
    ) -> _DeliveryClaim:
        evidence = self._store.evidence
        evidence.validate_source_ref(key)
        if type(revision) is not int or revision <= 0:
            raise _DeliveryRefused("Destination claim is unavailable")
        row = conn.execute(
            "SELECT c.project,c.payload,c.digest,c.sequence FROM claims c"
            " JOIN commits t ON t.sequence=c.sequence WHERE c.key=?"
            " AND NOT EXISTS (SELECT 1 FROM content_disputes d WHERE d.key=c.key)",
            (key.value,),
        ).fetchone()
        if row is None:
            raise _DeliveryRefused("Destination claim is unavailable")
        project, raw, digest, sequence = row
        payload = _stored_claim(raw, digest)
        owner = UUID(project)
        if str(owner) != project or (
            payload.material.scope is not None
            and payload.material.scope.project_id != owner
        ):
            raise _DeliveryRefused("Destination claim identity changed")
        latest = _revision_head(conn, key, _tip(conn), evidence)
        if latest is None:
            recorded_revision, usage = 1, payload.material.usage
        else:
            sequence, recorded_revision, usage = (
                latest.sequence,
                latest.payload.revision,
                latest.payload.usage,
            )
        if (
            revision != recorded_revision
            or conn.execute(
                "SELECT 1 FROM commits WHERE sequence=?", (sequence,)
            ).fetchone()
            is None
        ):
            raise _DeliveryRefused("Destination claim is no longer current")
        claim = PendingClaim(
            key,
            owner,
            usage,
            payload.material.scope,
            payload.material.time_basis,
            payload.evidence,
            sequence,
            recorded_revision,
        )
        canonical = _encode(
            claim, PendingClaim, validate_ref=evidence.validate_source_ref
        )
        return _DeliveryClaim(
            claim, evidence.key_id, sha256(canonical.encode()).hexdigest()
        )

    def reserve_delivery(self, key: SourceRef, revision: int) -> _DeliveryClaim:
        """Read a current deliverable revision without creating a reservation row."""
        with self._store.transaction() as conn:
            self._require_delivery_schema(conn)
            return self._delivery_claim(conn, key, revision)

    def _ack_payload(self, result: _DeliveryAck) -> str:
        # Only the outer claim key belongs to the service. The nested receipt
        # holds a project-key reference authenticated by its original Ledger.
        self._store.evidence.validate_source_ref(result.claim_key)
        return _encode(result, _DeliveryAck)

    def _stored_ack(self, row: tuple) -> _DeliveryAck:
        (
            project,
            destination,
            key,
            revision,
            claim_seq,
            ack_seq,
            raw,
            seal,
            ack_commit,
            claim_commit,
        ) = row
        evidence = self._store.evidence
        try:
            result = _decode(raw, _DeliveryAck)
            expected_seal = evidence.pseudonymize("monitor-delivery-ack-v1", raw).value
        except (ValueError, TypeError):
            raise _DeliveryRefused(
                "Invalid private destination acknowledgment"
            ) from None
        receipt = result.receipt
        if (
            self._ack_payload(result) != raw
            or not hmac.compare_digest(expected_seal, seal)
            or (str(receipt.project_id), receipt.destination_key)
            != (project, destination)
            or (result.claim_key.value, receipt.revision) != (key, revision)
            or (receipt.claim_sequence, result.sequence) != (claim_seq, ack_seq)
            or (claim_commit, ack_commit) != (claim_seq, ack_seq)
            or not 0 < claim_seq < ack_seq
        ):
            raise _DeliveryRefused("Invalid private destination acknowledgment")
        return result

    def _acknowledged(
        self, conn: sqlite3.Connection, project: UUID, key: SourceRef, revision: int
    ) -> _DeliveryAck | None:
        entries = conn.execute(
            _DELIVERY_ACK_ROWS + " WHERE (a.project,a.claim_key,a.revision)=(?,?,?)",
            (str(project), key.value, revision),
        ).fetchall()
        if len(entries) > 1:
            raise _DeliveryRefused("Ambiguous private destination acknowledgment")
        return self._stored_ack(entries[0]) if entries else None

    def _require_destination_in(
        self, conn: sqlite3.Connection, project: UUID, destination_key: str
    ) -> None:
        self._require_delivery_schema(conn)
        if any(
            row != (destination_key,)
            for row in conn.execute(
                "SELECT DISTINCT destination_key FROM delivery_acks WHERE project=?",
                (str(project),),
            )
        ):
            raise _DeliveryRefused("Destination ledger key changed")

    def _require_delivery_destination(
        self, project: UUID, destination_key: str
    ) -> None:
        with self._store.transaction() as conn:
            self._require_destination_in(conn, project, destination_key)

    def ack(
        self,
        delivery: "ProjectDelivery",
        issued: _DeliveryClaim,
        receipt: _DeliveryReceipt,
    ) -> _DeliveryAck:
        """Acknowledge the exact append-only effect under its existing custody."""
        from .monitor_writer import ProjectDelivery

        try:
            if type(delivery) is not ProjectDelivery or delivery._journal is not self:
                raise ValueError("Delivery belongs to another coordinator")
            if (
                type(issued) is not _DeliveryClaim
                or type(receipt) is not _DeliveryReceipt
            ):
                raise ValueError("Invalid destination proof")
            claim = issued.claim
            if (
                issued.service_key != self._store.evidence.key_id
                or issued.digest != receipt.claim_digest
                or sha256(
                    _encode(
                        claim,
                        PendingClaim,
                        validate_ref=self._store.evidence.validate_source_ref,
                    ).encode()
                ).hexdigest()
                != issued.digest
                or (claim.project_id, claim.revision, claim.sequence)
                != (receipt.project_id, receipt.revision, receipt.claim_sequence)
            ):
                raise ValueError("Destination receipt claim identity changed")
            verified = delivery._readback(issued, receipt)
            if verified != receipt:
                raise ValueError("Destination receipt does not match durable usage")
            with self._store.transaction(write=True) as conn:
                self._require_destination_in(
                    conn, claim.project_id, receipt.destination_key
                )
                existing = self._acknowledged(
                    conn, claim.project_id, claim.key, claim.revision
                )
                if existing is not None:
                    if existing.receipt != verified:
                        raise ValueError("Destination acknowledgment changed")
                    delivery._require_current()
                    return existing
                if self._delivery_claim(conn, claim.key, claim.revision) != issued:
                    raise ValueError("Destination claim changed before acknowledgment")
                sequence = _tip(conn) + 1
                result = _DeliveryAck(claim.key, verified, sequence)
                raw = self._ack_payload(result)
                seal = self._store.evidence.pseudonymize(
                    "monitor-delivery-ack-v1", raw
                ).value
                self._record_sequence(conn, sequence)
                conn.execute(
                    "INSERT INTO delivery_acks (project,destination_key,claim_key,revision,"
                    " claim_sequence,ack_sequence,payload,seal) VALUES (?,?,?,?,?,?,?,?)",
                    (
                        str(claim.project_id),
                        verified.destination_key,
                        claim.key.value,
                        claim.revision,
                        claim.sequence,
                        sequence,
                        raw,
                        seal,
                    ),
                )
                delivery._require_current()
                return result
        except (LedgerError, ValueError, sqlite3.Error, AttributeError):
            raise _DeliveryRefused(
                "Verified destination acknowledgment is unavailable"
            ) from None

    def delivery_tail(self, project: UUID, destination_key: str) -> int:
        """Return the verified destination high-water mark."""
        with self._store.transaction() as conn:
            self._require_destination_in(conn, project, destination_key)
            top = conn.execute(
                _DELIVERY_ACK_ROWS + " WHERE a.project=? AND a.destination_key=?"
                " ORDER BY a.claim_sequence DESC LIMIT 1",
                (str(project), destination_key),
            ).fetchone()
            return 0 if top is None else self._stored_ack(top).receipt.claim_sequence

    def _delivery_capacity(
        self, conn: sqlite3.Connection, project: UUID, replaces: SourceRef | None = None
    ) -> bool:
        if conn.execute("PRAGMA user_version").fetchone() != (
            _DELIVERY_SCHEMA_VERSION,
        ):
            return True
        count, already_pending = 0, False
        evidence = self._store.evidence
        head = _tip(conn)
        for key_value, sequence, disputed_at, dispute in conn.execute(
            "SELECT c.key,c.sequence,d.sequence,d.payload FROM claims c"
            " LEFT JOIN content_disputes d ON d.key=c.key WHERE c.project=?",
            (str(project),),
        ):
            key = SourceRef(key_value)
            evidence.validate_source_ref(key)
            if dispute is not None:
                raw, digest = conn.execute(
                    "SELECT payload,digest FROM claims WHERE key=?", (key.value,)
                ).fetchone()
                _stored_content_dispute(
                    conn,
                    key,
                    _stored_claim(raw, digest).evidence,
                    disputed_at,
                    dispute,
                    evidence,
                )
                continue
            latest = _revision_head(conn, key, head, evidence)
            if latest is None:
                revision = 1
            else:
                sequence, revision = latest.sequence, latest.payload.revision
            ack = self._acknowledged(conn, project, key, revision)
            if ack is not None:
                if ack.receipt.claim_sequence != sequence:
                    raise _DeliveryRefused(
                        "Destination acknowledgment sequence changed"
                    )
                continue
            count += 1
            already_pending |= key == replaces
            if count >= self._pending_per_project and (
                replaces is None or already_pending
            ):
                return already_pending
        return already_pending or count < self._pending_per_project

    def _fresh_view(
        self, connection: sqlite3.Connection, read: _Read, *, confirm: bool = True
    ) -> tuple[ScopeView, RegistryView]:
        self._writer.lease
        releases, conflicts = self._effective_releases(connection)
        view = self._scopes._journal_view(
            read.batch, releases, conflicts, confirm=confirm
        )
        registry = self._writer.view()
        if view._registry != registry:
            raise LedgerError("Journal scope or registry changed during read")
        return view, registry

    def _known_excluded(self, proof: _ObservationProof, registry: RegistryView) -> bool:
        position = proof.position
        return bool(registry.projects) and all(
            self._writer.span_disposition(
                project.project_id,
                position.source_id,
                position.stream_ref,
                position.ordinal,
                proof.end,
            )
            is Eligibility.EXCLUDED
            for project in registry.projects
        )

    @staticmethod
    def _paired_frontier(view: ScopeView) -> int:
        # Every observation ending in this exact authenticated prefix was
        # handled when the pair committed, including the retained rival.
        return max((ordinal + 1 for _, ordinal in view._effective_terminals), default=0)

    @staticmethod
    def _paired_receipts(
        boundaries: tuple[SourceBoundary, ...], view: ScopeView
    ) -> set[SourceBoundary]:
        settled = set()
        for terminal, completed in view._effective_terminals:
            if terminal not in boundaries:
                continue
            settled.add(terminal)
            following = min(
                (
                    item
                    for item in boundaries
                    if item.kind is BoundaryKind.TURN
                    and item.ordinal > completed
                    and (item.provider, item.session_ref, item.stream_ref)
                    == (terminal.provider, terminal.session_ref, terminal.stream_ref)
                ),
                default=None,
                key=lambda item: item.ordinal,
            )
            if (
                following is not None
                and following.receipt_ref == terminal.receipt_ref
                and following.epoch_ref == terminal.epoch_ref
            ):
                # Codex repeats this receipt at the first subsequent turn.
                # The exact committed REQUEST already covered the command.
                settled.add(following)
        return settled

    def _boundaries_settled(
        self, read: _Read, view: ScopeView, *, after: int = -1
    ) -> bool:
        evidence = self._store.evidence
        boundaries = tuple(native.boundary for native in read.batch.boundaries)
        if any(not isinstance(item, SourceBoundary) for item in boundaries):
            return False
        settled_receipts = self._paired_receipts(boundaries, view)
        for boundary in boundaries:
            if (
                boundary.ordinal <= after
                or boundary.receipt_ref is None
                or boundary in settled_receipts
            ):
                continue
            position = ScopePosition(
                read.batch.source_id,
                read.batch.surface,
                boundary.session_ref,
                boundary.stream_ref,
                boundary.ordinal,
            )
            _, outcomes = _timeline(view.events, position)
            event_settled = any(
                item.position == position
                and item.native_boundary == boundary
                and outcomes[item.command_id].status
                in (HandoffStatus.APPLIED, HandoffStatus.REJECTED)
                for item in view.events
            )
            matching_holds = tuple(
                hold
                for hold in view.holds
                if hold.position == position
                and evidence.pseudonymize("scope-receipt", str(hold.command_id))
                == boundary.receipt_ref
            )
            if any(hold.state is not HoldState.RESOLVED for hold in matching_holds):
                return False
            # A disposition's original hold does not attest the disposition's
            # separate receipt target. Its verified disposition seam is M08b.
            if not (event_settled or matching_holds):
                return False
        return True

    def _complete(
        self,
        read: _Read,
        view: ScopeView,
        registry: RegistryView,
        selected: tuple[RoutedRevision, ...],
        outcomes: tuple[ClaimDisposition, ...],
    ) -> bool:
        if read.batch.diagnostics or any(
            item.status not in (ClaimStatus.PENDING, ClaimStatus.REPLAY)
            for item in outcomes
        ):
            return False
        selected_ids = {id(item.observation) for item in selected}
        proofs = {id(item.observation): item for item in view._proofs}
        if read.grok is not None:
            return all(
                id(item) in selected_ids for item in read.batch.observations
            ) and all(
                type(native.boundary) is GrokBoundary
                and any(
                    event.position
                    == ScopePosition(
                        read.batch.source_id,
                        read.batch.surface,
                        native.boundary.session_ref,
                        native.boundary.stream_ref,
                        native.boundary.ordinal,
                    )
                    and event.native_boundary == native.boundary
                    and event.reported is not None
                    and event.reported.status is HandoffStatus.APPLIED
                    for event in view.events
                )
                for native in read.batch.boundaries
            )
        settled = self._paired_frontier(view)
        for item in read.batch.observations:
            if id(item) in selected_ids:
                continue
            proof = proofs.get(id(item))
            if proof is None:
                return False
            if proof.end <= settled:
                continue
            if proof.position.ordinal < settled or not self._known_excluded(
                proof, registry
            ):
                return False
            position = proof.position
            if any(
                hold.state is not HoldState.RESOLVED
                and _scope_stream(hold.position) == _scope_stream(position)
                and hold.affected.start < proof.end
                and position.ordinal < hold.affected.end
                for hold in view.holds
            ):
                return False
        return self._boundaries_settled(read, view)

    @staticmethod
    def _record_sequence(connection: sqlite3.Connection, sequence: int) -> None:
        connection.execute("INSERT OR IGNORE INTO commits VALUES (?)", (sequence,))

    def _grok_claim_evidence(
        self,
        candidate: RoutedRevision,
        proof: _ObservationProof,
        project: UUID,
        view: RegistryView,
    ) -> ClaimEvidence:
        admission = candidate._read.grok
        typed = proof.grok
        if (
            admission is None
            or type(typed) not in (_VerifiedGrokMark, _VerifiedGrokHookless)
            or project not in proof.eligible_projects
            or (
                type(typed) is _VerifiedGrokHookless
                and candidate.route.scope is not None
            )
        ):
            raise LedgerError("Grok claim has no original eligible route")
        identity = self._scopes._grok_identity(admission, project)
        epochs = tuple(
            epoch
            for epoch in _grok_records(view)
            if type(epoch) is _GrokEpoch
            and epoch.identity == identity
            and epoch.start.ordinal <= typed.start
            and (epoch.end is None or typed.end <= epoch.end.ordinal)
        )
        if (
            identity is None
            or len(epochs) != 1
            or (proof.position.session_ref, proof.position.stream_ref)
            != (identity.session, identity.stream)
            or proof.end != typed.end
            or typed.key != candidate.observation.key
        ):
            raise LedgerError("Grok claim capture epoch is unavailable")
        (epoch,) = epochs
        return ClaimEvidence(
            identity.source_id,
            identity.surface,
            identity.session,
            identity.stream,
            typed.start,
            typed.end,
            epoch.generation,
            epoch.start.boundary,
        )

    def _claim(
        self,
        connection: sqlite3.Connection,
        candidate: RoutedRevision,
        proof: _ObservationProof,
        registry: RegistryView,
        sequence: int,
    ) -> ClaimDisposition:
        observation = candidate.observation
        key = observation.key
        project = candidate.route.project_id
        if project is None:
            raise LedgerError("Journal claim has no verified project")
        usage_type = type(observation.usage)
        if usage_type is not UsageObservation and (
            usage_type is not GrokObservation
            or observation.revision != 1
            or candidate._read.grok is None
        ):
            return ClaimDisposition(ClaimStatus.HELD, key, project, _tip(connection))

        evidence = self._store.evidence
        evidence.validate_source_ref(key)
        existing = connection.execute(
            "SELECT project,digest,payload,sequence FROM claims WHERE key = ?",
            (key.value,),
        ).fetchone()
        if observation.revision != 1 and existing is None:
            return ClaimDisposition(ClaimStatus.HELD, key, project, _tip(connection))
        _encode(
            observation.usage,
            usage_type,
            validate_ref=evidence.validate_source_ref,
        )
        material = _UsageMaterial(
            observation.usage, candidate.route.scope, observation.time_basis
        )
        digest = _claim_digest(material)
        position = (
            self._grok_claim_evidence(candidate, proof, project, registry)
            if usage_type is GrokObservation
            else _evidence(proof, project, registry)
        )
        location = _encode(
            position, ClaimEvidence, validate_ref=evidence.validate_source_ref
        )

        if existing is None:
            if not self._delivery_capacity(connection, project):
                return ClaimDisposition(
                    ClaimStatus.HELD, key, project, _tip(connection)
                )
            self._record_sequence(connection, sequence)
            payload = _encode(_ClaimPayload(material, position), _ClaimPayload).encode()
            connection.execute(
                "INSERT INTO claims(key,project,digest,payload,sequence) VALUES (?,?,?,?,?)",
                (key.value, str(project), digest, payload, sequence),
            )
            return ClaimDisposition(ClaimStatus.PENDING, key, project, sequence)

        old_project, old_digest, old_payload, old_sequence = existing
        first = _stored_claim(old_payload, old_digest)
        if str(project) != old_project:
            params = (key.value, str(project), digest, location.encode())
            dispute = connection.execute(
                "SELECT sequence FROM disputes WHERE (key,contender,digest,evidence) = (?,?,?,?)",
                params,
            ).fetchone()
            if dispute is not None:
                return ClaimDisposition(
                    ClaimStatus.DISPUTED, key, UUID(old_project), dispute[0]
                )
            self._record_sequence(connection, sequence)
            connection.execute(
                "INSERT INTO disputes(key,contender,digest,evidence,sequence) VALUES (?,?,?,?,?)",
                (*params, sequence),
            )
            return ClaimDisposition(
                ClaimStatus.DISPUTED, key, UUID(old_project), sequence
            )

        disputed = connection.execute(
            "SELECT min(sequence) FROM disputes WHERE key = ?", (key.value,)
        ).fetchone()[0]
        content = connection.execute(
            "SELECT sequence,payload FROM content_disputes WHERE key = ?",
            (key.value,),
        ).fetchone()
        if (
            observation.revision == 1
            and digest == old_digest
            and (usage_type is not GrokObservation or first.evidence == position)
        ):
            if disputed is not None:
                return ClaimDisposition(ClaimStatus.DISPUTED, key, project, disputed)
            if content is None:
                return ClaimDisposition(ClaimStatus.REPLAY, key, project, old_sequence)
        held = ClaimDisposition(ClaimStatus.HELD, key, project, old_sequence)
        if (
            (disputed is not None and content is None)
            or observation.revision == 1
            or observation.native_surface is not NativeSurface.CLAUDE_CODE_MACOS
        ):
            return held
        return self._reserve_revision(
            connection, candidate, position, registry, sequence, first, held, content
        )

    def _reserve_revision(
        self,
        connection: sqlite3.Connection,
        candidate: RoutedRevision,
        position: ClaimEvidence,
        registry: RegistryView,
        sequence: int,
        first: _ClaimPayload,
        held: ClaimDisposition,
        content: tuple[int, bytes] | None,
    ) -> ClaimDisposition:
        observation = candidate.observation
        key, owner = held.key, held.project_id
        original = first.evidence
        if (
            candidate.route.scope != first.material.scope
            or observation.time_basis is not first.material.time_basis
            or observation.usage.observed_at != first.material.usage.observed_at
            or _claim_span(position) != _claim_span(original)
        ):
            return held
        batch = candidate._read.batch
        proof = self._scopes.verified_revision(batch, observation)
        if proof is None or proof.route != candidate.route:
            return held
        witness = proof.witness
        evidence = self._store.evidence
        cursor = batch._native_cursor
        assert cursor is not None
        if content is not None:
            written, raw = content
            dispute = _stored_content_dispute(
                connection, key, original, written, raw, evidence
            )
            if _matches_content_edge(dispute.accepted, dispute.common, witness) or (
                _matches_content_edge(dispute.contender, dispute.common, witness)
                and position == dispute.contender.origin
                and (cursor.locator_ref, cursor.incarnation_ref)
                == (dispute.contender.locator_ref, dispute.contender.incarnation_ref)
            ):
                return ClaimDisposition(ClaimStatus.DISPUTED, key, owner, written)
            return held

        known = _revision_by_material(
            connection, key, witness.successor_material, evidence
        )
        if known is not None:
            if _same_revision(known, witness):
                return ClaimDisposition(ClaimStatus.REPLAY, key, owner, known.sequence)
            return held

        if position.source_id != original.source_id:
            return self._record_content_dispute(
                connection,
                candidate,
                position,
                registry,
                sequence,
                first,
                held,
                witness,
            )
        if position != original or not _original_capture(
            batch, owner, original, registry
        ):
            return held
        latest = _revision_head(connection, key, sequence, evidence)
        if latest is None:
            genesis = replace(observation, revision=1, usage=first.material.usage)
            if witness.predecessor_material != _claude_revision_material(
                evidence, genesis
            ):
                return held
        else:
            if (
                witness.predecessor_material != latest.material
                or witness.predecessor_ordinal != latest.ordinal
                or (cursor.locator_ref, cursor.incarnation_ref)
                != (latest.payload.locator_ref, latest.payload.incarnation_ref)
            ):
                return held
            predecessor = self._scopes.verified_revision(batch, witness.predecessor)
            if (
                predecessor is None
                or predecessor.witness.prefix_ref != latest.payload.prefix_ref
            ):
                return held

        if not self._delivery_capacity(connection, owner, replaces=key):
            return held
        assert type(observation.usage) is UsageObservation
        payload = _RevisionPayload(
            observation.usage,
            observation.revision,
            witness.prefix_ref,
            cursor.locator_ref,
            cursor.incarnation_ref,
        )
        data = _encode(
            payload, _RevisionPayload, validate_ref=evidence.validate_source_ref
        ).encode()
        self._record_sequence(connection, sequence)
        connection.execute(
            "INSERT INTO claim_revisions(key,sequence,later_ordinal,material,predecessor,payload)"
            " VALUES (?,?,?,?,?,?)",
            (
                key.value,
                sequence,
                witness.later_ordinal,
                witness.successor_material.value,
                witness.predecessor_material.value,
                data,
            ),
        )
        return ClaimDisposition(ClaimStatus.PENDING, key, owner, sequence)

    def _record_content_dispute(
        self,
        connection: sqlite3.Connection,
        candidate: RoutedRevision,
        position: ClaimEvidence,
        registry: RegistryView,
        sequence: int,
        first: _ClaimPayload,
        held: ClaimDisposition,
        witness: _NativeRevisionWitness,
    ) -> ClaimDisposition:
        key, owner = held.key, held.project_id
        evidence = self._store.evidence
        common = _revision_by_material(
            connection, key, witness.predecessor_material, evidence
        )
        if common is None or witness.predecessor_ordinal != common.ordinal:
            return held
        batch = candidate._read.batch
        predecessor = self._scopes.verified_revision(batch, witness.predecessor)
        if predecessor is None or not _same_revision(common, predecessor.witness):
            return held

        usage = candidate.observation.usage
        assert type(usage) is UsageObservation
        if usage == first.material.usage:
            return held
        child = _distinct_accepted_child(
            connection, key, common.material, usage, evidence
        )

        cursor = batch._native_cursor
        assert cursor is not None
        if (
            child is None
            or child.ordinal <= common.ordinal
            or witness.later_ordinal <= common.ordinal
            or witness.prefix_ref == child.payload.prefix_ref
            or cursor.incarnation_ref == child.payload.incarnation_ref
            or not _original_capture(batch, owner, position, registry)
        ):
            return held

        payload = _ContentDisputePayload(
            common.material,
            _accepted_edge(child, first.evidence),
            _ContentEdge(
                witness.successor_material,
                position,
                witness.later_ordinal,
                witness.prefix_ref,
                cursor.locator_ref,
                cursor.incarnation_ref,
            ),
        )
        data = _encode(
            payload, _ContentDisputePayload, validate_ref=evidence.validate_source_ref
        ).encode()
        self._record_sequence(connection, sequence)
        connection.execute(
            "INSERT INTO content_disputes(key,sequence,payload) VALUES (?,?,?)",
            (key.value, sequence, data),
        )
        return ClaimDisposition(ClaimStatus.DISPUTED, key, owner, sequence)

    def _write_progress(
        self, connection: sqlite3.Connection, read: _Read, sequence: int
    ) -> None:
        evidence = self._store.evidence
        if read.grok is not None:
            value = _grok_progress(read.progress, read.stream, evidence)
            data = _encode(
                value, _GrokProgress, validate_ref=evidence.validate_source_ref
            ).encode()
        else:
            data = _encode(
                read.progress, StreamCursor, validate_ref=evidence.validate_source_ref
            ).encode()
        self._record_sequence(connection, sequence)
        connection.execute(
            "INSERT INTO progress(source,surface,stream,locator,incarnation,sequence,cursor)"
            " VALUES (?,?,?,?,?,?,?)",
            (*read.stream, sequence, data),
        )

    def _reserve(
        self, read: _Read, selected: tuple[RoutedRevision, ...]
    ) -> tuple[ClaimDisposition, ...]:
        with self._store.transaction(write=True) as connection:
            current = self._cursor(connection, read.stream)
            if current != read.prior and current != read.progress:
                raise ConflictError("Journal cursor changed after preparation")
            if read.prior is not None and read.prior != read.progress:
                if read.grok is not None:
                    old = _grok_checkpoint(read.prior, read.stream)
                    new = _grok_checkpoint(read.progress, read.stream)
                else:
                    old = _source_checkpoint(read.prior).cursor
                    new = _source_checkpoint(read.progress).cursor
                if new.offset <= old.offset:
                    raise ConflictError(
                        "Journal cursor did not advance its verified physical prefix"
                    )
            view, registry = self._fresh_view(connection, read)
            proofs = {id(item.observation): item for item in view._proofs}
            settled = 0 if read.grok is not None else self._paired_frontier(view)
            for item in selected:
                if (
                    id(item.observation) not in proofs
                    or proofs[id(item.observation)].position.ordinal < settled
                    or resolve_route(item.observation, registry, view) != item.route
                ):
                    raise LedgerError("Journal route changed after preparation")
            sequence = _tip(connection) + 1
            outcomes = tuple(
                self._claim(
                    connection, item, proofs[id(item.observation)], registry, sequence
                )
                for item in selected
            )
            if current != read.progress and self._complete(
                read, view, registry, selected, outcomes
            ):
                self._write_progress(connection, read, sequence)

            final_view, final_registry = self._fresh_view(connection, read)
            if final_view != view or final_registry != registry:
                raise LedgerError("Journal scope or registry changed before commit")
            return outcomes

    def reserve(
        self, candidate: RoutedRevision, progress: StreamCursor
    ) -> ClaimDisposition:
        """Stage one observation without advancing over unhandled batch obligations."""
        if (
            type(candidate) is not RoutedRevision
            or self._candidates.get(id(candidate)) is not candidate
            or candidate._read.progress is not progress
        ):
            raise LedgerError("Journal candidate or cursor was not issued together")
        (outcome,) = self._reserve(candidate._read, (candidate,))
        return outcome

    def reserve_batch(self, prepared: PreparedRouting) -> tuple[ClaimDisposition, ...]:
        """Stage all verified claims and eligible same-read progress atomically."""
        if (
            type(prepared) is not PreparedRouting
            or self._batches.get(id(prepared)) is not prepared
        ):
            raise LedgerError("Journal batch was not issued by this writer")
        return self._reserve(prepared._read, prepared.candidates)

    def record_disposition(self, change: VerifiedRouteDisposition) -> JournalChange:
        """Record a current proposal while leaving routing and progress intact."""
        with self._store.transaction(write=True) as connection:
            record = self._scopes.require_route_disposition(change)
            hold = change.hold
            if (record.hold_id, record.hold_state) != (hold.command_id, hold.state):
                raise LedgerError("Verified journal disposition changed its hold")
            payload = _JournalDispositionPayload(
                hold.project_id,
                hold.position,
                hold.affected.start,
                hold.affected.end,
                hold.command_digest,
                record,
            )
            evidence = self._store.evidence
            command, hold_id = str(record.command_id), str(record.hold_id)
            row = connection.execute(
                _DISPOSITION_ROWS + " WHERE d.command = ?", (command,)
            ).fetchone()
            if row is not None:
                written = _stored_disposition(row, evidence)
                if written.disposition != payload:
                    raise ConflictError("Journal disposition command changed")
            else:
                if (
                    connection.execute(
                        "SELECT 1 FROM route_dispositions WHERE hold = ?", (hold_id,)
                    ).fetchone()
                    is not None
                ):
                    raise ConflictError(
                        "Journal hold already has a recorded disposition"
                    )
                sequence = _tip(connection) + 1
                raw = _encode(
                    payload,
                    _JournalDispositionPayload,
                    validate_ref=evidence.validate_source_ref,
                ).encode("utf-8")
                self._record_sequence(connection, sequence)
                connection.execute(
                    "INSERT INTO route_dispositions VALUES (?, ?, ?, ?)",
                    (command, hold_id, sequence, raw),
                )
                written = JournalChange(sequence, payload)
            # The scope check releases the inbox lock before SQLite commits.
            # The durable row records historical evidence for a proposal.
            if self._scopes.require_route_disposition(change) != record:
                raise LedgerError("Verified journal disposition changed before commit")
            return written

    def _settlements(
        self, connection: sqlite3.Connection, limit: int
    ) -> tuple[JournalChange, ...]:
        if self._store._current_version(connection) < _PAIRED_SCHEMA_VERSION:
            return ()
        evidence = self._store.evidence
        changes = []
        used_ids: set[UUID] = set()
        used_keys: set[SourceRef] = set()
        for sequence, raw, commit in connection.execute(
            "SELECT s.sequence,s.payload,c.sequence FROM paired_settlements s"
            " LEFT JOIN commits c ON c.sequence=s.sequence"
            " WHERE s.sequence <= ? ORDER BY s.sequence",
            (limit,),
        ):
            try:
                _positive(sequence)
                stored = _decode(
                    raw, _StoredSettlement, validate_ref=evidence.validate_source_ref
                )
                pair = stored.pair
                if (
                    commit != sequence
                    or stored.identity != _settlement_identity(sequence, pair, evidence)
                    or raw != _encode(stored, _StoredSettlement).encode()
                ):
                    raise ValueError("Invalid paired settlement identity")
                _check_distinct_sides(pair)
                ids = {
                    item
                    for side in (pair.owner, pair.rival)
                    for item in (side.release.command_id, side.release.hold.command_id)
                }
                if ids & used_ids or pair.key in used_keys:
                    raise ValueError("Duplicate paired settlement identity")
                for side in (pair.owner, pair.rival):
                    _validate_settled_side(side, sequence, evidence)
                    row = connection.execute(
                        "SELECT cursor FROM progress"
                        " WHERE (source,surface,stream,locator,incarnation,sequence)"
                        " = (?,?,?,?,?,?)",
                        (*_settlement_stream(side), sequence),
                    ).fetchone()
                    if row != (_encode(side.cursor, StreamCursor).encode(),):
                        raise ValueError("Invalid paired settlement progress")
                self._validate_settlement_claims(connection, pair)
            except (TypeError, ValueError):
                raise LedgerError("Invalid stored paired settlement") from None
            used_ids.update(ids)
            used_keys.add(pair.key)
            changes.append(JournalChange(sequence, paired=pair))
        return tuple(changes)

    def _effective_releases(
        self, connection: sqlite3.Connection
    ) -> tuple[tuple[_JournalScopeRelease, ...], frozenset[UUID]]:
        releases = []
        conflicts: set[UUID] = set()
        for change in self._settlements(connection, _tip(connection)):
            assert change.paired is not None
            for side in (change.paired.owner, change.paired.rival):
                release = side.release
                ids = (str(release.command_id), str(release.hold.command_id))
                rows = connection.execute(
                    "SELECT 1 FROM route_dispositions"
                    " WHERE command IN (?,?) OR hold IN (?,?) LIMIT 1",
                    (*ids, *ids),
                )
                if rows.fetchone() is not None:
                    conflicts.add(release.hold.command_id)
                releases.append(release)
        return tuple(releases), frozenset(conflicts)

    def _validate_settlement_claims(
        self, connection: sqlite3.Connection, pair: _PairedSettlement
    ) -> None:
        owner, rival = pair.owner, pair.rival
        first = connection.execute(
            "SELECT project,digest,payload,sequence FROM claims WHERE key = ?",
            (pair.key.value,),
        ).fetchone()
        if (
            first is None
            or (first[0], first[1], first[3])
            != (
                str(owner.release.hold.project_id),
                owner.claim_digest,
                owner.claim_sequence,
            )
            or _stored_claim(first[2], first[1]).evidence != owner.claim
        ):
            raise LedgerError("Paired settlement first ownership changed")
        dispute = connection.execute(
            "SELECT sequence FROM disputes WHERE (key,contender,digest,evidence) = (?,?,?,?)",
            (
                pair.key.value,
                str(rival.release.hold.project_id),
                rival.claim_digest,
                _encode(rival.claim, ClaimEvidence).encode(),
            ),
        ).fetchone()
        if dispute != (rival.claim_sequence,):
            raise LedgerError("Paired settlement ownership dispute changed")

    def _settled_side(
        self,
        key: SourceRef,
        side: _VerifiedSettlementSide,
        releases: tuple[_JournalScopeRelease, ...],
        conflicts: frozenset[UUID],
        claim_sequence: int,
    ) -> tuple[_SettledSide, ScopeView]:
        terminal = side._terminal
        if (
            type(terminal.boundary) is not SourceBoundary
            or terminal.project_context is None
        ):
            raise LedgerError("Paired settlement needs an exact owned terminal")
        release = _JournalScopeRelease(
            side.hold,
            side._original,
            side.command.command_id,
            terminal.project_context,
            side._prior_route,
            terminal.boundary,
            _source_checkpoint(side.progress.cursor).provider.ordinal,
            _source_checkpoint(side.progress.cursor).cursor,
            HoldState.RESOLVED,
        )
        view = side._issuer._journal_view(
            side._batch, (*releases, release), conflicts, progress=side.progress
        )
        registry = view._registry
        assert registry is not None
        claims = [
            item
            for item in side.progress.proofs
            if item.observation.key == key
            and side.hold.affected.start
            <= item.position.ordinal
            < item.end
            <= side.hold.affected.end
        ]
        if len(claims) != 1:
            raise LedgerError("Paired settlement lacks one exact native obligation")
        (proof,) = claims
        observation = proof.observation
        route = resolve_route(observation, registry, view)
        if (
            route.status is not RouteStatus.ROUTED
            or route.project_id != side.hold.project_id
            or observation.revision != 1
            or type(observation.usage) is not UsageObservation
        ):
            raise LedgerError("Paired settlement obligation is not exactly routed")
        material = _UsageMaterial(
            observation.usage, route.scope, observation.time_basis
        )
        return _SettledSide(
            release,
            _scope_command_digest(side.command),
            side.request.digest,
            side.request.grant_id,
            side.progress.cursor,
            _evidence(proof, side.hold.project_id, registry),
            _claim_digest(material),
            claim_sequence,
        ), view

    def _advance_settlement_side(
        self,
        connection: sqlite3.Connection,
        key: SourceRef,
        side: _VerifiedSettlementSide,
        settled: _SettledSide,
        view: ScopeView,
        sequence: int,
    ) -> None:
        batch = side._batch
        stream = _stream(batch.source_id, batch._locator)
        prior = self._cursor(connection, stream)
        next_cursor = _source_checkpoint(settled.cursor).cursor
        old_ordinal = -1
        if prior is not None:
            old = _source_checkpoint(prior)
            if old.cursor.offset >= next_cursor.offset:
                raise LedgerError(
                    "Paired settlement does not advance its native prefix"
                )
            old_ordinal = old.provider.ordinal
            _capture_position(batch._locator._source, old.cursor, fixed=next_cursor)
        read = _Read(batch, stream, prior, settled.cursor)
        registry = view._registry
        assert registry is not None
        if any(
            hold.state is not HoldState.RESOLVED
            and _scope_stream(hold.position) == _scope_stream(side.hold.position)
            and hold.affected.end > old_ordinal + 1
            and hold.affected.start
            <= _source_checkpoint(settled.cursor).provider.ordinal
            for hold in view.holds
        ):
            raise LedgerError("Paired settlement encounters an unrelated held span")
        if not self._boundaries_settled(read, view, after=old_ordinal):
            raise LedgerError("Paired settlement encounters an unrelated receipt")
        for proof in side.progress.proofs:
            observation = proof.observation
            if proof.end <= old_ordinal + 1:
                continue
            if proof.position.ordinal <= old_ordinal:
                raise LedgerError("Paired settlement overlaps the prior cursor")
            if observation.key == key:
                if _evidence(proof, side.hold.project_id, registry) != settled.claim:
                    raise LedgerError(
                        "Paired settlement encounters another disputed copy"
                    )
                continue
            route = resolve_route(observation, registry, view)
            if route.status is not RouteStatus.ROUTED:
                if not self._known_excluded(proof, registry):
                    raise LedgerError("Paired settlement has unrouted native usage")
                continue
            result = self._claim(
                connection,
                RoutedRevision(observation, route, read),
                proof,
                registry,
                sequence,
            )
            if result.status not in (ClaimStatus.PENDING, ClaimStatus.REPLAY):
                raise LedgerError(
                    "Paired settlement encounters an unrelated claim conflict"
                )
            if result.status is ClaimStatus.REPLAY:
                row = connection.execute(
                    "SELECT payload,digest FROM claims WHERE key = ?",
                    (result.key.value,),
                ).fetchone()
                if row is None or _stored_claim(*row).evidence != _evidence(
                    proof, result.project_id, registry
                ):
                    raise LedgerError("Paired settlement claim replay changed its span")
        self._write_progress(connection, read, sequence)

    def _build_settlement_change(
        self,
        connection: sqlite3.Connection,
        key: SourceRef,
        owner: _VerifiedSettlementSide,
        rival: _VerifiedSettlementSide,
    ) -> tuple[JournalChange, bool]:
        tip = _tip(connection)
        previous = self._settlements(connection, tip)
        releases, conflicts = self._effective_releases(connection)
        evidence = self._store.evidence
        evidence.validate_source_ref(key)
        sides = (owner, rival)
        ids = {
            item
            for side in sides
            for item in (side.command.command_id, side.hold.command_id)
        }
        encoded_ids = tuple(str(item) for item in ids)
        if (
            len(ids) != 4
            or connection.execute(
                "SELECT 1 FROM route_dispositions WHERE command IN (?,?,?,?)"
                " OR hold IN (?,?,?,?) LIMIT 1",
                (*encoded_ids, *encoded_ids),
            ).fetchone()
            is not None
        ):
            raise LedgerError("Paired settlement conflicts with a historical proposal")
        existing = None
        for old in previous:
            assert old.paired is not None
            old_ids = {
                item
                for side in (old.paired.owner, old.paired.rival)
                for item in (side.release.command_id, side.release.hold.command_id)
            }
            if old.paired.key == key or old_ids & ids:
                if old.paired.key != key or old_ids != ids:
                    raise ConflictError(
                        "Paired settlement conflicts with committed history"
                    )
                existing = old
        owner_row = connection.execute(
            "SELECT sequence FROM claims WHERE key = ?", (key.value,)
        ).fetchone()
        disputes = connection.execute(
            "SELECT sequence FROM disputes WHERE key = ?", (key.value,)
        ).fetchall()
        if (
            owner_row is None
            or len(disputes) != 1
            or connection.execute(
                "SELECT 1 FROM content_disputes WHERE key = ?", (key.value,)
            ).fetchone()
            is not None
        ):
            raise LedgerError(
                "Paired settlement requires exactly one ownership dispute"
            )
        # Retry compares the exact original release once rather than applying it twice.
        other_releases = tuple(
            row for row in releases if row.hold.command_id not in ids
        )
        first, first_view = self._settled_side(
            key, owner, other_releases, conflicts, owner_row[0]
        )
        second, second_view = self._settled_side(
            key, rival, other_releases, conflicts, disputes[0][0]
        )
        pair = _PairedSettlement(key, first, second)
        sequence = existing.sequence if existing is not None else tip + 1
        _check_distinct_sides(pair)
        for side in (first, second):
            _validate_settled_side(side, sequence, evidence)
        self._validate_settlement_claims(connection, pair)
        if existing is not None:
            if existing.paired != pair:
                raise ConflictError("Paired settlement retry changed its evidence")
            return existing, False
        self._advance_settlement_side(
            connection, key, owner, first, first_view, sequence
        )
        self._advance_settlement_side(
            connection, key, rival, second, second_view, sequence
        )
        stored = _StoredSettlement(pair, _settlement_identity(sequence, pair, evidence))
        self._store._enable_paired(connection)
        connection.execute(
            "INSERT INTO paired_settlements VALUES (?,?)",
            (sequence, _encode(stored, _StoredSettlement).encode()),
        )
        return JournalChange(sequence, paired=pair), True

    def settle_disposition(
        self,
        key: SourceRef,
        owner: _VerifiedSettlementSide,
        rival: _VerifiedSettlementSide,
    ) -> JournalChange:
        """Commit one effective release and both exact native frontiers."""
        if (
            type(owner) is not _VerifiedSettlementSide
            or type(rival) is not _VerifiedSettlementSide
            or owner._issuer is rival._issuer
            or any(side._issuer.registry is not self._writer for side in (owner, rival))
            or owner.scope_digest != rival.scope_digest
        ):
            raise LedgerError(
                "Expected independent settlement proofs under one scope writer"
            )
        sides = (owner, rival)
        try:
            with self._scopes._route_requests((owner.command, rival.command)) as (
                requests,
                recheck,
            ):
                with self._store.transaction(write=True) as connection:
                    for side, request in zip(sides, requests, strict=True):
                        side._issuer._require_settlement_side(side, request)
                    change, inserted = self._build_settlement_change(
                        connection, key, owner, rival
                    )
                    if (
                        inserted
                        and self._settlements(connection, change.sequence)[-1] != change
                    ):
                        raise LedgerError(
                            "Paired settlement failed transactional readback"
                        )
                    for side, request in zip(sides, requests, strict=True):
                        side._issuer._require_settlement_side(side, request)
                    recheck()
            with self._store.transaction() as connection:
                if change not in self._settlements(connection, change.sequence):
                    raise LedgerError("Paired settlement failed committed readback")
                for side in sides:
                    side._issuer._require_batch_qualification(side._batch)
                    cursor = _source_checkpoint(side.progress.cursor).cursor
                    _capture_position(
                        side._batch._locator._source, cursor, fixed=cursor
                    )
            return change
        except (_CaptureDiscontinuity, OSError, sqlite3.Error, ValueError):
            raise LedgerError(
                "Unable to verify paired settlement and its native prefixes"
            ) from None

    def as_of(self, sequence: int | None = None) -> JournalView:
        """Read immutable first claims and disputes at a private journal sequence."""
        with self._store.transaction() as connection:
            head = _tip(connection)
            limit = head if sequence is None else sequence
            if type(limit) is not int or not 0 <= limit <= head:
                raise ValueError("Journal sequence is unavailable")
            claims = []
            evidence = self._store.evidence
            for key, project, raw, digest, written in connection.execute(
                "SELECT key,project,payload,digest,sequence FROM claims"
                " WHERE sequence <= ? ORDER BY sequence, key",
                (limit,),
            ):
                payload = _stored_claim(raw, digest)
                observation_key = SourceRef(key)
                evidence.validate_source_ref(observation_key)
                _encode(
                    payload.evidence,
                    ClaimEvidence,
                    validate_ref=evidence.validate_source_ref,
                )
                _encode(
                    payload.material.usage,
                    UsageObservation | GrokObservation,
                    validate_ref=evidence.validate_source_ref,
                )
                revision = _revision_head(connection, observation_key, limit, evidence)
                claims.append(
                    PendingClaim(
                        observation_key,
                        UUID(project),
                        payload.material.usage
                        if revision is None
                        else revision.payload.usage,
                        payload.material.scope,
                        payload.material.time_basis,
                        payload.evidence,
                        written if revision is None else revision.sequence,
                        1 if revision is None else revision.payload.revision,
                    )
                )
            disputes = []
            for key, contender, raw, written in connection.execute(
                "SELECT key, contender, evidence, sequence FROM disputes"
                " WHERE sequence <= ? ORDER BY sequence, key, contender, digest",
                (limit,),
            ):
                observation_key = SourceRef(key)
                evidence.validate_source_ref(observation_key)
                disputes.append(
                    OwnershipDispute(
                        observation_key,
                        UUID(contender),
                        _decode(
                            raw,
                            ClaimEvidence,
                            validate_ref=evidence.validate_source_ref,
                        ),
                        written,
                    )
                )
            content_disputes = []
            for key, project, first, digest, written, raw in connection.execute(
                "SELECT d.key,c.project,c.payload,c.digest,d.sequence,d.payload"
                " FROM content_disputes d JOIN claims c ON d.key = c.key"
                " WHERE d.sequence <= ? ORDER BY d.sequence,d.key",
                (limit,),
            ):
                observation_key = SourceRef(key)
                evidence.validate_source_ref(observation_key)
                payload = _stored_content_dispute(
                    connection,
                    observation_key,
                    _stored_claim(first, digest).evidence,
                    written,
                    raw,
                    evidence,
                )
                content_disputes.append(
                    ContentDispute(
                        observation_key,
                        UUID(project),
                        payload.common,
                        payload.accepted,
                        payload.contender,
                        written,
                    )
                )
            dispositions = []
            for row in connection.execute(
                _DISPOSITION_ROWS
                + " WHERE d.sequence <= ? ORDER BY d.sequence, d.command",
                (limit,),
            ):
                change = _stored_disposition(row, evidence)
                assert change.disposition is not None
                affected = _affected_disposition_keys(
                    change.disposition, claims, disputes, content_disputes
                )
                dispositions.append(JournalChangeProjection(change, affected))
            return JournalView(
                limit,
                tuple(claims),
                tuple(disputes),
                tuple(content_disputes),
                tuple(dispositions),
                self._settlements(connection, limit),
            )
