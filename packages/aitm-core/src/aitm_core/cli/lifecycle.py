"""Installed promote and demote routes over one qualified workflow profile."""

import argparse
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from aitm_core.ext.api import CapabilitySlot
from aitm_core.ext.registry import load_extensions
from aitm_core.machine.guards import core_guard
from aitm_core.machine.obligations import HOSTED_DELIVERY
from aitm_core.machine.profile import load_profile
from aitm_core.machine.transitions import (
    TransitionRequest,
    preflight_transition,
    transition,
)
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.operations import AuthorityOrigin, WriteAuthorization
from aitm_core.services import (
    ServicePorts,
    UnavailablePort,
    backend,
    mutate,
    preflight_policy,
)
from aitm_core.setup.init import _active_installation
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.sync import PathSelection, sync
from aitm_core.store.workspace import BindingConflict, Workspace

CORE_GUARDS = (
    "core.story.identity-recorded",
    "core.story.description-complete",
    "core.design.accepted-current",
    "core.refine.complete",
    "core.plan.admission-ready",
    "core.plan.capacity-current",
    HOSTED_DELIVERY.pickup_guard,
    HOSTED_DELIVERY.binding_guard,
    HOSTED_DELIVERY.candidate_guard,
    HOSTED_DELIVERY.rework_guard,
    HOSTED_DELIVERY.closeout_guard,
    HOSTED_DELIVERY.terminal_guard,
    HOSTED_DELIVERY.delivered_guard,
)
BUILTINS = tuple(
    CapabilitySlot(id=rule, version=1, kind="guard", placements=("onEnter", "onExit"))
    for rule in CORE_GUARDS
)


def _run(route, args, identity, ports):
    from aitm_core.models.operations import OperationOwner

    installation, _ = _active_installation(
        Repository(Path.cwd(), "refs/heads/aitm-lifecycle-probe")
    )
    workspace = Workspace(installation)
    scope = StoryRef(story=args.story)

    def binding():
        return workspace.require(scope, args.binding, args.generation, args.session)

    with workspace.lock():
        lease = binding()
        if lease.purpose not in (
            BindingPurpose.PLANNING,
            BindingPurpose.IMPLEMENTATION,
        ):
            raise BindingConflict(
                "Transition requires a current planning or implementation binding."
            )

    staged = preflight_policy(installation, ports=ports)
    if staged.outcome != LocalOutcome.COMPLETED or staged.policy is None:
        return CommandResult(
            operation_id=identity,
            local=staged.outcome,
            publication=staged.publication,
            evidence=staged.evidence,
        )
    policy = staged.policy
    store = backend(workspace.repo, installation.store, ports=ports)
    profile = load_profile(policy)
    registry = load_extensions(policy, ports.extension_declarations, builtins=BUILTINS)
    owner = OperationOwner(
        actor=EventActor(kind="tool", harness="aitm-cli", session=args.session),
        binding=args.binding,
        generation=args.generation,
    )

    def latest():
        prepared = preflight_policy(installation, ports=ports)
        revision = prepared.views.planning.observed_commit
        if (
            prepared.outcome != LocalOutcome.COMPLETED
            or prepared.policy is None
            or revision is None
            or prepared.policy.revision != policy.revision
            or prepared.policy.workflow.digest != profile.source.digest
        ):
            raise UnavailablePort("policy_refresh")
        return store.read_tree(revision)

    def implementation_head_is_current():
        if lease.branch is None or lease.source is None:
            return False
        observed = workspace.repo._run("show-ref", "--verify", "--hash", lease.branch)
        if (
            observed.returncode != 0
            or observed.stdout.strip().decode() != lease.source.commit
        ):
            return False
        return (
            workspace.repo._git("rev-parse", f"{lease.source.commit}^{{tree}}")
            .strip()
            .decode()
            == lease.source.tree
        )

    def apply(operation, expected):
        with workspace.lock():
            current = binding()
            if (current.purpose, current.source, current.branch, current.attempt) != (
                lease.purpose,
                lease.source,
                lease.branch,
                lease.attempt,
            ):
                raise BindingConflict("Transition binding changed before mutation.")
            if any(
                guard.guard == HOSTED_DELIVERY.binding_guard and guard.ok
                for guard in operation.guards
            ):
                if not implementation_head_is_current():
                    raise BindingConflict(
                        "Pinned implementation source changed before mutation."
                    )

            def authorize(candidate, change):
                return WriteAuthorization(
                    allowed=candidate == owner and change == operation.change,
                    origin=AuthorityOrigin.REGISTERED,
                )

            return mutate(
                installation,
                operation,
                expected,
                ports=replace(ports, write_authorization=authorize),
            )

    def observe_binding(call):
        if (
            lease.purpose != BindingPurpose.IMPLEMENTATION
            or not callable(ports.implementation_binding)
            or not implementation_head_is_current()
        ):
            return None
        return ports.implementation_binding(call, lease)

    def guard(call):
        return core_guard(
            call,
            leaf_hours=policy.config.limits.leaf_agent_hours,
            implementation_binding=observe_binding,
            planning_capacity=ports.planning_capacity
            if callable(ports.planning_capacity)
            else None,
            kind_requirements=ports.kind_requirements
            if callable(ports.kind_requirements)
            else None,
            story_exit_guards=ports.story_exit_guards
            if callable(ports.story_exit_guards)
            else None,
        )

    def authored():
        return sync(workspace, binding(), PathSelection(), ports=ports).command

    request = TransitionRequest(
        story=scope.story,
        operation_id=identity,
        owner=owner,
        at=datetime.now(UTC).isoformat(),
        backend=store,
        profile=profile,
        registry=registry,
        policy_digest=policy.source.digest,
        mode=policy.config.enforcement.mode,
        guard=guard,
        allowance_millis=max(1, round(policy.config.limits.leaf_agent_hours * 3600000)),
        direction="forward" if route == ("promote",) else "rework",
        target=args.target,
        reason=args.reason,
        source=lease.source,
        binding_ref=lease.branch,
        binding_attempt=lease.attempt,
        latest_snapshot=latest,
        sync=authored,
        transact=apply,
    )
    request = replace(
        request,
        before_sync=lambda: preflight_transition(request, ports.attempt_preflight),
    )
    return transition(request).command


def handle(
    route: tuple[str, ...],
    arguments: tuple[str, ...],
    *,
    ports: ServicePorts | None = None,
) -> CommandResult:
    identity = uuid4().hex
    parser = argparse.ArgumentParser(prog=f"aitm {route[0]}", exit_on_error=False)
    parser.add_argument("story", type=int)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--target")
    parser.add_argument("--reason")
    try:
        return _run(
            route, parser.parse_args(arguments), identity, ports or ServicePorts()
        )
    except BindingConflict as error:
        outcome, reason = LocalOutcome.CONFLICT, str(error)
    except (OSError, UnavailablePort) as error:
        outcome, reason = LocalOutcome.UNAVAILABLE, str(error)
    except (
        ValueError,
        GitCommandError,
        ValidationRejected,
        argparse.ArgumentError,
    ) as error:
        outcome, reason = LocalOutcome.INTEGRITY_ERROR, str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(reason,))
