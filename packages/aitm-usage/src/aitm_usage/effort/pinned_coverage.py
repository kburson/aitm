"""Allowlisted, story-scoped coverage at an explicit observation cutoff."""

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID

from ..types import _unique_fields
from .receipts import require_digest, require_item
from .store import EffortError

COVERAGE_SCHEMA = "aitm.story-effort-coverage/v1"
COVERAGE_KIND = "story-effort-coverage"
ADMISSION_SCHEMA = "aitm.story-effort-admission/v1"
MAX_INPUT_BLOB_BYTES = 2 << 20
WINDOW_FIELDS = ("window_start_utc", "window_end_utc", "cutoff_utc")
COVERAGE_STATES = frozenset(
    {
        "observed",
        "pending-binding",
        "pending-evidence",
        "missing",
        "unavailable",
        "withdrawn",
        "disputed",
    }
)
_TIMING_PATH = re.compile(r"attachments/timing/[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\.json")
_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_UTC_STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)"
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def utc_stamp(value: object) -> datetime:
    if type(value) is not str or _UTC_STAMP.fullmatch(value) is None:
        raise EffortError("Expected an exact UTC timestamp")
    try:
        return datetime.fromisoformat(value).astimezone(UTC)
    except ValueError:
        raise EffortError("Expected an exact UTC timestamp") from None


def canonical_window(window: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(window, Mapping) or set(window) != set(WINDOW_FIELDS):
        raise EffortError("Expected a complete UTC reporting window")
    start, end, cutoff = (utc_stamp(window[name]) for name in WINDOW_FIELDS)
    if not start < end <= cutoff:
        raise EffortError("Expected start before end at or before cutoff")
    return {
        name: point.isoformat().removesuffix("+00:00") + "Z"
        for name, point in zip(WINDOW_FIELDS, (start, end, cutoff), strict=True)
    }


def _uuid(value: object) -> UUID:
    if type(value) is not str:
        raise EffortError("Invalid coverage identifier")
    result = UUID(value)
    if str(result) != value:
        raise EffortError("Invalid coverage identifier")
    return result


def _ids(values: object) -> set[UUID]:
    if type(values) is not list:
        raise EffortError("Invalid explicit admission identifiers")
    unique = {_uuid(value) for value in values}
    if len(unique) != len(values):
        raise EffortError("Duplicate explicit admission identifier")
    return unique


def _count(value: object) -> bool:
    return type(value) is int and 0 <= value < 2**63


def _labels(values: object) -> bool:
    return (
        type(values) is list
        and all(type(value) is str and _LABEL.fullmatch(value) for value in values)
        and values == sorted(set(values))
    )


def _timing_joins(joins: object, attempts: set[str]) -> None:
    if type(joins) is not list:
        raise EffortError("Invalid coverage timing joins")
    seen = set()
    for row in joins:
        if type(row) is not dict or set(row) != {
            "attempt",
            "path",
            "sha256",
            "project",
            "observation",
            "clock",
            "waits",
        }:
            raise EffortError("Invalid coverage timing join")
        require_digest(row["attempt"])
        require_digest(row["sha256"])
        require_digest(row["clock"])
        if (
            row["attempt"] not in attempts
            or row["attempt"] in seen
            or type(row["path"]) is not str
            or _TIMING_PATH.fullmatch(row["path"]) is None
            or any(
                type(row[key]) is not str or _LABEL.fullmatch(row[key]) is None
                for key in ("project", "observation")
            )
            or not _labels(row["waits"])
            or row["observation"] in row["waits"]
        ):
            raise EffortError("Invalid coverage timing join")
        seen.add(row["attempt"])
    if [row["attempt"] for row in joins] != sorted(seen):
        raise EffortError("Expected ordered coverage timing joins")


def validate_coverage(data: bytes) -> dict:
    """Verify canonical wire bytes and a complete, privacy-safe status vocabulary."""
    try:
        if type(data) is not bytes or not 0 < len(data) <= MAX_INPUT_BLOB_BYTES:
            raise EffortError("Invalid coverage size")
        row = json.loads(data, object_pairs_hook=_unique_fields)
        keys = {
            "schema",
            "project",
            "story",
            "window",
            "admission",
            "attempts",
            "unattributed",
            "verified_no_work",
            "supersedes",
            "attestation_sha256",
        }
        if type(row) is not dict or keys != row.keys() - {"timing"}:
            raise EffortError("Invalid coverage fields")
        if row["schema"] != COVERAGE_SCHEMA or row["admission"] not in (
            "open",
            "closed",
        ):
            raise EffortError("Invalid coverage schema or admission")
        _uuid(row["project"])
        require_item(row["story"])
        if row["story"] is None or canonical_window(row["window"]) != row["window"]:
            raise EffortError("Invalid coverage story or window")
        if row["unattributed"] is not None and not _count(row["unattributed"]):
            raise EffortError("Invalid coverage unattributed count")
        for key in ("supersedes", "attestation_sha256"):
            if row[key] is not None:
                require_digest(row[key])
        if (
            type(row["verified_no_work"]) is not bool
            or type(row["attempts"]) is not list
        ):
            raise EffortError("Invalid coverage attempt set")
        attempts = []
        for attempt in row["attempts"]:
            if (
                type(attempt) is not dict
                or set(attempt) != {"attempt", "state"}
                or attempt["state"] not in COVERAGE_STATES
            ):
                raise EffortError("Invalid coverage attempt")
            require_digest(attempt["attempt"])
            attempts.append(attempt["attempt"])
        if attempts != sorted(set(attempts)):
            raise EffortError("Invalid duplicate or unordered coverage attempt")
        closed = row["admission"] == "closed"
        if closed and row["attestation_sha256"] is None:
            raise EffortError("Closed coverage requires attested admission")
        if (
            row["verified_no_work"]
            and (not closed or attempts or row["unattributed"] != 0)
            or closed
            and not attempts
            and not row["verified_no_work"]
        ):
            raise EffortError(
                "Closed empty coverage requires verified no-work evidence"
            )
        if "timing" in row:
            _timing_joins(row["timing"], set(attempts))
        if canonical(row) != data:
            raise EffortError("Expected canonical coverage bytes")
        return row
    except (TypeError, ValueError, RecursionError, KeyError):
        raise EffortError("Invalid story effort coverage record") from None


def _admission(
    evidence: dict, store, sessions, story, window, attempts, unresolved
) -> tuple:
    required = {
        "schema",
        "project",
        "story",
        "window",
        "sessions",
        "attempts",
        "missing",
        "unattributed",
        "verified_no_work",
        "source_sha256",
    }
    if type(evidence) is not dict or required != evidence.keys() - {"timing"}:
        raise EffortError("Invalid admission evidence fields")
    evidence_scope = (
        evidence["schema"],
        evidence["project"],
        evidence["story"],
        canonical_window(evidence["window"]),
        _ids(evidence["sessions"]),
    )
    if evidence_scope != (
        ADMISSION_SCHEMA,
        str(store.project_id),
        story,
        window,
        set(sessions),
    ):
        raise EffortError(
            "Admission evidence differs from the selected reporting scope"
        )
    require_digest(evidence["source_sha256"])
    expected = _ids(evidence["attempts"])
    missing = _ids(evidence["missing"])
    if expected != set(attempts) or not missing <= expected:
        raise EffortError(
            "Admission evidence does not reconcile to the enrolled attempt set"
        )
    if any(attempts[item] == "observed" for item in missing):
        raise EffortError("An observed attempt cannot be declared missing")
    unattributed = evidence["unattributed"]
    if unattributed is not None and (
        not _count(unattributed) or unattributed < unresolved
    ):
        raise EffortError("Admission evidence understates unresolved coverage")
    no_work = evidence["verified_no_work"]
    if type(no_work) is not bool or no_work and (attempts or unattributed != 0):
        raise EffortError("Invalid no-work declaration")
    private_timing = evidence.get("timing", [])
    if type(private_timing) is not list:
        raise EffortError("Invalid admission timing joins")
    try:
        timing = [
            item | {"attempt": store.public_attempt(_uuid(item["attempt"]))}
            for item in private_timing
        ]
    except (KeyError, TypeError, ValueError):
        raise EffortError("Invalid admission timing joins") from None
    timing.sort(key=lambda row: row["attempt"])
    return (
        missing,
        unattributed,
        no_work,
        timing,
        sha256(canonical(evidence)).hexdigest(),
    )


def export_coverage(
    store,
    sessions: Sequence[UUID],
    story: int,
    window: Mapping[str, str],
    admission: str,
    evidence: dict | None = None,
    supersedes: str | None = None,
) -> bytes:
    """Freeze one scoped store snapshot; attestation is provided by its owner."""
    window = canonical_window(window)
    if (
        admission not in ("open", "closed")
        or admission == "closed"
        and evidence is None
    ):
        raise EffortError("Closed admission requires explicit admission evidence")
    attempts, unresolved = store.coverage_snapshot(sessions, story, window)
    missing = set()
    unattributed = unresolved or None
    no_work = False
    timing = []
    attestation = None
    if evidence is not None:
        missing, unattributed, no_work, timing, attestation = _admission(
            evidence,
            store,
            sessions,
            story,
            window,
            attempts,
            unresolved,
        )
    if admission == "closed" and not attempts and not no_work:
        raise EffortError("Closed empty coverage requires verified no-work evidence")
    if admission == "open" and no_work:
        raise EffortError("A verified no-work declaration requires closed admission")
    rows = sorted(
        (
            {
                "attempt": store.public_attempt(key),
                "state": "missing"
                if key in missing and state.startswith("pending-")
                else state,
            }
            for key, state in attempts.items()
        ),
        key=lambda row: row["attempt"],
    )
    value = {
        "schema": COVERAGE_SCHEMA,
        "project": str(store.project_id),
        "story": story,
        "window": window,
        "admission": admission,
        "attempts": rows,
        "unattributed": unattributed,
        "verified_no_work": no_work,
        "supersedes": supersedes,
        "attestation_sha256": attestation,
    }
    if timing:
        value["timing"] = timing
    data = canonical(value)
    validate_coverage(data)
    return data
