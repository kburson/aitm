"""Installed scoped sync, unbind, and explicit publication reconciliation."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.entities import sync_entity
from aitm_core.models.binding import EntityRef, StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.services import ServicePorts
from aitm_core.setup.init import _active_installation
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.publication import ReplayConflict
from aitm_core.store.sync import PathSelection, reconcile_sync, sync, unbind
from aitm_core.store.workspace import BindingConflict, Workspace


def handle(
    route: tuple[str, ...],
    arguments: tuple[str, ...],
    *,
    ports: ServicePorts | None = None,
) -> CommandResult:
    services = ports or ServicePorts()
    parser = argparse.ArgumentParser(prog=f"aitm {route[0]}", exit_on_error=False)
    parser.add_argument("story", type=int, nargs="?")
    parser.add_argument("--entity")
    parser.add_argument("--binding")
    parser.add_argument("--generation", type=int)
    parser.add_argument("--session")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--delete", action="append", default=[])
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--reconcile")
    parser.add_argument("--retained")
    parser.add_argument("--expected-shared")
    parser.add_argument("--resolve", action="store_true")
    identity = uuid4().hex
    try:
        args = parser.parse_args(arguments)
        if (args.entity is None) == (args.story is None):
            raise ValueError("Select one story or entity binding scope.")
        if args.entity is not None and callable(services.entity_sync):
            result = services.entity_sync(route, arguments)
            if not isinstance(result, CommandResult):
                raise ValueError("Entity sync returned unqualified evidence.")
            return result
        if not (args.binding and args.generation and args.session):
            raise ValueError("Provide the binding identity, generation and session.")
        repo = Repository(Path.cwd(), "refs/heads/aitm-sync-probe")
        installation, _ = _active_installation(repo)
        workspace = Workspace(installation)
        scope = (
            workspace.entity_scope(args.entity, args.binding)
            if args.entity is not None
            else StoryRef(story=args.story)
        )
        binding = workspace.require(scope, args.binding, args.generation, args.session)
        selection = PathSelection(tuple(args.path), tuple(args.delete))
        if args.reconcile:
            if route != ("sync",):
                raise ValueError("Reconciliation requires sync.")
            if args.resolve and (
                not args.retained
                or not args.expected_shared
                or not (args.path or args.delete)
            ):
                raise ValueError(
                    "Resolution requires the retained revision, expected shared tip and explicit paths."
                )
            return reconcile_sync(
                workspace,
                binding,
                args.reconcile,
                args.retained,
                args.expected_shared,
                selection,
                args.resolve,
                ports=services,
            ).command
        if args.retained or args.expected_shared or args.resolve:
            raise ValueError("Resolution options require --reconcile.")
        # The normal service always attempts bounded hosted publication. --push
        # selects that same route and never dispatches a second operation.
        if isinstance(scope, EntityRef):
            return sync_entity(
                workspace,
                binding,
                selection,
                release=route == ("unbind",),
                ports=services,
            ).command
        operation = unbind if route == ("unbind",) else sync
        return operation(workspace, binding, selection, ports=services).command
    except (BindingConflict, ReplayConflict) as error:
        return CommandResult(
            operation_id=identity, local=LocalOutcome.CONFLICT, evidence=(str(error),)
        )
    except OSError as error:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(str(error),),
        )
    except (
        ValueError,
        GitCommandError,
        ValidationRejected,
        argparse.ArgumentError,
    ) as error:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.INTEGRITY_ERROR,
            evidence=(str(error),),
        )
