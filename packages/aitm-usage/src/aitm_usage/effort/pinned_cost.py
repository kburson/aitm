"""Prepare the existing dashboard Cost receipt from an independently verified report."""

import json
import re
from hashlib import sha256

from .pinned_publication import _OID, _OPERATOR, _utc
from .pinned_report import validate_envelope

_COST_BASIS = "standard-api-equivalent"
_TOKEN_COLUMNS = ("cached_input", "new_input", "output")
_UNRESOLVED = (
    "pending",
    "unattributed",
    "missing",
    "unavailable",
    "withdrawn",
    "disputed",
)
_PUBLIC_REASON = re.compile(r"[a-z][a-z0-9_-]{0,95}")
_PRICE = re.compile(r"(?:0|[1-9][0-9]{0,19})(?:\.[0-9]{1,18})?")
_PROOF_FIELDS = {
    "operator_ref",
    "verified_at_utc",
    "source_report_id",
    "source_sha256",
    "verified_story",
    "project_uuid",
    "artifact_commit",
    "selector",
}


def _held(*reasons: str) -> dict:
    return {"status": "held", "reasons": list(reasons)}


def _verified_binding(
    report: dict, digest: str, selector: dict, verification: dict
) -> bool:
    manifest = report["manifest"]
    if not isinstance(selector, dict) or not isinstance(verification, dict):
        return False
    project = selector.get("project")
    expected_selector = {
        "project": project,
        "report_id": report["report_id"],
        "rate_card": manifest["rate_sha256"],
        "pricing_basis": _COST_BASIS,
        **manifest["window"],
    }
    if (
        not isinstance(project, str)
        or not _OPERATOR.fullmatch(project)
        or selector != expected_selector
        or verification.keys() != _PROOF_FIELDS
    ):
        return False
    operator = verification["operator_ref"]
    artifact_commit = verification["artifact_commit"]
    try:
        time_matches = _utc(verification["verified_at_utc"]) >= _utc(
            manifest["window"]["cutoff_utc"]
        )
    except ValueError:
        return False
    return (
        time_matches
        and isinstance(operator, str)
        and _OPERATOR.fullmatch(operator) is not None
        and isinstance(artifact_commit, str)
        and _OID.fullmatch(artifact_commit) is not None
        and verification["source_report_id"] == report["report_id"]
        and verification["source_sha256"] == digest
        and type(verification["verified_story"]) is int
        and verification["verified_story"] == manifest["story"]
        and verification["project_uuid"] == manifest["project"]
        and verification["selector"] == expected_selector
    )


def _complete_coverage(summary: dict) -> bool:
    coverage = summary.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("admission") != "closed":
        return False
    expected = coverage.get("expected_turns")
    if type(expected) is not int or expected < 0:
        return False
    for name in (*_UNRESOLVED, "sampled_attempts", "measured_turns"):
        value = coverage.get(name)
        if type(value) is not int or value != (0 if name in _UNRESOLVED else expected):
            return False

    def is_complete(evidence: object) -> bool:
        return (
            isinstance(evidence, dict)
            and evidence.get("status") == "complete"
            and type(evidence.get("known_turns")) is int
            and evidence["known_turns"] == expected
        )

    token_coverage = summary.get("token_coverage")
    return (
        summary.get("api_price_basis") == _COST_BASIS
        and is_complete(summary.get("api_estimate_coverage"))
        and isinstance(token_coverage, dict)
        and all(is_complete(token_coverage.get(name)) for name in _TOKEN_COLUMNS)
    )


def cost_candidate(
    envelope: bytes, selector: dict, operator_verification: dict
) -> dict:
    """Return a canonical #181 receipt candidate or an explicit hold.

    The caller independently checks the authorized operator and the protected
    report bytes before supplying their exact readback binding. This operation
    does not register the receipt or write to GitHub.
    """
    report = validate_envelope(envelope)
    summary = report["report"]
    reasons = summary["cost_hold_reasons"]
    if summary["cost_eligible"] is not True or reasons:
        if (
            isinstance(reasons, list)
            and reasons
            and all(
                isinstance(reason, str) and _PUBLIC_REASON.fullmatch(reason)
                for reason in reasons
            )
        ):
            return _held(*sorted(set(reasons)))
        return _held("incomplete-cost")
    digest = sha256(envelope).hexdigest()
    if not _verified_binding(report, digest, selector, operator_verification):
        return _held("unverified-cost-source")
    amount = summary["api_estimate_usd"]
    tokens = summary["tokens"]
    if (
        not _complete_coverage(summary)
        or not isinstance(amount, str)
        or not _PRICE.fullmatch(amount)
        or not isinstance(tokens, dict)
        or any(
            type(tokens.get(name)) is not int or tokens[name] < 0
            for name in _TOKEN_COLUMNS
        )
    ):
        return _held("invalid-complete-cost")
    usage = {
        "tokens": {name: tokens[name] for name in _TOKEN_COLUMNS},
        "priced_usd": amount,
    }
    usage_digest = sha256(
        json.dumps(
            usage, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()
    story = report["manifest"]["story"]
    batch = f"pinned-{report['report_id']}"
    observed = operator_verification["verified_at_utc"]
    receipt = {
        "schema": "aitm.story-usage-receipt/v1",
        "project": selector["project"],
        "subject": story,
        "batch": batch,
        "recorded_at_utc": observed,
        "source": {
            "ref": f"planning:{operator_verification['artifact_commit']}",
            "sha256": digest,
        },
        "selector": dict(selector),
        "usage": usage,
        "coverage": "complete",
        "verification": {
            "operator_ref": operator_verification["operator_ref"],
            "verified_at_utc": observed,
            "source_report_id": report["report_id"],
            "source_sha256": digest,
            "verified_story": story,
            "selector": dict(selector),
            "pricing_basis": _COST_BASIS,
            "coverage": "complete",
            "sanitized_data_sha256": usage_digest,
        },
    }
    return {
        "status": "eligible",
        "path": f"attachments/timing/{batch}-{story}.json",
        "receipt": receipt,
    }
