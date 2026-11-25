"""Grok Build usage from a bounded native run and its authorized retained view."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import BinaryIO
from uuid import UUID

from ...monitor_types import GrokTokenCounts
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

_VERSION = "1.0.92"
_SURFACE = "usage"


class _Invalid(ValueError):
    def __init__(self, gap: CaptureGap = CaptureGap.MALFORMED) -> None:
        self.gap = gap


def _object(value: object) -> dict:
    if not isinstance(value, dict):
        raise _Invalid()
    return value


def _decode(raw: bytes) -> dict:
    return _object(json.loads(raw, object_pairs_hook=_unique_fields))


def _uuid(value: object) -> str:
    if not isinstance(value, str) or len(value) != 36 or str(UUID(value)) != value:
        raise _Invalid()
    return value


def _count(value: object) -> int:
    if type(value) is not int or not 0 <= value < 2**63:
        raise _Invalid()
    return value


def _turn_number(value: object) -> int:
    ordinal = _count(value)
    if ordinal == 0:
        raise _Invalid()
    return ordinal


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise _Invalid()
    time = datetime.fromisoformat(value)
    if time.utcoffset() is None:
        raise _Invalid()
    return time.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class _Usage:
    tokens: GrokTokenCounts
    ticks: int
    breakdown: tuple[tuple[str, int, int, int, int, int], ...]

    @classmethod
    def decode(cls, row: dict, *, stored: bool) -> "_Usage":
        models = _object(row.get("modelUsage"))
        if not models or any(
            not isinstance(model, str) or not 0 < len(model) <= 128 for model in models
        ):
            raise _Invalid()
        breakdown = []
        read_key = "cachedReadTokens" if stored else "cacheReadInputTokens"
        creation_key = "cacheCreationTokens" if stored else "cacheCreationInputTokens"
        for model, value in sorted(models.items()):
            detail = _object(value)
            gross = _count(detail.get("inputTokens"))
            read = _count(detail.get(read_key))
            created = _count(detail.get(creation_key))
            uncached = _count(gross - read - created) if stored else gross
            output = _count(detail.get("outputTokens"))
            if stored:
                GrokTokenCounts(
                    uncached,
                    read,
                    created,
                    output,
                    _count(detail.get("reasoningTokens")),
                    _count(detail.get("totalTokens")),
                )
            calls = _count(detail.get("modelCalls"))
            if calls == 0:
                raise _Invalid()
            breakdown.append((model, uncached, read, created, output, calls))
        calls = sum(model[-1] for model in breakdown)
        if stored:
            gross = _count(row.get("inputTokens"))
            cached = _count(row.get("cachedReadTokens"))
            created = _count(row.get("cacheCreationTokens"))
            primary = row.get("primaryModelId")
            if (
                calls != _count(row.get("modelCalls"))
                or not isinstance(primary, str)
                or primary not in models
            ):
                raise _Invalid()
            usage = GrokTokenCounts(
                gross - cached - created,
                cached,
                created,
                _count(row.get("outputTokens")),
                _count(row.get("reasoningTokens")),
                _count(row.get("totalTokens")),
            )
            ticks = _count(row.get("costUsdTicks"))
            for field in (
                "inputTokens",
                "cachedReadTokens",
                "cacheCreationTokens",
                "outputTokens",
                "reasoningTokens",
                "totalTokens",
                "costUsdTicks",
            ):
                if (
                    sum(_count(detail.get(field)) for detail in models.values())
                    != row[field]
                ):
                    raise _Invalid()
        else:
            wire = _object(row.get("usage"))
            usage = GrokTokenCounts(
                _count(wire.get("input_tokens")),
                _count(wire.get("cache_read_input_tokens")),
                _count(wire.get("cache_creation_input_tokens")),
                _count(wire.get("output_tokens")),
                _count(wire.get("reasoning_tokens")),
                _count(wire.get("total_tokens")),
            )
            totals = (
                usage.uncached_input_tokens,
                usage.cache_read_tokens,
                usage.cache_creation_tokens,
                usage.output_tokens,
            )
            fields = (
                "inputTokens",
                "cacheReadInputTokens",
                "cacheCreationInputTokens",
                "outputTokens",
            )
            if (
                tuple(
                    sum(_count(detail.get(name)) for detail in models.values())
                    for name in fields
                )
                != totals
            ):
                raise _Invalid()
            ticks = _count(row.get("total_cost_usd_ticks"))
        return cls(usage, ticks, tuple(breakdown))


@dataclass(frozen=True, slots=True)
class _StoredTurn:
    number: int
    ended: datetime
    usage: _Usage
    digest: str


def _retained(raw: bytes, session: str) -> dict[int, _StoredTurn]:
    document = _decode(raw)
    if document.get("sessionId") != session:
        raise _Invalid(CaptureGap.WRONG_TURN)
    rows = document.get("turns")
    if not isinstance(rows, list):
        raise _Invalid()
    turns = {}
    for item in rows:
        row = _object(item)
        number = _turn_number(row.get("turnNumber"))
        if number in turns or _count(row.get("turnCount")) != 1:
            raise _Invalid(CaptureGap.WRONG_TURN)
        encoded = json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
        turns[number] = _StoredTurn(
            number,
            _instant(row.get("endedAt")),
            _Usage.decode(row, stored=True),
            sha256(encoded).hexdigest(),
        )
    return turns


def _end(stdout: bytes, session: str) -> dict:
    terminal = None
    for line in stdout.splitlines(keepends=True):
        if not line.endswith(b"\n") or terminal is not None:
            raise _Invalid()
        row = _decode(line)
        if row.get("type") == "end":
            if row.get("sessionId") != session:
                raise _Invalid(CaptureGap.WRONG_TURN)
            if not (
                row.get("stopReason") == "cancelled" and row.get("requestId") == ""
            ):
                _uuid(row.get("requestId"))
            terminal = row
    if terminal is None:
        raise _Invalid(CaptureGap.MISSING)
    return terminal


@dataclass(frozen=True, slots=True)
class GrokAdapter:
    """Use the caller-authorized exact output of Grok Build's usage command.

    The caller verifies the installed version, owns the enrolled session and
    supplies its exclusive baseline before a resume. A fresh capture must use
    a new explicit session. For interactive work the caller arms the returned
    native ordinal before recovery. The adapter never starts or discovers sessions.
    """

    enrollment: Enrollment
    account: SourceRef
    pseudonymize: Callable[[str, str], SourceRef] = field(repr=False)
    session: str = field(repr=False)
    harness_version: str
    open_usage: Callable[[str], BinaryIO] | None = field(default=None, repr=False)
    baseline: bytes | None = field(default=None, repr=False)
    max_bytes: int = 1 << 20
    scope: UsageScope = UsageScope.UNKNOWN

    def __post_init__(self) -> None:
        _uuid(self.session)
        _validate_byte_limit(self.max_bytes)
        if not isinstance(self.scope, UsageScope):
            raise ValueError("Expected a caller-authorized usage scope")

    def native_turn(self, number: int) -> NativeTurn:
        return NativeTurn(
            "grok",
            _VERSION,
            _SURFACE,
            self.account,
            self.pseudonymize("grok-session", self.session),
            self.pseudonymize("grok-turn", f"{self.session}:{_turn_number(number)}"),
        )

    def _check(self, enrollment: Enrollment) -> None:
        if enrollment != self.enrollment:
            raise _Invalid(CaptureGap.WRONG_ATTEMPT)
        if self.harness_version != _VERSION:
            raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)

    def _read(self, raw: bytes) -> dict[int, _StoredTurn]:
        if len(raw) > self.max_bytes:
            raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
        if not raw:
            raise _Invalid(CaptureGap.MISSING)
        return _retained(raw, self.session)

    def _lookup(self) -> dict[int, _StoredTurn]:
        if self.open_usage is None:
            raise _Invalid(CaptureGap.MISSING)
        try:
            with self.open_usage(self.session) as stream:
                evidence = _read_evidence(stream, self.max_bytes)
        except OSError:
            raise _Invalid(CaptureGap.MISSING) from None
        if isinstance(evidence, CaptureGap):
            raise _Invalid(evidence)
        return self._read(evidence)

    def _receipt(self, turn: _StoredTurn) -> Observation:
        tokens = turn.usage.tokens
        normalized = TokenCounts(
            input_tokens=tokens.uncached_input_tokens
            + tokens.cache_read_tokens
            + tokens.cache_creation_tokens,
            cached_input_tokens=tokens.cache_read_tokens,
            output_tokens=tokens.output_tokens,
            reasoning_output_tokens=tokens.reasoning_output_tokens,
            total_tokens=tokens.total_tokens,
        )
        return Observation(
            Outcome.COMPLETED,
            UsageReceipt(
                self.enrollment.project_id,
                self.enrollment.attempt_id,
                self.native_turn(turn.number),
                turn.digest,
                turn.ended,
                1,
                Availability.COMPLETE,
                Outcome.COMPLETED,
                normalized,
                scope=self.scope,
                ended_at=turn.ended,
                time_basis=TimeBasis.NATIVE,
                schema="aitm.effort.receipt/v2",
                grok_cost_usd_ticks=turn.usage.ticks,
                grok_cache_creation_tokens=tokens.cache_creation_tokens,
            ),
        )

    def observe(self, event: CaptureEvent) -> Observation:
        outcome = Outcome.UNKNOWN
        try:
            self._check(event.enrollment)
            if len(event.stdout) > self.max_bytes or 1 in event.truncated_streams:
                raise _Invalid(CaptureGap.EVIDENCE_LIMIT)
            terminal = _end(event.stdout, self.session)
            incomplete = terminal.get("usage_is_incomplete", False)
            if type(incomplete) is not bool:
                raise _Invalid()
            if terminal.get("stopReason") == "cancelled":
                return Observation(Outcome.INTERRUPTED, gap=CaptureGap.MISSING)
            if terminal.get("stopReason") != "end_turn":
                raise _Invalid()
            outcome = Outcome.COMPLETED
            if incomplete:
                raise _Invalid(CaptureGap.MISSING)
            if _count(terminal.get("num_turns")) != 1:
                raise _Invalid()
            usage = _Usage.decode(terminal, stored=False)
            before = {} if self.baseline is None else self._read(self.baseline)
            after = self._lookup()
            added = after.keys() - before.keys()
            if (
                any(after.get(number) != row for number, row in before.items())
                or len(added) > 1
            ):
                raise _Invalid(CaptureGap.WRONG_TURN)
            if not added:
                raise _Invalid(CaptureGap.MISSING)
            (number,) = added
            row = after[number]
            if row.usage != usage:
                raise _Invalid()
            return self._receipt(row)
        except _Invalid as error:
            return Observation(outcome, gap=error.gap)
        except (ValueError, OverflowError, RecursionError):
            return Observation(outcome, gap=CaptureGap.MALFORMED)

    def recover(self, exact_ref: ExactReference) -> Observation:
        try:
            self._check(exact_ref.enrollment)
            expected = exact_ref.turn
            if (expected.provider, expected.version, expected.surface) != (
                "grok",
                _VERSION,
                _SURFACE,
            ):
                raise _Invalid(CaptureGap.UNEXPECTED_HARNESS)
            for turn in self._read(exact_ref.evidence).values():
                if self.native_turn(turn.number) == expected:
                    return self._receipt(turn)
            raise _Invalid(CaptureGap.WRONG_TURN)
        except _Invalid as error:
            return Observation(gap=error.gap)
        except (ValueError, OverflowError, RecursionError):
            return Observation(gap=CaptureGap.MALFORMED)
