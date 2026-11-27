"""Render portable document views from pinned inputs."""

from dataclasses import dataclass, field
from json import dumps
from re import fullmatch

from aitm_core.description import description_path
from aitm_core.documents import DocumentError, _parse, canonicalize, rewrite_metadata
from aitm_core.events import StoryState
from aitm_core.models.documents import DocumentSchema, Metadata
from aitm_core.models.lifecycle import LifecycleState
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.store.backend import Blobs


@dataclass(frozen=True, slots=True)
class ViewState:
    story: StoryState
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
    """Refresh authored metadata and regenerate the view from folded facts."""
    lifecycle = state.story.domains.get("lifecycle")
    if not isinstance(lifecycle, LifecycleState):
        raise ValueError("render requires a folded, initialized story")

    description_file = description_path(lifecycle.story_id)
    directory = description_file.removesuffix("description.md")
    view_path = directory + "story.md"
    generated = state.metadata.model_copy(
        update={
            "status": lifecycle.workflow_state.state_id,
            "last_worktree": state.worktree_label,
        }
    )
    blobs = {
        path: rewrite_metadata(raw, generated, schema=schema)
        if raw is not None
        else None
        for path, raw in sorted(authored.items())
        if path != view_path
    }
    description = lifecycle.description
    body = b""
    if description is not None:
        raw = blobs.get(description_file)
        if (
            raw is None
            or canonicalize(raw, schema).canonical_sha256 != description.content_hash
        ):
            raise DocumentError(
                "authored description disagrees with the folded description"
            )
        body = _parse(raw).body

    details = {
        "State history": [
            entry.model_dump(mode="json") for entry in lifecycle.state_history
        ],
        "Estimates": {
            phase: fact.model_dump(mode="json")
            for phase, fact in lifecycle.estimates.items()
        },
    }
    evidence = state.story.domains.get("evidence")
    for name, event_type in (
        ("Guard results", "core.guard.evaluated"),
        ("Expansions", "core.expansion.recorded"),
        ("Trips", "core.trip.recorded"),
        ("Test receipts", "core.test.receipt"),
    ):
        facts = (
            evidence.facts.get(event_type, ())
            if isinstance(evidence, EvidenceState)
            else ()
        )
        details[name] = [
            fact.payload.model_dump(mode="json", by_alias=True) for fact in facts
        ]

    title = (
        description.title if description is not None else f"Story {lifecycle.story_id}"
    )
    issue = lifecycle.graduation.issue
    relations = lifecycle.relationships
    estimate = next(
        (
            lifecycle.estimates[phase]
            for phase in ("jit", "plan", "refine", "decomposition")
            if phase in lifecycle.estimates
        ),
        None,
    )
    header = {
        **generated.model_dump(by_alias=True, exclude_none=True, exclude={"status"}),
        "schema": "aitm.story/v1",
        "id": lifecycle.story_id,
        "title": title,
        "kind": lifecycle.kind,
        "state": lifecycle.workflow_state.state_id,
        "issue": issue,
        "parent": relations.parent,
        "children": relations.children,
        "blocked-by": relations.blocked_by,
        "blocking": relations.blocking,
        "estimate": estimate.model_dump(mode="json") if estimate is not None else None,
        "origin": lifecycle.graduation.source_id,
        "files": [
            path.removeprefix(directory)
            for path, raw in blobs.items()
            if path.startswith(directory) and raw is not None
        ],
        "expansions": details["Expansions"],
        "trips": details["Trips"],
    }
    heading = f"---\n{_json(header)}\n---\n\n# {title}\n\n[Issue]({issue})\n\n".encode()
    sections = "".join(
        f"<details><summary>{name}</summary>\n\n```json\n{_json(value)}\n```\n</details>\n\n"
        for name, value in details.items()
    )
    blobs[view_path] = heading + body + b"\n\n" + sections.encode()
    return blobs


def _json(value: object) -> str:
    return dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
