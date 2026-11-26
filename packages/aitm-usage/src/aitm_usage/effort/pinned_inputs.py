"""Resolve one story's immutable reporting inputs from a verified planning tree."""

import json
import os
import re
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from time import monotonic
from uuid import UUID

from ..types import _unique_fields
from .pinned_coverage import (
    COVERAGE_KIND,
    MAX_INPUT_BLOB_BYTES,
    WINDOW_FIELDS,
    canonical_window,
    utc_stamp,
    validate_coverage,
)
from .receipts import require_item
from .session import validate_public_receipt
from .session_publication import _GIT_TIMEOUT, _RECEIPT_PATH
from .store import EffortError

_MAX_INPUT_TOTAL = 64 << 20
_FULL_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_COVERAGE_PATH = re.compile(r"attachments/effort/coverage/[0-9a-f]{64}\.json")
_SHA = re.compile(r"[0-9a-f]{64}")
_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")


def _matches(value: object, pattern: re.Pattern) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


class PinnedTree:
    """Read bounded regular blobs from an exact Git commit without a checkout."""

    def __init__(self, repository: Path, commit: str):
        if not _matches(commit, _FULL_COMMIT):
            raise EffortError("Expected a full immutable Git commit ID")
        self.repository = repository
        self.commit = commit
        self.total = 0
        self._entries: dict[str, tuple[bytes, str] | None] = {}
        self._env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self._env.update(
            GIT_NO_REPLACE_OBJECTS="1",
            GIT_NO_LAZY_FETCH="1",
            GIT_OPTIONAL_LOCKS="0",
            GIT_TERMINAL_PROMPT="0",
            GIT_ALLOW_PROTOCOL="",
            GIT_LITERAL_PATHSPECS="1",
        )
        try:
            resolved = self._read(
                "rev-parse", "--verify", f"{commit}^{{commit}}", limit=256
            )
        except ValueError:
            raise EffortError("Pinned Git commit is unavailable") from None
        if resolved.strip() != commit.encode():
            raise EffortError("Expected a full immutable Git commit ID")

    def _entry(self, path: str) -> tuple[bytes, str] | None:
        if path not in self._entries:
            raw = self._read("ls-tree", "-z", self.commit, "--", path, limit=4096)
            entry = None
            if raw:
                details, name = raw[:-1].split(b"\t", 1)
                mode, _, object_id = details.split(b" ")
                if name != path.encode():
                    raise EffortError("Unexpected path in pinned evidence tree")
                entry = mode, object_id.decode("ascii")
            self._entries[path] = entry
        return self._entries[path]

    def _roots(self, path: str, *, directory: bool = False) -> bool:
        relative = PurePosixPath(path)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or relative.as_posix() != path
        ):
            raise EffortError("Invalid pinned evidence path")
        parents = (*relative.parents, relative) if directory else relative.parents
        for parent in parents:
            if parent == PurePosixPath("."):
                continue
            found = self._entry(parent.as_posix())
            if found is None:
                return False
            if found[0] != b"040000":
                raise EffortError("Expected a normal pinned evidence directory")
        return True

    def read(
        self, path: str, *, limit: int = MAX_INPUT_BLOB_BYTES, optional: bool = False
    ) -> bytes | None:
        entry = self._entry(path) if self._roots(path) else None
        if entry is None:
            if optional:
                return None
            raise EffortError("Pinned evidence file is unavailable")
        mode, object_id = entry
        if mode != b"100644":
            raise EffortError("Expected a normal pinned evidence file")
        size = int(self._read("cat-file", "-s", object_id, limit=256))
        if size > limit or self.total + size > _MAX_INPUT_TOTAL:
            raise EffortError("Pinned evidence exceeds read limits")
        self.total += size
        data = self._read("cat-file", "blob", object_id, limit=size)
        if len(data) != size:
            raise EffortError("Pinned evidence length changed")
        return data

    def paths(self, root: str) -> tuple[bytes, ...]:
        if not self._roots(root, directory=True):
            return ()
        data = self._read(
            "ls-tree",
            "-rz",
            "--name-only",
            self.commit,
            "--",
            root,
            limit=_MAX_INPUT_TOTAL,
            operation="tree listing",
        )
        return tuple(data.split(b"\0")[:-1])

    def _read(self, *args: str, limit: int, operation: str = "Git read") -> bytes:
        command = ["git", "-C", str(self.repository), *args]
        deadline = monotonic() + _GIT_TIMEOUT

        def read_pipe(pipe):
            data = bytearray()
            while len(data) <= limit:
                chunk = os.read(pipe, min(65536, limit + 1 - len(data)))
                if not chunk:
                    return bytes(data)
                data.extend(chunk)
            raise EffortError(f"Pinned {operation} exceeds read limits")

        with (
            subprocess.Popen(
                command,
                env=self._env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            ) as child,
            ThreadPoolExecutor(max_workers=1) as reader,
        ):
            try:
                pending = reader.submit(read_pipe, child.stdout.fileno())
                data = pending.result(timeout=max(0, deadline - monotonic()))
                if child.wait(timeout=max(0, deadline - monotonic())):
                    raise EffortError(f"Pinned {operation} failed")
                return data
            except (TimeoutError, subprocess.TimeoutExpired):
                raise EffortError(f"Pinned {operation} deadline exceeded") from None
            finally:
                if child.poll() is None:
                    child.kill()


@dataclass(frozen=True, slots=True)
class PinnedInputs:
    project: UUID
    story: int
    planning_commit: str
    window: dict[str, str]
    receipts: tuple[dict, ...]
    coverage: dict | None
    gaps: tuple[str, ...]
    manifest: dict
    timing: tuple[dict, ...] = ()


def _digest(path: str, raw: bytes) -> dict:
    return {"path": path, "sha256": sha256(raw).hexdigest()}


def _events(tree: PinnedTree, root: str) -> tuple[tuple[dict, ...], dict | None]:
    path = f"{root}/events.jsonl"
    try:
        file = tree.read(path, optional=True)
        if file is None:
            return (), None
        if file and not file.endswith(b"\n"):
            raise EffortError("Incomplete pinned story event stream")
        events = tuple(
            json.loads(line, object_pairs_hook=_unique_fields)
            for line in file.splitlines()
        )
        if any(type(row) is not dict for row in events):
            raise EffortError("Invalid pinned story event stream")
    except (ValueError, RecursionError) as error:
        raise EffortError("Invalid pinned story event stream") from error
    return events, _digest(path, file)


def _registration_time(event: dict, story: int):
    actor = event.get("actor")
    provenance = event.get("provenance")
    if (
        event.get("type") != "core.evidence.recorded"
        or type(event.get("story")) is not int
        or event["story"] != story
        or type(event.get("v")) is not int
        or event["v"] != 0
        or type(actor) is not dict
        or actor.get("kind") not in ("human", "agent", "tool")
        or type(provenance) is not dict
        or provenance.get("route") != "manual-bootstrap"
        or provenance.get("runtime_transition") is not False
    ):
        raise EffortError("Invalid pinned evidence registration")
    occurred = utc_stamp(event.get("ts"))
    recorded = utc_stamp(event.get("recorded_at_utc", event["ts"]))
    if occurred > recorded:
        raise EffortError("Invalid pinned evidence chronology")
    return recorded


def _records(
    tree: PinnedTree, events: tuple[dict, ...], root: str, identity: tuple, window: dict
) -> tuple[dict | None, list[dict], str | None]:
    project, story = identity
    records = {}
    cutoff = utc_stamp(window["cutoff_utc"])
    for row in events:
        item = row.get("data")
        if (
            row.get("type") != "core.evidence.recorded"
            or type(item) is not dict
            or item.get("kind") != COVERAGE_KIND
        ):
            continue
        try:
            item_window = item.get("window")
            if canonical_window(item_window) != item_window:
                raise EffortError("Noncanonical registered window")
            if item_window != window:
                continue
            if _registration_time(row, story) < cutoff:
                raise EffortError("Coverage was registered before its cutoff")
        except EffortError:
            return None, [], "coverage-invalid-registration"
        scope = item.get("scope")
        if (
            set(item) != {"kind", "path", "sha256", "scope", "window"}
            or scope != {"project": str(project), "story": story}
            or type(scope["story"]) is not int
            or not _matches(item.get("path"), _COVERAGE_PATH)
            or not _matches(item.get("sha256"), _SHA)
        ):
            return None, [], "coverage-invalid-registration"
        path = f"{root}/{item['path']}"
        try:
            raw = tree.read(path, optional=True)
        except ValueError:
            return None, [], "coverage-invalid-file"
        if raw is None:
            return None, [], "coverage-file-missing"
        digest = sha256(raw).hexdigest()
        if (
            digest != item["sha256"]
            or item["path"] != f"attachments/effort/coverage/{digest}.json"
        ):
            return None, [], "coverage-digest-mismatch"
        try:
            record = validate_coverage(raw)
        except EffortError:
            return None, [], "coverage-invalid-file"
        if (record["project"], record["story"], record["window"]) != (
            str(project),
            story,
            window,
        ):
            return None, [], "coverage-invalid-scope"
        records[digest] = record, _digest(path, raw)
    if not records:
        return None, [], "coverage-missing"
    heads = records.keys() - {
        record["supersedes"]
        for record, _ in records.values()
        if record["supersedes"] is not None
    }
    if len(heads) != 1:
        return None, [], "coverage-conflict"
    (cursor,) = heads
    latest = records[cursor][0]
    ordered = []
    while cursor is not None and cursor in records and len(ordered) < len(records):
        row, descriptor = records[cursor]
        ordered.append(descriptor)
        cursor = row["supersedes"]
    if cursor is not None or len(ordered) != len(records):
        return None, [], "coverage-conflict"
    return latest, ordered[::-1], None


def _receipt_files(tree: PinnedTree, root: str, project: UUID, story: int) -> list:
    files = []
    identities = set()
    attempts = {}
    for rawpath in tree.paths(f"{root}/attachments/effort/session"):
        match = _RECEIPT_PATH.fullmatch(rawpath)
        if match is None:
            raise EffortError("Invalid pinned story receipt path")
        _, _, identity = match.groups()
        path = rawpath.decode("ascii")
        revision = path.rsplit("-r", 1)[1].removesuffix(".json")
        raw = tree.read(path)
        try:
            row = validate_public_receipt(raw)
        except (TypeError, ValueError, RecursionError):
            raise EffortError("Invalid pinned story receipt bytes") from None
        identifier = identity.decode("ascii")
        if (row["project"], row["story"], row["identity"], row["revision"]) != (
            str(project),
            story,
            identifier,
            int(revision),
        ):
            raise EffortError("Pinned receipt scope differs from its path or report")
        if attempts.setdefault(row["attempt"], identifier) != identifier:
            raise EffortError("Multiple pinned receipt identities for one attempt")
        identities.add(identity)
        descriptor = _digest(path, raw) | {
            "identity": identifier,
            "revision": row["revision"],
        }
        files.append((row, descriptor))
    if identities:
        for path in tree.paths(".aitm/stories"):
            match = _RECEIPT_PATH.fullmatch(path)
            if (
                match
                and match[3] in identities
                and not path.startswith(root.encode() + b"/")
            ):
                raise EffortError(
                    "Pinned receipt identity is assigned to another story"
                )
    return files


def _eligible(files, cutoff, gaps):
    groups = {}
    for row, descriptor in files:
        groups.setdefault(row["identity"], []).append((row, descriptor))
    excluded = []
    selected = []
    for group in groups.values():
        chain = sorted(group, key=lambda pair: pair[0]["revision"])
        previous = None
        observed = []
        crossed = False
        for revision, (current, descriptor) in enumerate(chain, 1):
            same = ("attempt", "project", "provider", "role", "story", "identity")
            if (
                current["revision"] != revision
                or current["previous_receipt_sha256"]
                != (previous[1]["sha256"] if previous else None)
                or previous
                and any(current[key] != previous[0][key] for key in same)
            ):
                raise EffortError("Invalid pinned receipt revision lineage")
            moment = utc_stamp(current["observed_at"])
            if observed and moment < observed[-1]:
                if moment <= cutoff < observed[-1]:
                    crossed = True
                else:
                    raise EffortError("Regressed pinned receipt revision time")
            observed.append(moment)
            previous = current, descriptor
        if crossed:
            gaps.add("cutoff-lineage")
            excluded.extend(
                descriptor | {"reason": "cutoff-lineage"} for _, descriptor in chain
            )
            continue
        pick = max(
            (i for i, moment in enumerate(observed) if moment <= cutoff), default=-1
        )
        for i, (current, descriptor) in enumerate(chain):
            if i == pick:
                selected.append((current, descriptor))
            else:
                reason = "superseded" if i < pick else "after-cutoff"
                excluded.append(descriptor | {"reason": reason})
    return selected, excluded


def _outside(row: dict, start, end) -> str | None:
    begin = utc_stamp(row["started_at"]) if row["started_at"] is not None else None
    stop = utc_stamp(row["ended_at"]) if row["ended_at"] is not None else None
    if (
        begin is not None
        and begin >= end
        or stop is not None
        and (stop < start or stop == start and begin is not None and begin < start)
    ):
        return "outside-window"
    if begin is None or stop is None:
        return "unknown-window"
    if begin < start or stop > end:
        return "crossing-window"
    return None


def _select_scope(selected, excluded, coverage, start, end, gaps):
    attempts = (
        {}
        if coverage is None
        else {item["attempt"]: item["state"] for item in coverage["attempts"]}
    )
    keep = []
    settled = set()
    for row, descriptor in selected:
        state = attempts.get(row["attempt"])
        reason = _outside(row, start, end)
        if state in ("withdrawn", "disputed") and reason != "outside-window":
            reason = state
        elif coverage is not None and reason is None and state != "observed":
            gaps.add("coverage-unmatched-receipts")
            if coverage["admission"] == "closed" or state is not None:
                reason = "coverage-unmatched-receipts"
        if reason is None:
            keep.append((row, descriptor))
            settled.add(row["attempt"])
        else:
            excluded.append(descriptor | {"reason": reason})
            if reason != "outside-window":
                gaps.add(reason)
    if any(
        state == "observed" and attempt not in settled
        for attempt, state in attempts.items()
    ):
        gaps.add("coverage-unmatched-receipts")
    return keep


def _timing_source(source: dict) -> None:
    if (
        type(source) is not dict
        or not source
        or source.keys() - {"ref", "sha256"}
        or "ref" in source
        and not _matches(source["ref"], _LABEL)
        or "sha256" in source
        and not _matches(source["sha256"], _SHA)
    ):
        raise EffortError("Invalid registered timing source evidence")


def _timing_rows(source: dict, recorded_at) -> dict:
    _timing_source(source["source"])
    observations = source["observations"]
    if type(observations) is not list or not observations:
        raise EffortError("Missing registered timing observations")
    rows = {}
    for row in observations:
        identifier = row["observation_id"]
        if not _matches(identifier, _LABEL) or identifier in rows:
            raise EffortError("Invalid or duplicate timing observation identity")
        if "source" in row:
            _timing_source(row["source"])
        observed_at = utc_stamp(row.get("recorded_at_utc", source["recorded_at_utc"]))
        if observed_at > recorded_at or any(
            stamp > observed_at or stamp.microsecond % 1000 != 0
            for stamp in (
                utc_stamp(row[key])
                for key in ("start_utc", "end_utc")
                if row[key] is not None
            )
        ):
            raise EffortError("Invalid timing observation chronology or precision")
        rows[identifier] = row
    return rows


def _registered_timing(tree, events, root, story, coverage, receipts, cutoff, gaps):
    if not coverage or not coverage.get("timing"):
        return (), []
    by_attempt = {row["attempt"]: row for row in receipts}
    timing = []
    sources = {}
    joins = coverage["timing"]
    target_keys = ("path", "sha256", "observation")
    targets = Counter(tuple(join[key] for key in target_keys) for join in joins)
    for join in joins:
        receipt = by_attempt.get(join["attempt"])
        path = f"{root}/{join['path']}"
        try:
            if targets[tuple(join[key] for key in target_keys)] != 1:
                raise EffortError("Multiple attempts use the same timing observation")
            expected = {
                "kind": "story-timing-receipt",
                "path": join["path"],
                "sha256": join["sha256"],
                "scope": {"project": join["project"], "story": story},
            }
            registrations = [
                _registration_time(event, story)
                for event in events
                if event.get("type") == "core.evidence.recorded"
                and event.get("data") == expected
            ]
            admitted = [recorded for recorded in registrations if recorded <= cutoff]
            if not receipt or not admitted:
                raise EffortError("Missing trusted timing registration")
            if path not in sources:
                raw = tree.read(path)
                if sha256(raw).hexdigest() != join["sha256"]:
                    raise EffortError("Mismatched pinned timing digest")
                source = json.loads(raw, object_pairs_hook=_unique_fields)
                recorded_at = utc_stamp(source["recorded_at_utc"])
                if (
                    (source["schema"], source["project"], source["subject"])
                    != (
                        "aitm.story-timing-receipt/v1",
                        join["project"],
                        story,
                    )
                    or type(source["batch"]) is not str
                    or join["path"]
                    != f"attachments/timing/{source['batch']}-{story}.json"
                    or recorded_at > cutoff
                    or any(recorded < recorded_at for recorded in admitted)
                ):
                    raise EffortError("Invalid registered timing scope")
                sources[path] = (
                    _timing_rows(source, recorded_at),
                    _digest(path, raw),
                )
            source_rows, digest = sources[path]
            if digest["sha256"] != join["sha256"]:
                raise EffortError("Mismatched pinned timing digest")
            turn = source_rows[join["observation"]]
            start, end = (utc_stamp(turn[key]) for key in ("start_utc", "end_utc"))
            if (
                turn["kind"] != "agent-turn"
                or turn["coverage"] != "complete"
                or not _matches(turn["basis"], _LABEL)
                or not _matches(turn["actor"], _LABEL)
                or not start < end
                or (start, end)
                != (utc_stamp(receipt["started_at"]), utc_stamp(receipt["ended_at"]))
            ):
                raise EffortError("Pinned timing does not bind the receipt interval")
            waits = []
            for label in join["waits"]:
                wait = source_rows[label]
                first, last = (utc_stamp(wait[key]) for key in ("start_utc", "end_utc"))
                if (
                    wait["kind"] != "owner-wait"
                    or wait["coverage"] != "complete"
                    or not _matches(wait["basis"], _LABEL)
                    or wait["actor"] != turn["actor"]
                    or not start <= first < last <= end
                    or not turn.get("turn")
                    or wait.get("turn") != turn["turn"]
                ):
                    raise EffortError("Incomplete registered owner wait")
                waits.append({"start": first.isoformat(), "end": last.isoformat()})
            linked_waits = {
                row["observation_id"]
                for row in source_rows.values()
                if row["kind"] == "owner-wait"
                and row["actor"] == turn["actor"]
                and row.get("turn") == turn.get("turn")
            }
            if linked_waits != set(join["waits"]):
                raise EffortError("Unreconciled registered owner waits")
            timing.append(
                {
                    "attempt": join["attempt"],
                    "actor": turn["actor"],
                    "clock": join["clock"],
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "owner_waits": waits,
                }
            )
        except (TypeError, ValueError, KeyError, RecursionError):
            gaps.add("timing-evidence-invalid")
    return tuple(timing), [value[1] for value in sources.values()]


def read_inputs(
    repo: Path, project: UUID, story: int, planning_commit: str, window: dict
) -> PinnedInputs:
    """Read only exact target evidence; known gaps remain distinct from malformed receipts."""
    require_item(story)
    if type(project) is not UUID or story is None:
        raise EffortError("Expected a report project UUID and story")
    window = canonical_window(window)
    start, end, cutoff = (utc_stamp(window[field]) for field in WINDOW_FIELDS)
    tree = PinnedTree(repo, planning_commit)
    root = f".aitm/stories/{story // 100:03d}/{story}"
    story_path = f"{root}/story.md"
    story_data = tree.read(story_path)
    lines = story_data.splitlines()
    if not lines or lines[0] != b"---" or b"---" not in lines[1:]:
        raise EffortError("Pinned story frontmatter is unavailable")
    header_end = lines.index(b"---", 1)
    identifiers = [
        line[3:].strip() for line in lines[1:header_end] if line.startswith(b"id:")
    ]
    if identifiers != [str(story).encode()]:
        raise EffortError("Pinned story does not match the requested scope")
    gaps: set[str] = set()
    try:
        events, registration = _events(tree, root)
    except EffortError:
        events, registration = (), None
        gaps.add("coverage-invalid-event-stream")
    coverage, coverage_files, gap = _records(
        tree, events, root, (project, story), window
    )
    if gap is not None:
        gaps.add(gap)
    selected, excluded = _eligible(
        _receipt_files(tree, root, project, story), cutoff, gaps
    )
    eligible = _select_scope(selected, excluded, coverage, start, end, gaps)
    eligible.sort(key=lambda pair: pair[1]["path"])
    rows = tuple(row for row, _ in eligible)
    timing, timing_files = _registered_timing(
        tree, events, root, story, coverage, rows, cutoff, gaps
    )
    manifest = {
        "receipts": [descriptor for _, descriptor in eligible],
        "excluded": sorted(excluded, key=lambda descriptor: descriptor["path"]),
        "coverage": coverage_files,
        "timing": sorted(timing_files, key=lambda item: item["path"]),
        "registration": registration,
    }
    return PinnedInputs(
        project,
        story,
        tree.commit,
        window,
        rows,
        coverage,
        tuple(sorted(gaps)),
        manifest,
        timing,
    )
