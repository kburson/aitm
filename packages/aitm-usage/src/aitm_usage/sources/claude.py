"""Claude Code request revisions from the scanner's verified JSONL prefix."""

import json
import shlex
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import Decimal
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
    LedgerView,
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
)
from .scan import FrameBatch, SidebandFrame, SidebandKind, SourceFrame

_PROVIDER = Provider.CLAUDE
_MODEL = ModelLabel.CLAUDE_OPUS_5_5
_EMPTY = TokenCounts()
_ZERO = TokenCounts(0, 0, 0, 0, 0, total_tokens=0)
_STANDARD_PROCESSING = (
    ("service_tier", "standard"),
    ("speed", "standard"),
    ("inference_geo", "global"),
)
_STOP_REASONS = ("end_turn", "tool_use", "max_tokens", "stop_sequence", "refusal")
_EFFORTS = {
    e.value: e
    for e in (Effort.LOW, Effort.MEDIUM, Effort.HIGH, Effort.XHIGH, Effort.MAX)
}
_WINDOWS = {
    "five_hour": (QuotaBucket.FIVE_HOUR, 18000),
    "seven_day": (QuotaBucket.SEVEN_DAY, 604800),
}
_TELEMETRY = ("api-request", "api-request-shape", "attachment", "queue-operation")
_GAPS = (DiagnosticCode.IDENTITY_CONFLICT, DiagnosticCode.MALFORMED_USAGE)


@dataclass(frozen=True, slots=True)
class _Tool:
    kind: str
    tool_ref: SourceRef
    assistant_ref: SourceRef
    request_ref: SourceRef
    eligible: bool
    ordinal: int = field(compare=False)
    saw_child: bool = False
    uncertain_child: bool = False


@dataclass(frozen=True, slots=True)
class _Receipt:
    boundary_ref: SourceRef
    receipt_ref: SourceRef
    parent_ref: SourceRef
    request_ref: SourceRef
    ordinal: int
    api_ref: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class _Route:
    segment_ref: SourceRef | None = None
    tool: _Tool | None = None
    receipt: _Receipt | None = None
    last_request: SourceRef | None = None
    saw_tool: bool = False


@dataclass(frozen=True, slots=True)
class ClaudeState:
    """One stream's private read context.

    Set reserved_session_id only for the UUID reserved and verified by the
    controlled launcher. Quota requires an independently verified account_ref
    and a matching native owner in the current committed prefix.
    An explicitly supplied prior_view pins the ledger read for this batch.
    """

    ledger: Ledger = field(repr=False)
    reserved_session_id: UUID | None = field(default=None, repr=False)
    account_ref: SourceRef | None = None
    prior_view: LedgerView | None = field(default=None, repr=False)
    _stream_ref: SourceRef | None = field(default=None, repr=False)
    _checkpoint: ProviderCheckpoint | None = field(default=None, repr=False)
    _route: _Route = field(default_factory=_Route, repr=False)
    neutral_markers: bool = False

    def __post_init__(self) -> None:
        if (
            self.reserved_session_id is not None
            and type(self.reserved_session_id) is not UUID
        ):
            raise ValueError("Expected the verified Claude session UUID")
        if self.account_ref is not None:
            self.ledger.validate_source_ref(self.account_ref)
        if (
            self.prior_view is not None
            and self.prior_view.project_id != self.ledger.identity.project_id
        ):
            raise ValueError("Expected a prior ledger view for this project")


def _command_ref(ledger: Ledger, session_ref: SourceRef, command_id: UUID) -> str:
    ledger.validate_source_ref(session_ref)
    if type(command_id) is not UUID:
        raise ValueError("Expected an opaque Claude scope command ID")
    return str(command_id)


def claude_receipt_reference(
    ledger: Ledger, session_ref: SourceRef, command_id: UUID
) -> SourceRef:
    """Derive the U02 receipt reference before publishing the scope command."""
    return ledger.pseudonymize(
        "scope-receipt", _command_ref(ledger, session_ref, command_id)
    )


def claude_request_boundary_reference(
    ledger: Ledger, session_ref: SourceRef, command_id: UUID
) -> SourceRef:
    """Reserve the request following the native Bash command and its receipt."""
    return ledger.pseudonymize(
        "claude-scope-next-request",
        f"{session_ref.value}:{_command_ref(ledger, session_ref, command_id)}",
    )


def _object(value: object) -> dict:
    return value if type(value) is dict else {}


def _identifier(value: object) -> str | None:
    if (
        type(value) is str
        and 0 < len(value) <= 256
        and value.isascii()
        and value.isprintable()
        and value.strip() == value
    ):
        return value
    return None


def _uuid(value: object) -> UUID | None:
    if type(value) is str and len(value) == 36:
        try:
            return UUID(value)
        except ValueError:
            pass
    return None


def _number(value: object) -> int | None:
    return value if type(value) is int and 0 <= value < 2**63 else None


def _sum(*values: int | None) -> int | None:
    if all(value is not None for value in values):
        return _number(sum(values))
    return None


def _tokens(
    uncached, cached, write_5m, write_1h, output, reasoning=None
) -> TokenCounts:
    return TokenCounts(
        _sum(uncached, cached),
        cached,
        write_5m,
        write_1h,
        output,
        reasoning,
        _sum(uncached, cached, write_5m, write_1h, output),
    )


def _usage(raw: dict) -> TokenCounts | None:
    if not raw:
        return None
    details = _object(raw.get("output_tokens_details"))
    writes = _object(raw.get("cache_creation"))
    quantities = (
        (raw, "input_tokens"),
        (raw, "cache_read_input_tokens"),
        (writes, "ephemeral_5m_input_tokens"),
        (writes, "ephemeral_1h_input_tokens"),
        (raw, "output_tokens"),
        (details, "thinking_tokens"),
        (raw, "cache_creation_input_tokens"),
    )
    if (
        raw.get("cache_creation") is not None
        and type(raw["cache_creation"]) is not dict
        or raw.get("output_tokens_details") is not None
        and type(raw["output_tokens_details"]) is not dict
        or any(
            data.get(key) is not None and _number(data[key]) is None
            for data, key in quantities
        )
    ):
        return None
    uncached, cached, write5, write1, output, reasoning, write_total = (
        data.get(key) for data, key in quantities
    )
    if write_total == 0 and write5 is None and write1 is None:
        write5 = write1 = 0
    if (
        write_total is not None
        and any(value is not None and value > write_total for value in (write5, write1))
        or write_total is not None
        and write5 is not None
        and write1 is not None
        and write5 + write1 != write_total
        or reasoning is not None
        and output is not None
        and reasoning > output
    ):
        return None
    counts = _tokens(uncached, cached, write5, write1, output, reasoning)
    return counts if counts != _EMPTY else None


def _components(counts: TokenCounts) -> tuple[int | None, ...]:
    return (
        None
        if counts.input_tokens is None or counts.cached_input_tokens is None
        else counts.input_tokens - counts.cached_input_tokens,
        counts.cached_input_tokens,
        counts.cache_write_5m_tokens,
        counts.cache_write_1h_tokens,
        counts.output_tokens,
    )


def _exact(counts: TokenCounts) -> bool:
    return counts.total_tokens is not None and all(
        value is not None and value >= 0 for value in _components(counts)
    )


def _add(before: TokenCounts, after: TokenCounts) -> TokenCounts | None:
    totals = _tokens(
        *(
            _sum(a, b)
            for a, b in zip(_components(before), _components(after), strict=True)
        )
    )
    return totals if _exact(totals) else None


def _monotonic(before: TokenCounts, after: TokenCounts) -> bool:
    return all(
        old is None or (new is not None and new >= old)
        for old, new in zip(
            (*_components(before), before.reasoning_output_tokens),
            (*_components(after), after.reasoning_output_tokens),
            strict=True,
        )
    )


def _cost_counts(raw: dict) -> TokenCounts | None:
    keys = (
        "inputTokens",
        "cacheReadInputTokens",
        "cacheCreationInputTokens",
        "cacheCreationEphemeral5mInputTokens",
        "cacheCreationEphemeral1hInputTokens",
        "outputTokens",
    )
    values = tuple(_number(raw.get(key)) for key in keys)
    if any(
        key in raw and value is None for key, value in zip(keys, values, strict=True)
    ):
        return None
    uncached, cached, write_total, write5, write1, output = values
    if write_total == 0 and write5 is None and write1 is None:
        write5 = write1 = 0
    if write_total is None or _sum(write5, write1) != write_total:
        return None
    counts = _tokens(uncached, cached, write5, write1, output)
    return counts if _exact(counts) else None


def _quota(frame: SourceFrame, account: SourceRef | None) -> tuple[QuotaEvidence, ...]:
    if account is None or account == frame.session_ref:
        return ()
    data = _object(frame.row.get("rate_limit_info"))
    if data.get("status") not in ("allowed", "allowed_warning", "rejected"):
        return ()
    windows = _object(data.get("unifiedWindows"))
    if not windows and type(data.get("rateLimitType")) is str:
        windows = {data["rateLimitType"]: data}
    results = []
    for label, (bucket, seconds) in _WINDOWS.items():
        window = _object(windows.get(label))
        utilization = window.get("utilization")
        reset = _number(window.get("resetsAt"))
        if type(utilization) not in (float, int) or reset is None:
            continue
        percent = Decimal(str(utilization)) * 100
        if not percent.is_finite() or not 0 <= percent <= 100:
            continue
        precision = max(0, -percent.normalize().as_tuple().exponent)
        if precision > 3:
            continue
        try:
            reset_at = datetime.fromtimestamp(reset, UTC)
        except (OverflowError, OSError, ValueError):
            continue
        if reset_at <= frame.observed_at:
            continue
        results.append(
            QuotaEvidence(
                _PROVIDER,
                account,
                bucket,
                frame.observed_at,
                int(percent * 1000),
                precision,
                QuotaSource.CLAUDE_RATE_LIMIT_EVENT,
                reset_at,
                seconds,
            )
        )
    return tuple(results)


def _pseudonym(
    ledger: Ledger, frame: SourceFrame, domain: str, identity: object
) -> SourceRef | None:
    raw = _identifier(identity)
    return (
        None
        if raw is None
        else ledger.pseudonymize(f"claude-{domain}", f"{frame.session_ref.value}:{raw}")
    )


def _cutoff_origin(ledger: Ledger, api_ref: SourceRef) -> SourceRef:
    return ledger.pseudonymize("claude-api-pre-cutoff", api_ref.value)


def _row_uuid(ledger: Ledger, frame: SourceFrame, field_name: str) -> SourceRef | None:
    raw = _uuid(frame.row.get(field_name))
    return _pseudonym(ledger, frame, "row", str(raw)) if raw is not None else None


def _message(frame: SourceFrame) -> dict:
    message = _object(frame.row.get("message"))
    return (
        message
        if message.get("type") == "message" and message.get("role") == "assistant"
        else {}
    )


def _request_refs(
    ledger: Ledger, frame: SourceFrame, message: dict
) -> tuple[SourceRef | None, SourceRef | None]:
    return (
        _pseudonym(ledger, frame, "request", frame.row.get("requestId")),
        _pseudonym(ledger, frame, "message", message.get("id")),
    )


def _nested(frame: SourceFrame) -> bool:
    return (
        frame.row.get("isSidechain") is True
        or frame.row.get("parent_tool_use_id") is not None
    )


def _parent_tool(ledger: Ledger, frame: SourceFrame) -> SourceRef | None:
    return _pseudonym(ledger, frame, "tool", frame.row.get("parent_tool_use_id"))


def _eligible(frame: SourceFrame, eligibility: Eligibility) -> bool:
    return (
        eligibility is Eligibility.ELIGIBLE
        and frame.eligibility is Eligibility.ELIGIBLE
        and not frame.pre_cutoff
    )


def _marker_command(value: object, project_root: Path | None, session_id: UUID) -> bool:
    if type(value) is not str or len(value) > 8192:
        return False
    try:
        parts = shlex.split(value)
    except ValueError:
        return False
    return (
        len(parts) == 10
        and parts[:2] == ["aitm-usage", "--project"]
        and (
            Path(parts[2]).is_absolute()
            if project_root is None
            else parts[2] == str(project_root)
        )
        and parts[3:6]
        in (["scope", "mark", "--marker"], ["development", "bind", "--binding"])
        and Path(parts[6]).is_absolute()
        and parts[7:] == ["--session-id", str(session_id), "--json"]
        and value == shlex.join(parts)
    )


def _marker_output(block: dict, details: dict) -> UUID | None:
    text = block.get("content")
    if (
        type(text) is not str
        or len(text) > 256
        or type(details.get("stdout")) is not str
        or len(details["stdout"]) > 256
        or details["stdout"].strip() != text.strip()
        or details.get("stderr") != ""
        or details.get("interrupted") is not False
    ):
        return None
    try:
        result = _object(json.loads(text, object_pairs_hook=_unique_fields))
    except (ValueError, RecursionError):
        return None
    if set(result) == {"command_id", "status"} and result["status"] == "queued":
        return _uuid(result["command_id"])
    return None


def _unique_fields(pairs: list[tuple[str, object]]) -> dict:
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("Duplicate structured receipt field")
    return fields


def _explicit_session(ledger: Ledger, frame: SourceFrame) -> bool:
    session = _uuid(frame.row.get("sessionId", frame.row.get("session_id")))
    return (
        session is not None
        and session_reference(ledger, _PROVIDER, str(session)) == frame.session_ref
    )


def _single_tool(message: dict, kind: str) -> dict:
    content = message.get("content")
    if type(content) is list and len(content) == 1:
        block = _object(content[0])
        if block.get("type") == kind:
            return block
    return {}


class _RouteWalk:
    """Prove serialized native tool outcomes without retaining their payloads."""

    def __init__(self, batch: FrameBatch, state: ClaudeState, eligibility: Eligibility):
        self.ledger = state.ledger
        self.session_id = state.reserved_session_id
        self.neutral_markers = state.neutral_markers
        self.marker_root = None if state.neutral_markers else self.ledger.root
        self.reserved_ref = (
            session_reference(self.ledger, _PROVIDER, str(self.session_id))
            if self.session_id is not None
            else None
        )
        self.eligibility = eligibility
        self.route = (
            state._route
            if batch.cursor.source_ref == state._stream_ref
            and batch.provider_checkpoint == state._checkpoint
            else _Route()
        )
        prefix = batch.provider_checkpoint.request_prefix
        self.seen = {entry.request_ref: entry.message_ref for entry in prefix}
        self.messages = set(self.seen.values())
        self.boundaries: dict[int, SourceBoundary] = {}
        self.reports: dict[int, tuple[_Tool, TokenCounts]] = {}
        self.child_results: set[int] = set()
        self.overlap_gaps: set[int] = set()

    def assistant(self, frame: SourceFrame) -> None:
        message = _message(frame)
        req, msg = _request_refs(self.ledger, frame, message)
        tool, receipt = self.route.tool, self.route.receipt
        new_request = (
            req is not None
            and msg is not None
            and req not in self.seen
            and msg not in self.messages
        )
        valid = (
            req is not None
            and msg is not None
            and (new_request or self.seen.get(req) == msg)
            and _usage(_object(message.get("usage"))) is not None
        )
        if new_request and valid:
            self.seen[req] = msg
            self.messages.add(msg)
        if _nested(frame):
            if tool is not None and tool.kind == "agent":
                parent = _parent_tool(self.ledger, frame)
                if not valid or parent is None:
                    tool = replace(tool, uncertain_child=True)
                elif parent == tool.tool_ref:
                    tool = replace(tool, saw_child=True)
                if not valid or parent != tool.tool_ref:
                    self.overlap_gaps.add(frame.ordinal)
            else:
                tool = None
            self.route = replace(self.route, receipt=None, tool=tool)
            return
        if not valid:
            self.route = _Route(frame.segment_ref)
            return
        if receipt is not None:
            if (
                new_request
                and not frame.pre_cutoff
                and req != receipt.request_ref
                and frame.row.get("isSidechain") is False
                and _row_uuid(self.ledger, frame, "parentUuid") == receipt.parent_ref
                and receipt.api_ref is not None
                and self.seen.get(receipt.api_ref)
                != _cutoff_origin(self.ledger, receipt.api_ref)
                and _pseudonym(
                    self.ledger, frame, "api-request", frame.row.get("requestRef")
                )
                == receipt.api_ref
            ):
                self.boundaries[frame.ordinal] = SourceBoundary(
                    _PROVIDER,
                    frame.stream_ref,
                    frame.session_ref,
                    frame.ordinal,
                    BoundaryKind.REQUEST,
                    receipt.boundary_ref,
                    _epoch(self.ledger, frame.session_ref, frame.stream_ref),
                    receipt.receipt_ref,
                )
            self.route = replace(self.route, receipt=None)

        content = message.get("content")
        same_request = req == self.route.last_request
        if type(content) is not list:
            self.route = replace(self.route, tool=None, last_request=req, saw_tool=True)
            return
        has_tool = any(_object(part).get("type") == "tool_use" for part in content)
        if same_request and not has_tool:
            return
        block = _single_tool(message, "tool_use")
        assistant = _row_uuid(self.ledger, frame, "uuid")
        tool_ref = _pseudonym(self.ledger, frame, "tool", block.get("id"))
        kind = None
        if (
            message.get("stop_reason") == "tool_use"
            and frame.row.get("isSidechain") is False
            and assistant is not None
            and tool_ref is not None
            and type(block.get("input")) is dict
        ):
            arguments = block["input"]
            session = self.session_id
            if self.neutral_markers and _explicit_session(self.ledger, frame):
                session = _uuid(frame.row.get("sessionId", frame.row.get("session_id")))
            if (
                block.get("name") == "Bash"
                and session is not None
                and (self.neutral_markers or frame.session_ref == self.reserved_ref)
                and _marker_command(arguments.get("command"), self.marker_root, session)
                and not arguments.get("run_in_background")
            ):
                kind = "bash"
            elif block.get("name") == "Agent" and not any(
                key in arguments
                for key in ("resume", "run_in_background", "isolation", "team_name")
            ):
                kind = "agent"
        proposed = (
            _Tool(
                kind,
                tool_ref,
                assistant,
                req,
                _eligible(frame, self.eligibility),
                frame.ordinal,
            )
            if kind is not None
            else None
        )
        if same_request and self.route.saw_tool and proposed != self.route.tool:
            proposed = None
        self.route = replace(
            self.route,
            tool=proposed,
            last_request=req,
            saw_tool=has_tool,
        )

    def user(self, frame: SourceFrame) -> None:
        tool = self.route.tool
        if (
            self.neutral_markers
            and tool is not None
            and tool.kind == "agent"
            and _nested(frame)
        ):
            # A child's own tool result cannot settle the outer Agent call.
            if _parent_tool(self.ledger, frame) != tool.tool_ref:
                self.route = replace(
                    self.route, tool=replace(tool, uncertain_child=True)
                )
            return
        self.route = _Route(frame.segment_ref)
        if tool is None or frame.row.get("isSidechain") is not False:
            return
        message = _object(frame.row.get("message"))
        block = _single_tool(message, "tool_result")
        details = _object(frame.row.get("toolUseResult"))
        user_ref = _row_uuid(self.ledger, frame, "uuid")
        if (
            message.get("role") != "user"
            or user_ref is None
            or _row_uuid(self.ledger, frame, "parentUuid") != tool.assistant_ref
            or _row_uuid(self.ledger, frame, "sourceToolAssistantUUID")
            != tool.assistant_ref
            or _pseudonym(self.ledger, frame, "tool", block.get("tool_use_id"))
            != tool.tool_ref
            or block.get("is_error", False) is not False
        ):
            return
        if tool.kind == "bash":
            command = _marker_output(block, details)
            if command is not None:
                self.route = replace(
                    self.route,
                    receipt=_Receipt(
                        claude_request_boundary_reference(
                            self.ledger, frame.session_ref, command
                        ),
                        claude_receipt_reference(
                            self.ledger, frame.session_ref, command
                        ),
                        user_ref,
                        tool.request_ref,
                        tool.ordinal,
                    ),
                )
        elif (
            details.get("status") == "completed"
            and _identifier(details.get("agentId")) is not None
        ):
            if tool.saw_child:
                self.child_results.add(frame.ordinal)
            elif (
                not tool.uncertain_child
                and tool.eligible
                and _eligible(frame, self.eligibility)
            ):
                counts = _usage(_object(details.get("usage")))
                if counts is not None:
                    self.reports[frame.ordinal] = (tool, counts)

    def step(self, frame: SourceFrame) -> None:
        if frame.segment_ref != self.route.segment_ref:
            self.route = _Route(frame.segment_ref)
        tool = self.route.tool
        if (
            tool is not None
            and tool.eligible
            and not _eligible(frame, self.eligibility)
        ):
            self.route = replace(self.route, tool=replace(tool, eligible=False))
        kind = frame.row["type"]
        if kind == "assistant":
            self.assistant(frame)
        elif kind == "user":
            self.user(frame)
        elif kind == "attachment" and self.route.receipt is not None:
            receipt = self.route.receipt
            own = _row_uuid(self.ledger, frame, "uuid")
            if (
                own is not None
                and _explicit_session(self.ledger, frame)
                and frame.row.get("isSidechain") is False
                and _row_uuid(self.ledger, frame, "parentUuid") == receipt.parent_ref
            ):
                self.route = replace(
                    self.route, receipt=replace(receipt, parent_ref=own)
                )
            else:
                self.route = replace(self.route, receipt=None)
        elif kind == "api-request":
            api_ref = _pseudonym(self.ledger, frame, "api-request", frame.row.get("id"))
            if api_ref is not None and frame.pre_cutoff:
                self.seen[api_ref] = _cutoff_origin(self.ledger, api_ref)
            if self.route.receipt is not None:
                receipt = self.route.receipt
                self.route = replace(
                    self.route,
                    receipt=(
                        replace(receipt, api_ref=api_ref)
                        if api_ref is not None
                        and receipt.api_ref is None
                        and not frame.pre_cutoff
                        and _explicit_session(self.ledger, frame)
                        else None
                    ),
                )
        elif kind not in (*_TELEMETRY, "rate_limit_event"):
            self.route = _Route(frame.segment_ref)

    def scan(self, frames: tuple[SourceFrame, ...], gaps: set[int]) -> None:
        for frame in frames:
            # Scanner structural gaps cause a new segment. Keep the explicit
            # guard as the last row of a batch may itself have no frame.
            self.step(frame)
        if gaps and (not frames or max(gaps) > frames[-1].ordinal):
            self.route = _Route()


def _epoch(ledger: Ledger, session: SourceRef, stream: SourceRef) -> SourceRef:
    return ledger.pseudonymize(
        "claude-request-epoch", f"{session.value}:{stream.value}"
    )


def _key(ledger: Ledger, stream: SourceRef, request: SourceRef) -> SourceRef:
    return ledger.pseudonymize(
        "claude-usage-observation", f"{stream.value}:{request.value}"
    )


def _isolation(ledger: Ledger, stream: SourceRef, kind: str) -> SourceRef:
    return ledger.pseudonymize(f"claude-{kind}-stream", stream.value)


def _report_key(ledger: Ledger, stream: SourceRef, tool: SourceRef) -> SourceRef:
    return ledger.pseudonymize("claude-agent-report", f"{stream.value}:{tool.value}")


def _metadata(frame: SourceFrame, message: dict) -> tuple[ModelLabel, Effort | None]:
    effort = frame.row.get("effort")
    return (
        (_MODEL if message.get("model") == _MODEL.value else ModelLabel.UNKNOWN),
        _EFFORTS.get(effort) if type(effort) is str else None,
    )


def _processing(raw: dict) -> tuple[ProcessingTier | None, bool]:
    """Qualify Standard only with all fields and distinguish sparse rows."""
    if any(
        key in raw and raw[key] != expected for key, expected in _STANDARD_PROCESSING
    ):
        return None, True
    if all(key in raw for key, _ in _STANDARD_PROCESSING):
        return ProcessingTier.STANDARD, False
    return None, False


def _context(counts: TokenCounts) -> int | None:
    return _sum(
        counts.input_tokens, counts.cache_write_5m_tokens, counts.cache_write_1h_tokens
    )


def _gap_ordinals(batch: FrameBatch) -> set[int]:
    held = next((frame.ordinal for frame in batch.frames if frame.boundary_only), None)
    return {
        entry.ordinal
        for entry in batch.diagnostics
        if entry.ordinal is not None
        and entry.code in _GAPS
        and (held is None or entry.ordinal < held)
    }


class _UsageWalk:
    def __init__(
        self,
        batch: FrameBatch,
        state: ClaudeState,
        eligibility: Eligibility,
        routes: _RouteWalk,
    ):
        self.ledger = state.ledger
        self.view = (
            state.prior_view if state.prior_view is not None else self.ledger.as_of()
        )
        self.batch = batch
        self.routes = routes
        self.eligibility = eligibility
        self.stream = batch.cursor.source_ref
        self.prior = batch.provider_checkpoint
        self.ordinal = self.prior.ordinal
        self.epoch = self.prior.epoch_ref
        stored = next(
            (
                checkpoint
                for checkpoint in self.view.checkpoints
                if checkpoint.cursor.source_ref == self.stream
            ),
            None,
        )
        if (
            stored is not None
            and (
                stored.provider != self.prior
                or stored.cursor.offset > batch.cursor.offset
            )
            or stored is None
            and self.epoch is not None
        ):
            raise ValueError(
                "Claude adapter requires the scanner's fixed prior ledger view"
            )
        self.baseline = self.prior.baseline if self.epoch is not None else _ZERO
        self.prefix = {item.request_ref: item for item in self.prior.request_prefix}
        self.messages = {
            item.message_ref: item.request_ref for item in self.prior.request_prefix
        }
        self.excluded_counts: dict[SourceRef, tuple[TokenCounts, bool]] = {}
        self.unknown_models: dict[SourceRef, SourceRef] = {}
        self.current = {revision.key: revision for revision in self.view.current}
        self.revisions: list[Revision] = []
        self.diagnostics = list(batch.diagnostics)
        self.quota: list[QuotaEvidence] = []
        self.account = state.account_ref
        if any(
            event.kind is SidebandKind.SESSION_OWNER
            and event.content.get("account_ref") != self.account
            for event in batch.commit_sideband
        ):
            self.account = None
        self.owner_segments: set[SourceRef] = set()
        self.latest: SourceFrame | None = None
        self.changed: set[SourceRef] = set()
        self.quota_checked = False

    def gap(
        self,
        frame: SourceFrame | UsageObservation,
        code: DiagnosticCode,
        *,
        ordinal: int | None = None,
    ) -> None:
        if ordinal is None:
            ordinal = (
                frame.ordinal
                if isinstance(frame, SourceFrame)
                else frame.boundary.ordinal
            )
        self.diagnostics.append(
            Diagnostic(code, frame.observed_at, _PROVIDER, self.stream, ordinal)
        )

    def problem(self, frame: SourceFrame, code: DiagnosticCode) -> None:
        self.baseline = None
        if _eligible(frame, self.eligibility):
            self.gap(frame, code)

    def publish(
        self, key: SourceRef, record: UsageObservation, previous: Revision | None
    ) -> None:
        revision = Revision(
            key, 1 if previous is None else previous.revision + 1, record
        )
        self.current[key] = revision
        self.revisions.append(revision)

    def lineage(
        self, req: SourceRef, prefix: RequestPrefix, session: SourceRef
    ) -> Revision | None:
        revision = self.current.get(_key(self.ledger, self.stream, req))
        if revision is not None and isinstance(
            record := revision.record, UsageObservation
        ):
            expected_streams = (
                self.stream,
                _isolation(self.ledger, self.stream, "nested"),
            )
            if (
                record.request_ref == req
                and record.message_ref == prefix.message_ref
                and record.tokens == prefix.tokens
                and record.boundary.provider is _PROVIDER
                and record.boundary.ordinal == prefix.ordinal
                and record.boundary.session_ref == session
                and record.boundary.stream_ref in expected_streams
                and record.boundary.epoch_ref == self.epoch
                and record.boundary.kind is BoundaryKind.REQUEST
                and record.client_version is self.prior.client_version
                and record.format_version == self.prior.format_version
            ):
                return revision
        return None

    def exclude(
        self,
        frame: SourceFrame,
        req: SourceRef,
        msg: SourceRef,
        prior: RequestPrefix | None,
        counts: TokenCounts | None,
        model: ModelLabel,
        stopped: bool,
    ) -> None:
        if prior is None:
            self.prefix[req] = RequestPrefix(req, msg, frame.ordinal, _EMPTY)
            self.messages[msg] = req
        if self.baseline is None:
            return
        earlier = self.excluded_counts.get(req)
        if (
            counts is None
            or model is not _MODEL
            or (prior is not None and earlier is None)
            or (
                earlier is not None
                and (not _monotonic(earlier[0], counts) or (earlier[1] and not stopped))
            )
        ):
            # A restarted tombstone has no per-request quantities. It cannot
            # safely refine the previously committed aggregate baseline.
            self.baseline = None
        else:
            self.excluded_counts[req] = counts, stopped

    def excluded_baseline(self) -> TokenCounts | None:
        total = self.baseline
        for counts, stopped in self.excluded_counts.values():
            if total is None or not stopped or not _exact(counts):
                return None
            total = _add(total, counts)
        return total

    def assistant(self, frame: SourceFrame) -> None:
        message = _message(frame)
        req, msg = _request_refs(self.ledger, frame, message)
        if req is None or msg is None:
            self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
            return
        prior = self.prefix.get(req)
        if (prior is not None and prior.message_ref != msg) or self.messages.get(
            msg, req
        ) != req:
            self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
            return
        raw_usage = _object(message.get("usage"))
        counts = _usage(raw_usage)
        stopped = message.get("stop_reason") in _STOP_REASONS
        model, effort = _metadata(frame, message)
        tier, contradictory_processing = _processing(raw_usage)
        client_ref = _pseudonym(
            self.ledger, frame, "api-request", frame.row.get("requestRef")
        )
        origin = self.prefix.get(client_ref)
        excluded_origin = origin is not None and (
            origin.message_ref != client_ref
            or frame.ordinal not in self.routes.boundaries
        )
        tool = _parent_tool(self.ledger, frame)
        if (
            prior is not None
            and prior.tokens == _EMPTY
            or prior is None
            and (excluded_origin or not _eligible(frame, self.eligibility))
        ):
            if (
                counts is not None
                and tool is not None
                and _key(self.ledger, self.stream, req) not in self.current
            ):
                self.withdraw_overlapping_report(frame, tool)
            self.exclude(frame, req, msg, prior, counts, model, stopped)
            if excluded_origin and _eligible(frame, self.eligibility):
                self.gap(frame, DiagnosticCode.COVERAGE_GAP)
            return
        if not _eligible(frame, self.eligibility):
            # A revision in an excluded segment cannot change an eligible record.
            self.baseline = None
            return
        if counts is None and prior is None:
            self.prefix[req] = RequestPrefix(req, msg, frame.ordinal, _EMPTY)
            self.messages[msg] = req
            self.problem(frame, DiagnosticCode.MALFORMED_USAGE)
            return
        key = _key(self.ledger, self.stream, req)
        model_ref = (
            _pseudonym(self.ledger, frame, "model", message.get("model"))
            if model is ModelLabel.UNKNOWN
            else None
        )
        if prior is None:
            if key in self.current:
                self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
                return
            stream = (
                _isolation(self.ledger, self.stream, "nested")
                if _nested(frame)
                else self.stream
            )
            boundary = self.routes.boundaries.get(frame.ordinal)
            if boundary is None:
                boundary = SourceBoundary(
                    _PROVIDER,
                    stream,
                    frame.session_ref,
                    frame.ordinal,
                    BoundaryKind.REQUEST,
                    req,
                    self.epoch,
                )
            record = UsageObservation(
                boundary,
                frame.observed_at,
                frame.client_version,
                frame.format_version,
                counts,
                Availability.PARTIAL,
                req,
                msg,
                model,
                effort,
                tier,
                _context(counts),
            )
            if model_ref is not None:
                self.unknown_models[req] = model_ref
            previous = None
        else:
            previous = self.lineage(req, prior, frame.session_ref)
            if previous is None or previous.record.model is not model:
                self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
                return
            record = previous.record
            if (
                model is ModelLabel.UNKNOWN
                and counts is not None
                and counts != record.tokens
                and (model_ref is None or self.unknown_models.get(req) != model_ref)
            ):
                self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
                return
            nested_stream = record.boundary.stream_ref != self.stream
            if nested_stream != _nested(frame):
                self.problem(frame, DiagnosticCode.IDENTITY_CONFLICT)
                return
            # Only the original request can qualify a tier. Later processing
            # evidence can invalidate it independently of rejected token counts.
            revised_tier = None if contradictory_processing else record.processing_tier
            issue = None
            if counts is None:
                issue = DiagnosticCode.MALFORMED_USAGE
            elif not _monotonic(record.tokens, counts):
                issue = DiagnosticCode.COUNTER_REGRESSION
            elif (
                record.availability is Availability.COMPLETE
                and counts != record.tokens
                or prior.complete
                and not stopped
            ):
                issue = DiagnosticCode.UNRECONCILED_USAGE
            if issue is not None:
                self.problem(frame, issue)
                if revised_tier is not record.processing_tier:
                    self.publish(
                        key, replace(record, processing_tier=revised_tier), previous
                    )
                return
            record = replace(
                record,
                tokens=counts,
                context_tokens=_context(counts),
                processing_tier=revised_tier,
            )
        self.prefix[req] = RequestPrefix(
            req, msg, record.boundary.ordinal, counts, stopped
        )
        self.messages[msg] = req
        if previous is None or record != previous.record:
            self.publish(key, record, previous)
            self.changed.add(key)
        if tool is not None:
            self.withdraw_overlapping_report(frame, tool)

    def withdraw_overlapping_report(self, frame: SourceFrame, tool: SourceRef) -> None:
        key = _report_key(self.ledger, self.stream, tool)
        prior = self.current.get(key)
        if prior is not None and isinstance(record := prior.record, UsageObservation):
            if (
                record.boundary.provider is _PROVIDER
                and record.boundary.session_ref == frame.session_ref
                and record.boundary.stream_ref
                == _isolation(self.ledger, self.stream, "aggregate")
                and record.boundary.boundary_ref == tool
                and record.boundary.ordinal < frame.ordinal
                and record.availability is Availability.PARTIAL
            ):
                self.publish(
                    key,
                    replace(record, tokens=_EMPTY, availability=Availability.UNKNOWN),
                    prior,
                )
                self.gap(record, DiagnosticCode.OVERLAP_UNVERIFIED)

    def report(self, frame: SourceFrame, tool: _Tool, counts: TokenCounts) -> None:
        parent = self.prefix.get(tool.request_ref)
        if (
            parent is None
            or self.lineage(tool.request_ref, parent, frame.session_ref) is None
        ):
            self.problem(frame, DiagnosticCode.OVERLAP_UNVERIFIED)
            return
        key = _report_key(self.ledger, self.stream, tool.tool_ref)
        stream = _isolation(self.ledger, self.stream, "aggregate")
        boundary = SourceBoundary(
            _PROVIDER,
            stream,
            frame.session_ref,
            frame.ordinal,
            BoundaryKind.REQUEST,
            tool.tool_ref,
            self.epoch,
        )
        record = UsageObservation(
            boundary,
            frame.observed_at,
            frame.client_version,
            frame.format_version,
            counts,
            Availability.PARTIAL,
        )
        self.gap(frame, DiagnosticCode.OVERLAP_UNVERIFIED)
        self.baseline = None
        if key not in self.current:
            self.publish(key, record, None)

    def terminal(
        self,
        models: object,
        session: SourceRef,
        ordinal: int,
        location: SourceFrame | UsageObservation | None,
    ) -> None:
        totals: dict[str, TokenCounts] = {}
        qualified: list[tuple[Revision, UsageObservation]] = []
        baseline = self.excluded_baseline()
        valid = baseline is not None
        if baseline is not None and baseline != _ZERO:
            totals[_MODEL.value] = baseline
        if valid:
            for req, prefix in self.prefix.items():
                if prefix.tokens == _EMPTY:
                    continue
                revision = self.lineage(req, prefix, session)
                if revision is None or not prefix.complete or not _exact(prefix.tokens):
                    valid = False
                    break
                record = revision.record
                if record.model is ModelLabel.UNKNOWN:
                    valid = False
                    break
                model = record.model.value
                total = _add(totals.get(model, _ZERO), prefix.tokens)
                if total is None:
                    valid = False
                    break
                totals[model] = total
                qualified.append((revision, record))
        evidence = _object(models)
        if (
            valid
            and qualified
            and set(evidence) == set(totals)
            and all(
                _cost_counts(_object(evidence[model])) == total
                for model, total in totals.items()
            )
        ):
            for revision, record in qualified:
                if record.availability is Availability.PARTIAL:
                    self.publish(
                        revision.key,
                        replace(record, availability=Availability.COMPLETE),
                        revision,
                    )
            return
        if location is not None:
            self.gap(location, DiagnosticCode.UNRECONCILED_USAGE, ordinal=ordinal)

    def sideband(self, event: SidebandFrame) -> None:
        if self.eligibility is not Eligibility.ELIGIBLE:
            return
        assert event.timed_ordinal is not None and event.segment_ref is not None
        if event.kind is SidebandKind.SESSION_OWNER:
            if self.account is not None:
                self.owner_segments.add(event.segment_ref)
            return
        location = self.latest
        if location is None or location.ordinal != event.timed_ordinal:
            location = None
            if self.prefix:
                # The scanner has checked the historical timed context. An
                # original usage time is the only available timestamp here.
                for prefix in reversed(tuple(self.prefix.values())):
                    prior = self.lineage(prefix.request_ref, prefix, event.session_ref)
                    if prior is not None:
                        location = prior.record
                        break
        self.terminal(
            event.content.get("modelUsage"),
            event.session_ref,
            event.timed_ordinal,
            location,
        )

    def step(self, frame: SourceFrame) -> None:
        if _eligible(frame, self.eligibility):
            self.latest = frame
        kind = frame.row["type"]
        if kind == "assistant":
            if frame.ordinal in self.routes.overlap_gaps and _eligible(
                frame, self.eligibility
            ):
                self.gap(frame, DiagnosticCode.OVERLAP_UNVERIFIED)
            self.assistant(frame)
        elif kind == "user":
            if (
                _eligible(frame, self.eligibility)
                and _object(frame.row.get("toolUseResult")).get("status") == "completed"
            ):
                if frame.ordinal in self.routes.reports:
                    self.report(frame, *self.routes.reports[frame.ordinal])
                elif frame.ordinal not in self.routes.child_results:
                    self.problem(frame, DiagnosticCode.OVERLAP_UNVERIFIED)
        elif kind == "api-request" and not _eligible(frame, self.eligibility):
            # A native API request may start before cutoff or in an excluded
            # checkout and emit its first assistant row after a restart.
            client_ref = _pseudonym(
                self.ledger, frame, "api-request", frame.row.get("id")
            )
            if client_ref is not None and _explicit_session(self.ledger, frame):
                self.prefix.setdefault(
                    client_ref,
                    RequestPrefix(
                        client_ref,
                        _cutoff_origin(self.ledger, client_ref)
                        if frame.pre_cutoff
                        else client_ref,
                        frame.ordinal,
                        _EMPTY,
                    ),
                )
            else:
                self.baseline = None
        elif kind == "result":
            if _eligible(frame, self.eligibility):
                if (
                    frame.row.get("subtype") == "success"
                    and frame.row.get("is_error") is False
                ):
                    self.terminal(
                        frame.row.get("modelUsage"),
                        frame.session_ref,
                        frame.ordinal,
                        frame,
                    )
                else:
                    self.gap(frame, DiagnosticCode.COVERAGE_GAP)
        elif kind == "rate_limit_event":
            if _eligible(frame, self.eligibility):
                account = (
                    self.account if frame.segment_ref in self.owner_segments else None
                )
                quota = _quota(frame, account)
                self.quota.extend(quota)
                self.quota_checked = True
                if not quota:
                    self.gap(frame, DiagnosticCode.COVERAGE_GAP)
        elif kind not in _TELEMETRY:
            self.problem(frame, DiagnosticCode.UNKNOWN_USAGE)

    def run(self, gaps: set[int]) -> ProviderCheckpoint:
        events = sorted(
            [
                (frame.ordinal, frame)
                for frame in (*self.batch.commit_frames, *self.batch.commit_sideband)
            ]
            + [(ordinal, None) for ordinal in gaps],
            key=lambda item: item[0],
        )
        for ordinal, event in events:
            if ordinal < self.ordinal:
                raise ValueError("Claude commit prefix moved backwards")
            self.ordinal = ordinal
            if event is None:
                self.baseline = None
                continue
            epoch = _epoch(self.ledger, event.session_ref, self.stream)
            if self.epoch is not None and epoch != self.epoch:
                raise ValueError("Claude session changed within the logical stream")
            self.epoch = epoch
            if isinstance(event, SidebandFrame):
                self.sideband(event)
            else:
                self.step(event)
        if self.latest is not None and not self.quota_checked:
            self.gap(self.latest, DiagnosticCode.COVERAGE_GAP)
        for key in self.changed:
            current = self.current[key].record
            if current.availability is Availability.PARTIAL:
                self.gap(current, DiagnosticCode.UNRECONCILED_USAGE)
        return replace(
            self.prior,
            epoch_ref=self.epoch,
            ordinal=self.ordinal,
            baseline=self.excluded_baseline()
            if self.epoch is not None
            else self.prior.baseline,
            request_prefix=tuple(self.prefix.values()),
        )


def _validate(batch: FrameBatch) -> None:
    if (
        batch.provider_checkpoint is None
        or batch.provider_checkpoint.provider is not _PROVIDER
        or batch.provider_checkpoint.client_version is not ClientVersion.CLAUDE_2_1_318
        or batch.provider_checkpoint.format_version != 1
    ):
        raise ValueError("Expected a supported Claude Code provider checkpoint")
    if any(
        event.provider is not _PROVIDER or event.stream_ref != batch.cursor.source_ref
        for event in (
            *batch.frames,
            *batch.sideband,
            *batch.commit_frames,
            *batch.commit_sideband,
        )
    ):
        raise ValueError("Expected one verified Claude Code stream")


def read_claude(
    batch: FrameBatch, state: ClaudeState, eligibility: Eligibility
) -> AdapterResult:
    """Read a fixed snapshot. Only its commit frontier can revise usage.

    Join scope proof with batch.scope_evidence, apply an accepted enrollment
    and rescan before publishing the cursor and usage in one ledger batch.
    """
    return _read_claude(batch, state, eligibility)[0]


def _read_claude(
    batch: FrameBatch, state: ClaudeState, eligibility: Eligibility
) -> tuple[AdapterResult, ProviderCheckpoint | None, int | None]:
    if batch.cursor is None:
        return AdapterResult(diagnostics=batch.diagnostics), None, None
    _validate(batch)
    routes = _RouteWalk(batch, state, eligibility)
    gaps = _gap_ordinals(batch)
    routes.scan(batch.commit_frames, gaps)
    walk = _UsageWalk(batch, state, eligibility, routes)
    observed = walk.run(gaps)
    checkpoint = observed
    unsettled = None
    pending = routes.route.tool or routes.route.receipt
    if state.neutral_markers and pending is not None:
        # Replay pending native linkage and nested-tool overlap after restart.
        checkpoint = None
        unsettled = min(
            (
                entry.ordinal
                for entry in observed.request_prefix
                if entry.request_ref == pending.request_ref
            ),
            default=pending.ordinal,
        )
    routes.scan(batch.frames[len(batch.commit_frames) :], set())
    return (
        AdapterResult(
            tuple(walk.revisions),
            tuple(dict.fromkeys(walk.diagnostics)),
            tuple(routes.boundaries.values()),
            checkpoint,
            tuple(walk.quota),
        ),
        observed,
        unsettled,
    )


def retains_streamed_prefix(
    batch: FrameBatch, state: ClaudeState, checkpoint: ProviderCheckpoint
) -> bool:
    """Verify that eligible provisional requests can be revised after restart."""
    return _first_unretained_request(batch, state, checkpoint) is None


def _first_unretained_request(
    batch: FrameBatch, state: ClaudeState, checkpoint: ProviderCheckpoint
) -> int | None:
    retained = {
        item.request_ref: item.message_ref for item in checkpoint.request_prefix
    }
    for frame in batch.commit_frames:
        if frame.row["type"] != "assistant" or not _eligible(
            frame, Eligibility.ELIGIBLE
        ):
            continue
        message = _message(frame)
        if (
            message.get("stop_reason") is not None
            or _usage(_object(message.get("usage"))) is None
        ):
            continue
        request, message_ref = _request_refs(state.ledger, frame, message)
        if message_ref is None or retained.get(request) != message_ref:
            return frame.ordinal
    return None


def advance_claude_state(
    state: ClaudeState, batch: FrameBatch, result: AdapterResult
) -> ClaudeState:
    """Carry only sanitized tool order after the matching ledger commit."""
    if batch.cursor is None or result.provider_checkpoint is None:
        return state
    _validate(batch)
    view = state.ledger.as_of()
    if not any(
        entry.cursor == batch.cursor and entry.provider == result.provider_checkpoint
        for entry in view.checkpoints
    ):
        raise ValueError("Expected the committed Claude adapter result")
    routes = _RouteWalk(batch, state, Eligibility.ELIGIBLE)
    routes.scan(batch.commit_frames, _gap_ordinals(batch))
    return replace(
        state,
        prior_view=None,
        _stream_ref=batch.cursor.source_ref,
        _checkpoint=result.provider_checkpoint,
        _route=routes.route,
    )
