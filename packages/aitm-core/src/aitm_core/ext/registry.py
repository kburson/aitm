"""Resolve extension declarations against committed policy without loading effects."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from graphlib import CycleError, TopologicalSorter
from heapq import heapify, heappop, heappush
from importlib.metadata import version
from types import MappingProxyType

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from aitm_core.config import PolicySnapshot
from aitm_core.ext.api import (
    ActivityProducerRegistration,
    CapabilitySlot,
    DirectiveRegistration,
    Extension,
    Placement,
    ProducerRef,
)

type Capability = CapabilitySlot | DirectiveRegistration


class RegistrationError(ValueError):
    """A registry would make declaration or dependency authority ambiguous."""


class RegistryStatus(StrEnum):
    ENABLED = "enabled"
    MISSING = "missing"
    DISABLED = "disabled"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class Resolution[T]:
    status: RegistryStatus
    registration: T | None = None
    reason: str | None = None


_MEASUREMENT_CLASSES = {
    "engaged-interval/v1": "measured-engagement",
    "tool-interval/v1": "tool-duration",
    "cli-gap/v1": "gap-estimate",
}


@dataclass(frozen=True, slots=True)
class Registry:
    ordered: tuple[Extension, ...]
    _extensions: Mapping[str, Resolution[Extension]]
    _capabilities: Mapping[str, tuple[str, Capability]]
    _activity: Mapping[str, ActivityProducerRegistration]

    def extension_status(self, name: str) -> Resolution[Extension]:
        return self._extensions.get(
            name, Resolution(RegistryStatus.MISSING, reason=f"{name} is not installed")
        )

    def resolve(
        self,
        identifier: str,
        *,
        version: int | None = None,
        placement: Placement | None = None,
    ) -> Resolution[Capability]:
        found = self._capabilities.get(identifier)
        if found is None:
            return Resolution(
                RegistryStatus.MISSING, reason=f"{identifier} is unregistered"
            )
        owner, registration = found
        if owner != "core":
            status = self.extension_status(owner)
            if status.status is not RegistryStatus.ENABLED:
                return Resolution(status.status, reason=status.reason)
        slot = _capability_slot(registration)
        if version is not None and version != slot.version:
            return Resolution(
                RegistryStatus.INCOMPATIBLE,
                reason=f"{identifier} has version {slot.version}, required {version}",
            )
        if placement is not None and placement not in slot.placements:
            return Resolution(
                RegistryStatus.INCOMPATIBLE,
                reason=f"{identifier} cannot be placed in {placement}",
            )
        return Resolution(RegistryStatus.ENABLED, registration)

    def register_activity(self, contract: ActivityProducerRegistration) -> ProducerRef:
        if self._activity.get(contract.id) != contract:
            raise RegistrationError(
                f"{contract.id} is not enabled with this exact contract"
            )
        return ProducerRef(**contract.model_dump())


def _capability_slot(registration: Capability) -> CapabilitySlot:
    if isinstance(registration, DirectiveRegistration):
        return registration.slot
    if registration.kind == "directive":
        raise RegistrationError(
            f"directive {registration.id} requires Markdown metadata"
        )
    return registration


def _declarations(
    manifests: Iterable[Extension], builtins: Iterable[Capability]
) -> dict[str, tuple[str, Capability]]:
    by_id: set[str] = set()
    capabilities = {}

    def admit(namespace: str, identifier: str) -> None:
        if not identifier.startswith(f"{namespace}."):
            raise RegistrationError(f"{identifier} is outside namespace {namespace}")
        if identifier in by_id:
            raise RegistrationError(f"duplicate registration {identifier}")
        by_id.add(identifier)

    for registration in builtins:
        identifier = _capability_slot(registration).id
        admit("core", identifier)
        capabilities[identifier] = ("core", registration)
    for manifest in manifests:
        for registration in (*manifest.capabilities, *manifest.directives):
            identifier = _capability_slot(registration).id
            admit(manifest.namespace, identifier)
            capabilities[identifier] = (manifest.name, registration)
        for item in (
            *manifest.event_types,
            *manifest.activity_producers,
            *manifest.init_steps,
        ):
            admit(manifest.namespace, item.id)
    return capabilities


def _installed_and_status(
    declarations: Iterable[Extension], enabled: tuple[str, ...], core: Version
) -> tuple[dict[str, Extension], dict[str, Resolution[Extension]]]:
    if len(set(enabled)) != len(enabled):
        raise RegistrationError("duplicate extension in committed policy")
    installed: dict[str, Extension] = {}
    owners: set[str] = {"core"}
    statuses = {
        name: Resolution(RegistryStatus.MISSING, reason=f"{name} is not installed")
        for name in enabled
    }
    for manifest in declarations:
        if manifest.name == "core" or manifest.namespace in owners:
            raise RegistrationError(
                f"reserved or duplicate namespace {manifest.namespace}"
            )
        if manifest.name in installed:
            raise RegistrationError(f"duplicate installed extension {manifest.name}")
        try:
            Version(manifest.version)
            requirement = SpecifierSet(manifest.requires_core)
        except (InvalidVersion, InvalidSpecifier) as error:
            raise RegistrationError(f"{manifest.name}: {error}") from error
        installed[manifest.name] = manifest
        owners.add(manifest.namespace)
        if manifest.name not in enabled:
            statuses[manifest.name] = Resolution(
                RegistryStatus.DISABLED,
                reason=f"{manifest.name} is disabled by committed policy",
            )
        elif core not in requirement:
            statuses[manifest.name] = Resolution(
                RegistryStatus.INCOMPATIBLE,
                reason=f"{manifest.name} requires Core {requirement}; found {core}",
            )
        else:
            statuses[manifest.name] = Resolution(RegistryStatus.ENABLED, manifest)
    return installed, statuses


def _ordered(
    installed: Mapping[str, Extension], statuses: Mapping[str, Resolution[Extension]]
) -> tuple[Extension, ...]:
    graph: TopologicalSorter[str] = TopologicalSorter()
    for name, manifest in installed.items():
        if statuses[name].status is not RegistryStatus.ENABLED:
            continue
        dependencies: set[str] = set()
        for dependency in manifest.dependencies:
            target = dependency.name
            if target in dependencies:
                raise RegistrationError(f"{name} has duplicate dependency {target}")
            dependencies.add(target)
            state = statuses.get(target)
            if state is None or state.status is not RegistryStatus.ENABLED:
                status = RegistryStatus.MISSING if state is None else state.status
                raise RegistrationError(f"{name} requires {target}, which is {status}")
            try:
                requirement = SpecifierSet(dependency.version)
            except InvalidSpecifier as error:
                raise RegistrationError(
                    f"{name} dependency {target}: {error}"
                ) from error
            if Version(installed[target].version) not in requirement:
                raise RegistrationError(
                    f"{name} requires {target} {requirement}, incompatible version"
                )
        graph.add(name, *sorted(dependencies))
    try:
        graph.prepare()
    except CycleError as error:
        raise RegistrationError(
            f"extension dependency cycle: {error.args[1]}"
        ) from error

    ready = [(installed[name].namespace, name) for name in graph.get_ready()]
    heapify(ready)
    result = []
    while ready:
        _, name = heappop(ready)
        result.append(installed[name])
        graph.done(name)
        for waiting in graph.get_ready():
            heappush(ready, (installed[waiting].namespace, waiting))
    return tuple(result)


def load_extensions(
    policy: PolicySnapshot,
    installed: Iterable[Extension] = (),
    *,
    builtins: Iterable[Capability] = (),
) -> Registry:
    """Validate discovered declarations and committed selection. C63 owns discovery."""
    core = Version(version("aitm-core"))
    manifests, statuses = _installed_and_status(
        installed, policy.config.extensions.enabled, core
    )
    capabilities = _declarations(manifests.values(), builtins)
    ordered = _ordered(manifests, statuses)
    activity: dict[str, ActivityProducerRegistration] = {}
    for manifest in ordered:
        for contract in manifest.activity_producers:
            if (
                _MEASUREMENT_CLASSES.get(contract.measurement_contract)
                != contract.coverage_class
            ):
                raise RegistrationError(
                    f"{contract.id} has an unsupported measurement contract"
                )
            activity[contract.id] = contract
    return Registry(
        ordered,
        MappingProxyType(statuses),
        MappingProxyType(capabilities),
        MappingProxyType(activity),
    )
