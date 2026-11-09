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
from typing import BinaryIO

from ..ledger import Ledger, LedgerError
from ..scopes import BoundaryEvidence, session_reference
from ..types import (
    ClientVersion,
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    Provider,
    ProviderCheckpoint,
    Registration,
    ScopeEnrollment,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    normalize_client_version,
)

_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
_FILE_FLAGS = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
_SUPPORTED_CLIENTS = {
    Provider.CODEX: ClientVersion.CODEX_0_167_0_ALPHA_3_2,
    Provider.CLAUDE: ClientVersion.CLAUDE_2_1_318,
}
_CLAUDE_SESSION_ROWS = {"user", "assistant", "system", "result", "rate_limit_event"}
_MAX_ROW_BYTES = 16 * 1024 * 1024
_READ_CHUNK = 64 * 1024
type _Row = dict[str, object]
type _FileID = tuple[int, int, int]


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


@dataclass(frozen=True, slots=True)
class FrameBatch:
    """Look-ahead and an independent commit frontier from one verified snapshot.

    Adapters inspect frames for boundaries. Only commit_frames may advance
    provider state or yield usage. Publish cursor, adapter state and observations
    together through Ledger.apply, using the exact input checkpoint as its prior.
    """

    frames: tuple[SourceFrame, ...] = ()
    commit_frames: tuple[SourceFrame, ...] = ()
    cursor: SourceCursor | None = None
    provider_checkpoint: ProviderCheckpoint | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    observed_through: datetime | None = None

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
    _registration: Registration = field(repr=False, compare=False)
    _ledger: Ledger = field(repr=False, compare=False)
    _enrollments: tuple[_Enrollment, ...] = field(repr=False, default=())
    _excluded: frozenset[SourceRef] = field(repr=False, default=frozenset())

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
        matches before admitting usage. A verified committed prefix suffices for
        earlier boundaries.
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
        if batch is not None or evidence is not None:
            if (
                batch is None
                or evidence
                != BoundaryEvidence(enrollment.boundary, enrollment.anchor_ref)
                or batch.scope_evidence(enrollment.boundary) != evidence
            ):
                raise ValueError("Expected fresh evidence for the verified enrollment")
            frame = batch._matching_frame(enrollment.boundary)
            assert frame is not None
            prefix = frame._prefix
        updated = tuple(
            selector
            for selector in self._enrollments
            if selector.scope.boundary.ordinal != enrollment.boundary.ordinal
        )
        return replace(self, _enrollments=(*updated, _Enrollment(enrollment, prefix)))

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


def _session(ledger: Ledger, provider: Provider, raw: object) -> SourceRef | None:
    if type(raw) is not str:
        return None
    try:
        return session_reference(ledger, provider, raw)
    except ValueError:
        return None


def _claude_session(row: _Row, ledger: Ledger) -> SourceRef | None:
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


def _origin_from(row: _Row, ordinal: int, ledger: Ledger) -> _Origin | None:
    kind = row["type"]
    if kind == "session_meta" and ordinal == 0:
        provider = Provider.CODEX
        metadata = _codex_payload(row) or {}
        session = _session(ledger, provider, metadata.get("id"))
        raw_client = metadata.get("cli_version")
    elif kind in _CLAUDE_SESSION_ROWS and ("sessionId" in row or "session_id" in row):
        provider = Provider.CLAUDE
        metadata = row
        session = _claude_session(row, ledger)
        raw_client = row.get("version")
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
    return _Origin(provider, session, client, 1)


def _origin(stream: BinaryIO, size: int, ledger: Ledger) -> _Origin | None:
    """Look for startup identity without following arbitrary transcript fields."""
    found_complete = False
    digest = hashlib.sha256()
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
                origin, startup_ordinal=ordinal, startup_digest=digest.hexdigest()
            )
    if found_complete or size > limit:
        return _Origin(None, None, issue=DiagnosticCode.UNSUPPORTED_FORMAT)
    return None


def discover(registration: Registration) -> Iterator[CandidateSource]:
    """Enumerate regular JSONL files under explicit roots without symlink traversal.

    Supply the latest checkpoint for each stream_ref when scanning rediscovered
    candidates. Also compare locator_ref to detect replacement at a known path.
    """
    ledger = Ledger.open(registration.state_root, registration.project_id)
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
                    locator = ledger.pseudonymize(
                        "source-locator", os.fsencode(path).hex()
                    )
                    incarnation = ledger.pseudonymize(
                        "source-incarnation", ":".join(map(str, snapshot.identity[-1]))
                    )
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
                    )
        except OSError:
            continue


def checkout_anchor_reference(ledger: Ledger, path: Path) -> SourceRef:
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
    return _Segment(cwd, ref, _checkout_anchor(cwd, source))


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
        if kind in _CLAUDE_SESSION_ROWS or "sessionId" in row or "session_id" in row:
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


@dataclass(frozen=True, slots=True)
class _CompleteRow:
    start: int
    prefix_before: str
    frame: SourceFrame | None
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


def _hash_prefix(stream: BinaryIO, size: int) -> str:
    digest = hashlib.sha256()
    offset = 0
    while offset < size:
        # Read the descriptor directly so a buffered seek cannot reuse stale bytes.
        raw = os.pread(stream.fileno(), min(_READ_CHUNK, size - offset), offset)
        if not raw:
            raise _ChangedSource
        digest.update(raw)
        offset += len(raw)
    return digest.hexdigest()


def _mtime(info: os.stat_result) -> tuple[int, int, int]:
    return info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _verify_snapshot(
    stream: BinaryIO,
    source: CandidateSource,
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
    current = _reprobe(source._path)
    # A directory can be moved out and back with identical inodes at both
    # endpoints. Directory ctime witnesses apply only to this open snapshot.
    if not snapshot.same_path(current) or _mtime(current.stat) != _mtime(after):
        raise _ChangedSource


def _validation_ref(
    source: CandidateSource, origin: _Origin, offset: int, digest: str
) -> SourceRef:
    # The held zero-byte frontier still authenticates the observed origin.
    if offset == 0:
        return source._ledger.pseudonymize(
            "source-origin", f"{source.stream_ref.value}:{origin.startup_digest}"
        )
    return source._ledger.pseudonymize(
        "source-prefix", f"{source.stream_ref.value}:{offset}:{digest}"
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


def _read(
    stream: BinaryIO,
    snapshot: _Snapshot,
    source: CandidateSource,
    checkpoint: SourceCheckpoint | None,
    cutoff: datetime,
) -> FrameBatch:
    prior = _prior_offset(source, checkpoint)
    origin = _origin(stream, snapshot.stat.st_size, source._ledger)
    if origin is None or (origin.provider, origin.session_ref) != (
        source.provider,
        source.session_ref,
    ):
        raise _SourceIssue(DiagnosticCode.SOURCE_REPLACED)
    if origin.issue is not None:
        raise _SourceIssue(origin.issue)
    assert origin.provider is not None and origin.session_ref is not None
    assert origin.format is not None

    if checkpoint is not None and prior == snapshot.stat.st_size:
        prefix = _hash_prefix(stream, prior)
        _verify_prior(source, origin, checkpoint, prior, prefix)
        _verify_snapshot(stream, source, snapshot, prior, prefix)
        return _project(source, checkpoint, origin, [], {}, {}, prior, prefix)

    stream.seek(0)
    records = []
    segment = None
    checkouts: dict[Path, tuple[SourceRef, _FileID]] = {}
    selections = {entry.scope.boundary.ordinal: entry for entry in source._enrollments}
    admitted: dict[SourceRef, int] = {}
    pending: dict[SourceRef, int] = {}
    end = 0
    prefix = hashlib.sha256().hexdigest()
    prior_verified = False
    for ordinal, start, before, prefix, row in _lines(stream, snapshot.stat.st_size):
        end = stream.tell()
        if ordinal == origin.startup_ordinal and prefix != origin.startup_digest:
            raise _ChangedSource
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
        if issue is None and moment is None:
            issue = DiagnosticCode.MALFORMED_USAGE
        if issue is not None:
            if selection is not None:
                raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
            segment = None
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
                selection.scope.anchor_ref == segment.anchor
                and selection.prefix == prefix
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
        if start >= prior:
            assert moment is not None and row is not None
            records.append(
                _CompleteRow(
                    start,
                    before,
                    SourceFrame(
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
                    ),
                    proof_gap,
                )
            )
    if not prior_verified:
        _verify_prior(source, origin, checkpoint, end, prefix)
    if any(
        _checkout_anchor(cwd, source) != anchor for cwd, anchor in checkouts.items()
    ):
        raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
    _verify_snapshot(stream, source, snapshot, end, prefix)
    if selections:
        raise _SourceIssue(DiagnosticCode.BOUNDARY_UNVERIFIED)
    return _project(source, checkpoint, origin, records, admitted, pending, end, prefix)


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
        tuple(frames),
        tuple(commit_frames),
        cursor,
        provider,
        tuple(diagnostics),
        max((frame.observed_at for frame in commit_frames), default=None),
    )


def scan(
    source: CandidateSource, checkpoint: SourceCheckpoint | None, cutoff: datetime
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
        if not any(
            root.is_absolute()
            and ".." not in root.parts
            and source._path.is_relative_to(root)
            for root in source._registration.source_roots
        ):
            raise _ChangedSource
        with _open_snapshot(source._path, identity_prefix=source._identity) as (
            stream,
            snapshot,
        ):
            return _read(stream, snapshot, source, checkpoint, cutoff)
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
