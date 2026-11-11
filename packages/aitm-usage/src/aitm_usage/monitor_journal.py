"""Writer-bound private routing claims and native replay checkpoints."""

import re
import sqlite3
from dataclasses import dataclass, field, replace
from enum import StrEnum
from hashlib import sha256
from itertools import chain
from uuid import UUID
from weakref import WeakValueDictionary

from ._monitor_journal_store import JournalStore
from .ledger import ConflictError, LedgerError
from .monitor_registry import Registry, RegistryView, _ServiceEvidence
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
    _ObservationProof,
    _RouteDispositionRecord,
    _timeline,
    resolve_route,
)
from .monitor_scope import (
    _stream as _scope_stream,
)
from .monitor_types import NativeSurface, ObservationTimeBasis
from .sources.adapter import (
    NativeObservation,
    SourceLocator,
    StreamCursor,
    _claude_revision_material,
    _NativeRevisionWitness,
)
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

_Stream = tuple[str, str, str, str, str]
_DISPOSITION_ROWS = (
    "SELECT d.command,d.hold,d.sequence,c.sequence,d.payload"
    " FROM route_dispositions d LEFT JOIN commits c ON c.sequence=d.sequence"
)


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
    usage: UsageObservation
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
    usage: UsageObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis
    evidence: ClaimEvidence
    sequence: int
    revision: int = 1


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
class JournalChange:
    sequence: int
    disposition: _JournalDispositionPayload


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


@dataclass(frozen=True, slots=True)
class _Read:
    batch: VerifiedScopeBatch = field(repr=False)
    stream: _Stream = field(repr=False)
    prior: StreamCursor | None = field(repr=False)
    progress: StreamCursor = field(repr=False)


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


def _source_checkpoint(progress: StreamCursor) -> SourceCheckpoint:
    if type(progress.checkpoint) is not SourceCheckpoint:
        raise LedgerError("Journal requires a verified native cursor")
    return progress.checkpoint


def _tip(connection: sqlite3.Connection) -> int:
    return connection.execute(
        "SELECT coalesce(max(sequence), 0) FROM commits"
    ).fetchone()[0]


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


class RoutingJournal:
    """Stage exact observations under the existing coordinator writer lease."""

    def __init__(self, writer: Registry, scopes: ScopeState) -> None:
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
        cursor = _decode(
            row[0], StreamCursor, validate_ref=self._store.evidence.validate_source_ref
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
        stream = _stream(source_id, locator)
        prior = self.cursor_for(source_id, locator)
        batch = self._scopes.read_source(source_id, locator, cursor=prior)
        progress = batch.cursor
        if progress is None:
            raise LedgerError("Native read did not provide a verified journal cursor")
        checkpoint = _source_checkpoint(progress).cursor
        if (
            batch.source_id != source_id
            or batch.surface.value != stream[1]
            or (
                checkpoint.source_ref.value,
                checkpoint.locator_ref.value,
                checkpoint.incarnation_ref.value,
            )
            != stream[2:]
        ):
            raise LedgerError("Native read changed the journal cursor identity")
        view = self._scopes.view(batch)
        registry = self._writer.view()
        read = _Read(batch, stream, prior, progress)
        candidates = tuple(
            RoutedRevision(observation, route, read)
            for observation in batch.observations
            if (route := resolve_route(observation, registry, view)).status
            is RouteStatus.ROUTED
        )
        for candidate in candidates:
            self._candidates[id(candidate)] = candidate
        prepared = PreparedRouting(candidates, progress, read)
        self._batches[id(prepared)] = prepared
        return prepared

    def _fresh_view(self, read: _Read) -> tuple[ScopeView, RegistryView]:
        self._writer.lease
        view = self._scopes.view(read.batch, _confirm_publication=True)
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

    def _boundaries_settled(self, read: _Read, view: ScopeView) -> bool:
        evidence = self._store.evidence
        for native in read.batch.boundaries:
            boundary = native.boundary
            if not isinstance(boundary, SourceBoundary):
                return False
            if boundary.receipt_ref is None:
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
        for item in read.batch.observations:
            if id(item) in selected_ids:
                continue
            proof = proofs.get(id(item))
            if proof is None or not self._known_excluded(proof, registry):
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
        if type(observation.usage) is not UsageObservation:
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
            UsageObservation,
            validate_ref=evidence.validate_source_ref,
        )
        material = _UsageMaterial(
            observation.usage, candidate.route.scope, observation.time_basis
        )
        digest = _claim_digest(material)
        position = _evidence(proof, project, registry)
        location = _encode(
            position, ClaimEvidence, validate_ref=evidence.validate_source_ref
        )

        if existing is None:
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
        if observation.revision == 1 and digest == old_digest:
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
        data = _encode(
            read.progress,
            StreamCursor,
            validate_ref=self._store.evidence.validate_source_ref,
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
                old = _source_checkpoint(read.prior).cursor
                new = _source_checkpoint(read.progress).cursor
                if new.offset <= old.offset:
                    raise ConflictError(
                        "Journal cursor did not advance its verified physical prefix"
                    )
            view, registry = self._fresh_view(read)
            proofs = {id(item.observation): item for item in view._proofs}
            for item in selected:
                if (
                    id(item.observation) not in proofs
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

            final_view, final_registry = self._fresh_view(read)
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
                connection.execute("INSERT INTO commits VALUES (?)", (sequence,))
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
                    UsageObservation,
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
            )
