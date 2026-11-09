"""Typed inputs and the closed wire formats used by the ledger and scope inbox."""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
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


class ModelLabel(StrEnum):
    UNKNOWN = "unknown"
    GPT_6_ASTRA = "gpt-6-astra"
    GPT_6_1_SOL = "gpt-6.1-sol"
    CLAUDE_OPUS_5_5 = "claude-opus-5-5"


class ClientVersion(StrEnum):
    UNKNOWN = "unknown"
    CODEX_0_167_0_ALPHA_3_2 = "0.167.0-alpha.3.2"
    CLAUDE_2_1_318 = "2.1.318"


class QuotaBucket(StrEnum):
    FIVE_HOUR = "five-hour"
    SEVEN_DAY = "seven-day"


class QuotaSource(StrEnum):
    CODEX_INLINE = "codex-inline"
    CODEX_ACCOUNT = "codex-account"
    CLAUDE_RATE_LIMIT_EVENT = "claude-rate-limit-event"
    CLAUDE_USAGE = "claude-usage"


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


def normalize_model(raw: str | None) -> ModelLabel:
    try:
        return ModelLabel(raw)
    except ValueError:
        return ModelLabel.UNKNOWN


def normalize_client_version(raw: str | None) -> ClientVersion:
    try:
        return ClientVersion(raw)
    except ValueError:
        return ClientVersion.UNKNOWN


@dataclass(frozen=True, slots=True)
class SourceRef:
    """Opaque project-keyed pseudonym for an identifier, locator, or source anchor."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or not re.fullmatch(
            r"hmac-sha256:[a-f0-9]{64}:[a-f0-9]{64}", self.value
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
    client_version: ClientVersion
    format_version: int
    tokens: TokenCounts
    availability: Availability
    request_ref: SourceRef | None = None
    message_ref: SourceRef | None = None
    model: ModelLabel = ModelLabel.UNKNOWN
    effort: Effort | None = None
    processing_tier: ProcessingTier | None = None
    context_tokens: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "client_version", normalize_client_version(self.client_version)
        )
        object.__setattr__(self, "model", normalize_model(self.model))
        _positive(self.format_version)
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
class DevelopmentBinding:
    """A verified owner marker and its claimed checkout and generation."""

    marker: ScopeMarker
    anchor_ref: SourceRef
    generation: int

    def __post_init__(self) -> None:
        _positive(self.generation)
        if (
            self.marker.item.kind is ItemKind.PROJECT
            or self.marker.phase is not WorkPhase.DEVELOPMENT
            or self.marker.role not in (None, ReviewRole.AUTHOR)
            or self.marker.attempt_ref is None
            or self.marker.review_ref is not None
        ):
            raise ValueError("Invalid development owner scope")


@dataclass(frozen=True, slots=True)
class ScopeCorrection:
    correction_id: UUID
    project_id: UUID
    replacement: ScopeMarker
    evidence_ref: SourceRef

    def __post_init__(self) -> None:
        if self.replacement.project_id != self.project_id:
            raise ValueError("Scope correction project mismatch")
        if self.correction_id == self.replacement.marker_id:
            raise ValueError("Scope correction requires its own command ID")


@dataclass(frozen=True, slots=True)
class DraftAlias:
    command_id: UUID
    project_id: UUID
    draft: ItemKey
    issue: ItemKey

    def __post_init__(self) -> None:
        if (
            self.draft.kind is not ItemKind.DRAFT
            or self.issue.kind is not ItemKind.ISSUE
        ):
            raise ValueError("An alias requires a draft and a permanent issue")


@dataclass(frozen=True, slots=True)
class ItemParent:
    command_id: UUID
    project_id: UUID
    child: ItemKey
    parent: ItemKey

    def __post_init__(self) -> None:
        if self.child.kind is ItemKind.PROJECT or self.parent.kind is ItemKind.PROJECT:
            raise ValueError("A parent link requires draft or issue items")


InboxPayload = (
    ScopeMarker | DevelopmentBinding | ScopeCorrection | DraftAlias | ItemParent
)
_COMMAND_TYPES = {
    "scope-mark": ScopeMarker,
    "development-bind": DevelopmentBinding,
    "scope-correct": ScopeCorrection,
    "item-alias": DraftAlias,
    "item-parent": ItemParent,
}
MarkerId = UUID


@dataclass(frozen=True, slots=True)
class InboxCommand:
    command_id: UUID
    project_id: UUID
    payload: InboxPayload

    def __post_init__(self) -> None:
        payload = self.payload
        if type(payload) not in _COMMAND_TYPES.values():
            raise ValueError("Unsupported inbox command")
        if isinstance(payload, DevelopmentBinding):
            payload = payload.marker
        if isinstance(payload, ScopeCorrection):
            payload_id = payload.correction_id
        elif isinstance(payload, (DraftAlias, ItemParent)):
            payload_id = payload.command_id
        else:
            payload_id = payload.marker_id
        if self.command_id != payload_id or self.project_id != payload.project_id:
            raise ValueError("Inbox command identity mismatch")


@dataclass(frozen=True, slots=True)
class CommandDigest:
    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or not re.fullmatch(
            r"sha256:[a-f0-9]{64}", self.value
        ):
            raise ValueError("Invalid inbox command digest")


class MarkerDisposition(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class CommandAcknowledgment:
    command_id: UUID
    digest: CommandDigest
    disposition: MarkerDisposition


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    command: InboxCommand
    digest: CommandDigest
    disposition: MarkerDisposition
    boundary: SourceBoundary | None = None
    anchor_ref: SourceRef | None = None

    @property
    def acknowledgment(self) -> CommandAcknowledgment:
        return CommandAcknowledgment(
            self.command.command_id, self.digest, self.disposition
        )


@dataclass(frozen=True, slots=True)
class ScopeEnrollment:
    """The effective scope and its source-attested starting boundary."""

    marker: ScopeMarker
    boundary: SourceBoundary
    anchor_ref: SourceRef | None = None
    generation: int | None = None

    def __post_init__(self) -> None:
        marker, boundary = self.marker, self.boundary
        if (
            marker.provider is not boundary.provider
            or marker.session_ref != boundary.session_ref
            or marker.boundary_kind is not boundary.kind
            or marker.boundary_ref != boundary.boundary_ref
            or marker.receipt_ref is None
            or marker.receipt_ref != boundary.receipt_ref
        ):
            raise ValueError("Scope enrollment requires matching source proof")
        if self.generation is not None:
            if self.anchor_ref is None:
                raise ValueError("Development enrollment requires a checkout anchor")
            DevelopmentBinding(marker, self.anchor_ref, self.generation)


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


@dataclass(frozen=True, slots=True)
class QuotaEvidence:
    """A structured account-window reading. Percentage units are 0.001 points."""

    provider: Provider
    account_ref: SourceRef
    bucket: QuotaBucket
    observed_at: datetime
    percent_milli: int
    precision: int
    source: QuotaSource
    reset_at: datetime | None = None
    window_seconds: int | None = None

    def __post_init__(self) -> None:
        if (
            type(self.provider) is not Provider
            or type(self.account_ref) is not SourceRef
            or type(self.bucket) is not QuotaBucket
            or type(self.source) is not QuotaSource
        ):
            raise ValueError(
                "Invalid quota evidence classification or account reference"
            )
        codex_sources = (QuotaSource.CODEX_INLINE, QuotaSource.CODEX_ACCOUNT)
        if (self.provider is Provider.CODEX) != (self.source in codex_sources):
            raise ValueError("Quota source does not match provider")
        if (
            type(self.percent_milli) is not int
            or not 0 <= self.percent_milli <= 100_000
            or type(self.precision) is not int
            or not 0 <= self.precision <= 3
            or self.percent_milli % 10 ** (3 - self.precision)
        ):
            raise ValueError("Invalid fixed-point quota percentage or precision")
        for moment in (self.observed_at, self.reset_at):
            if moment is not None and (
                type(moment) is not datetime or moment.utcoffset() != timedelta(0)
            ):
                raise ValueError("Quota times must be UTC")
        if self.observed_at is None:
            raise ValueError("Quota observation time is required")
        if self.window_seconds is not None:
            _positive(self.window_seconds)


class Currency(StrEnum):
    USD = "USD"


def _rate_version(version: str) -> None:
    if type(version) is not str or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", version
    ):
        raise ValueError("Expected a rate card version date")
    date.fromisoformat(version)


@dataclass(frozen=True, slots=True)
class RateBasis:
    version: str
    sha256: str
    currency: Currency

    def __post_init__(self) -> None:
        _rate_version(self.version)
        if type(self.sha256) is not str or not re.fullmatch(
            r"[a-f0-9]{64}", self.sha256
        ):
            raise ValueError("Expected a SHA-256 rate card digest")
        if type(self.currency) is not Currency:
            raise ValueError("Unsupported rate card currency")

    @property
    def identifier(self) -> str:
        return f"standard-api-{self.currency.value}:{self.version}:sha256:{self.sha256}"


@dataclass(frozen=True, slots=True)
class PriceResult:
    basis: RateBasis
    availability: Availability
    usd: Decimal | None

    def __post_init__(self) -> None:
        if type(self.basis) is not RateBasis:
            raise ValueError("Expected a versioned rate basis")
        expected = Availability.UNKNOWN if self.usd is None else Availability.COMPLETE
        if self.availability is not expected:
            raise ValueError("Price and availability disagree")
        if self.usd is not None:
            _decimal_text(self.usd)

    @property
    def currency(self) -> Currency:
        return self.basis.currency


@dataclass(frozen=True, slots=True)
class PriceObservation:
    observation_key: SourceRef
    observation_revision: int
    result: PriceResult

    def __post_init__(self) -> None:
        _positive(self.observation_revision)

    @property
    def rate_basis(self) -> str:
        return self.result.basis.identifier

    @property
    def usd(self) -> Decimal | None:
        return self.result.usd

    @property
    def availability(self) -> Availability:
        return self.result.availability

    @property
    def currency(self) -> Currency:
        return self.result.currency


@dataclass(frozen=True, slots=True)
class AccountObservation(QuotaEvidence):
    @property
    def task_burn_availability(self) -> Availability:
        return Availability.UNKNOWN


@dataclass(frozen=True, slots=True)
class SpendObservation:
    observation_key: SourceRef
    observation_revision: int
    availability: Availability = Availability.UNKNOWN

    def __post_init__(self) -> None:
        _positive(self.observation_revision)
        if self.availability is not Availability.UNKNOWN:
            raise ValueError("Actual billed spend is unavailable in this schema")


Record = (
    UsageObservation
    | ScopeMarker
    | Diagnostic
    | ScopeEnrollment
    | CommandReceipt
    | DraftAlias
    | ItemParent
    | PriceObservation
    | AccountObservation
    | SpendObservation
)
_RECORD_TYPES = {
    "usage": UsageObservation,
    "scope-marker": ScopeMarker,
    "diagnostic": Diagnostic,
    "scope-enrollment": ScopeEnrollment,
    "command-receipt": CommandReceipt,
    "draft-alias": DraftAlias,
    "item-parent": ItemParent,
    "api-equivalent-price": PriceObservation,
    "account-observation": AccountObservation,
    "actual-spend": SpendObservation,
}
_TAGGED_CODECS = {
    Record: (
        "record",
        _RECORD_TYPES,
        {model: tag for tag, model in _RECORD_TYPES.items()},
    ),
    InboxPayload: (
        "command",
        _COMMAND_TYPES,
        {model: tag for tag, model in _COMMAND_TYPES.items()},
    ),
}


@dataclass(frozen=True, slots=True)
class Revision:
    key: SourceRef
    revision: int
    record: Record

    def __post_init__(self) -> None:
        _positive(self.revision)
        if self.revision != 1 and isinstance(
            self.record, (PriceObservation, AccountObservation, SpendObservation)
        ):
            raise ValueError("Accounting records are immutable at their own keys")


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
    client_version: ClientVersion = ClientVersion.UNKNOWN
    format_version: int | None = None

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version != 1:
            raise ValueError("Unsupported provider checkpoint version")
        _nonnegative(self.ordinal)
        object.__setattr__(
            self, "client_version", normalize_client_version(self.client_version)
        )
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
    quota: tuple[QuotaEvidence, ...] = ()


@dataclass(frozen=True, slots=True)
class LedgerBatch:
    revisions: tuple[Revision, ...] = ()
    checkpoint: SourceCheckpoint | None = None
    prior_checkpoint: SourceCheckpoint | None = None


@dataclass(frozen=True, slots=True)
class LedgerView:
    project_id: UUID
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


# USD values use a bounded, canonical decimal string on the wire. Thirteen
# fractional places cover per-million rates at six places and a 1.5x multiplier.
_DECIMAL_TEXT = re.compile(r"(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{0,12}[1-9])?")


def _decimal_text(value: Decimal) -> str:
    if (
        type(value) is not Decimal
        or not value.is_finite()
        or value.is_signed()
        or value.adjusted() > 23
        or value.as_tuple().exponent < -13
    ):
        raise ValueError("Expected a bounded nonnegative decimal")
    if not value:
        return "0"
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _wire(
    value: object,
    expected: type,
    *,
    decode: bool,
    validate_ref: Callable[[SourceRef], None] | None = None,
) -> object:
    """Convert only the exact fields and scalar types declared in a wire model."""

    def convert(item: object, kind: type) -> object:
        return _wire(item, kind, decode=decode, validate_ref=validate_ref)

    origin = get_origin(expected)
    if expected in _TAGGED_CODECS:
        field_name, types, tags = _TAGGED_CODECS[expected]
        if decode and type(value) is dict and value.keys() == {"kind", field_name}:
            tag = value["kind"]
            if type(tag) is str and tag in types:
                return convert(value[field_name], types[tag])
        if not decode and type(value) in tags:
            return {
                "kind": tags[type(value)],
                field_name: convert(value, type(value)),
            }
    elif origin is UnionType:
        for choice in get_args(expected):
            try:
                return convert(value, choice)
            except (TypeError, ValueError):
                continue
    elif origin is tuple:
        if type(value) is (list if decode else tuple):
            item_type, _ = get_args(expected)
            items = (convert(item, item_type) for item in value)
            return tuple(items) if decode else list(items)
    elif expected in (str, int, bool, type(None)):
        if type(value) is expected:
            return value
    elif expected is Decimal:
        if decode and type(value) is str and _DECIMAL_TEXT.fullmatch(value):
            return Decimal(value)
        if not decode:
            return _decimal_text(value)
    elif expected is SourceRef:
        reference = SourceRef(value) if decode and type(value) is str else value
        if type(reference) is SourceRef:
            if validate_ref is not None:
                validate_ref(reference)
            return reference if decode else reference.value
    elif expected in (datetime, UUID) or issubclass(expected, StrEnum):
        if decode and type(value) is str:
            if expected is datetime:
                moment = datetime.fromisoformat(value)
                if moment.utcoffset() is not None:
                    return moment
            else:
                return expected(value)
        elif not decode and type(value) is expected:
            if isinstance(value, datetime):
                if value.utcoffset() is not None:
                    return value.astimezone(UTC).isoformat()
            else:
                return str(value)
    elif is_dataclass(expected):
        schema = _fields(expected)
        if decode and type(value) is dict and value.keys() == schema.keys():
            return expected(
                **{name: convert(value[name], kind) for name, kind in schema.items()}
            )
        if not decode and type(value) is expected:
            return {
                name: convert(getattr(value, name), kind)
                for name, kind in schema.items()
            }
    raise ValueError("Value does not match the allowlisted usage fields")


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate usage fields")
    return result


def _encode(
    value: object,
    model: type,
    *,
    validate_ref: Callable[[SourceRef], None] | None = None,
) -> str:
    return json.dumps(
        _wire(value, model, decode=False, validate_ref=validate_ref),
        sort_keys=True,
        separators=(",", ":"),
    )


def _decode[T](
    data: str | bytes,
    model: type[T],
    *,
    validate_ref: Callable[[SourceRef], None] | None = None,
) -> T:
    try:
        payload = json.loads(data, object_pairs_hook=_unique_fields)
        return cast(T, _wire(payload, model, decode=True, validate_ref=validate_ref))
    except (RecursionError, TypeError, ValueError):
        raise ValueError("Invalid allowlisted usage envelope") from None


def encode_marker(marker: ScopeMarker) -> bytes:
    """Encode the closed marker shape. Authenticate it with the project ledger before use."""
    return _encode(marker, ScopeMarker).encode("utf-8")


def decode_marker(data: bytes) -> ScopeMarker:
    return _decode(data, ScopeMarker)


def encode_binding(binding: DevelopmentBinding) -> bytes:
    return _encode(binding, DevelopmentBinding).encode("utf-8")


def decode_binding(data: bytes) -> DevelopmentBinding:
    return _decode(data, DevelopmentBinding)


def encode_correction(correction: ScopeCorrection) -> bytes:
    return _encode(correction, ScopeCorrection).encode("utf-8")


def decode_correction(data: bytes) -> ScopeCorrection:
    return _decode(data, ScopeCorrection)


def encode_command(command: InboxCommand) -> bytes:
    return _encode(command, InboxCommand).encode("utf-8")


def decode_command(data: bytes) -> InboxCommand:
    return _decode(data, InboxCommand)
