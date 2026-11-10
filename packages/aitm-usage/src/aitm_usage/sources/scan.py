"""Confinement, continuity and segment admission for local provider JSONL."""

import errno
import hashlib
import json
import os
import stat
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID

from ..ledger import Ledger, LedgerError
from ..monitor_types import NativeSurface
from ..scopes import BoundaryEvidence, session_reference
from ..types import (
    ClientVersion,
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    LedgerView,
    Provider,
    ProviderCheckpoint,
    Registration,
    ScopeEnrollment,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    UsageObservation,
    normalize_client_version,
)

_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
_FILE_FLAGS = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
_SUPPORTED_CLIENTS = {
    Provider.CODEX: ClientVersion.CODEX_0_167_0_ALPHA_3_2,
    Provider.CLAUDE: ClientVersion.CLAUDE_2_1_318,
}
_CLAUDE_SESSION_ROWS = {"user", "assistant", "system", "result", "rate_limit_event"}
_CLAUDE_QUEUE_FIELDS = {
    "type": str,
    "operation": str,
    "timestamp": str,
    "sessionId": str,
}
_CLAUDE_STARTUP_ATTACHMENT_FIELDS = {
    "type": str,
    "attachment": dict,
    "cwd": str,
    "entrypoint": str,
    "gitBranch": str,
    "isSidechain": bool,
    "sessionId": str,
    "timestamp": str,
    "userType": str,
    "uuid": str,
    "version": str,
}
_CLAUDE_STARTUP_HOOK_FIELDS = {
    "type": str,
    "hookEvent": str,
    "hookName": str,
    "toolUseID": str,
}
_CLAUDE_BOOKKEEPING = {
    "api-request-blob": ("hash", str),
    "atis-latch": ("atis", str),
    "last-prompt": ("lastPrompt", str),
    "tools-used": ("tools", list),
    "mode": ("mode", str),
}
_CLAUDE_COST_COUNTS = (
    "inputTokens",
    "outputTokens",
    "cacheReadInputTokens",
    "cacheCreationInputTokens",
    "cacheCreationEphemeral5mInputTokens",
    "cacheCreationEphemeral1hInputTokens",
)
_MAX_ROW_BYTES = 16 * 1024 * 1024
_READ_CHUNK = 64 * 1024
type _Row = dict[str, object]
type _FileID = tuple[int, int, int]


class SourceEvidence(Protocol):
    """Read authority for native prefixes and keyed source identifiers."""

    def pseudonymize(self, namespace: str, raw_reference: str) -> SourceRef: ...

    def validate_source_ref(self, reference: SourceRef) -> None: ...

    def as_of(self) -> LedgerView: ...


class SourceConfiguration(Protocol):
    """The scanner only needs source paths, checkout anchors and a namespace."""

    project_id: UUID
    source_roots: tuple[Path, ...]
    checkout_anchors: tuple[Path, ...]
    cutoff: datetime


class CoverageKind(StrEnum):
    CLOSED_TURN = "closed-turn"
    RECOGNIZED_USAGE = "recognized-usage"
    UNFAMILIAR_USAGE = "unfamiliar-usage"
    IN_FLIGHT_CUTOFF = "in-flight-cutoff"


@dataclass(frozen=True, slots=True)
class FrameClassification:
    """Adapter-supplied coverage evidence for a stable scanner ordinal."""

    ordinal: int
    kind: CoverageKind
    turn_ref: SourceRef | None = None

    def __post_init__(self) -> None:
        if (
            type(self.ordinal) is not int
            or not 0 <= self.ordinal < 2**63
            or type(self.kind) is not CoverageKind
            or (self.turn_ref is not None and type(self.turn_ref) is not SourceRef)
            or (
                self.kind in (CoverageKind.CLOSED_TURN, CoverageKind.RECOGNIZED_USAGE)
                and self.turn_ref is None
            )
        ):
            raise ValueError("Invalid source coverage classification")


@dataclass(frozen=True, slots=True)
class SourceFrame:
    """One complete row. The provider record is private, transient adapter input."""

    provider: Provider
    session_ref: SourceRef
    stream_ref: SourceRef
    ordinal: int
    observed_at: datetime
    client_version: ClientVersion
    format_version: int
    segment_ref: SourceRef
    anchor_ref: SourceRef | None
    pre_cutoff: bool
    row: _Row = field(repr=False, compare=False)
    eligibility: Eligibility = Eligibility.UNKNOWN
    boundary_only: bool = False
    _prefix: str = field(repr=False, compare=False, default="")


class SidebandKind(StrEnum):
    COST_STATE = "cost-state"
    SESSION_OWNER = "session-owner"


_CLAUDE_UNTIMED = _CLAUDE_BOOKKEEPING.keys() | {kind.value for kind in SidebandKind}


@dataclass(frozen=True, slots=True)
class SidebandFrame:
    """Untimed Claude metadata with the nearest preceding timed context, if any."""

    kind: SidebandKind
    provider: Provider
    session_ref: SourceRef
    stream_ref: SourceRef
    ordinal: int
    segment_ref: SourceRef | None
    timed_ordinal: int | None
    content: _Row = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class FrameBatch:
    """Look-ahead and an independent commit frontier from one verified snapshot.

    Adapters inspect frames for boundaries and use commit_frames for timed
    usage. Commit-sideband records have an eligible timed predecessor within
    the same frontier. Historical predecessors require durable usage evidence
    in the same segment. Sideband may only reconcile already eligible prefixes.
    Reapply current accepted enrollments and rescan before committing, including
    after a checkout becomes registered. Publish cursor, adapter state and
    observations together through Ledger.apply with the exact prior checkpoint.
    """

    frames: tuple[SourceFrame, ...] = ()
    commit_frames: tuple[SourceFrame, ...] = ()
    cursor: SourceCursor | None = None
    provider_checkpoint: ProviderCheckpoint | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    observed_through: datetime | None = None
    sideband: tuple[SidebandFrame, ...] = ()
    commit_sideband: tuple[SidebandFrame, ...] = ()
    _prior_checkout: tuple[tuple[int, SourceRef], ...] = field(
        default=(), repr=False, compare=False
    )

    def _matching_frame(self, boundary: SourceBoundary) -> SourceFrame | None:
        matches = [
            frame
            for frame in self.frames
            if (
                frame.provider is boundary.provider
                and frame.session_ref == boundary.session_ref
                and frame.stream_ref == boundary.stream_ref
                and frame.ordinal == boundary.ordinal
            )
        ]
        return matches[0] if len(matches) == 1 else None

    def scope_evidence(self, boundary: SourceBoundary) -> BoundaryEvidence | None:
        """Join an adapter-proven boundary to its exact scanner frame."""
        frame = self._matching_frame(boundary)
        return None if frame is None else BoundaryEvidence(boundary, frame.anchor_ref)

    def coverage(
        self,
        classifications: Iterable[FrameClassification],
        *,
        previously_recognized: Iterable[SourceRef] = (),
    ) -> tuple[Diagnostic, ...]:
        """Project bounded adapter classifications for eligible committed rows.

        Supply already recognized turn references when a turn spans batches.
        U03 relies on the adapters for real turn and activation-span semantics.
        """
        frames = {
            frame.ordinal: frame
            for frame in self.commit_frames
            if frame.eligibility is Eligibility.ELIGIBLE
        }
        current = {entry for entry in classifications if entry.ordinal in frames}
        recognized = set(previously_recognized)
        recognized.update(
            entry.turn_ref
            for entry in current
            if entry.kind is CoverageKind.RECOGNIZED_USAGE
        )
        gaps = set()
        for entry in current:
            if entry.kind is CoverageKind.UNFAMILIAR_USAGE:
                gaps.add((entry.ordinal, DiagnosticCode.UNKNOWN_USAGE))
            elif entry.kind is CoverageKind.IN_FLIGHT_CUTOFF or (
                entry.kind is CoverageKind.CLOSED_TURN
                and entry.turn_ref not in recognized
            ):
                gaps.add((entry.ordinal, DiagnosticCode.COVERAGE_GAP))
        diagnostics = []
        for ordinal, code in sorted(gaps):
            frame = frames[ordinal]
            diagnostics.append(
                Diagnostic(
                    code, frame.observed_at, frame.provider, frame.stream_ref, ordinal
                )
            )
        return tuple(diagnostics)


@dataclass(frozen=True, slots=True)
class _Enrollment:
    scope: ScopeEnrollment
    prefix: str | None
    anchor_ref: SourceRef | None


@dataclass(frozen=True, slots=True)
class CandidateSource:
    """A rediscovered transcript and its project-authenticated public identity."""

    provider: Provider | None
    session_ref: SourceRef | None
    stream_ref: SourceRef
    locator_ref: SourceRef
    incarnation_ref: SourceRef
    _path: Path = field(repr=False, compare=False)
    _identity: tuple[_FileID, ...] = field(repr=False, compare=False)
    _registration: SourceConfiguration = field(repr=False, compare=False)
    _ledger: SourceEvidence = field(repr=False, compare=False)
    _enrollments: tuple[_Enrollment, ...] = field(repr=False, default=())
    _excluded: frozenset[SourceRef] = field(repr=False, default=frozenset())
    _native_surface: NativeSurface | None = field(
        repr=False, compare=False, default=None
    )
    _monitor: bool = field(repr=False, compare=False, default=False)

    def _matches(self, entry: SourceBoundary | SourceFrame) -> bool:
        return (
            entry.provider is self.provider
            and entry.session_ref == self.session_ref
            and entry.stream_ref == self.stream_ref
        )

    def with_enrollment(
        self,
        enrollment: ScopeEnrollment,
        *,
        batch: FrameBatch | None = None,
        evidence: BoundaryEvidence | None = None,
    ) -> "CandidateSource":
        """Select a verified U02 enrollment for the corresponding segment.

        If its boundary is beyond the durable cursor, pass fresh adapter
        evidence joined through batch.scope_evidence and the batch that produced
        it. The rescan verifies that the exact prefix through the boundary still
        matches before admitting usage. Fresh evidence may establish a checkout
        for an enrollment originally accepted without one. A verified committed
        prefix suffices for earlier boundaries.
        """
        if (
            type(enrollment) is not ScopeEnrollment
            or not self._matches(enrollment.boundary)
            or enrollment.marker.project_id != self._registration.project_id
            or not any(
                entry.record == enrollment for entry in self._ledger.as_of().current
            )
        ):
            raise ValueError("Expected a verified enrollment for this source")
        prefix = None
        anchor_ref = None
        if batch is not None or evidence is not None:
            if (
                batch is None
                or evidence is None
                or batch.scope_evidence(enrollment.boundary) != evidence
                or (
                    enrollment.anchor_ref is not None
                    and enrollment.anchor_ref != evidence.anchor_ref
                )
            ):
                raise ValueError("Expected fresh evidence for the verified enrollment")
            frame = batch._matching_frame(enrollment.boundary)
            assert frame is not None
            prefix = frame._prefix
            anchor_ref = evidence.anchor_ref
        updated = tuple(
            selector
            for selector in self._enrollments
            if selector.scope.boundary.ordinal != enrollment.boundary.ordinal
        )
        return replace(
            self, _enrollments=(*updated, _Enrollment(enrollment, prefix, anchor_ref))
        )

    def with_exclusion(self, frame: SourceFrame) -> "CandidateSource":
        """Resolve an unanchored segment that the caller knows is unrelated."""
        if not self._matches(frame) or frame.anchor_ref is not None:
            raise ValueError("Expected an unanchored segment for this source")
        return replace(self, _excluded=self._excluded | {frame.segment_ref})


@dataclass(frozen=True, slots=True)
class _Snapshot:
    identity: tuple[_FileID, ...]
    directory_ctimes: tuple[int, ...]
    stat: os.stat_result

    def same_path(self, other: "_Snapshot") -> bool:
        return (
            self.identity == other.identity
            and self.directory_ctimes == other.directory_ctimes
        )


class _ChangedSource(OSError):
    pass


class _CaptureDiscontinuity(ValueError):
    """A stable, authenticated source no longer has its prior physical prefix."""


@dataclass(frozen=True, slots=True)
class _CapturePosition:
    cursor: SourceCursor
    next_ordinal: int
    partial_ordinal: int | None
    provider: Provider
    native_surface: NativeSurface | None
    client_version: ClientVersion
    format_version: int


@dataclass(frozen=True, slots=True)
class _CaptureLocatorPresence:
    at_locator: bool
    same_incarnation: bool
    locator_size: int | None
    locator_is_original: bool
    prefix_changed: bool


class _SourceIssue(Exception):
    def __init__(self, code: DiagnosticCode):
        self.code = code


def _file_id(info: os.stat_result) -> _FileID:
    return info.st_dev, info.st_ino, getattr(info, "st_birthtime_ns", 0)


@contextmanager
def _directory(
    path: Path,
) -> Iterator[tuple[int, tuple[_FileID, ...], tuple[int, ...]]]:
    if not path.is_absolute() or ".." in path.parts:
        raise _ChangedSource
    fd = os.open(path.anchor, _DIRECTORY_FLAGS)
    try:
        info = os.fstat(fd)
        chain = [_file_id(info)]
        ctimes = [info.st_ctime_ns]
        for name in path.parts[1:]:
            child = os.open(name, _DIRECTORY_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
            info = os.fstat(fd)
            chain.append(_file_id(info))
            ctimes.append(info.st_ctime_ns)
        yield fd, tuple(chain), tuple(ctimes)
    finally:
        os.close(fd)


def _regular_info(directory: int, name: str) -> os.stat_result:
    info = os.stat(name, dir_fd=directory, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise _ChangedSource
    return info


def _probe(path: Path) -> _Snapshot:
    with _directory(path.parent) as (directory, chain, ctimes):
        info = _regular_info(directory, path.name)
        return _Snapshot((*chain, _file_id(info)), ctimes, info)


def _reprobe(path: Path) -> _Snapshot:
    try:
        return _probe(path)
    except OSError:
        raise _ChangedSource from None


@contextmanager
def _open_snapshot(
    path: Path, *, identity_prefix: tuple[_FileID, ...]
) -> Iterator[tuple[BinaryIO, _Snapshot]]:
    with _directory(path.parent) as (directory, chain, ctimes):
        info = _regular_info(directory, path.name)
        identity = (*chain, _file_id(info))
        if identity[: len(identity_prefix)] != identity_prefix:
            raise _ChangedSource
        fd = os.open(path.name, _FILE_FLAGS, dir_fd=directory)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        snapshot = _Snapshot(identity, ctimes, opened)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or _file_id(opened) != identity[-1]
            or not snapshot.same_path(_reprobe(path))
        ):
            raise _ChangedSource
        yield stream, snapshot


def _transcripts(directory: int, path: Path) -> Iterator[Path]:
    with os.scandir(directory) as entries:
        for entry in sorted(entries, key=lambda item: item.name):
            try:
                if entry.is_dir(follow_symlinks=False):
                    child = os.open(entry.name, _DIRECTORY_FLAGS, dir_fd=directory)
                    try:
                        yield from _transcripts(child, path / entry.name)
                    finally:
                        os.close(child)
                elif entry.name.endswith(".jsonl") and entry.is_file(
                    follow_symlinks=False
                ):
                    yield path / entry.name
            except OSError:
                continue


def _locator_reference(evidence: SourceEvidence, path: Path) -> SourceRef:
    return evidence.pseudonymize("source-locator", os.fsencode(path).hex())


def _incarnation_reference(evidence: SourceEvidence, identity: _FileID) -> SourceRef:
    return evidence.pseudonymize("source-incarnation", ":".join(map(str, identity)))


def _directory_witness(info: os.stat_result) -> tuple[_FileID, int, int]:
    return _file_id(info), info.st_mtime_ns, info.st_ctime_ns


def _capture_locator_presence(
    root: Path,
    evidence: SourceEvidence,
    locator_ref: SourceRef,
    incarnation_ref: SourceRef,
    *,
    root_identity: tuple[int, ...] | None = None,
    prior: SourceCursor | None = None,
) -> _CaptureLocatorPresence:
    """Check absence by metadata and optionally reprove the one exact prior file."""
    evidence.validate_source_ref(locator_ref)
    evidence.validate_source_ref(incarnation_ref)
    if prior is not None:
        if (prior.locator_ref, prior.incarnation_ref) != (locator_ref, incarnation_ref):
            raise ValueError("Expected the exact prior native locator")
        evidence.validate_source_ref(prior.source_ref)
        evidence.validate_source_ref(prior.anchor_ref)
    directories = {}
    locator = None
    same_incarnation = False
    prefix_changed = False
    with _directory(root) as (root_fd, root_chain, root_ctimes):
        if root_identity is not None and root_chain[-1][:2] != root_identity:
            raise _ChangedSource
        pending = [(root, _directory_witness(os.fstat(root_fd)))]
        while pending:
            path, expected = pending.pop()
            with _directory(path) as (fd, chain, _):
                if (
                    chain[: len(root_chain)] != root_chain
                    or _directory_witness(os.fstat(fd)) != expected
                ):
                    raise _ChangedSource
                directories[path] = expected
                with os.scandir(fd) as entries:
                    for entry in sorted(
                        entries, key=lambda item: item.name, reverse=True
                    ):
                        child = path / entry.name
                        info = entry.stat(follow_symlinks=False)
                        if stat.S_ISDIR(info.st_mode):
                            pending.append((child, _directory_witness(info)))
                        if _locator_reference(evidence, child) == locator_ref:
                            locator = child, info
                        if (
                            stat.S_ISREG(info.st_mode)
                            and _incarnation_reference(evidence, _file_id(info))
                            == incarnation_ref
                        ):
                            same_incarnation = True

        locator_size = None
        locator_is_original = False
        if locator is not None:
            path, original = locator
            with _directory(path.parent) as (parent, chain, _):
                current = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                if (
                    chain[: len(root_chain)] != root_chain
                    or _file_id(current) != _file_id(original)
                    or current.st_mode != original.st_mode
                    or _mtime(current) != _mtime(original)
                ):
                    raise _ChangedSource
                if stat.S_ISREG(current.st_mode):
                    locator_size = current.st_size
                    locator_is_original = (
                        _incarnation_reference(evidence, _file_id(current))
                        == incarnation_ref
                    )
                    if (
                        locator_is_original
                        and prior is not None
                        and 0 < prior.offset <= current.st_size
                    ):
                        with _open_snapshot(
                            path, identity_prefix=(*chain, _file_id(current))
                        ) as (
                            stream,
                            snapshot,
                        ):
                            digest = _hash_prefix(stream, prior.offset)
                            _verify_snapshot(
                                stream, path, snapshot, prior.offset, digest
                            )
                        prefix_changed = (
                            _source_prefix_reference(
                                evidence, prior.source_ref, prior.offset, digest
                            )
                            != prior.anchor_ref
                        )
        # Check the entire walk, including earlier siblings, after enumeration.
        for path, expected in directories.items():
            with _directory(path) as (fd, chain, ctimes):
                if (
                    chain[: len(root_chain)] != root_chain
                    or ctimes[: len(root_ctimes)] != root_ctimes
                    or _directory_witness(os.fstat(fd)) != expected
                ):
                    raise _ChangedSource
    return _CaptureLocatorPresence(
        locator is not None,
        same_incarnation,
        locator_size,
        locator_is_original,
        prefix_changed,
    )


def _unique_fields(pairs: list[tuple[str, object]]) -> _Row:
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("Duplicate source fields")
    return fields


def _nonfinite(_: str) -> None:
    raise ValueError("Nonfinite source number")


def _decode_row(raw: bytes) -> _Row | None:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_fields,
            parse_constant=_nonfinite,
        )
    except (ValueError, RecursionError):
        return None
    if not isinstance(value, dict) or type(value.get("type")) is not str:
        return None
    return value


def _codex_payload(row: _Row) -> _Row | None:
    payload = row.get("payload")
    return payload if isinstance(payload, dict) else None


def _session(
    ledger: SourceEvidence, provider: Provider, raw: object
) -> SourceRef | None:
    if type(raw) is not str:
        return None
    try:
        return session_reference(ledger, provider, raw)
    except ValueError:
        return None


def _claude_session(row: _Row, ledger: SourceEvidence) -> SourceRef | None:
    references = {
        _session(ledger, Provider.CLAUDE, row[key])
        for key in ("sessionId", "session_id")
        if key in row
    }
    return next(iter(references)) if len(references) == 1 else None


@dataclass(frozen=True, slots=True)
class _Origin:
    provider: Provider | None
    session_ref: SourceRef | None
    client: ClientVersion = ClientVersion.UNKNOWN
    format: int | None = None
    issue: DiagnosticCode | None = None
    startup_ordinal: int = field(default=0, compare=False)
    startup_digest: str = field(default="", compare=False)
    startup_excluded: tuple[int, ...] = ()
    native_surface: NativeSurface | None = field(default=None, compare=False)


def _origin_from(row: _Row, ordinal: int, ledger: SourceEvidence) -> _Origin | None:
    kind = row["type"]
    surface = None
    if kind == "session_meta" and ordinal == 0:
        provider = Provider.CODEX
        metadata = _codex_payload(row) or {}
        session = _session(ledger, provider, metadata.get("id"))
        raw_client = metadata.get("cli_version")
        if (
            metadata.get("originator") == "Codex Desktop"
            and metadata.get("source") == "vscode"
        ):
            surface = NativeSurface.CODEX_DESKTOP_MACOS
    elif kind in _CLAUDE_SESSION_ROWS and ("sessionId" in row or "session_id" in row):
        provider = Provider.CLAUDE
        metadata = row
        session = _claude_session(row, ledger)
        raw_client = row.get("version")
        if "sessionId" in row:
            surface = NativeSurface.CLAUDE_CODE_MACOS
    else:
        return None
    client = normalize_client_version(raw_client)
    formats = [
        entry["format_version"]
        for entry in (row, metadata)
        if "format_version" in entry
    ]
    if session is None:
        return _Origin(provider, None, issue=DiagnosticCode.IDENTITY_CONFLICT)
    if client is not _SUPPORTED_CLIENTS[provider] or any(
        type(version) is not int or version != 1 for version in formats
    ):
        return _Origin(
            provider, session, client, issue=DiagnosticCode.UNSUPPORTED_FORMAT
        )
    return _Origin(provider, session, client, 1, native_surface=surface)


def _closed_fields(row: _Row, fields: dict[str, type]) -> bool:
    return row.keys() == fields.keys() and all(
        type(row[key]) is expected for key, expected in fields.items()
    )


def _native_uuid(value: object) -> UUID | None:
    if type(value) is str:
        try:
            return UUID(value)
        except ValueError:
            pass
    return None


def _claude_startup_root(row: _Row) -> bool:
    return (
        row.get("entrypoint") == "sdk-cli"
        and row.get("userType") == "external"
        and row.get("isSidechain") is False
        and row.get("parent_tool_use_id") is None
    )


def _claude_startup_attachment(
    row: _Row, client: ClientVersion, parent: UUID | None
) -> UUID | None:
    if parent is None:
        top = _CLAUDE_STARTUP_ATTACHMENT_FIELDS | {"parentUuid": type(None)}
        nested = _CLAUDE_STARTUP_HOOK_FIELDS | {
            "command": str,
            "content": str,
            "stdout": str,
            "stderr": str,
            "durationMs": int,
            "exitCode": int,
        }
        kind = "hook_success"
    else:
        top = _CLAUDE_STARTUP_ATTACHMENT_FIELDS | {
            "parentUuid": str,
            "rendered": list,
            "renderedRole": str,
        }
        nested = _CLAUDE_STARTUP_HOOK_FIELDS | {"content": list}
        kind = "hook_additional_context"
    if (
        not _closed_fields(row, top)
        or row["type"] != "attachment"
        or not _claude_startup_root(row)
        or row["version"] != client.value
        or _native_uuid(row["parentUuid"]) != parent
    ):
        return None
    hook = row["attachment"]
    if (
        not _closed_fields(hook, nested)
        or hook["type"] != kind
        or hook["hookEvent"] != "SessionStart"
    ):
        return None
    return _native_uuid(row["uuid"])


def _claude_startup_ordinals(
    preceding: list[tuple[int, _Row | None]],
    user: _Row,
    origin: _Origin,
    ledger: SourceEvidence,
) -> tuple[int, ...]:
    if (
        origin.provider is not Provider.CLAUDE
        or origin.issue is not None
        or len(preceding) < 4
        or user["type"] != "user"
        or type(user.get("sessionId")) is not str
        or not _claude_startup_root(user)
        or _moment(user) is None
    ):
        return ()
    user_id = _native_uuid(user.get("uuid"))
    message = user.get("message")
    if (
        user_id is None
        or type(message) is not dict
        or message.get("role") != "user"
        or type(message.get("content")) not in (str, list)
    ):
        return ()

    timed = []
    for ordinal, row in preceding:
        if row is None or _claude_session(row, ledger) != origin.session_ref:
            return ()
        if row["type"] in _CLAUDE_UNTIMED:
            try:
                _claude_sideband_content(row, ledger)
            except ValueError:
                return ()
            continue
        if _moment(row) is None:
            return ()
        timed.append((ordinal, row))
    if len(timed) != 4:
        return ()

    enqueue, dequeue, success, additional = (row for _, row in timed)
    if (
        not _closed_fields(enqueue, _CLAUDE_QUEUE_FIELDS | {"content": str})
        or enqueue["type"] != "queue-operation"
        or enqueue["operation"] != "enqueue"
        or not _closed_fields(dequeue, _CLAUDE_QUEUE_FIELDS)
        or dequeue["type"] != "queue-operation"
        or dequeue["operation"] != "dequeue"
    ):
        return ()
    success_id = _claude_startup_attachment(success, origin.client, None)
    if success_id is None:
        return ()
    additional_id = _claude_startup_attachment(additional, origin.client, success_id)
    if (
        additional_id is None
        or len({user_id, success_id, additional_id}) != 3
        or _native_uuid(user.get("parentUuid")) != additional_id
    ):
        return ()
    return tuple(ordinal for ordinal, _ in timed)


def _origin(stream: BinaryIO, size: int, ledger: SourceEvidence) -> _Origin | None:
    """Look for startup identity without following arbitrary transcript fields."""
    found_complete = False
    digest = hashlib.sha256()
    preceding = []
    # Claude can place bookkeeping rows ahead of the first session-bearing row.
    limit = min(size, _MAX_ROW_BYTES)
    for ordinal in range(64):
        if stream.tell() >= limit:
            break
        raw = stream.readline(limit - stream.tell())
        if not raw.endswith(b"\n"):
            break
        found_complete = True
        digest.update(raw)
        row = _decode_row(raw)
        if (
            row is not None
            and (origin := _origin_from(row, ordinal, ledger)) is not None
        ):
            return replace(
                origin,
                startup_ordinal=ordinal,
                startup_digest=digest.hexdigest(),
                startup_excluded=_claude_startup_ordinals(
                    preceding, row, origin, ledger
                ),
            )
        preceding.append((ordinal, row))
    if found_complete or size > limit:
        return _Origin(None, None, issue=DiagnosticCode.UNSUPPORTED_FORMAT)
    return None


def discover(registration: Registration) -> Iterator[CandidateSource]:
    """Enumerate regular JSONL files under explicit roots without symlink traversal.

    Supply the latest checkpoint for each stream_ref when scanning rediscovered
    candidates. Also compare locator_ref to detect replacement at a known path.
    """
    ledger = Ledger.open(registration.state_root, registration.project_id)
    yield from _discover_sources(registration, ledger)


def _discover_sources(
    registration: SourceConfiguration, ledger: SourceEvidence
) -> Iterator[CandidateSource]:
    seen = set()
    for root in registration.source_roots:
        try:
            with _directory(root) as (directory, chain, _):
                for path in _transcripts(directory, root):
                    if path in seen:
                        continue
                    try:
                        with _open_snapshot(path, identity_prefix=chain) as (
                            stream,
                            snapshot,
                        ):
                            origin = _origin(stream, snapshot.stat.st_size, ledger)
                            if not snapshot.same_path(_probe(path)):
                                continue
                    except OSError:
                        continue
                    if origin is None:
                        continue
                    seen.add(path)
                    locator = _locator_reference(ledger, path)
                    incarnation = _incarnation_reference(ledger, snapshot.identity[-1])
                    stream_ref = (
                        ledger.pseudonymize(
                            f"{origin.provider.value}-stream", origin.session_ref.value
                        )
                        if origin.session_ref is not None
                        and origin.provider is not None
                        else locator
                    )
                    yield CandidateSource(
                        origin.provider,
                        origin.session_ref,
                        stream_ref,
                        locator,
                        incarnation,
                        path,
                        snapshot.identity,
                        registration,
                        ledger,
                        _native_surface=origin.native_surface,
                    )
        except OSError:
            continue


def checkout_anchor_reference(ledger: SourceEvidence, path: Path) -> SourceRef:
    """Use the scanner's checkout namespace for U02 bindings and registration."""
    return ledger.pseudonymize("checkout-anchor", os.fsencode(path).hex())


def _moment(row: _Row) -> datetime | None:
    raw = row.get("timestamp")
    if type(raw) is not str:
        return None
    try:
        moment = datetime.fromisoformat(raw)
        if moment.utcoffset() is not None:
            return moment.astimezone(UTC)
    except (ValueError, OverflowError):
        pass
    return None


def _checkout_path(raw: object) -> Path | None:
    if type(raw) is not str or not raw or "\0" in raw:
        return None
    path = Path(raw)
    if path.is_absolute() and ".." not in path.parts:
        return path
    return None


def _checkout_anchor(
    cwd: Path | None, source: CandidateSource
) -> tuple[SourceRef, _FileID] | None:
    if cwd is None:
        return None
    for anchor in sorted(
        source._registration.checkout_anchors,
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if not anchor.is_absolute() or not cwd.is_relative_to(anchor):
            continue
        try:
            if (
                anchor.resolve(strict=True) == anchor
                and cwd.is_dir()
                and cwd.resolve(strict=True).is_relative_to(anchor)
            ):
                info = anchor.stat(follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    return checkout_anchor_reference(source._ledger, anchor), _file_id(
                        info
                    )
        except (OSError, RuntimeError, ValueError):
            continue
    return None


@dataclass(frozen=True, slots=True)
class _Segment:
    cwd: Path | None = field(repr=False)
    ref: SourceRef
    start_ordinal: int
    checkout: tuple[SourceRef, _FileID] | None

    @property
    def anchor(self) -> SourceRef | None:
        return self.checkout[0] if self.checkout is not None else None


def _segment(
    source: CandidateSource, cwd: Path | None, ordinal: int, prefix: str
) -> _Segment:
    ref = source._ledger.pseudonymize(
        "source-segment", f"{source.stream_ref.value}:{ordinal}:{prefix}"
    )
    return _Segment(cwd, ref, ordinal, _checkout_anchor(cwd, source))


def _row_context(
    row: _Row, ordinal: int, source: CandidateSource, origin: _Origin
) -> tuple[DiagnosticCode | None, bool, Path | None]:
    kind = row["type"]
    if origin.provider is Provider.CODEX:
        metadata = _codex_payload(row)
        if metadata is None:
            return DiagnosticCode.MALFORMED_USAGE, False, None
        if kind == "session_meta" and ordinal != 0:
            raise _SourceIssue(DiagnosticCode.IDENTITY_CONFLICT)
        updates = kind in ("session_meta", "turn_context")
    else:
        metadata = row
        if (
            kind in _CLAUDE_SESSION_ROWS
            or kind in _CLAUDE_UNTIMED
            or "sessionId" in row
            or "session_id" in row
        ):
            session = _claude_session(row, source._ledger)
            if session is None:
                return DiagnosticCode.IDENTITY_CONFLICT, False, None
            if session != source.session_ref:
                raise _SourceIssue(DiagnosticCode.IDENTITY_CONFLICT)
        if (
            "version" in row
            and normalize_client_version(row["version"]) is not origin.client
        ):
            raise _SourceIssue(DiagnosticCode.UNSUPPORTED_FORMAT)
        updates = kind in ("user", "assistant", "system") and "cwd" in metadata
    if any(
        type(entry["format_version"]) is not int or entry["format_version"] != 1
        for entry in (row, metadata)
        if "format_version" in entry
    ):
        raise _SourceIssue(DiagnosticCode.UNSUPPORTED_FORMAT)
    return None, updates, _checkout_path(metadata.get("cwd")) if updates else None


def _claude_sideband_content(row: _Row, ledger: SourceEvidence) -> _Row | None:
    if "timestamp" in row:
        raise ValueError("Native bookkeeping must be untimed")
    kind = row["type"]
    if kind in _CLAUDE_BOOKKEEPING:
        key, expected = _CLAUDE_BOOKKEEPING[kind]
        value = row.get(key)
        if type(value) is not expected:
            raise ValueError("Malformed native bookkeeping")
        if kind == "tools-used" and any(
            type(label) is not str or not label.strip() for label in value
        ):
            raise ValueError("Malformed native tool labels")
        return None
    if kind == SidebandKind.SESSION_OWNER:
        account = row.get("accountUuid")
        if type(account) is not str:
            raise ValueError("Missing native account identity")
        return {
            "account_ref": ledger.pseudonymize("claude-account", str(UUID(account)))
        }

    model_usage = row.get("modelUsage")
    if not isinstance(model_usage, dict):
        raise ValueError("Malformed native cost state")
    retained = {}
    for model, raw in model_usage.items():
        if not model or not isinstance(raw, dict):
            raise ValueError("Malformed native model usage")
        counts = {key: raw[key] for key in _CLAUDE_COST_COUNTS if key in raw}
        if not counts or any(
            type(value) is not int or not 0 <= value < 2**63
            for value in counts.values()
        ):
            raise ValueError("Malformed native token quantities")
        retained[model] = counts
    return {"modelUsage": retained}


@dataclass(frozen=True, slots=True)
class _SidebandRecord:
    frame: SidebandFrame
    context: SourceFrame | None
    segment_start: int | None


@dataclass(frozen=True, slots=True)
class _CompleteRow:
    start: int
    prefix_before: str
    frame: SourceFrame | _SidebandRecord | None
    diagnostic: Diagnostic | None


def _lines(
    stream: BinaryIO, size: int
) -> Iterator[tuple[int, int, str, str, _Row | None]]:
    """Yield complete records with prefix witnesses. Oversized rows are gaps."""
    digest = hashlib.sha256()
    start = 0
    ordinal = 0
    while start < size:
        before = digest.hexdigest()
        raw = stream.readline(min(_MAX_ROW_BYTES + 1, size - start))
        if not raw:
            break
        digest.update(raw)
        if len(raw) > _MAX_ROW_BYTES:
            while not raw.endswith(b"\n") and stream.tell() < size:
                raw = stream.readline(min(_READ_CHUNK, size - stream.tell()))
                if not raw:
                    break
                digest.update(raw)
            row = None
        else:
            row = _decode_row(raw) if raw.endswith(b"\n") else None
        if not raw.endswith(b"\n"):
            break
        yield ordinal, start, before, digest.hexdigest(), row
        start = stream.tell()
        ordinal += 1


def _prefix_chunks(stream: BinaryIO, size: int, *, offset: int = 0) -> Iterator[bytes]:
    while offset < size:
        # Read the descriptor directly so a buffered seek cannot reuse stale bytes.
        raw = os.pread(stream.fileno(), min(_READ_CHUNK, size - offset), offset)
        if not raw:
            raise _ChangedSource
        yield raw
        offset += len(raw)


def _hash_prefix(stream: BinaryIO, size: int) -> str:
    digest = hashlib.sha256()
    for raw in _prefix_chunks(stream, size):
        digest.update(raw)
    return digest.hexdigest()


def _mtime(info: os.stat_result) -> tuple[int, int, int]:
    return info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _verify_snapshot(
    stream: BinaryIO,
    path: Path,
    snapshot: _Snapshot,
    complete_size: int,
    prefix: str,
) -> None:
    after = os.fstat(stream.fileno())
    if (
        _file_id(after) != snapshot.identity[-1]
        or after.st_nlink != 1
        or after.st_size < snapshot.stat.st_size
    ):
        raise _ChangedSource
    if _mtime(after) != _mtime(snapshot.stat):
        if after.st_size == snapshot.stat.st_size:
            raise _ChangedSource
        # Providers may append while polled. Only the verified original prefix
        # participates in this snapshot. A changed existing row fails closed.
        if _hash_prefix(stream, complete_size) != prefix:
            raise _ChangedSource
    current = _reprobe(path)
    # A directory can be moved out and back with identical inodes at both
    # endpoints. Directory ctime witnesses apply only to this open snapshot.
    if not snapshot.same_path(current) or _mtime(current.stat) != _mtime(after):
        raise _ChangedSource


def _validation_ref(
    source: CandidateSource, origin: _Origin | None, offset: int, digest: str
) -> SourceRef:
    # The held zero-byte frontier still authenticates the observed origin.
    if offset == 0:
        if origin is None or not origin.startup_digest:
            raise _CaptureDiscontinuity("Private source origin is unavailable")
        return source._ledger.pseudonymize(
            "source-origin", f"{source.stream_ref.value}:{origin.startup_digest}"
        )
    return _source_prefix_reference(source._ledger, source.stream_ref, offset, digest)


def _source_prefix_reference(
    evidence: SourceEvidence,
    stream_ref: SourceRef,
    offset: int,
    digest: str,
) -> SourceRef:
    return evidence.pseudonymize(
        "source-prefix", f"{stream_ref.value}:{offset}:{digest}"
    )


def _within_source_roots(source: CandidateSource) -> bool:
    return any(
        root.is_absolute()
        and ".." not in root.parts
        and source._path.is_relative_to(root)
        for root in source._registration.source_roots
    )


def _capture_cursor_identity(source: CandidateSource, cursor: SourceCursor) -> None:
    for reference in (
        cursor.source_ref,
        cursor.locator_ref,
        cursor.incarnation_ref,
        cursor.anchor_ref,
    ):
        source._ledger.validate_source_ref(reference)
    if cursor.locator_ref != source.locator_ref:
        # Seeing the stream at another locator says nothing about the old one.
        raise _ChangedSource
    if (
        cursor.incarnation_ref != source.incarnation_ref
        or cursor.source_ref != source.stream_ref
    ):
        raise _CaptureDiscontinuity("Private source identity changed")


def _verify_capture_cursor(
    source: CandidateSource, origin: _Origin | None, cursor: SourceCursor, digest: str
) -> None:
    if _validation_ref(source, origin, cursor.offset, digest) != cursor.anchor_ref:
        raise _CaptureDiscontinuity("Private source prefix changed")


def _capture_extent(
    stream: BinaryIO, size: int, prior_offset: int
) -> tuple[str, str, int, int | None]:
    """Hash and count the same descriptor bytes, including the prior prefix."""
    digest = hashlib.sha256()
    witnesses = []
    complete = offset = 0
    last = b""
    for end in (prior_offset, size):
        for raw in _prefix_chunks(stream, end, offset=offset):
            digest.update(raw)
            complete += raw.count(b"\n")
            last = raw[-1:]
        witnesses.append(digest.hexdigest())
        offset = end
    prior_prefix, prefix = witnesses
    partial = complete if size and last != b"\n" else None
    return prior_prefix, prefix, complete, partial


def _capture_position(
    source: CandidateSource,
    prior: SourceCursor | None,
    *,
    fixed: SourceCursor | None = None,
) -> _CapturePosition:
    """Count physical rows through the present or already armed byte prefix."""
    if not _within_source_roots(source):
        raise _ChangedSource
    if fixed is not None and prior is not None and fixed.offset < prior.offset:
        raise ValueError("Private capture position precedes the authorized prefix")
    with _open_snapshot(source._path, identity_prefix=source._identity) as (
        stream,
        snapshot,
    ):
        if (
            _locator_reference(source._ledger, source._path) != source.locator_ref
            or _incarnation_reference(source._ledger, snapshot.identity[-1])
            != source.incarnation_ref
        ):
            raise ValueError("Invalid private capture source identity")
        for cursor in (prior, fixed):
            if cursor is not None:
                _capture_cursor_identity(source, cursor)
        size = snapshot.stat.st_size if fixed is None else fixed.offset
        required = max(size, prior.offset if prior is not None else 0)
        if snapshot.stat.st_size < required:
            current = _reprobe(source._path)
            if not snapshot.same_path(current) or current.stat.st_size >= required:
                raise _ChangedSource
            raise _CaptureDiscontinuity("Private source was truncated")

        # A zero-offset cursor can be authenticated only with its native startup.
        origin = _origin(stream, size or snapshot.stat.st_size, source._ledger)
        origin_size = stream.tell()
        prior_prefix, prefix, complete, partial = _capture_extent(
            stream, size, prior.offset if prior is not None else 0
        )
        if (
            origin is not None
            and origin.startup_digest
            and (_hash_prefix(stream, origin_size) != origin.startup_digest)
        ):
            raise _ChangedSource
        _verify_snapshot(stream, source._path, snapshot, size, prefix)
        if prior is not None:
            _verify_capture_cursor(source, origin, prior, prior_prefix)
        if fixed is not None:
            _verify_capture_cursor(source, origin, fixed, prefix)
        if (
            origin is None
            or origin.issue is not None
            or origin.provider is None
            or origin.session_ref is None
            or origin.format is None
            or (origin.provider, origin.session_ref, origin.native_surface)
            != (source.provider, source.session_ref, source._native_surface)
            or source._ledger.pseudonymize(
                f"{origin.provider.value}-stream", origin.session_ref.value
            )
            != source.stream_ref
        ):
            raise ValueError("Private native source origin is unavailable")
        cursor = SourceCursor(
            source.stream_ref,
            source.locator_ref,
            source.incarnation_ref,
            size,
            _validation_ref(source, origin, size, prefix),
        )
        return _CapturePosition(
            cursor,
            complete if partial is None else complete + 1,
            partial,
            origin.provider,
            origin.native_surface,
            origin.client,
            origin.format,
        )


def _prior_offset(source: CandidateSource, checkpoint: SourceCheckpoint | None) -> int:
    if checkpoint is None:
        return 0
    try:
        for reference in (
            checkpoint.cursor.source_ref,
            checkpoint.cursor.locator_ref,
            checkpoint.cursor.incarnation_ref,
            checkpoint.cursor.anchor_ref,
        ):
            source._ledger.validate_source_ref(reference)
    except LedgerError:
        raise _SourceIssue(DiagnosticCode.IDENTITY_CONFLICT) from None
    if (
        checkpoint.cursor.source_ref != source.stream_ref
        or checkpoint.provider.provider is not source.provider
    ):
        code = (
            DiagnosticCode.SOURCE_REPLACED
            if checkpoint.cursor.locator_ref == source.locator_ref
            else DiagnosticCode.IDENTITY_CONFLICT
        )
        raise _SourceIssue(code)
    if (
        checkpoint.cursor.offset == 0
        and checkpoint.cursor.incarnation_ref != source.incarnation_ref
    ):
        raise _SourceIssue(_continuity_issue(source, checkpoint.cursor))
    return checkpoint.cursor.offset


def _continuity_issue(source: CandidateSource, prior: SourceCursor) -> DiagnosticCode:
    if prior.locator_ref == source.locator_ref:
        return DiagnosticCode.SOURCE_REPLACED
    return DiagnosticCode.OVERLAP_UNVERIFIED


def _verify_prior(
    source: CandidateSource,
    origin: _Origin,
    checkpoint: SourceCheckpoint | None,
    offset: int,
    prefix: str,
) -> None:
    if checkpoint is None:
        return
    cursor = checkpoint.cursor
    if (
        offset == cursor.offset
        and _validation_ref(source, origin, offset, prefix) == cursor.anchor_ref
    ):
        return
    raise _SourceIssue(_continuity_issue(source, cursor))


def _verify_read_extent(
    stream: BinaryIO,
    snapshot: _Snapshot,
    source: CandidateSource,
    origin: _Origin,
    end: int,
    prefix: str,
    capture_limit: SourceCursor | None,
) -> None:
    if capture_limit is not None:
        # The framed rows omit a partial last row. The armed byte prefix includes it.
        captured = _hash_prefix(stream, capture_limit.offset)
        complete = (
            captured if end == capture_limit.offset else _hash_prefix(stream, end)
        )
        if complete != prefix:
            raise _ChangedSource
        _verify_capture_cursor(source, origin, capture_limit, captured)
        end, prefix = capture_limit.offset, captured
    _verify_snapshot(stream, source._path, snapshot, end, prefix)


def _read(
    stream: BinaryIO,
    snapshot: _Snapshot,
    source: CandidateSource,
    checkpoint: SourceCheckpoint | None,
    cutoff: datetime,
    capture_limit: SourceCursor | None,
) -> FrameBatch:
    prior = _prior_offset(source, checkpoint)
    size = snapshot.stat.st_size
    if capture_limit is not None:
        try:
            _capture_cursor_identity(source, capture_limit)
        except LedgerError:
            raise _SourceIssue(DiagnosticCode.IDENTITY_CONFLICT) from None
        if not prior <= capture_limit.offset <= size:
            raise _ChangedSource
        size = capture_limit.offset
    origin = _origin(stream, size or snapshot.stat.st_size, source._ledger)
    if origin is None or (origin.provider, origin.session_ref) != (
        source.provider,
        source.session_ref,
    ):
        raise _SourceIssue(DiagnosticCode.SOURCE_REPLACED)
    if origin.issue is not None:
        raise _SourceIssue(origin.issue)
    if source._monitor and origin.native_surface is not source._native_surface:
        raise _SourceIssue(DiagnosticCode.UNSUPPORTED_FORMAT)
    assert origin.provider is not None and origin.session_ref is not None
    assert origin.format is not None

    if checkpoint is not None and prior == size:
        prefix = _hash_prefix(stream, prior)
        _verify_prior(source, origin, checkpoint, prior, prefix)
        _verify_read_extent(
            stream, snapshot, source, origin, prior, prefix, capture_limit
        )
        return _project(source, checkpoint, origin, [], {}, {}, prior, prefix)

    stream.seek(0)
    records = []
    prior_ordinals = (
        {entry.ordinal for entry in checkpoint.provider.request_prefix}
        if source._monitor
        and origin.provider is Provider.CLAUDE
        and checkpoint is not None
        else set()
    )
    revision_checkouts = []
    segment = None
    last_timed = None
    checkouts: dict[Path, tuple[SourceRef, _FileID]] = {}
    selections = {entry.scope.boundary.ordinal: entry for entry in source._enrollments}
    admitted: dict[SourceRef, int] = {}
    pending: dict[SourceRef, int] = {}
    end = 0
    prefix = hashlib.sha256().hexdigest()
    prior_verified = origin_verified = False
    for ordinal, start, before, prefix, row in _lines(stream, size):
        end = stream.tell()
        if ordinal == origin.startup_ordinal:
            if prefix != origin.startup_digest:
                raise _ChangedSource
            origin_verified = True
        if start >= prior and not prior_verified:
            _verify_prior(source, origin, checkpoint, start, before)
            prior_verified = True
        selection = selections.pop(ordinal, None)
        moment = _moment(row) if row is not None else None
        issue, updates, cwd = (
            _row_context(row, ordinal, source, origin)
            if row is not None
            else (DiagnosticCode.MALFORMED_USAGE, False, None)
        )
        if ordinal in origin.startup_excluded:
            if selection is not None or issue is not None or moment is None:
                raise _SourceIssue(issue or DiagnosticCode.BOUNDARY_UNVERIFIED)
            continue
        if (
            row is not None
            and origin.provider is Provider.CLAUDE
            and row["type"] in _CLAUDE_UNTIMED
        ):
            moment = None
            if issue is None:
                if selection is not None:
                    raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
                try:
                    content = _claude_sideband_content(row, source._ledger)
                except ValueError:
                    issue = DiagnosticCode.MALFORMED_USAGE
                else:
                    if content is not None and start >= prior:
                        sideband = SidebandFrame(
                            SidebandKind(row["type"]),
                            origin.provider,
                            origin.session_ref,
                            source.stream_ref,
                            ordinal,
                            last_timed.segment_ref if last_timed is not None else None,
                            last_timed.ordinal if last_timed is not None else None,
                            content,
                        )
                        records.append(
                            _CompleteRow(
                                start,
                                before,
                                _SidebandRecord(
                                    sideband,
                                    last_timed,
                                    segment.start_ordinal
                                    if segment is not None
                                    else None,
                                ),
                                None,
                            )
                        )
                    continue
        if issue is None and moment is None:
            issue = DiagnosticCode.MALFORMED_USAGE
        if issue is not None:
            if selection is not None:
                raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
            segment = None
            last_timed = None
            if start >= prior:
                records.append(
                    _CompleteRow(
                        start,
                        before,
                        None,
                        Diagnostic(
                            issue,
                            moment or cutoff,
                            origin.provider,
                            source.stream_ref,
                            ordinal,
                        ),
                    )
                )
            continue
        if segment is None or (updates and cwd != segment.cwd):
            segment = _segment(source, cwd, ordinal, prefix)
            if cwd is not None and segment.checkout is not None:
                prior_checkout = checkouts.setdefault(cwd, segment.checkout)
                if prior_checkout != segment.checkout:
                    raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
        proof_gap = None
        if selection is not None:
            # The prior prefix is authenticated before this projection can
            # escape. Registration additions only affect proof for new rows.
            if end <= prior or (
                selection.anchor_ref == segment.anchor and selection.prefix == prefix
            ):
                admitted.setdefault(segment.ref, ordinal)
            else:
                pending.setdefault(segment.ref, ordinal)
                proof_gap = Diagnostic(
                    DiagnosticCode.BOUNDARY_UNVERIFIED,
                    moment or cutoff,
                    origin.provider,
                    source.stream_ref,
                    ordinal,
                )
        if start >= prior or origin.provider is Provider.CLAUDE:
            assert moment is not None and row is not None
            last_timed = SourceFrame(
                origin.provider,
                origin.session_ref,
                source.stream_ref,
                ordinal,
                moment,
                origin.client,
                origin.format,
                segment.ref,
                segment.anchor,
                moment < cutoff,
                row,
                _prefix=prefix,
            )
            if start >= prior:
                records.append(_CompleteRow(start, before, last_timed, proof_gap))
            elif ordinal in prior_ordinals and last_timed.anchor_ref is not None:
                revision_checkouts.append((ordinal, last_timed.anchor_ref))
    if origin.startup_excluded and not origin_verified:
        raise _ChangedSource
    if not prior_verified:
        _verify_prior(source, origin, checkpoint, end, prefix)
    if any(
        _checkout_anchor(cwd, source) != anchor for cwd, anchor in checkouts.items()
    ):
        raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
    _verify_read_extent(stream, snapshot, source, origin, end, prefix, capture_limit)
    if selections:
        raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
    result = _project(
        source, checkpoint, origin, records, admitted, pending, end, prefix
    )
    return (
        replace(result, _prior_checkout=tuple(revision_checkouts))
        if revision_checkouts
        else result
    )


def _eligibility(
    frame: SourceFrame,
    source: CandidateSource,
    admitted: dict[SourceRef, int],
    pending: dict[SourceRef, int],
) -> Eligibility:
    start = admitted.get(frame.segment_ref)
    unproven = pending.get(frame.segment_ref)
    if unproven is not None and (start is None or unproven <= frame.ordinal):
        return Eligibility.UNKNOWN
    if start is not None:
        allowed = frame.ordinal >= start
        return (
            Eligibility.ELIGIBLE
            if allowed and not frame.pre_cutoff
            else Eligibility.EXCLUDED
        )
    if frame.anchor_ref is not None:
        return Eligibility.EXCLUDED if frame.pre_cutoff else Eligibility.ELIGIBLE
    if frame.segment_ref in source._excluded:
        return Eligibility.EXCLUDED
    return Eligibility.UNKNOWN


def _durable_usage_ordinals(
    source: CandidateSource, checkpoint: SourceCheckpoint | None
) -> tuple[int, ...]:
    if checkpoint is None:
        return ()
    view = source._ledger.as_of()
    if checkpoint not in view.checkpoints:
        return ()
    ordinals = []
    for revision in view.current:
        record = revision.record
        if (
            isinstance(record, UsageObservation)
            and source._matches(record.boundary)
            and record.observed_at >= source._registration.cutoff
        ):
            ordinals.append(record.boundary.ordinal)
    return tuple(ordinals)


def _project(
    source: CandidateSource,
    checkpoint: SourceCheckpoint | None,
    origin: _Origin,
    records: list[_CompleteRow],
    admitted: dict[SourceRef, int],
    pending: dict[SourceRef, int],
    offset: int,
    prefix: str,
) -> FrameBatch:
    frames = []
    commit_frames = []
    sideband = []
    commit_sideband = []
    durable_usage = None
    diagnostics = []
    held = False
    for entry in records:
        frame = entry.frame
        if entry.diagnostic is not None and (
            not held or entry.diagnostic.code is DiagnosticCode.BOUNDARY_UNVERIFIED
        ):
            diagnostics.append(entry.diagnostic)
        if frame is None:
            continue
        if isinstance(frame, _SidebandRecord):
            sideband.append(frame.frame)
            context = frame.context
            if (
                held
                or context is None
                or _eligibility(context, source, admitted, pending)
                is not Eligibility.ELIGIBLE
            ):
                continue
            if commit_frames and commit_frames[-1].ordinal == context.ordinal:
                commit_sideband.append(frame.frame)
                continue
            if durable_usage is None:
                durable_usage = _durable_usage_ordinals(source, checkpoint)
            assert frame.segment_start is not None
            if any(
                frame.segment_start <= ordinal <= context.ordinal
                for ordinal in durable_usage
            ):
                commit_sideband.append(frame.frame)
            continue
        eligibility = _eligibility(frame, source, admitted, pending)
        if not held and eligibility is Eligibility.UNKNOWN:
            offset, prefix = entry.start, entry.prefix_before
            held = True
        frame = replace(
            frame,
            eligibility=Eligibility.UNKNOWN if held else eligibility,
            boundary_only=held,
        )
        frames.append(frame)
        if not held:
            commit_frames.append(frame)
    # Verifying an identical archive must not republish a checkpoint merely
    # because discovery returned another locator for the same logical stream.
    if checkpoint is not None and offset == checkpoint.cursor.offset:
        cursor = checkpoint.cursor
    else:
        cursor = SourceCursor(
            source.stream_ref,
            source.locator_ref,
            source.incarnation_ref,
            offset,
            _validation_ref(source, origin, offset, prefix),
        )
    assert origin.provider is not None
    provider = replace(
        checkpoint.provider
        if checkpoint is not None
        else ProviderCheckpoint(origin.provider),
        client_version=origin.client,
        format_version=origin.format,
    )
    return FrameBatch(
        frames=tuple(frames),
        commit_frames=tuple(commit_frames),
        cursor=cursor,
        provider_checkpoint=provider,
        diagnostics=tuple(diagnostics),
        observed_through=max(
            (frame.observed_at for frame in commit_frames), default=None
        ),
        sideband=tuple(sideband),
        commit_sideband=tuple(commit_sideband),
    )


def scan(
    source: CandidateSource,
    checkpoint: SourceCheckpoint | None,
    cutoff: datetime,
    *,
    _capture_limit: SourceCursor | None = None,
) -> FrameBatch:
    """Verify an approved snapshot and expose complete rows through its safe cursor."""
    if (
        type(cutoff) is not datetime
        or cutoff.tzinfo is None
        or cutoff.utcoffset() is None
        or cutoff != source._registration.cutoff
    ):
        raise ValueError("Expected the pinned activation cutoff")
    cutoff = cutoff.astimezone(UTC)
    try:
        if not _within_source_roots(source):
            raise _ChangedSource
        with _open_snapshot(source._path, identity_prefix=source._identity) as (
            stream,
            snapshot,
        ):
            return _read(stream, snapshot, source, checkpoint, cutoff, _capture_limit)
    except _CaptureDiscontinuity:
        code = DiagnosticCode.SOURCE_REPLACED
    except _SourceIssue as failure:
        code = failure.code
    except OSError as failure:
        code = (
            DiagnosticCode.SOURCE_REPLACED
            if isinstance(failure, _ChangedSource)
            or failure.errno in (errno.ELOOP, errno.ENOTDIR)
            else DiagnosticCode.SOURCE_UNAVAILABLE
        )
    return FrameBatch(
        diagnostics=(Diagnostic(code, cutoff, source.provider, source.stream_ref),)
    )
