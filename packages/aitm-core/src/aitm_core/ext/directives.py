"""Read a declared directive at the exact workflow source coordinate."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from aitm_core.config import CommittedFile, PolicyUnavailable
from aitm_core.ext.api import CapabilityScope, DirectiveRegistration
from aitm_core.ext.registry import Registry, RegistryStatus
from aitm_core.machine.profile import ProfileSource
from aitm_core.models.operations import repository_path
from aitm_core.store.objects import GitCommandError

type CommittedFileReader = Callable[[str, str], CommittedFile | None]


class DirectiveStatus(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    DISABLED = "disabled"
    INCOMPATIBLE = "incompatible"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class DirectiveSnapshot:
    """A C90 source pin and a reader of regular files by exact tree and path."""

    source: ProfileSource
    read_file: CommittedFileReader


@dataclass(frozen=True, slots=True)
class DirectiveContent:
    path: str
    revision: str
    tree: str
    digest: str
    markdown: str


@dataclass(frozen=True, slots=True)
class DirectiveView:
    capability_id: str
    status: DirectiveStatus
    version: int | None = None
    scope: CapabilityScope | None = None
    requested_evidence: tuple[str, ...] = ()
    content: DirectiveContent | None = None
    reason: str | None = None


def resolve_directive(
    registry: Registry,
    snapshot: DirectiveSnapshot,
    capability_id: str,
    *,
    version: int | None = None,
) -> DirectiveView:
    """Pin the selected directive content without dispatching the slot."""
    result = registry.resolve(capability_id, version=version, placement="action")
    if result.status is not RegistryStatus.ENABLED:
        return DirectiveView(
            capability_id, DirectiveStatus(result.status.value), reason=result.reason
        )
    registration = result.registration
    if not isinstance(registration, DirectiveRegistration):
        return DirectiveView(
            capability_id,
            DirectiveStatus.INCOMPATIBLE,
            reason="the selected capability is not a directive",
        )

    try:
        path = repository_path(registration.markdown)
        file = snapshot.read_file(snapshot.source.tree, path)
        if file is None:
            raise PolicyUnavailable(
                f"directive file is missing from pinned tree: {path}"
            )
        if not isinstance(file, CommittedFile) or file.path != path:
            raise PolicyUnavailable(
                f"directive file evidence disagrees with path {path}"
            )
        if not isinstance(file.content, bytes):
            raise PolicyUnavailable(
                f"directive file evidence must contain bytes: {path}"
            )
        markdown = file.content.decode("utf-8")
    except UnicodeDecodeError:
        reason = f"directive Markdown must be UTF-8: {registration.markdown}"
    except (GitCommandError, OSError, ValueError) as error:
        reason = str(error)
    else:
        return DirectiveView(
            capability_id,
            DirectiveStatus.AVAILABLE,
            version=registration.slot.version,
            scope=registration.slot.scope,
            requested_evidence=registration.requested_evidence,
            content=DirectiveContent(
                path=path,
                revision=snapshot.source.revision,
                tree=snapshot.source.tree,
                digest=file.digest,
                markdown=markdown,
            ),
        )
    return DirectiveView(capability_id, DirectiveStatus.UNAVAILABLE, reason=reason)
