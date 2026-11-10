"""Private monitor project, installation and native capture authority."""

import hmac
import os
import platform
import re
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

from .ledger import (
    STORE_NAME,
    ConflictError,
    Ledger,
    LedgerError,
    _check_acl,
    _control_root,
    _ensure_private_directory,
    _lease,
    _path_exists,
    _pin_directory,
    _PinnedPath,
    _private,
    validate_private_path,
)
from .scopes import _publish, _read_private
from .sources.adapter import ProviderAdapter, SourceLocator, StreamCursor
from .sources.scan import CandidateSource
from .types import (
    Eligibility,
    LedgerView,
    SourceRef,
    _decode,
    _encode,
    _nonnegative,
    _positive,
)

if TYPE_CHECKING:
    from .monitor_control import ControlInbox

_STATE_FILE = "registry-v1.json"
_COORDINATOR_FILE = "coordinator.lock"
_SOURCE_KEY_FILE = "source-key-v1"
_MAX_REGISTRY_BYTES = 1024 * 1024
_PROVIDER_NAMES = {"codex", "claude", "grok"}
_COMMAND_FORMAT = "aitm.usage.monitor-control/v1"
_REGISTRY_FORMAT = "aitm.usage.monitor-registry/v1"


class ProjectAdopted(LedgerError):
    """Legacy mutation is unavailable for a pinned adopted project."""


def default_monitor_root() -> Path:
    return _control_root() / "monitor"


@dataclass(frozen=True, slots=True)
class ProjectRegistrationRequest:
    project_id: UUID
    state_dir: str
    display_name: str
    remote: str | None = None
    anchors: tuple[str, ...] = ()
    default_driver: str | None = None


@dataclass(frozen=True, slots=True)
class SourceApprovalRequest:
    source_id: UUID
    provider: str
    surface: str
    platform: str
    architecture: str
    client_version: str
    format_version: int
    root: str


@dataclass(frozen=True, slots=True)
class AnchorRequest:
    project_id: UUID
    anchor: str


@dataclass(frozen=True, slots=True)
class CaptureChange:
    project_id: UUID
    source_id: UUID
    enabled: bool


type ControlPayload = (
    ProjectRegistrationRequest | SourceApprovalRequest | AnchorRequest | CaptureChange
)


@dataclass(frozen=True, slots=True)
class ControlCommand:
    command_id: UUID
    payload: (
        ProjectRegistrationRequest
        | SourceApprovalRequest
        | AnchorRequest
        | CaptureChange
    )
    format: str = _COMMAND_FORMAT

    def __post_init__(self) -> None:
        if self.format != _COMMAND_FORMAT:
            raise ValueError("Unsupported monitor control command")

    @property
    def payload_digest(self) -> str:
        return sha256(_encode(self, ControlCommand).encode("utf-8")).hexdigest()


class ControlStatus(StrEnum):
    QUEUED = "queued"
    APPLIED = "applied"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ControlReceipt:
    command_id: UUID
    status: ControlStatus
    payload_digest: str
    reason: str | None = None

    def __post_init__(self) -> None:
        if type(self.payload_digest) is not str or not re.fullmatch(
            r"[a-f0-9]{64}", self.payload_digest
        ):
            raise ValueError("Invalid command digest")


@dataclass(frozen=True, slots=True)
class _PhysicalDirectory:
    path: str = field(repr=False)
    identity: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.identity) != 2:
            raise ValueError("Invalid directory identity")
        for value in self.identity:
            _nonnegative(value)


@dataclass(frozen=True, slots=True)
class RegisteredProject:
    project_id: UUID
    state: _PhysicalDirectory
    display_name: str
    remote: str | None
    anchors: tuple[_PhysicalDirectory, ...]
    default_driver: str | None
    adopted_key_id: str | None = None


@dataclass(frozen=True, slots=True)
class ApprovedSource:
    approval: SourceApprovalRequest = field(repr=False)
    directory: _PhysicalDirectory

    @property
    def source_id(self) -> UUID:
        return self.approval.source_id


@dataclass(frozen=True, slots=True)
class CaptureEpoch:
    project_id: UUID
    source_id: UUID
    stream_ref: SourceRef
    ordinal: int
    boundary_ref: SourceRef
    generation: int
    enabled: bool

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)
        _positive(self.generation)


@dataclass(frozen=True, slots=True)
class VerifiedBoundary:
    source_id: UUID
    stream_ref: SourceRef
    ordinal: int
    boundary_ref: SourceRef


@dataclass(frozen=True, slots=True)
class RegistryView:
    projects: tuple[RegisteredProject, ...] = ()
    sources: tuple[ApprovedSource, ...] = ()
    permissions: tuple[CaptureChange, ...] = ()
    epochs: tuple[CaptureEpoch, ...] = ()
    receipts: tuple[ControlReceipt, ...] = ()
    source_key_id: str | None = None
    format: str = _REGISTRY_FORMAT

    def __post_init__(self) -> None:
        if self.format != _REGISTRY_FORMAT:
            raise ValueError("Unsupported monitor registry version")
        if self.source_key_id is not None and not re.fullmatch(
            r"[a-f0-9]{64}", self.source_key_id
        ):
            raise ValueError("Invalid private source key identity")


@dataclass(frozen=True, slots=True)
class _ServiceEvidence:
    """Stable source-only references independent of destination project keys."""

    key: bytes = field(repr=False)

    @property
    def key_id(self) -> str:
        return sha256(self.key).hexdigest()

    def as_of(self) -> LedgerView:
        namespace = UUID(
            bytes=hmac.digest(self.key, b"monitor-source-namespace/v1", "sha256")[:16]
        )
        return LedgerView(namespace, 0, (), ())

    def _tag(self, digest: str) -> str:
        return hmac.digest(
            self.key, b"monitor-source-proof/v1\0" + bytes.fromhex(digest), "sha256"
        ).hex()

    def pseudonymize(self, namespace: str, raw_reference: str) -> SourceRef:
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", namespace) or not raw_reference:
            raise ValueError("Expected a monitor source namespace and identifier")
        message = f"monitor-source-ref/v1\0{namespace}\0{raw_reference}".encode()
        digest = hmac.digest(self.key, message, "sha256").hex()
        return SourceRef(f"hmac-sha256:{digest}:{self._tag(digest)}")

    def validate_source_ref(self, reference: SourceRef) -> None:
        if type(reference) is not SourceRef:
            raise LedgerError("Unverified monitor source reference")
        _, digest, tag = reference.value.split(":")
        if not hmac.compare_digest(tag, self._tag(digest)):
            raise LedgerError("Unverified monitor source reference")


class _AwaitBoundary(Exception):
    pass


type _BoundaryVerifier = Callable[[CaptureChange], Iterable[VerifiedBoundary]]


def _identity(path: Path) -> tuple[int, int]:
    info = path.stat()
    return info.st_dev, info.st_ino


def _directory(raw: str, *, private: bool = False) -> _PhysicalDirectory:
    path = Path(raw)
    if not path.is_absolute() or ".." in path.parts or "\0" in raw:
        raise ValueError("Expected an absolute directory path")
    if private:
        validate_private_path(path, directory=True)
    path = path.resolve(strict=True)
    if not path.is_dir():
        raise ValueError("Expected a physical directory")
    if private:
        validate_private_path(path, directory=True)
    return _PhysicalDirectory(str(path), _identity(path))


def _pinned(directory: _PhysicalDirectory) -> bool:
    try:
        return _directory(directory.path) == directory
    except (OSError, ValueError):
        return False


def _ancestry(directory: _PhysicalDirectory) -> set[tuple[int, ...]]:
    if not _pinned(directory):
        raise LedgerError("Registered directory identity changed")
    return {directory.identity, *map(_identity, Path(directory.path).parents)}


def _separate_anchors(
    projects: tuple[RegisteredProject, ...],
    project_id: UUID,
    anchors: tuple[_PhysicalDirectory, ...],
) -> None:
    others = tuple(
        anchor
        for project in projects
        if project.project_id != project_id
        for anchor in project.anchors
    )
    for anchor in anchors:
        ancestry = _ancestry(anchor)
        for existing in others:
            if existing.identity in ancestry or anchor.identity in _ancestry(existing):
                raise ConflictError("Project checkout anchors overlap")


def _project(view: RegistryView, project_id: UUID) -> RegisteredProject:
    for project in view.projects:
        if project.project_id == project_id:
            return project
    raise ValueError("Project is not registered")


def _source(view: RegistryView, source_id: UUID) -> ApprovedSource:
    for source in view.sources:
        if source.source_id == source_id:
            return source
    raise ValueError("Source installation is not approved")


def _edge(row: CaptureChange | CaptureEpoch) -> tuple[UUID, UUID]:
    return row.project_id, row.source_id


def _permission(view: RegistryView, change: CaptureChange) -> RegistryView:
    if change in view.permissions:
        return view
    remaining = tuple(item for item in view.permissions if _edge(item) != _edge(change))
    return replace(view, permissions=(*remaining, change))


def _command_outcome(view: RegistryView, command_id: UUID) -> ControlReceipt | None:
    return next((item for item in view.receipts if item.command_id == command_id), None)


def _read_state(root: _PinnedPath) -> bytes | None:
    for _ in range(3):
        try:
            named = os.stat(_STATE_FILE, dir_fd=root.fd, follow_symlinks=False)
            _private(named)
            fd = os.open(
                _STATE_FILE,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=root.fd,
            )
        except FileNotFoundError:
            root.check()
            return None
        except OSError:
            raise LedgerError("Private monitor registry is unavailable") from None
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(fd)
            if opened.st_nlink == 0:
                # Atomic replacement can unlink a valid, already opened snapshot.
                if not os.path.samestat(named, opened):
                    continue
                if (named.st_mode, named.st_uid) != (opened.st_mode, opened.st_uid):
                    raise LedgerError("Private monitor registry identity changed")
            else:
                _private(opened)
            _check_acl(fd)
            data = stream.read(_MAX_REGISTRY_BYTES + 1)
        root.check()
        return data
    raise LedgerError("Private monitor registry changed during read")


class Registry:
    """Committed read snapshots and writes under one private coordinator lease."""

    def __init__(self, root: Path, _writer: _PinnedPath | None = None):
        self.root = root.absolute()
        self._writer = _writer
        self._verified: dict[int, VerifiedBoundary] = {}

    @contextmanager
    def writer(self) -> Iterator["Registry"]:
        _ensure_private_directory(self.root)
        with _lease(self.root / _COORDINATOR_FILE, create=True) as lease:
            yield Registry(self.root, lease)

    @property
    def lease(self) -> _PinnedPath:
        if self._writer is None:
            raise LedgerError("Monitor coordinator lease is required")
        self._writer.check()
        return self._writer

    def view(self, *, _confirm_publication: bool = False) -> RegistryView:
        if not _path_exists(self.root):
            return RegistryView()
        with _pin_directory(self.root) as root:
            data = _read_state(root)
            if data is not None and _confirm_publication:
                # A previous atomic replacement may have failed its directory sync.
                os.fsync(root.fd)
                root.check()
        if data is None:
            return RegistryView()
        if len(data) > _MAX_REGISTRY_BYTES:
            raise LedgerError("Private monitor registry is too large")
        try:
            state = _decode(data, RegistryView)
        except ValueError:
            raise LedgerError("Invalid private monitor registry") from None
        if (
            len({item.project_id for item in state.projects}) != len(state.projects)
            or len({item.source_id for item in state.sources}) != len(state.sources)
            or len({_edge(item) for item in state.permissions})
            != len(state.permissions)
            or len({item.command_id for item in state.receipts}) != len(state.receipts)
            or any(item.status is ControlStatus.QUEUED for item in state.receipts)
        ):
            raise LedgerError("Duplicate private monitor registry identity")
        return state

    def _save(self, view: RegistryView) -> None:
        lease = self.lease
        data = _encode(view, RegistryView).encode("utf-8")
        if len(data) > _MAX_REGISTRY_BYTES:
            raise LedgerError("Private monitor registry is too large")
        with _pin_directory(self.root) as root:
            lease.check()
            _publish(root, _STATE_FILE, data, replace_pending=True)
            lease.check()

    def command_status(self, command_id: UUID) -> ControlReceipt | None:
        return _command_outcome(self.view(_confirm_publication=True), command_id)

    def source_evidence(self) -> _ServiceEvidence:
        """Read or explicitly initialize the coordinator's source-only key."""
        self.lease
        state = self.view()
        with _pin_directory(self.root) as root:
            key = _read_private(root, _SOURCE_KEY_FILE)
            if key is None and state.source_key_id is None:
                if not _publish(root, _SOURCE_KEY_FILE, os.urandom(32)):
                    raise LedgerError("Monitor source key already exists")
                key = _read_private(root, _SOURCE_KEY_FILE)
        if key is None or len(key) != 32:
            raise LedgerError("Monitor source key is unavailable")
        evidence = _ServiceEvidence(key)
        if state.source_key_id is None:
            self._save(replace(state, source_key_id=evidence.key_id))
        elif state.source_key_id != evidence.key_id:
            raise LedgerError("Monitor source key changed")
        return evidence

    def _register(
        self, view: RegistryView, request: ProjectRegistrationRequest
    ) -> tuple[RegistryView, RegisteredProject]:
        _encode(request, ProjectRegistrationRequest)
        if not 0 < len(request.display_name) <= 256:
            raise ValueError("Invalid project display name")
        if (
            request.default_driver is not None
            and request.default_driver not in _PROVIDER_NAMES
        ):
            raise ValueError("Invalid default provider")
        state = _directory(request.state_dir, private=True)
        state_path = Path(state.path)
        if state_path.is_relative_to(self.root) or self.root.is_relative_to(state_path):
            raise ValueError("Monitor registry must be separate from project state")
        existing = next(
            (p for p in view.projects if p.project_id == request.project_id), None
        )
        if existing is not None and existing.state != state:
            raise ConflictError("Project state identity changed")
        if _path_exists(state_path / STORE_NAME):
            ledger = Ledger.open(state_path, request.project_id)
            if (
                existing is not None
                and existing.adopted_key_id is not None
                and ledger.identity.key_id != existing.adopted_key_id
            ):
                raise ConflictError("Adopted project key changed")
        if any(
            p.state.identity == state.identity and p.project_id != request.project_id
            for p in view.projects
        ):
            raise ConflictError("Project state is already registered")
        earlier = existing.anchors if existing is not None else ()
        anchors = {item.identity: item for item in earlier}
        for raw in request.anchors:
            item = _directory(raw)
            anchors.setdefault(item.identity, item)
        ordered = tuple(anchors.values())
        _separate_anchors(view.projects, request.project_id, ordered)
        project = RegisteredProject(
            request.project_id,
            state,
            request.display_name,
            request.remote,
            ordered,
            request.default_driver,
            None if existing is None else existing.adopted_key_id,
        )
        projects = tuple(p for p in view.projects if p.project_id != request.project_id)
        return replace(view, projects=(*projects, project)), project

    def register_project(
        self, request: ProjectRegistrationRequest
    ) -> RegisteredProject:
        self.lease
        view, project = self._register(self.view(), request)
        self._save(view)
        return project

    def _approve(
        self, view: RegistryView, request: SourceApprovalRequest
    ) -> tuple[RegistryView, ApprovedSource]:
        _encode(request, SourceApprovalRequest)
        _positive(request.format_version)
        if (
            request.provider not in _PROVIDER_NAMES
            or request.platform not in {"Darwin", "Linux"}
            or request.architecture not in {"arm64", "aarch64", "x86_64"}
            or not re.fullmatch(r"[a-z0-9-]{1,64}", request.surface)
            or not re.fullmatch(r"[A-Za-z0-9_.+-]{1,64}", request.client_version)
        ):
            raise ValueError("Invalid approved source tuple")
        root = _directory(request.root)
        approved = ApprovedSource(replace(request, root=root.path), root)
        for existing in view.sources:
            if existing.source_id == approved.source_id:
                if existing != approved:
                    raise ConflictError("Approved source identity changed")
                return view, existing
            if (
                existing.directory.identity == root.identity
                and replace(
                    existing.approval, source_id=request.source_id, root=root.path
                )
                == approved.approval
            ):
                raise ConflictError("Source installation already has an identity")
        return replace(view, sources=(*view.sources, approved)), approved

    def approve_source(self, request: SourceApprovalRequest) -> ApprovedSource:
        self.lease
        view, approved = self._approve(self.view(), request)
        self._save(view)
        return approved

    def verify_boundary(
        self,
        source_id: UUID,
        locator: SourceLocator,
        boundary_ref: SourceRef,
        cursor: StreamCursor | None = None,
    ) -> VerifiedBoundary:
        """Obtain a typed fence from the exact pinned native reader."""
        self.lease
        view = self.view()
        source = _source(view, source_id)
        candidate = locator._source
        approval = source.approval
        if (
            type(candidate) is not CandidateSource
            or not _pinned(source.directory)
            or candidate._registration.path.resolve() != Path(source.directory.path)
            or not candidate._path.is_relative_to(candidate._registration.path)
            or (platform.system(), platform.machine())
            != (approval.platform, approval.architecture)
        ):
            raise LedgerError("Source is outside the approved installation")
        evidence = candidate._ledger
        if (
            type(evidence) is not _ServiceEvidence
            or view.source_key_id != evidence.key_id
        ):
            raise LedgerError("Capture requires the monitor source namespace")
        pinned = self.source_evidence()
        if not hmac.compare_digest(pinned.key, evidence.key):
            raise LedgerError("Capture source key changed")
        evidence.validate_source_ref(boundary_ref)
        batch = ProviderAdapter().read_delta(locator, cursor)
        found = {
            item.usage.boundary
            for item in batch.observations
            if item.native_surface.value == approval.surface
            and item.usage.boundary.provider.value == approval.provider
            and item.usage.client_version.value == approval.client_version
            and item.usage.format_version == approval.format_version
            and item.usage.boundary.boundary_ref == boundary_ref
        }
        if len(found) != 1:
            raise LedgerError("Expected one verified native capture boundary")
        (boundary,) = found
        if boundary.stream_ref != locator.stream_ref:
            raise LedgerError("Native capture stream changed")
        evidence.validate_source_ref(boundary.stream_ref)
        proof = VerifiedBoundary(
            source_id,
            boundary.stream_ref,
            boundary.ordinal,
            boundary.boundary_ref,
        )
        self._verified[id(proof)] = proof
        return proof

    def _epoch(
        self, view: RegistryView, change: CaptureChange, proof: VerifiedBoundary
    ) -> tuple[RegistryView, CaptureEpoch]:
        _encode(change, CaptureChange)
        _project(view, change.project_id)
        source = _source(view, change.source_id)
        if (
            type(proof) is not VerifiedBoundary
            or self._verified.get(id(proof)) is not proof
            or proof.source_id != change.source_id
            or not _pinned(source.directory)
        ):
            raise LedgerError("Native capture boundary is unavailable")
        prior = [
            epoch
            for epoch in view.epochs
            if _edge(epoch) == _edge(change) and epoch.stream_ref == proof.stream_ref
        ]
        previous = prior[-1] if prior else None
        if previous is not None and proof.ordinal <= previous.ordinal:
            if (
                proof.ordinal == previous.ordinal
                and proof.boundary_ref == previous.boundary_ref
                and change.enabled is previous.enabled
            ):
                return view, previous
            raise ConflictError("Stale or conflicting capture boundary")
        epoch = CaptureEpoch(
            change.project_id,
            change.source_id,
            proof.stream_ref,
            proof.ordinal,
            proof.boundary_ref,
            1 if previous is None else previous.generation + 1,
            change.enabled,
        )
        return replace(view, epochs=(*view.epochs, epoch)), epoch

    def set_permission(
        self, change: CaptureChange, boundary: VerifiedBoundary
    ) -> CaptureEpoch:
        self.lease
        if type(boundary) is not VerifiedBoundary:
            raise LedgerError("Native capture boundary is unavailable")
        view = self.view()
        streams = {
            epoch.stream_ref for epoch in view.epochs if _edge(epoch) == _edge(change)
        }
        if not change.enabled and boundary.stream_ref not in streams:
            raise ConflictError("Cannot disable an unadmitted native stream")
        if streams - {boundary.stream_ref}:
            raise ConflictError("Capture change requires all native streams")
        view, epoch = self._epoch(view, change, boundary)
        self._save(_permission(view, change))
        return epoch

    def enroll_stream(
        self, project_id: UUID, source_id: UUID, boundary: VerifiedBoundary
    ) -> CaptureEpoch:
        self.lease
        if type(boundary) is not VerifiedBoundary:
            raise LedgerError("Native capture boundary is unavailable")
        change = CaptureChange(project_id, source_id, True)
        view = self.view()
        if change not in view.permissions:
            raise ConflictError("Capture is disabled for this source")
        if any(
            _edge(epoch) == _edge(change)
            and epoch.stream_ref == boundary.stream_ref
            and epoch.boundary_ref != boundary.boundary_ref
            for epoch in view.epochs
        ):
            raise ConflictError("Native stream is already enrolled")
        next_view, epoch = self._epoch(view, change, boundary)
        if next_view != view:
            self._save(next_view)
        return epoch

    def source_read_allowed(self, project_id: UUID, source_id: UUID) -> bool:
        view = self.view()
        edge = project_id, source_id
        if not any(_edge(item) == edge and item.enabled for item in view.permissions):
            return False
        return _pinned(_source(view, source_id).directory)

    def span_disposition(
        self,
        project_id: UUID,
        source_id: UUID,
        stream_ref: SourceRef,
        start: int,
        end: int,
    ) -> Eligibility:
        _nonnegative(start)
        _nonnegative(end)
        if end <= start:
            raise ValueError("Capture span must be nonempty")
        enabled = False
        for epoch in self.view().epochs:
            if (
                _edge(epoch) != (project_id, source_id)
                or epoch.stream_ref != stream_ref
                or epoch.ordinal >= end
            ):
                continue
            if epoch.ordinal <= start:
                enabled = epoch.enabled
            elif enabled is not epoch.enabled:
                return Eligibility.UNKNOWN
        return Eligibility.ELIGIBLE if enabled else Eligibility.EXCLUDED

    def _apply(
        self,
        view: RegistryView,
        payload: ControlPayload,
        verifier: _BoundaryVerifier | None,
    ) -> RegistryView:
        if isinstance(payload, ProjectRegistrationRequest):
            return self._register(view, payload)[0]
        if isinstance(payload, SourceApprovalRequest):
            return self._approve(view, payload)[0]
        if isinstance(payload, AnchorRequest):
            existing = _project(view, payload.project_id)
            request = ProjectRegistrationRequest(
                existing.project_id,
                existing.state.path,
                existing.display_name,
                existing.remote,
                (payload.anchor,),
                existing.default_driver,
            )
            return self._register(view, request)[0]
        _project(view, payload.project_id)
        approved = _source(view, payload.source_id)
        if not _pinned(approved.directory):
            raise LedgerError("Source installation identity changed")
        known = {
            epoch.stream_ref for epoch in view.epochs if _edge(epoch) == _edge(payload)
        }
        proofs = tuple(verifier(payload)) if verifier is not None else ()
        supplied = {
            proof.stream_ref for proof in proofs if type(proof) is VerifiedBoundary
        }
        if len(supplied) != len(proofs):
            raise ConflictError("Conflicting capture proof")
        if not known <= supplied:
            raise _AwaitBoundary
        if not payload.enabled and supplied != known:
            raise ConflictError("Disable cannot enroll a native stream")
        for proof in proofs:
            view, _ = self._epoch(view, payload, proof)
        return _permission(view, payload)

    def apply_pending(
        self,
        inbox: "ControlInbox",
        writer_lease: _PinnedPath,
        boundary_verifier: _BoundaryVerifier | None,
    ) -> tuple[ControlReceipt, ...]:
        if writer_lease is not self.lease or inbox.root != self.root:
            raise LedgerError("Monitor command requires the matching coordinator lease")
        applied: list[ControlReceipt] = []
        held_edges: set[tuple[UUID, UUID]] = set()
        with inbox.publication() as locked:
            view = self.view()
            for command in inbox.iter_pending(locked):
                digest = command.payload_digest
                receipt = _command_outcome(view, command.command_id)
                if receipt is not None:
                    if receipt.payload_digest != digest:
                        raise ConflictError("Monitor command ID has conflicting bytes")
                    if self.command_status(command.command_id) != receipt:
                        raise LedgerError("Private monitor receipt changed")
                    inbox.discard(locked, command)
                    continue
                payload = command.payload
                if isinstance(payload, CaptureChange) and _edge(payload) in held_edges:
                    continue
                try:
                    next_view = self._apply(view, payload, boundary_verifier)
                except _AwaitBoundary:
                    assert isinstance(payload, CaptureChange)
                    held_edges.add(_edge(payload))
                    continue
                except (ConflictError, LedgerError, OSError, ValueError):
                    next_view = view
                    receipt = ControlReceipt(
                        command.command_id,
                        ControlStatus.REJECTED,
                        digest,
                        "invalid-or-conflicting-request",
                    )
                else:
                    receipt = ControlReceipt(
                        command.command_id, ControlStatus.APPLIED, digest
                    )
                view = replace(next_view, receipts=(*next_view.receipts, receipt))
                self._save(view)
                inbox.discard(locked, command)
                applied.append(receipt)
        return tuple(applied)


def check_legacy_mutation(root: Path) -> None:
    """Refuse adopted legacy state before either mutation path touches it."""
    adopted = tuple(
        project
        for project in Registry(default_monitor_root()).view().projects
        if project.adopted_key_id is not None
    )
    if not adopted:
        return
    path = root.absolute()
    current = None
    if _path_exists(path):
        current = _directory(str(path), private=True)
    for project in adopted:
        if project.state.path != str(path) and (
            current is None or project.state.identity != current.identity
        ):
            continue
        if current != project.state:
            raise LedgerError("Adopted private project state identity changed")
        ledger = Ledger.open(path, project.project_id)
        if ledger.identity.key_id != project.adopted_key_id:
            raise LedgerError("Adopted private project key changed")
        raise ProjectAdopted("project-adopted-use-monitor")
