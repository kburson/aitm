"""The v1 semantic map of reviewed child descriptors."""

from graphlib import CycleError, TopologicalSorter
from hashlib import sha256
from typing import Annotated

import rfc8785
from pydantic import Field, RootModel, model_validator

from aitm_core.models.identity import IdentityFact, SourceDescription
from aitm_core.models.lifecycle import Estimate, StoryKind

EntryKey = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")]
Text = Annotated[str, Field(min_length=1, pattern=r"\S")]


class PlanEntry(IdentityFact):
    kind: StoryKind
    description: SourceDescription
    agent_hours: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    size: Text
    priority: Annotated[str, Field(pattern=r"^P[0-3]$")]
    deliverable: Text
    verification: Text
    acceptance_criteria: tuple[Text, ...]
    dependencies: tuple[EntryKey, ...] = ()
    cross_child_commitments: tuple[Text, ...] = ()

    @model_validator(mode="after")
    def check_descriptor(self):
        if self.kind != "epic" and self.agent_hours > 4:
            raise ValueError("bounded child proposal exceeds four agent-hours")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("duplicate dependency key")
        return self

    @property
    def digest(self) -> str:
        # Preserve the original canonical entry identity when the optional
        # cross-child commitments are absent.
        exclude = (
            {"cross_child_commitments"} if not self.cross_child_commitments else None
        )
        return sha256(
            rfc8785.dumps(self.model_dump(mode="json", exclude=exclude))
        ).hexdigest()

    @property
    def proposal(self) -> Estimate:
        return Estimate(
            phase="decomposition",
            agent_hours=self.agent_hours,
            size=self.size,
            priority=self.priority,
            source="accepted-parent-plan",
        )


class DecompositionMap(RootModel[dict[EntryKey, PlanEntry]]):
    @model_validator(mode="after")
    def check_dependencies(self):
        if not self.root:
            raise ValueError("decomposition requires at least one entry")
        graph = {key: entry.dependencies for key, entry in self.root.items()}
        if any(
            dependency not in graph for keys in graph.values() for dependency in keys
        ):
            raise ValueError("decomposition has an unknown dependency entry")
        try:
            TopologicalSorter(graph).prepare()
        except CycleError as error:
            raise ValueError("decomposition contains a dependency cycle") from error
        return self
