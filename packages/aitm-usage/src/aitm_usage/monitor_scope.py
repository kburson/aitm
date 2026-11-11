"""Private native scope decisions and provenance-only coverage holds."""

import os
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from itertools import groupby
from pathlib import Path
from uuid import UUID
from weakref import WeakValueDictionary

from .ledger import ConflictError, Ledger, LedgerError, _path_exists, _pin_directory
from .monitor_registry import (
    Registry,
    RegistryView,
    _check_capture_root,
    _pinned,
    _project,
    _read_state,
    _ServiceEvidence,
    _source,
)
from .monitor_types import GrokCheckpoint, GrokDiagnostic, NativeSurface
from .scopes import _publish
from .sources.adapter import (
    AdapterBatch,
    CandidateSource,
    NativeBoundary,
    NativeObservation,
    ProviderAdapter,
    SourceLocator,
    StreamCursor,
    _claude_revision_material,
    _GrokSource,
    _NativeRevisionWitness,
)
from .sources.claude import _ClaudeRevisionKind
from .sources.grok import (
    _MAX_NATIVE_BYTES,
    GrokAdapter,
)
from .sources.grok import (
    _Held as _GrokHeld,
)
from .sources.grok import (
    _read_file as _read_grok_file,
)
from .sources.grok import (
    _validate_prior as _validate_grok_prior,
)
from .sources.scan import (
    _capture_position,
    _CaptureDiscontinuity,
    _hash_prefix,
    _open_snapshot,
    _origin,
    _source_prefix_reference,
    _verify_snapshot,
    checkout_anchor_reference,
)
from .types import (
    DevelopmentBinding,
    Diagnostic,
    Eligibility,
    InboxCommand,
    ItemKey,
    ReviewRole,
    ScopeEnrollment,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    UsageObservation,
    WorkPhase,
    _decode,
    _encode,
    _nonnegative,
)

_FILE = "scope-v1.json"
_FORMAT = "aitm.usage.monitor-scope/v1"
_MAX_SNAPSHOT = 1024 * 1024
_MAX_HOLDS = 256
_MAX_AUTHORIZATIONS = 256
_HOLD_TIME = timedelta(minutes=15)


@dataclass(frozen=True, slots=True)
class Scope:
    project_id: UUID
    item: ItemKey | None = None
    phase: WorkPhase | None = None
    participant_ref: SourceRef | None = None
    role: ReviewRole | None = None
    attempt_ref: SourceRef | None = None
    review_ref: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class Mark:
    command_id: UUID
    scope: Scope
    receipt_ref: SourceRef
    destination_binding: DevelopmentBinding | None = None


@dataclass(frozen=True, slots=True)
class Handoff:
    command_id: UUID
    current_project: UUID
    destination: Scope
    before_generation: int
    retained_checkout: SourceRef | None
    receipt_ref: SourceRef
    destination_binding: DevelopmentBinding | None = None

    def __post_init__(self) -> None:
        _nonnegative(self.before_generation)


@dataclass(frozen=True, slots=True)
class Disposition:
    command_id: UUID
    project_id: UUID
    hold_id: UUID
    receipt_ref: SourceRef
    release_previous: bool = False


type ScopeCommand = Mark | Handoff | Disposition


@dataclass(frozen=True, slots=True)
class ScopeAuthority:
    """Transient operator authority bound to the pinned project ledger."""

    project_id: UUID
    key_id: str


@dataclass(frozen=True, slots=True)
class ScopePosition:
    source_id: UUID
    surface: NativeSurface
    session_ref: SourceRef
    stream_ref: SourceRef
    ordinal: int

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)


@dataclass(frozen=True, slots=True)
class AffectedScope:
    start: int
    end: int
    observation_keys: tuple[SourceRef, ...] = ()

    def __post_init__(self) -> None:
        _nonnegative(self.start)
        _nonnegative(self.end)
        if self.end <= self.start:
            raise ValueError("Expected a nonempty native scope span")


class HandoffStatus(StrEnum):
    APPLIED = "applied"
    HELD = "held"
    CONFLICT = "conflict"
    REJECTED = "rejected"


class RouteStatus(StrEnum):
    ROUTED = "routed"
    HELD = "held"
    UNASSIGNED = "unassigned"


class HoldState(StrEnum):
    HELD = "held"
    GAP = "gap"
    RESOLVED = "resolved"


@dataclass(frozen=True, slots=True)
class HandoffDisposition:
    status: HandoffStatus
    affected: AffectedScope
    generation: int | None = None


@dataclass(frozen=True, slots=True)
class RouteDecision:
    status: RouteStatus
    project_id: UUID | None = None
    scope: Scope | None = None
    generation: int | None = None
    affected_projects: tuple[UUID, ...] = ()


@dataclass(frozen=True, slots=True)
class ProofHold:
    command_id: UUID
    command_digest: str
    project_id: UUID
    position: ScopePosition
    affected: AffectedScope
    first_seen: datetime
    expires_at: datetime
    state: HoldState = HoldState.HELD


@dataclass(frozen=True, slots=True)
class _ScopeEvent:
    command_id: UUID
    digest: str
    scope: Scope
    position: ScopePosition
    checkout: SourceRef | None
    anchor_project: UUID | None
    eligible: bool
    affected: AffectedScope
    native_boundary: SourceBoundary | None
    current_project: UUID | None = None
    before_generation: int | None = None
    retained_checkout: SourceRef | None = None
    reported: HandoffDisposition | None = None


@dataclass(frozen=True, slots=True)
class _Resolution:
    command_id: UUID
    digest: str
    result: ProofHold


@dataclass(frozen=True, slots=True)
class _ScopeSnapshot:
    events: tuple[_ScopeEvent, ...] = ()
    holds: tuple[ProofHold, ...] = ()
    resolutions: tuple[_Resolution, ...] = ()
    format: str = _FORMAT


@dataclass(frozen=True, slots=True)
class _ObservationProof:
    observation: NativeObservation = field(repr=False)
    position: ScopePosition
    end: int
    checkout: SourceRef | None
    anchor_project: UUID | None
    eligible_projects: frozenset[UUID]


@dataclass(frozen=True, slots=True, weakref_slot=True)
class VerifiedScopeBatch:
    source_id: UUID
    surface: NativeSurface
    observations: tuple[NativeObservation, ...]
    boundaries: tuple[NativeBoundary, ...]
    diagnostics: tuple[Diagnostic | GrokDiagnostic, ...]
    cursor: StreamCursor | None
    _proofs: tuple[_ObservationProof, ...] = field(repr=False)
    _admitted: frozenset[UUID] = field(repr=False)
    _locator: SourceLocator = field(repr=False)
    _native_cursor: SourceCursor | None = field(repr=False)
    _registry: RegistryView = field(repr=False)
    _revision_witnesses: tuple[
        tuple[NativeObservation, _NativeRevisionWitness], ...
    ] = field(default=(), repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class _VerifiedRevision:
    observation: NativeObservation = field(repr=False)
    witness: _NativeRevisionWitness = field(repr=False)
    route: RouteDecision
    original: ScopePosition
    later: ScopePosition
    _batch: VerifiedScopeBatch = field(repr=False)
    _writer: Registry = field(repr=False)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class VerifiedBoundary:
    """Scope-only proof issued from an approved same-read native receipt."""

    command_id: UUID
    digest: str
    position: ScopePosition
    checkout: SourceRef | None
    anchor_project: UUID | None
    eligible: bool
    affected: AffectedScope
    native_boundary: SourceBoundary | None
    _batch: VerifiedScopeBatch = field(repr=False)
    _authority: ScopeAuthority = field(repr=False)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class ScopeView:
    events: tuple[_ScopeEvent, ...]
    holds: tuple[ProofHold, ...]
    _proofs: tuple[_ObservationProof, ...] = field(default=(), repr=False)
    _registry: RegistryView | None = field(default=None, repr=False)


_ISSUED_VIEWS: WeakValueDictionary[int, ScopeView] = WeakValueDictionary()


@dataclass(frozen=True, slots=True)
class _Route:
    scope: Scope | None = None
    generation: int = 0
    anchor_project: UUID | None = None
    checkout: SourceRef | None = None
    held: tuple[UUID, ...] = ()


def _stream(
    position: ScopePosition,
) -> tuple[UUID, NativeSurface, SourceRef, SourceRef]:
    return (
        position.source_id,
        position.surface,
        position.session_ref,
        position.stream_ref,
    )


def _digest(command: ScopeCommand) -> str:
    return sha256(_encode(command, type(command)).encode()).hexdigest()


def _project_id(command: ScopeCommand) -> UUID:
    if isinstance(command, Handoff):
        return command.current_project
    return command.scope.project_id if isinstance(command, Mark) else command.project_id


def _scope(command: ScopeCommand) -> Scope:
    if isinstance(command, Handoff):
        return command.destination
    return command.scope if isinstance(command, Mark) else Scope(command.project_id)


def _projects(event: _ScopeEvent) -> tuple[UUID, ...]:
    return tuple(
        dict.fromkeys(
            project
            for project in (
                event.anchor_project,
                event.current_project,
                event.scope.project_id,
            )
            if project is not None
        )
    )


def _eligible_event(event: _ScopeEvent, before: _Route) -> HandoffStatus:
    if not event.eligible:
        return HandoffStatus.HELD
    current = None if before.scope is None else before.scope.project_id
    if event.before_generation is None:
        if event.scope.project_id not in (event.anchor_project, current):
            if event.anchor_project is not None or current is not None:
                return HandoffStatus.CONFLICT
        if event.anchor_project not in (None, event.scope.project_id):
            return HandoffStatus.CONFLICT
        return HandoffStatus.APPLIED
    if (
        event.current_project != current
        or event.before_generation != before.generation
        or event.retained_checkout != before.checkout
        or (
            event.checkout != before.checkout
            and event.anchor_project != event.scope.project_id
        )
    ):
        return HandoffStatus.HELD
    return HandoffStatus.APPLIED


def _timeline(
    events: tuple[_ScopeEvent, ...],
    position: ScopePosition,
    *,
    through: int | None = None,
) -> tuple[_Route, dict[UUID, HandoffDisposition]]:
    matching = sorted(
        (
            event
            for event in events
            if _stream(event.position) == _stream(position)
            and (through is None or event.position.ordinal <= through)
        ),
        key=lambda event: event.position.ordinal,
    )
    route = _Route()
    statuses = {}
    for _, rows in groupby(matching, key=lambda event: event.position.ordinal):
        group = tuple(rows)
        anchors = {
            (event.anchor_project, event.checkout)
            for event in group
            if event.anchor_project is not None
        }
        if route.scope is None and len(anchors) == 1:
            ((project, checkout),) = anchors
            route = _Route(Scope(project), 0, project, checkout, route.held)
        outcomes = {event.command_id: _eligible_event(event, route) for event in group}
        valid = [
            event
            for event in group
            if outcomes[event.command_id] is HandoffStatus.APPLIED
        ]
        if len(valid) > 1 or len(anchors) > 1:
            for event in valid:
                outcomes[event.command_id] = HandoffStatus.CONFLICT
            valid = []
        if valid:
            (event,) = valid
            generation = route.generation + 1
            route = _Route(
                event.scope, generation, event.anchor_project, event.checkout
            )
        blocked = tuple(
            dict.fromkeys(
                project
                for event in group
                if outcomes[event.command_id] is not HandoffStatus.APPLIED
                for project in _projects(event)
            )
        )
        if blocked:
            route = replace(route, held=blocked)
        for event in group:
            status = outcomes[event.command_id]
            statuses[event.command_id] = HandoffDisposition(
                status,
                event.affected,
                route.generation if status is HandoffStatus.APPLIED else None,
            )
    return route, statuses


def resolve_route(
    observation: NativeObservation, registry: RegistryView, scopes: ScopeView
) -> RouteDecision:
    """Resolve only the original observation authenticated by this scope view."""
    proof = next(
        (row for row in scopes._proofs if row.observation is observation), None
    )
    if (
        _ISSUED_VIEWS.get(id(scopes)) is not scopes
        or proof is None
        or scopes._registry != registry
    ):
        return RouteDecision(RouteStatus.HELD)
    ordinal = proof.position.ordinal
    for hold in scopes.holds:
        if (
            hold.state is not HoldState.RESOLVED
            and _stream(hold.position) == _stream(proof.position)
            and hold.affected.start < proof.end
            and ordinal < hold.affected.end
        ):
            return RouteDecision(RouteStatus.HELD)
    route, _ = _timeline(scopes.events, proof.position, through=ordinal)
    if proof.end > ordinal + 1:
        final, _ = _timeline(scopes.events, proof.position, through=proof.end - 1)
        if final != route:
            projects = tuple(
                dict.fromkeys(
                    item.scope.project_id
                    for item in (route, final)
                    if item.scope is not None
                )
            )
            return RouteDecision(RouteStatus.HELD, affected_projects=projects)
    if route.held:
        return RouteDecision(RouteStatus.HELD, affected_projects=route.held)
    scope = route.scope
    project = proof.anchor_project if scope is None else scope.project_id
    if project is None:
        return RouteDecision(RouteStatus.UNASSIGNED)
    if (
        scope is not None
        and proof.checkout not in (None, route.checkout)
        and proof.anchor_project != project
    ):
        return RouteDecision(RouteStatus.HELD, affected_projects=(project,))
    if proof.anchor_project not in (None, project) and (
        route.checkout != proof.checkout or route.anchor_project != proof.anchor_project
    ):
        return RouteDecision(
            RouteStatus.HELD, affected_projects=(project, proof.anchor_project)
        )
    if project not in proof.eligible_projects:
        return RouteDecision(RouteStatus.HELD, affected_projects=(project,))
    explicit = scope if scope is not None and scope.item is not None else None
    return RouteDecision(RouteStatus.ROUTED, project, explicit, route.generation)


class ScopeState:
    """Verified scope custody under the monitor's existing coordinator."""

    def __init__(
        self,
        registry: Registry,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        grok_reader: GrokAdapter | None = None,
    ):
        self.registry = registry
        self._clock = clock
        self._grok_reader = grok_reader
        self._operators: dict[UUID, ScopeAuthority] = {}
        self._authorized: dict[UUID, tuple[str, ScopeAuthority]] = {}
        self._batches: WeakValueDictionary[int, VerifiedScopeBatch] = (
            WeakValueDictionary()
        )
        self._boundaries: WeakValueDictionary[int, VerifiedBoundary] = (
            WeakValueDictionary()
        )

    def _snapshot(self, *, confirm: bool = False) -> _ScopeSnapshot:
        if not _path_exists(self.registry.root):
            return _ScopeSnapshot()
        with _pin_directory(self.registry.root) as root:
            data = _read_state(root, _FILE, _MAX_SNAPSHOT)
            if data is not None and confirm:
                os.fsync(root.fd)
                root.check()
        if data is None:
            return _ScopeSnapshot()
        if len(data) > _MAX_SNAPSHOT:
            raise LedgerError("Private scope state exceeds its limit")
        try:
            state = _decode(data, _ScopeSnapshot)
        except ValueError:
            raise LedgerError("Invalid private scope state") from None
        if (
            state.format != _FORMAT
            or len({entry.command_id for entry in state.events}) != len(state.events)
            or len({entry.command_id for entry in state.holds}) != len(state.holds)
            or len({entry.command_id for entry in state.resolutions})
            != len(state.resolutions)
            or any(event.reported is None for event in state.events)
        ):
            raise LedgerError("Invalid private scope custody")
        return state

    def _save(self, state: _ScopeSnapshot) -> None:
        lease = self.registry.lease
        data = _encode(state, _ScopeSnapshot).encode()
        if len(data) > _MAX_SNAPSHOT:
            raise LedgerError("Private scope state exceeds its limit")
        with _pin_directory(self.registry.root) as root:
            lease.check()
            _publish(root, _FILE, data, replace_pending=True)
            lease.check()

    def _ledger(self, project_id: UUID) -> Ledger:
        try:
            project = _project(self.registry.view(), project_id)
        except ValueError:
            raise LedgerError("Scope project is not registered") from None
        if not _pinned(project.state):
            raise LedgerError("Scope project state identity changed")
        ledger = Ledger.open(Path(project.state.path), project_id)
        if project.adopted_key_id not in (None, ledger.identity.key_id):
            raise LedgerError("Scope project ledger identity changed")
        return ledger

    def operator(self, project_id: UUID) -> ScopeAuthority:
        """Issue local operator authority after opening the pinned project."""
        self.registry.lease
        ledger = self._ledger(project_id)
        authority = self._operators.get(project_id)
        if authority is None or authority.key_id != ledger.identity.key_id:
            authority = ScopeAuthority(project_id, ledger.identity.key_id)
            self._operators[project_id] = authority
        return authority

    def _require_authority(
        self, command: ScopeCommand, authority: ScopeAuthority
    ) -> None:
        project = _project_id(command)
        if (
            type(authority) is not ScopeAuthority
            or self._operators.get(project) is not authority
            or self._ledger(project).identity.key_id != authority.key_id
        ):
            raise LedgerError("Scope proposal authority does not match its project")

    def authorize(self, command: ScopeCommand, authority: ScopeAuthority) -> None:
        """Bind one canonical proposal before its native proof can be applied."""
        self.registry.lease
        if type(command) not in (Mark, Handoff, Disposition):
            raise LedgerError("Invalid scope proposal")
        self._require_authority(command, authority)
        destination = _scope(command)
        ledger = self._ledger(destination.project_id)
        evidence = self.registry.source_evidence()
        evidence.validate_source_ref(command.receipt_ref)
        for ref in (
            destination.participant_ref,
            destination.attempt_ref,
            destination.review_ref,
        ):
            if ref is not None:
                try:
                    evidence.validate_source_ref(ref)
                except LedgerError:
                    ledger.validate_source_ref(ref)
        if isinstance(command, Handoff):
            if command.current_project == destination.project_id:
                raise ConflictError("A handoff requires a different project")
            if command.retained_checkout is not None:
                evidence.validate_source_ref(command.retained_checkout)
        digest = _digest(command)
        current = self._authorized.get(command.command_id)
        if current is not None and current != (digest, authority):
            raise ConflictError("Scope command ID has conflicting proposal bytes")
        if current is None and len(self._authorized) >= _MAX_AUTHORIZATIONS:
            raise LedgerError("Too many pending scope authorizations")
        self._authorized[command.command_id] = digest, authority

    def _read_grok(
        self,
        source_id: UUID,
        locator: SourceLocator,
    ) -> tuple[SourceLocator, AdapterBatch]:
        if type(self._grok_reader) is not GrokAdapter:
            raise LedgerError("Grok scope reader is unavailable")
        approved = _source(self.registry.view(), source_id)
        _check_capture_root(approved.directory)
        source = locator._source
        evidence = self.registry.source_evidence()
        if (
            type(source) is not _GrokSource
            or source.root.path != Path(approved.directory.path)
            or source.root.evidence != evidence
            or not source.path.is_relative_to(source.root.path)
        ):
            raise LedgerError("Grok scope locator is outside the approved source")
        matches = tuple(
            entry
            for entry in self._grok_reader.discover(source.root)
            if entry.stream_ref == locator.stream_ref
        )
        if len(matches) != 1:
            raise LedgerError("Expected one approved Grok scope stream")
        (current,) = matches
        pinned = current._source
        origin = pinned.origin
        identity = pinned.snapshot.identity[len(source.root.path.parts) - 1][:2]
        declared = approved.approval
        if (
            pinned.path != source.path
            or identity != approved.directory.identity
            or origin is None
            or (declared.provider, declared.surface)
            != ("grok", NativeSurface.GROK_BUILD_MACOS)
            or (
                origin.system,
                origin.architecture,
                origin.version,
                origin.format_version,
            )
            != (
                declared.platform,
                declared.architecture,
                declared.client_version,
                declared.format_version,
            )
        ):
            raise LedgerError("Grok scope source tuple changed")
        result = self._grok_reader.read_delta(current, None)
        _check_capture_root(approved.directory)
        if (
            result.cursor is None
            or type(result.cursor.checkpoint) is not GrokCheckpoint
        ):
            raise LedgerError("Grok scope source proof is unavailable")
        return current, result

    def _anchor(self, view: RegistryView, checkout: SourceRef | None) -> UUID | None:
        if checkout is None:
            return None
        evidence = self.registry.source_evidence()
        evidence.validate_source_ref(checkout)
        projects = {
            project.project_id
            for project in view.projects
            for anchor in project.anchors
            if _pinned(anchor)
            and checkout_anchor_reference(evidence, Path(anchor.path)) == checkout
        }
        if len(projects) > 1:
            raise ConflictError("Native checkout has ambiguous project ownership")
        return next(iter(projects), None)

    def _eligible(
        self, admitted: frozenset[UUID], position: ScopePosition, end: int
    ) -> frozenset[UUID]:
        if position.surface is NativeSurface.GROK_BUILD_MACOS:
            return frozenset()
        eligible = set()
        for project_id in admitted:
            bound = self.registry.capture_read_limit(
                project_id, position.source_id, position.stream_ref
            )
            if (
                bound is None or end <= bound.ordinal
            ) and self.registry.span_disposition(
                project_id,
                position.source_id,
                position.stream_ref,
                position.ordinal,
                end,
            ) is Eligibility.ELIGIBLE:
                eligible.add(project_id)
        return frozenset(eligible)

    def _admitted_readers(
        self, view: RegistryView, source_id: UUID, locator: SourceLocator
    ) -> frozenset[UUID]:
        latest = {
            epoch.project_id: epoch
            for epoch in view.epochs
            if epoch.source_id == source_id and epoch.stream_ref == locator.stream_ref
        }
        bounds = {
            project_id: self.registry.capture_read_limit(
                project_id, source_id, locator.stream_ref
            )
            for project_id in latest
        }
        if not any(bound is None for bound in bounds.values()):
            raise LedgerError("Native scope source has no admitted unbounded read")
        admitted = set()
        for project_id, epoch in latest.items():
            bound = bounds[project_id]
            if bound is not None and bound.cursor is None:
                continue
            prior = (
                (epoch.position or epoch.observed.checkpoint.cursor)
                if bound is None
                else bound.cursor
            )
            try:
                _capture_position(locator._source, prior, fixed=prior)
            except (_CaptureDiscontinuity, OSError, ValueError):
                continue
            admitted.add(project_id)
        if not any(bounds[project_id] is None for project_id in admitted):
            raise LedgerError("Native scope source lost its enrolled physical prefix")
        return frozenset(admitted)

    def _scope_enrollments(
        self, source_id: UUID, stream_ref: SourceRef
    ) -> tuple[SourceBoundary, ...]:
        events = self._snapshot().events
        selected = []
        for event in events:
            if (
                event.position.source_id != source_id
                or event.position.stream_ref != stream_ref
                or event.before_generation is not None
                or event.anchor_project is not None
                or event.native_boundary is None
            ):
                continue
            _, dispositions = _timeline(events, event.position)
            if dispositions[event.command_id].status is HandoffStatus.APPLIED:
                selected.append(event.native_boundary)
        return tuple(selected)

    def read_source(
        self,
        source_id: UUID,
        locator: SourceLocator,
        *,
        cursor: StreamCursor | None = None,
    ) -> VerifiedScopeBatch:
        """Read one exact pinned native stream and retain provenance for its results."""
        self.registry.lease
        view = self.registry.view()
        revision_witnesses: list[tuple[NativeObservation, _NativeRevisionWitness]] = []
        if type(locator._source) is CandidateSource:
            if not any(
                self.registry.capture_read_limit(
                    project.project_id, source_id, locator.stream_ref
                )
                is None
                for project in view.projects
            ):
                raise LedgerError("Native scope source has no admitted unbounded read")
            approved, current = self.registry._approved_candidate(
                view, source_id, locator
            )
            admitted = self._admitted_readers(view, source_id, current)
            if cursor is not None:
                if not isinstance(checkpoint := cursor.checkpoint, SourceCheckpoint):
                    raise LedgerError("Expected a native scope checkpoint")
                try:
                    _capture_position(
                        current._source, checkpoint.cursor, fixed=checkpoint.cursor
                    )
                except (_CaptureDiscontinuity, OSError, ValueError):
                    raise LedgerError("Native scope checkpoint changed") from None
            try:
                physical = _capture_position(current._source, None)
            except (_CaptureDiscontinuity, OSError, ValueError):
                raise LedgerError(
                    "Native scope physical prefix is unavailable"
                ) from None
            self.registry._verify_capture_tuple(approved, physical)
            native_cursor = physical.cursor
            # A caller cursor cannot hide the first occurrence of a queued receipt.
            batch = ProviderAdapter().read_delta(
                current,
                None,
                _scope_boundaries=self._scope_enrollments(
                    source_id, current.stream_ref
                ),
                _capture_limit=native_cursor,
                _revision_witnesses=revision_witnesses,
            )
            _check_capture_root(approved.directory)
            surface = NativeSurface(approved.approval.surface)
        else:
            current, batch = self._read_grok(source_id, locator)
            surface = NativeSurface.GROK_BUILD_MACOS
            admitted = frozenset()
            native_cursor = None

        proofs = []
        evidence = self.registry.source_evidence()
        for observation in batch.observations:
            usage = observation.usage
            native = (
                usage.boundary
                if isinstance(usage, UsageObservation)
                else observation.position
            )
            if native is None or native.stream_ref != locator.stream_ref:
                continue
            if observation.native_surface is not surface:
                raise LedgerError("Scope observation surface changed")
            for ref in (observation.key, native.session_ref, native.stream_ref):
                evidence.validate_source_ref(ref)
            position = ScopePosition(
                source_id,
                surface,
                native.session_ref,
                native.stream_ref,
                native.ordinal,
            )
            end = (
                position.ordinal + 1
                if observation.span_end is None
                else observation.span_end
            )
            if end <= position.ordinal:
                raise LedgerError(
                    "Verified scope observation has an invalid native span"
                )
            checkout = observation.project_context
            proofs.append(
                _ObservationProof(
                    observation,
                    position,
                    end,
                    checkout,
                    self._anchor(view, checkout),
                    self._eligible(admitted, position, end),
                )
            )
        verified = VerifiedScopeBatch(
            source_id=source_id,
            surface=surface,
            observations=batch.observations,
            boundaries=batch.boundaries,
            diagnostics=batch.diagnostics,
            cursor=batch.cursor,
            _proofs=tuple(proofs),
            _admitted=admitted,
            _locator=current,
            _native_cursor=native_cursor,
            _registry=view,
            _revision_witnesses=tuple(revision_witnesses),
        )
        self._batches[id(verified)] = verified
        return verified

    def verified_revision(
        self, batch: VerifiedScopeBatch, observation: NativeObservation
    ) -> _VerifiedRevision | None:
        """Prove one later Claude change while retaining its original route."""
        view = self.view(batch, _confirm_publication=True)
        witness = next(
            (
                entry
                for candidate, entry in batch._revision_witnesses
                if candidate is observation
            ),
            None,
        )
        if witness is None:
            return None
        proofs = {id(item.observation): item for item in batch._proofs}
        original = proofs.get(id(observation))
        prior = proofs.get(id(witness.predecessor))
        registry = view._registry
        cursor = batch.cursor
        if (
            original is None
            or prior is None
            or original.position != prior.position
            or original.end != prior.end
            or registry is None
            or cursor is None
            or type(cursor.checkpoint) is not SourceCheckpoint
            or not original.position.ordinal
            <= witness.predecessor_ordinal
            < witness.later_ordinal
            <= cursor.checkpoint.provider.ordinal
        ):
            return None
        usage = observation.usage
        before = witness.predecessor.usage
        if (
            type(usage) is not UsageObservation
            or type(before) is not UsageObservation
            or usage.boundary != before.boundary
            or usage.observed_at != before.observed_at
            or observation.time_basis is not witness.predecessor.time_basis
            or observation.key != witness.predecessor.key
        ):
            return None

        evidence = self.registry.source_evidence()
        source = batch._locator._source
        if (
            type(source) is not CandidateSource
            or type(source._ledger) is not _ServiceEvidence
            or source._ledger.key_id != evidence.key_id
        ):
            raise LedgerError("Claude revision source key changed")
        evidence.validate_source_ref(witness.prefix_ref)
        if (
            _claude_revision_material(evidence, witness.predecessor)
            != witness.predecessor_material
            or _claude_revision_material(evidence, observation)
            != witness.successor_material
        ):
            raise LedgerError("Claude revision material changed after the native read")

        route = resolve_route(observation, registry, view)
        if (
            route.status is not RouteStatus.ROUTED
            or route.project_id is None
            or route != resolve_route(witness.predecessor, registry, view)
            or not self._revision_capture_chain(
                batch, observation, witness, original.position, route.project_id
            )
        ):
            return None
        later = replace(original.position, ordinal=witness.later_ordinal)
        if self.view(batch, _confirm_publication=True) != view:
            raise LedgerError("Claude revision scope changed during proof")
        return _VerifiedRevision(
            observation, witness, route, original.position, later, batch, self.registry
        )

    def _revision_capture_chain(
        self,
        batch: VerifiedScopeBatch,
        observation: NativeObservation,
        witness: _NativeRevisionWitness,
        original: ScopePosition,
        owner: UUID,
    ) -> bool:
        edges = {id(candidate): edge for candidate, edge in batch._revision_witnesses}
        while True:
            before, after = witness.predecessor.usage, observation.usage
            if (
                type(before) is not UsageObservation
                or type(after) is not UsageObservation
                or not original.ordinal
                <= witness.predecessor_ordinal
                < witness.later_ordinal
            ):
                return False
            start = (
                witness.predecessor_ordinal
                if before.tokens != after.tokens
                else witness.later_ordinal
            )
            span = replace(original, ordinal=start)
            if owner not in self._eligible(
                batch._admitted, span, witness.later_ordinal + 1
            ):
                return False
            contributors = witness.terminal_contributor_spans
            if witness.kind is not _ClaudeRevisionKind.ASSISTANT and not contributors:
                return False
            if any(
                not 0 <= start < end <= witness.later_ordinal
                or owner
                not in self._eligible(
                    batch._admitted, replace(original, ordinal=start), end
                )
                for start, end in contributors
            ):
                return False
            if witness.predecessor_ordinal == original.ordinal:
                return True
            # Terminal evidence can leave counters unchanged. Prove that those
            # counters themselves came through eligible native predecessor edges.
            observation = witness.predecessor
            prior = edges.get(id(observation))
            if prior is None or prior.later_ordinal != witness.predecessor_ordinal:
                return False
            witness = prior

    def _recheck_batch(self, batch: VerifiedScopeBatch) -> None:
        self.registry.lease
        if (
            self._batches.get(id(batch)) is not batch
            or batch._registry != self.registry.view()
        ):
            raise LedgerError("Scope registry or issuer changed since the native read")
        approved = _source(batch._registry, batch.source_id)
        _check_capture_root(approved.directory)
        native = batch._locator._source
        try:
            if batch._native_cursor is not None:
                _capture_position(
                    native, batch._native_cursor, fixed=batch._native_cursor
                )
            else:
                assert batch.cursor is not None
                checkpoint = batch.cursor.checkpoint
                origin = native.origin
                if (
                    origin is None
                    or self._grok_reader.verify_origin(native.path) != origin
                ):
                    raise LedgerError("Grok scope origin changed")
                data = _read_grok_file(
                    native.path, native.snapshot.identity, _MAX_NATIVE_BYTES
                )
                _validate_grok_prior(native, origin, data, checkpoint)
        except (_CaptureDiscontinuity, _GrokHeld, OSError, ValueError):
            raise LedgerError("Verified native scope source changed") from None
        _check_capture_root(approved.directory)
        for checkout, project in {
            (proof.checkout, proof.anchor_project) for proof in batch._proofs
        }:
            if self._anchor(batch._registry, checkout) != project:
                raise LedgerError("Verified scope checkout identity changed")

    def _development_proof(
        self,
        command: Mark | Handoff,
        batch: VerifiedScopeBatch,
        position: ScopePosition,
        checkout: SourceRef | None,
    ) -> bool:
        scope = _scope(command)
        binding = command.destination_binding
        if scope.phase is not WorkPhase.DEVELOPMENT:
            return True
        if (
            scope.role not in (None, ReviewRole.AUTHOR)
            or scope.review_ref is not None
            or scope.attempt_ref is None
            or binding is None
            or (
                binding.marker.project_id,
                binding.marker.item,
                binding.marker.participant_ref,
                binding.marker.attempt_ref,
            )
            != (scope.project_id, scope.item, scope.participant_ref, scope.attempt_ref)
        ):
            return False
        project = _project(batch._registry, scope.project_id)
        ledger = self._ledger(scope.project_id)
        ledger.validate_command(
            InboxCommand(binding.marker.marker_id, scope.project_id, binding)
        )
        anchors = tuple(
            Path(anchor.path)
            for anchor in project.anchors
            if _pinned(anchor)
            and checkout_anchor_reference(ledger, Path(anchor.path))
            == binding.anchor_ref
        )
        if len(anchors) != 1:
            return False
        owners = tuple(
            record
            for revision in ledger.as_of().current
            if isinstance(record := revision.record, ScopeEnrollment)
            and record.anchor_ref == binding.anchor_ref
            and record.generation is not None
        )
        latest = max((record.generation for record in owners), default=None)
        current = tuple(record for record in owners if record.generation == latest)
        if (
            latest != binding.generation
            or len(current) != 1
            or current[0].marker != binding.marker
        ):
            return False
        if isinstance(command, Handoff):
            return True
        if (
            checkout_anchor_reference(self.registry.source_evidence(), anchors[0])
            != checkout
        ):
            return False
        return self._same_legacy_stream(batch, position, ledger, current[0])

    @staticmethod
    def _same_legacy_stream(
        batch: VerifiedScopeBatch,
        position: ScopePosition,
        ledger: Ledger,
        owner: ScopeEnrollment,
    ) -> bool:
        source = batch._locator._source
        cursor = batch._native_cursor
        if (
            type(source) is not CandidateSource
            or cursor is None
            or cursor.offset == 0
            or source.session_ref != position.session_ref
            or source.stream_ref != position.stream_ref
        ):
            return False
        try:
            with _open_snapshot(source._path, identity_prefix=source._identity) as (
                stream,
                snapshot,
            ):
                digest = _hash_prefix(stream, cursor.offset)
                if (
                    _source_prefix_reference(
                        source._ledger, cursor.source_ref, cursor.offset, digest
                    )
                    != cursor.anchor_ref
                ):
                    return False
                origin = _origin(stream, cursor.offset, ledger)
                _verify_snapshot(stream, source._path, snapshot, cursor.offset, digest)
        except (LedgerError, OSError, ValueError):
            return False
        return (
            origin is not None
            and origin.provider is owner.marker.provider
            and origin.session_ref == owner.marker.session_ref
            and owner.boundary.stream_ref
            == ledger.pseudonymize(
                f"{origin.provider.value}-stream", origin.session_ref.value
            )
        )

    def verify_boundary(
        self,
        command: ScopeCommand,
        authority: ScopeAuthority,
        batch: VerifiedScopeBatch,
        target: NativeBoundary,
    ) -> VerifiedBoundary:
        self.registry.lease
        self._require_authority(command, authority)
        digest = _digest(command)
        if self._authorized.get(command.command_id) != (digest, authority):
            raise LedgerError("Scope proposal has no matching authorization")
        if self._batches.get(id(batch)) is not batch or not any(
            row is target for row in batch.boundaries
        ):
            raise LedgerError("Scope receipt is outside the verified native read")
        self._recheck_batch(batch)
        boundary = target.boundary
        evidence = self.registry.source_evidence()
        if boundary.receipt_ref != command.receipt_ref:
            raise LedgerError(
                "Native scope receipt does not match the authorized proposal"
            )
        candidates = [
            item
            for item in batch.boundaries
            if item.boundary.receipt_ref == command.receipt_ref
            and item.boundary.stream_ref == boundary.stream_ref
            and item.boundary.session_ref == boundary.session_ref
        ]
        earliest = min(item.boundary.ordinal for item in candidates)
        first = {item for item in candidates if item.boundary.ordinal == earliest}
        if len(first) != 1 or target not in first:
            raise LedgerError("Expected the first unique receipt-linked native target")
        if batch.surface is not NativeSurface.GROK_BUILD_MACOS and (
            command.receipt_ref
            != evidence.pseudonymize("scope-receipt", str(command.command_id))
        ):
            raise LedgerError("Native scope receipt is bound to another command")
        for ref in (
            boundary.session_ref,
            boundary.stream_ref,
            boundary.boundary_ref,
            boundary.receipt_ref,
        ):
            evidence.validate_source_ref(ref)
        position = ScopePosition(
            batch.source_id,
            batch.surface,
            boundary.session_ref,
            boundary.stream_ref,
            boundary.ordinal,
        )
        if (
            isinstance(command, Handoff)
            and batch.surface is NativeSurface.GROK_BUILD_MACOS
        ):
            next_turn = min(
                (
                    item.position.ordinal
                    for item in batch._proofs
                    if _stream(item.position) == _stream(position)
                    and item.position.ordinal > position.ordinal
                ),
                default=None,
            )
            if next_turn is None:
                raise LedgerError("Grok handoff requires the next verified native turn")
            position = replace(position, ordinal=next_turn)

        matching = tuple(
            item
            for item in batch._proofs
            if _stream(item.position) == _stream(position)
        )
        affected = tuple(
            item for item in matching if item.position.ordinal >= position.ordinal
        )
        if isinstance(command, Disposition):
            original = next(
                (
                    item
                    for item in self._snapshot().holds
                    if item.command_id == command.hold_id
                ),
                None,
            )
            if original is not None:
                affected = tuple(
                    item
                    for item in matching
                    if original.affected.start <= item.position.ordinal
                    and item.end <= original.affected.end
                    and command.project_id in item.eligible_projects
                )
        keys = tuple(dict.fromkeys(item.observation.key for item in affected))[
            :_MAX_HOLDS
        ]
        affected = tuple(item for item in affected if item.observation.key in keys)
        start = min(
            (item.position.ordinal for item in affected), default=position.ordinal
        )
        end = max((item.end for item in affected), default=position.ordinal + 1)
        checkout = target.project_context
        anchor = self._anchor(batch._registry, checkout)
        eligible_projects = self._eligible(
            batch._admitted, position, position.ordinal + 1
        )
        eligible = _scope(command).project_id in eligible_projects
        if isinstance(command, (Mark, Handoff)) and not self._development_proof(
            command, batch, position, checkout
        ):
            raise LedgerError(
                "Develop scope requires the current destination owner worktree"
            )
        if isinstance(command, Handoff):
            eligible = eligible and command.current_project in eligible_projects
        proof = VerifiedBoundary(
            command.command_id,
            digest,
            position,
            checkout,
            anchor,
            eligible,
            AffectedScope(start, end, keys),
            boundary if isinstance(boundary, SourceBoundary) else None,
            batch,
            authority,
        )
        self._boundaries[id(proof)] = proof
        return proof

    def _require_boundary(
        self, receipt: VerifiedBoundary, command: ScopeCommand | None = None
    ) -> None:
        self.registry.lease
        if self._boundaries.get(id(receipt)) is not receipt:
            raise LedgerError("Expected a current writer-verified native scope receipt")
        self._recheck_batch(receipt._batch)
        if (
            self._anchor(receipt._batch._registry, receipt.checkout)
            != receipt.anchor_project
            or self._ledger(receipt._authority.project_id).identity.key_id
            != receipt._authority.key_id
        ):
            raise LedgerError("Verified scope authority or checkout changed")
        if command is not None:
            self._require_authority(command, receipt._authority)
            if (
                command.command_id != receipt.command_id
                or _digest(command) != receipt.digest
            ):
                raise LedgerError("Scope receipt is bound to different command bytes")
            if isinstance(command, (Mark, Handoff)) and not self._development_proof(
                command, receipt._batch, receipt.position, receipt.checkout
            ):
                raise LedgerError("Develop handoff destination owner proof changed")

    def receipt(
        self,
        command: ScopeCommand,
        authority: ScopeAuthority,
    ) -> HandoffDisposition | ProofHold | None:
        """Return an exact committed outcome without rereading the native source."""
        self.registry.lease
        self._require_authority(command, authority)
        state = self._snapshot(confirm=True)
        digest = _digest(command)
        for item in state.events:
            if item.command_id == command.command_id:
                if item.digest != digest:
                    raise ConflictError(
                        "Scope command ID has conflicting proposal bytes"
                    )
                return item.reported
        for item in state.resolutions:
            if item.command_id == command.command_id:
                if item.digest != digest:
                    raise ConflictError("Scope disposition ID has conflicting bytes")
                return item.result
        for hold in state.holds:
            if hold.command_id == command.command_id:
                if hold.command_digest != digest:
                    raise ConflictError("Scope hold has conflicting proposal bytes")
                return hold
        return None

    def _apply(
        self, command: Mark | Handoff, receipt: VerifiedBoundary
    ) -> HandoffDisposition:
        self._require_boundary(receipt, command)
        state = self._snapshot(confirm=True)
        event = _ScopeEvent(
            receipt.command_id,
            receipt.digest,
            _scope(command),
            receipt.position,
            receipt.checkout,
            receipt.anchor_project,
            receipt.eligible,
            receipt.affected,
            receipt.native_boundary,
            command.current_project if isinstance(command, Handoff) else None,
            command.before_generation if isinstance(command, Handoff) else None,
            command.retained_checkout if isinstance(command, Handoff) else None,
        )
        old = next(
            (row for row in state.events if row.command_id == event.command_id), None
        )
        if old is not None:
            if old != replace(event, affected=old.affected, reported=old.reported):
                raise ConflictError("Scope command ID has conflicting native proof")
            assert old.reported is not None
            self._authorized.pop(command.command_id, None)
            return old.reported
        hold = next(
            (item for item in state.holds if item.command_id == event.command_id), None
        )
        if hold is not None:
            if (hold.position, hold.command_digest) != (event.position, event.digest):
                raise ConflictError("Scope hold has conflicting command bytes")
            self._authorized.pop(command.command_id, None)
            status = (
                HandoffStatus.REJECTED
                if hold.state is HoldState.RESOLVED
                else HandoffStatus.HELD
            )
            return HandoffDisposition(status, hold.affected)
        _, result = _timeline((*state.events, event), event.position)
        outcome = result[event.command_id]
        _, previous = _timeline(state.events, event.position)
        changed = tuple(
            item.affected
            for key, item in result.items()
            if key != event.command_id and previous.get(key) != item
        )
        if changed:
            affected = (outcome.affected, *changed)
            keys = tuple(
                dict.fromkeys(key for item in affected for key in item.observation_keys)
            )[:_MAX_HOLDS]
            outcome = replace(
                outcome,
                affected=AffectedScope(
                    min(item.start for item in affected),
                    max(item.end for item in affected),
                    keys,
                ),
            )
        self._save(
            replace(state, events=(*state.events, replace(event, reported=outcome)))
        )
        self._authorized.pop(command.command_id, None)
        return outcome

    def apply_mark(
        self, command: Mark, receipt: VerifiedBoundary
    ) -> HandoffDisposition:
        return self._apply(command, receipt)

    def apply_handoff(
        self, command: Handoff, receipt: VerifiedBoundary
    ) -> HandoffDisposition:
        return self._apply(command, receipt)

    def _now(self) -> datetime:
        value = self._clock()
        if type(value) is not datetime or value.utcoffset() is None:
            raise ValueError("Expected an aware scope clock")
        return value.astimezone(UTC)

    def hold(self, receipt: VerifiedBoundary) -> ProofHold:
        self._require_boundary(receipt)
        state = self._snapshot(confirm=True)
        prior = next(
            (hold for hold in state.holds if hold.command_id == receipt.command_id),
            None,
        )
        if prior is not None:
            if (prior.position, prior.command_digest) != (
                receipt.position,
                receipt.digest,
            ):
                raise ConflictError("Scope hold has conflicting native proof")
            return prior
        _, dispositions = _timeline(state.events, receipt.position)
        previous = dispositions.get(receipt.command_id)
        if previous is not None and previous.status is HandoffStatus.APPLIED:
            raise LedgerError(
                "An applied scope requires independent evidence to be held"
            )
        now = self._now()
        now = max(now, max((hold.first_seen for hold in state.holds), default=now))
        unresolved = sum(hold.state is HoldState.HELD for hold in state.holds)
        hold = ProofHold(
            receipt.command_id,
            receipt.digest,
            receipt._authority.project_id,
            receipt.position,
            receipt.affected,
            now,
            now + _HOLD_TIME,
            HoldState.GAP if unresolved >= _MAX_HOLDS else HoldState.HELD,
        )
        self._save(replace(state, holds=(*state.holds, hold)))
        self._authorized.pop(receipt.command_id, None)
        return hold

    def expire(self) -> tuple[ProofHold, ...]:
        self.registry.lease
        state = self._snapshot(confirm=True)
        now = self._now()
        due = tuple(
            replace(item, state=HoldState.GAP)
            for item in state.holds
            if item.state is HoldState.HELD and item.expires_at <= now
        )
        if due:
            changed = {item.command_id: item for item in due}
            self._save(
                replace(
                    state,
                    holds=tuple(
                        changed.get(item.command_id, item) for item in state.holds
                    ),
                )
            )
        return due

    def dispose(self, command: Disposition, receipt: VerifiedBoundary) -> ProofHold:
        self._require_boundary(receipt, command)
        state = self._snapshot(confirm=True)
        existing = next(
            (
                item
                for item in state.resolutions
                if item.command_id == command.command_id
            ),
            None,
        )
        original = next(
            (item for item in state.holds if item.command_id == command.hold_id), None
        )
        if original is None:
            raise LedgerError("Scope hold is unavailable")
        if existing is not None:
            if (
                existing.digest != receipt.digest
                or existing.result.command_id != original.command_id
            ):
                raise ConflictError("Scope disposition ID has conflicting bytes")
            return existing.result
        if (
            command.project_id != original.project_id
            or original.state is not HoldState.HELD
            or not receipt.eligible
            or _stream(receipt.position) != _stream(original.position)
            or not original.affected.start
            <= receipt.position.ordinal
            < original.affected.end
            or receipt.affected.start > original.affected.start
            or receipt.affected.end < original.affected.end
            or not set(original.affected.observation_keys)
            <= set(receipt.affected.observation_keys)
            or receipt.command_id == original.command_id
        ):
            raise LedgerError(
                "Independent scope disposition proof does not cover the owned hold"
            )
        hold = replace(original, state=HoldState.GAP)
        if (
            command.release_previous
            and original.state is HoldState.HELD
            and self._now() < original.expires_at
        ):
            prior, _ = _timeline(
                state.events, original.position, through=original.affected.start - 1
            )
            through, _ = _timeline(
                state.events, original.position, through=original.affected.end - 1
            )
            if (
                prior.scope is not None
                and prior.scope.project_id == command.project_id
                and prior == through
                and prior.checkout is not None
                and prior.checkout == receipt.checkout
                and not prior.held
            ):
                hold = replace(original, state=HoldState.RESOLVED)
        self._save(
            replace(
                state,
                holds=tuple(
                    hold if item.command_id == hold.command_id else item
                    for item in state.holds
                ),
                resolutions=(
                    *state.resolutions,
                    _Resolution(command.command_id, receipt.digest, hold),
                ),
            )
        )
        self._authorized.pop(command.command_id, None)
        return hold

    def view(
        self, *batches: VerifiedScopeBatch, _confirm_publication: bool = False
    ) -> ScopeView:
        state = self._snapshot(confirm=_confirm_publication)
        registry = None
        if batches:
            for batch in batches:
                self._recheck_batch(batch)
            registry = self.registry.view(_confirm_publication=_confirm_publication)
        view = ScopeView(
            state.events,
            state.holds,
            tuple(proof for batch in batches for proof in batch._proofs),
            registry,
        )
        _ISSUED_VIEWS[id(view)] = view
        return view
