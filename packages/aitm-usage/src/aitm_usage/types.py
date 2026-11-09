"""Typed inputs and the closed wire formats used by the ledger and scope inbox."""

import json
import re
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime
from enum import StrEnum
from functools import cache
from pathlib import Path
from types import UnionType
from typing import cast, get_args, get_origin, get_type_hints
from uuid import UUID


class Provider(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"


class Availability(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class Eligibility(StrEnum):
    ELIGIBLE = "eligible"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


class BoundaryKind(StrEnum):
    REQUEST = "request"
    TURN = "turn"


class WorkPhase(StrEnum):
    BRAINSTORMING = "brainstorming"
    DESIGN = "design"
    PLANNING = "planning"
    DOCUMENT_REVIEW = "document-review"
    DEVELOPMENT = "development"
    TEST = "test"
    SOURCE_REVIEW = "source-review"
    DELIVERY = "delivery"
    HOUSEKEEPING = "housekeeping"


class ReviewRole(StrEnum):
    AUTHOR = "author"
    REVIEWER = "reviewer"
    SAR = "sar"
    SPR = "spr"
    XPR = "xpr"


class ItemKind(StrEnum):
    PROJECT = "project"
    ISSUE = "issue"
    DRAFT = "draft"


class DiagnosticCode(StrEnum):
    COVERAGE_GAP = "coverage-gap"
    UNKNOWN_USAGE = "unknown-usage"
    MALFORMED_USAGE = "malformed-usage"
    UNSUPPORTED_FORMAT = "unsupported-format"
    SOURCE_REPLACED = "source-replaced"
    SOURCE_UNAVAILABLE = "source-unavailable"
    OVERLAP_UNVERIFIED = "overlap-unverified"
    IDENTITY_CONFLICT = "identity-conflict"
    COUNTER_REGRESSION = "counter-regression"
    UNRECONCILED_USAGE = "unreconciled-usage"
    BOUNDARY_UNVERIFIED = "boundary-unverified"


class Effort(StrEnum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"
    MAX = "max"
    ULTRA = "ultra"


class ProcessingTier(StrEnum):
    STANDARD = "standard"
    PRIORITY = "priority"
    FAST = "fast"
    FLEX = "flex"
    BATCH = "batch"


def _nonnegative(value: int) -> None:
    if type(value) is not int or not 0 <= value < 2**63:
        raise ValueError("Expected a nonnegative signed 64-bit count")


def _positive(value: int) -> None:
    _nonnegative(value)
    if value == 0:
        raise ValueError("Expected a positive count")


def _client_version(value: str) -> None:
    if type(value) is not str or not re.fullmatch(
        r"v?\d+\.\d+(?:\.\d+)?(?:[-+][a-zA-Z0-9.-]{1,32})?", value
    ):
        raise ValueError("Expected a client version")


@dataclass(frozen=True, slots=True)
class SourceRef:
    """Opaque project-keyed pseudonym for an identifier, locator, or source anchor."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or not re.fullmatch(
            r"hmac-sha256:[a-f0-9]{64}", self.value
        ):
            raise ValueError("Expected a project-keyed reference")


@dataclass(frozen=True, slots=True)
class Registration:
    project_id: UUID
    state_root: Path
    source_roots: tuple[Path, ...]
    checkout_anchors: tuple[Path, ...]
    cutoff: datetime


@dataclass(frozen=True, slots=True)
class SourceBoundary:
    provider: Provider
    stream_ref: SourceRef
    session_ref: SourceRef
    ordinal: int
    kind: BoundaryKind
    boundary_ref: SourceRef
    epoch_ref: SourceRef | None = None
    receipt_ref: SourceRef | None = None

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)


@dataclass(frozen=True, slots=True)
class TokenCounts:
    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_5m_tokens: int | None = None
    cache_write_1h_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                _nonnegative(value)


@dataclass(frozen=True, slots=True)
class UsageObservation:
    boundary: SourceBoundary
    observed_at: datetime
    client_version: str
    format_version: int
    tokens: TokenCounts
    availability: Availability
    request_ref: SourceRef | None = None
    message_ref: SourceRef | None = None
    model: str | None = None
    effort: Effort | None = None
    processing_tier: ProcessingTier | None = None
    context_tokens: int | None = None

    def __post_init__(self) -> None:
        _client_version(self.client_version)
        _positive(self.format_version)
        if self.model is not None and (
            type(self.model) is not str
            or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,95}", self.model)
        ):
            raise ValueError("Expected a model identifier")
        if self.context_tokens is not None:
            _nonnegative(self.context_tokens)


@dataclass(frozen=True, slots=True)
class ItemKey:
    kind: ItemKind
    identifier: UUID | int | None = None

    def __post_init__(self) -> None:
        if self.kind is ItemKind.ISSUE:
            _positive(self.identifier)
        elif self.kind is ItemKind.DRAFT and type(self.identifier) is UUID:
            return
        elif self.kind is ItemKind.PROJECT and self.identifier is None:
            return
        else:
            raise ValueError("Invalid item identifier")


@dataclass(frozen=True, slots=True)
class ScopeMarker:
    marker_id: UUID
    provider: Provider
    session_ref: SourceRef
    scope_sequence: int
    boundary_kind: BoundaryKind
    boundary_ref: SourceRef
    published_at: datetime
    item: ItemKey
    phase: WorkPhase
    participant_ref: SourceRef
    project_id: UUID
    role: ReviewRole | None = None
    receipt_ref: SourceRef | None = None
    attempt_ref: SourceRef | None = None
    review_ref: SourceRef | None = None

    def __post_init__(self) -> None:
        _positive(self.scope_sequence)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: DiagnosticCode
    observed_at: datetime
    provider: Provider | None = None
    source_ref: SourceRef | None = None
    ordinal: int | None = None

    def __post_init__(self) -> None:
        if self.ordinal is not None:
            _nonnegative(self.ordinal)


Record = UsageObservation | ScopeMarker | Diagnostic


@dataclass(frozen=True, slots=True)
class Revision:
    key: SourceRef
    revision: int
    record: Record

    def __post_init__(self) -> None:
        _positive(self.revision)


@dataclass(frozen=True, slots=True)
class SourceCursor:
    source_ref: SourceRef
    locator_ref: SourceRef
    incarnation_ref: SourceRef
    offset: int
    anchor_ref: SourceRef

    def __post_init__(self) -> None:
        _nonnegative(self.offset)


@dataclass(frozen=True, slots=True)
class RequestPrefix:
    request_ref: SourceRef
    message_ref: SourceRef
    ordinal: int
    tokens: TokenCounts
    complete: bool = False

    def __post_init__(self) -> None:
        _nonnegative(self.ordinal)


@dataclass(frozen=True, slots=True)
class ProviderCheckpoint:
    provider: Provider
    epoch_ref: SourceRef | None = None
    ordinal: int = 0
    baseline: TokenCounts | None = None
    request_prefix: tuple[RequestPrefix, ...] = ()
    version: int = 1
    client_version: str | None = None
    format_version: int | None = None

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version != 1:
            raise ValueError("Unsupported provider checkpoint version")
        _nonnegative(self.ordinal)
        if self.client_version is not None:
            _client_version(self.client_version)
        if self.format_version is not None:
            _positive(self.format_version)


@dataclass(frozen=True, slots=True)
class SourceCheckpoint:
    cursor: SourceCursor
    provider: ProviderCheckpoint


@dataclass(frozen=True, slots=True)
class AdapterResult:
    revisions: tuple[Revision, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    boundaries: tuple[SourceBoundary, ...] = ()
    provider_checkpoint: ProviderCheckpoint | None = None


@dataclass(frozen=True, slots=True)
class LedgerBatch:
    revisions: tuple[Revision, ...] = ()
    checkpoint: SourceCheckpoint | None = None
    prior_checkpoint: SourceCheckpoint | None = None


@dataclass(frozen=True, slots=True)
class LedgerView:
    sequence: int
    revisions: tuple[Revision, ...]
    checkpoints: tuple[SourceCheckpoint, ...]

    @property
    def current(self) -> tuple[Revision, ...]:
        latest = {revision.key: revision for revision in self.revisions}
        return tuple(latest.values())


@cache
def _fields(model: type) -> dict[str, type]:
    hints = get_type_hints(model)
    return {field.name: hints[field.name] for field in fields(model)}


def _wire(value: object, expected: type, *, decode: bool) -> object:
    """Convert only the exact fields and scalar types declared in a wire model."""
    origin = get_origin(expected)
    if origin is UnionType:
        for choice in get_args(expected):
            try:
                return _wire(value, choice, decode=decode)
            except (TypeError, ValueError):
                continue
    elif origin is tuple:
        if type(value) is (list if decode else tuple):
            item_type, _ = get_args(expected)
            items = (_wire(item, item_type, decode=decode) for item in value)
            return tuple(items) if decode else list(items)
    elif expected in (str, int, bool, type(None)):
        if type(value) is expected:
            return value
    elif expected in (datetime, UUID, SourceRef) or issubclass(expected, StrEnum):
        if decode and type(value) is str:
            if expected is datetime:
                moment = datetime.fromisoformat(value)
                if moment.utcoffset() is not None:
                    return moment.astimezone(UTC)
            else:
                return expected(value)
        elif not decode and type(value) is expected:
            if expected is datetime:
                if value.utcoffset() is not None:
                    return value.astimezone(UTC).isoformat()
            elif expected is SourceRef:
                return value.value
            else:
                return str(value)
    elif is_dataclass(expected):
        schema = _fields(expected)
        if decode and type(value) is dict and value.keys() == schema.keys():
            return expected(
                **{
                    name: _wire(value[name], kind, decode=True)
                    for name, kind in schema.items()
                }
            )
        if not decode and type(value) is expected:
            return {
                name: _wire(getattr(value, name), kind, decode=False)
                for name, kind in schema.items()
            }
    raise ValueError("Value does not match the allowlisted usage fields")


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate usage fields")
    return result


def _encode(value: object, model: type) -> str:
    return json.dumps(
        _wire(value, model, decode=False), sort_keys=True, separators=(",", ":")
    )


def _decode[T](data: str | bytes, model: type[T]) -> T:
    try:
        payload = json.loads(data, object_pairs_hook=_unique_fields)
        return cast(T, _wire(payload, model, decode=True))
    except (TypeError, ValueError):
        raise ValueError("Invalid allowlisted usage envelope") from None


def encode_marker(marker: ScopeMarker) -> bytes:
    """Validate the entire marker before the inbox owner publishes it."""
    return _encode(marker, ScopeMarker).encode("utf-8")


def decode_marker(data: bytes) -> ScopeMarker:
    return _decode(data, ScopeMarker)
