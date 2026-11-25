"""Portable, closed wire types for evidence already verified by the caller."""

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import cast
from uuid import UUID

from ..types import (
    Availability,
    SourceRef,
    TokenCounts,
    _unique_fields,
    _wire,
)


class Role(StrEnum):
    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"


class Outcome(StrEnum):
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"
    UNKNOWN = "unknown"


class UsageScope(StrEnum):
    BOUNDED = "bounded"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TimeBasis(StrEnum):
    NATIVE = "native"
    CALLER = "caller"
    UNKNOWN = "unknown"


def require_digest(value: str) -> None:
    if not isinstance(value, str) or not re.fullmatch("[a-f0-9]{64}", value):
        raise ValueError("Expected a SHA-256 digest")


def require_item(value: int | None) -> None:
    if value is not None and (type(value) is not int or value < 1):
        raise ValueError("Expected a positive backlog item number")


@dataclass(frozen=True, slots=True)
class ReviewBinding:
    review: SourceRef
    round: int

    def __post_init__(self) -> None:
        require_item(self.round)
        if self.round is None:
            raise ValueError("Expected a review round")


@dataclass(frozen=True, slots=True)
class Enrollment:
    project_id: UUID
    run_id: UUID
    attempt_id: UUID
    role: Role
    story: int | None = None
    epic: int | None = None
    parent_attempt_id: UUID | None = None
    review: ReviewBinding | None = None

    def __post_init__(self) -> None:
        require_item(self.story)
        require_item(self.epic)
        if self.parent_attempt_id == self.attempt_id:
            raise ValueError("An attempt cannot be its own parent")
        if self.review is not None and self.role != Role.REVIEWER:
            raise ValueError("Only reviewer attempts carry review bindings")


@dataclass(frozen=True, slots=True)
class NativeTurn:
    provider: str
    version: str
    surface: str
    account: SourceRef
    session: SourceRef
    turn: SourceRef

    def __post_init__(self) -> None:
        for value in (self.provider, self.version, self.surface):
            if not isinstance(value, str) or not re.fullmatch(
                r"[a-zA-Z0-9][a-zA-Z0-9._+-]{0,95}", value
            ):
                raise ValueError("Invalid harness metadata")

    @property
    def identity(self) -> str:
        # A headless stream and an exact later lookup can observe the same turn.
        fields = (
            self.provider,
            self.account.value,
            self.session.value,
            self.turn.value,
        )
        return sha256(json.dumps(fields, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class UsageReceipt:
    project_id: UUID
    attempt_id: UUID
    turn: NativeTurn
    source_sha256: str
    observed_at: datetime
    revision: int
    coverage: Availability
    outcome: Outcome
    tokens: TokenCounts
    scope: UsageScope = UsageScope.UNKNOWN
    previous_digest: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    time_basis: TimeBasis = TimeBasis.UNKNOWN
    schema: str = "aitm.effort.receipt/v1"
    grok_cost_usd_ticks: int | None = None
    grok_cache_creation_tokens: int | None = None

    def __post_init__(self) -> None:
        grok = (self.grok_cost_usd_ticks, self.grok_cache_creation_tokens)
        if self.schema == "aitm.effort.receipt/v2":
            if self.turn.provider != "grok" or any(
                type(count) is not int or not 0 <= count < 2**63 for count in grok
            ):
                raise ValueError("Expected native Grok usage fields")
        elif self.schema != "aitm.effort.receipt/v1" or any(
            v is not None for v in grok
        ):
            raise ValueError("Unsupported receipt schema")
        require_digest(self.source_sha256)
        if type(self.revision) is not int or not 1 <= self.revision < 2**63:
            raise ValueError("Expected a positive receipt revision")
        if (self.revision == 1) != (self.previous_digest is None):
            raise ValueError("Revised receipts require a predecessor digest")
        if self.previous_digest is not None:
            require_digest(self.previous_digest)
        moments = (self.observed_at, self.started_at, self.ended_at)
        if self.observed_at is None or any(
            moment is not None and moment.utcoffset() is None for moment in moments
        ):
            raise ValueError("Expected timezone-aware receipt times")
        for name in ("observed_at", "started_at", "ended_at"):
            moment = getattr(self, name)
            if moment is not None:
                object.__setattr__(self, name, moment.astimezone(UTC))
        if self.time_basis == TimeBasis.UNKNOWN and any(moments[1:]):
            raise ValueError("Interval times require a known basis")
        if self.started_at and self.ended_at and self.ended_at < self.started_at:
            raise ValueError("Receipt end precedes start")

    @property
    def observation_id(self) -> str:
        return self.turn.identity

    def to_json(self) -> str:
        payload = _wire(self, UsageReceipt, decode=False, validate_ref=None)
        if self.schema == "aitm.effort.receipt/v1":
            del payload["grok_cost_usd_ticks"], payload["grok_cache_creation_tokens"]
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, value: str | bytes) -> "UsageReceipt":
        try:
            payload = json.loads(value, object_pairs_hook=_unique_fields)
            if (
                isinstance(payload, dict)
                and payload.get("schema") == "aitm.effort.receipt/v1"
            ):
                for name in ("grok_cost_usd_ticks", "grok_cache_creation_tokens"):
                    if name in payload:
                        raise ValueError("Unexpected native field in v1 receipt")
                    payload[name] = None
            return cast(
                UsageReceipt, _wire(payload, cls, decode=True, validate_ref=None)
            )
        except (RecursionError, TypeError, ValueError):
            raise ValueError("Invalid allowlisted usage envelope") from None

    @property
    def digest(self) -> str:
        return sha256(self.to_json().encode()).hexdigest()
