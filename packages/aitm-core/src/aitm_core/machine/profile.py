"""Parse the versioned, ordered workflow document pinned by committed policy."""

from itertools import pairwise
from tomllib import TOMLDecodeError, loads
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from aitm_core.config import PolicySnapshot
from aitm_core.ext.api import Identifier, Name
from aitm_core.models.config import Name as Nonblank
from aitm_core.models.config import Oid
from aitm_core.models.events import DIGEST

type ContractID = Annotated[
    str, Field(pattern=r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+/v[1-9][0-9]*$")
]


class ProfileUnavailable(ValueError):
    """The pinned workflow bytes do not establish a supported profile."""


class _ProfileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProfileSource(_ProfileRecord):
    path: Nonblank
    revision: Oid
    tree: Oid
    digest: DIGEST


class WorkflowState(_ProfileRecord):
    id: Name
    label: Nonblank
    on_enter: tuple[Identifier, ...] = Field(default=(), alias="onEnter")
    action: tuple[Identifier, ...] = ()
    on_exit: tuple[Identifier, ...] = Field(default=(), alias="onExit")

    @model_validator(mode="after")
    def check_slots(self) -> Self:
        for slot in (self.on_enter, self.action, self.on_exit):
            if len(set(slot)) != len(slot):
                raise ValueError(f"duplicate rule in a slot of state {self.id}")
        return self


class WorkflowEdge(_ProfileRecord):
    source: Name = Field(alias="from")
    target: Name = Field(alias="to")
    kind: Literal["normal", "rework", "reopen", "terminal"] = "normal"
    prepare: tuple[Identifier, ...] = ()
    guards: tuple[Identifier, ...] = ()
    operation: Identifier | None = None

    @model_validator(mode="after")
    def check_slots(self) -> Self:
        if len(set(self.prepare)) != len(self.prepare) or len(set(self.guards)) != len(
            self.guards
        ):
            raise ValueError("duplicate rule in an edge slot")
        return self


class LifecycleDestinations(_ProfileRecord):
    terminal: Name
    non_delivery: Name
    reopen_design: Name
    reopen_plan: Name


class RecoveryDestinations(_ProfileRecord):
    design_rework: Name
    implementation_rework: Name
    trip: Name
    scope_pivot: Name


class WorkflowProfile(_ProfileRecord):
    schema_version: Literal["aitm.workflow/v1"] = Field(alias="schema")
    id: Name
    contract: ContractID
    source: ProfileSource
    lifecycle: LifecycleDestinations
    recovery: RecoveryDestinations
    states: Annotated[tuple[WorkflowState, ...], Field(min_length=1)]
    edges: tuple[WorkflowEdge, ...] = ()

    @property
    def _ordinary_pairs(self) -> tuple[tuple[str, str], ...]:
        ordered = [state.id for state in self.states]
        terminal = ordered.index(self.lifecycle.terminal)
        return tuple(pairwise(ordered[: terminal + 1]))

    @property
    def ordinary_edges(self) -> tuple[WorkflowEdge, ...]:
        declared = {(edge.source, edge.target): edge for edge in self.edges}
        return tuple(
            declared[(source, target)]
            if (source, target) in declared
            else WorkflowEdge.model_validate({"from": source, "to": target})
            for source, target in self._ordinary_pairs
        )

    @property
    def transitions(self) -> tuple[WorkflowEdge, ...]:
        ordinary = self.ordinary_edges
        pairs = set(self._ordinary_pairs)
        return (
            *ordinary,
            *(edge for edge in self.edges if (edge.source, edge.target) not in pairs),
        )

    @model_validator(mode="after")
    def check_graph(self) -> Self:
        ids = {state.id for state in self.states}
        if len(ids) != len(self.states):
            raise ValueError("duplicate state ID")
        for destinations in (self.lifecycle, self.recovery):
            for purpose, destination in destinations.model_dump().items():
                if destination not in ids:
                    raise ValueError(f"{purpose} refers to unknown state {destination}")
        terminal = self.lifecycle.terminal
        if self.lifecycle.non_delivery != terminal:
            raise ValueError("non_delivery must target the terminal state")

        pairs: set[tuple[str, str]] = set()
        ordinary = set(self._ordinary_pairs)
        for edge in self.edges:
            pair = edge.source, edge.target
            if not ids.issuperset(pair):
                raise ValueError(f"edge {pair} refers to an unknown state")
            if pair in pairs:
                raise ValueError(f"duplicate edge {pair}")
            pairs.add(pair)
            if edge.source == edge.target:
                raise ValueError(f"edge {pair} aliases its own state")
            if edge.source == terminal and edge.kind != "reopen":
                raise ValueError(
                    "the terminal state only permits a declared reopen edge"
                )
            if edge.kind == "normal" and pair not in ordinary:
                raise ValueError("normal edges must follow the ordered state sequence")
            if pair in ordinary and edge.kind not in ("normal", "terminal"):
                raise ValueError(
                    "a nonordinary edge cannot replace an ordered transition"
                )
            if edge.kind == "terminal" and edge.target != terminal:
                raise ValueError(
                    "a terminal edge must target the declared terminal state"
                )
            if edge.kind == "reopen" and (
                edge.source != terminal
                or edge.target
                not in (self.lifecycle.reopen_design, self.lifecycle.reopen_plan)
            ):
                raise ValueError(
                    "a reopen edge must use a declared terminal recovery route"
                )
        return self


def load_profile(policy_snapshot: PolicySnapshot) -> WorkflowProfile:
    """Read only the workflow already pinned by the C07 policy port."""
    workflow = policy_snapshot.workflow
    if workflow.path != policy_snapshot.config.workflow.file:
        raise ProfileUnavailable(
            f"{workflow.path}: differs from the configured workflow path"
        )
    try:
        document = loads(workflow.content.decode("utf-8"))
        if "source" in document:
            raise ProfileUnavailable(
                "profile source is derived from the committed snapshot"
            )
        source = ProfileSource(
            path=workflow.path,
            revision=policy_snapshot.revision,
            tree=policy_snapshot.tree,
            digest=workflow.digest,
        )
        return WorkflowProfile.model_validate(document | {"source": source})
    except (
        UnicodeDecodeError,
        TOMLDecodeError,
        ValidationError,
        ProfileUnavailable,
    ) as error:
        raise ProfileUnavailable(f"{workflow.path}: {error}") from error
