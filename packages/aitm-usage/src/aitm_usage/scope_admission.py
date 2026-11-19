"""Private scope-producer grants and typed monitor proposals."""

import hmac
import os
import re
import stat
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import file_digest, sha256
from pathlib import Path
from uuid import UUID, uuid4, uuid5

from .ledger import (
    ConflictError,
    Ledger,
    LedgerError,
    _path_exists,
    _pin_directory,
    _PinnedPath,
)
from .monitor_registry import (
    _SOURCE_KEY_FILE,
    ApprovedSource,
    Registry,
    _check_capture_root,
    _directory,
    _PhysicalDirectory,
    _project,
    _read_state,
    _ServiceEvidence,
    _source,
)
from .monitor_scope import Mark, Scope
from .monitor_types import NativeSurface
from .scopes import _filename, _private_child, _publish, _read_private
from .types import (
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemParent,
    Provider,
    ScopeCorrection,
    ScopeMarker,
    SourceRef,
    _decode,
    _encode,
    _nonnegative,
    _positive,
    decode_command,
    encode_command,
)

PROTOCOL = "aitm.usage.monitor-scope-proposal/v1"
_GRANTS = "scope-admission-v1"
WITNESS_LIFETIME = timedelta(seconds=60)
_MAX_CLOCK_SKEW = timedelta(seconds=5)


class GrantRole(StrEnum):
    OPERATOR = "operator"
    INTEGRATION = "integration"


@dataclass(frozen=True, slots=True)
class MarkRequest:
    command_id: UUID
    grant_id: UUID
    scope: Scope
    destination_binding: DevelopmentBinding | None = None


@dataclass(frozen=True, slots=True)
class HandoffRequest:
    command_id: UUID
    grant_id: UUID
    current_project: UUID
    destination: Scope
    before_generation: int
    retained_checkout: SourceRef | None = None
    destination_binding: DevelopmentBinding | None = None

    def __post_init__(self) -> None:
        _nonnegative(self.before_generation)
        if self.current_project == self.destination.project_id:
            raise ValueError("A scope handoff requires another project")


@dataclass(frozen=True, slots=True)
class DispositionRequest:
    command_id: UUID
    grant_id: UUID
    project_id: UUID
    hold_id: UUID
    release_previous: bool = False


@dataclass(frozen=True, slots=True)
class AdoptedRequest:
    command_id: UUID
    grant_id: UUID
    project_id: UUID
    adoption_id: UUID
    legacy_bytes: str
    claude_session: SourceRef | None

    def __post_init__(self) -> None:
        data = self.legacy_bytes.encode()
        legacy = decode_command(data)
        if (
            (legacy.command_id, legacy.project_id) != (self.command_id, self.project_id)
            or encode_command(legacy) != data
            or type(legacy.payload)
            not in (
                DevelopmentBinding,
                DraftAlias,
                ItemParent,
                ScopeCorrection,
                ScopeMarker,
            )
        ):
            raise ValueError("Adopted scope request changed its legacy command")
        marker = (
            legacy.payload.marker
            if isinstance(legacy.payload, DevelopmentBinding)
            else legacy.payload
        )
        expected = (
            marker.session_ref
            if isinstance(marker, ScopeMarker) and marker.provider is Provider.CLAUDE
            else None
        )
        if self.claude_session != expected:
            raise ValueError("Adopted scope request changed its verified session")


ScopeRequest = MarkRequest | HandoffRequest | DispositionRequest | AdoptedRequest

REQUEST_TYPES = {
    "mark": MarkRequest,
    "handoff": HandoffRequest,
    "dispose": DispositionRequest,
}
_ACTIONS = {
    MarkRequest: "mark",
    HandoffRequest: "handoff",
    DispositionRequest: "dispose",
    AdoptedRequest: "legacy",
}


def _owner(request: ScopeRequest) -> UUID:
    if isinstance(request, MarkRequest):
        return request.scope.project_id
    if isinstance(request, HandoffRequest):
        return request.current_project
    return request.project_id


def legacy_grant_id(project_id: UUID, adoption_id: UUID) -> UUID:
    return uuid5(project_id, f"monitor-legacy-scope/v1:{adoption_id}")


def adopted_request(
    command: InboxCommand, adoption_id: UUID, claude_session: SourceRef | None
) -> AdoptedRequest:
    return AdoptedRequest(
        command.command_id,
        legacy_grant_id(command.project_id, adoption_id),
        command.project_id,
        adoption_id,
        encode_command(command).decode(),
        claude_session,
    )


@dataclass(frozen=True, slots=True)
class _Grant:
    grant_id: UUID
    generation: int
    project_id: UUID
    role: GrantRole
    actions: tuple[str, ...]
    account: _PhysicalDirectory
    project: _PhysicalDirectory
    ledger_key: str
    authority_key: str
    adoption_id: UUID | None

    def __post_init__(self) -> None:
        _positive(self.generation)
        allowed = {"legacy"} if self.adoption_id is not None else set(REQUEST_TYPES)
        if (
            not self.actions
            or tuple(sorted(set(self.actions))) != self.actions
            or not set(self.actions) <= allowed
            or (
                self.adoption_id is not None
                and self.grant_id != legacy_grant_id(self.project_id, self.adoption_id)
            )
        ):
            raise ValueError("Invalid scope producer grant")


@dataclass(frozen=True, slots=True)
class _ReaderWitness:
    issued: datetime
    expires: datetime
    probe_digest: str
    tag: str

    def __post_init__(self) -> None:
        if not all(
            re.fullmatch(r"[a-f0-9]{64}", value)
            for value in (self.probe_digest, self.tag)
        ):
            raise ValueError("Invalid scope reader witness")


@dataclass(frozen=True, slots=True)
class _GrantRecord:
    grant: _Grant
    credential: str = field(repr=False)
    witness: _ReaderWitness | None = None
    revoked: bool = False

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-f0-9]{64}", self.credential):
            raise ValueError("Invalid scope credential")


@dataclass(frozen=True, slots=True)
class _GrantCommit:
    revision: int
    record: _GrantRecord
    seal: str

    def __post_init__(self) -> None:
        if not 0 < self.revision < 10**20 or not re.fullmatch(
            r"[a-f0-9]{64}", self.seal
        ):
            raise ValueError("Invalid committed scope grant")


@dataclass(frozen=True, slots=True)
class _ScopeBody:
    request: ScopeRequest
    generation: int
    format: str = PROTOCOL

    def __post_init__(self) -> None:
        _positive(self.generation)
        if self.format != PROTOCOL:
            raise ValueError("Unsupported scope proposal format")


@dataclass(frozen=True, slots=True)
class ScopeEnvelope:
    body: _ScopeBody
    seal: str

    @property
    def command_id(self) -> UUID:
        return self.body.request.command_id

    @property
    def payload_digest(self) -> str:
        return sha256(_encode(self, ScopeEnvelope).encode()).hexdigest()


def _tag(secret: bytes, domain: bytes, *parts: str) -> str:
    return hmac.digest(
        secret, domain + b"\0" + b"\0".join(p.encode() for p in parts), "sha256"
    ).hex()


def _credential(record: _GrantRecord) -> bytes:
    return bytes.fromhex(record.credential)


def _authority(registry: Registry, root: _PinnedPath) -> _ServiceEvidence:
    expected = registry.view().source_key_id
    if expected is None:
        raise LedgerError("Scope authority is not initialized")
    key = _read_private(root, _SOURCE_KEY_FILE)
    if key is None or len(key) != 32:
        raise LedgerError("Scope authority is unavailable")
    evidence = _ServiceEvidence(key)
    if evidence.key_id != expected:
        raise LedgerError("Scope authority changed")
    return evidence


def _witness_tag(
    key: bytes, record: _GrantRecord, issued: datetime, expires: datetime, digest: str
) -> str:
    return _tag(
        key,
        b"scope-witness/v1",
        PROTOCOL,
        _encode(record.grant, _Grant),
        issued.isoformat(),
        expires.isoformat(),
        digest,
    )


def _witness_for_probe(
    writer: Registry, record: _GrantRecord, now: datetime, probe: ScopeEnvelope
) -> _ReaderWitness:
    writer.lease
    expires = now + WITNESS_LIFETIME
    digest = probe.payload_digest
    with _pin_directory(writer.root) as root:
        key = _authority(writer, root)
        tag = _witness_tag(key.key, record, now, expires, digest)
    return _ReaderWitness(now, expires, digest, tag)


def check_witness_time(record: _GrantRecord, now: datetime) -> _ReaderWitness:
    witness = record.witness
    if (
        witness is None
        or witness.issued.utcoffset() != timedelta(0)
        or witness.expires.utcoffset() != timedelta(0)
        or witness.issued > now + _MAX_CLOCK_SKEW
        or not now < witness.expires
        or not timedelta(0) < witness.expires - witness.issued <= WITNESS_LIFETIME
    ):
        raise LedgerError("Scope consumer is unavailable")
    return witness


def require_witness(registry: Registry, record: _GrantRecord, now: datetime) -> None:
    witness = check_witness_time(record, now)
    with _pin_directory(registry.root) as root:
        key = _authority(registry, root)
        tag = _witness_tag(
            key.key, record, witness.issued, witness.expires, witness.probe_digest
        )
        if not hmac.compare_digest(witness.tag, tag):
            raise LedgerError("Scope consumer is unavailable")


def seal_request(record: _GrantRecord, request: ScopeRequest) -> ScopeEnvelope:
    grant = record.grant
    if (
        record.revoked
        or request.grant_id != grant.grant_id
        or _owner(request) != grant.project_id
        or _ACTIONS[type(request)] not in grant.actions
        or (
            isinstance(request, AdoptedRequest)
            and request.adoption_id != grant.adoption_id
        )
    ):
        raise LedgerError("Scope producer grant is unavailable")
    body = _ScopeBody(request, grant.generation)
    seal = _tag(_credential(record), b"scope-command/v1", _encode(body, _ScopeBody))
    return ScopeEnvelope(body, seal)


def _grant_tag(key: bytes, grant: _Grant) -> str:
    return _tag(key, b"scope-grant/v1", _encode(grant, _Grant))


def _commit_tag(key: bytes, revision: int, record: _GrantRecord) -> str:
    return _tag(
        key, b"scope-grant-commit/v1", str(revision), _encode(record, _GrantRecord)
    )


@contextmanager
def _grant_directory(
    root: _PinnedPath, grant_id: UUID, *, create: bool
) -> Iterator[_PinnedPath | None]:
    with _private_child(root, _GRANTS, create=create) as directory:
        if directory is None:
            yield None
        else:
            with _private_child(directory, str(grant_id), create=create) as grant:
                yield grant


def _revisions(grant: _PinnedPath) -> list[str]:
    return sorted(
        name for name in os.listdir(grant.fd) if re.fullmatch(r"[0-9]{20}\.json", name)
    )


def _read_commit(
    root: _PinnedPath,
    directory: _PinnedPath,
    registry: Registry,
    grant_id: UUID,
    name: str,
) -> _GrantCommit:
    data = _read_private(directory, name)
    if data is None:
        raise LedgerError("Committed scope grant disappeared")
    commit = _decode(data, _GrantCommit)
    key = _authority(registry, root)
    record = commit.record
    if (
        f"{commit.revision:020}.json" != name
        or record.grant.grant_id != grant_id
        or _encode(commit, _GrantCommit).encode() != data
        or not hmac.compare_digest(
            commit.seal, _commit_tag(key.key, commit.revision, record)
        )
        or not hmac.compare_digest(record.credential, _grant_tag(key.key, record.grant))
    ):
        raise LedgerError("Invalid committed scope grant")
    return commit


def _committed_grant(
    registry: Registry, root: _PinnedPath, grant_id: UUID, *, confirm: bool = False
) -> _GrantCommit | None:
    with _grant_directory(root, grant_id, create=False) as directory:
        if directory is None or not (names := _revisions(directory)):
            return None
        commit = _read_commit(root, directory, registry, grant_id, names[-1])
        if confirm:
            os.fsync(directory.fd)
            directory.check()
        return commit


def stored_grant(root: Path, grant_id: UUID) -> _GrantRecord | None:
    if not _path_exists(root):
        return None
    with _pin_directory(root) as directory:
        commit = _committed_grant(Registry(root), directory, grant_id)
        return None if commit is None else commit.record


def preliminary_grant(root: Path, grant_id: UUID) -> bool:
    record = stored_grant(root, grant_id)
    return record is not None and not record.revoked


@contextmanager
def open_grant(
    registry: Registry, grant_id: UUID
) -> Iterator[tuple[_GrantRecord, Callable[[], None], int]]:
    with _pin_directory(registry.root) as root:
        commit = _committed_grant(registry, root, grant_id, confirm=True)
        if commit is None or commit.record.revoked:
            raise LedgerError("Scope producer grant is unavailable")
        record = commit.record
        grant = record.grant
        view = registry.view()
        project = _project(view, grant.project_id)
        if (
            grant.account != _directory(str(root.path), private=True)
            or grant.project != project.state
            or grant.authority_key != view.source_key_id
        ):
            raise LedgerError("Scope producer grant identity changed")
        with _pin_directory(Path(project.state.path)) as state:
            ledger = Ledger.open(state.path, grant.project_id)
            if (
                grant.project != _directory(str(state.path), private=True)
                or grant.ledger_key != ledger.identity.key_id
                or (
                    grant.adoption_id is not None
                    and (
                        project.adopted_key_id != grant.ledger_key
                        or _adoption(ledger, state) != grant.adoption_id
                    )
                )
            ):
                raise LedgerError("Scope producer project identity changed")

            def recheck() -> None:
                root.check()
                state.check()
                current = Ledger.open(state.path, grant.project_id)
                if current.identity != ledger.identity or (
                    grant.adoption_id is not None
                    and _adoption(current, state) != grant.adoption_id
                ):
                    raise LedgerError("Scope producer project ledger changed")

            yield record, recheck, commit.revision
            recheck()


def require_unseen_legacy(record: _GrantRecord, request: ScopeRequest) -> None:
    if isinstance(request, AdoptedRequest):
        command = decode_command(request.legacy_bytes.encode())
        ledger = Ledger.open(Path(record.grant.project.path), request.project_id)
        if ledger.command_receipt(command) is not None:
            raise LedgerError("The legacy command already has a receipt")


def _adoption(ledger: Ledger, state: _PinnedPath) -> UUID | None:
    from .scopes import read_monitor_adoption

    return read_monitor_adoption(ledger, state)


def build_grant(
    writer: Registry,
    grant_id: UUID,
    project_id: UUID,
    actions: tuple[str, ...],
    generation: int,
    role: GrantRole,
    adoption_id: UUID | None,
) -> _GrantRecord:
    writer.lease
    view = writer.view()
    if view.source_key_id is None:
        raise LedgerError("Scope authority is not initialized")
    project = _project(view, project_id)
    with _pin_directory(Path(project.state.path)) as state:
        ledger = Ledger.open(state.path, project_id)
        if project.state != _directory(str(state.path), private=True) or (
            adoption_id is not None
            and (
                project.adopted_key_id != ledger.identity.key_id
                or _adoption(ledger, state) != adoption_id
            )
        ):
            raise LedgerError("Scope producer project identity changed")
        key = writer.source_evidence()
        grant = _Grant(
            grant_id,
            generation,
            project_id,
            role,
            tuple(sorted(actions)),
            _directory(str(writer.root), private=True),
            project.state,
            ledger.identity.key_id,
            key.key_id,
            adoption_id,
        )
        token = _grant_tag(key.key, grant)
        state.check()
    return _GrantRecord(grant, token)


def _write_grant(
    writer: Registry, record: _GrantRecord, previous: _GrantRecord | None
) -> None:
    writer.lease
    grant_id = record.grant.grant_id
    with (
        _pin_directory(writer.root) as root,
        _grant_directory(root, grant_id, create=True) as directory,
    ):
        assert directory is not None
        names = _revisions(directory)
        current = (
            _read_commit(root, directory, writer, grant_id, names[-1])
            if names
            else None
        )
        if (current.record if current is not None else None) != previous:
            raise LedgerError("Scope producer grant changed")
        key = _authority(writer, root)
        if not hmac.compare_digest(
            record.credential, _grant_tag(key.key, record.grant)
        ):
            raise LedgerError("Scope producer grant seal does not match")
        revision = 1 if current is None else current.revision + 1
        commit = _GrantCommit(revision, record, _commit_tag(key.key, revision, record))
        writer.lease
        if not _publish(
            directory, f"{revision:020}.json", _encode(commit, _GrantCommit).encode()
        ):
            raise LedgerError("Scope producer grant changed")
        # The highest authenticated revision wins even if cleanup was interrupted.
        for name in names:
            os.unlink(name, dir_fd=directory.fd)
        if names:
            os.fsync(directory.fd)
        writer.lease


@contextmanager
def pinned_destination(
    registry: Registry, request: ScopeRequest
) -> Iterator[Callable[[], None] | None]:
    if not isinstance(request, HandoffRequest):
        yield None
        return
    project = _project(registry.view(), request.destination.project_id)
    with _pin_directory(Path(project.state.path)) as state:
        if project.state != _directory(str(state.path), private=True):
            raise LedgerError("Scope destination identity changed")
        ledger = Ledger.open(state.path, project.project_id)

        def recheck() -> None:
            state.check()
            if Ledger.open(state.path, project.project_id).identity != ledger.identity:
                raise LedgerError("Scope destination ledger changed")

        yield recheck
        recheck()


_GROK_RECEIPTS = "grok-scope-receipts-v1"
_GROK_QUALIFICATION_RECORD = "isolated-qualification.json"
_MAX_GROK_RECEIPTS_BYTES = 1024 * 1024


@dataclass(frozen=True, slots=True)
class _GrokScopeAttempt:
    selector: SourceRef
    command_id: UUID
    proposal_digest: str
    source_id: UUID
    source: SourceRef
    profile: SourceRef
    qualification_record: SourceRef
    checkout: SourceRef
    session: SourceRef
    process: SourceRef
    image: SourceRef
    expires: datetime
    prompt: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class _GrokScopeReceipts:
    attempts: tuple[_GrokScopeAttempt, ...]
    seal: str


def _grok_receipts_name(evidence: _ServiceEvidence) -> str:
    key = evidence.pseudonymize("grok-scope-receipts", "v1").value
    return f"{key.rsplit(':', 1)[1]}.json"


def _grok_qualification_record_ref(
    root: _PinnedPath, evidence: _ServiceEvidence
) -> SourceRef:
    # The live writer authenticates the revision. The hook only compares the
    # pinned record to the reference sealed by that writer during staging.
    record = _read_private(root, _GROK_QUALIFICATION_RECORD)
    if record is None:
        raise LedgerError("Grok qualification revision changed")
    return evidence.pseudonymize(
        "grok-qualification-record", sha256(record).hexdigest()
    )


def _grok_receipts_wire(
    attempts: tuple[_GrokScopeAttempt, ...], evidence: _ServiceEvidence
) -> _GrokScopeReceipts:
    body = _encode(
        attempts,
        tuple[_GrokScopeAttempt, ...],
        validate_ref=evidence.validate_source_ref,
    )
    return _GrokScopeReceipts(
        attempts, _tag(evidence.key, b"grok-scope-receipts/v1", body)
    )


def _grok_receipts(
    directory: _PinnedPath, evidence: _ServiceEvidence
) -> tuple[_GrokScopeAttempt, ...]:
    name = _grok_receipts_name(evidence)
    raw = _read_state(directory, name, _MAX_GROK_RECEIPTS_BYTES)
    if raw is None:
        return ()
    receipt = _decode(
        raw, _GrokScopeReceipts, validate_ref=evidence.validate_source_ref
    )
    expected = _grok_receipts_wire(receipt.attempts, evidence)
    if (
        len(raw) > _MAX_GROK_RECEIPTS_BYTES
        or not hmac.compare_digest(receipt.seal, expected.seal)
        or _encode(receipt, _GrokScopeReceipts).encode() != raw
    ):
        raise LedgerError("Invalid committed Grok scope receipts")
    return receipt.attempts


def _store_grok_receipts(
    directory: _PinnedPath,
    evidence: _ServiceEvidence,
    attempts: tuple[_GrokScopeAttempt, ...],
    recheck: Callable[[], None],
) -> None:
    data = _encode(_grok_receipts_wire(attempts, evidence), _GrokScopeReceipts).encode()
    if len(data) > _MAX_GROK_RECEIPTS_BYTES:
        raise LedgerError("Private Grok scope receipt capacity exceeded")
    if (
        not _publish(
            directory,
            _grok_receipts_name(evidence),
            data,
            replace_pending=True,
            before_commit=recheck,
        )
        or _grok_receipts(directory, evidence) != attempts
    ):
        raise LedgerError("Grok scope receipt publication changed")


@contextmanager
def _grok_mark_proposal(
    registry: Registry,
    directory: _PinnedPath,
    command_id: UUID,
    *,
    require_current_witness: bool,
) -> Iterator[tuple[ScopeEnvelope, Callable[[], None]]]:
    from .monitor_control import _decode_publication

    name = _filename(command_id)
    data = _read_private(directory, name)
    if data is None:
        raise LedgerError("Grok mark proposal is unavailable")
    envelope = _decode_publication(name, data).command
    if (
        type(envelope) is not ScopeEnvelope
        or type(envelope.body.request) is not MarkRequest
    ):
        raise LedgerError("Grok hook requires an exact sealed mark proposal")
    request = envelope.body.request
    with (
        open_grant(registry, request.grant_id) as (grant, recheck_grant, _),
        pinned_destination(registry, request) as recheck_destination,
    ):

        def recheck():
            recheck_grant()
            if _read_private(directory, name) != data:
                raise ConflictError("Grok mark proposal changed")
            if recheck_destination is not None:
                recheck_destination()
            with open_grant(registry, request.grant_id) as (current, _, _):
                if seal_request(current, request) != envelope:
                    raise ConflictError("Grok mark grant changed")
                if require_current_witness:
                    require_witness(registry, current, datetime.now(UTC))

        if seal_request(grant, request) != envelope:
            raise LedgerError("Grok mark proposal seal changed")
        recheck()
        yield envelope, recheck
        recheck()


def scope_receipt_ref(evidence: _ServiceEvidence, command_id: UUID) -> SourceRef:
    return evidence.pseudonymize("scope-receipt", str(command_id))


@contextmanager
def grok_mark(
    writer: Registry,
    request: MarkRequest,
    source_id: UUID,
    checkout: Path,
) -> Iterator[Mark]:
    """Keep the original grant current through the coordinator's first application."""
    from .monitor_control import ControlInbox

    lease = writer.lease
    with (
        ControlInbox(writer.root).publication() as locked,
        _pin_directory(writer.root) as root,
        _private_child(root, _GROK_RECEIPTS, create=False) as directory,
        _grok_mark_proposal(
            writer, locked.directory, request.command_id, require_current_witness=False
        ) as (envelope, _),
    ):
        if directory is None or envelope.body.request != request:
            raise LedgerError("Original Grok mark proposal is unavailable")
        evidence = _authority(writer, root)
        approved, source = _grok_approved_ref(writer, evidence, source_id)
        live = writer._require_live_source(approved)
        checkout_ref = _grok_checkout_ref(
            writer, evidence, request.scope.project_id, checkout
        )
        original = next(
            (
                item
                for item in _grok_receipts(directory, evidence)
                if item.command_id == request.command_id
            ),
            None,
        )
        if (
            original is None
            or original.prompt is None
            or original.proposal_digest != envelope.payload_digest
            or (
                original.source_id,
                original.source,
                original.profile,
                original.checkout,
            )
            != (source_id, source, live.profile.generation, checkout_ref)
        ):
            raise LedgerError("Original Grok mark receipt is unavailable")
        lease.check()
        yield Mark(
            request.command_id,
            request.scope,
            scope_receipt_ref(evidence, request.command_id),
            request.destination_binding,
        )
        lease.check()
        writer._require_live_source(approved, prior=live)


def _grok_process_ref(
    evidence: _ServiceEvidence, pid: int, started: datetime
) -> SourceRef:
    from .process_identity import process_reference_domain

    return evidence.pseudonymize(
        "grok-scope-process",
        f"{process_reference_domain()}{pid}:{started.astimezone(UTC).isoformat()}",
    )


def _grok_image_ref(evidence: _ServiceEvidence, executable: Path) -> SourceRef:
    info = executable.stat(follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or info.st_size > 256 * 1024 * 1024:
        raise LedgerError("Grok process image is not a bounded regular file")
    return evidence.pseudonymize(
        "grok-scope-image",
        f"{info.st_dev}:{info.st_ino}:{info.st_size}:{info.st_mtime_ns}",
    )


def _grok_checkout_ref(
    registry: Registry, evidence: _ServiceEvidence, project_id: UUID, checkout: Path
) -> SourceRef:
    physical = _directory(str(checkout))
    project = _project(registry.view(), project_id)
    if physical not in project.anchors:
        raise LedgerError("Grok scope checkout is outside the owner project")
    return evidence.pseudonymize(
        "grok-scope-checkout", f"{physical.identity[0]}:{physical.identity[1]}"
    )


def _grok_scope_refs(
    evidence: _ServiceEvidence, session: str, prompt: str | None = None
) -> tuple[SourceRef, SourceRef | None]:
    from .sources.grok import _uuid

    session_ref = evidence.pseudonymize("grok-scope-session", _uuid(session))
    prompt_ref = (
        None
        if prompt is None
        else evidence.pseudonymize(
            "grok-scope-prompt", f"{session_ref.value}:{_uuid(prompt)}"
        )
    )
    return session_ref, prompt_ref


def _grok_approved_ref(
    registry: Registry, evidence: _ServiceEvidence, source_id: UUID
) -> tuple[ApprovedSource, SourceRef]:
    approved = _source(registry.view(), source_id)
    if approved.approval.surface != NativeSurface.GROK_BUILD_MACOS:
        raise LedgerError("Grok scope marker requires its qualified carrier")
    _check_capture_root(approved.directory)
    approved_ref = evidence.pseudonymize(
        "grok-scope-source",
        _encode(approved.approval, type(approved.approval))
        + str(approved.directory.identity),
    )
    return approved, approved_ref


def stage_grok_attempt(
    writer: Registry,
    source_id: UUID,
    command_id: UUID,
    session: str,
    checkout: Path,
    pid: int,
) -> SourceRef:
    """Stage one already sealed owner mark for the qualified native launch."""
    from .monitor_control import ControlInbox
    from .process_identity import read_process_identity

    lease = writer.lease
    now = datetime.now(UTC)
    inbox = ControlInbox(writer.root)
    with inbox.publication() as locked, _pin_directory(writer.root) as root:
        evidence = _authority(writer, root)
        approved, source = _grok_approved_ref(writer, evidence, source_id)
        live = writer._require_live_source(approved)
        qualification_record = _grok_qualification_record_ref(root, evidence)
        writer._require_live_source(approved, prior=live)
        process = read_process_identity(pid)
        if process is None:
            raise LedgerError("Grok scope native process is unavailable")
        image = _grok_image_ref(evidence, process.executable)
        with process.executable.open("rb") as binary:
            digest = file_digest(binary, "sha256").hexdigest()
        if (
            evidence.pseudonymize("isolated-executable-v1", digest)
            != live.installation.executable
            or _grok_image_ref(evidence, process.executable) != image
        ):
            raise LedgerError("Grok scope native process image changed")
        session_ref, _ = _grok_scope_refs(evidence, session)
        with (
            _grok_mark_proposal(
                writer, locked.directory, command_id, require_current_witness=True
            ) as (
                envelope,
                recheck,
            ),
            _private_child(root, _GROK_RECEIPTS, create=True) as directory,
        ):
            assert directory is not None
            request = envelope.body.request
            checkout_ref = _grok_checkout_ref(
                writer, evidence, request.scope.project_id, checkout
            )
            attempts = _grok_receipts(directory, evidence)
            draft = _GrokScopeAttempt(
                evidence.pseudonymize("grok-scope-attempt", uuid4().hex),
                command_id,
                envelope.payload_digest,
                source_id,
                source,
                live.profile.generation,
                qualification_record,
                checkout_ref,
                session_ref,
                _grok_process_ref(evidence, pid, process.started),
                image,
                now + WITNESS_LIFETIME,
            )
            prior = next(
                (item for item in attempts if item.command_id == command_id), None
            )
            if prior is not None:
                if prior != replace(
                    draft,
                    selector=prior.selector,
                    expires=prior.expires,
                    prompt=prior.prompt,
                ):
                    raise ConflictError(
                        "Grok scope mark already belongs to another attempt"
                    )
                if prior.prompt is None and now >= prior.expires:
                    raise LedgerError("Grok scope attempt expired")
                return prior.selector
            if any(
                item.session == session_ref
                and item.prompt is None
                and now < item.expires
                for item in attempts
            ):
                raise ConflictError(
                    "A Grok scope attempt is already pending for this session"
                )

            def confirm():
                recheck()
                lease.check()
                writer._require_live_source(approved, prior=live)
                if (
                    _grok_qualification_record_ref(root, evidence)
                    != qualification_record
                ):
                    raise LedgerError("Grok qualification revision changed")
                writer._require_live_source(approved, prior=live)
                if (
                    read_process_identity(pid) != process
                    or _grok_image_ref(evidence, process.executable) != image
                    or _grok_checkout_ref(
                        writer, evidence, request.scope.project_id, checkout
                    )
                    != checkout_ref
                ):
                    raise LedgerError("Staged Grok scope custody changed")

            _store_grok_receipts(directory, evidence, (*attempts, draft), confirm)
            lease.check()
            return draft.selector


def bind_grok_prompt(
    root_path: Path,
    selector: SourceRef,
    session: str,
    prompt: str,
    checkout: Path,
) -> SourceRef:
    """The native hook binds its one staged receipt without a coordinator lease."""
    from .monitor_control import ControlInbox
    from .sources.grok_scope_hook import _has_process_ancestor

    registry = Registry(root_path)
    now = datetime.now(UTC)
    with (
        ControlInbox(registry.root).publication() as locked,
        _pin_directory(registry.root) as root,
        _private_child(root, _GROK_RECEIPTS, create=False) as directory,
    ):
        evidence = _authority(registry, root)
        evidence.validate_source_ref(selector)
        session_ref, prompt_ref = _grok_scope_refs(evidence, session, prompt)
        if directory is None:
            raise LedgerError("Staged Grok scope attempt is unavailable")
        attempts = _grok_receipts(directory, evidence)
        attempt = next((item for item in attempts if item.selector == selector), None)
        if (
            attempt is None
            or attempt.session != session_ref
            or (attempt.prompt is None and now >= attempt.expires)
        ):
            raise LedgerError("Staged Grok scope attempt is unavailable")
        if attempt.prompt is not None and attempt.prompt != prompt_ref:
            raise ConflictError("Grok scope attempt already belongs to another prompt")
        with _grok_mark_proposal(
            registry,
            locked.directory,
            attempt.command_id,
            require_current_witness=attempt.prompt is None,
        ) as (envelope, recheck):
            project_id = envelope.body.request.scope.project_id

            def confirm():
                recheck()
                _, source = _grok_approved_ref(registry, evidence, attempt.source_id)
                if (
                    source != attempt.source
                    or envelope.payload_digest != attempt.proposal_digest
                    or _grok_checkout_ref(registry, evidence, project_id, checkout)
                    != attempt.checkout
                    or not _has_process_ancestor(
                        evidence, attempt.process, attempt.image
                    )
                ):
                    raise LedgerError("Staged Grok scope hook custody changed")
                if (
                    _grok_qualification_record_ref(root, evidence)
                    != attempt.qualification_record
                ):
                    raise LedgerError("Grok qualification revision changed")

            confirm()
            if attempt.prompt is None:
                if any(
                    item.session == session_ref and item.prompt == prompt_ref
                    for item in attempts
                ):
                    raise ConflictError("Grok prompt already has an owner receipt")
                updated = tuple(
                    replace(item, prompt=prompt_ref) if item is attempt else item
                    for item in attempts
                )
                _store_grok_receipts(directory, evidence, updated, confirm)
            return scope_receipt_ref(evidence, attempt.command_id)


def grok_receipt_lookup(
    writer: Registry, source_id: UUID, checkout: Path
) -> Callable[[str, str, str], SourceRef | None]:
    """Bind a pure native receipt lookup to the current qualified writer."""
    from .monitor_control import INBOX_NAME

    lease = writer.lease

    def find(session: str, prompt: str, _event_id: str) -> SourceRef | None:
        try:
            lease.check()
            with (
                _pin_directory(writer.root) as root,
                _private_child(root, _GROK_RECEIPTS, create=False) as directory,
                _private_child(root, INBOX_NAME, create=False) as inbox,
            ):
                if directory is None or inbox is None:
                    return None
                evidence = _authority(writer, root)
                session_ref, prompt_ref = _grok_scope_refs(evidence, session, prompt)
                approved, source = _grok_approved_ref(writer, evidence, source_id)
                live = writer._require_live_source(approved)
                matching = tuple(
                    attempt
                    for attempt in _grok_receipts(directory, evidence)
                    if (attempt.session, attempt.prompt) == (session_ref, prompt_ref)
                )
                if len(matching) != 1:
                    return None
                (attempt,) = matching
                with _grok_mark_proposal(
                    writer, inbox, attempt.command_id, require_current_witness=False
                ) as (envelope, _):
                    project_id = envelope.body.request.scope.project_id
                    current = _grok_checkout_ref(writer, evidence, project_id, checkout)
                    if (
                        (attempt.source_id, attempt.source, attempt.profile)
                        != (source_id, source, live.profile.generation)
                        or current != attempt.checkout
                        or envelope.payload_digest != attempt.proposal_digest
                    ):
                        return None
                    writer._require_live_source(approved, prior=live)
                    return scope_receipt_ref(evidence, attempt.command_id)
        except (LedgerError, OSError, ValueError):
            return None

    return find
