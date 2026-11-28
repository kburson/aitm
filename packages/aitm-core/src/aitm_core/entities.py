"""Entity authoring over the governed planning workspace."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from aitm_core.documents import DocumentError, _parse
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import Binding, EntityRef

if TYPE_CHECKING:
    from aitm_core.services import ServicePorts
    from aitm_core.store.backend import Snapshot
    from aitm_core.store.sync import PathSelection, SyncResult
    from aitm_core.store.workspace import Workspace

ENTITY_SCHEMA = "aitm.intake/v1"
_AUTHORED_FIELDS = {"title", "tags"}


def entity_matches(source: EntityRef, data: bytes | None) -> bool:
    if data is None:
        return False
    try:
        header = _parse(data).header
    except DocumentError:
        return False
    return (
        header.get("schema") == ENTITY_SCHEMA
        and header.get("identity") == source.identity
    )


def validate_entity_authorship(
    source: EntityRef, previous: bytes | None, content: bytes
) -> None:
    if not entity_matches(source, previous) or not entity_matches(source, content):
        raise ValueError(
            f"Entity document identity cannot change at {source.document}."
        )
    assert previous is not None
    existing = _parse(previous).header
    updated = _parse(content).header
    if {k: v for k, v in existing.items() if k not in _AUTHORED_FIELDS} != {
        k: v for k, v in updated.items() if k not in _AUTHORED_FIELDS
    }:
        raise ValueError(
            f"Generated entity metadata cannot change at {source.document}."
        )
    title = updated.get("title")
    tags = updated.get("tags")
    if (
        not isinstance(title, str)
        or not title.strip()
        or not isinstance(tags, list)
        or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
    ):
        raise ValueError(f"Entity title and tags are invalid at {source.document}.")


class BindingDisposition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: EntityRef
    source_digest: str
    binding: str
    generation: int = Field(gt=0)
    outcome: Literal["discarded", "graduated"]
    recovery: str | None = None


def open_entity(
    workspace: Workspace, handle: EntityRef, session: str, paths: tuple[str, ...] = ()
) -> Binding:
    from aitm_core.store.workspace import BindRequest

    # With no explicit extras the workspace enumerates the committed allowlist.
    if paths and handle.document not in paths:
        paths = (handle.document, *paths)
    return workspace.bind(
        BindRequest(
            workspace.installation, handle, BindingPurpose.PLANNING, session, paths
        )
    )


def sync_entity(
    workspace: Workspace,
    binding: Binding,
    selected: PathSelection,
    *,
    release: bool = False,
    ports: ServicePorts | None = None,
) -> SyncResult:
    from aitm_core.store.sync import sync, unbind

    if not isinstance(binding.scope, EntityRef):
        raise ValueError("Entity sync requires an entity binding.")
    operation = unbind if release else sync
    return operation(workspace, binding, selected, ports=ports)


def finalize_entity_binding(
    workspace: Workspace,
    source: EntityRef,
    outcome: Literal["discarded", "graduated"],
    snapshot: Snapshot,
    *,
    operation_id: str | None = None,
) -> BindingDisposition | None:
    """Prepare a receipt while holding the workspace lock through source CAS."""
    from aitm_core.store.sync import _receipt, _recovery
    from aitm_core.store.workspace import BindingConflict, digest, read_workspace

    if workspace.repo.tip() != snapshot:
        raise BindingConflict("Planning moved before entity finalization.")
    binding = workspace.lookup(source)
    if binding is None or not binding.active:
        return None
    if binding.purpose != BindingPurpose.PLANNING:
        raise BindingConflict("The entity has an incompatible binding purpose.")
    if _receipt(workspace, binding).exists():
        raise BindingConflict(
            "Resolve the binding's pending publication before finalizing."
        )
    root = Path(binding.worktree)
    workspace.verify_binding_worktree(binding)
    paths = tuple(item.path for item in binding.paths)
    pinned = workspace.repo.read_blobs(
        snapshot.tree, tuple(set(paths) | {source.document})
    )
    source_digest = digest(pinned[source.document])
    if source_digest is None or not entity_matches(source, pinned[source.document]):
        raise BindingConflict("The frozen entity source cannot be verified.")
    dirty = {}
    for item in binding.paths:
        local = read_workspace(root, item.path)
        if digest(local) != item.digest and local != pinned[item.path]:
            dirty[item.path] = (local, pinned[item.path])
    recovery = None
    if dirty:
        if operation_id is None:
            raise BindingConflict(
                "An operation identity is required to retain unsynced edits."
            )
        from aitm_core.models.operations import repository_path

        if "/" in repository_path(operation_id):
            raise ValueError(
                "Finalization operation identity must be a single path component."
            )
        recovery = _recovery(workspace, binding, dirty, operation_id).name
    return BindingDisposition(
        source=source,
        source_digest=source_digest,
        binding=binding.identity,
        generation=binding.generation,
        outcome=outcome,
        recovery=recovery,
    )
