"""Render a pinned story dashboard snapshot as one offline HTML file."""

import argparse
import base64
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .evidence import COVERAGES, STATES, UTC_STAMP
from .snapshot import (
    GITHUB,
    REPOSITORY,
    SCHEMA,
    Snapshot,
    atomic_write,
    evidence_link,
    external_output_path,
)
from .usage import ReportSelector

_COMMIT = re.compile(r"[0-9a-f]{40}")
_ISSUE = re.compile(rf"/{REPOSITORY}/issues/[1-9][0-9]{{0,11}}")
_TEMPLATE = Path(__file__).with_name("dashboard.html")
_MEASURES = (
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


def _story_id(value: object) -> bool:
    return type(value) is int and 1 <= value < 10**12


def _is_utc(value: object) -> bool:
    if not isinstance(value, str) or UTC_STAMP.fullmatch(value) is None:
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate(snapshot: Snapshot) -> str:
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise ValueError("expected an A05 story dashboard v1 snapshot")
    if snapshot.get("repository") != REPOSITORY:
        raise ValueError("snapshot repository must match the AITM repository")
    planning = snapshot.get("planning")
    pin = planning.get("commit") if isinstance(planning, dict) else None
    if not isinstance(pin, str) or _COMMIT.fullmatch(pin) is None:
        raise ValueError("snapshot planning commit must be a full lowercase 40-hex pin")
    if not all(_is_utc(planning.get(key)) for key in ("committed_at_utc", "as_of_utc")):
        raise ValueError("snapshot planning timestamps must be UTC")
    usage = snapshot.get("usage_report")
    if (
        not isinstance(usage, dict)
        or "selector" not in usage
        or not (usage["selector"] is None or isinstance(usage["selector"], dict))
    ):
        raise ValueError("snapshot must contain the A05 usage report")
    if usage["selector"] is not None:
        ReportSelector.from_dict(usage["selector"])

    rows = snapshot.get("stories")
    if not isinstance(rows, list):
        raise ValueError("snapshot stories must be a list")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not _story_id(row.get("id")):
            raise ValueError("snapshot story must have a canonical numeric ID")
        if row["id"] in seen:
            raise ValueError("snapshot has duplicate story IDs")
        seen.add(row["id"])
        state = row.get("state")
        if not isinstance(row.get("title"), str) or (
            state is not None and (not isinstance(state, str) or state not in STATES)
        ):
            raise ValueError("snapshot story must have an A05 title and state")
        progress = row.get("last_progress")
        if progress is not None and (
            not isinstance(progress, dict)
            or not isinstance(progress.get("kind"), str)
            or not _is_utc(progress.get("occurred_at_utc"))
        ):
            raise ValueError("snapshot story has invalid progress evidence")
        estimate = row.get("estimate")
        if estimate is not None and (
            not isinstance(estimate, dict)
            or (
                estimate.get("agent_hours") is not None
                and not isinstance(estimate["agent_hours"], str)
            )
        ):
            raise ValueError("snapshot story has an invalid estimate")
        _validate_measures(row)
    for row in rows:
        children = row.get("descendants")
        parent = row.get("parent")
        if (
            not isinstance(children, list)
            or any(not _story_id(child) or child not in seen for child in children)
            or len(set(children)) != len(children)
            or row["id"] in children
            or (
                parent is not None
                and (not _story_id(parent) or parent not in seen or parent == row["id"])
            )
        ):
            raise ValueError("snapshot story has invalid ancestry")
        for contribution in row["timing"]["contributions"]:
            if contribution["story"] not in seen:
                raise ValueError(
                    "timing contribution story is absent from the snapshot"
                )
    return pin


def _validate_measures(row: dict) -> None:
    timing, cost = row.get("timing"), row.get("cost")
    if not isinstance(timing, dict) or not isinstance(cost, dict):
        raise ValueError("snapshot story is missing timing or Cost measures")
    contributions = timing.get("contributions")
    if not isinstance(contributions, list) or any(
        not isinstance(item, dict) or not _story_id(item.get("story"))
        for item in contributions
    ):
        raise ValueError("timing contributions must have canonical story IDs")
    measures = [timing.get(name) for name in _MEASURES]
    measures += [cost.get(name) for name in ("direct", "inclusive")]
    for item in measures:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("coverage"), str)
            or (item["coverage"] not in COVERAGES)
        ):
            raise ValueError("snapshot story has invalid measure coverage")
        through = item.get("evidence_through_utc")
        if through is not None and not _is_utc(through):
            raise ValueError("measure evidence-through must be UTC")
    for measure in measures[: len(_MEASURES)]:
        ms = measure.get("milliseconds")
        if ms is not None and (type(ms) is not int or not 0 <= ms <= 2**53 - 1):
            raise ValueError("timing must contain nonnegative integer milliseconds")
    for measure in measures[len(_MEASURES) :]:
        price = measure.get("priced_usd")
        if price is not None and (
            not isinstance(price, str)
            or re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", price) is None
        ):
            raise ValueError("Cost must contain an exact nonnegative decimal string")


def _approved_link(url: object, path: object, pin: str) -> str | None:
    if not isinstance(url, str) or any(
        not 33 <= ord(char) <= 126 or char in "%\\?" for char in url
    ):
        return None
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if (
        parts.scheme != "https"
        or parts.netloc != "github.com"
        or not url.startswith(f"{GITHUB}/")
    ):
        return None
    if _ISSUE.fullmatch(parts.path):
        return url if url == f"https://github.com{parts.path}" else None
    expected = evidence_link(pin, path) if isinstance(path, str) else None
    return url if url == expected else None


def _for_display(value, pin: str):
    if isinstance(value, list):
        return [_for_display(item, pin) for item in value]
    if isinstance(value, dict):
        return {
            key: _approved_link(item, value.get("path"), pin)
            if key == "url"
            else _for_display(item, pin)
            for key, item in value.items()
        }
    return value


def _inline_hash(template: str, tag: str) -> str:
    content = template.split(f"<{tag}>", 1)[1].split(f"</{tag}>", 1)[0]
    digest = hashlib.sha256(content.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


def render(snapshot: Snapshot) -> str:
    """Render A05 values without performing another timing or price projection."""
    pin = _validate(snapshot)
    payload = json.dumps(
        _for_display(snapshot, pin),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    template = _TEMPLATE.read_text(encoding="utf-8")
    return (
        template.replace("@@SCRIPT_HASH@@", _inline_hash(template, "script"), 1)
        .replace("@@STYLE_HASH@@", _inline_hash(template, "style"), 1)
        .replace("@@SNAPSHOT@@", payload, 1)
    )


def _unique_object(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("snapshot contains duplicate JSON keys")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.snapshot.expanduser().resolve()
        target = external_output_path(args.output)
        if source == target or (target.exists() and target.samefile(source)):
            raise ValueError("dashboard output cannot replace its input snapshot")
        data = json.loads(
            source.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
        )
        html = render(data)
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, html.encode("utf-8"))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
