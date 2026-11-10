"""Read immutable story evidence and validate prospective planning registrations."""

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

MAX_BLOB = 2 * 1024 * 1024
TIMING_SCHEMA = "aitm.story-timing-receipt/v1"
USAGE_SCHEMA = "aitm.story-usage-receipt/v1"
SCHEMAS = {"story-timing-receipt": TIMING_SCHEMA, "story-usage-receipt": USAGE_SCHEMA}
LEGACY_PATH = "attachments/2026-11-10-actual-backfill.json"
LEGACY_SHA256 = "8d619b606cfd0142c46da7402ee52c20b95d3a78725894c12cc385309342b139"
COVERAGES = {"complete", "partial", "unknown"}
KINDS = {
    "agent-turn",
    "tool",
    "owner-wait",
    "idle",
    "owner-request",
    "owner-response",
    "workflow-start",
    "workflow-delivered",
    "pending-wait",
    "missing",
}
STATES = {
    "backlog",
    "refine",
    "ready-for-plan",
    "plan",
    "develop",
    "test",
    "review",
    "rework",
    "retro",
    "done",
    "blocked",
    "on-hold",
    "cancelled",
    "draft",
    "ready-for-dev",
}
SHA1 = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
BATCH = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}")
UTC_STAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)"
)
ROOT = re.compile(r"\.aitm/stories/([0-9]{3,})/([1-9][0-9]{0,11})/(.+)")
RECEIPT_PATH = re.compile(
    r"attachments/timing/([A-Za-z0-9][A-Za-z0-9_-]{0,95})-([1-9][0-9]{0,11})\.json"
)


@dataclass(frozen=True)
class Gap:
    story: int
    code: str
    source: str


@dataclass(frozen=True)
class Story:
    id: int
    title: str
    state: str | None
    state_source: str | None
    path: str


@dataclass(frozen=True)
class Estimate:
    agent_hours: Decimal | None
    size: str | None
    phase: str | None
    roles: tuple[str, ...] | None
    source: str


@dataclass(frozen=True)
class Event:
    story: int
    kind: str
    timestamp: datetime
    data: dict[str, Any]
    source: str
    recorded_at: datetime
    actor: dict[str, Any] | None


@dataclass(frozen=True)
class Registration:
    story: int
    project: str
    kind: str
    path: str
    sha256: str
    batch: str
    source: str
    recorded_at: datetime

    @property
    def identity(self):
        return self.project, self.kind, self.sha256


@dataclass(frozen=True)
class Receipt:
    registration: Registration
    schema: str
    recorded_at: datetime
    source: dict[str, str]
    observations: tuple[dict[str, Any], ...] = ()
    selector: dict[str, Any] | None = None
    usage: dict[str, Any] | None = None
    coverage: str | None = None
    verification: dict[str, Any] | None = None
    supersedes: str | None = None

    @property
    def batch(self):
        return self.registration.batch


@dataclass(frozen=True)
class PlanningTree:
    commit: str
    commit_time: datetime
    as_of: datetime
    stories: dict[int, Story]
    events: tuple[Event, ...]
    estimates: dict[int, Estimate]
    parents: dict[int, int]
    descendants: dict[int, tuple[int, ...]]
    registrations: tuple[Registration, ...]
    receipts: tuple[Receipt, ...]
    legacy_seed: bytes | None
    gaps: tuple[Gap, ...]
    _claims: dict[tuple[int, str], tuple[Registration, ...]]
    _blobs: dict[str, "_Blob"]


def _check(condition, reason):
    if not condition:
        raise ValueError(reason)


def _pattern(value, expression):
    return isinstance(value, str) and expression.fullmatch(value) is not None


def _number(value):
    return type(value) is int and value > 0


def _stamp(value):
    _check(_pattern(value, UTC_STAMP), "expected a UTC timestamp")
    return datetime.fromisoformat(value).astimezone(UTC)


def _object(pairs):
    result = {}
    for key, value in pairs:
        _check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(_):
    raise ValueError("non-finite JSON number")


def _json(raw, **options):
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_object,
        parse_constant=_nonfinite,
        **options,
    )


def _fields(obj, required, optional=()):
    _check(
        isinstance(obj, dict)
        and set(required) <= obj.keys() <= set(required) | set(optional),
        "missing or unsupported fields",
    )


def _source(obj):
    _fields(obj, (), ("ref", "sha256"))
    _check(obj, "missing source evidence")
    if "ref" in obj:
        _check(_pattern(obj["ref"], TOKEN), "unsafe source reference")
    if "sha256" in obj:
        _check(_pattern(obj["sha256"], SHA256), "invalid source digest")


def _coverage(value):
    _check(isinstance(value, str) and value in COVERAGES, "invalid coverage")


def _timing(row, recorded):
    _fields(
        row,
        (
            "observation_id",
            "actor",
            "phase",
            "role",
            "kind",
            "coverage",
            "basis",
            "start_utc",
            "end_utc",
        ),
        ("turn", "attempt", "source", "missing_reason", "recorded_at_utc"),
    )
    for key in ("observation_id", "actor", "basis"):
        _check(_pattern(row[key], TOKEN), "invalid observation identity or basis")
    for key in ("phase", "role", "turn", "attempt", "missing_reason"):
        _check(
            row.get(key) is None or _pattern(row[key], TOKEN),
            "invalid observation scope",
        )
    _check(
        isinstance(row["kind"], str) and row["kind"] in KINDS,
        "invalid observation kind",
    )
    _coverage(row["coverage"])
    if "source" in row:
        _source(row["source"])
    row_time = _stamp(row["recorded_at_utc"]) if "recorded_at_utc" in row else recorded
    start, end = tuple(
        _stamp(row[key]) if row[key] is not None else None
        for key in ("start_utc", "end_utc")
    )
    _check(
        all(bound is None or bound.microsecond % 1000 == 0 for bound in (start, end)),
        "expected millisecond occurrence precision",
    )
    _check(start is None or end is None or start < end, "reversed or empty interval")
    if start is None or end is None:
        boundary = row["kind"] in {
            "owner-request",
            "owner-response",
            "workflow-start",
            "workflow-delivered",
        }
        if not (boundary and ((start is None) != (end is None))):
            _check(
                row["coverage"] != "complete" and row.get("missing_reason"),
                "missing boundary reason",
            )
    return row_time, start, end


def _selector(obj, project):
    _fields(
        obj,
        (
            "project",
            "report_id",
            "window_start_utc",
            "window_end_utc",
            "cutoff_utc",
            "rate_card",
            "pricing_basis",
        ),
    )
    _check(obj["project"] == project, "selector project mismatch")
    for key in ("report_id", "rate_card", "pricing_basis"):
        _check(_pattern(obj[key], TOKEN), "invalid report identity or pricing basis")
    start, end, cutoff = (
        _stamp(obj[key]) for key in ("window_start_utc", "window_end_utc", "cutoff_utc")
    )
    _check(start < end <= cutoff, "invalid report window")
    return cutoff


def _usage(obj, registration):
    direct = obj["usage"]
    _fields(direct, ("tokens", "priced_usd"))
    _check(
        isinstance(direct["tokens"], dict)
        and all(
            _pattern(key, TOKEN) and type(value) is int and value >= 0
            for key, value in direct["tokens"].items()
        ),
        "invalid token quantities",
    )
    price = direct["priced_usd"]
    _check(
        price is None
        or _pattern(price, re.compile(r"(?:0|[1-9][0-9]{0,19})(?:\.[0-9]{1,18})?")),
        "invalid decimal USD",
    )
    _coverage(obj["coverage"])
    cutoff = _selector(obj["selector"], registration.project)
    record = obj.get("verification")
    if record is not None:
        _fields(
            record,
            (
                "operator_ref",
                "verified_at_utc",
                "source_report_id",
                "source_sha256",
                "verified_story",
                "selector",
                "pricing_basis",
                "coverage",
                "sanitized_data_sha256",
            ),
        )
        _check(_pattern(record["operator_ref"], TOKEN), "invalid operator reference")
        _check(
            _pattern(record["source_sha256"], SHA256)
            and record["source_sha256"]
            == obj["source"].get("sha256", record["source_sha256"]),
            "verification source digest mismatch",
        )
        _check(
            type(record["verified_story"]) is int
            and record["verified_story"] == registration.story
            and record["selector"] == obj["selector"]
            and record["source_report_id"] == obj["selector"]["report_id"]
            and record["pricing_basis"] == obj["selector"]["pricing_basis"]
            and record["coverage"] == obj["coverage"],
            "verification scope mismatch",
        )
        encoded = json.dumps(
            direct, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        _check(
            record["sanitized_data_sha256"] == hashlib.sha256(encoded).hexdigest(),
            "sanitized usage digest mismatch",
        )
        verified = _stamp(record["verified_at_utc"])
        _check(verified >= cutoff, "verification precedes report cutoff")
        return verified
    return cutoff


def _registration(event):
    obj = event.data
    _check(
        event.kind == "core.evidence.recorded", "expected a core evidence registration"
    )
    _fields(obj, ("kind", "path", "sha256", "scope"))
    kind = obj["kind"]
    _check(isinstance(kind, str) and kind in SCHEMAS, "unsupported registration kind")
    match = (
        RECEIPT_PATH.fullmatch(obj["path"]) if isinstance(obj["path"], str) else None
    )
    _check(match and int(match[2]) == event.story, "noncanonical receipt path")
    _check(_pattern(obj["sha256"], SHA256), "invalid receipt digest")
    _fields(obj["scope"], ("story", "project"))
    story = obj["scope"]["story"]
    project = obj["scope"]["project"]
    _check(
        type(story) is int and story == event.story and _pattern(project, TOKEN),
        "registration scope mismatch",
    )
    return Registration(
        story,
        project,
        kind,
        obj["path"],
        obj["sha256"],
        match[1],
        event.source,
        event.recorded_at,
    )


class _FutureReceipt(ValueError):
    pass


def validate_receipt(
    raw: bytes, registration: Registration, *, as_of: datetime | None = None
) -> Receipt:
    """Validate the registered exact bytes; leave time aggregation and Cost assurance to projectors."""
    path = (
        RECEIPT_PATH.fullmatch(registration.path)
        if isinstance(registration.path, str)
        else None
    )
    _check(
        path
        and _number(registration.story)
        and int(path[2]) == registration.story
        and path[1] == registration.batch
        and _pattern(registration.project, TOKEN),
        "noncanonical receipt path or scope",
    )
    _check(len(raw) <= MAX_BLOB, "receipt exceeds byte limit")
    _check(
        hashlib.sha256(raw).hexdigest() == registration.sha256,
        "receipt digest mismatch",
    )
    obj = _json(raw)
    _check(
        isinstance(obj, dict)
        and obj.get("schema") == SCHEMAS.get(registration.kind)
        and registration.kind in SCHEMAS,
        "unsupported or mismatched schema",
    )
    base = ("schema", "project", "subject", "batch", "recorded_at_utc", "source")
    timing = obj["schema"] == TIMING_SCHEMA
    _fields(
        obj,
        base + (("observations",) if timing else ("selector", "usage", "coverage")),
        ("supersedes",) if timing else ("verification", "supersedes"),
    )
    _check(
        obj["project"] == registration.project
        and type(obj["subject"]) is int
        and obj["subject"] == registration.story
        and obj["batch"] == registration.batch,
        "receipt scope mismatch",
    )
    _check(_pattern(obj["batch"], BATCH), "invalid batch identity")
    _source(obj["source"])
    recorded = _stamp(obj["recorded_at_utc"])
    supersedes = obj.get("supersedes")
    _check(
        supersedes is None or _pattern(supersedes, SHA256),
        "invalid superseded receipt digest",
    )
    observations = obj.get("observations", [])
    _check(
        isinstance(observations, list) and (not timing or observations),
        "missing observations",
    )
    if timing:
        latest = max(
            [
                recorded,
                *(
                    bound
                    for row in observations
                    for bound in _timing(row, recorded)
                    if bound is not None
                ),
            ]
        )
    else:
        latest = max(recorded, _usage(obj, registration))
    if as_of is not None and latest > as_of:
        raise _FutureReceipt("receipt includes facts beyond the as-of cutoff")
    _check(
        latest <= recorded <= registration.recorded_at,
        "receipt chronology exceeds recording or registration",
    )
    return Receipt(
        registration,
        obj["schema"],
        recorded,
        obj["source"],
        tuple(observations),
        obj.get("selector"),
        obj.get("usage"),
        obj.get("coverage"),
        obj.get("verification"),
        supersedes,
    )


@dataclass(frozen=True)
class _Blob:
    mode: str
    oid: str
    size: int | None


class _Git:
    def __init__(self, repo):
        self.repo = repo.resolve(strict=True)
        self.env = {
            key: val for key, val in os.environ.items() if not key.startswith("GIT_")
        }
        self.env.update(
            GIT_NO_LAZY_FETCH="1",
            GIT_NO_REPLACE_OBJECTS="1",
            GIT_OPTIONAL_LOCKS="0",
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_ALLOW_PROTOCOL="",
        )
        config = (
            self.run("config", "--null", "--name-only", "--list").lower().split(b"\0")
        )
        objects = Path(
            os.fsdecode(
                self.run(
                    "rev-parse", "--path-format=absolute", "--git-path", "objects"
                ).rstrip(b"\n")
            )
        )
        _check(
            not any(
                key in {b"extensions.partialclone", b"extensions.partialclonefilter"}
                or (
                    key.startswith(b"remote.")
                    and key.endswith((b".promisor", b".partialclonefilter"))
                )
                for key in config
            )
            and not any((objects / "pack").glob("*.promisor"))
            and not (objects / "info" / "alternates").exists(),
            "partial or promisor repositories and alternate object stores are unsupported",
        )

    def run(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            env=self.env,
            capture_output=True,
            check=False,
        )
        _check(
            result.returncode == 0,
            f"Git could not read {args[0]} from the supplied repository",
        )
        return result.stdout

    def tree(self, pin):
        result = {}
        for entry in self.run(
            "ls-tree", "-r", "-l", "-z", pin, "--", ".aitm/stories"
        ).split(b"\0"):
            if not entry:
                continue
            meta, _, path = entry.partition(b"\t")
            try:
                path = path.decode("utf-8")
            except UnicodeDecodeError:
                continue
            mode, _, oid, size = meta.decode("ascii").split()
            result[path] = _Blob(mode, oid, None if size == "-" else int(size))
        return result

    def read(self, blob):
        _check(
            blob.mode in {"100644", "100755"}
            and blob.size is not None
            and blob.size <= MAX_BLOB,
            "expected a bounded regular Git blob",
        )
        return self.run("cat-file", "blob", blob.oid)


def _root(story):
    return f".aitm/stories/{story // 100:03d}/{story}/"


def _header(raw):
    text = raw.decode("utf-8")
    rows = text.splitlines()
    _check(rows and rows[0] == "---" and "---" in rows[1:], "missing story frontmatter")
    header = {}
    for line in rows[1 : rows.index("---", 1)]:
        key, sep, value = line.partition(":")
        if sep and key in {
            "id",
            "title",
            "state",
            "parent",
            "children",
            "estimate",
            "updated",
            "created",
        }:
            _check(key not in header, "duplicate frontmatter key")
            header[key] = value.strip()
    return header


def _header_value(header, key):
    value = header.get(key, "null")
    if (
        value.startswith(('"', "[", "{"))
        or value == "null"
        or re.fullmatch(r"[0-9]+", value)
    ):
        return _json(value.encode(), parse_float=Decimal)
    return value


def _header_estimate(value):
    try:
        return _header_value({"estimate": value}, "estimate")
    except json.JSONDecodeError:
        match = re.fullmatch(
            r"\{\s*agent-hours:\s*(null|[0-9]+(?:\.[0-9]+)?),\s*size:\s*(null|[A-Za-z0-9]+)\s*\}",
            value,
        )
        _check(match, "unsupported estimate frontmatter")
        return {
            "agent-hours": None if match[1] == "null" else Decimal(match[1]),
            "size": None if match[2] == "null" else match[2],
        }


def _event(row, story, source):
    _check(
        isinstance(row, dict)
        and type(row.get("story")) is int
        and row["story"] == story
        and _number(story)
        and isinstance(row.get("data"), dict)
        and _pattern(row.get("type"), TOKEN),
        "event identity does not match its story",
    )
    stamp = _stamp(row.get("ts"))
    recorded = _stamp(row["recorded_at_utc"]) if "recorded_at_utc" in row else stamp
    _check(stamp <= recorded, "event occurred after its recording")
    return Event(
        story,
        row["type"],
        stamp,
        row["data"],
        source,
        recorded,
        row["actor"] if isinstance(row.get("actor"), dict) else None,
    )


def _estimate(obj, key, source):
    _check(isinstance(obj, dict), "invalid estimate")
    hours, size, scope = obj.get(key), obj.get("size"), obj.get("scope")
    _check(
        hours is None
        or (
            type(hours) in {int, float, Decimal}
            and Decimal(str(hours)).is_finite()
            and hours >= 0
        ),
        "invalid estimate hours",
    )
    _check(size is None or _pattern(size, TOKEN), "invalid estimate size")
    phase = scope.get("phase") if isinstance(scope, dict) else None
    roles = scope.get("roles") if isinstance(scope, dict) else None
    _check(phase is None or _pattern(phase, TOKEN), "invalid estimate phase")
    _check(
        roles is None
        or (isinstance(roles, list) and all(_pattern(role, TOKEN) for role in roles)),
        "invalid estimate roles",
    )
    return Estimate(
        None if hours is None else Decimal(str(hours)),
        size,
        phase,
        None if roles is None else tuple(sorted(set(roles))),
        source,
    )


def _facts(git, blobs, as_of, gaps):
    stories, estimates, events = {}, {}, []
    own_parents, child_claims = {}, defaultdict(set)
    for path, blob in sorted(blobs.items()):
        match = ROOT.fullmatch(path)
        if not match or match[3] != "story.md":
            continue
        story = int(match[2])
        if _root(story) + "story.md" != path:
            continue
        try:
            header = _header(git.read(blob))
            title = _header_value(header, "title")
            _check(
                type(_header_value(header, "id")) is int
                and _header_value(header, "id") == story
                and isinstance(title, str)
                and title.strip(),
                "invalid story identity",
            )
            if "created" in header and _stamp(_header_value(header, "created")) > as_of:
                gaps.append(Gap(story, "future-story", path))
                continue
        except (ValueError, RecursionError):
            gaps.append(Gap(story, "invalid-story", path))
            continue
        journal = _root(story) + "events.jsonl"
        rows = []
        if journal in blobs:
            try:
                raw = git.read(blobs[journal])
            except ValueError:
                gaps.append(Gap(story, "invalid-journal", journal))
                raw = b""
            for line, entry in enumerate(raw.splitlines(), 1):
                if not entry.strip():
                    continue
                source = f"{journal}:{line}"
                try:
                    obj = _json(entry)
                    if (
                        isinstance(obj, dict)
                        and obj.get("type") == "core.draft.created"
                        and "story" in obj
                        and obj["story"] is None
                    ):
                        # A historical draft event isn't a story-scoped activity fact.
                        _stamp(obj.get("ts"))
                        gaps.append(Gap(story, "unbound-draft-event", source))
                        continue
                    row = _event(obj, story, source)
                    if row.recorded_at > as_of:
                        gaps.append(Gap(story, "future-event", source))
                    else:
                        rows.append(row)
                except (ValueError, RecursionError):
                    gaps.append(Gap(story, "invalid-event", source))
        else:
            gaps.append(Gap(story, "missing-journal", journal))
        # Python's stable sort preserves journal order for equal UTC instants.
        rows.sort(key=lambda row: (row.timestamp, row.recorded_at))
        events.extend(rows)
        try:
            header_eligible = (
                "updated" not in header
                or _stamp(_header_value(header, "updated")) <= as_of
            )
        except ValueError:
            header_eligible = False
        if not header_eligible:
            gaps.append(Gap(story, "ineligible-header", path))
        if header_eligible and "parent" in header:
            try:
                parent = _header_value(header, "parent")
                _check(parent is None or _number(parent), "invalid parent")
                own_parents[story] = (parent, False)
            except ValueError:
                gaps.append(Gap(story, "invalid-ancestry", path))
        if header_eligible and "children" in header:
            try:
                children = _header_value(header, "children")
                _check(
                    isinstance(children, list)
                    and all(_number(child) for child in children),
                    "invalid children",
                )
                for child in children:
                    child_claims[child].add(story)
            except (ValueError, RecursionError):
                gaps.append(Gap(story, "invalid-ancestry", path))
        state, state_source = None, None
        if header_eligible:
            try:
                state = _header_value(header, "state")
                _check(
                    isinstance(state, str) and state in STATES, "invalid story state"
                )
                state_source = path
            except ValueError:
                gaps.append(Gap(story, "invalid-state", path))
                state = None
            if "estimate" in header:
                try:
                    estimates[story] = _estimate(
                        _header_estimate(header["estimate"]), "agent-hours", path
                    )
                except (ValueError, RecursionError):
                    gaps.append(Gap(story, "invalid-estimate", path))
        for row in rows:
            if row.kind == "core.state.entered":
                candidate = row.data.get("state")
                if isinstance(candidate, str) and candidate in STATES:
                    state, state_source = candidate, row.source
                else:
                    state, state_source = None, None
                    gaps.append(Gap(story, "invalid-state", row.source))
            elif row.kind == "core.estimate.set":
                try:
                    estimates[story] = _estimate(row.data, "agent_hours", row.source)
                except ValueError:
                    estimates.pop(story, None)
                    gaps.append(Gap(story, "invalid-estimate", row.source))
            elif row.kind == "core.link.parent-set":
                parent = row.data.get("parent")
                if "parent" in row.data and (parent is None or _number(parent)):
                    own_parents[story] = (parent, True)
                else:
                    own_parents[story] = (None, True)
                    gaps.append(Gap(story, "invalid-ancestry", row.source))
            elif row.kind == "core.link.child-added":
                child = row.data.get("child")
                if _number(child):
                    child_claims[child].add(story)
                else:
                    gaps.append(Gap(story, "invalid-ancestry", row.source))
        stories[story] = Story(story, title, state, state_source, path)
    return (
        dict(sorted(stories.items())),
        dict(sorted(estimates.items())),
        tuple(sorted(events, key=lambda row: row.story)),
        own_parents,
        child_claims,
    )


def _graph(stories, own_parents, child_claims, gaps):
    parents = {}
    for child in sorted(stories.keys() | child_claims.keys()):
        path = _root(child) + "story.md"
        claims = child_claims[child]
        if child not in stories:
            for parent in sorted(claims):
                gaps.append(Gap(parent, "ancestry-missing", path))
            continue
        parent, explicit = own_parents.get(child, (None, False))
        candidates = ({parent} if parent is not None else set()) | claims
        if not explicit and len(candidates) > 1:
            gaps.extend(
                Gap(affected, "ancestry-conflict", path)
                for affected in sorted(candidates | {child})
            )
            continue
        if not explicit and candidates:
            parent = next(iter(candidates))
        if parent is not None:
            if parent in stories:
                parents[child] = parent
            else:
                gaps.append(Gap(child, "ancestry-missing", path))
    checked, cyclic = set(), set()
    for story in sorted(parents):
        index = {}
        node = story
        while node in parents and node not in checked:
            if node in index:
                cyclic.update(list(index)[index[node] :])
                break
            index[node] = len(index)
            node = parents[node]
        checked.update(index)
    for story in sorted(cyclic):
        del parents[story]
        gaps.append(Gap(story, "ancestry-cycle", stories[story].path))
    descendants = {story: [] for story in sorted(stories)}
    for story in sorted(parents):
        node = story
        while node in parents:
            node = parents[node]
            descendants[node].append(story)
    return parents, {story: tuple(children) for story, children in descendants.items()}


def _registered(git, blobs, events, as_of, gaps):
    claims = defaultdict(list)
    legacy_claims = {}
    for row in events:
        if row.kind != "core.evidence.recorded":
            continue
        kind = row.data.get("kind")
        if kind == "historical-actual-backfill":
            paths = row.data.get("evidence")
            if row.story == 181:
                # An exact retry repeats the original seed registration.
                key = json.dumps(row.data, sort_keys=True, separators=(",", ":"))
                legacy_claims.setdefault(key, row)
            if (
                row.story != 181
                or not isinstance(paths, list)
                or paths.count(LEGACY_PATH) != 1
                or row.data.get("receipt_sha256") != LEGACY_SHA256
            ):
                gaps.append(Gap(row.story, "invalid-legacy-seed", row.source))
        elif isinstance(kind, str) and kind in SCHEMAS:
            try:
                claim = _registration(row)
                claims[claim.story, claim.path].append(claim)
            except ValueError:
                gaps.append(Gap(row.story, "invalid-registration", row.source))

    receipts = []
    for (story, path), entries in sorted(claims.items()):
        claim = entries[0]
        if len({entry.identity for entry in entries}) != 1:
            gaps.append(Gap(story, "registration-conflict", claim.source))
            continue
        full_path = _root(story) + path
        blob = blobs.get(full_path)
        if blob is None:
            gaps.append(Gap(story, "receipt-missing", full_path))
            continue
        try:
            raw = git.read(blob)
        except ValueError:
            gaps.append(Gap(story, "receipt-blob", full_path))
            continue
        if hashlib.sha256(raw).hexdigest() != claim.sha256:
            gaps.append(Gap(story, "receipt-digest", full_path))
            continue
        try:
            receipts.append(validate_receipt(raw, claim, as_of=as_of))
        except _FutureReceipt:
            gaps.append(Gap(story, "future-receipt", full_path))
        except (ValueError, RecursionError):
            gaps.append(Gap(story, "invalid-receipt", full_path))

    legacy = list(legacy_claims.values())
    legacy_seed = None
    path = _root(181) + LEGACY_PATH
    if len(legacy) > 1:
        gaps.append(Gap(181, "legacy-conflict", legacy[1].source))
    elif legacy:
        data = legacy[0].data
        paths = data.get("evidence")
        if (
            isinstance(paths, list)
            and paths.count(LEGACY_PATH) == 1
            and data.get("receipt_sha256") == LEGACY_SHA256
        ):
            try:
                raw = git.read(blobs[path])
                _check(
                    hashlib.sha256(raw).hexdigest() == LEGACY_SHA256,
                    "legacy seed digest mismatch",
                )
                legacy_seed = raw
            except (KeyError, ValueError):
                gaps.append(Gap(181, "legacy-blob", path))
    return (
        tuple(receipts),
        legacy_seed,
        {key: tuple(items) for key, items in claims.items()},
    )


def read_tree(repo: Path, commit: str, as_of: datetime) -> PlanningTree:
    """Read only eligible story evidence from a full pinned Git commit."""
    _check(_pattern(commit, SHA1), "expected a full lowercase 40-hex commit")
    _check(
        isinstance(as_of, datetime) and as_of.utcoffset() == UTC.utcoffset(as_of),
        "expected a UTC cutoff",
    )
    git = _Git(repo)
    _check(
        git.run("cat-file", "-t", commit) == b"commit\n",
        "expected a direct commit object",
    )
    _check(
        int(git.run("cat-file", "-s", commit)) <= MAX_BLOB, "commit exceeds byte limit"
    )
    raw = git.run("cat-file", "commit", commit)
    header = raw.split(b"\n\n", 1)[0]
    match = re.search(rb"^committer [^\n]+ ([0-9]+) [+-][0-9]{4}$", header, re.M)
    _check(match, "invalid commit timestamp")
    try:
        commit_time = datetime.fromtimestamp(int(match[1]), UTC)
    except (OverflowError, OSError) as exc:
        raise ValueError("invalid commit timestamp") from exc
    _check(as_of >= commit_time, "as-of cutoff precedes commit time")
    blobs = git.tree(commit)
    gaps = []
    stories, estimates, events, own_parents, child_claims = _facts(
        git, blobs, as_of, gaps
    )
    parents, descendants = _graph(stories, own_parents, child_claims, gaps)
    receipts, seed, claims = _registered(git, blobs, events, as_of, gaps)
    return PlanningTree(
        commit,
        commit_time,
        as_of,
        stories,
        events,
        estimates,
        parents,
        descendants,
        tuple(receipt.registration for receipt in receipts),
        receipts,
        seed,
        tuple(sorted(gaps, key=lambda gap: (gap.story, gap.code, gap.source))),
        claims,
        blobs,
    )


def _local_bytes(path):
    # Don't block on a pipe or follow a symlink supplied as a prospective evidence file.
    with os.fdopen(
        os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW), "rb"
    ) as handle:
        info = os.fstat(handle.fileno())
        _check(
            stat.S_ISREG(info.st_mode) and info.st_size <= MAX_BLOB,
            "expected a bounded regular local file",
        )
        return handle.read(MAX_BLOB + 1)


def _prospective(repo, tree, raw, event_bytes):
    obj = _json(event_bytes)
    row = _event(
        obj, obj.get("story") if isinstance(obj, dict) else None, "prospective"
    )
    _check(
        row.story in tree.stories, "registration story is absent from the pinned tree"
    )
    _check(row.recorded_at <= tree.as_of, "registration is beyond the as-of cutoff")
    claim = _registration(row)
    prior = tree._claims.get((claim.story, claim.path), ())
    _check(
        all(item.identity == claim.identity for item in prior),
        "registration conflicts with the pinned path",
    )
    path = _root(claim.story) + claim.path
    if path in tree._blobs:
        _check(
            _Git(repo).read(tree._blobs[path]) == raw,
            "receipt would rewrite a pinned path",
        )
    elif prior:
        raise ValueError(
            "pinned registration has missing bytes; reconcile before retrying"
        )
    return validate_receipt(raw, claim, as_of=tree.as_of)


def _receipt_summary(receipt):
    claim = receipt.registration
    return {
        "story": claim.story,
        "project": claim.project,
        "path": claim.path,
        "sha256": claim.sha256,
        "schema": receipt.schema,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--registration", type=Path)
    args = parser.parse_args(argv)
    if (args.receipt is None) != (args.registration is None):
        parser.error("--receipt and --registration must be supplied together")
    try:
        tree = read_tree(args.repo, args.commit, _stamp(args.as_of))
        report = {
            "commit": tree.commit,
            "commit_time_utc": tree.commit_time.isoformat(),
            "as_of_utc": tree.as_of.isoformat(),
            "stories": len(tree.stories),
            "events": len(tree.events),
            "receipts": [_receipt_summary(receipt) for receipt in tree.receipts],
            "legacy_seed_sha256": LEGACY_SHA256
            if tree.legacy_seed is not None
            else None,
            "gaps": [
                {"story": gap.story, "code": gap.code, "source": gap.source}
                for gap in tree.gaps
            ],
        }
        if args.receipt is not None:
            receipt = _prospective(
                args.repo,
                tree,
                _local_bytes(args.receipt),
                _local_bytes(args.registration),
            )
            report["prospective"] = _receipt_summary(receipt)
    except (ValueError, OSError, RecursionError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
