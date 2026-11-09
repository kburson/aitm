"""Deterministic, allowlisted snapshots for the future C44 usage adapter."""

import ctypes
import errno
import json
import os
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC
from hashlib import sha256
from pathlib import Path
from secrets import token_hex
from uuid import UUID

from .ledger import (
    LedgerError,
    _check_acl,
    _path_id,
    _pin_directory,
    _PinnedPath,
    _private,
    _project_path,
    _validated_path,
)
from .pricing import RateCard, price
from .scopes import _RENAME_EXCL, _rename_exclusive, resolve_scope
from .types import (
    Availability,
    Diagnostic,
    LedgerView,
    PriceObservation,
    PriceResult,
    Revision,
    SourceRef,
    UsageObservation,
    _decimal_text,
    _nonnegative,
)

EXPORT_SCHEMA = "aitm.usage.export/v1"
MANIFEST_NAME = "manifest.json"
USAGE_NAME = "usage.jsonl"


class ExportError(LedgerError):
    """Invalid snapshot or unsafe/conflicting destination."""


@dataclass(frozen=True, slots=True)
class ExportReceipt:
    schema: str
    project_id: UUID
    cutoff: int
    rate_basis: str
    sha256: str
    row_count: int


def _json_line(payload: dict) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _public_ref(reference: SourceRef | None) -> str | None:
    return None if reference is None else reference.value.rsplit(":", 1)[0]


def _scope(usage: UsageObservation, view: LedgerView) -> dict | None:
    resolved = resolve_scope(usage, view)
    if resolved.scope is None or resolved.revision is None:
        return None
    marker = resolved.scope.marker
    item_id = marker.item.identifier
    return {
        "revision": {
            "source": _public_ref(resolved.revision.key),
            "number": resolved.revision.revision,
        },
        "item": {
            "kind": marker.item.kind.value,
            "id": str(item_id) if isinstance(item_id, UUID) else item_id,
        },
        "phase": marker.phase.value,
        "participant_ref": _public_ref(marker.participant_ref),
        "role": None if marker.role is None else marker.role.value,
        "attempt_ref": _public_ref(marker.attempt_ref),
        "review_ref": _public_ref(marker.review_ref),
    }


def _row(
    revision: Revision, usage: UsageObservation, result: PriceResult, view: LedgerView
) -> dict:
    scope = _scope(usage, view)
    tokens = usage.tokens
    return {
        "source": _public_ref(revision.key),
        "observation_revision": revision.revision,
        "provider": usage.boundary.provider.value,
        "boundary_kind": usage.boundary.kind.value,
        "observed_at": usage.observed_at.astimezone(UTC).isoformat(),
        "client_version": usage.client_version.value,
        "format_version": usage.format_version,
        "model": usage.model.value,
        "effort": None if usage.effort is None else usage.effort.value,
        "processing_tier": None
        if usage.processing_tier is None
        else usage.processing_tier.value,
        "availability": usage.availability.value,
        "tokens": {
            "input_tokens": tokens.input_tokens,
            "cached_input_tokens": tokens.cached_input_tokens,
            "cache_write_5m_tokens": tokens.cache_write_5m_tokens,
            "cache_write_1h_tokens": tokens.cache_write_1h_tokens,
            "output_tokens": tokens.output_tokens,
            "reasoning_output_tokens": tokens.reasoning_output_tokens,
            "total_tokens": tokens.total_tokens,
        },
        "scope_availability": "unknown" if scope is None else "complete",
        "scope": scope,
        "price": {
            "availability": result.availability.value,
            "currency": result.currency.value,
            "rate_basis": result.basis.identifier,
            "usd": None if result.usd is None else _decimal_text(result.usd),
        },
    }


def _render(
    view: LedgerView, rate_card: RateCard
) -> tuple[ExportReceipt, dict[str, bytes]]:
    _nonnegative(view.sequence)
    if type(view.project_id) is not UUID or type(rate_card) is not RateCard:
        raise ExportError("Invalid project identity or rate card")
    basis = rate_card.basis.identifier
    prices: dict[tuple[SourceRef, int], PriceResult] = {}
    diagnostics: Counter[tuple[str, str]] = Counter()
    observations = []
    for revision in view.current:
        record = revision.record
        if isinstance(record, PriceObservation) and record.rate_basis == basis:
            key = (record.observation_key, record.observation_revision)
            if prices.setdefault(key, record.result) != record.result:
                raise ExportError("Conflicting prices at the selected rate basis")
        elif isinstance(record, Diagnostic):
            provider = "" if record.provider is None else record.provider.value
            diagnostics[record.code.value, provider] += 1
        elif isinstance(record, UsageObservation):
            observations.append((revision, record))

    coverage = dict.fromkeys((item.value for item in Availability), 0)
    lines = []
    for revision, usage in sorted(observations, key=lambda pair: pair[0].key.value):
        result = prices.get((revision.key, revision.revision))
        if result is None:
            result = price(usage, rate_card)
        coverage[usage.availability.value] += 1
        lines.append(_json_line(_row(revision, usage, result, view)))
    data = b"".join(lines)
    receipt = ExportReceipt(
        EXPORT_SCHEMA,
        view.project_id,
        view.sequence,
        basis,
        sha256(data).hexdigest(),
        len(lines),
    )
    manifest = {
        "schema": receipt.schema,
        "project_id": str(receipt.project_id),
        "cutoff": receipt.cutoff,
        "rate_basis": receipt.rate_basis,
        "sha256": receipt.sha256,
        "row_count": receipt.row_count,
        "coverage": coverage,
        "diagnostics": [
            {"code": code, "provider": provider or None, "count": count}
            for (code, provider), count in sorted(diagnostics.items())
        ],
    }
    return receipt, {USAGE_NAME: data, MANIFEST_NAME: _json_line(manifest)}


def _check_snapshot(directory: _PinnedPath, files: dict[str, bytes]) -> None:
    """An exact, private, complete snapshot is the only successful replay."""
    if set(os.listdir(directory.fd)) != files.keys():
        raise ExportError("Conflicting export destination")
    for name, expected in files.items():
        fd = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory.fd
        )
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(fd)
            _private(info)
            _check_acl(fd)
            if (
                info.st_size != len(expected)
                or handle.read(len(expected) + 1) != expected
                or not os.path.samestat(
                    info, os.stat(name, dir_fd=directory.fd, follow_symlinks=False)
                )
            ):
                raise ExportError("Conflicting export destination")
    if set(os.listdir(directory.fd)) != files.keys():
        raise ExportError("Conflicting export destination")
    directory.check()


def _write_snapshot(directory: _PinnedPath, files: dict[str, bytes]) -> None:
    for name, data in files.items():
        fd = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory.fd,
        )
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(fd, 0o600)
            handle.write(data)
            handle.flush()
            os.fsync(fd)
    os.fsync(directory.fd)
    _check_snapshot(directory, files)


def _check_replay(
    parent_fd: int,
    destination: Path,
    ancestry: tuple[tuple[int, int], ...],
    files: dict[str, bytes],
) -> None:
    with _pin_directory(destination) as existing:
        if existing.identities[:-1] != ancestry:
            raise ExportError("Export destination ancestry changed")
        _check_snapshot(existing, files)
        # A prior publisher may have linked the complete snapshot but failed
        # to durably commit the destination directory entry.
        os.fsync(parent_fd)
        existing.check()


@contextmanager
def _new_private_child(
    parent_fd: int, path: Path, ancestry: tuple[tuple[int, int], ...]
) -> Iterator[_PinnedPath]:
    os.mkdir(path.name, mode=0o700, dir_fd=parent_fd)
    identity = _path_id(os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False))
    try:
        with _pin_directory(path) as child:
            if child.identities != (*ancestry, identity):
                raise ExportError("Export staging directory changed")
            yield child
    finally:
        try:
            info = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
            if _path_id(info) == identity:
                os.rmdir(path.name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass


def _publish_staged(
    container: _PinnedPath,
    parent_fd: int,
    destination: Path,
    ancestry: tuple[tuple[int, int], ...],
    files: dict[str, bytes],
) -> None:
    source = container.path / "snapshot"
    with _new_private_child(container.fd, source, container.identities) as staged:
        published = False
        try:
            _write_snapshot(staged, files)
            # A replacement of the outer staging name cannot substitute the
            # completed source entry in this pinned, private directory.
            if _rename_exclusive()(
                container.fd,
                os.fsencode(source.name),
                parent_fd,
                os.fsencode(destination.name),
                _RENAME_EXCL,
            ):
                if ctypes.get_errno() != errno.EEXIST:
                    raise ExportError("Unable to publish export snapshot")
                _check_replay(parent_fd, destination, ancestry, files)
            else:
                published = True
                os.fsync(container.fd)
                os.fsync(parent_fd)
                if _validated_path(destination, directory=True) != (
                    *ancestry,
                    staged.identities[-1],
                ):
                    raise ExportError("Export destination changed during publication")
        finally:
            if not published:
                for name in files:
                    try:
                        os.unlink(name, dir_fd=staged.fd)
                    except FileNotFoundError:
                        pass


def _publish(destination: Path, files: dict[str, bytes]) -> None:
    destination = _project_path(destination)
    if not destination.name:
        raise ExportError("Invalid export destination")
    stage = destination.with_name(f".export-{token_hex(16)}")
    ancestry = _validated_path(stage, directory=True, allow_missing=True)
    if len(ancestry) != len(destination.parents):
        raise ExportError("Export parent must exist")
    parent_fd = os.open(
        destination.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    )
    try:
        if _path_id(os.fstat(parent_fd)) != ancestry[-1]:
            raise ExportError("Export destination ancestry changed")
        try:
            os.stat(destination.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            _check_replay(parent_fd, destination, ancestry, files)
            return

        with _new_private_child(parent_fd, stage, ancestry) as container:
            _publish_staged(container, parent_fd, destination, ancestry, files)
    finally:
        os.close(parent_fd)


def export_as_of(
    view: LedgerView, rate_card: RateCard, destination: Path
) -> ExportReceipt:
    """Publish a complete export for exactly one committed ledger view and rate basis."""
    try:
        receipt, files = _render(view, rate_card)
        _publish(destination, files)
    except ExportError:
        raise
    except (LedgerError, OSError, ValueError):
        raise ExportError("Invalid export snapshot or destination") from None
    return receipt
