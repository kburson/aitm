"""Codex exec and configured TUI capture using caller-authorized local rollouts."""

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

_VERSION = "0.171.0-alpha.13"
_VERSIONS = frozenset({_VERSION, "0.171.0-alpha.13.2"})
_SURFACES = frozenset({"exec", "cli"})
_TERMINAL = {"task_complete": Outcome.COMPLETED, "turn_aborted": Outcome.INTERRUPTED}


class _Invalid(ValueError):
    def __init__(self, gap: CaptureGap = CaptureGap.MALFORMED) -> None:
        self.gap = gap


def _object(value: object) -> dict:
    if not isinstance(value, dict):
        raise _Invalid()
    return value


def _decode(line: bytes) -> dict:
    try:
        return _object(json.loads(line, object_pairs_hook=_unique_fields))
    except (ValueError, RecursionError):
        raise _Invalid() from None


def _rows(data: bytes) -> Iterator[tuple[int, int, dict]]:
    start = 0
    for line in data.splitlines(keepends=True):
        end = start + len(line)
        if not line.endswith(b"\n"):
            raise _Invalid()
        yield start, end, _decode(line)
        start = end


def _id(value: object) -> str:
    if not isinstance(value, str) or len(value) != 36:
        raise _Invalid()
    try:
        canonical = str(UUID(value))
    except ValueError:
        raise _Invalid() from None
    if canonical != value:
        raise _Invalid()
    return value


def _count(value: object) -> int:
    if type(value) is not int or not 0 <= value < 2**63:
        raise _Invalid()
    return value


@dataclass(frozen=True, slots=True)
class _Counts:
    gross: int
    cached: int
    output: int
    reasoning: int | None

    def __post_init__(self) -> None:
        if (
            self.gross < 0
            or not 0 <= self.cached <= self.gross
            or not 0 <= self.output < 2**63 - self.gross
            or (self.reasoning is not None and not 0 <= self.reasoning <= self.output)
        ):
            raise _Invalid()

    @classmethod
    def read(cls, value: object, *, retained: bool) -> "_Counts":
        data = _object(value)
        reasoning = data.get("reasoning_output_tokens")
        counts = cls(
            _count(data.get("input_tokens")),
            _count(data.get("cached_input_tokens")),
            _count(data.get("output_tokens")),
            None if reasoning is None else _count(reasoning),
        )
        if _count(data.get("cache_write_input_tokens", 0)) != 0 or (
            retained
            and _count(data.get("total_tokens")) != counts.gross + counts.output
        ):
            raise _Invalid()
        return counts

    def since(self, before: "_Counts") -> "_Counts":
        return _Counts(
            self.gross - before.gross,
            self.cached - before.cached,
            self.output - before.output,
            None
            if self.reasoning is None or before.reasoning is None
            else self.reasoning - before.reasoning,
        )

    def tokens(self) -> TokenCounts:
        return TokenCounts(
            input_tokens=self.gross,
            cached_input_tokens=self.cached,
            output_tokens=self.output,
            reasoning_output_tokens=self.reasoning,
            total_tokens=self.gross + self.output,
        )


_ZERO = _Counts(0, 0, 0, 0)


def _moment(row: dict) -> datetime:
    value = row.get("timestamp")
    if not isinstance(value, str):
        raise _Invalid()
    try:
        moment = datetime.fromisoformat(value)
        if moment.utcoffset() is None:
            raise _Invalid()
        return moment.astimezone(UTC)
    except (ValueError, OverflowError):
        raise _Invalid() from None


@dataclass(frozen=True, slots=True)
class _Turn:
    identifier: str
    start: int
    end: int
    started: datetime
    ended: datetime
    outcome: Outcome
    counts: _Counts | None
    cumulative: _Counts | None
    models: frozenset[str | None]
    requests: tuple[TokenCounts, ...]


@dataclass(slots=True)
class _ActiveTurn:
    identifier: str
    offset: int
    started: datetime
    before: _Counts
    last: _Counts | None
    cumulative: _Counts | None = None
    pending_counter: tuple[_Counts, _Counts] | None = None
    context: bool = False
    model: str | None = None
    models: set[str | None] = field(default_factory=set)
    requests: list[TokenCounts] = field(default_factory=list)

    def bind(self, payload: dict) -> None:
        if (
            payload.get("turn_id") != self.identifier
            or payload.get("root_turn_id", self.identifier) != self.identifier
        ):
            raise _Invalid(CaptureGap.WRONG_TURN)

    def count(self, info: dict) -> None:
        if not self.context:
            raise _Invalid(CaptureGap.WRONG_TURN)
        after = _Counts.read(info.get("total_token_usage"), retained=True)
        last = _Counts.read(info.get("last_token_usage"), retained=True)
        if self.pending_counter is not None:
            if self.pending_counter != (after, last):
                raise _Invalid()
            self.pending_counter = None
            return
        # Quota updates can re-emit the preceding request's exact usage.
        if after == (self.cumulative or self.before) and self.last is not None:
            if last != self.last:
                raise _Invalid()
            return
        self.advance(after, last)

    def record(self, payload: dict, session: str) -> str:
        self.bind(payload)
        if (
            not self.context
            or payload.get("session_id") != session
            or payload.get("thread_id") != session
            or payload.get("root_turn_id") != self.identifier
        ):
            raise _Invalid(CaptureGap.WRONG_TURN)
        response = payload.get("response_id")
        if not isinstance(response, str) or not 0 < len(response) <= 256:
            raise _Invalid()
        after = _Counts.read(payload.get("thread_token_usage"), retained=True)
        turn = _Counts.read(payload.get("turn_token_usage"), retained=True)
        last = _Counts.read(payload.get("usage"), retained=True)
        if after.since(self.before) != turn:
            raise _Invalid()
        self.advance(after, last)
        self.pending_counter = after, last
        return response

    def advance(self, after: _Counts, last: _Counts) -> None:
        if after.since(self.cumulative or self.before) != last:
            raise _Invalid()
        self.cumulative = after
        self.last = last
        self.models.add(self.model)
        self.requests.append(last.tokens())

    def finish(self, offset: int, row: dict, outcome: Outcome) -> _Turn:
        ended = _moment(row)
        if ended < self.started:
            raise _Invalid()
        return _Turn(
            self.identifier,
            self.offset,
            offset,
            self.started,
            ended,
            outcome,
            None if self.cumulative is None else self.cumulative.since(self.before),
            self.cumulative,
            frozenset(self.models),
            tuple(self.requests),
        )


@dataclass(frozen=True, slots=True)
class _Rollout:
    session: str
    version: str
    surface: str
    turns: tuple[_Turn, ...]
    active: str | None


def _rollout(evidence: bytes) -> _Rollout:
    rows = _rows(evidence)
    _, _, metadata = next(rows, (0, 0, {}))
    if metadata.get("type") != "session_meta":
        raise _Invalid()
    payload = _object(metadata.get("payload"))
    session = _id(payload.get("id"))
    if payload.get("session_id", session) != session:
        raise _Invalid(CaptureGap.WRONG_TURN)
    surface = payload.get("source")
    version = payload.get("cli_version")
    if (
        not isinstance(version, str)
        or version not in _VERSIONS
        or not isinstance(surface, str)
        or surface not in _SURFACES
    ):
        raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)

    active = None
    before = _ZERO
    last = None
    turns = []
    seen = set()
    responses = set()
    for offset, end, row in rows:
        kind = row.get("type")
        payload = _object(row.get("payload"))
        event = payload.get("type") if kind == "event_msg" else None
        if kind == "session_meta":
            raise _Invalid(CaptureGap.WRONG_TURN)
        if event == "task_started":
            identifier = _id(payload.get("turn_id"))
            if active is not None or identifier in seen:
                raise _Invalid(CaptureGap.WRONG_TURN)
            active = _ActiveTurn(identifier, offset, _moment(row), before, last)
            active.bind(payload)
            seen.add(identifier)
        elif kind == "turn_context" and active is not None:
            active.bind(payload)
            active.context = True
            model = payload.get("model")
            active.model = model if isinstance(model, str) else None
        elif kind == "token_usage_record":
            if active is None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            response = active.record(payload, session)
            if response in responses:
                raise _Invalid(CaptureGap.WRONG_TURN)
            responses.add(response)
        elif event == "token_count" and payload.get("info") is not None:
            if active is None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            active.count(_object(payload["info"]))
        elif isinstance(event, str) and event in _TERMINAL:
            if active is None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            active.bind(payload)
            outcome = _TERMINAL[event]
            if outcome is Outcome.COMPLETED and payload.get("error") is not None:
                outcome = Outcome.FAILED
            turn = active.finish(end, row, outcome)
            turns.append(turn)
            before = turn.cumulative or before
            last = active.last
            active = None
    return _Rollout(
        session,
        version,
        surface,
        tuple(turns),
        None if active is None else active.identifier,
    )


@dataclass(frozen=True, slots=True)
class CodexResume:
    """An exclusive enrolled session's exact retained prefix read before launch."""

    session: str = field(repr=False)
    evidence: bytes = field(repr=False)

    def __post_init__(self) -> None:
        _id(self.session)


@dataclass(frozen=True, slots=True)
class _Exec:
    session: str
    outcome: Outcome = Outcome.UNKNOWN
    counts: _Counts | None = None


def _exec(stdout: bytes) -> _Exec:
    session = None
    started = False
    outcome = Outcome.UNKNOWN
    counts = None
    for _, _, row in _rows(stdout):
        kind = row.get("type")
        if outcome is not Outcome.UNKNOWN or not isinstance(kind, str):
            raise _Invalid()
        if kind == "thread.started":
            if session is not None:
                raise _Invalid(CaptureGap.WRONG_TURN)
            session = _id(row.get("thread_id"))
        elif kind == "turn.started":
            if session is None or started:
                raise _Invalid(CaptureGap.WRONG_TURN)
            started = True
        elif kind in ("turn.completed", "turn.failed"):
            if not started:
                raise _Invalid(CaptureGap.WRONG_TURN)
            outcome = Outcome.COMPLETED if kind == "turn.completed" else Outcome.FAILED
            if kind == "turn.completed" or "usage" in row:
                counts = _Counts.read(row.get("usage"), retained=False)
    if session is None:
        raise _Invalid(CaptureGap.WRONG_TURN if stdout else CaptureGap.MISSING)
    return _Exec(session, outcome, counts)


@dataclass(frozen=True, slots=True)
class CodexAdapter:
    """Consume one caller-authorized Codex v0.171.0-alpha.13 capture.

    The caller supplies its configured account, project-keyed pseudonymizer and
    exact-file opener. Hold exclusive ownership of the enrolled session from
    the prelaunch snapshot through its completed read. No session discovery,
    authentication changes or model invocations are performed by the adapter.
    """

    project_id: UUID
    account: SourceRef
    pseudonymize: Callable[[str, str], SourceRef] = field(repr=False)
    open_rollout: Callable[[str], BinaryIO] | None = field(default=None, repr=False)
    resume: CodexResume | None = None
    max_bytes: int = 1 << 20
    scope: UsageScope = UsageScope.UNKNOWN

    def __post_init__(self) -> None:
        _validate_byte_limit(self.max_bytes)
        if not isinstance(self.scope, UsageScope):
            raise ValueError("Expected a caller-authorized usage scope")

    def native_turn(
        self, session: str, turn: str, *, surface: str, version: str = _VERSION
    ) -> NativeTurn:
        session = _id(session)
        turn = _id(turn)
        return NativeTurn(
            "codex",
            version,
            surface,
            self.account,
            self.pseudonymize("codex-session", session),
            self.pseudonymize("codex-turn", f"{session}:{turn}"),
        )

    def _lookup(self, session: str) -> bytes:
        if self.open_rollout is None:
            raise _Invalid(CaptureGap.MISSING)
        try:
            with self.open_rollout(session) as evidence:
                payload = _read_evidence(evidence, self.max_bytes)
        except OSError:
            raise _Invalid(CaptureGap.MISSING) from None
        if isinstance(payload, CaptureGap):
            raise _Invalid(payload)
        return payload

    def _check_project(self, enrollment: Enrollment) -> None:
        if enrollment.project_id != self.project_id:
            raise _Invalid(CaptureGap.WRONG_ATTEMPT)

    def _observation(
        self, enrollment: Enrollment, rollout: _Rollout, turn: _Turn, evidence: bytes
    ) -> Observation:
        counts = turn.counts
        if counts is None:
            coverage = Availability.UNKNOWN
        elif turn.outcome is Outcome.COMPLETED and counts.reasoning is not None:
            coverage = Availability.COMPLETE
        else:
            coverage = Availability.PARTIAL
        receipt = UsageReceipt(
            enrollment.project_id,
            enrollment.attempt_id,
            self.native_turn(
                rollout.session,
                turn.identifier,
                surface=rollout.surface,
                version=rollout.version,
            ),
            sha256(evidence[turn.start : turn.end]).hexdigest(),
            turn.ended,
            1,
            coverage,
            turn.outcome,
            TokenCounts() if counts is None else counts.tokens(),
            scope=self.scope,
            schema=UsageReceipt.schema_for(self.scope),
            started_at=turn.started,
            ended_at=turn.ended,
            time_basis=TimeBasis.NATIVE,
        )
        model = next(iter(turn.models)) if len(turn.models) == 1 else None
        return Observation(
            turn.outcome,
            receipt,
            CaptureGap.MISSING if counts is None else None,
            model=model,
            request_usage=turn.requests if model else None,
        )

    def observe(self, event: CaptureEvent) -> Observation:
        outcome = Outcome.UNKNOWN
        try:
            self._check_project(event.enrollment)
            stdout = event.stdout
            if 1 in event.truncated_streams:
                stdout = stdout[: stdout.rfind(b"\n") + 1]
            result = _exec(stdout)
            outcome = result.outcome
            if self.resume is not None and self.resume.session != result.session:
                raise _Invalid(CaptureGap.WRONG_TURN)
            evidence = self._lookup(result.session)
            rollout = _rollout(evidence)
            if rollout.session != result.session:
                raise _Invalid(CaptureGap.WRONG_TURN)
            if rollout.surface != "exec":
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)

            boundary = 0
            if self.resume is not None:
                prefix = self.resume.evidence
                if (
                    not prefix
                    or not prefix.endswith(b"\n")
                    or not evidence.startswith(prefix)
                ):
                    raise _Invalid(CaptureGap.WRONG_TURN)
                boundary = len(prefix)
            turns = [turn for turn in rollout.turns if turn.start >= boundary]
            if not turns:
                raise _Invalid(CaptureGap.MISSING)
            if (
                rollout.active is not None
                or len(turns) != 1
                or any(turn.start < boundary < turn.end for turn in rollout.turns)
            ):
                raise _Invalid(CaptureGap.WRONG_TURN)
            turn = turns[0]
            if result.outcome is not Outcome.UNKNOWN and result.outcome != turn.outcome:
                raise _Invalid()
            if result.counts is not None and result.counts != turn.cumulative:
                raise _Invalid()
            return self._observation(event.enrollment, rollout, turn, evidence)
        except _Invalid as error:
            return Observation(outcome, gap=error.gap)

    def observe_notification(
        self,
        enrollment: Enrollment,
        *,
        expected_turn: NativeTurn,
        notification: bytes,
    ) -> Observation:
        """Consume a configured TUI notify callback for a caller-bound turn."""
        try:
            self._check_project(enrollment)
            if len(notification) > self.max_bytes:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            event = _decode(notification)
            if event.get("type") != "agent-turn-complete":
                raise _Invalid()
            session = _id(event.get("thread-id"))
            turn = _id(event.get("turn-id"))
            if (
                self.native_turn(
                    session, turn, surface="cli", version=expected_turn.version
                )
                != expected_turn
            ):
                raise _Invalid(CaptureGap.WRONG_TURN)
            result = self.recover(
                ExactReference(enrollment, expected_turn, self._lookup(session))
            )
            if result.receipt is not None and result.outcome is not Outcome.COMPLETED:
                raise _Invalid(CaptureGap.WRONG_TURN)
            return result
        except _Invalid as error:
            return Observation(gap=error.gap)

    def recover(self, exact_ref: ExactReference) -> Observation:
        try:
            self._check_project(exact_ref.enrollment)
            wanted = exact_ref.turn
            if wanted.provider != "codex" or wanted.version not in _VERSIONS:
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
            if wanted.account != self.account:
                raise _Invalid(CaptureGap.WRONG_TURN)
            if len(exact_ref.evidence) > self.max_bytes:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            rollout = _rollout(exact_ref.evidence)
            if (wanted.surface, wanted.version) != (rollout.surface, rollout.version):
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
            if wanted.session != self.pseudonymize("codex-session", rollout.session):
                raise _Invalid(CaptureGap.WRONG_TURN)
            for turn in rollout.turns:
                if wanted == self.native_turn(
                    rollout.session,
                    turn.identifier,
                    surface=rollout.surface,
                    version=rollout.version,
                ):
                    return self._observation(
                        exact_ref.enrollment, rollout, turn, exact_ref.evidence
                    )
            if rollout.active is not None and wanted == self.native_turn(
                rollout.session,
                rollout.active,
                surface=rollout.surface,
                version=rollout.version,
            ):
                raise _Invalid(CaptureGap.MISSING)
            raise _Invalid(CaptureGap.WRONG_TURN)
        except _Invalid as error:
            return Observation(gap=error.gap)
