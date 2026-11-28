"""Installed expansion command."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.graduation import GraduationConflict
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.operations import OperationOwner
from aitm_core.providers.identity import (
    IdentityAuthority,
    IdentityConflict,
    IdentityProvider,
)
from aitm_core.relationships import GraphConflict
from aitm_core.rules.expansion import expand
from aitm_core.services import ServicePorts, expansion_graduation
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace


class ExpandedCommand(CommandResult):
    issue: int | None = None


def handle(
    route: tuple[str, ...],
    arguments: tuple[str, ...],
    *,
    ports: ServicePorts | None = None,
    identity_provider: IdentityProvider | None = None,
) -> CommandResult:
    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    parser.add_argument("story", type=int)
    parser.add_argument("--kind", choices=("defect", "story"), required=True)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    identity = uuid4().hex
    try:
        args = parser.parse_args(arguments)
        installation, _ = _active_installation(
            Repository(Path.cwd(), "refs/heads/aitm-expansion-probe")
        )
        workspace = Workspace(installation)
        with workspace.lock():
            binding = workspace.require(
                StoryRef(story=args.story), args.binding, args.generation, args.session
            )
        if binding.purpose not in (
            BindingPurpose.IMPLEMENTATION,
            BindingPurpose.PLANNING,
        ):
            raise BindingConflict(
                "Expansion requires the current implementation holder."
            )
        owner = OperationOwner(
            actor=EventActor(kind="tool", harness="aitm-cli", session=args.session),
            binding=binding.identity,
            generation=binding.generation,
        )
        external = (
            IdentityAuthority(installation, identity_provider)
            if identity_provider is not None
            else None
        )
        result = expand(
            expansion_graduation(installation, owner, ports),
            args.story,
            args.draft,
            args.kind,
            args.reason,
            external=external,
        )
        return ExpandedCommand(
            **result.command.model_dump(by_alias=False),
            issue=result.issue.number if result.issue is not None else None,
        )
    except (
        BindingConflict,
        GraduationConflict,
        GraphConflict,
        IdentityConflict,
    ) as error:
        outcome, reason = LocalOutcome.CONFLICT, str(error)
    except (argparse.ArgumentError, ValueError) as error:
        outcome, reason = LocalOutcome.REFUSED, str(error)
    except (GitCommandError, OSError) as error:
        outcome, reason = LocalOutcome.UNAVAILABLE, str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(reason,))
