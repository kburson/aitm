"""Canonical report serialization and a read-only legacy usage export view."""

import json
import re
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from ..types import (
    Availability,
    Currency,
    Provider,
    RateBasis,
    TokenCounts,
    _unique_fields,
)
from .store import EffortError

LEGACY_SCHEMA = "aitm.usage.export/v1"
REPORT_SCHEMA = "aitm.effort.report/v1"


def render_export(report: dict) -> str:
    """Render one fixed report as a portable, newline-terminated JSON document."""
    return (
        json.dumps(
            report,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    )


@dataclass(frozen=True, slots=True)
class LegacyRow:
    source: str
    observation_revision: int
    provider: Provider
    availability: Availability
    observed_tokens: int | None
    estimated_usd: str | None
    rate_basis: str


@dataclass(frozen=True, slots=True)
class LegacySnapshot:
    project_id: UUID
    cutoff: int
    rate_basis: str
    sha256: str
    rows: tuple[LegacyRow, ...]
    schema: str = LEGACY_SCHEMA


def _count(value: object, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value < 2**63:
        raise ValueError("Invalid export count")
    return value


def _row(row: dict, basis: str) -> LegacyRow:
    source = row["source"]
    if not re.fullmatch(r"hmac-sha256:[a-f0-9]{64}", source):
        raise ValueError("Invalid legacy source")
    availability = Availability(row["availability"])
    tokens = TokenCounts(**row["tokens"])
    price = row["price"]
    if price["rate_basis"] != basis or price["currency"] != Currency.USD:
        raise ValueError("Legacy rate basis differs from the manifest")
    price_availability = Availability(price["availability"])
    estimate = price["usd"]
    if price_availability == Availability.COMPLETE:
        if availability != Availability.COMPLETE or not re.fullmatch(
            r"(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{0,12}[1-9])?", estimate
        ):
            raise ValueError("Invalid legacy estimate")
    elif price_availability != Availability.UNKNOWN or estimate is not None:
        raise ValueError("Invalid legacy estimate availability")
    return LegacyRow(
        source,
        _count(row["observation_revision"], 1),
        Provider(row["provider"]),
        availability,
        tokens.total_tokens,
        estimate,
        basis,
    )


def read_legacy(directory: Path, project_id: UUID) -> LegacySnapshot:
    """Read an approved v1 export, validating the fields used by the report.

    The digest detects byte changes. Approval of the source and authorization
    to read it belong to the caller. Legacy identities are retained as issued.
    """
    try:
        manifest = json.loads(
            (directory / "manifest.json").read_bytes(), object_pairs_hook=_unique_fields
        )
        if manifest["schema"] != LEGACY_SCHEMA or manifest["project_id"] != str(
            project_id
        ):
            raise ValueError("Unexpected legacy schema or project")
        cutoff = _count(manifest["cutoff"])
        basis = manifest["rate_basis"]
        match = re.fullmatch(
            r"standard-api-USD:([0-9-]{10}):sha256:([a-f0-9]{64})", basis
        )
        if match is None:
            raise ValueError("Invalid legacy rate basis")
        RateBasis(*match.groups(), Currency.USD)
        data = (directory / "usage.jsonl").read_bytes()
        digest = sha256(data).hexdigest()
        if digest != manifest["sha256"] or (data and not data.endswith(b"\n")):
            raise ValueError("Invalid legacy usage bytes")
        rows = tuple(
            _row(json.loads(line, object_pairs_hook=_unique_fields), basis)
            for line in data.split(b"\n")[:-1]
        )
        sources = [row.source for row in rows]
        if sources != sorted(set(sources)):
            raise ValueError("Duplicate or unordered legacy sources")
        coverage = Counter(row.availability for row in rows)
        manifest_coverage = manifest["coverage"]
        if (
            _count(manifest["row_count"]) != len(rows)
            or manifest_coverage.keys() != set(Availability)
            or any(
                _count(manifest_coverage[key]) != coverage[key] for key in Availability
            )
        ):
            raise ValueError("Inconsistent legacy coverage")
    except (AttributeError, KeyError, RecursionError, TypeError, ValueError):
        raise EffortError("Invalid legacy usage snapshot") from None
    return LegacySnapshot(project_id, cutoff, basis, digest, rows)
