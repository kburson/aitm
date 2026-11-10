"""Writer-bound private routing claims and native replay checkpoints."""

import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from uuid import UUID
from weakref import WeakValueDictionary

from ._monitor_journal_store import JournalStore
from .ledger import ConflictError, LedgerError
from .monitor_registry import Registry, RegistryView
from .monitor_scope import (
    HandoffStatus,
    HoldState,
    RouteDecision,
    RouteStatus,
    Scope,
    ScopePosition,
    ScopeState,
    ScopeView,
    VerifiedScopeBatch,
    _ObservationProof,
    _timeline,
    resolve_route,
)
from .monitor_scope import (
    _stream as _scope_stream,
)
from .monitor_types import NativeSurface, ObservationTimeBasis
from .sources.adapter import NativeObservation, SourceLocator, StreamCursor
from .sources.scan import CandidateSource
from .types import (
    Eligibility,
    SourceBoundary,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
    _decode,
    _encode,
    _nonnegative,
    _positive,
)

_Stream = tuple[str, str, str, str, str]


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
class PendingClaim:
    key: SourceRef
    project_id: UUID
    usage: UsageObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis
    evidence: ClaimEvidence
    sequence: int


@dataclass(frozen=True, slots=True)
class OwnershipDispute:
    key: SourceRef
    contender: UUID
    evidence: ClaimEvidence
    sequence: int


@dataclass(frozen=True, slots=True)
class JournalView:
    sequence: int
    claims: tuple[PendingClaim, ...]
    disputes: tuple[OwnershipDispute, ...]


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
            "SELECT project, digest, sequence FROM claims WHERE key = ?", (key.value,)
        ).fetchone()
        if observation.revision != 1 and (
            existing is None or existing[0] == str(project)
        ):
            return ClaimDisposition(ClaimStatus.HELD, key, project, _tip(connection))
        _encode(
            observation.usage,
            UsageObservation,
            validate_ref=evidence.validate_source_ref,
        )
        material = _UsageMaterial(
            observation.usage, candidate.route.scope, observation.time_basis
        )
        digest = sha256(_encode(material, _UsageMaterial).encode()).hexdigest()
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

        old_project, old_digest, old_sequence = existing
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

        if digest != old_digest:
            return ClaimDisposition(ClaimStatus.HELD, key, project, old_sequence)
        disputed = connection.execute(
            "SELECT min(sequence) FROM disputes WHERE key = ?", (key.value,)
        ).fetchone()[0]
        if disputed is not None:
            return ClaimDisposition(ClaimStatus.DISPUTED, key, project, disputed)
        return ClaimDisposition(ClaimStatus.REPLAY, key, project, old_sequence)

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

    def as_of(self, sequence: int | None = None) -> JournalView:
        """Read immutable first claims and disputes at a private journal sequence."""
        with self._store.transaction() as connection:
            head = _tip(connection)
            limit = head if sequence is None else sequence
            if type(limit) is not int or not 0 <= limit <= head:
                raise ValueError("Journal sequence is unavailable")
            claims = []
            evidence = self._store.evidence
            for key, project, raw, written in connection.execute(
                "SELECT key, project, payload, sequence FROM claims"
                " WHERE sequence <= ? ORDER BY sequence, key",
                (limit,),
            ):
                payload = _decode(raw, _ClaimPayload)
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
                claims.append(
                    PendingClaim(
                        observation_key,
                        UUID(project),
                        payload.material.usage,
                        payload.material.scope,
                        payload.material.time_basis,
                        payload.evidence,
                        written,
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
            return JournalView(limit, tuple(claims), tuple(disputes))
