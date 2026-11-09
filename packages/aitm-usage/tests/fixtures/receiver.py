"""Disposable, SQLite-backed model of an immutable C44 usage sink and adapter."""

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    DiagnosticCode,
    Effort,
    ItemKey,
    ItemKind,
    ModelLabel,
    ProcessingTier,
    Provider,
    ReviewRole,
    TokenCounts,
    WorkPhase,
)


class ReceiverConflict(ValueError):
    """An immutable source or snapshot was supplied with contradictory bytes."""


class ImportInterrupted(RuntimeError):
    """Controlled interruption before the receiver commits an import."""


def _canonical(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _decode(raw: bytes) -> dict:
    payload = json.loads(raw)
    if type(payload) is not dict or raw != _canonical(payload):
        raise ValueError("Noncanonical usage export object")
    return payload


def _closed(value, keys):
    if type(value) is not dict or value.keys() != set(keys.split()):
        raise ValueError("Invalid usage export fields")


def _count(value, *, minimum=0):
    if type(value) is not int or not minimum <= value < 2**63:
        raise ValueError("Invalid usage export count")


def _matches(value, pattern):
    if type(value) is not str or re.fullmatch(pattern, value) is None:
        raise ValueError("Invalid usage export reference or decimal")


def _source(value):
    _matches(value, r"hmac-sha256:[a-f0-9]{64}")


def _validate_basis(basis):
    _matches(basis, r"standard-api-USD:[0-9]{4}-[0-9]{2}-[0-9]{2}:sha256:[a-f0-9]{64}")
    date.fromisoformat(basis.split(":")[1])


def _validate_scope(row):
    scope = row["scope"]
    if scope is None:
        if row["scope_availability"] != Availability.UNKNOWN:
            raise ValueError("Missing scope must be Unknown")
        return
    if row["scope_availability"] != Availability.COMPLETE:
        raise ValueError("Known scope must be complete")
    _closed(scope, "revision item phase participant_ref role attempt_ref review_ref")
    _closed(scope["revision"], "source number")
    _source(scope["revision"]["source"])
    _count(scope["revision"]["number"], minimum=1)
    _closed(scope["item"], "kind id")
    kind = ItemKind(scope["item"]["kind"])
    identifier = scope["item"]["id"]
    if kind is ItemKind.DRAFT:
        raw = identifier
        if type(raw) is not str:
            raise ValueError("Invalid draft UUID")
        identifier = UUID(raw)
        if raw != str(identifier):
            raise ValueError("Noncanonical draft UUID")
    ItemKey(kind, identifier)
    WorkPhase(scope["phase"])
    _source(scope["participant_ref"])
    if scope["role"] is not None:
        ReviewRole(scope["role"])
    for field in ("attempt_ref", "review_ref"):
        if scope[field] is not None:
            _source(scope[field])


def _validate_price(row, rate_basis):
    price = row["price"]
    _closed(price, "availability currency rate_basis usd")
    _validate_basis(price["rate_basis"])
    if price["rate_basis"] != rate_basis or price["currency"] != "USD":
        raise ValueError("Inconsistent pricing basis")
    if price["availability"] == Availability.COMPLETE:
        if row["availability"] != Availability.COMPLETE:
            raise ValueError("Incomplete usage cannot have a complete price")
        _matches(price["usd"], r"(?:0|[1-9][0-9]{0,23})(?:\.[0-9]{0,12}[1-9])?")
    elif price["availability"] != Availability.UNKNOWN or price["usd"] is not None:
        raise ValueError("Invalid Unknown price")


def _validate_row(row, rate_basis):
    _closed(
        row,
        "source observation_revision provider boundary_kind observed_at client_version "
        "format_version model effort processing_tier availability tokens "
        "scope_availability scope price",
    )
    _source(row["source"])
    _count(row["observation_revision"], minimum=1)
    _count(row["format_version"], minimum=1)
    Provider(row["provider"])
    BoundaryKind(row["boundary_kind"])
    ClientVersion(row["client_version"])
    ModelLabel(row["model"])
    Availability(row["availability"])
    if type(row["observed_at"]) is not str:
        raise ValueError("Invalid observation time")
    observed_at = datetime.fromisoformat(row["observed_at"])
    if (
        observed_at.utcoffset() != timedelta(0)
        or observed_at.isoformat() != row["observed_at"]
    ):
        raise ValueError("Noncanonical observation time")
    if row["effort"] is not None:
        Effort(row["effort"])
    if row["processing_tier"] is not None:
        ProcessingTier(row["processing_tier"])
    _closed(
        row["tokens"],
        "input_tokens cached_input_tokens cache_write_5m_tokens cache_write_1h_tokens "
        "output_tokens reasoning_output_tokens total_tokens",
    )
    TokenCounts(**row["tokens"])
    _validate_scope(row)
    _validate_price(row, rate_basis)


def _load_snapshot(
    directory: Path, project_id: UUID
) -> tuple[dict, list[tuple[dict, bytes]]]:
    raw_manifest = (directory / "manifest.json").read_bytes()
    if not raw_manifest.endswith(b"\n"):
        raise ValueError("Incomplete usage export manifest")
    manifest = _decode(raw_manifest[:-1])
    _closed(
        manifest,
        "schema project_id cutoff rate_basis sha256 row_count coverage diagnostics",
    )
    if manifest["schema"] != "aitm.usage.export/v1" or manifest["project_id"] != str(
        project_id
    ):
        raise ValueError("Unsupported usage export schema or project")
    _count(manifest["cutoff"])
    _count(manifest["row_count"])
    _validate_basis(manifest["rate_basis"])
    data = (directory / "usage.jsonl").read_bytes()
    if sha256(data).hexdigest() != manifest["sha256"]:
        raise ValueError("Invalid usage export digest")
    if data and not data.endswith(b"\n"):
        raise ValueError("Incomplete usage export row")
    rows = []
    previous = ""
    coverage = {item.value: 0 for item in Availability}
    for payload in data.split(b"\n")[:-1]:
        row = _decode(payload)
        _validate_row(row, manifest["rate_basis"])
        if row["source"] <= previous:
            raise ReceiverConflict("Unordered or duplicate export source")
        previous = row["source"]
        coverage[row["availability"]] += 1
        rows.append((row, payload))
    if manifest["row_count"] != len(rows) or manifest["coverage"] != coverage:
        raise ValueError("Inconsistent usage export coverage")
    for value in manifest["coverage"].values():
        _count(value)

    if type(manifest["diagnostics"]) is not list:
        raise ValueError("Invalid usage export diagnostics")
    seen = set()
    for diagnostic in manifest["diagnostics"]:
        _closed(diagnostic, "code count provider")
        code = DiagnosticCode(diagnostic["code"])
        provider = diagnostic["provider"]
        if provider is not None:
            Provider(provider)
        _count(diagnostic["count"], minimum=1)
        if (code, provider) in seen:
            raise ValueError("Duplicate diagnostic summary")
        seen.add((code, provider))
    return manifest, rows


def _compatible(row) -> bool:
    return (
        row["availability"] == Availability.COMPLETE
        and row["scope_availability"] == Availability.COMPLETE
    )


class Receiver:
    """Import snapshots and invoke an immutable sink in one disposable transaction."""

    def __init__(self, database: Path, project_id: UUID):
        self._db = sqlite3.connect(database, isolation_level=None)
        self._project_id = project_id
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta(
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                project TEXT NOT NULL, watermark INTEGER
            );
            CREATE TABLE IF NOT EXISTS snapshot(
                cutoff INTEGER NOT NULL, basis TEXT NOT NULL, digest TEXT NOT NULL,
                projection_digest TEXT NOT NULL, PRIMARY KEY(cutoff, basis)
            );
            CREATE TABLE IF NOT EXISTS component(
                kind TEXT NOT NULL, identity BLOB NOT NULL, payload BLOB NOT NULL,
                PRIMARY KEY(kind, identity)
            );
            CREATE TABLE IF NOT EXISTS accepted(
                source TEXT PRIMARY KEY, digest TEXT NOT NULL, payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pending(
                source TEXT PRIMARY KEY, digest TEXT NOT NULL, payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reconciliation(
                source TEXT NOT NULL, digest TEXT NOT NULL, payload BLOB NOT NULL,
                PRIMARY KEY(source, digest)
            );
            """
        )
        self._db.execute(
            "INSERT OR IGNORE INTO meta VALUES(1, ?, NULL)", (str(project_id),)
        )
        if self._db.execute("SELECT project FROM meta").fetchone()[0] != str(
            project_id
        ):
            self._db.close()
            raise ValueError("Receiver project identity mismatch")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()

    @property
    def watermark(self) -> int | None:
        return self._db.execute("SELECT watermark FROM meta").fetchone()[0]

    @property
    def accepted(self) -> dict[str, str]:
        return dict(self._db.execute("SELECT source, digest FROM accepted"))

    @property
    def pending(self) -> set[str]:
        return {row[0] for row in self._db.execute("SELECT source FROM pending")}

    @property
    def reconciliation(self) -> dict[str, int]:
        return dict(
            self._db.execute(
                "SELECT source, COUNT(*) FROM reconciliation GROUP BY source"
            )
        )

    @contextmanager
    def _transaction(self):
        if self._db.in_transaction:
            yield
            return
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            yield

    def _remember(self, kind: str, identity: object, value: object) -> None:
        key = _canonical(identity)
        payload = _canonical(value)
        stored = self._db.execute(
            "SELECT payload FROM component WHERE kind = ? AND identity = ?", (kind, key)
        ).fetchone()
        if stored is None:
            self._db.execute(
                "INSERT INTO component VALUES(?, ?, ?)", (kind, key, payload)
            )
        elif stored[0] != payload:
            raise ReceiverConflict(
                f"Different payload with the same source provenance ({kind})"
            )

    def _remember_components(self, row: dict) -> None:
        source = row["source"]
        revision = row["observation_revision"]
        scope = row["scope"]
        price = row["price"]
        self._remember("source", source, row["provider"])
        self._remember(
            "observation",
            [source, revision],
            {
                key: value
                for key, value in row.items()
                if key not in ("scope", "scope_availability", "price")
            },
        )
        if scope is not None:
            self._remember("scope", scope["revision"], scope)
        self._remember("price", [source, revision, price["rate_basis"]], price)

    def ingest_usage(self, source: str, payload: bytes) -> str:
        """The modeled C44 seam accepts one exact compatible payload per key."""
        row = _decode(payload)
        _closed(row.get("price"), "availability currency rate_basis usd")
        _validate_row(row, row["price"]["rate_basis"])
        if source != row["source"] or not _compatible(row):
            raise ValueError("Incompatible immutable usage payload")
        digest = sha256(payload).hexdigest()
        with self._transaction():
            self._remember_components(row)
            result = self._db.execute(
                "INSERT OR IGNORE INTO accepted VALUES(?, ?, ?)",
                (source, digest, payload),
            )
            if result.rowcount == 1:
                return "accepted"
            original = self._db.execute(
                "SELECT payload FROM accepted WHERE source = ?", (source,)
            ).fetchone()[0]
            if original != payload:
                raise ReceiverConflict("Different payload for an accepted source")
            return "duplicate"

    def _consider(self, row: dict, payload: bytes) -> None:
        source = row["source"]
        digest = sha256(payload).hexdigest()
        accepted = self._db.execute(
            "SELECT digest FROM accepted WHERE source = ?", (source,)
        ).fetchone()
        if accepted is None and _compatible(row):
            self.ingest_usage(source, payload)
        else:
            self._remember_components(row)
            if accepted is None:
                self._db.execute(
                    """INSERT INTO pending VALUES(?, ?, ?)
                       ON CONFLICT(source) DO UPDATE SET digest=excluded.digest, payload=excluded.payload""",
                    (source, digest, payload),
                )
                return
            if accepted[0] != digest:
                self._db.execute(
                    "INSERT OR IGNORE INTO reconciliation VALUES(?, ?, ?)",
                    (source, digest, payload),
                )
        self._db.execute("DELETE FROM pending WHERE source = ?", (source,))

    def import_snapshot(
        self, directory: Path, *, interrupt_after: int | None = None
    ) -> str:
        manifest, rows = _load_snapshot(directory, self._project_id)
        cutoff, basis = manifest["cutoff"], manifest["rate_basis"]
        digest = sha256(_canonical(manifest)).hexdigest()
        # A rate selection can change price at the same cutoff. The fixed usage
        # and coverage must still agree with the previously imported projection.
        projection = {
            key: value
            for key, value in manifest.items()
            if key not in ("rate_basis", "sha256")
        }
        projection["rows"] = [
            {key: value for key, value in row.items() if key != "price"}
            for row, _ in rows
        ]
        projection_digest = sha256(_canonical(projection)).hexdigest()
        with self._transaction():
            watermark = self.watermark
            if watermark is not None and cutoff < watermark:
                return "stale"
            for (
                previous_basis,
                previous_digest,
                previous_projection,
            ) in self._db.execute(
                "SELECT basis, digest, projection_digest FROM snapshot WHERE cutoff = ?",
                (cutoff,),
            ):
                if previous_projection != projection_digest:
                    raise ReceiverConflict(
                        "Different usage projection at the same cutoff"
                    )
                if previous_basis == basis:
                    if previous_digest != digest:
                        raise ReceiverConflict(
                            "Different manifest for the same cutoff and rate"
                        )
                    return "duplicate"
            for index, (row, payload) in enumerate(rows, 1):
                self._consider(row, payload)
                if index == interrupt_after:
                    raise ImportInterrupted("Interrupted before snapshot commit")
            self._db.execute(
                "INSERT INTO snapshot VALUES(?, ?, ?, ?)",
                (cutoff, basis, digest, projection_digest),
            )
            self._db.execute("UPDATE meta SET watermark = ?", (cutoff,))
            return "imported"
