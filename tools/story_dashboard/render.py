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
_SHA256 = re.compile(r"[0-9a-f]{64}")
_PRICE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
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


def _object(value: object, label: str, required: str, optional: str = "") -> dict:
    expected = set(required.split())
    if not isinstance(value, dict) or not expected <= value.keys() <= expected | set(
        optional.split()
    ):
        raise ValueError(f"unexpected fields in snapshot {label}")
    return value


def _optional_text(value: object) -> bool:
    return value is None or isinstance(value, str)


def _array(value: object, label: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"snapshot {label} must be an array")
    return value


def _text_array(value: object, label: str) -> None:
    if any(not isinstance(item, str) for item in _array(value, label)):
        raise ValueError(f"snapshot {label} must contain only text")


def _digests(value: object, label: str) -> None:
    if any(
        not isinstance(item, str) or _SHA256.fullmatch(item) is None
        for item in _array(value, label)
    ):
        raise ValueError(f"snapshot {label} must contain SHA-256 digests")


def _millis(value: object) -> bool:
    return type(value) is int and 0 <= value <= 2**53 - 1


def _validate_evidence(value: object) -> None:
    item = _object(
        value, "evidence", "path url", "receipt_sha256 source_ref source_sha256 reason"
    )
    if not all(
        _optional_text(item.get(key)) for key in ("path", "url", "source_ref", "reason")
    ):
        raise ValueError("snapshot evidence fields must be text or null")
    for key in ("receipt_sha256", "source_sha256"):
        digest = item.get(key)
        if digest is not None and (
            not isinstance(digest, str) or _SHA256.fullmatch(digest) is None
        ):
            raise ValueError("snapshot evidence digest must be SHA-256 or null")


def _validate_measure(value: object, *, is_cost: bool) -> None:
    common = "coverage evidence_through_utc evidence"
    fields = (
        "priced_usd basis receipt_digests gaps"
        if is_cost
        else "milliseconds bases pending reasons"
    )
    item = _object(value, "measure", f"{common} {fields}")
    if not isinstance(item["coverage"], str) or item["coverage"] not in COVERAGES:
        raise ValueError("snapshot story has invalid measure coverage")
    through = item["evidence_through_utc"]
    if through is not None and not _is_utc(through):
        raise ValueError("measure evidence-through must be UTC")
    for ref in _array(item["evidence"], "evidence"):
        _validate_evidence(ref)
    if is_cost:
        price = item["priced_usd"]
        if price is not None and (
            not isinstance(price, str) or _PRICE.fullmatch(price) is None
        ):
            raise ValueError("Cost must contain an exact nonnegative decimal string")
        if not _optional_text(item["basis"]):
            raise ValueError("snapshot Cost basis must be text or null")
        _digests(item["receipt_digests"], "Cost receipt digests")
        for value in _array(item["gaps"], "Cost gaps"):
            gap = _object(value, "Cost gap", "story code evidence")
            if not _story_id(gap["story"]) or not isinstance(gap["code"], str):
                raise ValueError("snapshot Cost gap must have a story ID and text code")
            _validate_evidence(gap["evidence"])
    else:
        ms = item["milliseconds"]
        if (ms is not None and not _millis(ms)) or not isinstance(
            item["pending"], bool
        ):
            raise ValueError(
                "snapshot timing requires integer milliseconds or null and a pending flag"
            )
        _text_array(item["bases"], "timing bases")
        _text_array(item["reasons"], "timing reasons")


def _validate_story(value: object) -> None:
    row = _object(
        value,
        "story",
        "id title state parent descendants last_progress estimate timing cost",
    )
    if not _story_id(row["id"]):
        raise ValueError("snapshot story must have a canonical numeric ID")
    state = row["state"]
    if not isinstance(row["title"], str) or (
        state is not None and (not isinstance(state, str) or state not in STATES)
    ):
        raise ValueError("snapshot story must have an A05 title and state")
    if row["last_progress"] is not None:
        progress = _object(
            row["last_progress"], "progress", "kind occurred_at_utc evidence"
        )
        if not isinstance(progress["kind"], str) or not _is_utc(
            progress["occurred_at_utc"]
        ):
            raise ValueError("snapshot story has invalid progress evidence")
        _validate_evidence(progress["evidence"])
    if row["estimate"] is not None:
        estimate = _object(
            row["estimate"], "estimate", "agent_hours size phase roles basis evidence"
        )
        if not all(
            _optional_text(estimate[key])
            for key in ("agent_hours", "size", "phase", "basis")
        ):
            raise ValueError("snapshot story has an invalid estimate")
        if estimate["roles"] is not None:
            _text_array(estimate["roles"], "estimate roles")
        _validate_evidence(estimate["evidence"])
    timing = _object(
        row["timing"], "timing", " ".join((*_MEASURES, "contributions", "calibration"))
    )
    for name in _MEASURES:
        _validate_measure(timing[name], is_cost=False)
    for value in _array(timing["contributions"], "timing contributions"):
        item = _object(
            value, "contribution", "story project actor phase role attempt milliseconds"
        )
        if (
            not _story_id(item["story"])
            or not _millis(item["milliseconds"])
            or not all(
                _optional_text(item[key])
                for key in ("project", "actor", "phase", "role", "attempt")
            )
        ):
            raise ValueError(
                "snapshot timing contribution has invalid identity or amount"
            )
    calibration = _object(
        timing["calibration"], "calibration", "eligible estimate_evidence reasons"
    )
    if not isinstance(calibration["eligible"], bool):
        raise ValueError("snapshot calibration eligibility must be boolean")
    _text_array(calibration["reasons"], "calibration reasons")
    _validate_evidence(calibration["estimate_evidence"])
    cost = _object(row["cost"], "Cost", "direct inclusive")
    for item in cost.values():
        _validate_measure(item, is_cost=True)


def _validate(snapshot: Snapshot) -> str:
    _object(snapshot, "document", "schema repository planning usage_report stories")
    if snapshot["schema"] != SCHEMA:
        raise ValueError("expected an A05 story dashboard v1 snapshot")
    if snapshot["repository"] != REPOSITORY:
        raise ValueError("snapshot repository must match the AITM repository")
    planning = _object(
        snapshot["planning"], "planning", "commit committed_at_utc as_of_utc"
    )
    pin = planning["commit"]
    if not isinstance(pin, str) or _COMMIT.fullmatch(pin) is None:
        raise ValueError("snapshot planning commit must be a full lowercase 40-hex pin")
    if not all(_is_utc(planning[key]) for key in ("committed_at_utc", "as_of_utc")):
        raise ValueError("snapshot planning timestamps must be UTC")
    usage = _object(
        snapshot["usage_report"],
        "usage report",
        "selector source_sha256 receipt_digests",
    )
    if usage["selector"] is not None:
        ReportSelector.from_dict(usage["selector"])
    if usage["source_sha256"] is not None:
        _digests([usage["source_sha256"]], "usage source digest")
    _digests(usage["receipt_digests"], "usage receipt digests")

    rows = _array(snapshot["stories"], "stories")
    seen = set()
    for row in rows:
        _validate_story(row)
        if row["id"] in seen:
            raise ValueError("snapshot has duplicate story IDs")
        seen.add(row["id"])
    for row in rows:
        children = _array(row["descendants"], "descendants")
        parent = row["parent"]
        if (
            any(not _story_id(child) or child not in seen for child in children)
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
    """Copy validated v1 data and clear rejected evidence destinations."""
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
