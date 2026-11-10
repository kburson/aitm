"""Cumulative usage and source-order scope evidence from Codex rollouts."""

import json
import re
import shlex
from dataclasses import dataclass, field, fields, replace
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from itertools import combinations
from pathlib import Path
from uuid import UUID

from ..ledger import Ledger
from ..scopes import session_reference
from ..types import (
    AdapterResult,
    Availability,
    BoundaryKind,
    ClientVersion,
    Diagnostic,
    DiagnosticCode,
    Effort,
    Eligibility,
    ModelLabel,
    ProcessingTier,
    Provider,
    ProviderCheckpoint,
    QuotaBucket,
    QuotaEvidence,
    QuotaSource,
    RequestPrefix,
    Revision,
    SourceBoundary,
    SourceRef,
    TokenCounts,
    UsageObservation,
    normalize_model,
)
from .scan import FrameBatch, SourceFrame

_PROVIDER = Provider.CODEX
_CLIENT = ClientVersion.CODEX_0_167_0_ALPHA_3_2
_FORMAT = 1
_ZERO = TokenCounts(0, 0, 0, 0, 0, 0, 0)
_TOKEN_FIELDS = tuple(item.name for item in fields(TokenCounts))
_WINDOW_BUCKETS = {300: QuotaBucket.FIVE_HOUR, 10080: QuotaBucket.SEVEN_DAY}
_ATTEMPT_ERRORS = {"error", "stream_error", "turn_aborted"}
_NONUSAGE_EVENTS = {
    "agent_message",
    "agent_reasoning",
    "agent_reasoning_raw_content",
    "exec_command_begin",
    "exec_command_end",
    "item_completed",
    "item_started",
    "user_message",
    "warning",
}
_NONUSAGE_ITEMS = {
    "additional_tools",
    "agent_message",
    "developer_message",
    "message",
    "reasoning",
}
_NONUSAGE_ROWS = {
    "dynamic_tools_updated",
    "inter_agent_communication_metadata",
    "world_state",
}
_CALLS = {"function_call", "custom_tool_call", "local_shell_call"}
_OUTPUTS = {"function_call_output", "custom_tool_call_output"}
# This dedicated Desktop wrapper runs precisely the scope CLI command and
# returns its JSON stdout. Free-form scripts and mixed tool batches lack proof.
_MARKER_WRAPPER = re.compile(
    r"const marker = await tools\.exec_command\((\{.*\})\); text\(marker\.output\);"
)
_DESKTOP_OUTPUT = re.compile(
    r"Script completed\nWall time \d+(?:\.\d+)? seconds\nOutput:\n"
)


@dataclass(frozen=True, slots=True)
class _Turn:
    start: SourceBoundary
    segment_ref: SourceRef
    root_turn_ref: SourceRef
    post_cutoff: bool
    model: ModelLabel = ModelLabel.UNKNOWN
    effort: Effort | None = None
    processing_tier: ProcessingTier | None = None
    seen_context: bool = False
    seen_counter: bool = False


@dataclass(frozen=True, slots=True)
class _Call:
    call_ref: SourceRef
    segment_ref: SourceRef
    marker: bool
    response_seen: bool = False


@dataclass(frozen=True, slots=True)
class _Receipt:
    reference: SourceRef
    target: SourceRef


@dataclass(frozen=True, slots=True)
class _Response:
    boundary: SourceBoundary
    request_ref: SourceRef
    counts: TokenCounts
    thread_counts: TokenCounts
    turn_counts: TokenCounts | None
    thread_delta: TokenCounts | None
    model: ModelLabel
    effort: Effort | None
    processing_tier: ProcessingTier | None
    eligible: bool


class _CompactionStage(Enum):
    WORLD_STATE = 1
    TURN_CONTEXT = 2
    SETTINGS = 3
    DISPLAY = 4


@dataclass(frozen=True, slots=True)
class _Compaction:
    segment_ref: SourceRef
    stage: _CompactionStage = _CompactionStage.WORLD_STATE


@dataclass(slots=True)
class _Context:
    turn: _Turn | None = None
    call: _Call | None = None
    parallel: bool = False
    serial_output: SourceRef | None = None
    receipt: _Receipt | None = None
    next_turn_receipt: _Receipt | None = None
    response: _Response | None = None
    ambiguous: bool = False
    conflict: bool = False
    closed_turn: SourceRef | None = None
    tainted: bool = False
    enrollment_output: bool = False
    compaction: _Compaction | None = None


@dataclass(frozen=True, slots=True)
class CodexState:
    """Per-stream in-memory context. Construct fresh after a process restart.

    Supply a private configured account pseudonym only when it identifies the
    account used by this source. The creator of a thread can differ from the
    account used on resume, so session creator metadata is insufficient.
    """

    ledger: Ledger = field(repr=False)
    account_ref: SourceRef | None = None
    _stream_ref: SourceRef | None = field(default=None, repr=False)
    _checkpoint: ProviderCheckpoint | None = field(default=None, repr=False)
    _context: _Context = field(default_factory=_Context, repr=False)
    _seen_requests: frozenset[SourceRef] = field(default=frozenset(), repr=False)
    _have_history: bool = field(default=False, repr=False)
    _exact_only: bool = field(default=False, repr=False)
    _thread_counts: TokenCounts | None = field(default=None, repr=False)
    neutral_markers: bool = False

    def __post_init__(self) -> None:
        if self.account_ref is not None:
            self.ledger.validate_source_ref(self.account_ref)


def _uuid(value: object) -> UUID | None:
    if type(value) is not str or len(value) > 36:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


def _session(ledger: Ledger, raw: object) -> SourceRef | None:
    value = _uuid(raw)
    return None if value is None else session_reference(ledger, _PROVIDER, str(value))


def _validate_command(ledger: Ledger, session_ref: SourceRef, command_id: UUID) -> None:
    ledger.validate_source_ref(session_ref)
    if type(command_id) is not UUID:
        raise ValueError("Expected an opaque Codex scope command ID")


def codex_receipt_reference(
    ledger: Ledger, session_ref: SourceRef, command_id: UUID
) -> SourceRef:
    """Use the UUID returned as command_id by the U02 scope mark CLI."""
    _validate_command(ledger, session_ref, command_id)
    return ledger.pseudonymize("scope-receipt", str(command_id))


def codex_request_boundary_reference(
    ledger: Ledger, session_ref: SourceRef, command_id: UUID
) -> SourceRef:
    """Reserve the next request target before publishing the scope command."""
    _validate_command(ledger, session_ref, command_id)
    return ledger.pseudonymize(
        "codex-scope-next-request", f"{session_ref.value}:{command_id}"
    )


def codex_turn_boundary_reference(
    ledger: Ledger, session_ref: SourceRef, turn_id: str
) -> SourceRef:
    """Reference the provider's next identifiable turn, when known."""
    ledger.validate_source_ref(session_ref)
    if _identifier(turn_id) is None:
        raise ValueError("Expected a Codex turn identifier")
    return ledger.pseudonymize("codex-turn", f"{session_ref.value}:{turn_id}")


def _identifier(raw: object) -> str | None:
    if type(raw) is str and 0 < len(raw) <= 256 and raw.isascii() and raw.isprintable():
        return raw
    return None


def _object(raw: object) -> dict:
    return raw if type(raw) is dict else {}


def _number(raw: object) -> int | None:
    return raw if type(raw) is int and 0 <= raw < 2**63 else None


def _counts(raw: object) -> TokenCounts | None:
    data = _object(raw)
    gross = _number(data.get("input_tokens"))
    cached = _number(data.get("cached_input_tokens"))
    output = _number(data.get("output_tokens"))
    total = _number(data.get("total_tokens"))
    reasoning = _number(data.get("reasoning_output_tokens"))
    writes = _number(data.get("cache_write_input_tokens", 0))
    # Codex supplies one unclassified write field. A nonzero value cannot
    # become a five-minute or one-hour quantity under the shared contract.
    if (
        gross is None
        or cached is None
        or output is None
        or total != gross + output
        or cached > gross
        or writes != 0
        or ("reasoning_output_tokens" in data and reasoning is None)
        or (reasoning is not None and reasoning > output)
    ):
        return None
    return TokenCounts(gross, cached, 0, 0, output, reasoning, total)


def _difference(before: TokenCounts, after: TokenCounts) -> TokenCounts:
    quantities = []
    for key in _TOKEN_FIELDS:
        earlier = getattr(before, key)
        current = getattr(after, key)
        quantities.append(
            None if earlier is None or current is None else current - earlier
        )
    return TokenCounts(*quantities)


def _compatible(left: TokenCounts, right: TokenCounts) -> bool:
    # The reasoning subset may be absent. Never use it as additional output.
    for key in _TOKEN_FIELDS:
        a, b = getattr(left, key), getattr(right, key)
        if a != b and (
            key != "reasoning_output_tokens" or (a is not None and b is not None)
        ):
            return False
    return True


def _coherent(counts: TokenCounts) -> bool:
    gross, cached, output = (
        counts.input_tokens,
        counts.cached_input_tokens,
        counts.output_tokens,
    )
    return (
        gross is not None
        and cached is not None
        and output is not None
        and counts.total_tokens == gross + output
        and counts.cache_write_5m_tokens == counts.cache_write_1h_tokens == 0
        and cached <= gross
        and (
            counts.reasoning_output_tokens is None
            or counts.reasoning_output_tokens <= output
        )
    )


def _decode_baseline(stored: TokenCounts | None) -> tuple[TokenCounts | None, bool]:
    if stored is None or stored.total_tokens is not None:
        return stored, False
    # An incomplete cumulative checkpoint can retain a high-water witness
    # without representing a qualified baseline for the intervening span.
    if stored.input_tokens is not None and stored.output_tokens is not None:
        total = _number(stored.input_tokens + stored.output_tokens)
        high_water = replace(stored, total_tokens=total)
        if _coherent(high_water):
            return high_water, True
    return None, False


def _quota_window(
    raw: object, account_ref: SourceRef, observed_at: datetime
) -> QuotaEvidence | None:
    data = _object(raw)
    minutes = _number(data.get("window_minutes"))
    reset = _number(data.get("resets_at"))
    percent = data.get("used_percent")
    if (
        minutes not in _WINDOW_BUCKETS
        or reset is None
        or type(percent) not in (int, float)
    ):
        return None
    value = Decimal(str(percent))
    if not value.is_finite() or not 0 <= value <= 100:
        return None
    precision = max(0, -value.normalize().as_tuple().exponent)
    if precision > 3:
        return None
    try:
        reset_at = datetime.fromtimestamp(reset, UTC)
    except (OverflowError, OSError, ValueError):
        return None
    if reset_at <= observed_at:
        return None
    return QuotaEvidence(
        _PROVIDER,
        account_ref,
        _WINDOW_BUCKETS[minutes],
        observed_at,
        int(value * 1000),
        precision,
        QuotaSource.CODEX_INLINE,
        reset_at,
        minutes * 60,
    )


def _marker_command(payload: dict, project_root: Path | None) -> bool:
    source = payload.get("input")
    if (
        payload.get("type") != "custom_tool_call"
        or payload.get("name") != "exec"
        or type(source) is not str
    ):
        return False
    # Desktop can append exactly one ASCII line feed to the tool input.
    source = source.removesuffix("\n")
    if len(source) > 8192:
        return False
    wrapper = _MARKER_WRAPPER.fullmatch(source)
    if wrapper is None:
        return False
    try:
        options = _object(json.loads(wrapper[1]))
        cmd = options.get("cmd")
        if set(options) != {"cmd"} or type(cmd) is not str:
            return False
        parts = shlex.split(cmd)
    except (ValueError, RecursionError):
        return False
    return (
        len(parts) == 8
        and parts[:2] == ["aitm-usage", "--project"]
        and (
            Path(parts[2]).is_absolute()
            if project_root is None
            else parts[2] == str(project_root)
        )
        and parts[3:6]
        in (
            ["scope", "mark", "--marker"],
            ["development", "bind", "--binding"],
        )
        and Path(parts[6]).is_absolute()
        and parts[7] == "--json"
        and cmd == shlex.join(parts)
    )


def _marker_output(payload: dict) -> UUID | None:
    if payload.get("type") != "custom_tool_call_output":
        return None
    blocks = payload.get("output")
    if type(blocks) is not list or len(blocks) != 2:
        return None
    header, body = (_object(block) for block in blocks)
    if any(block.get("type") != "input_text" for block in (header, body)):
        return None
    prefix, content = header.get("text"), body.get("text")
    if (
        type(prefix) is not str
        or len(prefix) > 128
        or _DESKTOP_OUTPUT.fullmatch(prefix) is None
        or type(content) is not str
        or len(content) > 256
    ):
        return None
    try:
        result = _object(json.loads(content))
    except (ValueError, RecursionError):
        return None
    if set(result) == {"command_id", "status"} and result["status"] == "queued":
        return _uuid(result["command_id"])
    return None


def _matching_context(state: CodexState, batch: FrameBatch) -> bool:
    return (
        batch.cursor is not None
        and batch.cursor.source_ref == state._stream_ref
        and batch.provider_checkpoint == state._checkpoint
    )


class _Walk:
    """Fold one verified scanner snapshot without mutating its input state."""

    def __init__(self, batch: FrameBatch, state: CodexState, eligibility: Eligibility):
        self.state = state
        self.marker_root = None if state.neutral_markers else state.ledger.root
        self.record_usage = eligibility is Eligibility.ELIGIBLE
        state.ledger.validate_source_ref(batch.cursor.source_ref)
        matching = _matching_context(state, batch)
        self.context = replace(state._context) if matching else _Context()
        self.seen_requests = set(state._seen_requests) if matching else set()
        self.have_history = matching and state._have_history
        self.prior = batch.provider_checkpoint
        self.checkpoint = self.prior
        self.epoch = None if self.prior is None else self.prior.epoch_ref
        # A fresh process can trust the cumulative value without knowing
        # whether the entire span since that value was project-eligible.
        self.exact_only = state._exact_only if matching else self.epoch is not None
        self.ordinal = (
            None if self.prior is None or self.epoch is None else self.prior.ordinal
        )
        self.baseline, withheld = _decode_baseline(
            None if self.prior is None else self.prior.baseline
        )
        if not matching:
            self.context.tainted = withheld
        self.thread_counts = state._thread_counts if matching else None
        self.lookahead_total: TokenCounts | None = None
        self.unpublished = {
            entry.request_ref: entry
            for entry in (() if self.prior is None else self.prior.request_prefix)
        }
        self.seen_requests.update(self.unpublished)
        self.boundaries: list[SourceBoundary] = []
        self.diagnostics: list[Diagnostic] = list(batch.diagnostics)
        self.revisions: list[Revision] = []
        self.quota: list[QuotaEvidence] = []
        self.batch = batch

    @property
    def ledger(self) -> Ledger:
        return self.state.ledger

    @staticmethod
    def eligible(frame: SourceFrame) -> bool:
        return frame.eligibility is Eligibility.ELIGIBLE and not frame.pre_cutoff

    def gap(self, frame: SourceFrame, code: DiagnosticCode) -> None:
        if self.record_usage and self.eligible(frame):
            self.diagnostics.append(
                Diagnostic(
                    code, frame.observed_at, _PROVIDER, frame.stream_ref, frame.ordinal
                )
            )

    def boundary(
        self,
        frame: SourceFrame,
        kind: BoundaryKind,
        reference: SourceRef,
        receipt: SourceRef | None = None,
    ) -> SourceBoundary:
        return SourceBoundary(
            _PROVIDER,
            frame.stream_ref,
            frame.session_ref,
            frame.ordinal,
            kind,
            reference,
            self.epoch,
            receipt,
        )

    def epoch_reference(self, frame: SourceFrame, root: SourceRef) -> SourceRef:
        return self.ledger.pseudonymize(
            "codex-counter-epoch", f"{frame.stream_ref.value}:{root.value}"
        )

    def startup(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        if (
            frame.ordinal != 0
            or _session(self.ledger, payload.get("id")) != frame.session_ref
            or payload.get("model_provider") != "openai"
        ):
            if commit:
                self.gap(frame, DiagnosticCode.UNKNOWN_USAGE)
            return
        root = _session(self.ledger, payload.get("session_id"))
        if root is None:
            if commit:
                self.gap(frame, DiagnosticCode.IDENTITY_CONFLICT)
            return
        self.epoch = self.epoch_reference(frame, root)
        source = payload.get("source")
        parent = _session(self.ledger, payload.get("parent_thread_id"))
        spawned = _object(_object(_object(source).get("subagent")).get("thread_spawn"))
        independent = (
            root != frame.session_ref
            and parent is not None
            and parent != frame.session_ref
            and _session(self.ledger, spawned.get("parent_thread_id")) == parent
            and payload.get("thread_source") == "subagent"
            and payload.get("history_mode") == "paginated"
        )
        native = (
            root == frame.session_ref
            and parent is None
            and source in ("cli", "exec", "mcp", "vscode")
        )
        inherited = any(
            payload.get(name) is not None
            for name in (
                "forked_from_id",
                "history_base",
                "subagent_history_start_ordinal",
            )
        )
        if commit and not inherited and (native or independent):
            self.baseline = _ZERO

    def remember(self, frame: SourceFrame, request: SourceRef) -> bool:
        if not self.have_history:
            # On restart, the fixed ledger view can identify already published
            # responses. Replays of the same input checkpoint remain identical.
            if self.prior is not None and self.prior.epoch_ref is not None:
                self.seen_requests.update(
                    record.request_ref
                    for entry in self.ledger.as_of().current
                    if isinstance((record := entry.record), UsageObservation)
                    and record.boundary.stream_ref == frame.stream_ref
                    and record.boundary.ordinal <= self.prior.ordinal
                    and record.request_ref is not None
                )
            self.have_history = True
        new = request not in self.seen_requests
        self.seen_requests.add(request)
        return new

    def turn_start(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        context = self.context
        raw_id = _identifier(payload.get("turn_id"))
        raw_root = payload.get("root_turn_id")
        root_id = raw_id if raw_root is None else _identifier(raw_root)
        if raw_id is None or root_id is None:
            if commit:
                self.gap(frame, DiagnosticCode.MALFORMED_USAGE)
                self.baseline = None
            self.context = _Context(
                tainted=context.tainted or context.enrollment_output
            )
            return
        if commit and context.turn is not None:
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            self.baseline = None
        ref = codex_turn_boundary_reference(self.ledger, frame.session_ref, raw_id)
        # A pre-turn marker needs a recognized prior command and a closed
        # preceding turn. A publication timestamp alone supplies no proof.
        receipt = (
            context.next_turn_receipt
            if context.closed_turn is not None
            and context.closed_turn != ref
            and not frame.pre_cutoff
            else None
        )
        start = self.boundary(
            frame,
            BoundaryKind.TURN,
            ref,
            None if receipt is None else receipt.reference,
        )
        self.context = _Context(
            turn=_Turn(
                start,
                frame.segment_ref,
                codex_turn_boundary_reference(self.ledger, frame.session_ref, root_id),
                not frame.pre_cutoff,
            ),
            tainted=context.tainted or context.enrollment_output or frame.pre_cutoff,
        )

    def matches_turn(
        self,
        frame: SourceFrame,
        payload: dict,
        turn: _Turn | None,
        *,
        require_root: bool = False,
    ) -> bool:
        raw_id = _identifier(payload.get("turn_id"))
        if (
            turn is None
            or raw_id is None
            or turn.start.boundary_ref
            != codex_turn_boundary_reference(self.ledger, frame.session_ref, raw_id)
        ):
            return False
        raw_root = payload.get("root_turn_id")
        if raw_root is None:
            return not require_root
        root = _identifier(raw_root)
        return root is not None and turn.root_turn_ref == codex_turn_boundary_reference(
            self.ledger, frame.session_ref, root
        )

    def turn_context(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        context = self.context
        turn = context.turn
        if commit and not self.eligible(frame):
            context.tainted = True
        if not self.matches_turn(frame, payload, turn):
            if commit:
                self.gap(frame, DiagnosticCode.BOUNDARY_UNVERIFIED)
            self.context = _Context(
                ambiguous=True, tainted=context.tainted or context.enrollment_output
            )
            return
        raw_model = payload.get("model")
        model = (
            normalize_model(raw_model) if type(raw_model) is str else ModelLabel.UNKNOWN
        )
        if model is ModelLabel.CLAUDE_OPUS_5_5:
            model = ModelLabel.UNKNOWN
        try:
            effort = Effort(payload.get("effort"))
        except ValueError:
            effort = None
        if not turn.seen_context and turn.segment_ref == frame.segment_ref:
            self.boundaries.append(turn.start)
        if turn.segment_ref != frame.segment_ref:
            self.discard_serial_output()
            context.compaction = None
            context.call = None
            context.serial_output = None
            context.receipt = None
            context.next_turn_receipt = None
        context.turn = replace(
            turn,
            model=model,
            effort=effort,
            processing_tier=None,
            seen_context=True,
            segment_ref=frame.segment_ref,
        )

    def settings(self, frame: SourceFrame, payload: dict) -> None:
        turn = self.context.turn
        if turn is None:
            return
        settings = _object(payload.get("thread_settings"))
        tier = None
        if (
            turn.seen_context
            and turn.segment_ref == frame.segment_ref
            and _session(self.ledger, payload.get("thread_id")) == frame.session_ref
            and settings.get("model_provider_id") == "openai"
            and turn.model is not ModelLabel.UNKNOWN
            and settings.get("model") == turn.model.value
        ):
            configured = settings.get("service_tier")
            # The effective configuration supports a comparison basis. It
            # does not attest the served tier or actual billing.
            if configured == "default":
                tier = ProcessingTier.STANDARD
            elif type(configured) is str:
                try:
                    tier = ProcessingTier(configured)
                except ValueError:
                    pass
        self.context.turn = replace(turn, processing_tier=tier)

    def turn_end(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        context = self.context
        turn = context.turn
        matches = self.matches_turn(frame, payload, turn)
        unsettled = context.response is not None or (turn is not None and not matches)
        if commit and (not matches or not turn.seen_counter or unsettled):
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
        self.context = _Context(
            closed_turn=turn.start.boundary_ref if matches else None,
            next_turn_receipt=context.next_turn_receipt if matches else None,
            tainted=context.tainted or context.enrollment_output or unsettled,
        )

    def discard_serial_output(self) -> None:
        context = self.context
        context.tainted |= context.enrollment_output
        context.enrollment_output = False
        context.receipt = None
        context.serial_output = None

    def response_output(self, frame: SourceFrame, commit: bool) -> None:
        if not commit or self.eligible(frame):
            return
        context = self.context
        if (
            context.receipt is not None
            and context.serial_output == frame.segment_ref
            and context.turn is not None
            and context.turn.segment_ref == frame.segment_ref
            and not frame.pre_cutoff
            and not context.conflict
            and not context.ambiguous
        ):
            # U03 enrolls at the exact response record. Earlier native
            # output can belong to that request if its serial proof survives.
            context.enrollment_output = True
        else:
            context.tainted = True

    def tool(self, frame: SourceFrame, payload: dict, kind: str, commit: bool) -> None:
        context = self.context
        raw_call = _identifier(payload.get("call_id"))
        if raw_call is None:
            context.call = None
            context.parallel = True
            self.discard_serial_output()
            return
        ref = self.ledger.pseudonymize(
            "codex-tool-call", f"{frame.session_ref.value}:{raw_call}"
        )
        if kind in _CALLS:
            self.response_output(frame, commit)
            if context.call is not None or context.parallel:
                context.call = None
                context.parallel = True
            else:
                context.call = _Call(
                    ref, frame.segment_ref, _marker_command(payload, self.marker_root)
                )
            return

        call = context.call
        context.call = None
        if (
            context.parallel
            or call is None
            or not call.response_seen
            or call.call_ref != ref
            or call.segment_ref != frame.segment_ref
        ):
            self.discard_serial_output()
            return
        self.discard_serial_output()
        context.serial_output = frame.segment_ref if not frame.pre_cutoff else None
        command = (
            _marker_output(payload) if call.marker and not frame.pre_cutoff else None
        )
        context.receipt = None
        if command is not None:
            context.receipt = _Receipt(
                codex_receipt_reference(self.ledger, frame.session_ref, command),
                codex_request_boundary_reference(
                    self.ledger, frame.session_ref, command
                ),
            )
            context.next_turn_receipt = context.receipt

    def reject_response(
        self, frame: SourceFrame, code: DiagnosticCode, commit: bool
    ) -> None:
        context = self.context
        context.conflict = True
        context.call = None
        self.discard_serial_output()
        context.next_turn_receipt = None
        context.compaction = None
        if commit:
            self.gap(frame, code)

    def response(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        context = self.context
        turn = context.turn
        if commit and not self.eligible(frame):
            context.tainted = True
        root = _session(self.ledger, payload.get("session_id"))
        owner = _session(self.ledger, payload.get("thread_id"))
        if (
            root is None
            or owner != frame.session_ref
            or self.epoch != self.epoch_reference(frame, root)
        ):
            self.reject_response(frame, DiagnosticCode.IDENTITY_CONFLICT, commit)
            return
        response_id = _identifier(payload.get("response_id"))
        if (
            response_id is None
            or _identifier(payload.get("turn_id")) is None
            or _identifier(payload.get("root_turn_id")) is None
        ):
            self.reject_response(frame, DiagnosticCode.MALFORMED_USAGE, commit)
            return
        if turn is not None and not self.matches_turn(
            frame, payload, turn, require_root=True
        ):
            self.reject_response(frame, DiagnosticCode.IDENTITY_CONFLICT, commit)
            return
        request_ref = self.ledger.pseudonymize(
            "codex-response", f"{self.epoch.value}:{response_id}"
        )
        if not self.remember(frame, request_ref):
            self.reject_response(frame, DiagnosticCode.IDENTITY_CONFLICT, commit)
            return
        if commit:
            # Codex uses the prefix envelope as an identity-only tombstone.
            # The response ID is the only durable identity for unpublished usage.
            self.unpublished[request_ref] = RequestPrefix(
                request_ref, request_ref, frame.ordinal, TokenCounts()
            )
        counts = _counts(payload.get("usage"))
        thread_counts = _counts(payload.get("thread_token_usage"))
        if counts is None or thread_counts is None:
            self.reject_response(frame, DiagnosticCode.MALFORMED_USAGE, commit)
            return
        thread_delta = None
        if commit and self.thread_counts is not None:
            try:
                thread_delta = _difference(self.thread_counts, thread_counts)
            except ValueError:
                self.reject_response(frame, DiagnosticCode.COUNTER_REGRESSION, commit)
                return
        if commit:
            self.thread_counts = thread_counts
        serial = context.serial_output == frame.segment_ref and not frame.pre_cutoff
        same_turn = turn is not None and turn.segment_ref == frame.segment_ref
        receipt = (
            context.receipt
            if serial and same_turn and not context.ambiguous and not context.conflict
            else None
        )
        boundary = self.boundary(
            frame,
            BoundaryKind.REQUEST,
            request_ref if receipt is None else receipt.target,
            None if receipt is None else receipt.reference,
        )
        if same_turn:
            self.boundaries.append(boundary)
        if context.enrollment_output:
            context.tainted |= receipt is None or not self.eligible(frame)
            context.enrollment_output = False
        context.compaction = None
        context.ambiguous |= context.response is not None
        context.response = _Response(
            boundary,
            request_ref,
            counts,
            thread_counts,
            _counts(payload.get("turn_token_usage")),
            thread_delta,
            turn.model if same_turn else ModelLabel.UNKNOWN,
            turn.effort if same_turn else None,
            turn.processing_tier if same_turn else None,
            same_turn and (turn.post_cutoff or serial) and self.eligible(frame),
        )
        context.receipt = None
        context.serial_output = None
        if context.call is not None:
            if context.call.response_seen:
                context.call = None
                context.parallel = True
            else:
                context.call = replace(context.call, response_seen=True)
        else:
            context.parallel = False

    def compacted(self, frame: SourceFrame, payload: dict) -> bool:
        context = self.context
        response = context.response
        turn = context.turn
        checkpoint = _object(payload.get("latest_token_usage_record"))
        response_id = _identifier(checkpoint.get("response_id"))
        first = _uuid(payload.get("first_window_id"))
        previous = _uuid(payload.get("previous_window_id"))
        current = _uuid(payload.get("window_id"))
        number = _number(payload.get("window_number"))
        root = _session(self.ledger, checkpoint.get("session_id"))
        if (
            response is None
            or turn is None
            or response.boundary.ordinal + 1 != frame.ordinal
            or turn.segment_ref != frame.segment_ref
            or context.conflict
            or context.ambiguous
            or first is None
            or previous is None
            or current is None
            or current in (first, previous)
            or not number
            or response_id is None
            or response_id != payload.get("compaction_response_id")
            or root is None
            or self.epoch != self.epoch_reference(frame, root)
            or _session(self.ledger, checkpoint.get("thread_id")) != frame.session_ref
            or not self.matches_turn(frame, checkpoint, turn, require_root=True)
            or response.request_ref
            != self.ledger.pseudonymize(
                "codex-response", f"{self.epoch.value}:{response_id}"
            )
            or _counts(checkpoint.get("usage")) != response.counts
            or _counts(checkpoint.get("thread_token_usage")) != response.thread_counts
            or response.turn_counts is None
            or _counts(checkpoint.get("turn_token_usage")) != response.turn_counts
        ):
            return False
        self.discard_serial_output()
        # Require independent thread-delta proof before display rebaselining.
        if response.thread_delta is not None and _compatible(
            response.thread_delta, response.counts
        ):
            context.compaction = _Compaction(frame.segment_ref)
        else:
            context.tainted = True
        return True

    def continue_compaction(
        self, frame: SourceFrame, kind: str, item: str | None, payload: dict
    ) -> None:
        witness = self.context.compaction
        if witness is None:
            return
        stage = witness.stage
        next_stage = None
        if witness.segment_ref == frame.segment_ref:
            if stage is _CompactionStage.WORLD_STATE:
                if kind == "world_state" and payload.get("full") is True:
                    next_stage = _CompactionStage.TURN_CONTEXT
            elif stage is _CompactionStage.TURN_CONTEXT:
                if kind == "turn_context" and self.matches_turn(
                    frame, payload, self.context.turn
                ):
                    next_stage = _CompactionStage.SETTINGS
            elif stage is _CompactionStage.SETTINGS:
                if (
                    kind == "event_msg"
                    and item == "thread_settings_applied"
                    and _session(self.ledger, payload.get("thread_id"))
                    == frame.session_ref
                ):
                    next_stage = _CompactionStage.DISPLAY
            elif kind == "event_msg" and item == "token_count":
                next_stage = stage
        if next_stage is None:
            self.context.compaction = None
            self.context.tainted = True
        elif next_stage is not stage:
            self.context.compaction = replace(witness, stage=next_stage)

    def rate_limits(self, frame: SourceFrame, raw: object) -> None:
        if raw is None or not self.record_usage or not self.eligible(frame):
            return
        if type(raw) is not dict or raw.get("limit_id", "codex") != "codex":
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        signals = tuple(
            raw[key] for key in ("primary", "secondary") if raw.get(key) is not None
        )
        if not signals:
            return
        account = self.state.account_ref
        if account is None or "limit_id" not in raw:
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        windows: dict[QuotaBucket, QuotaEvidence] = {}
        conflicting = set()
        for value in signals:
            quota = _quota_window(value, account, frame.observed_at)
            if quota is None:
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
                continue
            if windows.setdefault(quota.bucket, quota) != quota:
                conflicting.add(quota.bucket)
        if conflicting:
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
        self.quota.extend(
            quota for key, quota in windows.items() if key not in conflicting
        )

    def finish_counter(self, *, retain_output: bool = False) -> None:
        context = self.context
        if context.enrollment_output and not retain_output:
            self.discard_serial_output()
        context.response = None
        context.compaction = None
        context.ambiguous = context.conflict = False

    def counter(self, frame: SourceFrame, payload: dict, commit: bool) -> None:
        if commit:
            self.rate_limits(frame, payload.get("rate_limits"))
        raw_info = payload.get("info")
        if raw_info is None and "info" in payload:
            return  # A quota-only tick does not consume pending response evidence.
        info = _object(raw_info)
        total = _counts(info.get("total_token_usage"))
        if not commit:
            # Compare look-ahead snapshots only to preserve structural order
            # through repeated display counters. This never updates accounting.
            if total is not None and (
                self.lookahead_total is None
                or self.lookahead_total.total_tokens != total.total_tokens
            ):
                self.lookahead_total = total
                self.finish_counter(retain_output=True)
            return
        context = self.context
        if total is None:
            self.gap(frame, DiagnosticCode.MALFORMED_USAGE)
            self.finish_counter()
            context.tainted = True
            return
        before = self.baseline
        eligible = self.eligible(frame)
        if before is None or not _coherent(before):
            self.finish_counter()
            self.baseline = total
            self.exact_only = not eligible
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        if before.total_tokens == total.total_tokens:
            # Codex can re-emit a stale usage snapshot with a quota update.
            # It does not settle any pending response or excluded activity.
            if not _compatible(before, total):
                self.gap(frame, DiagnosticCode.UNRECONCILED_USAGE)
            if context.tainted or context.enrollment_output:
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return

        compacted = (
            context.compaction is not None
            and context.compaction.stage is _CompactionStage.DISPLAY
        )
        try:
            difference = _difference(before, total)
        except ValueError:
            self.finish_counter()
            if compacted:
                self.baseline = total
                self.exact_only = not eligible
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            else:
                self.gap(frame, DiagnosticCode.COUNTER_REGRESSION)
            return

        last = _counts(info.get("last_token_usage"))
        response = context.response
        ambiguous, conflict = context.ambiguous, context.conflict
        # A separating positive snapshot may settle the preceding request
        # while output of the next receipt-proven request is already present.
        preceding = (
            response is not None
            and last is not None
            and not ambiguous
            and not conflict
            and all(
                _compatible(a, b)
                for a, b in combinations((response.counts, difference, last), 2)
            )
        )
        self.finish_counter(retain_output=preceding)
        tainted, exact_only = context.tainted, self.exact_only
        coherent = _coherent(difference)
        if compacted or (coherent and not conflict):
            context.tainted = False
            self.exact_only = not eligible
        self.baseline = total
        turn = context.turn
        if turn is not None:
            context.turn = replace(turn, seen_counter=True)
        if response is None and not conflict:
            self.thread_counts = None
        if not self.record_usage or not eligible or conflict:
            return
        safe = (
            response.eligible
            if response is not None
            else (
                turn is not None
                and turn.post_cutoff
                and turn.segment_ref == frame.segment_ref
            )
        )
        if compacted or tainted or not safe:
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        if not coherent:
            self.gap(frame, DiagnosticCode.UNRECONCILED_USAGE)
            return

        evidence = [difference]
        if last is not None:
            evidence.append(last)
        if response is not None:
            evidence.append(response.counts)
            if response.thread_delta is not None:
                evidence.append(response.thread_delta)
        reasoning = {
            counts.reasoning_output_tokens
            for counts in evidence
            if counts.reasoning_output_tokens is not None
        }
        agrees = (
            last is not None
            and all(_compatible(a, b) for a, b in combinations(evidence, 2))
            and (
                response is None
                or response.thread_delta is not None
                or _compatible(response.thread_counts, total)
            )
        )
        if before == _ZERO and not agrees:
            # Startup can supply zero only when the first snapshot proves
            # that the apparent first increment is one observed request.
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        complete = agrees and not ambiguous
        if exact_only and (not complete or response is None):
            # A first positive snapshot can separate the numeric baselines.
            # Only the actual reconciled response can qualify that delta.
            self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        if not complete:
            self.gap(frame, DiagnosticCode.UNRECONCILED_USAGE)
        if len(reasoning) > 1:
            difference = replace(difference, reasoning_output_tokens=None)
        self.observe(frame, difference, response, turn, complete)

    def observe(
        self,
        frame: SourceFrame,
        counts: TokenCounts,
        response: _Response | None,
        turn: _Turn | None,
        complete: bool,
    ) -> None:
        request_ref = None
        model, effort, tier = ModelLabel.UNKNOWN, None, None
        if not complete:
            stream = self.ledger.pseudonymize(
                "codex-unallocated-stream", frame.stream_ref.value
            )
            key = self.ledger.pseudonymize(
                "codex-unallocated-usage", f"{self.epoch.value}:{frame.ordinal}"
            )
            boundary = SourceBoundary(
                _PROVIDER,
                stream,
                frame.session_ref,
                frame.ordinal,
                BoundaryKind.REQUEST,
                key,
                self.epoch,
            )
        else:
            if response is not None:
                request_ref, boundary = response.request_ref, response.boundary
                model, effort, tier = (
                    response.model,
                    response.effort,
                    response.processing_tier,
                )
            else:
                request_ref = self.ledger.pseudonymize(
                    "codex-counter-request", f"{self.epoch.value}:{frame.ordinal}"
                )
                boundary = self.boundary(frame, BoundaryKind.REQUEST, request_ref)
                if turn is not None:
                    model, effort, tier = turn.model, turn.effort, turn.processing_tier
            key = self.ledger.pseudonymize(
                "codex-usage", f"{self.epoch.value}:{boundary.ordinal}"
            )
            if model is ModelLabel.UNKNOWN or effort is None:
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
        self.revisions.append(
            Revision(
                key,
                1,
                UsageObservation(
                    boundary,
                    frame.observed_at,
                    frame.client_version,
                    frame.format_version,
                    counts,
                    Availability.COMPLETE if complete else Availability.PARTIAL,
                    request_ref=request_ref,
                    model=model,
                    effort=effort,
                    processing_tier=tier,
                    context_tokens=counts.input_tokens if complete else None,
                ),
            )
        )

    def step(self, frame: SourceFrame, commit: bool) -> None:
        if (
            frame.provider is not _PROVIDER
            or frame.client_version is not _CLIENT
            or frame.format_version != _FORMAT
            or frame.stream_ref != self.batch.cursor.source_ref
        ):
            raise ValueError("Expected a verified Codex frame")
        if self.ordinal is not None and frame.ordinal != self.ordinal + 1:
            self.context = _Context(ambiguous=True)
            if commit:
                self.baseline = None
                self.thread_counts = None
        self.ordinal = frame.ordinal
        kind = frame.row["type"]
        payload = _object(frame.row.get("payload"))
        item = payload.get("type")
        item = item if type(item) is str else None
        self.continue_compaction(frame, kind, item, payload)

        if kind == "session_meta":
            self.startup(frame, payload, commit)
        elif self.epoch is None:
            if commit:
                self.gap(frame, DiagnosticCode.UNKNOWN_USAGE)
        elif kind == "turn_context":
            self.turn_context(frame, payload, commit)
        elif kind == "token_usage_record":
            self.response(frame, payload, commit)
        elif kind == "event_msg" and item == "token_count":
            self.counter(frame, payload, commit)
        elif kind == "compacted":
            if not self.compacted(frame, payload):
                self.discard_serial_output()
                self.context.tainted = True
                if commit:
                    self.gap(frame, DiagnosticCode.UNKNOWN_USAGE)
        elif kind == "event_msg" and item == "thread_settings_applied":
            self.settings(frame, payload)
        elif kind == "event_msg" and item == "task_started":
            self.turn_start(frame, payload, commit)
        elif kind == "event_msg" and item == "task_complete":
            self.turn_end(frame, payload, commit)
        elif kind == "response_item" and item in (_CALLS | _OUTPUTS):
            self.tool(frame, payload, item, commit)
        elif kind == "event_msg" and item in _ATTEMPT_ERRORS:
            self.context.ambiguous = True
            self.context.call = None
            self.discard_serial_output()
            self.context.compaction = None
            if commit:
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
                if not self.eligible(frame):
                    self.context.tainted = True
        elif (
            kind in _NONUSAGE_ROWS
            or (kind == "event_msg" and item in _NONUSAGE_EVENTS)
            or (kind == "response_item" and item in _NONUSAGE_ITEMS)
        ):
            if kind == "response_item" and (
                item == "reasoning"
                or (item == "message" and payload.get("role") == "assistant")
            ):
                self.response_output(frame, commit)
        else:
            self.context.ambiguous = True
            self.context.call = None
            self.discard_serial_output()
            self.context.compaction = None
            if commit:
                self.gap(frame, DiagnosticCode.UNKNOWN_USAGE)
                if not self.eligible(frame):
                    self.context.tainted = True

    def committed(self, published: tuple[Revision, ...] = ()) -> None:
        for frame in self.batch.commit_frames:
            self.step(frame, commit=True)
        # A scanner-rejected row has no SourceFrame. A malformed committed
        # tail still invalidates the span even if the next read has no frames.
        invalid = [
            entry.ordinal
            for entry in self.batch.diagnostics
            if entry.ordinal is not None
            and entry.code
            in (DiagnosticCode.MALFORMED_USAGE, DiagnosticCode.IDENTITY_CONFLICT)
            and (self.ordinal is None or entry.ordinal > self.ordinal)
        ]
        if invalid:
            self.ordinal = max(invalid)
            self.baseline = None
            self.thread_counts = None
            self.context = _Context(ambiguous=True)
        for revision in (*self.revisions, *published):
            self.unpublished.pop(revision.record.request_ref, None)
        if self.prior is not None and self.ordinal is not None:
            baseline = self.baseline
            if baseline is not None and (
                self.context.tainted or self.context.enrollment_output
            ):
                baseline = replace(baseline, total_tokens=None)
            self.checkpoint = replace(
                self.prior,
                epoch_ref=self.epoch,
                ordinal=self.ordinal,
                baseline=baseline,
                request_prefix=tuple(self.unpublished.values()),
            )


def read_codex(
    batch: FrameBatch, state: CodexState, eligibility: Eligibility
) -> AdapterResult:
    """Read verified Codex frames without publishing or advancing transient state.

    U08 uses ELIGIBLE for normal collection and selects explicit exclusions in
    the scanner. The argument can constrain scanner admission, never widen it.
    Join boundaries with FrameBatch.scope_evidence before consuming markers.
    Rescan accepted enrollments before the single cursor and usage commit.
    """
    return _read_codex(batch, state, eligibility)[0]


def _read_codex(
    batch: FrameBatch, state: CodexState, eligibility: Eligibility
) -> tuple[AdapterResult, int | None]:
    if batch.cursor is None:
        return AdapterResult(diagnostics=batch.diagnostics), None
    if (
        batch.provider_checkpoint is None
        or batch.provider_checkpoint.provider is not _PROVIDER
    ):
        raise ValueError("Expected a Codex provider checkpoint")
    walk = _Walk(batch, state, eligibility)
    walk.committed()
    checkpoint = walk.checkpoint
    unsettled = None
    if state.neutral_markers and (
        walk.context.turn is not None or walk.context.next_turn_receipt is not None
    ):
        # The legacy warm state can resume mid-turn. A monitor cursor stores
        # only the durable provider prefix, so replay this unsettled frontier.
        checkpoint = None
        turn = walk.context.turn
        unsettled = walk.ordinal if turn is None else turn.start.ordinal
    walk.lookahead_total = walk.baseline
    for frame in batch.frames[len(batch.commit_frames) :]:
        walk.step(frame, commit=False)
    ordinals = {frame.ordinal for frame in batch.frames}
    return (
        AdapterResult(
            tuple(walk.revisions),
            tuple(dict.fromkeys(walk.diagnostics)),
            tuple(entry for entry in walk.boundaries if entry.ordinal in ordinals),
            checkpoint,
            tuple(walk.quota),
        ),
        unsettled,
    )


def advance_codex_state(
    state: CodexState, batch: FrameBatch, result: AdapterResult
) -> CodexState:
    """Advance sanitized context only after the caller's matching Ledger.apply.

    The scanner's durable checkpoint is the source of truth after a restart.
    This method reconstructs context from the committed prefix alone.
    """
    if batch.cursor is None or result.provider_checkpoint is None:
        return state
    walk = _Walk(batch, state, Eligibility.EXCLUDED)
    walk.committed(result.revisions)
    if walk.checkpoint != result.provider_checkpoint:
        raise ValueError("Expected the matching committed Codex result")
    return replace(
        state,
        _stream_ref=batch.cursor.source_ref,
        _checkpoint=result.provider_checkpoint,
        _context=walk.context,
        _seen_requests=frozenset(walk.seen_requests),
        _have_history=walk.have_history,
        _exact_only=walk.exact_only,
        _thread_counts=walk.thread_counts,
    )
