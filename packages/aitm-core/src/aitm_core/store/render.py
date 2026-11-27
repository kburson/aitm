"""Render portable document views from pinned inputs."""

from dataclasses import dataclass, field
from re import fullmatch

from aitm_core.documents import rewrite_metadata
from aitm_core.models.documents import DocumentSchema, Metadata
from aitm_core.store.backend import Blobs


@dataclass(frozen=True, slots=True)
class ViewState:
    metadata: Metadata = field(default_factory=Metadata)
    worktree_label: str | None = None

    def __post_init__(self) -> None:
        if self.worktree_label is not None and not fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*", self.worktree_label
        ):
            raise ValueError(
                "shared worktree metadata requires a stable worktree label"
            )


def render(state: ViewState, authored: Blobs, schema: DocumentSchema) -> Blobs:
    """Project generated metadata without using authored documents as state."""
    generated = state.metadata.model_copy(
        update={"last_worktree": state.worktree_label}
    )
    return {
        path: rewrite_metadata(raw, generated, schema=schema)
        if raw is not None
        else None
        for path, raw in sorted(authored.items())
    }
