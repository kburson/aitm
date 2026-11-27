"""Compile effective extension ownership and authorize planning write sets."""

from collections.abc import Callable
from fnmatch import fnmatchcase
from functools import lru_cache

from aitm_core.ext.api import EventRegistration, Extension
from aitm_core.ext.registry import RegistrationError, Registry, RegistryStatus
from aitm_core.models.events import EventEnvelope, validate_envelope
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    RelatedWriteSet,
    WriteAuthorization,
    repository_path,
)
from aitm_core.services import UnavailablePort
from aitm_core.store.backend import WriteAuthorizer
from aitm_core.store.validation import (
    CORE_ROOT_NAMES,
    CORE_STORY_NAMES,
    PlanningPath,
    classify_planning_path,
)


class OwnershipError(RegistrationError):
    """An ownership declaration is unsafe or conflicts with another owner."""


_FORBIDDEN_PARTS = frozenset({"", ".", "..", ".git"})
_FORBIDDEN_PREFIXES = frozenset(
    part[:length] for part in _FORBIDDEN_PARTS for length in range(len(part) + 1)
)
_CORE_PATHS = (
    ("stories",),
    ("stories", "*"),
    ("stories", "*", "*"),
    *((name, "**") for name in sorted(CORE_ROOT_NAMES | {"core"})),
    *(
        ("stories", "*", "*", name, "**")
        for name in sorted(CORE_STORY_NAMES | {"core"})
    ),
)


def _parse(pattern: str) -> tuple[str, ...]:
    try:
        parts = repository_path(pattern).split("/")
    except ValueError as error:
        raise OwnershipError(f"invalid ownership pattern {pattern!r}") from error
    if (
        parts[0].casefold() == ".aitm"
        or any(part.casefold() in _FORBIDDEN_PARTS for part in parts)
        or any("**" in part and part != "**" for part in parts)
        or any(
            character in "[]{}" or not character.isprintable() for character in pattern
        )
    ):
        raise OwnershipError(f"unsupported ownership pattern {pattern!r}")
    return tuple(parts)


@lru_cache(maxsize=512)
def _segments_intersect(first: str, second: str) -> bool:
    """Find a shared nonempty segment by walking the two character automata."""
    # A wildcard transition only needs the literal characters, the characters
    # that distinguish forbidden names, and one ordinary valid character.
    alphabet = (set(first) | set(second) | set(".gitx")) - {"*", "?"}
    pending: list[tuple[int, int, str | None]] = [(0, 0, "")]
    seen = set()
    while pending:
        state = pending.pop()
        if state in seen:
            continue
        seen.add(state)
        i, j, prefix = state
        if i == len(first) and j == len(second) and prefix not in _FORBIDDEN_PARTS:
            return True
        left = first[i : i + 1]
        right = second[j : j + 1]
        if left == "*":
            pending.append((i + 1, j, prefix))
        if right == "*":
            pending.append((i, j + 1, prefix))
        if not left or not right:
            continue
        for character in alphabet:
            if left not in ("*", "?", character) or right not in ("*", "?", character):
                continue
            next_prefix = None if prefix is None else prefix + character.casefold()
            if next_prefix not in _FORBIDDEN_PREFIXES:
                next_prefix = None
            pending.append((i + (left != "*"), j + (right != "*"), next_prefix))
    return False


def _paths_intersect(
    first: tuple[str, ...],
    second: tuple[str, ...],
    segments_match: Callable[[str, str], bool],
    *,
    second_is_pattern: bool = True,
) -> bool:
    """Walk paired path positions, expanding each ** into zero or more segments."""
    pending = [(0, 0)]
    seen = set()
    while pending:
        state = pending.pop()
        if state in seen:
            continue
        seen.add(state)
        i, j = state
        if i == len(first) and j == len(second):
            return True
        left = first[i] if i < len(first) else ""
        right = second[j] if j < len(second) else ""
        left_globstar = left == "**"
        right_globstar = second_is_pattern and right == "**"
        if left_globstar:
            pending.append((i + 1, j))
        if right_globstar:
            pending.append((i, j + 1))
        if (
            left
            and right
            and segments_match(
                "*" if left_globstar else left, "*" if right_globstar else right
            )
        ):
            pending.append((i + (not left_globstar), j + (not right_globstar)))
    return False


def _match_concrete(pattern: str, segment: str) -> bool:
    return fnmatchcase(segment, pattern)


def _compile_extensions(registry: Registry) -> dict[str, tuple[tuple[str, ...], ...]]:
    scopes = {}
    for extension in registry.ordered:
        paths = tuple(_parse(pattern) for pattern in extension.owned_paths)
        for path in paths:
            if any(
                _paths_intersect(path, core, _segments_intersect)
                for core in _CORE_PATHS
            ):
                raise OwnershipError(
                    f"{extension.name} ownership path {'/'.join(path)!r} overlaps Core"
                )
            for owner, other_paths in scopes.items():
                for other in other_paths:
                    if _paths_intersect(path, other, _segments_intersect):
                        raise OwnershipError(
                            f"{extension.name} ownership path {'/'.join(path)!r} "
                            f"overlaps {owner} path {'/'.join(other)!r}"
                        )
        scopes[extension.name] = paths
    return scopes


def _validate_event(
    event: EventEnvelope,
    namespace: str,
    registrations: dict[str, EventRegistration],
) -> None:
    registration = registrations.get(event.type)
    if namespace != event.namespace or registration is None:
        raise ValueError(f"extension does not own event {event.type}")
    payload = event.data.copy()
    version = payload.pop("version", 1)
    if type(version) is not int or version != registration.version:
        raise ValueError(
            f"event {event.type} requires schema version {registration.version}"
        )
    registration.model.model_validate(payload)


class ExtensionWriteAuthorizer:
    """Apply committed registry ownership before Core admits planning writes.

    Declarations are relative to .aitm. Within a segment, * matches zero or
    more characters and ? matches one. A whole ** segment matches zero or more
    segments. Registration rejects overlaps between effective owners and Core.
    """

    def __init__(self, registry: Registry, core: WriteAuthorizer | None = None) -> None:
        self._registry = registry
        self._core = core
        self._scopes = _compile_extensions(registry)
        self._events = {
            extension.name: {item.id: item for item in extension.event_types}
            for extension in registry.ordered
        }

    def __call__(
        self, owner: OperationOwner, change: RelatedWriteSet
    ) -> WriteAuthorization:
        extension = self._resolve(owner)
        try:
            self._check_paths(change, extension)
            self._check_events(change, extension)
        except ValueError as error:
            return WriteAuthorization(
                allowed=False, origin=AuthorityOrigin.REGISTERED, reason=str(error)
            )
        if extension is None:
            if self._core is None:
                raise UnavailablePort("write_authorization")
            return self._core(owner, change)
        return WriteAuthorization(
            allowed=True,
            origin=AuthorityOrigin.REGISTERED,
            extension=owner.extension,
            owned_paths=tuple(sorted(write.path for write in change.writes)),
        )

    def _resolve(self, owner: OperationOwner) -> Extension | None:
        identity = owner.extension
        if identity is None:
            return None
        result = self._registry.extension_status(identity.name)
        manifest = result.registration
        if (
            result.status is not RegistryStatus.ENABLED
            or manifest is None
            or manifest.version != identity.version
        ):
            raise UnavailablePort("write_authorization")
        return manifest

    def _check_paths(
        self, change: RelatedWriteSet, extension: Extension | None
    ) -> None:
        for write in change.writes:
            role = classify_planning_path(write.path)
            if extension is None:
                if role is PlanningPath.EXTENSION_DATA:
                    raise ValueError(f"Core does not own extension path {write.path}")
                continue
            parts = tuple(write.path.split("/")[1:])
            if role is not PlanningPath.EXTENSION_DATA or not any(
                _paths_intersect(
                    pattern, parts, _match_concrete, second_is_pattern=False
                )
                for pattern in self._scopes[extension.name]
            ):
                raise ValueError(
                    f"{extension.name} does not own planning path {write.path}"
                )

    def _check_events(
        self, change: RelatedWriteSet, extension: Extension | None
    ) -> None:
        for append in change.events:
            for raw in append.records:
                event = validate_envelope(raw)
                if event.story != append.story:
                    raise ValueError(
                        f"event {event.id} is outside story {append.story}"
                    )
                if extension is not None:
                    _validate_event(
                        event, extension.namespace, self._events[extension.name]
                    )
                elif event.namespace != "core":
                    raise ValueError(f"Core does not own event {event.type}")
