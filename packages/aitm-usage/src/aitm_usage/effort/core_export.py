"""Adapt an exact planning report to the existing Core usage fixture wire."""

import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from hmac import digest
from pathlib import Path
from uuid import UUID

from ..types import (
    Availability,
    Provider,
    WorkPhase,
    normalize_client_version,
    normalize_model,
)
from .pinned_amounts import load_comparison_rates
from .pinned_coverage import utc_stamp
from .pinned_inputs import read_inputs
from .pinned_report import (
    ReportUnavailable,
    build_pinned_report,
    canonical,
    reopen_pinned_report,
)
from .store import EffortError

MAX_BUNDLE_BYTES = 32 << 20
_BUNDLE_FILES = ("manifest.json", "usage.jsonl", "provenance.json")
_FIXTURE_PRICE = re.compile(r"(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{0,12}[1-9])?")
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_WIRE_TIMESTEP = timedelta(microseconds=1)
_APPROVED_PROVIDERS = frozenset(Provider)


def _public_hmac(value: str) -> str:
    return "hmac-sha256:" + value


def _scope(receipt, authority, key):
    if authority is None:
        return None
    phase, actor = authority
    phase = WorkPhase.DEVELOPMENT if phase == "implement" else phase
    if phase not in WorkPhase:
        return None
    project, story, source, attempt = (
        receipt[field] for field in ("project", "story", "identity", "attempt")
    )

    def reference(domain, values):
        return _public_hmac(
            digest(key, canonical([domain, project, *values]), "sha256").hex()
        )

    participant = reference("core-export-participant/v1", [actor])
    assertion = reference(
        "core-export-scope/v1", [story, source, attempt, str(phase), participant]
    )
    return {
        "revision": {"source": assertion, "number": 1},
        "item": {"kind": "issue", "id": story},
        "phase": str(phase),
        "participant_ref": participant,
        "role": None,
        "attempt_ref": _public_hmac(attempt),
        "review_ref": None,
    }


def _wire_row(receipt, turn, authority, key, rate_basis):
    availability = receipt["coverage"]
    if availability == Availability.COMPLETE and (
        receipt["outcome"] != "completed"
        or any(
            receipt["tokens"][field] is None
            for field in ("input_tokens", "cached_input_tokens", "output_tokens")
        )
    ):
        availability = Availability.PARTIAL
    scope = _scope(receipt, authority, key)
    amount = turn["api_estimate_usd"]
    price_gap = turn["api_estimate_gap"]
    if amount is not None and _FIXTURE_PRICE.fullmatch(amount) is None:
        amount, price_gap = None, "v1-price-precision"
    if availability != Availability.COMPLETE:
        amount, price_gap = None, price_gap or "incomplete-usage"
    return {
        "source": _public_hmac(receipt["identity"]),
        "observation_revision": receipt["revision"],
        "provider": receipt["provider"],
        "boundary_kind": "turn",
        "observed_at": utc_stamp(receipt["observed_at"]).isoformat(),
        "client_version": normalize_client_version(receipt["version"]),
        "format_version": 1,
        "model": normalize_model(receipt["model"]),
        "effort": None,
        "processing_tier": None,
        "availability": availability,
        "tokens": receipt["tokens"],
        "scope_availability": "complete" if scope is not None else "unknown",
        "scope": scope,
        "price": {
            "availability": "complete" if amount is not None else "unknown",
            "currency": "USD",
            "rate_basis": rate_basis,
            "usd": amount,
        },
    }, price_gap


def _project(inputs, report, key, rate_basis):
    counts = Counter(dict.fromkeys(Availability, 0))
    rows = []
    provenance = []
    authority = {
        attempt: (phase, actor) for attempt, phase, actor in inputs.scope_authority
    }
    turns = {(turn["identity"], turn["revision"]): turn for turn in report["turns"]}
    descriptors = {
        (row["identity"], row["revision"]): row["sha256"]
        for row in inputs.manifest["receipts"]
    }
    for receipt in inputs.receipts:
        identity = (receipt["identity"], receipt["revision"])
        turn = turns[identity]
        evidence = {
            "source": _public_hmac(identity[0]),
            "revision": identity[1],
            "receipt_sha256": descriptors[identity],
            "model": receipt["model"],
            "client_version": receipt["version"],
            "provider": receipt["provider"],
        }
        exclusion = turn["exclusion"]
        if receipt["provider"] not in _APPROVED_PROVIDERS:
            reason = "unsupported-provider"
        elif exclusion == "unproved-disjoint-scope":
            reason = None
        else:
            reason = exclusion
        if reason is not None:
            provenance.append(evidence | {"status": "held", "reason": reason})
            continue
        scope = authority.get(receipt["attempt"]) if exclusion is None else None
        row, price_gap = _wire_row(receipt, turn, scope, key, rate_basis)
        raw = canonical(row)
        rows.append((row["source"], raw))
        counts[row["availability"]] += 1
        compatible = row["scope"] is not None and row["availability"] == "complete"
        provenance.append(
            evidence
            | {
                "status": "compatible" if compatible else "pending",
                "reason": exclusion
                or (
                    "scope-unknown"
                    if row["scope"] is None
                    else None
                    if compatible
                    else "incomplete-usage"
                ),
                "price_gap": price_gap,
                "row_sha256": sha256(raw[:-1]).hexdigest(),
            }
        )
    omissions = Counter()
    for row in inputs.manifest["excluded"]:
        reason = row["reason"]
        if reason in {"outside-window", "after-cutoff"}:
            omissions[reason] += 1
        else:
            provenance.append(
                {
                    "source": _public_hmac(row["identity"]),
                    "revision": row["revision"],
                    "receipt_sha256": row["sha256"],
                    "status": "held",
                    "reason": reason,
                }
            )
    provenance.sort(key=lambda row: (row["source"], row["revision"]))
    return b"".join(raw for _, raw in sorted(rows)), counts, provenance, dict(omissions)


def build_core_export(
    repository: Path,
    artifact_commit: str,
    project: UUID,
    story: int,
    report_id: str,
    rate_card: Path,
    scope_key: bytes,
) -> dict[str, bytes]:
    """Build fixture-compatible files from the exact, reproduced report inputs."""
    if type(scope_key) is not bytes or len(scope_key) != 32:
        raise EffortError("Expected exactly 32 bytes for the Core export scope key")
    try:
        envelope = reopen_pinned_report(
            repository, artifact_commit, project, story, report_id
        )
    except ReportUnavailable:
        raise EffortError("Pinned report unavailable for Core export") from None
    manifest = envelope["manifest"]
    inputs = read_inputs(
        repository, project, story, manifest["planning_commit"], manifest["window"]
    )
    rates = load_comparison_rates(rate_card, manifest["rate_sha256"])
    original = canonical(envelope)
    if original != build_pinned_report(inputs, rates):
        raise EffortError(
            "Could not reproduce the pinned report from its planning inputs"
        )
    report = envelope["report"]
    cutoff = (utc_stamp(inputs.window["cutoff_utc"]) - _EPOCH) // _WIRE_TIMESTEP
    if cutoff < 0:
        raise EffortError("Core export cutoff predates the Unix epoch")
    basis = f"standard-api-USD:{rates.version}:sha256:{rates.sha256}"
    data, counts, rows, omissions = _project(inputs, report, scope_key, basis)
    wire = canonical(
        {
            "schema": "aitm.usage.export/v1",
            "project_id": str(project),
            "cutoff": cutoff,
            "rate_basis": basis,
            "sha256": sha256(data).hexdigest(),
            "row_count": sum(counts.values()),
            "coverage": counts,
            "diagnostics": [],
        }
    )
    provenance = canonical(
        {
            "schema": "aitm.story-core-export-provenance/v1",
            "project": str(project),
            "story": story,
            "report_id": report_id,
            "artifact_commit": artifact_commit,
            "planning_commit": inputs.planning_commit,
            "report_sha256": sha256(original).hexdigest(),
            "window": inputs.window,
            "rate_sha256": rates.sha256,
            "wire_sha256": {
                "manifest.json": sha256(wire).hexdigest(),
                "usage.jsonl": sha256(data).hexdigest(),
            },
            "coverage": report["coverage"],
            "cost_eligible": report["cost_eligible"],
            "cost_hold_reasons": report["cost_hold_reasons"],
            "api_estimate_usd": report["api_estimate_usd"],
            "api_price_basis": report["api_price_basis"],
            "omitted_counts": omissions,
            "rows": rows,
        }
    )
    return dict(zip(_BUNDLE_FILES, (wire, data, provenance), strict=True))


def render_core_bundle(files: dict[str, bytes]) -> bytes:
    bundle = canonical(
        {
            "schema": "aitm.story-core-export-bundle/v1",
            "files": {name: files[name].decode("utf-8") for name in _BUNDLE_FILES},
        }
    )
    if len(bundle) > MAX_BUNDLE_BYTES:
        raise EffortError("Core export bundle exceeds its byte limit")
    return bundle
