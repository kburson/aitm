"""Private registration, guarded source collection, and lease-free status."""

import json
import os
import platform
import re
import sqlite3
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

from .accounting import account_observations
from .ledger import ConflictError, Ledger, LedgerError, _pin_directory
from .pricing import RateCard, load_rate_card
from .rollup import _prices
from .scopes import (
    MAX_COMMAND_BYTES,
    BoundaryEvidence,
    _private_child,
    _publish,
    _read_private,
    drain_inbox,
    session_reference,
)
from .sources.claude import ClaudeState, advance_claude_state, read_claude
from .sources.codex import CodexState, advance_codex_state, read_codex
from .sources.scan import (
    CandidateSource,
    FrameBatch,
    checkout_anchor_reference,
    discover,
    scan,
)
from .types import (
    AccountObservation,
    AdapterResult,
    Availability,
    CommandReceipt,
    Diagnostic,
    DiagnosticCode,
    Eligibility,
    InboxCommand,
    LedgerBatch,
    LedgerView,
    MarkerDisposition,
    ProjectRegistration,
    Provider,
    Registration,
    Revision,
    ScopeEnrollment,
    SourceAnchor,
    SourceAnchorCommand,
    SourceCheckpoint,
    SourceRef,
    UsageObservation,
    _decode,
    _encode,
    _unique_fields,
)

REGISTRATION_NAME = "registration.json"
ANCHORS_NAME = "source-anchors"
CLAUDE_SESSIONS_NAME = "claude-sessions"
STATUS_NAME = "status.json"
_STATUS_SOURCE_LIMIT = 128


@dataclass(frozen=True, slots=True)
class _AccountAuthority:
    provider: Provider
    stream_ref: SourceRef
    account_ref: SourceRef


@dataclass(frozen=True, slots=True)
class _RetentionLimit:
    provider: Provider
    seconds: int

    def __post_init__(self) -> None:
        if not 0 < self.seconds < 2**63:
            raise ValueError("Expected a positive retention limit")


@dataclass(frozen=True, slots=True)
class _Config:
    project_id: UUID
    source_roots: tuple[str, ...]
    checkout_anchors: tuple[str, ...]
    cutoff: datetime
    excluded_segments: tuple[SourceRef, ...]
    account_refs: tuple[_AccountAuthority, ...]
    retention_limits: tuple[_RetentionLimit, ...]


@dataclass(frozen=True, slots=True)
class _AnchorProposal:
    command_id: UUID
    project_id: UUID
    checkout: str


def _path(value: str, *, existing: bool) -> Path:
    path = Path(value)
    if (
        not path.is_absolute()
        or ".." in path.parts
        or str(path) != value
        or "\0" in value
    ):
        raise ValueError("Expected a canonical absolute directory")
    if existing and not _directory_available(path):
        raise ValueError("Expected an available canonical directory")
    return path


def _directory_available(path: Path) -> bool:
    try:
        return (
            path.resolve(strict=True) == path
            and path.is_dir()
            and os.access(path, os.R_OK | os.X_OK)
        )
    except (OSError, ValueError, RuntimeError):
        return False


def _input[T](path: Path, model: type[T], **defaults: object) -> T:
    with path.open("rb") as handle:
        raw = handle.read(MAX_COMMAND_BYTES + 1)
    if len(raw) > MAX_COMMAND_BYTES:
        raise ValueError("Private configuration is too large")
    data = json.loads(raw, object_pairs_hook=_unique_fields)
    if type(data) is not dict:
        raise ValueError("Expected a private configuration object")
    return _decode(json.dumps({**defaults, **data}), model)


def _checked_config(config: _Config, *, existing: bool) -> _Config:
    if not config.source_roots:
        raise ValueError("An approved source root is required")
    for paths in (config.source_roots, config.checkout_anchors):
        if len(set(paths)) != len(paths):
            raise ValueError("Duplicate registration directory")
        for raw in paths:
            _path(raw, existing=existing)
    if len(set(config.excluded_segments)) != len(config.excluded_segments):
        raise ValueError("Duplicate exclusion selector")
    if len(
        {(entry.provider, entry.stream_ref) for entry in config.account_refs}
    ) != len(config.account_refs):
        raise ValueError("Duplicate account authority")
    if len({entry.provider for entry in config.retention_limits}) != len(
        config.retention_limits
    ):
        raise ValueError("Duplicate retention limit")
    return replace(
        config,
        source_roots=tuple(sorted(config.source_roots)),
        checkout_anchors=tuple(sorted(config.checkout_anchors)),
        excluded_segments=tuple(
            sorted(config.excluded_segments, key=lambda ref: ref.value)
        ),
        account_refs=tuple(
            sorted(
                config.account_refs,
                key=lambda entry: (entry.provider, entry.stream_ref.value),
            )
        ),
        retention_limits=tuple(
            sorted(config.retention_limits, key=lambda entry: entry.provider)
        ),
        cutoff=config.cutoff.astimezone(UTC),
    )


def _registration_revision(ledger: Ledger, config: _Config) -> Revision:
    if config.project_id != ledger.identity.project_id:
        raise LedgerError("Private registration project mismatch")
    config_text = _encode(config, _Config, validate_ref=ledger.validate_source_ref)
    return Revision(
        ledger.pseudonymize("collector-registration", str(config.project_id)),
        1,
        ProjectRegistration(
            config.project_id,
            ledger.pseudonymize("collector-configuration", config_text),
            config.cutoff,
            tuple(
                checkout_anchor_reference(ledger, Path(raw))
                for raw in config.checkout_anchors
            ),
        ),
    )


def _publish_exact(directory, name: str, data: bytes) -> None:
    if len(data) > MAX_COMMAND_BYTES:
        raise ValueError("Private configuration is too large")
    prior = _read_private(directory, name)
    if prior is None:
        if _publish(directory, name, data):
            return
        prior = _read_private(directory, name)
    if prior != data:
        raise ConflictError("Private configuration already has different bytes")


def register_project(root: Path, config_path: Path) -> Registration:
    """Stage exact private configuration, then accept it under the writer lease."""
    config = _checked_config(
        _input(
            config_path,
            _Config,
            excluded_segments=[],
            account_refs=[],
            retention_limits=[],
        ),
        existing=True,
    )
    ledger = Ledger.initialize(root, config.project_id)
    with ledger.writer() as writer, _pin_directory(writer.root) as directory:
        registration = _registration_revision(writer, config)
        for revision in writer.as_of().current:
            if revision.key == registration.key and revision != registration:
                raise ConflictError("Project registration already exists")
        writer.require_writer()
        _publish_exact(directory, REGISTRATION_NAME, _encode(config, _Config).encode())
        writer.apply(LedgerBatch((registration,)))
        return _registration(writer, config)


def _authorized_config(
    ledger: Ledger, view: LedgerView
) -> tuple[_Config, ProjectRegistration]:
    with _pin_directory(ledger.root) as project:
        raw = _read_private(project, REGISTRATION_NAME)
    if raw is None:
        raise LedgerError("Project registration is unavailable")
    config = _checked_config(
        _decode(raw.decode("utf-8"), _Config, validate_ref=ledger.validate_source_ref),
        existing=False,
    )
    revision = _registration_revision(ledger, config)
    if (
        _encode(config, _Config).encode() != raw
        or view.project_id != config.project_id
        or revision not in view.current
    ):
        raise LedgerError("Private registration is not accepted")
    return config, revision.record


def _registration(
    ledger: Ledger, config: _Config, additions: tuple[Path, ...] = ()
) -> Registration:
    return Registration(
        config.project_id,
        ledger.root,
        tuple(map(Path, config.source_roots)),
        tuple(sorted(set(map(Path, config.checkout_anchors)) | set(additions))),
        config.cutoff,
    )


def _anchor_revision(ledger: Ledger, payload: SourceAnchorCommand) -> Revision:
    return Revision(
        ledger.pseudonymize("collector-source-anchor", str(payload.command_id)),
        1,
        SourceAnchor(
            payload.command_id,
            payload.project_id,
            payload.configuration_ref,
            payload.anchor_ref,
        ),
    )


def _staged_anchor(ledger: Ledger, payload: SourceAnchorCommand) -> Path | None:
    with (
        _pin_directory(ledger.root) as project,
        _private_child(project, ANCHORS_NAME, create=False) as staged,
    ):
        raw = (
            None
            if staged is None
            else _read_private(staged, f"{payload.command_id}.json")
        )
    if raw is None:
        return None
    proposal = _decode(raw.decode("utf-8"), _AnchorProposal)
    path = _path(proposal.checkout, existing=False)
    if (
        proposal.project_id != payload.project_id
        or proposal.command_id != payload.command_id
        or checkout_anchor_reference(ledger, path) != payload.anchor_ref
        or _encode(proposal, _AnchorProposal).encode() != raw
    ):
        return None
    return path


def stage_source_anchor(ledger: Ledger, anchor_path: Path) -> InboxCommand:
    """Stage the raw path privately and return the only command it authorizes."""
    proposal = _input(anchor_path, _AnchorProposal)
    path = _path(proposal.checkout, existing=False)
    with _pin_directory(ledger.root) as project:
        _, registration = _authorized_config(ledger, ledger.as_of())
        payload = SourceAnchorCommand(
            proposal.command_id,
            proposal.project_id,
            registration.configuration_ref,
            checkout_anchor_reference(ledger, path),
        )
        command = InboxCommand(payload.command_id, payload.project_id, payload)
        ledger.command_receipt(command)
        with _private_child(project, ANCHORS_NAME, create=True) as staged:
            assert staged is not None
            name = f"{payload.command_id}.json"
            if _read_private(staged, name) is None and not _directory_available(path):
                raise ValueError("Expected an available canonical checkout")
            _publish_exact(staged, name, _encode(proposal, _AnchorProposal).encode())
        project.check()
    return command


def source_anchor_decision(
    ledger: Ledger, payload: SourceAnchorCommand, view: LedgerView
) -> tuple[MarkerDisposition, tuple[Revision, ...]]:
    """Authorize the static inbox route against the exact private proposal."""
    ledger.require_writer()
    try:
        _, registration = _authorized_config(ledger, view)
        path = _staged_anchor(ledger, payload)
    except (ValueError, LedgerError):
        return MarkerDisposition.CONFLICT, ()
    if (
        payload.project_id != registration.project_id
        or payload.configuration_ref != registration.configuration_ref
        or path is None
    ):
        return MarkerDisposition.CONFLICT, ()
    if not _directory_available(path):
        return MarkerDisposition.PENDING, ()
    return MarkerDisposition.ACCEPTED, (_anchor_revision(ledger, payload),)


def _effective_registration(
    ledger: Ledger, view: LedgerView
) -> tuple[Registration, _Config]:
    config, registration = _authorized_config(ledger, view)
    current = {entry.key: entry for entry in view.current}
    additions = []
    for entry in current.values():
        receipt = entry.record
        if not isinstance(receipt, CommandReceipt):
            continue
        command = receipt.command
        payload = command.payload
        if (
            type(payload) is not SourceAnchorCommand
            or receipt.disposition is not MarkerDisposition.ACCEPTED
            or receipt.boundary is not None
            or receipt.anchor_ref is not None
            or payload.project_id != registration.project_id
            or payload.configuration_ref != registration.configuration_ref
            or receipt.digest != ledger.validate_command(command)
            or entry.key
            != ledger.pseudonymize("inbox-command", str(command.command_id))
        ):
            continue
        expected = _anchor_revision(ledger, payload)
        if current.get(expected.key) != expected:
            continue
        path = _staged_anchor(ledger, payload)
        if path is None:
            raise LedgerError("Accepted anchor's private proof is unavailable")
        additions.append(path)
    return _registration(ledger, config, tuple(additions)), config


def load_registration(ledger: Ledger) -> Registration:
    """Load the fixed cutoff and only fully accepted checkout anchors."""
    registration, _ = _effective_registration(ledger, ledger.as_of())
    return registration


def _session_filename(reference: SourceRef) -> str:
    return f"{reference.value.split(':')[1]}.json"


def remember_claude_session(ledger: Ledger, reference: SourceRef) -> None:
    """Preserve the explicit CLI reservation assertion as a pseudonym only."""
    ledger.validate_source_ref(reference)
    with _pin_directory(ledger.root) as project:
        if _read_private(project, REGISTRATION_NAME) is None:
            return
        _authorized_config(ledger, ledger.as_of())
        with _private_child(project, CLAUDE_SESSIONS_NAME, create=True) as sessions:
            assert sessions is not None
            _publish_exact(
                sessions,
                _session_filename(reference),
                json.dumps(reference.value).encode(),
            )


def _claude_reservation(
    ledger: Ledger, source: CandidateSource, batch: FrameBatch
) -> UUID | None:
    reference = source.session_ref
    if reference is None or not batch.frames:
        return None
    try:
        with (
            _pin_directory(ledger.root) as project,
            _private_child(project, CLAUDE_SESSIONS_NAME, create=False) as sessions,
        ):
            if (
                sessions is None
                or _read_private(sessions, _session_filename(reference))
                != json.dumps(reference.value).encode()
            ):
                return None
    except (LedgerError, OSError):
        return None
    # The private assertion holds only a pseudonym. Recover the UUID
    # transiently from a scanner-authenticated frame, then verify its key.
    for frame in batch.frames:
        raw = frame.row.get("sessionId", frame.row.get("session_id"))
        if type(raw) is not str:
            continue
        try:
            candidate = UUID(raw)
        except ValueError:
            continue
        if session_reference(ledger, Provider.CLAUDE, str(candidate)) == reference:
            return candidate
    return None


@dataclass(frozen=True, slots=True)
class CollectionReport:
    sequence: int
    root_gaps: int
    missing_sources: int
    held_sources: int
    deferred_sources: int
    invalid_inbox: int
    relationship_halted: bool


@dataclass(frozen=True, slots=True)
class _Observed:
    source_ref: SourceRef
    proof: SourceRef
    through: datetime


@dataclass(frozen=True, slots=True)
class _Status:
    project_id: UUID
    configuration_ref: SourceRef
    heartbeat: datetime
    collector_version: str
    collector_interpreter_version: str
    report: CollectionReport
    observed: tuple[_Observed, ...]

    def __post_init__(self) -> None:
        for value in (self.collector_version, self.collector_interpreter_version):
            if not re.fullmatch(
                r"[0-9]{1,8}(?:\.[0-9]{1,8}){2}[a-z0-9.+-]{0,32}", value
            ):
                raise ValueError("Invalid collector runtime version")


def _read_status(root: Path) -> _Status | None:
    try:
        with _pin_directory(root) as directory:
            raw = _read_private(directory, STATUS_NAME)
        if raw is not None:
            status = _decode(raw.decode("utf-8"), _Status)
            if (
                len(status.observed) <= _STATUS_SOURCE_LIMIT
                and _encode(status, _Status).encode() == raw
            ):
                return status
    except (OSError, ValueError, LedgerError):
        pass
    return None


def _observed_proof(
    ledger: Ledger, checkpoint: SourceCheckpoint, through: datetime
) -> SourceRef:
    return ledger.pseudonymize(
        "collector-observed-through",
        _encode(checkpoint, SourceCheckpoint)
        + "\n"
        + through.astimezone(UTC).isoformat(),
    )


def _enrollments(view: LedgerView) -> dict[SourceRef, tuple[ScopeEnrollment, ...]]:
    by_stream = defaultdict(list)
    for entry in view.current:
        if isinstance(entry.record, ScopeEnrollment):
            by_stream[entry.record.boundary.stream_ref].append(entry.record)
    return {
        stream: tuple(sorted(scopes, key=lambda scope: scope.boundary.ordinal))
        for stream, scopes in by_stream.items()
    }


@dataclass(frozen=True, slots=True)
class _Projection:
    prior: SourceCheckpoint | None
    batch: FrameBatch
    result: AdapterResult
    state: CodexState | ClaudeState | None = None

    def evidence(self) -> tuple[BoundaryEvidence, ...]:
        return tuple(
            entry
            for boundary in self.result.boundaries
            if (entry := self.batch.scope_evidence(boundary)) is not None
        )


def _read(
    batch: FrameBatch, state: CodexState | ClaudeState, eligibility: Eligibility
) -> AdapterResult:
    if isinstance(state, CodexState):
        return read_codex(batch, state, eligibility)
    return read_claude(batch, state, eligibility)


def _candidate(
    candidates: list[CandidateSource], prior: SourceCheckpoint | None
) -> CandidateSource | None:
    if len(candidates) == 1:
        return candidates[0]
    if prior is None:
        return None
    cursor = prior.cursor
    matches = [
        candidate
        for candidate in candidates
        if (
            candidate.locator_ref == cursor.locator_ref
            and candidate.incarnation_ref == cursor.incarnation_ref
        )
    ]
    return matches[0] if len(matches) == 1 else None


class _Collector:
    def __init__(self, writer: Ledger, rates: RateCard):
        self.writer = writer
        self.rates = rates
        self.states: dict[
            SourceRef, tuple[SourceCheckpoint, CodexState | ClaudeState]
        ] = {}

    def _state(
        self,
        source: CandidateSource,
        batch: FrameBatch,
        prior: SourceCheckpoint | None,
        view: LedgerView,
        config: _Config,
    ) -> CodexState | ClaudeState:
        cached = self.states.get(source.stream_ref)
        state = cached[1] if cached is not None and cached[0] == prior else None
        account_ref = next(
            (
                entry.account_ref
                for entry in config.account_refs
                if entry.provider is source.provider
                and entry.stream_ref == source.stream_ref
            ),
            None,
        )
        if source.provider is Provider.CODEX:
            return (
                state
                if isinstance(state, CodexState)
                else CodexState(self.writer, account_ref)
            )
        if not isinstance(state, ClaudeState):
            state = ClaudeState(self.writer, account_ref=account_ref)
        return replace(
            state,
            prior_view=view,
            reserved_session_id=_claude_reservation(self.writer, source, batch),
        )

    def _project(
        self,
        source: CandidateSource,
        prior: SourceCheckpoint | None,
        view: LedgerView,
        scopes: tuple[ScopeEnrollment, ...],
        config: _Config,
    ) -> _Projection:
        batch = scan(source, prior, config.cutoff)
        if batch.cursor is None:
            return _Projection(
                prior, batch, AdapterResult(diagnostics=batch.diagnostics)
            )
        state = self._state(source, batch, prior, view, config)
        boundary_result = _read(batch, state, Eligibility.EXCLUDED)
        selected = source
        if batch.frames:
            proof = {
                boundary: evidence
                for boundary in boundary_result.boundaries
                if (evidence := batch.scope_evidence(boundary)) is not None
            }
            for scope in scopes:
                evidence = proof.get(scope.boundary)
                try:
                    if evidence is not None:
                        selected = selected.with_enrollment(
                            scope, batch=batch, evidence=evidence
                        )
                    elif (
                        prior is not None
                        and scope.boundary.ordinal < batch.frames[0].ordinal
                    ):
                        selected = selected.with_enrollment(scope)
                    else:
                        raise ValueError("Missing fresh boundary evidence")
                except ValueError:
                    return self._gap(
                        source.stream_ref,
                        source.provider,
                        prior,
                        config.cutoff,
                        DiagnosticCode.BOUNDARY_UNVERIFIED,
                    )
            exclusions = frozenset(config.excluded_segments)
            for segment in {
                frame.segment_ref: frame
                for frame in batch.frames
                if frame.anchor_ref is None and frame.segment_ref in exclusions
            }.values():
                selected = selected.with_exclusion(segment)
        if selected is not source:
            batch = scan(selected, prior, config.cutoff)
        return _Projection(
            prior, batch, _read(batch, state, Eligibility.ELIGIBLE), state
        )

    @staticmethod
    def _gap(
        stream: SourceRef,
        provider: Provider | None,
        prior: SourceCheckpoint | None,
        cutoff: datetime,
        code: DiagnosticCode,
    ) -> _Projection:
        diagnostic = Diagnostic(code, cutoff, provider, stream)
        return _Projection(
            prior, FrameBatch(), AdapterResult(diagnostics=(diagnostic,))
        )

    def _commit(self, projection: _Projection) -> SourceCheckpoint | None:
        batch, result = projection.batch, projection.result
        accounted = account_observations(result, self.rates, ledger=self.writer)
        if (
            batch.cursor is None
            or result.provider_checkpoint is None
            or batch.cursor.offset == 0
        ):
            if accounted.revisions:
                self.writer.apply(accounted)
            return None
        checkpoint = SourceCheckpoint(batch.cursor, result.provider_checkpoint)
        self.writer.apply(
            LedgerBatch(accounted.revisions, checkpoint, projection.prior)
        )
        state = projection.state
        if isinstance(state, CodexState):
            advanced = advance_codex_state(state, batch, result)
        else:
            assert isinstance(state, ClaudeState)
            advanced = replace(
                advance_claude_state(state, batch, result), reserved_session_id=None
            )
        self.states[checkpoint.cursor.source_ref] = checkpoint, advanced
        return checkpoint

    def poll(self, expected: Registration) -> CollectionReport:
        writer = self.writer
        writer.require_writer()
        prior_view = writer.as_of()
        registration, config = _effective_registration(writer, prior_view)
        if replace(
            expected, checkout_anchors=registration.checkout_anchors
        ) != registration or not set(expected.checkout_anchors) <= set(
            registration.checkout_anchors
        ):
            raise LedgerError(
                "Collector registration does not match the accepted project"
            )

        available = tuple(
            root for root in registration.source_roots if _directory_available(root)
        )
        previous = {entry.cursor.source_ref: entry for entry in prior_view.checkpoints}
        locators = {
            entry.cursor.locator_ref: entry.cursor.source_ref
            for entry in prior_view.checkpoints
        }
        groups = defaultdict(list)
        projections = {}
        for source in discover(replace(registration, source_roots=available)):
            stream = locators.get(source.locator_ref, source.stream_ref)
            if stream != source.stream_ref:
                projections[stream] = self._gap(
                    stream,
                    previous[stream].provider.provider,
                    previous[stream],
                    config.cutoff,
                    DiagnosticCode.SOURCE_REPLACED,
                )
                continue
            groups[stream].append(source)

        scopes = _enrollments(prior_view)
        for stream, candidates in groups.items():
            prior = previous.get(stream)
            source = _candidate(candidates, prior)
            if source is None:
                projections[stream] = self._gap(
                    stream,
                    candidates[0].provider,
                    prior,
                    config.cutoff,
                    DiagnosticCode.OVERLAP_UNVERIFIED,
                )
                continue
            projections[stream] = self._project(
                source, prior, prior_view, scopes.get(stream, ()), config
            )

        # Each projected batch and its scope proof come from verified source
        # bytes read before this single coherent publication snapshot.
        evidence = tuple(
            entry
            for projection in projections.values()
            for entry in projection.evidence()
        )
        inbox = drain_inbox(writer, evidence)
        after_drain = writer.as_of()
        current, _ = _effective_registration(writer, after_drain)
        current_scopes = _enrollments(after_drain)
        status = _read_status(writer.root)
        configuration_ref = _registration_revision(
            writer, config
        ).record.configuration_ref
        observed = {}
        if (
            status is not None
            and status.project_id == config.project_id
            and status.configuration_ref == configuration_ref
            and status.report.sequence <= prior_view.sequence
        ):
            observed = {
                entry.source_ref: entry
                for entry in status.observed
                if (
                    (checkpoint := previous.get(entry.source_ref)) is not None
                    and entry.proof
                    == _observed_proof(writer, checkpoint, entry.through)
                )
            }

        deferred = held = 0
        for stream, projection in projections.items():
            if current != registration or current_scopes.get(stream) != scopes.get(
                stream
            ):
                deferred += 1
                continue
            batch = projection.batch
            held += len(batch.frames) > len(batch.commit_frames)
            checkpoint = self._commit(projection)
            if checkpoint is not None:
                moment = batch.observed_through
                previous_time = observed.get(stream)
                if previous_time is not None:
                    moment = (
                        previous_time.through
                        if moment is None
                        else max(moment, previous_time.through)
                    )
                if moment is not None:
                    observed[stream] = _Observed(
                        stream, _observed_proof(writer, checkpoint, moment), moment
                    )
        retained = tuple(
            sorted(
                observed.values(),
                key=lambda entry: (entry.through, entry.source_ref.value),
                reverse=True,
            )
        )
        for stream in self.states.keys() - groups.keys():
            del self.states[stream]
        report = CollectionReport(
            writer.as_of().sequence,
            len(registration.source_roots) - len(available),
            len(previous.keys() - groups.keys()),
            held,
            deferred,
            inbox.invalid_publications,
            inbox.relationship_halted,
        )
        status = _Status(
            config.project_id,
            configuration_ref,
            datetime.now(UTC),
            version("aitm-usage"),
            platform.python_version(),
            report,
            retained[:_STATUS_SOURCE_LIMIT],
        )
        with _pin_directory(writer.root) as directory:
            writer.require_writer()
            _publish(
                directory,
                STATUS_NAME,
                _encode(status, _Status).encode(),
                replace_pending=True,
            )
        return report


def collect_once(registration: Registration, ledger: Ledger) -> CollectionReport:
    """Run one guarded scan, coherent inbox drain, and eligible source commit."""
    with ledger.writer() as writer:
        return _Collector(writer, load_rate_card()).poll(registration)


def run_service(registration: Registration, interval_seconds: int = 15) -> int:
    """Keep the same guarded writer across polls and wait locally between them."""
    if type(interval_seconds) is not int or interval_seconds <= 0:
        raise ValueError("Expected a positive poll interval")
    ledger = Ledger.open(registration.state_root, registration.project_id)
    try:
        with ledger.writer() as writer:
            collector = _Collector(writer, load_rate_card())
            while True:
                collector.poll(registration)
                time.sleep(interval_seconds)
    except KeyboardInterrupt:
        return 0


def _coverage(view: LedgerView) -> dict[str, dict[str, int | str]]:
    current = view.current
    prices = _prices(current)
    quota = Counter(
        entry.record.provider
        for entry in current
        if isinstance(entry.record, AccountObservation)
    )
    counts = {
        provider: {
            "observations": 0,
            "partial": 0,
            "unknown_usage": 0,
            "unknown_price": 0,
            "diagnostics": 0,
            "quota": "observed" if quota[provider] else "unknown",
            "quota_readings": quota[provider],
            "actual_spend": "unknown",
        }
        for provider in Provider
    }
    for entry in current:
        record = entry.record
        if isinstance(record, UsageObservation):
            count = counts[record.boundary.provider]
            count["observations"] += 1
            count["partial"] += record.availability is Availability.PARTIAL
            count["unknown_usage"] += record.availability is Availability.UNKNOWN
            count["unknown_price"] += prices.get((entry.key, entry.revision)) is None
        elif isinstance(record, Diagnostic) and record.provider is not None:
            counts[record.provider]["diagnostics"] += 1
    return {provider.value: count for provider, count in counts.items()}


def status_report(root: Path, ledger: Ledger | None) -> dict:
    """Read the private heartbeat and independently validate durable watermarks."""
    status = _read_status(root)
    view = registration = config = None
    read_gap = ledger is None
    if ledger is not None:
        try:
            view = ledger.as_of()
        except (OSError, LedgerError, ValueError, sqlite3.Error):
            read_gap = True
        if view is not None:
            try:
                config, registration = _authorized_config(ledger, view)
            except (OSError, LedgerError, ValueError):
                pass
        if status is not None and (
            status.project_id != ledger.identity.project_id
            or (
                registration is not None
                and status.configuration_ref != registration.configuration_ref
            )
        ):
            status = None
    confirmed = (
        status is not None
        and registration is not None
        and view is not None
        and status.report.sequence <= view.sequence
    )
    observed = (
        {entry.source_ref: entry for entry in status.observed} if confirmed else {}
    )
    now = datetime.now(UTC)
    retention = (
        {entry.provider: entry.seconds for entry in config.retention_limits}
        if config is not None
        else {}
    )
    sources = []
    if view is not None:
        for checkpoint in sorted(
            view.checkpoints, key=lambda entry: entry.cursor.source_ref.value
        ):
            cursor, provider = checkpoint.cursor, checkpoint.provider
            prior = observed.get(cursor.source_ref)
            through = (
                prior.through
                if prior is not None
                and prior.proof == _observed_proof(ledger, checkpoint, prior.through)
                else None
            )
            sources.append(
                {
                    "source_ref": cursor.source_ref.value,
                    "provider": provider.provider.value,
                    "client_version": provider.client_version.value,
                    "format_version": provider.format_version,
                    "offset": cursor.offset,
                    "observed_through": None
                    if through is None
                    else through.isoformat(),
                    "lag_seconds": None
                    if through is None
                    else max(0, int((now - through).total_seconds())),
                    "retention_seconds": None
                    if through is None
                    else retention.get(provider.provider),
                }
            )
    last_poll = status.report if confirmed else None
    return {
        "version": version("aitm-usage"),
        "interpreter_version": platform.python_version(),
        "heartbeat": None if status is None else status.heartbeat.isoformat(),
        "collector_version": None if status is None else status.collector_version,
        "collector_interpreter_version": None
        if status is None
        else status.collector_interpreter_version,
        "sequence": None if view is None else view.sequence,
        "status_sequence": None if last_poll is None else last_poll.sequence,
        "cutoff": None if registration is None else registration.cutoff.isoformat(),
        "read_gap": read_gap,
        "root_gaps": None if last_poll is None else last_poll.root_gaps,
        "missing_sources": None if last_poll is None else last_poll.missing_sources,
        "held_sources": None if last_poll is None else last_poll.held_sources,
        "deferred_sources": None if last_poll is None else last_poll.deferred_sources,
        "invalid_inbox": None if last_poll is None else last_poll.invalid_inbox,
        "relationship_halted": None
        if last_poll is None
        else last_poll.relationship_halted,
        "sources": sources,
        "coverage": _coverage(view) if view is not None else {},
        "task_quota": "unknown",
    }
