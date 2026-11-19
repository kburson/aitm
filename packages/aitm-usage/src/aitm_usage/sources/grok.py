"""Read and replay qualified Grok Build whole-turn evidence without assigning a project."""

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from ..ledger import LedgerError
from ..monitor_types import (
    GrokBoundary,
    GrokCheckpoint,
    GrokCompletion,
    GrokDiagnostic,
    GrokObservation,
    GrokTokenCounts,
    MonitorModel,
    MonitorProvider,
    NativeSurface,
    ObservationTimeBasis,
    ProviderCostEvidence,
)
from ..types import (
    Availability,
    DiagnosticCode,
    Eligibility,
    SourceRef,
    _encode,
    _nonnegative,
    _unique_fields,
)
from .adapter import (
    AdapterBatch,
    NativeBoundary,
    NativeObservation,
    NativePosition,
    SourceLocator,
    SourceRoot,
    StreamCursor,
    _GrokSource,
)
from .adapter import GrokOrigin as GrokOrigin
from .scan import (
    _directory,
    _InventoryCycle,
    _InventoryUnavailable,
    _nonfinite,
    _open_snapshot,
    _probe,
    _Snapshot,
    _transcripts,
    _verify_snapshot,
)

_BINARY = "197c66a63e5ac46e07450b0ca21d141ce665050a412180f185dadfae1c7a5b2a"
_SURFACE = NativeSurface.GROK_BUILD_MACOS
_TIME_BASIS = ObservationTimeBasis.NATIVE_COMPLETION
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_SNAPSHOT_WINDOW = timedelta(seconds=1)
_MAX_NATIVE_BYTES = 16 * 1024 * 1024
_MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
_MAX_ROW_BYTES = 1024 * 1024
_MAX_TURNS = 1024
_CONTENT_UPDATES = {"agent_message_chunk", "agent_thought_chunk"}
_NATIVE_METHOD = "_x.ai/session/update"
_CONTENT_METHOD = "session/update"

type _Row = dict[str, object]
type _VerifyReceipt = Callable[[str, str, str], SourceRef | None]
type _ReadHeadless = Callable[[str, str], _Row | None]
type _AdmitSpan = Callable[[int, int], Eligibility]


@dataclass(frozen=True, slots=True)
class _VerifiedGrokMark:
    key: SourceRef
    start: int
    end: int
    boundary: GrokBoundary


@dataclass(frozen=True, slots=True)
class _VerifiedGrokHookless:
    key: SourceRef
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class _GrokAttemptHeld:
    start: int
    code: DiagnosticCode
    key: SourceRef | None = None


type _GrokReadNotice = _VerifiedGrokMark | _VerifiedGrokHookless | _GrokAttemptHeld


@dataclass(frozen=True, slots=True)
class _GrokTerminalSpan:
    start: int
    ordinal: int
    byte_end: int
    verified: bool


@dataclass(frozen=True, slots=True)
class _GrokCaptureMaterial:
    source: _GrokSource
    origin: GrokOrigin
    data: bytes = field(repr=False)
    complete: int
    open_start: int | None
    terminals: tuple[_GrokTerminalSpan, ...]

    def prefix(self, offset: int) -> SourceRef:
        if not 0 <= offset <= self.complete:
            raise ValueError("Grok capture prefix is outside the verified native file")
        return _capture_prefix(self.source, self.origin, self.data, offset)


def _capture_prefix(
    source: _GrokSource, origin: GrokOrigin, data: bytes, offset: int
) -> SourceRef:
    return source.root.evidence.pseudonymize(
        "grok-capture-prefix-v1",
        f"{source.stream_ref.value}:{origin.incarnation.value}:"
        f"{offset}:{sha256(data[:offset]).hexdigest()}",
    )


class _Held(Exception):
    def __init__(self, code: DiagnosticCode, key: SourceRef | None = None):
        self.code = code
        self.key = key


@dataclass(frozen=True, slots=True)
class _Accounting:
    model: str
    tokens: GrokTokenCounts
    cost: ProviderCostEvidence | None

    def reference(self, source: _GrokSource) -> SourceRef:
        payload = json.dumps(
            [
                self.model,
                _encode(self.tokens, GrokTokenCounts),
                None if self.cost is None else self.cost.ticks,
            ],
            separators=(",", ":"),
        )
        return source.root.evidence.pseudonymize("grok-accounting", payload)


@dataclass(frozen=True, slots=True)
class _Update:
    kind: str
    time: datetime
    event_id: str
    fields: _Row


def _uuid(value: object) -> str:
    if type(value) is not str or len(value) != 36 or str(UUID(value)) != value:
        raise ValueError("Invalid native identifier")
    return value


def _object(value: object) -> _Row:
    if type(value) is not dict:
        raise ValueError("Expected an object")
    return value


def _load(data: bytes) -> _Row:
    return _object(
        json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_fields,
            parse_constant=_nonfinite,
        )
    )


def _int(row: _Row, key: str) -> int:
    value = row.get(key)
    _nonnegative(value)
    return value


def _optional_count(row: _Row, key: str) -> int | None:
    value = row.get(key)
    if value is not None:
        _nonnegative(value)
    return value


def _cost(row: _Row, key: str) -> ProviderCostEvidence | None:
    value = _optional_count(row, key)
    return None if value is None else ProviderCostEvidence(value)


def _persisted_tokens(row: _Row) -> GrokTokenCounts:
    gross = _int(row, "inputTokens")
    cached = _int(row, "cachedReadTokens")
    created = _int(row, "cacheCreationTokens")
    return GrokTokenCounts(
        gross - cached - created,
        cached,
        created,
        _int(row, "outputTokens"),
        _optional_count(row, "reasoningTokens"),
        _int(row, "totalTokens"),
    )


def _stored_accounting(usage: _Row) -> _Accounting:
    models = _object(usage.get("modelUsage"))
    turns = (
        _int(usage, field) for field in ("numTurns", "turnCount") if field in usage
    )
    if (
        _int(usage, "modelCalls") != 1
        or len(models) != 1
        or any(count != 1 for count in turns)
    ):
        # Only a single complete native call has qualified non-overlap proof.
        raise _Held(DiagnosticCode.OVERLAP_UNVERIFIED)
    ((model, model_usage),) = models.items()
    if not model or len(model) > 128:
        raise ValueError("Invalid Grok model")
    details = _object(model_usage)
    tokens = _persisted_tokens(usage)
    cost = _cost(usage, "costUsdTicks")
    if (
        _int(details, "modelCalls") != 1
        or _persisted_tokens(details) != tokens
        or _cost(details, "costUsdTicks") != cost
        or usage.get("primaryModelId", model) != model
    ):
        raise ValueError("Grok aggregate and model usage disagree")
    return _Accounting(model, tokens, cost)


def _headless_tokens(record: _Row) -> GrokTokenCounts:
    usage = _object(record.get("usage"))
    return GrokTokenCounts(
        _int(usage, "input_tokens"),
        _int(usage, "cache_read_input_tokens"),
        _int(usage, "cache_creation_input_tokens"),
        _int(usage, "output_tokens"),
        _optional_count(usage, "reasoning_tokens"),
        _int(usage, "total_tokens"),
    )


def _update(row: _Row, session_id: str) -> _Update:
    params = _object(row.get("params"))
    if params.get("sessionId") != session_id:
        raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED)
    meta = _object(params.get("_meta"))
    ms = _int(meta, "agentTimestampMs")
    event_id = meta.get("eventId")
    if (
        ms // 1000 != _int(row, "timestamp")
        or type(event_id) is not str
        or not 0 < len(event_id) <= 128
    ):
        raise ValueError("Invalid native update identity or time")
    fields = _object(params.get("update"))
    kind = fields.get("sessionUpdate")
    method = (
        _CONTENT_METHOD
        if kind in (*_CONTENT_UPDATES, "user_message_chunk")
        else _NATIVE_METHOD
    )
    if type(kind) is not str or row.get("method") != method:
        raise ValueError("Invalid native update envelope")
    return _Update(kind, _EPOCH + timedelta(milliseconds=ms), event_id, fields)


def _known_model(model: str) -> MonitorModel:
    if model == MonitorModel.GROK_4_7:
        return MonitorModel.GROK_4_7
    if model == MonitorModel.GROK_4_7_BUILD:
        return MonitorModel.GROK_4_7_BUILD
    return MonitorModel.UNKNOWN


def _qualified(origin: GrokOrigin) -> bool:
    return (
        (
            origin.system,
            origin.architecture,
            origin.version,
            origin.build,
            origin.executable_digest,
        )
        == ("Darwin", "arm64", "1.0.77", "50ca579fa996", _BINARY)
        and type(origin.format_version) is int
        and origin.format_version == 1
        and origin.lineage_id == origin.session_id
    )


def _read_file(path: Path, identity: tuple, limit: int) -> bytes:
    with _open_snapshot(path, identity_prefix=identity) as (stream, snapshot):
        size = snapshot.stat.st_size
        if size > limit:
            raise _Held(DiagnosticCode.COVERAGE_GAP)
        data = stream.read(size)
        if len(data) != size:
            raise _Held(DiagnosticCode.SOURCE_REPLACED)
        _verify_snapshot(stream, path, snapshot, size, sha256(data).hexdigest())
    return data


def _checkpoint(
    source: _GrokSource,
    origin: GrokOrigin,
    prefix: bytes,
    completions: tuple[GrokCompletion, ...],
    *,
    strict: bool = False,
) -> GrokCheckpoint:
    offset = len(prefix)
    state = sha256(
        _encode(completions, tuple[GrokCompletion, ...]).encode()
    ).hexdigest()
    anchor = source.root.evidence.pseudonymize(
        "grok-capture-delta-v1" if strict else "grok-prefix",
        json.dumps(
            [
                source.stream_ref.value,
                origin.incarnation.value,
                offset,
                sha256(prefix).hexdigest(),
                state,
                source.root.cutoff.astimezone(UTC).isoformat(),
                sorted(origin.inherited_prompt_ids),
            ],
            separators=(",", ":"),
        ),
    )
    return GrokCheckpoint(
        source.stream_ref, origin.incarnation, offset, anchor, completions
    )


def _validate_prior(
    source: _GrokSource,
    origin: GrokOrigin,
    data: bytes,
    prior: GrokCheckpoint,
    *,
    strict: bool = False,
) -> None:
    if (
        prior.offset > len(data)
        or len(prior.completions) > _MAX_TURNS
        or prior
        != _checkpoint(
            source, origin, data[: prior.offset], prior.completions, strict=strict
        )
    ):
        raise _Held(DiagnosticCode.SOURCE_REPLACED)


class _NativeWalk:
    def __init__(
        self,
        source: _GrokSource,
        origin: GrokOrigin,
        prior: tuple[GrokCompletion, ...],
        verify_receipt: _VerifyReceipt | None,
        read_headless: _ReadHeadless | None,
        *,
        strict: bool = False,
        trace: bool = False,
        admit_span: _AdmitSpan | None = None,
    ) -> None:
        self.source = source
        self.origin = origin
        self.verify_receipt = verify_receipt
        self.read_headless = read_headless
        self.completions = {turn.key: turn for turn in prior}
        self.new: list[GrokCompletion] = []
        self.boundaries: list[tuple[SourceRef, NativeBoundary]] = []
        self.prompt: str | None = None
        self.hook: _Update | None = None
        self.user_chunk = False
        self.strict = strict
        self.trace = trace
        self.admit_span = admit_span
        self.start: int | None = None
        self.notices: list[_GrokReadNotice] = []
        self.terminals: list[_GrokTerminalSpan] = []
        self.receipts = {
            turn.receipt_ref for turn in prior if turn.receipt_ref is not None
        }

    @staticmethod
    def _row(raw: bytes, origin: GrokOrigin) -> _Update:
        if not raw.endswith(b"\n") or len(raw) > _MAX_ROW_BYTES:
            raise _Held(DiagnosticCode.COVERAGE_GAP)
        return _update(_load(raw), origin.session_id)

    def read(self, data: bytes, offset: int) -> int:
        for raw in data.splitlines(keepends=True):
            update = None
            byte_end = offset + len(raw)
            try:
                update = self._row(raw, self.origin)
                self.advance(update, offset, byte_end)
            except _Held as hold:
                if self.trace and self._remember_held_terminal(
                    update, offset, byte_end
                ):
                    return byte_end
                if not self.strict:
                    raise
                resume = offset if self.start is None else self.start
                self.notices.append(_GrokAttemptHeld(resume, hold.code, hold.key))
                return resume
            offset += len(raw)
        if not self.trace and (self.prompt is not None or self.user_chunk):
            if not self.strict:
                raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED)
            assert self.start is not None
            self.notices.append(
                _GrokAttemptHeld(self.start, DiagnosticCode.BOUNDARY_UNVERIFIED)
            )
            return self.start
        return offset

    def _remember_held_terminal(
        self, update: _Update | None, offset: int, byte_end: int
    ) -> bool:
        # A verified row can identify the end of the already-armed native
        # turn even if it cannot prove successful accounting for that turn.
        if update is None or update.kind != "turn_completed" or self.start is None:
            return False
        try:
            prompt = _uuid(update.fields.get("prompt_id"))
        except ValueError:
            return False
        if self.prompt is not None and self.prompt != prompt:
            return False
        self.terminals.append(_GrokTerminalSpan(self.start, offset, byte_end, False))
        return True

    def advance(self, update: _Update, offset: int, byte_end: int) -> None:
        kind = update.kind
        if kind in _CONTENT_UPDATES:
            return
        if kind == "background_tasks" and update.fields.get("tasks") == []:
            return
        if kind == "user_message_chunk":
            if self.user_chunk:
                raise _Held(DiagnosticCode.OVERLAP_UNVERIFIED)
            self.user_chunk = True
            if self.start is None:
                self.start = offset
            return
        if kind == "hook_execution":
            self.start_hook(update, offset)
            return
        if kind == "turn_completed":
            self.complete(update, offset, byte_end)
            return
        raise _Held(DiagnosticCode.UNSUPPORTED_FORMAT)

    def start_hook(self, update: _Update, offset: int) -> None:
        fields = update.fields
        if fields.get("event_name") != "user_prompt_submit":
            raise _Held(DiagnosticCode.UNSUPPORTED_FORMAT)
        prompt = _uuid(fields.get("prompt_id"))
        if self.prompt is not None or self.user_chunk:
            raise _Held(DiagnosticCode.OVERLAP_UNVERIFIED)
        self.prompt = prompt
        self.start = offset
        runs = fields.get("runs")
        if type(runs) is list and len(runs) == 1:
            if _object(_object(runs[0]).get("status")).get("status") == "success":
                self.hook = update

    def complete(self, update: _Update, offset: int, byte_end: int) -> None:
        prompt = _uuid(update.fields.get("prompt_id"))
        refs = self.source.root.evidence
        key = refs.pseudonymize("grok-turn", f"{self.source.stream_ref.value}:{prompt}")
        old = self.completions.get(key)
        if old is not None and old.observed_at != update.time:
            raise _Held(DiagnosticCode.IDENTITY_CONFLICT, key)
        if self.prompt is not None and self.prompt != prompt:
            raise _Held(DiagnosticCode.OVERLAP_UNVERIFIED, key)
        if update.fields.get("stop_reason") != "end_turn":
            raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED, key)
        hook = self.hook
        attempted = self.prompt is not None
        start = self.start
        if self.strict and start is None:
            raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED, key)
        disposition = Eligibility.ELIGIBLE
        if self.admit_span is not None:
            assert start is not None
            disposition = self.admit_span(start, offset + 1)
            if disposition is Eligibility.UNKNOWN:
                raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED, key)
        if (
            disposition is Eligibility.EXCLUDED
            or prompt in self.origin.inherited_prompt_ids
            or update.time < self.source.root.cutoff
        ):
            if old is None:
                self.remember(
                    GrokCompletion(key, offset, update.time, None, None, None)
                )
            self._finish_turn()
            return
        try:
            usage = _object(update.fields.get("usage"))
            accounting = _stored_accounting(usage)
        except _Held as hold:
            raise _Held(hold.code, key) from None
        except ValueError:
            raise _Held(DiagnosticCode.MALFORMED_USAGE, key) from None
        self.check_headless(prompt, accounting, key)
        observation = GrokObservation(
            MonitorProvider.GROK,
            _SURFACE,
            update.time,
            _TIME_BASIS,
            accounting.tokens,
            Availability.COMPLETE,
            _known_model(accounting.model),
            accounting.cost,
        )
        boundary = self.verified_boundary(hook, update, prompt, key, offset)
        receipt = None if boundary is None else boundary.receipt_ref
        verified = not attempted or receipt is not None and receipt not in self.receipts
        if self.strict and not verified:
            raise _Held(DiagnosticCode.BOUNDARY_UNVERIFIED, key)
        complete = GrokCompletion(
            key,
            offset,
            update.time,
            observation,
            accounting.reference(self.source),
            receipt,
        )
        if old is not None:
            if old != replace(
                complete,
                ordinal=old.ordinal,
                receipt_ref=old.receipt_ref,
                snapshot_dispute=old.snapshot_dispute,
            ):
                raise _Held(DiagnosticCode.IDENTITY_CONFLICT, key)
            if (
                old.receipt_ref is not None
                and receipt is not None
                and old.receipt_ref != receipt
            ):
                raise _Held(DiagnosticCode.IDENTITY_CONFLICT, key)
            if self.trace and start is not None:
                self.terminals.append(
                    _GrokTerminalSpan(start, offset, byte_end, verified)
                )
            self._finish_turn()
            return
        self.remember(complete)
        if self.trace and start is not None:
            self.terminals.append(_GrokTerminalSpan(start, offset, byte_end, verified))
        self.new.append(complete)
        if receipt is not None:
            self.receipts.add(receipt)
        if self.strict:
            assert start is not None
            self.notices.append(
                _VerifiedGrokHookless(key, start, offset + 1)
                if boundary is None
                else _VerifiedGrokMark(key, start, offset + 1, boundary)
            )
        self._finish_turn()
        if boundary is not None:
            self.boundaries.append(
                (key, NativeBoundary(boundary, self.origin.checkout))
            )

    def _finish_turn(self) -> None:
        self.prompt = self.hook = self.start = None
        self.user_chunk = False

    def remember(self, completion: GrokCompletion) -> None:
        if len(self.completions) >= _MAX_TURNS:
            raise _Held(DiagnosticCode.COVERAGE_GAP, completion.key)
        self.completions[completion.key] = completion

    def verified_boundary(
        self,
        hook: _Update | None,
        update: _Update,
        prompt: str,
        key: SourceRef,
        offset: int,
    ) -> GrokBoundary | None:
        if hook is None or hook.time > update.time or self.verify_receipt is None:
            return None
        receipt = self.verify_receipt(self.origin.session_id, prompt, hook.event_id)
        if receipt is None:
            return None
        refs = self.source.root.evidence
        try:
            refs.validate_source_ref(receipt)
        except (LedgerError, TypeError, ValueError):
            return None
        return GrokBoundary(
            self.source.stream_ref,
            refs.pseudonymize("grok-session", self.origin.session_id),
            offset,
            refs.pseudonymize("grok-marker-boundary", f"{key.value}:{hook.event_id}"),
            receipt,
        )

    def check_headless(
        self, prompt: str, accounting: _Accounting, key: SourceRef
    ) -> None:
        if self.read_headless is None:
            return
        record = self.read_headless(self.origin.session_id, prompt)
        if record is None:
            return
        try:
            record = _object(record)
            if (
                record.get("type") != "end"
                or record.get("sessionId") != self.origin.session_id
                or record.get("requestId") != prompt
                or record.get("stopReason") != "end_turn"
            ):
                raise _Held(DiagnosticCode.IDENTITY_CONFLICT, key)
            for flag in ("usage_is_incomplete", "cost_is_partial"):
                if flag in record and type(record[flag]) is not bool:
                    raise ValueError("Invalid Grok headless evidence status")
            if record.get("usage_is_incomplete"):
                return
            tokens = _headless_tokens(record)
            cost = (
                None
                if record.get("cost_is_partial")
                else _cost(record, "total_cost_usd_ticks")
            )
        except ValueError:
            raise _Held(DiagnosticCode.MALFORMED_USAGE, key) from None
        if (
            tokens != accounting.tokens
            or cost is not None
            and accounting.cost is not None
            and cost != accounting.cost
        ):
            raise _Held(DiagnosticCode.IDENTITY_CONFLICT, key)


def _snapshot_rows(source: _GrokSource, origin: GrokOrigin) -> list[_Row] | None:
    path = source.path.with_name("usage.json")
    try:
        data = _read_file(path, source.snapshot.identity[:-1], _MAX_SNAPSHOT_BYTES)
        snapshot = _load(data)
        rows = snapshot.get("turns")
        if snapshot.get("sessionId") == origin.session_id and type(rows) is list:
            if len(rows) > _MAX_TURNS:
                raise _Held(DiagnosticCode.COVERAGE_GAP)
            return rows
    except (OSError, ValueError, OverflowError, RecursionError):
        pass
    return None


def _reconcile(
    source: _GrokSource, origin: GrokOrigin, walk: _NativeWalk
) -> tuple[tuple[GrokDiagnostic, ...], set[SourceRef]]:
    rows = _snapshot_rows(source, origin)
    matched: set[SourceRef] = set()
    orphan = False
    prior_ordinal = -1
    for value in rows or ():
        try:
            row = _object(value)
            ended = row.get("endedAt")
            if type(ended) is not str or len(ended) > 64:
                raise ValueError("Invalid snapshot end time")
            end = datetime.fromisoformat(ended)
            if end.utcoffset() is None:
                raise ValueError("Expected a timezone-aware snapshot end")
            if end + _SNAPSHOT_WINDOW <= source.root.cutoff:
                continue
            candidates = [
                turn
                for turn in walk.completions.values()
                if timedelta(0) <= turn.observed_at - end < _SNAPSHOT_WINDOW
            ]
            if len(candidates) != 1 or candidates[0].ordinal <= prior_ordinal:
                orphan = True
                continue
            turn = candidates[0]
        except (ValueError, OverflowError):
            orphan = True
            continue
        prior_ordinal = turn.ordinal
        if turn.observation is None:
            continue
        code = None
        try:
            snapshot_content = _stored_accounting(row).reference(source)
            if snapshot_content != turn.native_content_ref:
                code = DiagnosticCode.IDENTITY_CONFLICT
        except _Held as hold:
            code = hold.code
        except ValueError:
            code = DiagnosticCode.IDENTITY_CONFLICT
        if code is None:
            matched.add(turn.key)
        elif turn.snapshot_dispute is None:
            # A later snapshot alone cannot withdraw a prior keyed dispute.
            walk.completions[turn.key] = replace(turn, snapshot_dispute=code)
    disputed = {
        turn.key: turn
        for turn in walk.completions.values()
        if turn.snapshot_dispute is not None
    }
    disputes = tuple(
        GrokDiagnostic(
            turn.snapshot_dispute, turn.observed_at, source.stream_ref, turn.key
        )
        for turn in disputed.values()
    )
    gaps = [
        GrokDiagnostic(
            DiagnosticCode.UNRECONCILED_USAGE,
            turn.observed_at,
            source.stream_ref,
            turn.key,
        )
        for turn in walk.new
        if turn.key not in matched and turn.key not in disputed
    ]
    if orphan:
        gaps.append(
            GrokDiagnostic(
                DiagnosticCode.UNRECONCILED_USAGE, source.root.cutoff, source.stream_ref
            )
        )
    return (*gaps, *disputes), set(disputed)


class GrokAdapter:
    """Read the pinned macOS writer and service-admitted native lineage."""

    def __init__(
        self,
        verify_origin: Callable[[Path], GrokOrigin | None],
        verify_receipt: _VerifyReceipt | None = None,
        read_headless: _ReadHeadless | None = None,
        *,
        inventory_witness: Callable[[SourceRoot], SourceRef] | None = None,
    ) -> None:
        self.verify_origin = verify_origin
        self.verify_receipt = verify_receipt
        self.read_headless = read_headless
        self._inventory_witness = inventory_witness
        self._inventory_verifier = verify_origin
        self._inventory_parser = object()

    def discover(self, root: SourceRoot) -> Iterator[SourceLocator]:
        try:
            with _directory(root.path) as (directory, identity, _):
                for path in _transcripts(directory, root.path):
                    if path.name != "updates.jsonl":
                        continue
                    try:
                        snapshot = _probe(path)
                    except OSError:
                        continue
                    if snapshot.identity[: len(identity)] != identity:
                        continue
                    origin = self.verify_origin(path)
                    lineage = origin.lineage_id if origin is not None else None
                    stream_ref = root.evidence.pseudonymize(
                        "grok-stream" if lineage else "grok-unverified-source",
                        lineage or str(path),
                    )
                    yield SourceLocator(
                        _GrokSource(path, origin, root, snapshot, stream_ref)
                    )
        except OSError:
            return

    def _inventory_discover(
        self, root: SourceRoot, inventory: _InventoryCycle, *, profile: object
    ) -> Iterator[SourceLocator]:
        witness_for = self._inventory_witness
        if witness_for is None:
            raise _InventoryUnavailable(
                "Grok metadata inventory witness is unavailable"
            )
        verifier = self.verify_origin
        if verifier is not self._inventory_verifier:
            self._inventory_parser = object()
            self._inventory_verifier = verifier
        witness = witness_for(root)
        root.evidence.validate_source_ref(witness)

        def load(path: Path, _snapshot: _Snapshot) -> GrokOrigin | None:
            origin = verifier(path)
            if origin is not None and type(origin) is not GrokOrigin:
                raise _InventoryUnavailable("Grok metadata origin is unavailable")
            return origin

        def current() -> bool:
            return (
                self.verify_origin is verifier
                and self._inventory_witness is witness_for
                and witness_for(root) == witness
            )

        for path, snapshot, origin in inventory._origins(
            root.path,
            root.evidence,
            ("grok", self._inventory_parser, profile, witness),
            load,
            layout_name="updates.jsonl",
            witness=current,
        ):
            lineage = origin.lineage_id if origin is not None else None
            stream = root.evidence.pseudonymize(
                "grok-stream" if lineage else "grok-unverified-source",
                lineage or str(path),
            )
            yield SourceLocator(_GrokSource(path, origin, root, snapshot, stream))

    def _capture_material(
        self, locator: SourceLocator, verifier: _VerifyReceipt | None
    ) -> _GrokCaptureMaterial:
        source = locator._source
        if not isinstance(source, _GrokSource):
            raise _Held(DiagnosticCode.UNSUPPORTED_FORMAT)
        origin = source.origin
        if (
            origin is None
            or not _qualified(origin)
            or self.verify_origin(source.path) != origin
        ):
            raise _Held(DiagnosticCode.UNSUPPORTED_FORMAT)
        data = _read_file(source.path, source.snapshot.identity, _MAX_NATIVE_BYTES)
        walk = _NativeWalk(
            source,
            origin,
            (),
            verifier if self.verify_receipt is verifier else None,
            self.read_headless,
            trace=True,
        )
        end = walk.read(data, 0)
        if self.verify_origin(source.path) != origin:
            raise _Held(DiagnosticCode.SOURCE_REPLACED)
        return _GrokCaptureMaterial(
            source, origin, data, end, walk.start, tuple(walk.terminals)
        )

    def read_delta(
        self,
        locator: SourceLocator,
        cursor: StreamCursor | None,
        *,
        _proofs: list[_GrokReadNotice] | None = None,
        _receipt_verifier: _VerifyReceipt | None = None,
        _capture_limit: int | None = None,
        _capture_fences: tuple[tuple[int, SourceRef], ...] = (),
        _admit_span: _AdmitSpan | None = None,
    ) -> AdapterBatch:
        source = locator._source
        if not isinstance(source, _GrokSource):
            return AdapterBatch()
        origin = source.origin
        try:
            if (
                origin is None
                or not _qualified(origin)
                or self.verify_origin(source.path) != origin
            ):
                raise _Held(DiagnosticCode.UNSUPPORTED_FORMAT)
            if source.root.cutoff.utcoffset() is None:
                raise ValueError("Expected an aware cutoff")
            _uuid(origin.session_id)
            _uuid(origin.lineage_id)
            if len(origin.inherited_prompt_ids) > _MAX_TURNS:
                raise _Held(DiagnosticCode.COVERAGE_GAP)
            refs = source.root.evidence
            refs.validate_source_ref(origin.incarnation)
            if origin.checkout is not None:
                refs.validate_source_ref(origin.checkout)
            return self._read_delta(
                source,
                origin,
                cursor,
                _proofs,
                _receipt_verifier,
                _capture_limit,
                _capture_fences,
                _admit_span,
            )
        except _Held as hold:
            diagnostic = GrokDiagnostic(
                hold.code, source.root.cutoff, source.stream_ref, hold.key
            )
        except OSError:
            diagnostic = GrokDiagnostic(
                DiagnosticCode.SOURCE_REPLACED, source.root.cutoff, source.stream_ref
            )
        except (LedgerError, ValueError, OverflowError, RecursionError):
            diagnostic = GrokDiagnostic(
                DiagnosticCode.MALFORMED_USAGE, source.root.cutoff, source.stream_ref
            )
        return AdapterBatch(diagnostics=(diagnostic,), cursor=cursor)

    def _read_delta(
        self,
        source: _GrokSource,
        origin: GrokOrigin,
        cursor: StreamCursor | None,
        proofs: list[_GrokReadNotice] | None,
        verifier: _VerifyReceipt | None,
        capture_limit: int | None,
        capture_fences: tuple[tuple[int, SourceRef], ...],
        admit_span: _AdmitSpan | None,
    ) -> AdapterBatch:
        strict = proofs is not None
        data = _read_file(source.path, source.snapshot.identity, _MAX_NATIVE_BYTES)
        if any(
            not 0 <= end <= len(data)
            or _capture_prefix(source, origin, data, end) != prefix
            for end, prefix in capture_fences
        ):
            raise _Held(DiagnosticCode.SOURCE_REPLACED)
        if capture_limit is not None:
            if not 0 <= capture_limit <= len(data):
                raise _Held(DiagnosticCode.SOURCE_REPLACED)
            data = data[:capture_limit]
        prior = cursor.checkpoint if cursor is not None else None
        if prior is not None:
            if not isinstance(prior, GrokCheckpoint):
                raise _Held(DiagnosticCode.SOURCE_REPLACED)
            _validate_prior(source, origin, data, prior, strict=strict)
        offset = prior.offset if prior is not None else 0
        history = prior.completions if prior is not None else ()
        verify = self.verify_receipt
        if strict and verify is not verifier:
            verify = None
        walk = _NativeWalk(
            source,
            origin,
            history,
            verify,
            self.read_headless,
            strict=strict,
            admit_span=admit_span,
        )
        reached = walk.read(data[offset:], offset)
        diagnostics, disputed = _reconcile(source, origin, walk)
        if proofs is not None:
            for notice in walk.notices:
                if type(notice) is _GrokAttemptHeld:
                    diagnostics = (
                        *diagnostics,
                        GrokDiagnostic(
                            notice.code,
                            source.root.cutoff,
                            source.stream_ref,
                            notice.key,
                        ),
                    )
                    proofs.append(notice)
                elif notice.key not in disputed:
                    proofs.append(notice)
        session_ref = source.root.evidence.pseudonymize(
            "grok-session", origin.session_id
        )
        observations = tuple(
            NativeObservation(
                turn.key,
                1,
                turn.observation,
                _SURFACE,
                _TIME_BASIS,
                origin.checkout,
                position=NativePosition(session_ref, source.stream_ref, turn.ordinal),
            )
            for turn in walk.new
            if turn.key not in disputed
        )
        boundaries = tuple(
            boundary for key, boundary in walk.boundaries if key not in disputed
        )
        checkpoint = _checkpoint(
            source,
            origin,
            data[:reached],
            tuple(walk.completions.values()),
            strict=strict,
        )
        return AdapterBatch(
            observations, boundaries, diagnostics, StreamCursor(checkpoint)
        )
