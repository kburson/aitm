"""Build a reproducible local dashboard snapshot from pinned planning evidence."""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .attribution import resolve_timing
from .evidence import STATES, TOKEN, Event, Gap, PlanningTree, read_tree
from .timing import DurationMeasure, StoryTiming, project_timing
from .usage import ReportSelector, UsageMeasure, select_usage

Snapshot = dict[str, Any]
SCHEMA = "aitm.story-dashboard/v1"
VALIDATION_SCHEMA = "aitm.story-dashboard-validation/v1"
REPOSITORY = "kburson/aitm"
GITHUB = f"https://github.com/{REPOSITORY}"
_COMMIT = re.compile(r"[0-9a-f]{40}")
_EVIDENCE = re.compile(
    r"(?P<path>\.aitm/stories/(?P<bucket>[0-9]{3,})/(?P<story>[1-9][0-9]*)/"
    r"(?:[A-Za-z0-9][A-Za-z0-9_.-]*/)*[A-Za-z0-9][A-Za-z0-9_.-]*)"
    r"(?::(?P<line>[1-9][0-9]*))?"
)
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
_DURATIONS = (
    "direct_actual",
    "descendant_actual",
    "actual",
    "working_wall",
    "direct_owner_wait",
    "owner_wait",
    "all_phase_elapsed",
    "implementation_elapsed",
    "all_phase_age",
    "implementation_age",
)


def _utc(stamp: datetime | None) -> str | None:
    return (
        None
        if stamp is None
        else stamp.astimezone(UTC).isoformat().replace("+00:00", "Z")
    )


def _canonical(value: dict) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def evidence_link(commit: str, source: str | None) -> str | None:
    """Link a canonical story-tree path, optionally with its journal line."""
    if not source or _COMMIT.fullmatch(commit) is None:
        return None
    match = _EVIDENCE.fullmatch(source)
    if match is None:
        return None
    path, story, bucket, line = (
        match[name] for name in ("path", "story", "bucket", "line")
    )
    if len(story) > 12 or f"{int(story) // 100:03d}" != bucket:
        return None
    if line is not None and (not path.endswith("/events.jsonl") or len(line) > 12):
        return None
    anchor = "" if line is None else f"#L{line}"
    return f"{GITHUB}/blob/{commit}/{path}{anchor}"


def _evidence(commit: str, path: str | None) -> dict[str, str | None]:
    return {"path": path, "url": evidence_link(commit, path)}


def _gap(commit: str, gap: Gap) -> dict:
    return {
        "story": gap.story,
        "code": gap.code,
        "evidence": _evidence(commit, gap.source),
    }


def _duration(commit: str, measure: DurationMeasure) -> dict:
    return {
        "milliseconds": measure.milliseconds,
        "coverage": measure.coverage,
        "evidence_through_utc": _utc(measure.evidence_through),
        "bases": list(measure.bases),
        "pending": measure.pending,
        "reasons": list(measure.reasons),
        "evidence": [
            _evidence(commit, source.path)
            | {
                "receipt_sha256": source.receipt_sha256,
                "source_ref": source.source_ref,
                "source_sha256": source.source_sha256,
                "reason": source.reason,
            }
            for source in measure.sources
        ],
    }


def _timing(commit: str, story: StoryTiming) -> dict:
    return {key: _duration(commit, getattr(story, key)) for key in _DURATIONS} | {
        "contributions": [
            {
                "story": row.scope.story,
                "project": row.scope.project,
                "actor": row.scope.actor,
                "phase": row.scope.phase,
                "role": row.scope.role,
                "attempt": row.scope.attempt,
                "milliseconds": row.milliseconds,
            }
            for row in story.contributions
        ],
        "calibration": {
            "eligible": story.calibration.eligible,
            "estimate_evidence": _evidence(commit, story.calibration.estimate_source),
            "reasons": list(story.calibration.reasons),
        },
    }


def _cost(commit: str, measure: UsageMeasure, sources: dict[str, dict]) -> dict:
    return {
        "priced_usd": None
        if measure.priced_usd is None
        else format(measure.priced_usd, "f"),
        "coverage": measure.coverage,
        "basis": measure.basis,
        "evidence_through_utc": _utc(measure.evidence_through),
        "receipt_digests": list(measure.receipt_digests),
        "evidence": [
            sources[digest] for digest in measure.receipt_digests if digest in sources
        ],
        "gaps": [_gap(commit, item) for item in measure.gaps],
    }


def _is_progress(event: Event) -> bool:
    if event.kind == "core.state.entered":
        state = event.data.get("state")
        return isinstance(state, str) and state in STATES
    if event.kind == "core.story.graduated":
        return event.data.get("issue") == f"{GITHUB}/issues/{event.story}"
    if event.kind == "core.doc.accepted":
        role, path, digest = (
            event.data.get(key) for key in ("role", "path", "raw_digest")
        )
        if not all(isinstance(value, str) for value in (role, path, digest)):
            return False
        match = _EVIDENCE.fullmatch(path)
        return bool(
            match
            and match["story"] == str(event.story)
            and match["bucket"] == f"{event.story // 100:03d}"
            and match["line"] is None
            and TOKEN.fullmatch(role)
            and _DIGEST.fullmatch(digest)
        )
    return False


def _last_progress(events: tuple[Event, ...]) -> dict[int, Event]:
    progress = {}
    for event in events:
        if not _is_progress(event):
            continue
        current = progress.get(event.story)
        if current is None or (event.timestamp, event.recorded_at) >= (
            current.timestamp,
            current.recorded_at,
        ):
            progress[event.story] = event
    return progress


def _estimate_bases(events: tuple[Event, ...]) -> dict[str, str]:
    bases = {}
    for event in events:
        if event.kind != "core.estimate.set":
            continue
        scope = event.data.get("scope")
        basis = scope.get("basis") if isinstance(scope, dict) else None
        if isinstance(basis, str) and TOKEN.fullmatch(basis):
            bases[event.source] = basis
    return bases


def _build(
    tree: PlanningTree, selector: ReportSelector | None
) -> tuple[Snapshot, dict]:
    facts = resolve_timing(tree)
    timing = project_timing(tree, facts)
    usage = select_usage(tree, selector)
    progress = _last_progress(tree.events)
    estimate_bases = _estimate_bases(tree.events)
    receipt_sources = {}
    for item in tree.registrations:
        if item.sha256 in usage.resolved_receipt_digests:
            path = f".aitm/stories/{item.story // 100:03d}/{item.story}/{item.path}"
            receipt_sources[item.sha256] = _evidence(tree.commit, path) | {
                "receipt_sha256": item.sha256
            }
    rows = []
    for number, story in sorted(tree.stories.items()):
        estimate = tree.estimates.get(number)
        event = progress.get(number)
        cost = usage.stories[number]
        rows.append(
            {
                "id": number,
                "title": story.title,
                "state": story.state,
                "parent": tree.parents.get(number),
                "descendants": list(tree.descendants.get(number, ())),
                "last_progress": None
                if event is None
                else {
                    "kind": event.kind,
                    "occurred_at_utc": _utc(event.timestamp),
                    "evidence": _evidence(tree.commit, event.source),
                },
                "estimate": None
                if estimate is None
                else {
                    "agent_hours": None
                    if estimate.agent_hours is None
                    else str(estimate.agent_hours),
                    "size": estimate.size,
                    "phase": estimate.phase,
                    "roles": None if estimate.roles is None else list(estimate.roles),
                    "basis": estimate_bases.get(estimate.source),
                    "evidence": _evidence(tree.commit, estimate.source),
                },
                "timing": _timing(tree.commit, timing[number]),
                "cost": {
                    "direct": _cost(tree.commit, cost.direct, receipt_sources),
                    "inclusive": _cost(tree.commit, cost.inclusive, receipt_sources),
                },
            }
        )
    planning = {
        "commit": tree.commit,
        "committed_at_utc": _utc(tree.commit_time),
        "as_of_utc": _utc(tree.as_of),
    }
    snapshot = {
        "schema": SCHEMA,
        "repository": REPOSITORY,
        "planning": planning,
        "usage_report": {
            "selector": None if usage.selector is None else usage.selector.to_dict(),
            "source_sha256": usage.source_sha256,
            "receipt_digests": list(usage.resolved_receipt_digests),
        },
        "stories": rows,
    }
    usage_gaps = {
        gap
        for row in usage.stories.values()
        for measure in (row.direct, row.inclusive)
        for gap in measure.gaps
    }
    validation = {
        "schema": VALIDATION_SCHEMA,
        "planning": planning,
        "input_gaps": [_gap(tree.commit, gap) for gap in facts.input_gaps],
        "timing_gaps": [
            {
                "story": gap.story,
                "code": gap.code,
                "start_ms": gap.start_ms,
                "end_ms": gap.end_ms,
                "evidence": [
                    _evidence(tree.commit, source.receipt_path)
                    for source in gap.sources
                ],
            }
            for gap in facts.gaps
        ],
        "usage_gaps": [
            _gap(tree.commit, gap)
            for gap in sorted(
                usage_gaps, key=lambda gap: (gap.story, gap.code, gap.source)
            )
        ],
    }
    return snapshot, validation


def build_snapshot(
    tree: PlanningTree, selector: ReportSelector | None = None
) -> Snapshot:
    """Serialize the timing and usage projections for one immutable planning view."""
    return _build(tree, selector)[0]


def _git_env() -> dict[str, str]:
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    return env | {
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_ALLOW_PROTOCOL": "",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }


def external_output_path(path: Path, repo: Path | None = None) -> Path:
    """Resolve an operator destination and reject paths in any Git checkout."""
    target = path.expanduser().resolve()
    ancestry = (target, *target.parents)
    for parent in ancestry:
        marker = parent / ".git"
        if marker.exists() or marker.is_symlink():
            raise ValueError("output must be outside any Git worktree")
    ancestor = next(parent for parent in ancestry if parent.is_dir())
    environment = _git_env()
    discovered = subprocess.run(
        [
            "git",
            "-C",
            str(ancestor),
            "rev-parse",
            "--is-inside-work-tree",
            "--is-bare-repository",
        ],
        env=environment,
        capture_output=True,
        check=False,
    )
    if discovered.returncode == 0 and b"true" in discovered.stdout.splitlines():
        raise ValueError(
            "output must be outside any Git worktree or repository storage"
        )
    if repo is not None:
        linked = subprocess.check_output(
            ["git", "-C", str(repo), "worktree", "list", "--porcelain", "-z"],
            env=environment,
            stderr=subprocess.PIPE,
        )
        for line in linked.split(b"\0"):
            if line.startswith(b"worktree "):
                root = Path(os.fsdecode(line.removeprefix(b"worktree "))).resolve()
                if target.is_relative_to(root):
                    raise ValueError("output must be outside any linked Git worktree")
    return target


@contextmanager
def _output_directory(directory: Path, repo: Path | None = None):
    fd = os.open(directory, os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if external_output_path(directory, repo) != directory or not os.path.samestat(
            os.fstat(fd), directory.stat(follow_symlinks=False)
        ):
            raise ValueError("output directory changed during validation")
        yield fd
    finally:
        os.close(fd)


def _replace_output(directory: int, name: str, data: bytes) -> None:
    temp = f".story-dashboard-{secrets.token_hex(16)}.tmp"
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, name, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        try:
            os.unlink(temp, dir_fd=directory)
        except FileNotFoundError:
            pass


def atomic_write(destination: Path, data: bytes) -> None:
    """Atomically replace a verified external output in its existing directory."""
    external_output_path(destination)
    directory = external_output_path(destination.parent)
    with _output_directory(directory) as fd:
        _replace_output(fd, destination.name, data)


def _unique_object(items: list[tuple[str, Any]]) -> dict:
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError("duplicate usage selector key")
        value[key] = item
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--usage-report", type=Path, metavar="SELECTOR_JSON")
    args = parser.parse_args(argv)
    try:
        selector = None
        if args.usage_report is not None:
            selector = ReportSelector.from_dict(
                json.loads(
                    args.usage_report.read_text(encoding="utf-8"),
                    object_pairs_hook=_unique_object,
                )
            )
        tree = read_tree(args.repo, args.commit, datetime.fromisoformat(args.as_of))
        directory = external_output_path(args.output, args.repo)
        snapshot_path, validation_path = (
            directory / "snapshot.json",
            directory / "validation.json",
        )
        for artifact in (snapshot_path, validation_path):
            external_output_path(artifact, args.repo)
            if artifact.exists() and not artifact.is_file():
                raise ValueError("snapshot and validation destinations must be files")
        snapshot, validation = _build(tree, selector)
        payload = _canonical(snapshot)
        validation["snapshot_sha256"] = hashlib.sha256(payload).hexdigest()
        report = _canonical(validation)
        directory.mkdir(parents=True, exist_ok=True)
        with _output_directory(directory, args.repo) as fd:
            for artifact in (snapshot_path, validation_path):
                external_output_path(artifact, args.repo)
            _replace_output(fd, snapshot_path.name, payload)
            _replace_output(fd, validation_path.name, report)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
