"""The v1 event envelope and its lossless wire representation."""

import json
import math
import re
from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal, Never

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    PrivateAttr,
    ValidationError,
)

EVENT_TYPE_PATTERN = r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$"
DIGEST = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
UTC_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)"
)


class EnvelopeError(ValueError):
    """The supplied bytes do not form one supported event envelope."""


class EventActor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    kind: Literal["agent", "human", "tool"]
    harness: str | None = None
    session: str | None = None
    on_behalf_of: str | None = None


class BackfillRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    recorded_at: str
    by: EventActor
    source: Annotated[str, Field(min_length=1)]
    source_digest: DIGEST


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    v: Literal[1]
    id: Annotated[str, Field(min_length=1)]
    ts: str
    type: Annotated[str, Field(pattern=EVENT_TYPE_PATTERN)]
    story: Annotated[int, Field(gt=0)]
    actor: EventActor
    operation_id: Annotated[str, Field(min_length=1)]
    sequence: Annotated[int, Field(gt=0)]
    prior_log_digest: DIGEST
    data: dict[str, JsonValue]
    policy_digest: DIGEST | None = None
    read_set_digest: DIGEST | None = None
    recorded_at: str | None = None
    backfill: BackfillRecord | None = None
    _raw: bytes = PrivateAttr(default=b"")

    @property
    def namespace(self) -> str:
        return self.type.split(".", 1)[0]

    @property
    def raw_record(self) -> bytes:
        return self._raw


def _object(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise EnvelopeError(f"duplicate event key: {key}")
        result[key] = value
    return result


def _nonfinite_number(value: str) -> Never:
    raise EnvelopeError(f"nonfinite event number: {value}")


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        _nonfinite_number(value)
    return parsed


def _check_timestamp(value: str) -> None:
    if not UTC_TIMESTAMP.fullmatch(value):
        raise EnvelopeError("event timestamps require an explicit UTC date and time")
    try:
        datetime.fromisoformat(value)
    except ValueError as error:
        raise EnvelopeError("invalid event timestamp") from error


def validate_envelope(raw: bytes) -> EventEnvelope:
    """Validate one UTF-8 JSON record and retain its original bytes."""

    line = raw.removesuffix(b"\n")
    if b"\n" in line or b"\r" in line:
        raise EnvelopeError("expected one LF-delimited event record")
    try:
        decoded = json.loads(
            line.decode("utf-8"),
            object_pairs_hook=_object,
            parse_constant=_nonfinite_number,
            parse_float=_finite_float,
        )
        if not isinstance(decoded, dict) or type(decoded.get("v")) is not int:
            raise EnvelopeError("event requires an integer envelope version")
        event = EventEnvelope.model_validate(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as error:
        raise EnvelopeError("invalid event envelope") from error
    _check_timestamp(event.ts)
    if event.recorded_at is not None:
        _check_timestamp(event.recorded_at)
    if event.backfill is not None:
        _check_timestamp(event.backfill.recorded_at)
        path = PurePosixPath(event.backfill.source)
        if path.is_absolute() or not path.parts or ".." in path.parts:
            raise EnvelopeError(
                "backfill source requires a repository-relative file path"
            )
    event._raw = raw
    return event
