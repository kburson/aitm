"""Private command publication and source-ordered scope projection."""

import ctypes
import errno
import fcntl
import os
import secrets
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from uuid import UUID

from .ledger import (
    ConflictError,
    Ledger,
    LedgerError,
    _check_acl,
    _pin_directory,
    _PinnedPath,
    _private,
)
from .relationships import relationship_decision
from .types import (
    CommandAcknowledgment,
    CommandReceipt,
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemParent,
    LedgerView,
    MarkerDisposition,
    MarkerId,
    Provider,
    ReviewRole,
    Revision,
    ScopeCorrection,
    ScopeEnrollment,
    ScopeMarker,
    SourceBoundary,
    SourceRef,
    UsageObservation,
    WorkPhase,
    _decode,
    _encode,
    _positive,
    decode_command,
    encode_command,
)

INBOX_NAME = "inbox"
ACKS_NAME = "acks"
MAX_COMMAND_BYTES = 64 * 1024
_RENAME_EXCL = 0x00000004  # macOS renameatx_np(2)
_REVIEW_ROLES = (ReviewRole.REVIEWER, ReviewRole.SAR, ReviewRole.SPR, ReviewRole.XPR)


@dataclass(frozen=True, slots=True)
class BoundaryEvidence:
    """Adapter-verified boundary from an approved source, optionally with its checkout.

    A receipt reference on a request means the serialized tool receipt preceded
    that request. On a turn it means publication was proven before that exact
    next turn. An identity match without this proof carries no receipt reference.
    """

    boundary: SourceBoundary
    anchor_ref: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class ScopeResolution:
    scope: ScopeEnrollment | None = None
    revision: Revision | None = None
    reason: MarkerDisposition | None = None


@dataclass(frozen=True, slots=True)
class InboxDrain:
    receipts: tuple[CommandReceipt, ...] = ()
    invalid_publications: int = 0
    relationship_halted: bool = False


def _is_relationship(command: InboxCommand) -> bool:
    return isinstance(command.payload, (DraftAlias, ItemParent))


@dataclass(frozen=True, slots=True)
class _OrderedCommand:
    command: InboxCommand
    order: int

    def __post_init__(self) -> None:
        _positive(self.order)
        if not _is_relationship(self.command):
            raise ValueError("Only relationship commands have publication order")


@dataclass(frozen=True, slots=True)
class _Publication:
    command: InboxCommand
    data: bytes
    order: int | None = None


@dataclass(frozen=True, slots=True)
class _InboxSnapshot:
    publications: tuple[_Publication, ...]
    invalid: int
    relationship_halted: bool
    last_relationship_order: int


def session_reference(
    ledger: Ledger, provider: Provider, raw_session: str
) -> SourceRef:
    """Pseudonymize the transient Codex thread or controlled Claude session UUID."""
    if type(provider) is not Provider or type(raw_session) is not str:
        raise ValueError("Invalid provider session identity")
    try:
        session_id = UUID(raw_session)
    except ValueError:
        raise ValueError("Invalid provider session identity") from None
    return ledger.pseudonymize(f"{provider.value}-session", str(session_id))


def _boundary_target(boundary: SourceBoundary) -> tuple:
    return boundary.provider, boundary.session_ref, boundary.kind, boundary.boundary_ref


def _marker_target(marker: ScopeMarker) -> tuple:
    return (
        marker.provider,
        marker.session_ref,
        marker.boundary_kind,
        marker.boundary_ref,
    )


def attest_marker(marker: ScopeMarker, boundary: SourceBoundary) -> MarkerDisposition:
    if (
        _marker_target(marker) == _boundary_target(boundary)
        and marker.receipt_ref is not None
        and marker.receipt_ref == boundary.receipt_ref
    ):
        return MarkerDisposition.ACCEPTED
    return MarkerDisposition.PENDING


def _marker(command: InboxCommand) -> ScopeMarker | None:
    payload = command.payload
    if isinstance(payload, ScopeMarker):
        return payload
    if isinstance(payload, DevelopmentBinding):
        return payload.marker
    return None


@contextmanager
def _private_child(
    parent: _PinnedPath, name: str, *, create: bool
) -> Iterator[_PinnedPath | None]:
    parent.check()
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent.fd)
        except FileExistsError:
            pass
        except OSError:
            raise LedgerError("Unable to create private inbox directory") from None
        else:
            os.fsync(parent.fd)
    else:
        try:
            os.stat(name, dir_fd=parent.fd, follow_symlinks=False)
        except FileNotFoundError:
            yield None
            return
    with _pin_directory(parent.path / name) as child:
        parent.check()
        yield child


@contextmanager
def _publication(inbox: _PinnedPath) -> Iterator[None]:
    """Serialize publication with retirement, independently of the ledger lease."""
    inbox.check()
    fcntl.flock(inbox.fd, fcntl.LOCK_EX)
    try:
        inbox.check()
        yield
        inbox.check()
    finally:
        fcntl.flock(inbox.fd, fcntl.LOCK_UN)


@cache
def _rename_exclusive():
    try:
        rename = ctypes.CDLL(None, use_errno=True).renameatx_np
    except (AttributeError, OSError):
        raise LedgerError("Exclusive inbox publication is unavailable") from None
    rename.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    rename.restype = ctypes.c_int
    return rename


def _read_private(directory: _PinnedPath, name: str) -> bytes | None:
    try:
        fd = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory.fd
        )
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(fd)
        _private(info)
        _check_acl(fd)
        data = handle.read(MAX_COMMAND_BYTES + 1)
        if len(data) > MAX_COMMAND_BYTES or not os.path.samestat(
            info, os.stat(name, dir_fd=directory.fd, follow_symlinks=False)
        ):
            raise LedgerError("Invalid private inbox file")
        directory.check()
        return data


def _publish(
    directory: _PinnedPath, name: str, data: bytes, *, replace_pending: bool = False
) -> bool:
    """Publish fsynced bytes relative to a pinned private directory."""
    directory.check()
    temporary = f".publishing-{secrets.token_hex(16)}"
    fd = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
        dir_fd=directory.fd,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(fd, 0o600)
            _private(os.fstat(fd))
            _check_acl(fd)
            handle.write(data)
            handle.flush()
            os.fsync(fd)
        directory.check()
        if replace_pending:
            os.replace(
                temporary, name, src_dir_fd=directory.fd, dst_dir_fd=directory.fd
            )
        elif _rename_exclusive()(
            directory.fd,
            os.fsencode(temporary),
            directory.fd,
            os.fsencode(name),
            _RENAME_EXCL,
        ):
            if ctypes.get_errno() == errno.EEXIST:
                return False
            raise LedgerError("Unable to publish private inbox file")
        os.fsync(directory.fd)
        directory.check()
        return True
    finally:
        try:
            os.unlink(temporary, dir_fd=directory.fd)
        except FileNotFoundError:
            pass


def _filename(command_id: UUID) -> str:
    return f"{command_id}.json"


def _publication_bytes(command: InboxCommand, order: int | None) -> bytes:
    if order is None:
        return encode_command(command)
    return _encode(_OrderedCommand(command, order), _OrderedCommand).encode("utf-8")


def _decode_publication(data: bytes) -> _Publication:
    try:
        command = decode_command(data)
    except ValueError:
        ordered = _decode(data, _OrderedCommand)
        return _Publication(ordered.command, data, ordered.order)
    if _is_relationship(command):
        raise ValueError("Relationship publication is missing its order")
    return _Publication(command, data)


def enqueue_command(directory: Path, command: InboxCommand) -> CommandReceipt | None:
    """Queue canonical command bytes without taking the collector lease.

    Return the current durable outcome for a retry. None means published but
    the consuming writer has yet to record a disposition.
    """
    ledger = Ledger.open(directory, command.project_id)
    current = ledger.command_receipt(command)
    if current is not None:
        return current
    data = encode_command(command)
    try:
        with _pin_directory(ledger.root) as project:
            if Ledger.open(ledger.root, command.project_id).identity != ledger.identity:
                raise LedgerError("Private inbox project changed")
            with _private_child(project, INBOX_NAME, create=True) as inbox:
                assert inbox is not None
                with _publication(inbox):
                    # The first read may predate a final commit and retirement.
                    current = ledger.command_receipt(command)
                    if current is not None:
                        return current
                    decoded = decode_command(data)
                    ledger.validate_command(decoded)
                    if decoded != command:
                        raise LedgerError("Private inbox command changed")
                    name = _filename(command.command_id)
                    existing = _read_private(inbox, name)
                    if existing is None:
                        publication = data
                        if _is_relationship(command):
                            snapshot = _read_publications(inbox, ledger)
                            if snapshot.relationship_halted:
                                raise LedgerError(
                                    "Private relationship queue is halted"
                                )
                            order = snapshot.last_relationship_order + 1
                            publication = _publication_bytes(command, order)
                        if not _publish(inbox, name, publication):
                            existing = _read_private(inbox, name)
                    if existing is not None:
                        try:
                            prior = _decode_publication(existing)
                        except ValueError:
                            raise ConflictError(
                                "Inbox command ID has conflicting bytes"
                            ) from None
                        if (
                            prior.command != command
                            or _publication_bytes(prior.command, prior.order)
                            != existing
                        ):
                            raise ConflictError(
                                "Inbox command ID has conflicting bytes"
                            )
                project.check()
    except OSError:
        raise LedgerError("Private inbox publication failed") from None
    return ledger.command_receipt(command)


def enqueue_marker(directory: Path, marker: ScopeMarker) -> MarkerId:
    enqueue_command(
        directory, InboxCommand(marker.marker_id, marker.project_id, marker)
    )
    return marker.marker_id


def _acknowledge(
    inbox: _PinnedPath,
    directory: _PinnedPath,
    receipt: CommandReceipt,
    captured: bytes,
) -> None:
    expected = receipt.acknowledgment
    data = _encode(expected, CommandAcknowledgment).encode("utf-8")
    name = _filename(expected.command_id)
    with _publication(inbox):
        final = receipt.disposition is not MarkerDisposition.PENDING
        if final and _read_private(inbox, name) != captured:
            raise ConflictError("Inbox publication changed before retirement")
        existing = _read_private(directory, name)
        if existing != data:
            if existing is not None:
                previous = _decode(existing, CommandAcknowledgment)
                if previous != replace(expected, disposition=MarkerDisposition.PENDING):
                    raise ConflictError(
                        "Inbox acknowledgment conflicts with committed history"
                    )
            if not _publish(
                directory, name, data, replace_pending=existing is not None
            ):
                raise ConflictError("Inbox acknowledgment path changed")
        if final:
            os.unlink(name, dir_fd=inbox.fd)
            os.fsync(inbox.fd)


def _read_publications(inbox: _PinnedPath, ledger: Ledger) -> _InboxSnapshot:
    """Read a consistent set of final publications while holding the inbox mutex."""
    publications = []
    invalid = 0
    halted = False
    orders = set()
    for name in os.listdir(inbox.fd):
        if name.startswith(".") or not name.endswith(".json"):
            continue
        publication = None
        try:
            data = _read_private(inbox, name)
            if data is None:
                raise LedgerError("Private inbox publication disappeared")
            publication = _decode_publication(data)
            command = publication.command
            ledger.validate_command(command)
            if (
                _filename(command.command_id) != name
                or _publication_bytes(command, publication.order) != data
            ):
                raise ValueError("Invalid canonical inbox publication")
            if publication.order is not None:
                if publication.order in orders:
                    raise ValueError("Duplicate relationship publication order")
                orders.add(publication.order)
        except (LedgerError, OSError, ValueError):
            invalid += 1
            # Unclassifiable final bytes could hide an earlier relationship.
            halted |= publication is None or _is_relationship(publication.command)
        else:
            publications.append(publication)
    return _InboxSnapshot(tuple(publications), invalid, halted, max(orders, default=0))


def _dispatch_order(publication: _Publication) -> tuple[int, int, int]:
    command = publication.command
    payload = command.payload
    if publication.order is not None:
        return 3, publication.order, 0
    if isinstance(payload, ScopeCorrection):
        return 2, 0, command.command_id.int
    if isinstance(payload, DevelopmentBinding):
        return 0, payload.generation, command.command_id.int
    return 1, payload.scope_sequence, command.command_id.int


def _select_evidence(
    marker: ScopeMarker, boundaries: tuple[BoundaryEvidence, ...]
) -> tuple[BoundaryEvidence | None, SourceBoundary | None, bool]:
    targets = {
        entry
        for entry in boundaries
        if _boundary_target(entry.boundary) == _marker_target(marker)
    }
    proven = [
        entry
        for entry in targets
        if attest_marker(marker, entry.boundary) is MarkerDisposition.ACCEPTED
    ]
    proven_boundaries = {entry.boundary for entry in proven}
    anchors = {entry.anchor_ref for entry in proven if entry.anchor_ref is not None}
    contradictory = len(proven_boundaries) > 1 or len(anchors) > 1

    # A location hint can bound Unknown without authorizing attribution.
    locations = {replace(entry.boundary, receipt_ref=None) for entry in targets}
    hint = next(iter(locations)) if len(locations) == 1 else None
    if not proven or contradictory:
        return None, hint, contradictory
    return BoundaryEvidence(proven[0].boundary, next(iter(anchors), None)), hint, False


def _enrollments(view: LedgerView) -> Iterator[tuple[Revision, ScopeEnrollment]]:
    for revision in view.current:
        if isinstance(revision.record, ScopeEnrollment):
            yield revision, revision.record


def _same_session(left: SourceBoundary, right: SourceBoundary) -> bool:
    return left.provider is right.provider and left.session_ref == right.session_ref


def _same_stream(left: SourceBoundary, right: SourceBoundary) -> bool:
    return _same_session(left, right) and left.stream_ref == right.stream_ref


def _binding_for(
    candidate: ScopeEnrollment, scopes: tuple[ScopeEnrollment, ...]
) -> tuple[ScopeEnrollment, ...]:
    bindings: dict[SourceRef, ScopeEnrollment] = {}
    for scope in scopes:
        if scope.generation is None:
            continue
        if _same_stream(scope.boundary, candidate.boundary) and (
            scope.boundary.ordinal > candidate.boundary.ordinal
        ):
            continue
        anchor = scope.anchor_ref
        assert anchor is not None
        if anchor not in bindings or scope.generation > bindings[anchor].generation:
            bindings[anchor] = scope
    exact = tuple(
        binding
        for anchor, binding in bindings.items()
        if anchor == candidate.anchor_ref
        or _same_session(binding.boundary, candidate.boundary)
    )
    if exact:
        return exact
    if candidate.marker.role in _REVIEW_ROLES:
        matching_item = tuple(
            binding
            for binding in bindings.values()
            if binding.marker.item == candidate.marker.item
        )
        if candidate.marker.attempt_ref is not None:
            matching_attempt = tuple(
                binding
                for binding in matching_item
                if binding.marker.attempt_ref == candidate.marker.attempt_ref
            )
            return matching_attempt or matching_item
        return matching_item
    return ()


def _check_scope(
    candidate: ScopeEnrollment, scopes: tuple[ScopeEnrollment, ...]
) -> MarkerDisposition:
    marker = candidate.marker
    boundary = candidate.boundary
    for scope in scopes:
        same_stream = _same_stream(scope.boundary, boundary)
        later = boundary.ordinal > scope.boundary.ordinal
        if _same_session(scope.boundary, boundary):
            other_sequence = scope.marker.scope_sequence
            if other_sequence == marker.scope_sequence:
                return MarkerDisposition.CONFLICT
            if same_stream and (
                boundary.ordinal == scope.boundary.ordinal
                or later != (marker.scope_sequence > other_sequence)
            ):
                return MarkerDisposition.CONFLICT
        if (
            candidate.generation is not None
            and scope.generation is not None
            and scope.anchor_ref == candidate.anchor_ref
        ):
            generation = candidate.generation
            if generation == scope.generation:
                return MarkerDisposition.CONFLICT
            generation_later = generation > scope.generation
            if same_stream and generation_later != later:
                return MarkerDisposition.CONFLICT
            if not same_stream and not generation_later:
                return MarkerDisposition.CONFLICT
    if candidate.generation is not None:
        return MarkerDisposition.ACCEPTED

    bindings = _binding_for(candidate, scopes)
    if not bindings:
        return (
            MarkerDisposition.PENDING
            if marker.phase is WorkPhase.DEVELOPMENT
            else MarkerDisposition.ACCEPTED
        )
    if len(bindings) == 1 and _compatible_development_scope(candidate, bindings[0]):
        return MarkerDisposition.ACCEPTED
    return MarkerDisposition.CONFLICT


def _compatible_development_scope(
    candidate: ScopeEnrollment, binding: ScopeEnrollment
) -> bool:
    marker = candidate.marker
    owner = binding.marker
    if marker.item != owner.item or marker.attempt_ref not in (None, owner.attempt_ref):
        return False
    if (marker.provider, marker.session_ref) == (owner.provider, owner.session_ref):
        return (
            _same_stream(candidate.boundary, binding.boundary)
            and candidate.anchor_ref == binding.anchor_ref
            and marker.participant_ref == owner.participant_ref
            and marker.role in (None, ReviewRole.AUTHOR)
        )
    return (
        marker.phase is not WorkPhase.DEVELOPMENT
        and marker.role in _REVIEW_ROLES
        and marker.review_ref is not None
        and marker.participant_ref != owner.participant_ref
    )


def _correction(
    correction: ScopeCorrection,
    receipts: dict[UUID, CommandReceipt],
) -> tuple[MarkerDisposition, ScopeEnrollment | None]:
    replacement = correction.replacement
    prior = receipts.get(replacement.marker_id)
    if prior is None:
        return MarkerDisposition.PENDING, None
    original = prior.command.payload
    if (
        not isinstance(original, ScopeMarker)
        or replace(
            replacement,
            item=original.item,
            phase=original.phase,
            participant_ref=original.participant_ref,
            role=original.role,
            attempt_ref=original.attempt_ref,
            review_ref=original.review_ref,
        )
        != original
    ):
        return MarkerDisposition.CONFLICT, None
    if prior.disposition is MarkerDisposition.PENDING:
        return MarkerDisposition.PENDING, None
    boundary = prior.boundary
    if (
        boundary is None
        or attest_marker(replacement, boundary) is not MarkerDisposition.ACCEPTED
    ):
        return MarkerDisposition.CONFLICT, None
    return MarkerDisposition.ACCEPTED, ScopeEnrollment(
        replacement, boundary, prior.anchor_ref
    )


def _evaluate(
    ledger: Ledger,
    command: InboxCommand,
    view: LedgerView,
    boundaries: tuple[BoundaryEvidence, ...],
    receipts: dict[UUID, CommandReceipt],
) -> tuple[MarkerDisposition, BoundaryEvidence | None, tuple[Revision, ...]]:
    payload = command.payload
    if isinstance(payload, (DraftAlias, ItemParent)):
        disposition, effects = relationship_decision(payload, view, ledger.pseudonymize)
        return disposition, None, effects
    if isinstance(payload, ScopeCorrection):
        status, candidate = _correction(payload, receipts)
        if candidate is None:
            return status, None, ()
        evidence = BoundaryEvidence(candidate.boundary, candidate.anchor_ref)
    else:
        marker = _marker(command)
        assert marker is not None
        prior = receipts.get(command.command_id)
        if (
            prior is not None
            and prior.boundary is not None
            and attest_marker(marker, prior.boundary) is MarkerDisposition.ACCEPTED
        ):
            boundaries = (
                *boundaries,
                BoundaryEvidence(prior.boundary, prior.anchor_ref),
            )
        evidence, hint, contradictory = _select_evidence(marker, boundaries)
        location = None if hint is None else BoundaryEvidence(hint)
        if contradictory:
            return MarkerDisposition.CONFLICT, location, ()
        if evidence is None or (
            isinstance(payload, DevelopmentBinding)
            and payload.anchor_ref != evidence.anchor_ref
        ):
            return MarkerDisposition.PENDING, location, ()
        candidate = ScopeEnrollment(
            marker,
            evidence.boundary,
            evidence.anchor_ref,
            payload.generation if isinstance(payload, DevelopmentBinding) else None,
        )
    scopes = tuple(
        scope
        for _, scope in _enrollments(view)
        if scope.marker.marker_id != candidate.marker.marker_id
    )
    disposition = _check_scope(candidate, scopes)
    effects = (
        (_scope_revision(ledger, candidate, view),)
        if disposition is MarkerDisposition.ACCEPTED
        else ()
    )
    return disposition, evidence, effects


def _scope_revision(
    ledger: Ledger, scope: ScopeEnrollment, view: LedgerView
) -> Revision:
    key = ledger.pseudonymize("scope-enrollment", str(scope.marker.marker_id))
    number = next(
        (revision.revision for revision in view.current if revision.key == key), 0
    )
    return Revision(key, number + 1, scope)


def drain_inbox(writer: Ledger, boundaries: Iterable[BoundaryEvidence]) -> InboxDrain:
    """Consume queued commands as the collector, then publish durable acknowledgments."""
    writer.require_writer()
    boundaries = tuple(boundaries)
    for entry in boundaries:
        writer.validate_boundary(entry.boundary)
        if entry.anchor_ref is not None:
            writer.validate_source_ref(entry.anchor_ref)
    with (
        _pin_directory(writer.root) as project,
        _private_child(project, INBOX_NAME, create=False) as inbox,
    ):
        if inbox is None:
            return InboxDrain()
        with _publication(inbox):
            snapshot = _read_publications(inbox, writer)
        invalid = snapshot.invalid
        halted = snapshot.relationship_halted
        if not snapshot.publications:
            return InboxDrain(invalid_publications=invalid, relationship_halted=halted)
        outcomes = []
        with _private_child(inbox, ACKS_NAME, create=True) as acknowledgments:
            assert acknowledgments is not None
            view = writer.as_of()
            receipts = {
                revision.record.command.command_id: revision.record
                for revision in view.current
                if isinstance(revision.record, CommandReceipt)
            }
            for publication in sorted(snapshot.publications, key=_dispatch_order):
                command = publication.command
                relationship = publication.order is not None
                if relationship and halted:
                    break
                digest = writer.validate_command(command)
                current = receipts.get(command.command_id)
                if current is not None and (
                    current.digest != digest or current.command != command
                ):
                    invalid += 1
                    if relationship:
                        halted = True
                        break
                    continue
                receipt = current
                if current is None or current.disposition is MarkerDisposition.PENDING:
                    disposition, evidence, effects = _evaluate(
                        writer, command, view, boundaries, receipts
                    )
                    inbox.check()
                    receipt = writer.commit_command(
                        CommandReceipt(
                            command,
                            digest,
                            disposition,
                            None if evidence is None else evidence.boundary,
                            None if evidence is None else evidence.anchor_ref,
                        ),
                        effects,
                        expected_sequence=view.sequence,
                    )
                    if (
                        relationship
                        and receipt.disposition is MarkerDisposition.PENDING
                    ):
                        halted = True
                        break
                    receipts[command.command_id] = receipt
                    if current != receipt:
                        view = writer.as_of()
                writer.require_writer()
                _acknowledge(inbox, acknowledgments, receipt, publication.data)
                outcomes.append(receipt)
        return InboxDrain(tuple(outcomes), invalid, halted)


def _within_owner_generation(
    observation: UsageObservation,
    owner: ScopeEnrollment,
    enrollments: tuple[tuple[Revision, ScopeEnrollment], ...],
    view: LedgerView,
) -> bool:
    assert owner.generation is not None
    replacements = {
        revision.key
        for revision, scope in enrollments
        if scope.anchor_ref == owner.anchor_ref
        and scope.generation is not None
        and scope.generation > owner.generation
        and not _same_stream(scope.boundary, owner.boundary)
    }
    if not replacements:
        return True

    # Independent streams have no common provider ordinal. Preserve an old
    # enrollment only for a uniquely identified, admitted observation lineage
    # already present in the durable prefix before the first replacement.
    matches = [
        revision.key for revision in view.current if revision.record == observation
    ]
    if len(matches) != 1:
        return False
    (observation_key,) = matches
    enrolled = recorded = False
    for revision in view.revisions:
        record = revision.record
        if isinstance(record, ScopeEnrollment):
            if revision.key in replacements:
                return enrolled and recorded
            if record == owner:
                enrolled = True
        elif revision.key == observation_key:
            recorded = True
    return False


def resolve_scope(observation: UsageObservation, view: LedgerView) -> ScopeResolution:
    """Project an already admitted observation at this ledger snapshot."""
    boundary = observation.boundary
    enrollments = tuple(_enrollments(view))
    candidates = [
        (revision, scope)
        for revision, scope in enrollments
        if scope.marker.project_id == view.project_id
        and _same_stream(scope.boundary, boundary)
        and scope.boundary.ordinal <= boundary.ordinal
    ]
    current = max(candidates, key=lambda pair: pair[1].boundary.ordinal, default=None)
    active = None if current is None else current[1]
    if active is not None:
        # A delayed owner receipt may prove a binding before an already
        # enrolled marker. Only compare ordinals within that same stream.
        owner = max(
            (scope for _, scope in candidates if scope.generation is not None),
            key=lambda scope: scope.boundary.ordinal,
            default=None,
        )
        if owner is not None:
            if active != owner and not _compatible_development_scope(active, owner):
                return ScopeResolution(reason=MarkerDisposition.CONFLICT)
            if not _within_owner_generation(observation, owner, enrollments, view):
                return ScopeResolution()
    resolved_ids = {scope.marker.marker_id for _, scope in enrollments}
    blockers = set()
    for revision in view.current:
        receipt = revision.record
        if (
            not isinstance(receipt, CommandReceipt)
            or receipt.disposition is MarkerDisposition.ACCEPTED
            or receipt.command.project_id != view.project_id
        ):
            continue
        marker = _marker(receipt.command)
        if marker is None or marker.marker_id in resolved_ids:
            continue
        if (
            marker.provider is not boundary.provider
            or marker.session_ref != boundary.session_ref
        ):
            continue
        location = receipt.boundary
        if location is not None and _same_stream(location, boundary):
            if location.ordinal > boundary.ordinal:
                continue
            if active is not None and (
                active.boundary.ordinal > location.ordinal
                and active.marker.scope_sequence > marker.scope_sequence
            ):
                continue
        elif location is not None and location.receipt_ref is not None:
            continue
        elif active is not None and (
            active.marker.scope_sequence > marker.scope_sequence
            or active.boundary.ordinal == boundary.ordinal
            and active.marker.scope_sequence < marker.scope_sequence
            and _marker_target(marker) != _boundary_target(boundary)
        ):
            continue
        blockers.add(receipt.disposition)
    if MarkerDisposition.CONFLICT in blockers:
        return ScopeResolution(reason=MarkerDisposition.CONFLICT)
    if MarkerDisposition.PENDING in blockers:
        return ScopeResolution(reason=MarkerDisposition.PENDING)
    return ScopeResolution() if current is None else ScopeResolution(active, current[0])
