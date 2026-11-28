"""Validate configured workflow authority boundaries before offering transitions."""

from collections import defaultdict
from dataclasses import dataclass
from typing import get_args

from aitm_core.ext.api import (
    CapabilityKind,
    CapabilitySlot,
    DirectiveRegistration,
    Placement,
)
from aitm_core.ext.registry import Registry, RegistryStatus
from aitm_core.machine.profile import (
    LifecycleDestinations,
    RecoveryDestinations,
    WorkflowEdge,
    WorkflowProfile,
)
from aitm_core.models.lifecycle import StoryKind


@dataclass(frozen=True, slots=True)
class DeliveryContract:
    """Authority bindings supplied by Core, independently of the profile document."""

    id: str
    implementation: str
    review: str
    pickup_guard: str
    binding_guard: str
    candidate_guard: str
    rework_guard: str
    closeout_guard: str
    terminal_guard: str
    delivered_guard: str
    start: str
    rework: str
    reopen: str
    finalize: str
    entry_facts: frozenset[str] = frozenset()


HOSTED_DELIVERY = DeliveryContract(
    id="core.hosted-delivery/v1",
    implementation="dev",
    review="review",
    pickup_guard="core.plan.pickup-basis-current",
    binding_guard="core.dev.binding-ready",
    candidate_guard="core.dev.review-candidate-current",
    rework_guard="core.review.rework-authorized",
    closeout_guard="core.closeout.complete",
    terminal_guard="core.closeout.terminal-disposition-valid",
    delivered_guard="core.delivery.verified",
    start="core.attempt.begin-or-resume",
    rework="core.attempt.resume-for-rework",
    reopen="core.story.reopen",
    finalize="core.story.finalize-delivery",
)


@dataclass(frozen=True, slots=True)
class ProfileProblem:
    code: str
    location: str
    reason: str


@dataclass(frozen=True, slots=True)
class ProfileValidation:
    lifecycle: LifecycleDestinations
    recovery: RecoveryDestinations
    problems: tuple[ProfileProblem, ...]

    @property
    def valid(self) -> bool:
        return all(
            problem.code == "capability-unavailable" for problem in self.problems
        )

    @property
    def available(self) -> bool:
        return not self.problems


def _check_slots(profile: WorkflowProfile, registry: Registry) -> list[ProfileProblem]:
    problems: list[ProfileProblem] = []

    def check(
        identifiers: tuple[str, ...],
        placement: Placement,
        state: str,
        kinds: tuple[CapabilityKind, ...],
        location: str,
    ) -> None:
        for identifier in identifiers:
            resolved = registry.resolve(identifier)
            registration = resolved.registration
            if resolved.status is not RegistryStatus.ENABLED or registration is None:
                problems.append(
                    ProfileProblem(
                        "capability-unavailable",
                        location,
                        resolved.reason or identifier,
                    )
                )
                continue
            slot = (
                registration.slot
                if isinstance(registration, DirectiveRegistration)
                else registration
            )
            if slot.kind not in kinds:
                problems.append(ProfileProblem("slot-kind", location, identifier))
            elif placement not in slot.placements:
                problems.append(ProfileProblem("slot-placement", location, identifier))
            elif slot.scope.state_ids and state not in slot.scope.state_ids:
                problems.append(ProfileProblem("slot-scope", location, identifier))

    for state in profile.states:
        check(state.on_enter, "onEnter", state.id, ("guard",), f"{state.id}.onEnter")
        check(
            state.action,
            "action",
            state.id,
            ("action", "directive"),
            f"{state.id}.action",
        )
        check(state.on_exit, "onExit", state.id, ("guard",), f"{state.id}.onExit")
    for edge in profile.transitions:
        location = f"{edge.source}->{edge.target}"
        check(edge.prepare, "action", edge.source, ("action",), f"{location}.prepare")
        check(edge.guards, "onExit", edge.source, ("guard",), f"{location}.guards")
    return problems


def _check_predecessors(
    profile: WorkflowProfile, registry: Registry, contract: DeliveryContract
) -> list[ProfileProblem]:
    """Compute which facts can be established on every incoming route for each kind."""

    states = {state.id: state for state in profile.states}
    transitions = profile.transitions
    initial = next(iter(states))
    entries = {
        initial,
        profile.lifecycle.reopen_design,
        profile.lifecycle.reopen_plan,
        profile.recovery.design_rework,
        profile.recovery.trip,
        profile.recovery.scope_pivot,
    }
    incoming: dict[str, list[WorkflowEdge]] = defaultdict(list)
    reachable = entries.copy()
    pending = list(entries)
    outgoing: dict[str, list[WorkflowEdge]] = defaultdict(list)
    for edge in transitions:
        outgoing[edge.source].append(edge)
    while pending:
        for edge in outgoing[pending.pop()]:
            incoming[edge.target].append(edge)
            if edge.target not in reachable:
                reachable.add(edge.target)
                pending.append(edge.target)

    registrations: dict[str, CapabilitySlot] = {}

    def selected(identifiers: tuple[str, ...], kind: StoryKind):
        for identifier in identifiers:
            if identifier not in registrations:
                registration = registry.resolve(identifier).registration
                if registration is None:
                    continue
                registrations[identifier] = (
                    registration.slot
                    if isinstance(registration, DirectiveRegistration)
                    else registration
                )
            slot = registrations[identifier]
            if not slot.scope.story_kinds or kind in slot.scope.story_kinds:
                yield slot

    problems = []

    def sequence(
        identifiers: tuple[str, ...],
        baseline: frozenset[str],
        kind: StoryKind,
        location: str,
        *,
        report: bool,
    ) -> frozenset[str]:
        facts = set(baseline)
        for slot in selected(identifiers, kind):
            missing = set(slot.required_facts) - facts
            if report and missing:
                reason = f"{slot.id} for {kind} requires {', '.join(sorted(missing))}"
                problems.append(ProfileProblem("predecessor-fact", location, reason))
            if not missing:
                facts.update(slot.produced_evidence)
        return frozenset(facts)

    def on_edge(edge: WorkflowEdge, kind: StoryKind, *, report: bool) -> frozenset[str]:
        source = states[edge.source]
        if edge.kind in {"reopen", "rework"}:
            # Dedicated operations may invalidate evidence from the old route.
            baseline = contract.entry_facts
            rules = (*edge.prepare, *edge.guards)
        else:
            baseline = state_facts[edge.source]
            rules = (
                *source.on_enter,
                *source.action,
                *source.on_exit,
                *edge.prepare,
                *edge.guards,
            )
        return sequence(
            rules, baseline, kind, f"{edge.source}->{edge.target}", report=report
        )

    for kind in get_args(StoryKind):
        state_facts = dict.fromkeys(states, contract.entry_facts)
        while True:
            updated = {}
            for state in states:
                facts = [on_edge(edge, kind, report=False) for edge in incoming[state]]
                if state in entries or not facts:
                    facts.append(contract.entry_facts)
                updated[state] = frozenset.intersection(*facts)
            if updated == state_facts:
                break
            state_facts = updated

        for state_id, state in states.items():
            if state_id in reachable:
                sequence(
                    (*state.on_enter, *state.action),
                    state_facts[state_id],
                    kind,
                    state_id,
                    report=True,
                )
        for edge in transitions:
            if edge.source in reachable:
                on_edge(edge, kind, report=True)
    return list(dict.fromkeys(problems))


def _reachable(
    adjacency: dict[str, list[str]], start: str, *, excluding: str
) -> set[str]:
    visited = {excluding}
    pending = [start]
    while pending:
        state = pending.pop()
        if state in visited:
            continue
        visited.add(state)
        pending.extend(adjacency.get(state, ()))
    return visited - {excluding}


def _check_contract(
    profile: WorkflowProfile, contract: DeliveryContract
) -> list[ProfileProblem]:
    problems: list[ProfileProblem] = []
    states = {state.id: state for state in profile.states}
    ordered = list(states)
    dev, review, terminal = (
        contract.implementation,
        contract.review,
        profile.lifecycle.terminal,
    )
    if profile.contract != contract.id or not {dev, review}.issubset(states):
        return [
            ProfileProblem(
                "contract", profile.id, "delivery contract or states mismatch"
            )
        ]
    initial = ordered[0]
    if not 0 < ordered.index(dev) < ordered.index(review) < ordered.index(terminal):
        return [
            ProfileProblem("contract", profile.id, "delivery states are out of order")
        ]

    before_dev = set(ordered[: ordered.index(dev)])
    for purpose, destination in {
        "reopen_design": profile.lifecycle.reopen_design,
        "reopen_plan": profile.lifecycle.reopen_plan,
        "design_rework": profile.recovery.design_rework,
        "trip": profile.recovery.trip,
        "scope_pivot": profile.recovery.scope_pivot,
    }.items():
        if destination not in before_dev:
            problems.append(
                ProfileProblem("recovery-destination", purpose, destination)
            )
    if profile.recovery.implementation_rework != dev:
        problems.append(
            ProfileProblem("recovery-destination", "implementation_rework", dev)
        )

    for state_id in ordered[ordered.index(review) + 1 : ordered.index(terminal)]:
        state = states[state_id]
        if (
            contract.closeout_guard in state.on_exit
            or any(
                edge.source == state_id and contract.closeout_guard in edge.guards
                for edge in profile.transitions
            )
        ) and contract.delivered_guard not in state.on_enter:
            problems.append(
                ProfileProblem("verified-delivery", state_id, contract.delivered_guard)
            )

    adjacency: dict[str, list[str]] = defaultdict(list)
    reserved = {contract.start, contract.rework, contract.reopen, contract.finalize}
    for edge in profile.transitions:
        source, target = edge.source, edge.target
        location = f"{source}->{target}"
        if edge.kind != "reopen":
            adjacency[source].append(target)
        source_guards = {*states[source].on_exit, *edge.guards}
        target_guards = states[target].on_enter
        expected = None
        if edge.kind == "reopen":
            expected = contract.reopen
            if edge.operation != expected:
                problems.append(ProfileProblem("reopen", location, expected))
        elif edge.kind == "rework":
            expected = contract.rework
            if (
                source != review
                or target != dev
                or edge.operation != expected
                or contract.rework_guard not in edge.guards
                or contract.binding_guard not in target_guards
            ):
                problems.append(
                    ProfileProblem("implementation-rework", location, expected)
                )
        elif target == dev:
            expected = contract.start
            if (
                edge.operation != expected
                or contract.pickup_guard not in source_guards
                or contract.binding_guard not in target_guards
            ):
                problems.append(ProfileProblem("attempt-start", location, expected))
        elif target == terminal:
            expected = contract.finalize
            if (
                edge.operation != expected
                or contract.closeout_guard not in source_guards
                or contract.terminal_guard not in target_guards
            ):
                problems.append(
                    ProfileProblem("terminal-finalization", location, expected)
                )
        if target == review and contract.candidate_guard not in target_guards:
            problems.append(
                ProfileProblem("exact-candidate", location, contract.candidate_guard)
            )
        if edge.operation in reserved and edge.operation != expected:
            problems.append(
                ProfileProblem("operation-placement", location, edge.operation)
            )

    entries = dict.fromkeys(
        (
            initial,
            profile.lifecycle.reopen_design,
            profile.lifecycle.reopen_plan,
            profile.recovery.design_rework,
            profile.recovery.trip,
            profile.recovery.scope_pivot,
        )
    )
    for start in entries:
        if review in _reachable(adjacency, start, excluding=dev):
            problems.append(ProfileProblem("attempt-bypass", start, review))
        if terminal in _reachable(adjacency, start, excluding=review):
            problems.append(ProfileProblem("review-bypass", start, terminal))
    return problems


def validate_profile(
    profile: WorkflowProfile, registry: Registry, contract: DeliveryContract
) -> ProfileValidation:
    """Check structural obligations in every mode, independently of runtime proof."""

    problems = [*_check_contract(profile, contract), *_check_slots(profile, registry)]
    if not problems:
        problems.extend(_check_predecessors(profile, registry, contract))
    return ProfileValidation(
        lifecycle=profile.lifecycle,
        recovery=profile.recovery,
        problems=tuple(problems),
    )
