"""Publish and register one frozen report through an authorized planning origin."""

import json
import re
import tempfile
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from uuid import uuid4

from ..types import _unique_fields
from .pinned_report import canonical, report_path, validate_envelope
from .session_publication import (
    _MAX_PUSHES,
    _PLANNING,
    PublicationHold,
    _git,
    _PlanningTree,
    _read,
    _require_remote,
)

_MAX_REPORT_BYTES = 16 * 1024 * 1024
_REGISTRATION_KIND = "pinned-story-effort-report"
_OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
_OPERATOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)"
)


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValueError("Expected a UTC timestamp")
    return datetime.fromisoformat(value)


def _remote_tip(repository: Path, remote: str, fetch_ref: str) -> str | None:
    _require_remote(repository, remote)
    fetch = _git(
        repository,
        "fetch",
        "--no-tags",
        "--no-write-fetch-head",
        "--no-auto-maintenance",
        "--refmap=",
        "origin",
        f"{_PLANNING}:{fetch_ref}",
    )
    if fetch.returncode:
        return None
    return (
        _read(repository, "rev-parse", "--verify", f"{fetch_ref}^{{commit}}")
        .decode("ascii")
        .strip()
    )


def _story_root(story: int) -> str:
    return f".aitm/stories/{story // 100:03d}/{story}"


def _validate_tree(tree: _PlanningTree, story: int, path: str) -> None:
    for parent in reversed(PurePosixPath(path).parents):
        if parent != PurePosixPath("."):
            entry = tree.entry(parent.as_posix())
            if entry is not None and entry[0] != b"040000":
                raise PublicationHold(
                    "Report publication requires normal tree directories"
                )
    story_file = tree.entry(f"{_story_root(story)}/story.md")
    if story_file is not None and story_file[0] == b"100644":
        lines = tree.blob(story_file[1]).splitlines()
        if lines and lines[0] == b"---" and b"---" in lines[1:]:
            stop = lines.index(b"---", 1)
            ids = [
                line[3:].strip() for line in lines[1:stop] if line.startswith(b"id:")
            ]
            if ids == [str(story).encode("ascii")]:
                return
    raise PublicationHold("Planning story does not match the report scope")


def _require_ancestor(repository: Path, commit: str, tip: str) -> None:
    if not isinstance(commit, str) or not _OID.fullmatch(commit):
        raise PublicationHold(
            "Expected an exact planning commit for report publication"
        )
    result = _git(repository, "merge-base", "--is-ancestor", commit, tip)
    if result.returncode:
        raise PublicationHold(
            "The report commit is outside the authorized planning history"
        )


def _require_bytes(
    tree: _PlanningTree, path: str, expected: bytes, message: str
) -> None:
    item = tree.entry(path)
    if item is None or item[0] != b"100644":
        raise PublicationHold(message)
    size = int(_read(tree.repository, "cat-file", "-s", item[1]))
    if (
        size != len(expected)
        or size > _MAX_REPORT_BYTES
        or _read(tree.repository, "cat-file", "blob", item[1]) != expected
    ):
        raise PublicationHold(message)


def _commit_artifact(
    repository: Path, index: Path, tip: str, path: str, envelope: bytes
) -> str:
    _read(repository, "read-tree", tip, index=index)
    blob_id = _read(repository, "hash-object", "-w", "--stdin", data=envelope).strip()
    _read(
        repository,
        "update-index",
        "-z",
        "--index-info",
        index=index,
        data=b"100644 " + blob_id + b"\t" + path.encode("ascii") + b"\0",
    )
    tree = _read(repository, "write-tree", index=index).decode("ascii").strip()
    return (
        _read(
            repository,
            "commit-tree",
            tree,
            "-p",
            tip,
            "-m",
            "Publish pinned story effort report",
        )
        .decode("ascii")
        .strip()
    )


def _artifact_commit(
    repository: Path, tip: str, path: str, *, present: bool
) -> str | None:
    commits = (
        _read(repository, "log", "-2", "--first-parent", "--format=%H", tip, "--", path)
        .decode("ascii")
        .splitlines()
    )
    if not commits and not present:
        return None
    if present and len(commits) == 1 and _OID.fullmatch(commits[0]):
        return commits[0]
    raise PublicationHold("Refused conflicting immutable report history")


def publish_pinned_report(
    repository: Path, authorized_remote: str, envelope: bytes
) -> tuple[str, str]:
    """Publish validated bytes once and return the immutable report/commit pair."""
    report = validate_envelope(envelope, for_publication=True)
    story = report["manifest"]["story"]
    report_id = report["report_id"]
    path = report_path(story, report_id)
    fetch_ref = f"refs/aitm/pinned-report-publication/{uuid4().hex}"
    try:
        with tempfile.TemporaryDirectory(
            prefix="aitm-pinned-report-publication-"
        ) as directory:
            index = Path(directory) / "index"
            for attempt in range(_MAX_PUSHES + 1):
                tip = _remote_tip(repository, authorized_remote, fetch_ref)
                if tip is None:
                    continue
                _require_ancestor(
                    repository, report["manifest"]["planning_commit"], tip
                )
                tree = _PlanningTree(repository, tip)
                _validate_tree(tree, story, path)
                if tree.entry(path) is not None:
                    _require_bytes(
                        tree, path, envelope, "Refused conflicting immutable report"
                    )
                    artifact = _artifact_commit(repository, tip, path, present=True)
                    _require_ancestor(
                        repository, report["manifest"]["planning_commit"], artifact
                    )
                    _require_bytes(
                        _PlanningTree(repository, artifact),
                        path,
                        envelope,
                        "Report artifact readback mismatch",
                    )
                    return report_id, artifact
                _artifact_commit(repository, tip, path, present=False)
                if attempt == _MAX_PUSHES:
                    break
                candidate = _commit_artifact(repository, index, tip, path, envelope)
                _require_remote(repository, authorized_remote)
                _git(
                    repository,
                    "push",
                    "--porcelain",
                    "origin",
                    f"{candidate}:{_PLANNING}",
                )
        raise PublicationHold(
            "Planning report publication remains unverified after bounded retries"
        )
    finally:
        _git(repository, "update-ref", "-d", fetch_ref)


def _registration_exists(tree: _PlanningTree, story: int, data: dict) -> bool:
    path = f"{_story_root(story)}/events.jsonl"
    entry = tree.entry(path)
    if entry is None:
        raise PublicationHold("Cannot register a report without a story event stream")
    if entry[0] != b"100644":
        raise PublicationHold("Expected a normal story event stream")
    raw = tree.blob(entry[1])
    if raw and not raw.endswith(b"\n"):
        raise PublicationHold("Expected a newline-terminated story event stream")
    exists = False
    expected = canonical(data)
    try:
        for line in raw.splitlines():
            event = json.loads(line, object_pairs_hook=_unique_fields)
            if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
                raise ValueError("Invalid event")
            claim = event["data"]
            if claim.get("kind") != _REGISTRATION_KIND or not (
                claim.get("report_id") == data["report_id"]
                or claim.get("path") == data["path"]
            ):
                continue
            actor = event.get("actor")
            provenance = event.get("provenance")
            if (
                event.get("type") != "core.evidence.recorded"
                or not isinstance(actor, dict)
                or actor.get("kind") not in ("agent", "human", "tool")
                or not isinstance(actor.get("on-behalf-of"), str)
                or not _OPERATOR.fullmatch(actor["on-behalf-of"])
                or not isinstance(provenance, dict)
                or provenance.get("route") != "manual-bootstrap"
                or provenance.get("runtime_transition") is not False
                or _utc(event.get("ts")) < _utc(data["cutoff_utc"])
                or type(event.get("v")) is not int
                or event["v"] != 0
                or type(event.get("story")) is not int
                or event["story"] != story
                or canonical(claim) != expected
            ):
                raise PublicationHold("Refused conflicting pinned report registration")
            exists = True
    except PublicationHold:
        raise
    except (ValueError, RecursionError) as error:
        raise PublicationHold("Invalid pinned story event stream") from error
    return exists


def prepare_report_registration(
    repository: Path,
    authorized_remote: str,
    envelope: bytes,
    artifact_commit: str,
    *,
    operator_ref: str,
    recorded_at_utc: str,
) -> dict | None:
    """Prepare one registration fact from authorized readback, without writing."""
    report = validate_envelope(envelope)
    manifest = report["manifest"]
    story = manifest["story"]
    report_id = report["report_id"]
    path = report_path(story, report_id)
    cutoff = manifest["window"]["cutoff_utc"]
    try:
        time_is_valid = _utc(recorded_at_utc) >= _utc(cutoff)
    except ValueError:
        time_is_valid = False
    if (
        not isinstance(operator_ref, str)
        or not _OPERATOR.fullmatch(operator_ref)
        or not time_is_valid
    ):
        raise PublicationHold("Invalid report registration operator or recording time")
    data = {
        "kind": _REGISTRATION_KIND,
        "scope": {"project": manifest["project"], "story": story},
        "report_id": report_id,
        "artifact_commit": artifact_commit,
        "path": path.removeprefix(f"{_story_root(story)}/"),
        "sha256": sha256(envelope).hexdigest(),
        "planning_commit": manifest["planning_commit"],
        "window": manifest["window"],
        "cutoff_utc": cutoff,
        "rate_sha256": manifest["rate_sha256"],
    }
    fetch_ref = f"refs/aitm/pinned-report-publication/{uuid4().hex}"
    try:
        tip = _remote_tip(repository, authorized_remote, fetch_ref)
        if tip is None:
            raise PublicationHold("Cannot verify planning report registration readback")
        _require_ancestor(repository, manifest["planning_commit"], tip)
        _require_ancestor(repository, artifact_commit, tip)
        tree = _PlanningTree(repository, tip)
        _validate_tree(tree, story, path)
        _require_bytes(tree, path, envelope, "Report registration readback mismatch")
        if _artifact_commit(repository, tip, path, present=True) != artifact_commit:
            raise PublicationHold("Report artifact readback commit mismatch")
        _require_ancestor(repository, manifest["planning_commit"], artifact_commit)
        _require_bytes(
            _PlanningTree(repository, artifact_commit),
            path,
            envelope,
            "Report artifact readback mismatch",
        )
        if _registration_exists(tree, story, data):
            return None
        return {
            "v": 0,
            "type": "core.evidence.recorded",
            "ts": recorded_at_utc,
            "story": story,
            "actor": {"kind": "agent", "on-behalf-of": operator_ref},
            "provenance": {"route": "manual-bootstrap", "runtime_transition": False},
            "data": data,
        }
    finally:
        _git(repository, "update-ref", "-d", fetch_ref)
