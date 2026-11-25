"""Claude Code usage from a configured invocation and its exact transcript."""

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import BinaryIO
from uuid import UUID

from ...types import Availability, SourceRef, TokenCounts, _unique_fields
from ..capture import (
    CaptureEvent,
    CaptureGap,
    ExactReference,
    Observation,
    _read_evidence,
    _validate_byte_limit,
)
from ..receipts import (
    Enrollment,
    NativeTurn,
    Outcome,
    TimeBasis,
    UsageReceipt,
    UsageScope,
)

_VERSION = "2.1.331"
_ENTRYPOINTS = {"print": "sdk-cli", "cli": "cli"}
_INTERRUPTION = [{"type": "text", "text": "[Request interrupted by user]"}]


class _Invalid(ValueError):
    def __init__(self, gap: CaptureGap = CaptureGap.MALFORMED) -> None:
        self.gap = gap


def _object(value: object) -> dict:
    if not isinstance(value, dict):
        raise _Invalid()
    return value


def _decode(data: bytes) -> dict:
    try:
        return _object(json.loads(data, object_pairs_hook=_unique_fields))
    except (ValueError, RecursionError):
        raise _Invalid() from None


def _rows(payload: bytes) -> Iterator[tuple[bytes, dict]]:
    for line in payload.splitlines(keepends=True):
        if not line.endswith(b"\n"):
            raise _Invalid()
        yield line, _decode(line)


def _uuid(value: object) -> str:
    if not isinstance(value, str) or len(value) != 36:
        raise _Invalid()
    try:
        if str(UUID(value)) == value:
            return value
    except ValueError:
        pass
    raise _Invalid()


def _key(value: object) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= 256:
        raise _Invalid()
    return value


def _moment(value: object) -> datetime:
    if not isinstance(value, str):
        raise _Invalid()
    try:
        moment = datetime.fromisoformat(value)
        if moment.utcoffset() is not None:
            return moment.astimezone(UTC)
    except (ValueError, OverflowError):
        pass
    raise _Invalid()


def _count(value: object) -> int:
    if type(value) is not int or not 0 <= value < 2**63:
        raise _Invalid()
    return value


@dataclass(frozen=True, slots=True)
class _Usage:
    uncached: int
    read: int
    write_5m: int
    write_1h: int
    output: int
    thinking: int

    def __post_init__(self) -> None:
        _count(self.total)
        if self.thinking > self.output:
            raise _Invalid()

    @property
    def total(self) -> int:
        return self.uncached + self.read + self.write_5m + self.write_1h + self.output

    def __add__(self, other: "_Usage") -> "_Usage":
        return _Usage(
            self.uncached + other.uncached,
            self.read + other.read,
            self.write_5m + other.write_5m,
            self.write_1h + other.write_1h,
            self.output + other.output,
            self.thinking + other.thinking,
        )

    def tokens(self) -> TokenCounts:
        return TokenCounts(
            self.uncached + self.read,
            self.read,
            self.write_5m,
            self.write_1h,
            self.output,
            self.thinking,
            self.total,
        )

    @classmethod
    def from_result(cls, value: object) -> "_Usage":
        row = _object(value)
        usage = cls(
            _count(row.get("inputTokens")),
            _count(row.get("cacheReadInputTokens")),
            _count(row.get("cacheCreationEphemeral5mInputTokens")),
            _count(row.get("cacheCreationEphemeral1hInputTokens")),
            _count(row.get("outputTokens")),
            _count(row.get("thinkingTokens")),
        )
        if usage.write_5m + usage.write_1h != _count(
            row.get("cacheCreationInputTokens")
        ):
            raise _Invalid()
        return usage

    @classmethod
    def from_request(cls, value: object) -> "_Usage":
        row = _object(value)
        cache = _object(row.get("cache_creation"))
        details = _object(row.get("output_tokens_details"))
        usage = cls(
            _count(row.get("input_tokens")),
            _count(row.get("cache_read_input_tokens")),
            _count(cache.get("ephemeral_5m_input_tokens")),
            _count(cache.get("ephemeral_1h_input_tokens")),
            _count(row.get("output_tokens")),
            _count(details.get("thinking_tokens")),
        )
        if usage.write_5m + usage.write_1h != _count(
            row.get("cache_creation_input_tokens")
        ):
            raise _Invalid()
        return usage


_ZERO = _Usage(0, 0, 0, 0, 0, 0)


@dataclass(frozen=True, slots=True)
class _Node:
    line: bytes = field(repr=False)
    row: dict = field(repr=False)
    root: str | None


@dataclass(frozen=True, slots=True)
class _Transcript:
    nodes: dict[str, _Node] = field(repr=False)
    prompts: dict[str, str] = field(repr=False)


def _transcript(evidence: bytes, session: str) -> _Transcript:
    nodes = {}
    prompts = {}
    for line, row in _rows(evidence):
        native_session = row.get("sessionId")
        if native_session is not None and native_session != session:
            raise _Invalid(CaptureGap.WRONG_TURN)
        if "uuid" not in row or row.get("isSidechain") is True:
            continue
        identifier = _uuid(row.get("uuid"))
        if identifier in nodes:
            raise _Invalid(CaptureGap.WRONG_TURN)
        if native_session != session or row.get("isSidechain") is not False:
            raise _Invalid(CaptureGap.WRONG_TURN)
        parent = row.get("parentUuid")
        root = (
            nodes[parent].root if isinstance(parent, str) and parent in nodes else None
        )
        if (
            row.get("type") == "user"
            and row.get("turnPromptId") is not None
            and row.get("turnPromptId") == row.get("promptId")
        ):
            root = _uuid(row["promptId"])
            if root in prompts:
                raise _Invalid(CaptureGap.WRONG_TURN)
            prompts[root] = identifier
        nodes[identifier] = _Node(line, row, root)
    return _Transcript(nodes, prompts)


@dataclass(frozen=True, slots=True)
class _Retained:
    usage: dict[str, _Usage]
    requests: frozenset[tuple[str, str]]
    outcome: Outcome
    started: datetime
    ended: datetime
    digest: str


def _requests(transcript: _Transcript, prompt: str, surface: str) -> _Retained:
    root = transcript.prompts.get(prompt)
    if root is None:
        raise _Invalid(CaptureGap.WRONG_TURN)
    start = transcript.nodes[root]
    seen = {}
    message_owners = {}
    final = {}
    interruption = None
    for node in transcript.nodes.values():
        if node.root != prompt:
            continue
        row = node.row
        if (
            row.get("version") != _VERSION
            or row.get("entrypoint") != _ENTRYPOINTS[surface]
        ):
            raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
        if row.get("type") == "user" and row.get("turnPromptId") is None:
            message = row.get("message")
            if isinstance(message, dict) and message.get("content") == _INTERRUPTION:
                if interruption is not None or row.get("promptId") != prompt:
                    raise _Invalid(CaptureGap.WRONG_TURN)
                interruption = node
        if row.get("type") != "assistant" or row.get("requestId") is None:
            continue
        message = _object(row.get("message"))
        request = _key(row["requestId"])
        message_id = _key(message.get("id"))
        model = _key(message.get("model"))
        if (
            seen.setdefault(request, (message_id, model)) != (message_id, model)
            or message_owners.setdefault(message_id, request) != request
        ):
            raise _Invalid(CaptureGap.WRONG_TURN)
        previous = final.get(request)
        if previous is not None:
            prior = previous.row["message"]
            if prior.get("stop_reason") is not None:
                if message.get("stop_reason") is None:
                    continue
                if (prior.get("stop_reason"), prior.get("usage")) != (
                    message.get("stop_reason"),
                    message.get("usage"),
                ):
                    raise _Invalid()
                continue
        final[request] = node

    for node in transcript.nodes.values():
        row = node.row
        if node.root == prompt or row.get("type") != "assistant":
            continue
        request = row.get("requestId")
        message = row.get("message")
        message_id = message.get("id") if isinstance(message, dict) else None
        if (isinstance(request, str) and request in seen) or (
            isinstance(message_id, str) and message_id in message_owners
        ):
            raise _Invalid(CaptureGap.WRONG_TURN)

    usage = {}
    sources = [start.line]
    for request, node in final.items():
        message = node.row["message"]
        model = seen[request][1]
        usage[model] = usage.get(model, _ZERO) + _Usage.from_request(
            message.get("usage")
        )
        sources.append(node.line)
    last = next(reversed(final.values()), start)
    outcome = Outcome.UNKNOWN
    if interruption is not None:
        outcome = Outcome.INTERRUPTED
        last = interruption
        sources.append(interruption.line)
    elif final and last.row["message"].get("stop_reason") in (
        "end_turn",
        "stop_sequence",
        "max_tokens",
    ):
        if any(
            not isinstance(node.row["message"].get("stop_reason"), str)
            for node in final.values()
        ):
            raise _Invalid()
        outcome = Outcome.COMPLETED
    started, ended = (_moment(node.row.get("timestamp")) for node in (start, last))
    if ended < started:
        raise _Invalid()
    return _Retained(
        usage,
        frozenset((request, pair[0]) for request, pair in seen.items()),
        outcome,
        started,
        ended,
        sha256(b"".join(sources)).hexdigest(),
    )


@dataclass(frozen=True, slots=True)
class ClaudeAdapter:
    """Capture one attempt from a configured Claude Code 2.1.331 session.

    The caller owns the session, account and exact transcript opener. Launch
    one prompt per headless invocation with Claude's native sign-in and
    permissions. On the qualified macOS sign-in, the caller set USER in the
    HarnessCommand environment allowlist; no credential variable was needed.
    Use the independently armed NativeTurn for a Stop hook or an exact read.
    """

    enrollment: Enrollment
    account: SourceRef
    pseudonymize: Callable[[str, str], SourceRef] = field(repr=False)
    session: str = field(repr=False)
    open_transcript: Callable[[str], BinaryIO] | None = field(default=None, repr=False)
    max_bytes: int = 1 << 20
    scope: UsageScope = UsageScope.UNKNOWN

    def __post_init__(self) -> None:
        _uuid(self.session)
        _validate_byte_limit(self.max_bytes)
        if not isinstance(self.scope, UsageScope):
            raise ValueError("Expected a caller-authorized usage scope")

    def native_turn(self, prompt: str, *, surface: str) -> NativeTurn:
        return NativeTurn(
            "claude",
            _VERSION,
            surface,
            self.account,
            self.pseudonymize("claude-session", self.session),
            self.pseudonymize("claude-prompt", f"{self.session}:{_uuid(prompt)}"),
        )

    def _check(self, enrollment: Enrollment) -> None:
        if enrollment != self.enrollment:
            raise _Invalid(CaptureGap.WRONG_ATTEMPT)

    def _lookup(self) -> bytes:
        if self.open_transcript is None:
            raise _Invalid(CaptureGap.MISSING)
        try:
            with self.open_transcript(self.session) as evidence:
                result = _read_evidence(evidence, self.max_bytes)
        except OSError:
            raise _Invalid(CaptureGap.MISSING) from None
        if isinstance(result, CaptureGap):
            raise _Invalid(result)
        return result

    def _observation(
        self,
        native: NativeTurn,
        retained: _Retained,
        outcome: Outcome,
        usage: dict[str, _Usage],
        digest: str,
    ) -> Observation:
        if not usage:
            return Observation(outcome, gap=CaptureGap.MISSING)
        total = sum(usage.values(), _ZERO)
        return Observation(
            outcome,
            UsageReceipt(
                self.enrollment.project_id,
                self.enrollment.attempt_id,
                native,
                digest,
                retained.ended,
                1,
                Availability.COMPLETE
                if outcome is Outcome.COMPLETED
                else Availability.PARTIAL,
                outcome,
                total.tokens(),
                scope=self.scope,
                started_at=retained.started,
                ended_at=retained.ended,
                time_basis=TimeBasis.NATIVE,
            ),
        )

    def observe(self, event: CaptureEvent) -> Observation:
        outcome = Outcome.UNKNOWN
        try:
            self._check(event.enrollment)
            if len(event.stdout) > self.max_bytes or 1 in event.truncated_streams:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            if not event.stdout:
                raise _Invalid(CaptureGap.MISSING)
            rows = _rows(event.stdout)
            _, init = next(rows)
            if (
                init.get("type"),
                init.get("subtype"),
                init.get("claude_code_version"),
            ) != (
                "system",
                "init",
                _VERSION,
            ):
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
            if init.get("session_id") != self.session:
                raise _Invalid(CaptureGap.WRONG_TURN)
            witnesses = []
            terminal = None
            for line, row in rows:
                if row.get("session_id") != self.session:
                    raise _Invalid(CaptureGap.WRONG_TURN)
                if terminal is not None:
                    raise _Invalid()
                kind = row.get("type")
                if kind == "result":
                    terminal = (line, row)
                if (
                    kind in ("assistant", "user")
                    and row.get("parent_tool_use_id") is None
                ):
                    witnesses.append(row)
            if terminal is None:
                raise _Invalid(CaptureGap.MISSING)
            line, result = terminal
            outcome = (
                Outcome.INTERRUPTED
                if result.get("terminal_reason") == "aborted_streaming"
                else Outcome.COMPLETED
                if result.get("terminal_reason") == "completed"
                and result.get("is_error") is False
                else Outcome.FAILED
                if result.get("is_error") is True
                else Outcome.UNKNOWN
            )
            usage = {
                _key(model): _Usage.from_result(counts)
                for model, counts in _object(
                    result.get("model_usage_since_last_result")
                ).items()
            }
            transcript = _transcript(self._lookup(), self.session)
            prompts = set()
            streamed_requests = set()
            for row in witnesses:
                node = transcript.nodes.get(_uuid(row.get("uuid")))
                if (
                    node is None
                    or node.root is None
                    or row.get("type") != node.row.get("type")
                ):
                    raise _Invalid(CaptureGap.WRONG_TURN)
                if row["type"] == "assistant":
                    key = (
                        _key(row.get("request_id")),
                        _key(_object(row.get("message")).get("id")),
                    )
                    if key != (
                        node.row.get("requestId"),
                        _object(node.row.get("message")).get("id"),
                    ):
                        raise _Invalid(CaptureGap.WRONG_TURN)
                    streamed_requests.add(key)
                prompts.add(node.root)
            if len(prompts) != 1:
                raise _Invalid(CaptureGap.WRONG_TURN)
            prompt = prompts.pop()
            retained = _requests(transcript, prompt, "print")
            if not streamed_requests <= retained.requests:
                raise _Invalid(CaptureGap.WRONG_TURN)
            if retained.outcome != outcome:
                raise _Invalid()
            if retained.usage != usage:
                if outcome is not Outcome.INTERRUPTED or retained.usage:
                    raise _Invalid()
                digest = sha256(bytes.fromhex(retained.digest) + line).hexdigest()
            else:
                digest = retained.digest
            return self._observation(
                self.native_turn(prompt, surface="print"),
                retained,
                outcome,
                usage,
                digest,
            )
        except _Invalid as error:
            return Observation(outcome, gap=error.gap)

    def observe_stop(
        self, enrollment: Enrollment, *, expected_turn: NativeTurn, notification: bytes
    ) -> Observation:
        """Match a configured Stop hook to its armed prompt and exact retained turn.

        The caller owns hook execution and may retry a missing read within its
        settle window. The path in the hook body never authorizes a file read.
        """
        try:
            self._check(enrollment)
            if len(notification) > self.max_bytes:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            event = _decode(notification)
            if (
                event.get("hook_event_name") != "Stop"
                or event.get("stop_hook_active") is not False
            ):
                raise _Invalid()
            turn = self.native_turn(_uuid(event.get("prompt_id")), surface="cli")
            if event.get("session_id") != self.session or turn != expected_turn:
                raise _Invalid(CaptureGap.WRONG_TURN)
            observed = self.recover(ExactReference(enrollment, turn, self._lookup()))
            if (
                observed.receipt is not None
                and observed.outcome is not Outcome.COMPLETED
            ):
                raise _Invalid(CaptureGap.WRONG_TURN)
            return observed
        except _Invalid as error:
            return Observation(gap=error.gap)

    def recover(self, exact_ref: ExactReference) -> Observation:
        try:
            self._check(exact_ref.enrollment)
            wanted = exact_ref.turn
            if (
                wanted.provider != "claude"
                or wanted.version != _VERSION
                or wanted.surface not in _ENTRYPOINTS
            ):
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
            if len(exact_ref.evidence) > self.max_bytes:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            if not exact_ref.evidence:
                raise _Invalid(CaptureGap.MISSING)
            transcript = _transcript(exact_ref.evidence, self.session)
            for prompt in transcript.prompts:
                if wanted == self.native_turn(prompt, surface=wanted.surface):
                    retained = _requests(transcript, prompt, wanted.surface)
                    if retained.outcome is Outcome.UNKNOWN:
                        raise _Invalid(CaptureGap.MISSING)
                    return self._observation(
                        wanted,
                        retained,
                        retained.outcome,
                        retained.usage,
                        retained.digest,
                    )
            raise _Invalid(CaptureGap.WRONG_TURN)
        except _Invalid as error:
            return Observation(gap=error.gap)
