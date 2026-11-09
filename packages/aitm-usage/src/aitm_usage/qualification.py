"""Sanitized activation evidence and read-only checks of the installed collector."""

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from .backup import _DATABASE, _KEY, _MANIFEST, _authority_names, _json
from .export import _check_snapshot, _render
from .install import (
    InstallReceipt,
    LaunchControl,
    _Agent,
    _read_owned,
    _record_name,
    _runtime_for,
    _wheel,
    _wheel_path,
)
from .ledger import Ledger, LedgerError, _guard_path, _path_exists, _pin_directory
from .pricing import RateCard, load_rate_card
from .relationships import canonical_relationships
from .rollup import rollup
from .scopes import (
    MAX_COMMAND_BYTES,
    _decode_publication,
    _publication_bytes,
    attest_marker,
    resolve_scope,
    session_reference,
)
from .service import (
    _candidate,
    _Collector,
    _effective_registration,
    _enrollments,
    _observed_proof,
    _ProducerMode,
    _registration_revision,
    _Status,
    load_registration,
    status_report,
)
from .sources.claude import _isolation
from .sources.codex import _ATTEMPT_ERRORS, _object
from .sources.scan import CandidateSource, checkout_anchor_reference, discover, scan
from .types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    CommandReceipt,
    DevelopmentBinding,
    DiagnosticCode,
    ItemKey,
    ItemKind,
    LedgerView,
    MarkerDisposition,
    ModelLabel,
    Provider,
    ReviewRole,
    ScopeEnrollment,
    ScopeMarker,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
    WorkPhase,
    _decode,
    _encode,
    _nonnegative,
    _positive,
    _unique_fields,
)

_RECEIPT_SCHEMA = "aitm-usage-activation/v1"
_MAX_RECEIPT_AGE = timedelta(minutes=5)
_MAX_SOURCE_AGE = timedelta(minutes=15)
_POLL_SECONDS = 15
_MAX_HEARTBEAT_AGE = timedelta(seconds=3 * _POLL_SECONDS)
_DIGEST = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"[0-9a-f]{40}")
_VERSION = re.compile(
    r"[0-9]{1,8}(?:\.[0-9]{1,8}){2}(?:(?:a|b|rc|\.post|\.dev)[0-9]{1,8})?"
)
_MAX_EVIDENCE_BYTES = 256 * 1024
_MAX_PREFIX_BYTES = 32 * 1024 * 1024
_DISPOSABLE_ISSUES = range(1_000_000_000, 1_000_001_000)
PROOF_NAME = "activation-proof.json"


class _Basis(StrEnum):
    CONTROLLED = "real-controlled"
    PROJECT = "real-project"
    FIXTURE = "fixture-only"


class _Route(StrEnum):
    CODEX = "codex-desktop"
    CLAUDE = "claude-code-native"


class _Metric(StrEnum):
    OBSERVED = "observed"
    GAP = "source-gap"
    UNKNOWN = "unknown"


class _Order(StrEnum):
    MARKER_FIRST = "marker-first"
    BOUNDARY_FIRST = "boundary-first"


_ROUTES = {
    Provider.CODEX: (_Route.CODEX, ClientVersion.CODEX_0_167_0_ALPHA_3_2),
    Provider.CLAUDE: (_Route.CLAUDE, ClientVersion.CLAUDE_2_1_318),
}


def _now() -> datetime:
    return datetime.now(UTC)


def _match(pattern: re.Pattern, *values: str) -> None:
    if any(not pattern.fullmatch(value) for value in values):
        raise ValueError("Invalid activation identifier")


def _utc(*times: datetime) -> None:
    if any(moment.utcoffset() != timedelta(0) for moment in times):
        raise ValueError("Activation evidence times must be UTC")


@dataclass(frozen=True, slots=True)
class _CollectorEvidence:
    version: str
    interpreter_version: str
    wheel_sha256: str
    previous_started: datetime
    previous_heartbeat: datetime
    producer_started: datetime
    activation_heartbeat: datetime
    heartbeat: datetime
    poll_interval_seconds: int
    owned_unattended: bool
    same_process: bool
    private_state: bool

    def __post_init__(self) -> None:
        _match(_VERSION, self.version, self.interpreter_version)
        _match(_DIGEST, self.wheel_sha256)
        _utc(
            self.previous_started,
            self.previous_heartbeat,
            self.producer_started,
            self.activation_heartbeat,
            self.heartbeat,
        )


@dataclass(frozen=True, slots=True)
class _Coverage:
    model_switch: _Metric
    effort_switch: _Metric
    retry: _Metric
    nested: _Metric
    task_quota: _Metric
    actual_spend: _Metric

    def __post_init__(self) -> None:
        if (
            _Metric.UNKNOWN
            in (self.model_switch, self.effort_switch, self.retry, self.nested)
            or self.task_quota is not _Metric.UNKNOWN
            or self.actual_spend is not _Metric.UNKNOWN
        ):
            raise ValueError("Invalid provider coverage disposition")


@dataclass(frozen=True, slots=True)
class _ProviderEvidence:
    provider: Provider
    route: _Route
    client_version: ClientVersion
    format_version: int
    stream: str
    offset: int
    observed_through: datetime
    retention_seconds: int | None
    coverage: _Coverage

    def __post_init__(self) -> None:
        _match(_DIGEST, self.stream)
        _utc(self.observed_through)
        _nonnegative(self.offset)
        if self.retention_seconds is not None:
            _positive(self.retention_seconds)


@dataclass(frozen=True, slots=True)
class _Workflow:
    epic: str
    child_a: str
    child_b: str
    return_to_epic: str
    review_start: str
    review_end: str
    development: str
    housekeeping: str
    graduation_sequence: int
    direct: int
    inclusive: int
    child_a_direct: int
    child_b_direct: int

    @property
    def samples(self) -> tuple[str, ...]:
        return (
            self.epic,
            self.child_a,
            self.child_b,
            self.return_to_epic,
            self.review_start,
            self.review_end,
            self.development,
            self.housekeeping,
        )

    def __post_init__(self) -> None:
        _match(_DIGEST, *self.samples)
        for count in (
            self.graduation_sequence,
            self.direct,
            self.inclusive,
            self.child_a_direct,
            self.child_b_direct,
        ):
            _positive(count)


@dataclass(frozen=True, slots=True)
class _OrderEvidence:
    project_id: UUID
    provider: Provider
    order: _Order
    command: str
    publication_sha256: str
    before_prefix_sha256: str
    prefix_sha256: str
    first_request: str
    before_sequence: int
    after_sequence: int

    def __post_init__(self) -> None:
        _match(
            _DIGEST,
            self.command,
            self.publication_sha256,
            self.before_prefix_sha256,
            self.prefix_sha256,
            self.first_request,
        )
        _positive(self.before_sequence)
        _positive(self.after_sequence)


@dataclass(frozen=True, slots=True)
class _ExportEvidence:
    cutoff: int
    sha256: str
    rows: int
    replay_sha256: str
    replay_rows: int
    catchup_codex: str
    catchup_claude: str

    def __post_init__(self) -> None:
        _match(
            _DIGEST,
            self.sha256,
            self.replay_sha256,
            self.catchup_codex,
            self.catchup_claude,
        )
        for count in (self.cutoff, self.rows, self.replay_rows):
            _positive(count)


@dataclass(frozen=True, slots=True)
class _RecoveryEvidence:
    project_id: UUID
    cutoff: int
    rows: int
    backup_manifest_sha256: str
    before_sha256: str
    restored_sha256: str
    upgraded_sha256: str
    rolled_back_sha256: str
    rehearsal_version: str
    rehearsal_wheel_sha256: str
    started_at: datetime
    backed_up_at: datetime
    restored_at: datetime
    upgraded_at: datetime
    rolled_back_at: datetime

    def __post_init__(self) -> None:
        _positive(self.cutoff)
        _positive(self.rows)
        _match(_VERSION, self.rehearsal_version)
        _match(
            _DIGEST,
            self.backup_manifest_sha256,
            self.before_sha256,
            self.restored_sha256,
            self.upgraded_sha256,
            self.rolled_back_sha256,
            self.rehearsal_wheel_sha256,
        )
        _utc(
            self.started_at,
            self.backed_up_at,
            self.restored_at,
            self.upgraded_at,
            self.rolled_back_at,
        )


@dataclass(frozen=True, slots=True)
class ActivationReceipt:
    """Versioned publication shape. No private provider or host identity fields."""

    schema: str
    basis: _Basis
    project_id: UUID
    source_commit: str
    registration_cutoff: datetime
    observed_at: datetime
    collector: _CollectorEvidence
    providers: tuple[_ProviderEvidence, ...]
    workflow: _Workflow
    orders: tuple[_OrderEvidence, ...]
    export: _ExportEvidence
    recovery: _RecoveryEvidence

    def __post_init__(self) -> None:
        if self.schema != _RECEIPT_SCHEMA:
            raise ValueError("Unsupported activation receipt schema")
        _match(_COMMIT, self.source_commit)
        _utc(self.registration_cutoff, self.observed_at)


@dataclass(frozen=True, slots=True)
class QualificationResult:
    status: str

    @property
    def qualified(self) -> bool:
        return self.status == "qualified"


def decode_activation_receipt(data: str | bytes) -> ActivationReceipt:
    if len(data) > _MAX_EVIDENCE_BYTES:
        raise ValueError("Activation receipt is too large")

    def check_project_id(pairs: list[tuple[str, object]]) -> dict:
        node = _unique_fields(pairs)
        if "project_id" in node:
            raw = node["project_id"]
            if type(raw) is not str or str(UUID(raw)) != raw:
                raise ValueError("Invalid public project identity")
        return node

    payload = json.loads(data, object_pairs_hook=check_project_id)
    return _decode(json.dumps(payload), ActivationReceipt)


def validate_activation_receipt(
    receipt: ActivationReceipt, *, now: datetime | None = None
) -> QualificationResult:
    """Check the closed receipt without opening project files or inspecting launchd."""
    try:
        _encode(receipt, ActivationReceipt)
    except (AttributeError, TypeError, ValueError):
        return QualificationResult("invalid-receipt")
    now = _now() if now is None else now
    collector, workflow, export, recovery = (
        receipt.collector,
        receipt.workflow,
        receipt.export,
        receipt.recovery,
    )
    if receipt.basis is _Basis.FIXTURE:
        return QualificationResult("fixture-only")
    if not now - _MAX_RECEIPT_AGE <= receipt.observed_at <= now:
        return QualificationResult("stale-receipt")
    if not (
        receipt.registration_cutoff
        <= collector.previous_started
        < collector.previous_heartbeat
        < collector.producer_started
        < collector.activation_heartbeat
        <= collector.heartbeat
        <= receipt.observed_at
        and collector.poll_interval_seconds == _POLL_SECONDS
        and collector.owned_unattended
        and collector.same_process
        and collector.private_state
    ):
        return QualificationResult("service-evidence")
    if receipt.observed_at - collector.heartbeat > _MAX_HEARTBEAT_AGE:
        return QualificationResult("stale-heartbeat")
    if (
        len(receipt.providers) != len(_ROUTES)
        or {entry.provider for entry in receipt.providers} != set(_ROUTES)
        or len({entry.stream for entry in receipt.providers}) != len(_ROUTES)
        or any(
            (entry.route, entry.client_version) != _ROUTES[entry.provider]
            or entry.format_version != 1
            or not entry.offset
            for entry in receipt.providers
        )
    ):
        return QualificationResult("provider-evidence")
    for entry in receipt.providers:
        age = receipt.observed_at - entry.observed_through
        if not (
            receipt.registration_cutoff <= entry.observed_through <= collector.heartbeat
            and age <= _MAX_SOURCE_AGE
            and (
                entry.retention_seconds is None
                or age.total_seconds() < entry.retention_seconds
            )
        ):
            return QualificationResult("source-watermark")
    if (
        len(set(workflow.samples)) != len(workflow.samples)
        or workflow.graduation_sequence > export.cutoff
        or workflow.direct < 2
        or workflow.inclusive
        < workflow.direct + workflow.child_a_direct + workflow.child_b_direct
        or workflow.inclusive > export.rows
    ):
        return QualificationResult("workflow-evidence")
    orders = {(provider, order) for provider in _ROUTES for order in _Order}
    if (
        len(receipt.orders) != len(orders)
        or {(entry.provider, entry.order) for entry in receipt.orders} != orders
        or len({entry.command for entry in receipt.orders}) != len(orders)
        or len({entry.first_request for entry in receipt.orders}) != len(orders)
        or any(
            entry.before_sequence >= entry.after_sequence
            or entry.project_id in (receipt.project_id, recovery.project_id)
            or (
                entry.order is _Order.MARKER_FIRST
                and entry.before_prefix_sha256 == entry.prefix_sha256
            )
            for entry in receipt.orders
        )
    ):
        return QualificationResult("processing-order")
    if (
        export.sha256 != export.replay_sha256
        or export.rows != export.replay_rows
        or export.catchup_codex == export.catchup_claude
        or {export.catchup_codex, export.catchup_claude}.intersection(workflow.samples)
    ):
        return QualificationResult("export-parity")
    if not (
        recovery.project_id != receipt.project_id
        and recovery.rehearsal_version != collector.version
        and recovery.rehearsal_wheel_sha256 != collector.wheel_sha256
        and recovery.started_at
        < recovery.backed_up_at
        < recovery.restored_at
        < recovery.upgraded_at
        < recovery.rolled_back_at
        <= receipt.observed_at
    ):
        return QualificationResult("recovery-evidence")
    if (
        len(
            {
                recovery.before_sha256,
                recovery.restored_sha256,
                recovery.upgraded_sha256,
                recovery.rolled_back_sha256,
            }
        )
        != 1
    ):
        return QualificationResult("recovery-parity")
    return QualificationResult("qualified")


def read_activation_receipt(path: Path) -> ActivationReceipt:
    raw = _read_owned(path.absolute(), private=False, limit=_MAX_EVIDENCE_BYTES)
    if raw is None:
        raise ValueError("Missing activation receipt")
    return decode_activation_receipt(raw)


class QualificationError(ValueError):
    """A failed installed proof check. Messages are fixed public statuses."""


def _require(condition: bool, status: str) -> None:
    if not condition:
        raise QualificationError(status)


def _activation_times(
    evidence: InstallReceipt,
    ledger: Ledger,
    version: str,
    wheel: str,
    interpreter: str,
    dispositions: tuple[str, ...],
) -> tuple[datetime, datetime]:
    _require(
        evidence.project_id == str(ledger.identity.project_id)
        and evidence.label == f"org.aitm.usage.{ledger.identity.project_id}"
        and evidence.status in dispositions
        and evidence.version == version
        and evidence.wheel_sha256 == wheel
        and evidence.interpreter_version == interpreter
        and evidence.poll_interval_seconds == _POLL_SECONDS
        and evidence.producer_mode == "service"
        and type(evidence.producer_pid) is int
        and 0 < evidence.producer_pid < 2**31
        and evidence.producer_started is not None
        and evidence.heartbeat is not None,
        "lifecycle-evidence",
    )
    start = datetime.fromisoformat(evidence.producer_started)
    heartbeat = datetime.fromisoformat(evidence.heartbeat)
    _utc(start, heartbeat)
    _require(start < heartbeat, "lifecycle-evidence")
    return start, heartbeat


def _verify_running(
    ledger: Ledger,
    collector: _CollectorEvidence,
    lifecycle: InstallReceipt,
    launchctl: LaunchControl,
) -> dict:
    start, activation = _activation_times(
        lifecycle,
        ledger,
        collector.version,
        collector.wheel_sha256,
        collector.interpreter_version,
        ("installed", "already-active"),
    )
    _require(
        (start, activation)
        == (collector.producer_started, collector.activation_heartbeat),
        "lifecycle-evidence",
    )
    agent = _Agent(ledger, launchctl)
    control = _guard_path(ledger.root, ledger.identity.project_id).parent
    _require(not _path_exists(control / _record_name(agent)), "recovery-pending")
    plist = agent.read()
    _require(
        bool(plist) and not launchctl.is_disabled(agent.label), "service-unavailable"
    )
    runtime = _runtime_for(agent, agent.program(plist))
    _require(
        (runtime.version, runtime.wheel_sha256, runtime.interpreter_version)
        == (collector.version, collector.wheel_sha256, collector.interpreter_version),
        "wheel-mismatch",
    )

    def checked_status() -> dict:
        result = status_report(ledger.root, ledger)
        _require(result["read_gap"] is False, "ledger-read-gap")
        _require(result["registration_gap"] is False, "registration-gap")
        return result

    checked_status()
    fresh_after = _now() - _MAX_HEARTBEAT_AGE
    first = agent.healthy(runtime, plist, fresh_after)
    _require(first is not None, "service-unhealthy")
    _require(
        (first.process.pid, first.process.started) == (lifecycle.producer_pid, start),
        "process-incarnation",
    )
    status = checked_status()
    _require(
        status["producer_mode"] == "service"
        and status["producer_pid"] == first.process.pid
        and status["collector_version"] == runtime.version
        and status["collector_interpreter_version"] == runtime.interpreter_version
        and status["heartbeat"] is not None
        and status["status_sequence"] is not None,
        "service-unhealthy",
    )
    _require(
        type(status["invalid_inbox"]) is int
        and status["invalid_inbox"] == 0
        and status["relationship_halted"] is False,
        "inbox-gap",
    )
    heartbeat = datetime.fromisoformat(status["heartbeat"])
    last = agent.healthy(runtime, plist, _now() - _MAX_HEARTBEAT_AGE)
    _require(
        last is not None
        and last.process == first.process
        and datetime.fromisoformat(first.heartbeat)
        <= heartbeat
        <= datetime.fromisoformat(last.heartbeat)
        and collector.heartbeat <= heartbeat
        and not launchctl.is_disabled(agent.label)
        and not _path_exists(control / _record_name(agent)),
        "service-changed",
    )
    return status


def _read_proof(path: Path, limit: int = _MAX_EVIDENCE_BYTES) -> bytes:
    data = _read_owned(path, private=True, limit=limit)
    if data is None:
        raise QualificationError("proof-unavailable")
    return data


def _digest(ref: SourceRef) -> str:
    return ref.value.split(":")[1]


def _usage(view: LedgerView) -> dict[str, UsageObservation]:
    usage = {}
    logical = set()
    for entry in view.current:
        if not isinstance(record := entry.record, UsageObservation):
            continue
        boundary = record.boundary
        identity = (
            boundary.provider,
            boundary.session_ref,
            boundary.epoch_ref if boundary.provider is Provider.CODEX else None,
            record.request_ref or (boundary.stream_ref, boundary.ordinal),
        )
        key = _digest(entry.key)
        _require(key not in usage and identity not in logical, "duplicate-observation")
        usage[key] = record
        logical.add(identity)
    return usage


def _verify_exports(
    view: LedgerView, card: RateCard, digest: str, rows: int, snapshots: tuple[str, ...]
) -> None:
    _usage(view)
    result, files = _render(view, card)
    _require(
        result.sha256 == digest
        and result.row_count == rows
        and len(set(snapshots)) == len(snapshots),
        "export-parity",
    )
    pins = set()
    for path in snapshots:
        try:
            with _pin_directory(Path(path)) as snapshot:
                _require(snapshot.identities[-1] not in pins, "export-parity")
                pins.add(snapshot.identities[-1])
                _check_snapshot(snapshot, files)
        except (OSError, LedgerError):
            raise QualificationError("export-parity") from None


@dataclass(frozen=True, slots=True)
class _OrderProof:
    root: str
    publication: str
    source: str
    prefix_bytes: int
    before_status: str
    after_status: str
    before_source: str
    before_prefix_bytes: int
    before_captured_at: datetime
    before_confirmed_at: datetime
    publication_released_at: datetime | None

    def __post_init__(self) -> None:
        _positive(self.prefix_bytes)
        _nonnegative(self.before_prefix_bytes)
        _utc(self.before_captured_at, self.before_confirmed_at)
        if self.publication_released_at is not None:
            _utc(self.publication_released_at)


def _snapshot_status(ledger: Ledger, view: LedgerView, path: str) -> _Status:
    raw = _read_proof(Path(path))
    status = _decode(raw, _Status, validate_ref=ledger.validate_source_ref)
    _require(_encode(status, _Status).encode() == raw, "status-proof")
    _check_status_context(ledger, view, status)
    return status


def _check_status_context(ledger: Ledger, view: LedgerView, status: _Status) -> None:
    _, config = _effective_registration(ledger, view)
    _require(
        status.project_id == view.project_id
        and status.configuration_ref
        == _registration_revision(ledger, config).record.configuration_ref
        and status.report.sequence == view.sequence
        and config.cutoff <= status.heartbeat <= _now(),
        "status-proof",
    )


def _verify_order(
    entry: _OrderEvidence,
    proof: _OrderProof,
    card: RateCard,
    *,
    observed_at: datetime | None = None,
) -> None:
    ledger = Ledger.open(Path(proof.root), entry.project_id)
    before = ledger.as_of(entry.before_sequence)
    after = ledger.as_of(entry.after_sequence)
    status = _snapshot_status(ledger, before, proof.before_status)
    settled = _snapshot_status(ledger, after, proof.after_status)
    observed_at = _now() if observed_at is None else observed_at
    _require(
        status.producer_mode is settled.producer_mode is _ProducerMode.ONE_SHOT
        and proof.before_captured_at
        <= status.heartbeat
        <= proof.before_confirmed_at
        <= settled.heartbeat
        <= observed_at
        and settled.report.held_sources == settled.report.deferred_sources == 0
        and status.report.root_gaps
        == status.report.missing_sources
        == status.report.deferred_sources
        == status.report.invalid_inbox
        == 0
        and status.report.relationship_halted is False,
        "processing-order",
    )
    raw = _read_proof(Path(proof.publication), MAX_COMMAND_BYTES)
    published = _decode_publication(raw)
    command = published.command
    marker = command.payload
    key = ledger.pseudonymize("inbox-command", str(command.command_id))
    _require(
        isinstance(marker, ScopeMarker)
        and marker.item == ItemKey(ItemKind.ISSUE, 83)
        and marker.boundary_kind is BoundaryKind.REQUEST
        and marker.provider is entry.provider
        and marker.published_at <= proof.before_captured_at
        and published.order is None
        and _digest(key) == entry.command
        and sha256(raw).hexdigest() == entry.publication_sha256
        and _publication_bytes(command, None) == raw,
        "processing-order",
    )
    digest = ledger.validate_command(command)

    def recorded(view: LedgerView) -> CommandReceipt | None:
        return next(
            (
                revision.record
                for revision in view.current
                if revision.key == key and isinstance(revision.record, CommandReceipt)
            ),
            None,
        )

    prior, final = recorded(before), recorded(after)
    _require(
        final is not None
        and final.command == command
        and final.digest == digest
        and final.disposition is MarkerDisposition.ACCEPTED
        and final.boundary is not None
        and attest_marker(marker, final.boundary) is MarkerDisposition.ACCEPTED,
        "processing-order",
    )
    boundary = final.boundary
    usage = _usage(after).get(entry.first_request)
    _require(
        usage is not None
        and usage.boundary == boundary
        and usage.availability is not Availability.UNKNOWN
        and entry.first_request not in _usage(before),
        "processing-order",
    )
    enrollment = resolve_scope(usage, after).scope
    _require(
        enrollment is not None
        and enrollment.marker == marker
        and enrollment.boundary == boundary,
        "processing-order",
    )

    registration, config = _effective_registration(ledger, before)
    candidates = tuple(
        candidate
        for candidate in discover(registration)
        if candidate.stream_ref == boundary.stream_ref
        and candidate._path == Path(proof.source)
    )
    _require(len(candidates) == 1, "processing-order")
    candidate = candidates[0]
    checkpoint = next(
        (
            cp
            for cp in before.checkpoints
            if cp.cursor.source_ref == candidate.stream_ref
        ),
        None,
    )
    source = _read_proof(candidate._path, _MAX_PREFIX_BYTES)
    prefix = source[: proof.prefix_bytes]
    captured = Path(proof.before_source)
    before_prefix = _read_proof(captured, _MAX_PREFIX_BYTES)
    captured_info = captured.stat(follow_symlinks=False)
    _require(
        len(prefix) == proof.prefix_bytes
        and prefix.endswith(b"\n")
        and sha256(prefix).hexdigest() == entry.prefix_sha256
        and len(before_prefix) == proof.before_prefix_bytes
        and (not before_prefix or before_prefix.endswith(b"\n"))
        and sha256(before_prefix).hexdigest() == entry.before_prefix_sha256
        and prefix.startswith(before_prefix)
        and all(not captured.is_relative_to(root) for root in registration.source_roots)
        and not captured.samefile(candidate._path)
        and max(
            captured_info.st_mtime,
            captured_info.st_ctime,
            getattr(captured_info, "st_birthtime", captured_info.st_ctime),
        )
        <= proof.before_captured_at.timestamp()
        and (checkpoint is None or checkpoint.cursor.offset <= len(before_prefix)),
        "processing-order",
    )
    # Reuse the collector's discovery, scanner and adapter projection. This only
    # reads input and never commits a checkpoint, admits a command or starts a job.
    projection = _Collector(ledger, card, status.producer_mode)._project(
        candidate,
        checkpoint,
        before,
        _enrollments(before).get(candidate.stream_ref, ()),
        config,
    )
    frame = projection.batch._matching_frame(boundary)
    # The native adapter binds the current request to its preceding receipt.
    # This is the exact byte prefix through that authenticated request frame.
    target_prefix = b"\n".join(prefix.split(b"\n", boundary.ordinal + 1)[:-1]) + b"\n"
    _require(
        frame is not None
        and registration.cutoff
        <= marker.published_at
        <= frame.observed_at
        <= observed_at
        and boundary.ordinal < prefix.count(b"\n")
        and frame._prefix == sha256(target_prefix).hexdigest()
        and any(entry.boundary == boundary for entry in projection.evidence())
        and source == _read_proof(candidate._path, _MAX_PREFIX_BYTES)
        and before_prefix == _read_proof(captured, _MAX_PREFIX_BYTES),
        "processing-order",
    )
    if entry.order is _Order.MARKER_FIRST:
        _require(
            prior is not None
            and prior.command == command
            and prior.digest == digest
            and prior.disposition is MarkerDisposition.PENDING
            and prior.boundary is None
            and status.report.held_sources == 0
            and len(before_prefix) < len(target_prefix)
            and proof.publication_released_at is None,
            "processing-order",
        )
    else:
        _require(
            prior is None
            and status.report.held_sources == 1
            and checkpoint is not None
            and before_prefix.startswith(target_prefix)
            and frame.observed_at <= proof.before_captured_at
            and proof.publication_released_at is not None
            and proof.before_confirmed_at
            <= proof.publication_released_at
            <= settled.heartbeat
            and projection.batch.cursor == checkpoint.cursor
            and frame.boundary_only,
            "processing-order",
        )


def _verify_workflow(
    ledger: Ledger,
    view: LedgerView,
    evidence: _Workflow,
    cutoff: datetime,
    observed_at: datetime,
) -> tuple[UsageObservation, UsageObservation]:
    observations = _usage(view)
    _require(all(key in observations for key in evidence.samples), "workflow-evidence")
    (
        batch,
        child_a,
        child_b,
        returned,
        review_start,
        review_end,
        development,
        housekeeping,
    ) = (observations[key] for key in evidence.samples)
    _require(
        all(
            cutoff <= entry.observed_at <= observed_at
            and entry.availability is not Availability.UNKNOWN
            and entry.client_version is _ROUTES[entry.boundary.provider][1]
            and entry.format_version == 1
            for entry in (observations[key] for key in evidence.samples)
        ),
        "workflow-evidence",
    )
    registration, _ = _effective_registration(ledger, view)
    anchors = {
        checkout_anchor_reference(ledger, checkout)
        for checkout in registration.checkout_anchors
    }
    accepted = {
        revision.record.command.command_id: revision.record
        for revision in view.current
        if isinstance(revision.record, CommandReceipt)
        and revision.record.disposition is MarkerDisposition.ACCEPTED
    }

    def scope_for(usage: UsageObservation, *, first: bool = True) -> ScopeEnrollment:
        scope = resolve_scope(usage, view).scope
        _require(scope is not None, "workflow-evidence")
        receipt = accepted.get(scope.marker.marker_id)
        expected = scope.marker
        if scope.generation is not None:
            expected = DevelopmentBinding(
                scope.marker, scope.anchor_ref, scope.generation
            )
        _require(
            receipt is not None
            and receipt.command.payload == expected
            and receipt.digest == ledger.validate_command(receipt.command)
            and receipt.boundary == scope.boundary
            and attest_marker(scope.marker, scope.boundary)
            is MarkerDisposition.ACCEPTED
            and (not first or scope.boundary == usage.boundary)
            and scope.marker.published_at <= usage.observed_at,
            "workflow-evidence",
        )
        return scope

    planning = tuple(scope_for(entry) for entry in (batch, child_a, child_b, returned))
    author = planning[0]
    epic = ItemKey(ItemKind.ISSUE, 83)
    draft_a, draft_b = planning[1].marker.item, planning[2].marker.item
    _require(
        author.marker.item == planning[3].marker.item == epic
        and draft_a.kind is draft_b.kind is ItemKind.DRAFT
        and draft_a != draft_b
        and author.anchor_ref in anchors
        and all(
            scope.anchor_ref == author.anchor_ref
            and scope.marker.participant_ref == author.marker.participant_ref
            and scope.marker.provider is Provider.CODEX
            and scope.marker.session_ref == author.marker.session_ref
            and scope.boundary.stream_ref == author.boundary.stream_ref
            and scope.marker.phase is WorkPhase.PLANNING
            and scope.marker.role is ReviewRole.AUTHOR
            for scope in planning
        )
        and all(
            left.boundary.ordinal < right.boundary.ordinal
            and left.marker.scope_sequence < right.marker.scope_sequence
            for left, right in zip(planning, planning[1:])
        )
        and batch.observed_at
        <= child_a.observed_at
        <= child_b.observed_at
        <= returned.observed_at,
        "workflow-evidence",
    )

    reviewer = scope_for(review_start)
    _require(
        reviewer == scope_for(review_end, first=False)
        and reviewer.marker.provider is Provider.CLAUDE
        and reviewer.marker.role is ReviewRole.REVIEWER
        and reviewer.marker.phase is WorkPhase.DOCUMENT_REVIEW
        and reviewer.marker.review_ref is not None
        and reviewer.marker.participant_ref != author.marker.participant_ref
        and reviewer.marker.item in (epic, draft_a, draft_b)
        and review_start.boundary.ordinal < review_end.boundary.ordinal
        and review_start.observed_at < review_end.observed_at
        and max(batch.observed_at, review_start.observed_at)
        < min(returned.observed_at, review_end.observed_at),
        "workflow-evidence",
    )

    aliases, parents = canonical_relationships(view)
    just_before = ledger.as_of(evidence.graduation_sequence - 1)
    graduation = ledger.as_of(evidence.graduation_sequence)
    previous_aliases, _ = canonical_relationships(just_before)
    graduation_aliases, _ = canonical_relationships(graduation)
    target = graduation_aliases.get(draft_a)
    _require(
        target is not None
        and target != epic
        and target.kind is ItemKind.ISSUE
        and target.identifier in _DISPOSABLE_ISSUES
        and draft_a not in previous_aliases
        and aliases.get(draft_a) == target
        and draft_b not in aliases
        and parents.get(target) == parents.get(draft_b) == epic
        and all(key in _usage(just_before) for key in evidence.samples[:4])
        and rollup(target, just_before).direct.observation_count == 0
        and rollup(draft_a, just_before).direct == rollup(target, graduation).direct,
        "workflow-evidence",
    )

    def in_epic(item: ItemKey) -> bool:
        cursor = aliases.get(item, item)
        while cursor != epic and cursor in parents:
            cursor = parents[cursor]
        return cursor == epic

    # Relationship entries describe attribution. Only this leaf's authorized
    # real scopes and its two designated drafts can authorize the controlled run.
    approved = {epic, ItemKey(ItemKind.ISSUE, 96), draft_a, draft_b, target}
    _require(
        epic not in parents
        and all(item in approved for item in parents if in_epic(item))
        and all(draft == draft_a for draft, issue in aliases.items() if in_epic(issue)),
        "workflow-evidence",
    )
    owner = scope_for(development)
    maintenance = scope_for(housekeeping)
    _require(
        owner.marker.phase is WorkPhase.DEVELOPMENT
        and owner.generation is not None
        and owner.anchor_ref in anchors
        and owner.anchor_ref != author.anchor_ref
        and owner.marker.attempt_ref is not None
        and owner.marker.item in approved
        and in_epic(owner.marker.item)
        and maintenance.marker.phase is WorkPhase.HOUSEKEEPING
        and maintenance.marker.item in approved
        and in_epic(maintenance.marker.item),
        "workflow-evidence",
    )
    totals = rollup(epic, view)
    _require(
        (
            totals.direct.observation_count,
            totals.inclusive.observation_count,
            rollup(draft_a, view).direct.observation_count,
            rollup(draft_b, view).direct.observation_count,
        )
        == (
            evidence.direct,
            evidence.inclusive,
            evidence.child_a_direct,
            evidence.child_b_direct,
        ),
        "workflow-evidence",
    )
    return batch, review_start


@dataclass(frozen=True, slots=True)
class _BackupProof:
    status: str
    project_id: str
    key_id: str
    schema_version: int
    sequence: int
    manifest_sha256: str


@dataclass(frozen=True, slots=True)
class _RecoveryProof:
    root: str
    bundle: str
    initial: InstallReceipt
    stop: InstallReceipt
    backup: _BackupProof
    restore: _BackupProof
    resumed: InstallReceipt
    upgrade: InstallReceipt
    rollback: InstallReceipt
    before: str
    restored: str
    upgraded: str
    rolled_back: str


def _verify_bundle(ledger: Ledger, path: Path, receipt: _BackupProof) -> None:
    identity = ledger.identity
    _require(
        receipt.project_id == str(identity.project_id)
        and receipt.key_id == identity.key_id
        and receipt.schema_version == identity.schema_version,
        "recovery-evidence",
    )
    raw = _read_proof(path / _MANIFEST)
    _require(sha256(raw).hexdigest() == receipt.manifest_sha256, "recovery-parity")
    manifest = json.loads(raw, object_pairs_hook=_unique_fields)
    _require(type(manifest) is dict, "recovery-parity")
    files = manifest.get("files")
    expected = {
        _KEY,
        _DATABASE,
        *_authority_names(ledger, ledger.as_of(receipt.sequence)),
    }
    _require(type(files) is dict and files.keys() == expected, "recovery-parity")
    body = {
        "format": "aitm-usage.backup/v1",
        "project_id": receipt.project_id,
        "key_id": receipt.key_id,
        "schema_version": receipt.schema_version,
        "sequence": receipt.sequence,
        "files": files,
    }
    tag = ledger.pseudonymize("collector-backup-manifest", _json(body).decode())
    _require(raw == _json({**body, "proof": tag.value}), "recovery-parity")
    for name, digest in files.items():
        data = _read_proof(path / name, 128 * 1024 * 1024)
        _require(sha256(data).hexdigest() == digest, "recovery-parity")


def _stopped(ledger: Ledger, evidence: InstallReceipt) -> bool:
    project_id = str(ledger.identity.project_id)
    return evidence == InstallReceipt(
        project_id, f"org.aitm.usage.{project_id}", "stopped"
    )


def _verify_recovery(
    evidence: _RecoveryEvidence,
    proof: _RecoveryProof,
    collector: _CollectorEvidence,
    card: RateCard,
) -> None:
    ledger = Ledger.open(Path(proof.root), evidence.project_id)
    load_registration(ledger)
    interpreter = collector.interpreter_version
    primary = (collector.version, collector.wheel_sha256, interpreter)
    sibling = (evidence.rehearsal_version, evidence.rehearsal_wheel_sha256, interpreter)
    started, installed = _activation_times(
        proof.initial, ledger, *primary, ("installed",)
    )
    resumed, resumed_heartbeat = _activation_times(
        proof.resumed, ledger, *primary, ("installed",)
    )
    upgrade_start, upgraded = _activation_times(
        proof.upgrade, ledger, *sibling, ("upgraded",)
    )
    rollback_start, rolled_back = _activation_times(
        proof.rollback, ledger, *primary, ("upgraded",)
    )
    _require(
        started == evidence.started_at
        and upgraded == evidence.upgraded_at
        and rolled_back == evidence.rolled_back_at
        and installed
        <= evidence.backed_up_at
        < evidence.restored_at
        <= resumed
        < resumed_heartbeat
        < upgrade_start
        < upgraded
        < rollback_start
        and _stopped(ledger, proof.stop)
        and proof.backup.status == "backed-up"
        and proof.restore.status == "restored"
        and proof.backup.project_id == proof.restore.project_id
        and proof.backup.key_id == proof.restore.key_id
        and proof.backup.schema_version == proof.restore.schema_version
        and proof.backup.sequence == proof.restore.sequence == evidence.cutoff
        and proof.backup.manifest_sha256
        == proof.restore.manifest_sha256
        == evidence.backup_manifest_sha256,
        "recovery-evidence",
    )
    _verify_bundle(ledger, Path(proof.bundle), proof.backup)
    for activation in (proof.upgrade, proof.rollback):
        _require(
            activation.backup_id is not None
            and activation.backup_id == str(UUID(activation.backup_id))
            and activation.backup is not None
            and activation.backup.sequence >= evidence.cutoff,
            "recovery-evidence",
        )
        bundle = ledger.root / "service-backups" / activation.backup_id
        _verify_bundle(
            ledger, bundle, _BackupProof("backed-up", **activation.backup.as_dict())
        )
    _require(proof.upgrade.backup_id != proof.rollback.backup_id, "recovery-evidence")

    def wheel_sources(version: str, digest: str) -> dict[Path, bytes]:
        verified = _wheel(_wheel_path(ledger, version, digest), digest, private=True)
        return {
            path: data
            for path, data in verified.files.items()
            if path.parts[0] == "aitm_usage"
        }

    _require(
        wheel_sources(*primary[:2]) == wheel_sources(*sibling[:2]),
        "recovery-wheel-source",
    )
    _verify_exports(
        ledger.as_of(evidence.cutoff),
        card,
        evidence.before_sha256,
        evidence.rows,
        (proof.before, proof.restored, proof.upgraded, proof.rolled_back),
    )


@dataclass(frozen=True, slots=True)
class _ActivationProof:
    schema: str
    source_commit: str
    approved_wheel_sha256: str
    previous_lifecycle: InstallReceipt
    previous_stop: InstallReceipt
    lifecycle: InstallReceipt
    previous_status: str
    status: str
    export_before: str
    export_replay: str
    orders: tuple[_OrderProof, ...]
    recovery: _RecoveryProof


def _capture(
    ledger: Ledger, path: str, lifecycle: InstallReceipt, heartbeat: datetime
) -> tuple[LedgerView, _Status]:
    raw = _read_proof(Path(path))
    status = _decode(raw, _Status, validate_ref=ledger.validate_source_ref)
    view = ledger.as_of(status.report.sequence)
    _check_status_context(ledger, view, status)
    _require(
        _encode(status, _Status).encode() == raw
        and status.producer_mode.value == "service"
        and status.producer_pid == lifecycle.producer_pid
        and status.collector_version == lifecycle.version
        and status.collector_interpreter_version == lifecycle.interpreter_version
        and status.heartbeat == heartbeat
        and status.report.invalid_inbox == 0
        and status.report.relationship_halted is False,
        "status-proof",
    )
    return view, status


def _verify_watermarks(
    ledger: Ledger,
    view: LedgerView,
    captured: _Status,
    current: dict,
    entries: tuple[_ProviderEvidence, ...],
) -> None:
    checks = {_digest(entry.cursor.source_ref): entry for entry in view.checkpoints}
    witnesses = {_digest(entry.source_ref): entry for entry in captured.observed}
    live = {
        _digest(SourceRef(entry["source_ref"])): entry for entry in current["sources"]
    }
    for evidence in entries:
        checkpoint = checks.get(evidence.stream)
        witness = witnesses.get(evidence.stream)
        actual = live.get(evidence.stream)
        _require(
            checkpoint is not None
            and witness is not None
            and actual is not None
            and checkpoint.provider.provider is evidence.provider
            and checkpoint.provider.client_version is evidence.client_version
            and checkpoint.provider.format_version == evidence.format_version
            and checkpoint.cursor.offset == evidence.offset
            and witness.through == evidence.observed_through
            and witness.proof == _observed_proof(ledger, checkpoint, witness.through)
            and actual["provider"] == evidence.provider.value
            and actual["client_version"] == evidence.client_version.value
            and actual["format_version"] == evidence.format_version
            and actual["offset"] >= evidence.offset
            and actual["retention_seconds"] == evidence.retention_seconds
            and actual["observed_through"] is not None,
            "source-watermark",
        )
        through = datetime.fromisoformat(actual["observed_through"])
        age = _now() - through
        _require(
            evidence.observed_through
            <= through
            <= datetime.fromisoformat(current["heartbeat"])
            and timedelta(0) <= age <= _MAX_SOURCE_AGE
            and (
                evidence.retention_seconds is None
                or age.total_seconds() < evidence.retention_seconds
            ),
            "source-watermark",
        )


def _verify_selected_sources(
    ledger: Ledger,
    view: LedgerView,
    entries: tuple[_ProviderEvidence, ...],
    card: RateCard,
) -> None:
    registration, config = _effective_registration(ledger, view)
    selected = {entry.stream for entry in entries}
    checkpoints = {
        _digest(checkpoint.cursor.source_ref): checkpoint
        for checkpoint in view.checkpoints
        if _digest(checkpoint.cursor.source_ref) in selected
    }
    _require(checkpoints.keys() == selected, "selected-source-gap")
    sources = tuple(discover(registration))
    scopes = _enrollments(view)
    collector = _Collector(ledger, card, _ProducerMode.SERVICE)
    fatal = {
        DiagnosticCode.SOURCE_REPLACED,
        DiagnosticCode.SOURCE_UNAVAILABLE,
        DiagnosticCode.OVERLAP_UNVERIFIED,
        DiagnosticCode.UNSUPPORTED_FORMAT,
        DiagnosticCode.BOUNDARY_UNVERIFIED,
        DiagnosticCode.IDENTITY_CONFLICT,
        DiagnosticCode.COUNTER_REGRESSION,
    }
    for checkpoint in checkpoints.values():
        reference = checkpoint.cursor.source_ref
        candidate = _candidate(
            [item for item in sources if item.stream_ref == reference], checkpoint
        )
        _require(candidate is not None, "selected-source-gap")
        projection = collector._project(
            candidate, checkpoint, view, scopes.get(reference, ()), config
        )
        _require(
            projection.batch.cursor is not None
            and not any(frame.boundary_only for frame in projection.batch.frames)
            and not any(
                diagnostic.code in fatal for diagnostic in projection.result.diagnostics
            ),
            "selected-source-gap",
        )


def _verify_relationship_continuity(before: LedgerView, after: LedgerView) -> None:
    _require(
        canonical_relationships(before) == canonical_relationships(after),
        "relationship-changed",
    )


def _verify_catchup(
    receipt: ActivationReceipt, before: LedgerView, after: LedgerView
) -> None:
    _verify_relationship_continuity(before, after)
    previous, current = _usage(before), _usage(after)
    _require(previous.keys() <= current.keys(), "replay-evidence")
    approved_scopes = {
        resolve_scope(previous[key], before).scope
        for key in receipt.workflow.samples
        if key in previous
    } - {None}
    keys = {
        Provider.CODEX: receipt.export.catchup_codex,
        Provider.CLAUDE: receipt.export.catchup_claude,
    }
    for provider in receipt.providers:
        key = keys[provider.provider]
        usage = current.get(key)
        _require(
            key not in previous
            and usage is not None
            and usage.boundary.provider is provider.provider
            and _digest(usage.boundary.stream_ref) == provider.stream
            and usage.availability is not Availability.UNKNOWN
            and resolve_scope(usage, after).scope in approved_scopes
            and receipt.collector.previous_heartbeat
            < usage.observed_at
            < receipt.collector.producer_started,
            "replay-evidence",
        )


def _pinned_frames(
    source: CandidateSource,
    checkpoint: SourceCheckpoint,
    cutoff: datetime,
):
    # First verify the actual source prefix at the fixed historical frontier.
    if scan(source, checkpoint, cutoff).cursor is None:
        return ()
    return scan(source, None, cutoff).frames


def _verify_live_coverage(
    ledger: Ledger,
    view: LedgerView,
    evidence: _ProviderEvidence,
    cutoff: datetime,
) -> None:
    observations = tuple(_usage(view).values())
    selected = [
        item
        for item in observations
        if item.boundary.provider is evidence.provider
        and _digest(item.boundary.stream_ref) == evidence.stream
        and item.observed_at >= cutoff
    ]
    models = {item.model for item in selected if item.model is not ModelLabel.UNKNOWN}
    efforts = {item.effort for item in selected if item.effort is not None}
    _require(
        (evidence.coverage.model_switch is _Metric.OBSERVED) == (len(models) > 1)
        and (evidence.coverage.effort_switch is _Metric.OBSERVED) == (len(efforts) > 1),
        "coverage-evidence",
    )
    retry = evidence.coverage.retry is _Metric.OBSERVED
    nested = evidence.coverage.nested is _Metric.OBSERVED
    if not (retry or nested):
        return
    _require(bool(selected), "coverage-evidence")
    primary = selected[0].boundary
    if nested and evidence.provider is Provider.CLAUDE:
        stream = _isolation(ledger, primary.stream_ref, "nested")
        _require(
            any(
                item.boundary.provider is Provider.CLAUDE
                and item.boundary.session_ref == primary.session_ref
                and item.boundary.stream_ref == stream
                and item.observed_at >= cutoff
                and item.availability is not Availability.UNKNOWN
                for item in observations
            ),
            "coverage-evidence",
        )
        nested = False
    if not (retry or nested):
        return
    registration, _ = _effective_registration(ledger, view)
    checkpoints = {entry.cursor.source_ref: entry for entry in view.checkpoints}
    sources = {
        source.stream_ref: source
        for source in discover(registration)
        if source.stream_ref in checkpoints
        and source.incarnation_ref
        == checkpoints[source.stream_ref].cursor.incarnation_ref
    }
    if retry:
        _require(primary.stream_ref in sources, "coverage-evidence")
        frames = _pinned_frames(
            sources[primary.stream_ref], checkpoints[primary.stream_ref], cutoff
        )
        first = min(item.boundary.ordinal for item in selected)
        last = max(item.boundary.ordinal for item in selected)
        _require(
            any(
                first < frame.ordinal < last
                and not frame.pre_cutoff
                and (
                    (
                        evidence.provider is Provider.CODEX
                        and frame.row["type"] == "event_msg"
                        and _object(frame.row.get("payload")).get("type")
                        in _ATTEMPT_ERRORS
                    )
                    or (
                        evidence.provider is Provider.CLAUDE
                        and frame.row["type"] == "result"
                        and frame.row.get("is_error") is True
                    )
                )
                for frame in frames
            ),
            "coverage-evidence",
        )
    if nested:
        child_streams = {
            item.boundary.stream_ref
            for item in observations
            if item.boundary.provider is Provider.CODEX
            and item.boundary.session_ref != primary.session_ref
            and item.observed_at >= cutoff
            and item.availability is not Availability.UNKNOWN
        }
        _require(
            any(
                _codex_child(frame.row, ledger, primary.session_ref)
                for stream in child_streams.intersection(sources)
                for frame in _pinned_frames(
                    sources[stream], checkpoints[stream], cutoff
                )
            ),
            "coverage-evidence",
        )


def _codex_child(row: dict, ledger: Ledger, parent: SourceRef) -> bool:
    if row["type"] != "session_meta":
        return False
    metadata = _object(row.get("payload"))
    spawn = _object(
        _object(_object(metadata.get("source")).get("subagent")).get("thread_spawn")
    )
    raw = metadata.get("parent_thread_id")
    try:
        return (
            metadata.get("thread_source") == "subagent"
            and metadata.get("history_mode") == "paginated"
            and raw == spawn.get("parent_thread_id")
            and session_reference(ledger, Provider.CODEX, raw) == parent
        )
    except ValueError:
        return False


def verify_installed_activation(
    receipt: ActivationReceipt, ledger: Ledger, launchctl: LaunchControl
) -> QualificationResult:
    """Bind a sanitized receipt to private evidence and the current registered service."""
    result = validate_activation_receipt(receipt)
    if not result.qualified:
        return result
    _require(ledger.identity.project_id == receipt.project_id, "project-mismatch")
    try:
        registration = load_registration(ledger)
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        raise QualificationError("registration-gap") from None
    _require(
        registration.cutoff == receipt.registration_cutoff, "registration-mismatch"
    )
    proof = _decode(_read_proof(ledger.root / PROOF_NAME), _ActivationProof)
    collector = receipt.collector
    _require(
        proof.schema == "aitm-usage-activation-proof/v1"
        and proof.source_commit == receipt.source_commit
        and proof.approved_wheel_sha256 == collector.wheel_sha256
        and len(proof.orders) == len(receipt.orders),
        "proof-mismatch",
    )

    previous_start, previous_heartbeat = _activation_times(
        proof.previous_lifecycle,
        ledger,
        collector.version,
        collector.wheel_sha256,
        collector.interpreter_version,
        ("installed",),
    )
    _require(
        previous_start == collector.previous_started
        and previous_heartbeat <= collector.previous_heartbeat
        and _stopped(ledger, proof.previous_stop),
        "restart-evidence",
    )
    before, _ = _capture(
        ledger,
        proof.previous_status,
        proof.previous_lifecycle,
        collector.previous_heartbeat,
    )
    after, captured = _capture(
        ledger, proof.status, proof.lifecycle, collector.heartbeat
    )
    _require(
        before.sequence == receipt.export.cutoff and after.sequence > before.sequence,
        "export-cutoff",
    )

    card = load_rate_card()
    _verify_exports(
        before,
        card,
        receipt.export.sha256,
        receipt.export.rows,
        (proof.export_before, proof.export_replay),
    )
    batch, review = _verify_workflow(
        ledger, before, receipt.workflow, registration.cutoff, receipt.observed_at
    )
    streams = {item.provider: item.stream for item in receipt.providers}
    _require(
        streams[Provider.CODEX] == _digest(batch.boundary.stream_ref)
        and streams[Provider.CLAUDE] == _digest(review.boundary.stream_ref),
        "provider-evidence",
    )
    _verify_catchup(receipt, before, after)
    for provider in receipt.providers:
        _verify_live_coverage(ledger, after, provider, registration.cutoff)
    for entry, private in zip(receipt.orders, proof.orders, strict=True):
        _verify_order(entry, private, card, observed_at=receipt.observed_at)
    _verify_recovery(receipt.recovery, proof.recovery, collector, card)

    # Inspect the live process after reading historical evidence and selected sources.
    live_view = ledger.as_of()
    _verify_selected_sources(ledger, live_view, receipt.providers, card)
    current = _verify_running(ledger, collector, proof.lifecycle, launchctl)
    _require(
        current["status_sequence"] >= captured.report.sequence
        and current["sequence"] >= live_view.sequence
        and load_registration(ledger) == registration,
        "service-changed",
    )
    _verify_watermarks(ledger, after, captured, current, receipt.providers)
    _verify_relationship_continuity(after, ledger.as_of())
    return validate_activation_receipt(receipt)
