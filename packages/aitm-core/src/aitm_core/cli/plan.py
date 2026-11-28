"""Installed plan acceptance and provisional attempt reconciliation."""

import argparse
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from aitm_core.cli.review_import import accept
from aitm_core.events import UnavailableReducer
from aitm_core.jit import Baseline, Coverage
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.lifecycle import Estimate
from aitm_core.models.operations import (
    AuthorityOrigin,
    Operation,
    OperationOwner,
    WriteAuthorization,
)
from aitm_core.planning_evidence import (
    PlanningContext,
    PlanningRefusal,
    _result,
    _state,
    reconcile_attempt,
    record_jit,
    run_estimate,
)
from aitm_core.services import (
    ServicePorts,
    UnavailablePort,
    backend,
    mutate,
    preflight_policy,
)
from aitm_core.setup.init import _active_installation
from aitm_core.store.backend import OperationResult, Snapshot
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace


def _run(route: str, arguments: tuple[str, ...], identity: str) -> CommandResult:
    parser = argparse.ArgumentParser(prog=route, exit_on_error=False)
    parser.add_argument("--story", type=int, required=True)
    if route in ("attempt", "jit"):
        parser.add_argument("--attempt", required=True)
        parser.add_argument("--attempt-generation", type=int, required=True)
    if route == "jit":
        parser.add_argument("--baseline", required=True)
        parser.add_argument("--coverage", required=True, action="append")
        parser.add_argument("--partial", action="store_true")
    if route == "estimate":
        parser.add_argument("--phase", choices=("refine", "plan", "jit"), required=True)
        parser.add_argument("--hours", type=float, required=True)
        parser.add_argument("--size", required=True)
        parser.add_argument("--priority", required=True)
        parser.add_argument("--source", required=True)
        parser.add_argument("--rationale", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    args = parser.parse_args(arguments)
    scope = StoryRef(story=args.story)
    installation, _ = _active_installation(
        Repository(Path.cwd(), "refs/heads/aitm-plan-probe")
    )
    workspace = Workspace(installation)
    with workspace.lock():
        binding = workspace.require(scope, args.binding, args.generation, args.session)
        if route == "attempt" and (
            binding.purpose != BindingPurpose.IMPLEMENTATION
            or binding.source is None
            or binding.attempt != args.attempt
        ):
            raise BindingConflict(
                "Reconciliation requires the current implementation binding."
            )
        prepared = preflight_policy(installation)
        if prepared.outcome != LocalOutcome.COMPLETED:
            return CommandResult(
                operation_id=identity,
                local=prepared.outcome,
                publication=prepared.publication,
                evidence=prepared.evidence,
            )
        revision = prepared.views.planning.observed_commit
        if revision is None or prepared.policy is None:
            raise UnavailablePort("policy_refresh")
        store = backend(workspace.repo, installation.store)
        owner = OperationOwner(
            actor=EventActor(kind="tool", harness="aitm-cli", session=args.session),
            binding=args.binding,
            generation=args.generation,
        )

        def publish(operation: Operation, expected: Snapshot) -> OperationResult:
            def authorize(candidate, change):
                return WriteAuthorization(
                    allowed=candidate == owner and operation.change == change,
                    origin=AuthorityOrigin.REGISTERED,
                )

            return mutate(
                installation,
                operation,
                expected,
                ports=ServicePorts(write_authorization=authorize),
            )

        source = binding.source
        if route == "jit":
            if binding.purpose not in (
                BindingPurpose.PLANNING,
                BindingPurpose.IMPLEMENTATION,
                BindingPurpose.DELIVERABLE,
            ):
                raise BindingConflict(
                    "JIT requires a planning, implementation or deliverable binding."
                )
            if len(args.baseline) not in (40, 64) or any(
                character not in "0123456789abcdef" for character in args.baseline
            ):
                raise PlanningRefusal("JIT requires a full commit object ID.")
            if source is None:
                return _result(
                    identity,
                    LocalOutcome.UNAVAILABLE,
                    "JIT requires source coordinates from the current binding.",
                )
            if source.commit != args.baseline:
                raise BindingConflict("JIT baseline differs from the bound source.")
        if route == "estimate" and binding.purpose != BindingPurpose.PLANNING:
            raise BindingConflict("Estimate observations require a planning binding.")

        context = PlanningContext(
            backend=store,
            snapshot=store.read_tree(revision),
            owner=owner,
            policy_digest=prepared.policy.source.digest,
            operation_id=identity,
            at=datetime.now(UTC).isoformat(),
            publish=publish,
            scope=scope,
            source=source,
        )
        if route == "estimate":
            return _command(
                run_estimate(
                    context,
                    Estimate(
                        phase=args.phase,
                        agent_hours=args.hours,
                        size=args.size,
                        priority=args.priority,
                    ),
                    source=args.source,
                    rationale=args.rationale,
                )
            )
        if route == "jit":
            _, _, lifecycle = _state(context)
            plan = lifecycle.accepted_documents.get("plan")
            if plan is None or source is None:
                raise PlanningRefusal("No current accepted plan or baseline.")
            return _command(
                record_jit(
                    context,
                    Coverage(
                        baseline=Baseline(
                            kind="deliverable"
                            if binding.purpose == BindingPurpose.DELIVERABLE
                            else "source",
                            snapshot=source,
                        ),
                        plan_digest=plan.canonical_digest,
                        plan_generation=plan.plan_generation,
                        attempt=args.attempt,
                        attempt_generation=args.attempt_generation,
                        paths=tuple(args.coverage),
                        complete=not args.partial,
                    ),
                )
            )
        return _command(
            reconcile_attempt(
                context, attempt=args.attempt, generation=args.attempt_generation
            )
        )


def _command(result: OperationResult) -> CommandResult:
    if result.reason is not None and not result.command.evidence:
        return result.command.model_copy(update={"evidence": (result.reason,)})
    return result.command


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    if route == ("plan", "accept"):
        return accept("plan", arguments)
    identity = uuid4().hex
    if route in (("attempt", "reconcile"), ("estimate",), ("jit",)):
        try:
            return _run(route[0], arguments, identity)
        except (UnavailablePort, UnavailableReducer, GitCommandError, OSError) as error:
            return _result(identity, LocalOutcome.UNAVAILABLE, str(error))
        except (argparse.ArgumentError, BindingConflict, PlanningRefusal) as error:
            return _result(identity, LocalOutcome.REFUSED, str(error))
        except ValueError as error:
            return _result(identity, LocalOutcome.INTEGRITY_ERROR, str(error))
    return _result(
        identity,
        LocalOutcome.UNAVAILABLE,
        f"Core route is unavailable: {' '.join(route)}",
    )
