"""Provider-neutral input and result types for configured transition guards."""

from dataclasses import dataclass
from typing import Literal, Protocol

from aitm_core.machine.profile import WorkflowEdge
from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.lifecycle import LifecycleState
from aitm_core.models.operations import ReadExpectation, story_event_path
from aitm_core.store.backend import Blobs, Snapshot

type GuardStatus = Literal["pass", "blocked", "unavailable"]
type GuardPhase = Literal["onExit", "prepare", "edge", "onEnter"]


@dataclass(frozen=True, slots=True)
class ImplementationBinding:
    """Qualified preparation observation tied to one literal route and planning snapshot."""

    snapshot: Snapshot
    story: int
    identity: str
    generation: int
    branch: str
    source: SourceSnapshot
    target: DeliveryTarget
    attempt: str


@dataclass(frozen=True, slots=True)
class GuardDecision:
    status: GuardStatus
    code: str
    reason: str | None = None
    reads: tuple[ReadExpectation, ...] = ()
    plan_generation: int | None = None
    source: SourceSnapshot | None = None
    binding: ImplementationBinding | None = None


@dataclass(frozen=True, slots=True)
class GuardCall:
    identifier: str
    version: int
    phase: GuardPhase
    snapshot: Snapshot
    story: LifecycleState
    edge: WorkflowEdge
    blobs: Blobs
    policy_digest: str


class KindRequirements(Protocol):
    def __call__(self, request: GuardCall) -> GuardDecision: ...


class StoryExitGuards(Protocol):
    def __call__(self, request: GuardCall) -> GuardDecision: ...


class ImplementationBindingPort(Protocol):
    def __call__(self, request: GuardCall) -> ImplementationBinding | None: ...


def _design(call: GuardCall) -> GuardDecision:
    from aitm_core.documents import canonicalize
    from aitm_core.models.documents import DocumentSchema

    design = call.story.accepted_documents.get("design")
    raw = call.blobs.get(design.path) if design is not None else None
    current = (
        design is not None
        and raw is not None
        and design.policy_digest == call.policy_digest
        and canonicalize(raw, DocumentSchema()).canonical_sha256
        == design.canonical_digest
    )
    return GuardDecision("pass" if current else "blocked", "design-acceptance")


def _refinement(call: GuardCall, leaf_hours: float) -> GuardDecision:
    estimate = call.story.estimates.get("refine")
    current = (
        estimate is not None
        and estimate.agent_hours > 0
        and bool(estimate.size.strip())
        and estimate.priority in {"P0", "P1", "P2", "P3"}
        and (call.story.kind == "epic" or estimate.agent_hours <= leaf_hours)
    )
    return GuardDecision("pass" if current else "blocked", "refinement")


def core_guard(
    call: GuardCall,
    *,
    leaf_hours: float,
    kind_requirements: KindRequirements | None,
    story_exit_guards: StoryExitGuards | None,
    planning_capacity: KindRequirements | None = None,
    implementation_binding: ImplementationBindingPort | None = None,
) -> GuardDecision:
    """Evaluate the locally available facts and hold missing qualified providers."""

    def checked(ok: bool, code: str) -> GuardDecision:
        return GuardDecision("pass" if ok else "blocked", code)

    story = call.story
    match call.identifier:
        case "core.story.identity-recorded":
            return checked(bool(story.graduation.issue.strip()), "story-identity")
        case "core.story.description-complete":
            fact = story.description
            return checked(
                fact is not None
                and all(
                    value.strip()
                    for value in (
                        fact.title,
                        fact.actor,
                        fact.want,
                        fact.so_that,
                        fact.scope,
                    )
                ),
                "description",
            )
        case "core.design.accepted-current":
            return _design(call)
        case "core.refine.complete":
            return _refinement(call, leaf_hours)
        case "core.plan.admission-ready":
            for check in (
                _design(call),
                _refinement(call, leaf_hours),
                _dependencies(call),
            ):
                if check.status != "pass":
                    return check
            if kind_requirements is not None:
                return kind_requirements(call)
        case "core.plan.capacity-current":
            if planning_capacity is not None:
                return planning_capacity(call)
        case "core.plan.pickup-basis-current":
            if kind_requirements is not None:
                return kind_requirements(call)
        case "core.dev.binding-ready":
            if implementation_binding is not None:
                proof = implementation_binding(call)
                if proof is not None:
                    return GuardDecision(
                        "pass", "qualified-implementation-binding", binding=proof
                    )
        case _:
            if story_exit_guards is not None:
                return story_exit_guards(call)
    return GuardDecision(
        "unavailable", "qualified-provider-unavailable", call.identifier
    )


def _dependencies(call: GuardCall) -> GuardDecision:
    from aitm_core.events import core_reducers, fold

    for number in call.story.relationships.blocked_by:
        raw = call.blobs.get(story_event_path(number))
        if not raw:
            return GuardDecision(
                "unavailable", "dependency-evidence-missing", str(number)
            )
        state = fold(raw.splitlines(keepends=True), core_reducers())
        lifecycle = state.domains.get("lifecycle")
        if state.story_id != number or not isinstance(lifecycle, LifecycleState):
            raise ValueError("dependency history identifies another story")
        if (
            not lifecycle.transitions
            or lifecycle.transitions[-1].disposition != "delivered"
        ):
            return GuardDecision(
                "blocked", "dependency-delivery-unverified", str(number)
            )
    return GuardDecision("pass", "dependencies-delivered")
