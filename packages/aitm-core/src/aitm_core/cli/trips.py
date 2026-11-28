"""Installed trip decision and cooperative human pivot routes."""

import argparse
import os
from pathlib import Path
from uuid import uuid4

from aitm_core.machine.profile import load_profile
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
)
from aitm_core.pivots import HumanContext, pivot
from aitm_core.relationships import read_graph
from aitm_core.rules.trips import decide_trip
from aitm_core.services import ServicePorts, mutate, preflight_policy
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace


def _human_context(override):
    return HumanContext(
        interactive=os.isatty(0) and os.isatty(1),
        known_agent=any(
            os.environ.get(name)
            for name in ("CODEX_THREAD_ID", "CLAUDECODE", "GROK_SESSION_ID")
        ),
        requested_override=override,
    )


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    parser.add_argument("story", type=int)
    parser.add_argument("--expansion", choices=("continue", "fold", "abandon"))
    if route == ("pivot",):
        parser.add_argument("--reason", required=True)
        parser.add_argument("--scope-change", required=True)
        parser.add_argument("--as-human", action="store_true")
    else:
        parser.add_argument("--decision", choices=("scrap", "refactor"), required=True)
        parser.add_argument("--analysis", required=True)
        parser.add_argument("--rationale", required=True)
        parser.add_argument("--binding", required=True)
        parser.add_argument("--generation", type=int, required=True)
        parser.add_argument("--session", required=True)
    identity = uuid4().hex
    try:
        args = parser.parse_args(arguments)
        is_pivot = route == ("pivot",)
        installation, _ = _active_installation(
            Repository(Path.cwd(), "refs/heads/aitm-trip-probe")
        )
        prepared = preflight_policy(installation)
        repo = installation.repository
        if prepared.outcome != LocalOutcome.COMPLETED or prepared.policy is None:
            return CommandResult(
                operation_id=identity,
                local=prepared.outcome,
                publication=prepared.publication,
                evidence=prepared.evidence,
            )
        snapshot = repo.tip()
        if prepared.views.planning.observed_commit != snapshot.revision:
            return CommandResult(
                operation_id=identity,
                local=LocalOutcome.CONFLICT,
                publication=prepared.publication,
                evidence=("The planning snapshot advanced.",),
            )
        workspace = Workspace(installation)
        if is_pivot:
            owner = OperationOwner(actor=EventActor(kind="human", harness="aitm-cli"))
        else:
            with workspace.lock():
                workspace.require(
                    StoryRef(story=args.story),
                    args.binding,
                    args.generation,
                    args.session,
                )
            owner = OperationOwner(
                actor=EventActor(kind="tool", harness="aitm-cli", session=args.session),
                binding=args.binding,
                generation=args.generation,
            )
        policy = prepared.policy
        profile = load_profile(policy)
        graph = read_graph(repo, snapshot)
        mode = policy.config.enforcement.mode
        if is_pivot:
            operation = pivot(
                _human_context(args.as_human),
                graph,
                profile,
                mode,
                owner,
                policy.source.digest,
                args.story,
                args.reason,
                args.scope_change,
                args.expansion,
                repository=repo,
                snapshot=snapshot,
            )
        else:
            operation = decide_trip(
                repo,
                snapshot,
                graph,
                profile,
                mode,
                owner,
                policy.source.digest,
                args.story,
                args.decision,
                args.analysis,
                args.rationale,
                args.expansion,
            )

        def authorize(principal, change):
            return WriteAuthorization(
                allowed=principal == owner and change == operation.change,
                origin=AuthorityOrigin.REGISTERED,
            )

        return mutate(
            installation,
            operation,
            snapshot,
            ports=ServicePorts(write_authorization=authorize),
        ).command
    except (argparse.ArgumentError, BindingConflict, KeyError, ValueError) as error:
        outcome, reason = LocalOutcome.REFUSED, str(error)
    except (GitCommandError, OSError) as error:
        outcome, reason = LocalOutcome.UNAVAILABLE, str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(reason,))
