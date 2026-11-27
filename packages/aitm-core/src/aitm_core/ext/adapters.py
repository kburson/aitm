"""Resolve a versioned extension adapter while retaining the original bytes."""

from dataclasses import dataclass

from aitm_core.ext.api import Extension
from aitm_core.ext.registry import Registry, RegistryStatus


@dataclass(frozen=True, slots=True)
class AdapterResult:
    status: RegistryStatus
    owner: str
    version: str
    raw: bytes
    registration: Extension | None = None
    reason: str | None = None


def resolve_adapter(
    registry: Registry, owner: str, version: str, raw: bytes
) -> AdapterResult:
    """Return an available exact adapter or an opaque, lossless record."""
    result = registry.extension_status(owner)
    declaration = result.registration
    if declaration is None:
        return AdapterResult(result.status, owner, version, raw, reason=result.reason)
    if declaration.version != version:
        return AdapterResult(
            RegistryStatus.INCOMPATIBLE,
            owner,
            version,
            raw,
            reason=f"installed adapter version {declaration.version} differs from {version}",
        )
    return AdapterResult(RegistryStatus.ENABLED, owner, version, raw, declaration)
