"""Freeze and reopen a versioned story report at exact immutable Git pins."""

import json
import re
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import PurePosixPath
from uuid import UUID

from ..types import _unique_fields
from .export import render_export
from .session_publication import PublicationHold, _PlanningTree, _read
from .store import EffortError

_REPORT_SCHEMA = "aitm.story-effort-report/v1"
_RENDERER = "story-effort-text/v1"
MAX_ENVELOPE = 16 * 1024 * 1024
_DIGEST = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_TOKEN = re.compile(r"[A-Za-z0-9_.:+-]{1,192}")
_TEXT = re.compile(r"[A-Za-z0-9_.:# (),+%\n-]+")
_WINDOW_FIELDS = ("window_start_utc", "window_end_utc", "cutoff_utc")
_TOKEN_FIELDS = ("cached_input", "new_input", "output")


class ReportUnavailable(EffortError):
    """A syntactically valid reopen request cannot recover its exact report."""


def canonical(value: object) -> bytes:
    return render_export(value).encode("ascii")


def _sha(value: bytes) -> str:
    return sha256(value).hexdigest()


def _fields(value, names: set[str]) -> None:
    if type(value) is not dict or set(value) != names:
        raise EffortError("Unexpected pinned report fields")


def _match(pattern, value) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _scope(story: int) -> str:
    if type(story) is not int or not 1 <= story < 2**63:
        raise EffortError("Story must be a positive integer")
    return f".aitm/stories/{story // 100:03d}/{story}"


def report_path(story: int, report_id: str) -> str:
    if not _match(_DIGEST, report_id):
        raise EffortError("Report ID must be an exact SHA-256")
    return f"{_scope(story)}/attachments/effort/reports/{report_id}.json"


def require_commit(commit: str) -> None:
    if not _match(_COMMIT, commit):
        raise EffortError("Use a full immutable Git commit ID")


def check_window(value: dict) -> None:
    _fields(value, set(_WINDOW_FIELDS))
    moments = []
    for key in _WINDOW_FIELDS:
        timestamp = value[key]
        if not _match(_TOKEN, timestamp) or "T" not in timestamp:
            raise EffortError("Report window requires UTC timestamps")
        moment = datetime.fromisoformat(timestamp)
        if moment.utcoffset() != UTC.utcoffset(moment):
            raise EffortError("Report window requires UTC timestamps")
        moments.append(moment)
    if not moments[0] < moments[1] <= moments[2]:
        raise EffortError("Invalid report window or cutoff")


def _safe_value(value, story_root: str, depth: int = 0) -> None:
    if depth > 12:
        raise EffortError("Pinned report data is too deeply nested")
    if value is None or type(value) is bool:
        return
    if type(value) is int and 0 <= value < 2**100:
        return
    if isinstance(value, str):
        if _match(_TOKEN, value):
            return
        public = PurePosixPath(value)
        if (
            public.as_posix() == value
            and public.is_relative_to(story_root)
            and ".." not in public.parts
            and all(_match(_TOKEN, part) for part in public.parts)
        ):
            return
    if type(value) is list:
        for item in value:
            _safe_value(item, story_root, depth + 1)
        return
    if type(value) is dict and all(_match(_TOKEN, key) for key in value):
        for item in value.values():
            _safe_value(item, story_root, depth + 1)
        return
    raise EffortError("Unsafe or unsupported pinned report data")


def _check_evidence(inputs: dict, story_root: str) -> None:
    if not inputs:
        return
    _fields(inputs, {"receipts", "excluded", "coverage", "timing", "registration"})
    for group in ("receipts", "excluded", "coverage", "timing"):
        if type(inputs[group]) is not list:
            raise EffortError("Invalid pinned evidence list")
        for row in inputs[group]:
            names = {"path", "sha256"}
            if group in {"receipts", "excluded"}:
                names |= {"identity", "revision"}
            if group == "excluded":
                names.add("reason")
            _fields(row, names)
            _evidence_blob(row, story_root)
            if "identity" in row and (
                not _match(_DIGEST, row["identity"])
                or type(row["revision"]) is not int
                or row["revision"] < 1
                or not row["path"].endswith(
                    f"/{row['identity']}-r{row['revision']}.json"
                )
            ):
                raise EffortError("Invalid exact receipt descriptor")
            if "reason" in row and not _match(_TOKEN, row["reason"]):
                raise EffortError("Invalid exclusion reason")
    registration = inputs["registration"]
    if registration is not None:
        _fields(registration, {"path", "sha256"})
        _evidence_blob(registration, story_root)


def _evidence_blob(row: dict, story_root: str) -> None:
    if (
        type(row["path"]) is not str
        or not row["path"].startswith(f"{story_root}/")
        or not _match(_DIGEST, row["sha256"])
    ):
        raise EffortError("Invalid pinned evidence descriptor")
    _safe_value(row["path"], story_root)


def _check_manifest(manifest: dict) -> None:
    _fields(
        manifest,
        {"project", "story", "planning_commit", "window", "rate_sha256", "inputs"},
    )
    try:
        if str(UUID(manifest["project"])) != manifest["project"]:
            raise EffortError("Expected a canonical project UUID")
    except (AttributeError, TypeError, ValueError):
        raise EffortError("Expected a canonical project UUID") from None
    story_root = _scope(manifest["story"])
    require_commit(manifest["planning_commit"])
    check_window(manifest["window"])
    if (
        not _match(_DIGEST, manifest["rate_sha256"])
        or type(manifest["inputs"]) is not dict
    ):
        raise EffortError("Invalid rate or evidence pin")
    _check_evidence(manifest["inputs"], story_root)


def _check_report(report: dict, story: int) -> None:
    required = {"tokens", "api_estimate_usd", "cost_eligible", "cost_hold_reasons"}
    optional = {
        "token_coverage",
        "api_estimate_coverage",
        "api_price_basis",
        "provider_reported_grok_usd_ticks",
        "provider_reported_grok_coverage",
        "verified_billed_usd",
        "verified_billed_coverage",
        "coverage",
        "engagement_us",
        "engagement_coverage",
        "turns",
    }
    if type(report) is not dict or not required <= report.keys() <= required | optional:
        raise EffortError("Unexpected pinned report totals")
    _safe_value(report, _scope(story))
    _fields(report["tokens"], set(_TOKEN_FIELDS))
    if any(
        value is not None and type(value) is not int
        for value in report["tokens"].values()
    ):
        raise EffortError("Invalid report token totals")
    amount = report["api_estimate_usd"]
    if amount is not None and not _match(
        re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"), amount
    ):
        raise EffortError("Invalid report API equivalent")
    reasons = report["cost_hold_reasons"]
    if (
        type(report["cost_eligible"]) is not bool
        or type(reasons) is not list
        or any(not _match(_TOKEN, reason) for reason in reasons)
        or (report["cost_eligible"] and (reasons or amount is None))
    ):
        raise EffortError("Invalid report Cost disposition")


def _value(value) -> str:
    return "Unknown" if value is None else str(value)


def _coverage(value: dict | None) -> str:
    if not value:
        return ""
    return f" ({value['status']}, {_value(value['known_turns'])} known turns)"


def _render_text(manifest: dict, report: dict) -> str:
    """The v1 text is frozen into each envelope at build time."""
    window = manifest["window"]
    coverage = report.get("coverage", {})
    lines = [
        f"Story #{manifest['story']} effort and cost",
        f"Planning commit: {manifest['planning_commit']}",
        f"Occurrence: {window['window_start_utc']} to {window['window_end_utc']}",
        f"Observation cutoff: {window['cutoff_utc']}",
        f"Rate digest: {manifest['rate_sha256']}",
        f"Expected turns: {_value(coverage.get('expected_turns'))}",
        f"Measured turns: {_value(coverage.get('measured_turns'))}",
    ]
    for key in (
        "pending",
        "missing",
        "unavailable",
        "withdrawn",
        "disputed",
        "unattributed",
    ):
        lines.append(f"{key.capitalize()}: {_value(coverage.get(key))}")
    for key in _TOKEN_FIELDS:
        label = key.replace("_", " ").capitalize()
        lines.append(
            f"{label} tokens: {_value(report['tokens'][key])}"
            + _coverage(report.get("token_coverage", {}).get(key))
        )
    lines.extend(
        [
            f"Engagement microseconds: {_value(report.get('engagement_us'))}"
            + _coverage(report.get("engagement_coverage")),
            f"Grok provider reported USD ticks: {_value(report.get('provider_reported_grok_usd_ticks'))}"
            + _coverage(report.get("provider_reported_grok_coverage")),
            f"Standard API equivalent USD: {_value(report['api_estimate_usd'])}"
            + _coverage(report.get("api_estimate_coverage")),
            f"Verified billed USD: {_value(report.get('verified_billed_usd'))}"
            + _coverage(report.get("verified_billed_coverage")),
            "Project Cost: eligible"
            if report["cost_eligible"]
            else "Project Cost: held",
        ]
    )
    lines.extend(f"Cost hold: {reason}" for reason in report["cost_hold_reasons"])
    for turn in report.get("turns", []):
        lines.append(
            f"Turn {turn['identity']} revision {turn['revision']}: "
            f"{turn['provider']} {turn['role']}"
        )
    return "\n".join(lines) + "\n"


def _component_digests(manifest: dict, report: dict, text: str) -> dict:
    return {
        "manifest": _sha(canonical(manifest)),
        "report": _sha(canonical(report)),
        "text": _sha(text.encode("ascii")),
    }


def freeze_report(manifest: dict, report: dict) -> bytes:
    _check_manifest(manifest)
    _check_report(report, manifest["story"])
    text = _render_text(manifest, report)
    if not _match(_TEXT, text):
        raise EffortError("Invalid frozen report text")
    payload = {
        "schema": _REPORT_SCHEMA,
        "renderer": _RENDERER,
        "manifest": manifest,
        "report": report,
        "text": text,
        "digests": _component_digests(manifest, report, text),
    }
    raw = canonical(payload | {"report_id": _sha(canonical(payload))})
    if len(raw) > MAX_ENVELOPE:
        raise EffortError("Pinned report envelope exceeds its byte limit")
    return raw


def build_pinned_report(inputs, rates) -> bytes:
    from .pinned_amounts import summarize

    manifest = {
        "project": str(inputs.project),
        "story": inputs.story,
        "planning_commit": inputs.planning_commit,
        "window": inputs.window,
        "rate_sha256": rates.sha256,
        "inputs": inputs.manifest,
    }
    return freeze_report(manifest, summarize(inputs, rates))


def validate_envelope(raw: bytes, *, for_publication: bool = False) -> dict:
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_ENVELOPE:
        raise EffortError("Pinned report envelope exceeds its byte limit")
    try:
        envelope = json.loads(raw, object_pairs_hook=_unique_fields)
        _fields(
            envelope,
            {
                "schema",
                "renderer",
                "manifest",
                "report",
                "text",
                "digests",
                "report_id",
            },
        )
        if (
            envelope["schema"] != _REPORT_SCHEMA
            or envelope["renderer"] != _RENDERER
            or canonical(envelope) != raw
        ):
            raise EffortError("Unsupported or noncanonical pinned report")
        manifest, report, text = (
            envelope[key] for key in ("manifest", "report", "text")
        )
        _check_manifest(manifest)
        _check_report(report, manifest["story"])
        if not _match(_TEXT, text) or not text.endswith("\n"):
            raise EffortError("Invalid frozen report text")
        if for_publication and text != _render_text(manifest, report):
            raise EffortError("Report text does not match the producer renderer")
        if envelope["digests"] != _component_digests(manifest, report, text):
            raise EffortError("Frozen report component digest mismatch")
        payload = {key: value for key, value in envelope.items() if key != "report_id"}
        if envelope["report_id"] != _sha(canonical(payload)):
            raise EffortError("Pinned report identity mismatch")
        return envelope
    except (
        UnicodeError,
        json.JSONDecodeError,
        TypeError,
        RecursionError,
        OverflowError,
    ):
        raise EffortError("Invalid pinned report envelope") from None


def reopen_pinned_report(
    repo, artifact_commit: str, project: UUID, story: int, report_id: str
) -> dict:
    require_commit(artifact_commit)
    path = report_path(story, report_id)
    try:
        resolved = _read(repo, "rev-parse", "--verify", f"{artifact_commit}^{{commit}}")
        if resolved.decode("ascii").strip() != artifact_commit:
            raise ReportUnavailable("Pinned artifact commit unavailable")
        entry = _PlanningTree(repo, artifact_commit).entry(path)
        if entry is None:
            raise ReportUnavailable("Pinned report artifact missing")
        mode, blob = entry
        size = int(_read(repo, "cat-file", "-s", blob))
        if mode != b"100644" or not 0 < size <= MAX_ENVELOPE:
            raise ReportUnavailable("Pinned report artifact has invalid mode or size")
        envelope = validate_envelope(_read(repo, "cat-file", "blob", blob))
    except ReportUnavailable:
        raise
    except (PublicationHold, EffortError, ValueError):
        raise ReportUnavailable(
            "Pinned report artifact is unavailable or invalid"
        ) from None
    manifest = envelope["manifest"]
    if (
        envelope["report_id"] != report_id
        or manifest["project"] != str(project)
        or manifest["story"] != story
    ):
        raise ReportUnavailable("Pinned report identity or scope mismatch")
    return envelope
