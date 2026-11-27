"""Versioned declarations for Core and extension capability registration."""

from collections.abc import Callable
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aitm_core.models.events import EVENT_TYPE_PATTERN
from aitm_core.models.lifecycle import RepositoryPath, StoryKind, Text
from aitm_core.providers.backlog import BacklogProvider
from aitm_core.providers.githost import GitHostProvider

Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]*$")]
Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+$")]
Version = Annotated[int, Field(gt=0)]
Placement = Literal["onEnter", "action", "onExit"]
CapabilityKind = Literal["guard", "action", "directive"]
CoverageClass = Literal["measured-engagement", "tool-duration", "gap-estimate"]


class Registration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Dependency(Registration):
    name: Name
    version: Text


class CapabilityScope(Registration):
    state_ids: tuple[Name, ...] = ()
    story_kinds: tuple[StoryKind, ...] = ()


class CapabilitySlot(Registration):
    id: Identifier
    version: Version
    kind: CapabilityKind
    placements: Annotated[tuple[Placement, ...], Field(min_length=1)]
    scope: CapabilityScope = CapabilityScope()
    execution: Literal["requested", "queued", "observed"] | None = None
    required_facts: tuple[Identifier, ...] = ()
    produced_evidence: tuple[Identifier, ...] = ()

    @model_validator(mode="after")
    def check_placement(self) -> Self:
        allowed = {"onEnter", "onExit"} if self.kind == "guard" else {"action"}
        if len(set(self.placements)) != len(self.placements):
            raise ValueError("duplicate capability placement")
        if not allowed.issuperset(self.placements):
            raise ValueError(f"invalid placement for {self.kind}")
        if (self.kind == "action") != (self.execution is not None):
            raise ValueError(
                "only actions declare an execution mode, and all actions require one"
            )
        return self


class DirectiveRegistration(Registration):
    slot: CapabilitySlot
    markdown: RepositoryPath
    requested_evidence: tuple[Text, ...] = ()

    @model_validator(mode="after")
    def check_directive(self) -> Self:
        if self.slot.kind != "directive" or not self.markdown.endswith(".md"):
            raise ValueError(
                "directive requires a directive slot and a Markdown source"
            )
        return self


class EventRegistration(Registration):
    id: Annotated[str, Field(pattern=EVENT_TYPE_PATTERN)]
    version: Version
    model: type[BaseModel]


class ActivityProducerRegistration(Registration):
    id: Identifier
    version: Version
    measurement_contract: Text
    coverage_class: CoverageClass


class ProducerRef(Registration):
    id: Identifier
    version: Version
    measurement_contract: Text
    coverage_class: CoverageClass


class InitStepRegistration(Registration):
    id: Identifier
    version: Version
    factory: Callable[[], object]


class Extension(Registration):
    """Installed declaration. Construction and lookup leave all factories lazy."""

    name: Name
    namespace: Name
    version: Text
    requires_core: Text
    dependencies: tuple[Dependency, ...] = ()
    capabilities: tuple[CapabilitySlot, ...] = ()
    directives: tuple[DirectiveRegistration, ...] = ()
    event_types: tuple[EventRegistration, ...] = ()
    activity_producers: tuple[ActivityProducerRegistration, ...] = ()
    init_steps: tuple[InitStepRegistration, ...] = ()
    owned_paths: tuple[Text, ...] = ()
    cli_factory: Callable[[], object] | None = None
    backlog_factory: Callable[[], BacklogProvider] | None = None
    githost_factory: Callable[[], GitHostProvider] | None = None
    config_model: type[BaseModel] | None = None
