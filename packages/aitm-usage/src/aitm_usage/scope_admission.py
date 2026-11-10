"""Private scope-producer grants and typed monitor proposals."""

import hmac
import os
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid5

from .ledger import (
    Ledger,
    LedgerError,
    _path_exists,
    _pin_directory,
    _PinnedPath,
)
from .monitor_registry import (
    _SOURCE_KEY_FILE,
    Registry,
    _directory,
    _PhysicalDirectory,
    _project,
    _ServiceEvidence,
)
from .monitor_scope import Scope
from .scopes import _private_child, _publish, _read_private
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
