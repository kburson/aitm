"""Exact local Codex Desktop lifecycle signals and retained turn recovery."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from ..types import Availability, SourceRef, TokenCounts
from .adapters.codex import (
    _TERMINAL,
    _ZERO,
    _Counts,
    _decode,
    _id,
    _Invalid,
    _moment,
    _object,
    _rows,
)
from .capture import CaptureGap, Observation, _read_evidence, _validate_byte_limit
from .receipts import (
    Enrollment,
    NativeTurn,
    Outcome,
    TimeBasis,
    UsageReceipt,
    UsageScope,
)

_BUILD = "0.171.0-alpha.13.2"
_HOOKS = frozenset(
    {
        "UserPromptSubmit",
        "Stop",
        "Interrupt",
        "SubagentStart",
        "SubagentStop",
        "PreCompact",
        "PostCompact",
        "PreModelRequest",
        "PostModelRequest",
    }
)


@dataclass(frozen=True, slots=True)
class CodexHook:
    """Private correlation hints. The caller separately authorizes any path."""

    event: str
    session_id: str = field(repr=False)
    turn_id: str = field(repr=False)
    agent_id: str | None = field(repr=False)
    transcript_path: str | None = field(repr=False)
    model: str | None


def _model(value: object) -> str | None:
    if value is not None and (
        not isinstance(value, str)
        or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._+:/-]{0,95}", value)
    ):
        raise _Invalid()
    return value


def parse_codex_hook(raw: bytes) -> CodexHook:
    """Read exact identity fields without retaining prompts or messages."""
    try:
        if len(raw) > 1 << 20:
            raise _Invalid()
        payload = _decode(raw)
        name = payload.get("hook_event_name")
        if not isinstance(name, str) or name not in _HOOKS:
            raise _Invalid()
        subagent = name in {"SubagentStart", "SubagentStop"}
        agent_id = payload.get("agent_id")
        if subagent or agent_id is not None:
            agent_id = _id(agent_id)
        # Only SubagentStop puts the parent in the ordinary transcript field.
        path = payload.get(
            "agent_transcript_path" if name == "SubagentStop" else "transcript_path"
        )
        if path is not None and (
            not isinstance(path, str)
            or not 0 < len(path) < 4096
            or not Path(path).is_absolute()
            or "\0" in path
        ):
            raise _Invalid()
        return CodexHook(
            name,
            _id(payload.get("session_id")),
            _id(payload.get("turn_id")),
            agent_id,
            path,
            _model(payload.get("model")),
        )
    except _Invalid:
        raise ValueError("Invalid Codex lifecycle callback") from None


@dataclass(frozen=True, slots=True)
class CodexRequestUsage:
    model: str | None
    tokens: TokenCounts


@dataclass(frozen=True, slots=True)
class CodexDesktopCapture:
    observation: Observation
    model: str | None = None
    requests: tuple[CodexRequestUsage, ...] = ()


@dataclass(slots=True)
class _DesktopTurn:
    turn_id: str = field(repr=False)
    root_id: str = field(repr=False)
    offset: int
    started: datetime
    model: str | None = None
    context: bool = False
    counts: _Counts = _ZERO
    requests: list[CodexRequestUsage] = field(default_factory=list)
    response_ids: set[str] = field(default_factory=set, repr=False)

    def check(self, payload: dict) -> None:
        if (payload.get("turn_id"), payload.get("root_turn_id")) != (
            self.turn_id,
            self.root_id,
        ):
            raise _Invalid(CaptureGap.WRONG_TURN)

    def record(self, payload: dict, thread: str, session: str) -> None:
        self.check(payload)
        if (payload.get("thread_id"), payload.get("session_id")) != (thread, session):
            raise _Invalid(CaptureGap.WRONG_TURN)
        response_id = payload.get("response_id")
        if (
            not self.context
            or not isinstance(response_id, str)
            or not 0 < len(response_id) <= 256
        ):
            raise _Invalid()
        if response_id in self.response_ids:
            raise _Invalid(CaptureGap.WRONG_TURN)
        last = _Counts.read(payload.get("usage"), retained=True)
        cumulative = _Counts.read(payload.get("turn_token_usage"), retained=True)
        if cumulative.since(self.counts) != last:
            raise _Invalid()
        self.counts = cumulative
        self.response_ids.add(response_id)
        self.requests.append(CodexRequestUsage(self.model, last.tokens()))


def _check_metadata(row: dict, thread: str, parent: str | None) -> None:
    if row.get("type") != "session_meta":
        raise _Invalid()
    metadata = _object(row.get("payload"))
    if (
        metadata.get("cli_version") != _BUILD
        or metadata.get("originator") != "Codex Desktop"
    ):
        raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
    if metadata.get("id") != thread or metadata.get("session_id") != (parent or thread):
        raise _Invalid(CaptureGap.WRONG_TURN)
    source = metadata.get("source")
    if parent is None:
        if source != "vscode" or metadata.get("thread_source") not in (
            "user",
            "agent_created_thread",
        ):
            raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
    else:
        if metadata.get("thread_source") != "subagent":
            raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
        spawn = _object(_object(_object(source).get("subagent")).get("thread_spawn"))
        if spawn.get("parent_thread_id") != parent:
            raise _Invalid(CaptureGap.WRONG_TURN)


def _match_start(
    payload: dict,
    turn_id: str | None,
    parent_turn_id: str | None,
    *,
    agent_created_owner: bool = False,
) -> tuple[str, str] | None:
    candidate = _id(payload.get("turn_id"))
    if turn_id is not None and candidate != turn_id:
        return None
    attribution = _object(payload.get("turn_attribution"))
    declared_parent = attribution.get("parent_turn_id")
    # App-tool follow-ups in an agent-created Desktop chat carry the sending
    # turn's lineage. Their native owner thread and per-turn usage IDs are
    # still checked against the caller's exact enrolled reference.
    forwarded_owner = (
        agent_created_owner
        and attribution.get("turn_trigger") == "app_tool_send_message"
        and declared_parent is not None
        and _id(declared_parent) != candidate
    )
    if declared_parent != parent_turn_id and not forwarded_owner:
        if turn_id is not None:
            raise _Invalid(CaptureGap.WRONG_TURN)
        return None
    root_id = _id(payload.get("root_turn_id"))
    if (
        attribution.get("turn_id") != candidate
        or attribution.get("root_turn_id") != root_id
        or (parent_turn_id is None and not forwarded_owner and root_id != candidate)
        or ((parent_turn_id is not None or forwarded_owner) and candidate == root_id)
    ):
        raise _Invalid(CaptureGap.WRONG_TURN)
    return candidate, root_id


def _retained_bytes(path: Path, max_bytes: int) -> bytes:
    _validate_byte_limit(max_bytes)
    with path.open("rb") as stream:
        evidence = _read_evidence(stream, max_bytes)
    if isinstance(evidence, CaptureGap):
        raise _Invalid(evidence)
    # A concurrent writer may be appending the next JSON row.
    complete = evidence[: evidence.rfind(b"\n") + 1]
    if not complete:
        raise _Invalid(CaptureGap.MISSING)
    return complete


def codex_child_parent_turn(
    *,
    path: Path,
    session_id: str,
    turn_id: str,
    parent_session_id: str,
    max_bytes: int = 32 * 1024 * 1024,
) -> str | None:
    """Read a child callback's exact parent turn from its authorized transcript.

    The child file need not be complete. Missing retained start evidence is
    pending; conflicting identity must not be treated as a pending match.
    """
    try:
        thread, wanted, parent = map(_id, (session_id, turn_id, parent_session_id))
        if not path.is_absolute() or thread == parent:
            raise _Invalid(CaptureGap.WRONG_TURN)
        rows = _rows(_retained_bytes(path, max_bytes))
        _, _, header = next(rows, (0, 0, {}))
        _check_metadata(header, thread, parent)
        found = None
        for _, _, row in rows:
            if row.get("type") != "event_msg":
                continue
            payload = _object(row.get("payload"))
            if (
                payload.get("type") != "task_started"
                or payload.get("turn_id") != wanted
            ):
                continue
            if found is not None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            attribution = _object(payload.get("turn_attribution"))
            found = _id(attribution.get("parent_turn_id"))
            _match_start(payload, wanted, found)
        return found
    except FileNotFoundError:
        return None
    except _Invalid as error:
        if error.gap is CaptureGap.MISSING:
            return None
        raise ValueError("Codex child parent-turn evidence is invalid") from None
    except (OSError, TypeError, ValueError, OverflowError):
        raise ValueError("Codex child parent-turn evidence is invalid") from None


def _desktop_turn(
    evidence: bytes,
    thread: str,
    turn_id: str | None,
    parent: str | None,
    parent_turn: str | None,
) -> tuple[_DesktopTurn, datetime, int, Outcome]:
    rows = _rows(evidence)
    _, _, metadata = next(rows, (0, 0, {}))
    _check_metadata(metadata, thread, parent)
    agent_created_owner = (
        parent is None
        and turn_id is not None
        and metadata["payload"].get("thread_source") == "agent_created_thread"
    )

    active = None
    finished = None
    copied_parent = False
    for offset, end, row in rows:
        kind = row.get("type")
        payload = _object(row.get("payload"))
        event = payload.get("type") if kind == "event_msg" else None
        if kind == "session_meta":
            if (
                parent is None
                or copied_parent
                or active is not None
                or finished is not None
            ):
                raise _Invalid(CaptureGap.WRONG_TURN)
            _check_metadata(row, parent, None)
            copied_parent = True
        elif event == "task_started":
            if active is not None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            match = _match_start(
                payload, turn_id, parent_turn, agent_created_owner=agent_created_owner
            )
            if match is not None:
                if finished is not None:
                    raise _Invalid(CaptureGap.WRONG_TURN)
                active = _DesktopTurn(*match, offset, _moment(row))
        elif active is not None and kind == "turn_context":
            active.check(payload)
            active.context = True
            active.model = _model(payload.get("model"))
        elif active is not None and kind == "token_usage_record":
            active.record(payload, thread, parent or thread)
        elif active is not None and isinstance(event, str) and event in _TERMINAL:
            active.check(payload)
            ended = _moment(row)
            if ended < active.started:
                raise _Invalid()
            outcome = _TERMINAL[event]
            if outcome is Outcome.COMPLETED and payload.get("error") is not None:
                outcome = Outcome.FAILED
            finished = active, ended, end, outcome
            active = None
    if active is not None or finished is None:
        # A requested reference is durably pending until its exact file and
        # native terminal record reach retained storage.
        raise _Invalid(CaptureGap.MISSING)
    return finished


def recover_codex_desktop(
    enrollment: Enrollment,
    *,
    account: SourceRef,
    pseudonymize: Callable[[str, str], SourceRef],
    path: Path,
    session_id: str,
    turn_id: str | None,
    parent_session_id: str | None = None,
    parent_turn_id: str | None = None,
    max_bytes: int = 32 * 1024 * 1024,
) -> CodexDesktopCapture:
    """Recover one exact turn from a caller-authorized file without a scan.

    A child additionally needs its dispatch's parent session and turn. If the
    callback did not supply a verified child turn ID, only one retained direct
    child turn linked to the recorded parent turn is sufficient.
    """
    try:
        thread = _id(session_id)
        wanted = None if turn_id is None else _id(turn_id)
        child = parent_session_id is not None
        parent = _id(parent_session_id) if child else None
        parent_turn = _id(parent_turn_id) if child else None
        if (
            not path.is_absolute()
            or (not child and (wanted is None or parent_turn_id is not None))
            or (
                child
                and (
                    parent == thread
                    or parent_turn == wanted
                    or enrollment.parent_attempt_id is None
                )
            )
        ):
            raise _Invalid(CaptureGap.WRONG_ATTEMPT)
        evidence = _retained_bytes(path, max_bytes)
        turn, ended, end, outcome = _desktop_turn(
            evidence, thread, wanted, parent, parent_turn
        )
        coverage = Availability.UNKNOWN
        if turn.requests:
            coverage = (
                Availability.COMPLETE
                if outcome is Outcome.COMPLETED and turn.counts.reasoning is not None
                else Availability.PARTIAL
            )
        native = NativeTurn(
            "codex",
            _BUILD,
            "desktop-subagent" if child else "desktop",
            account,
            pseudonymize("codex-session", thread),
            pseudonymize("codex-turn", f"{thread}:{turn.turn_id}"),
        )
        receipt = UsageReceipt(
            enrollment.project_id,
            enrollment.attempt_id,
            native,
            sha256(evidence[turn.offset : end]).hexdigest(),
            ended,
            1,
            coverage,
            outcome,
            turn.counts.tokens() if turn.requests else TokenCounts(),
            scope=UsageScope.BOUNDED,
            started_at=turn.started,
            ended_at=ended,
            time_basis=TimeBasis.NATIVE,
        )
        models = {request.model for request in turn.requests}
        model = next(iter(models)) if len(models) == 1 else None
        gap = None if turn.requests else CaptureGap.MISSING
        return CodexDesktopCapture(
            Observation(outcome, receipt, gap), model, tuple(turn.requests)
        )
    except OSError:
        return CodexDesktopCapture(Observation(gap=CaptureGap.MISSING))
    except _Invalid as error:
        return CodexDesktopCapture(Observation(gap=error.gap))
    except (TypeError, ValueError, OverflowError):
        return CodexDesktopCapture(Observation(gap=CaptureGap.MALFORMED))
