"""Installed adapter for scoped worktree bindings."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.models.attempts import BindingPurpose, SourceSnapshot
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.setup.init import _active_installation
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import (
    AuthorityUnavailable,
    BindingConflict,
    BindRequest,
    Workspace,
)


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = argparse.ArgumentParser(prog="aitm bind", exit_on_error=False)
    parser.add_argument("story", type=int)
    parser.add_argument("--session", required=True)
    parser.add_argument("--path", action="append", default=[])
    purpose = parser.add_mutually_exclusive_group()
    for option in ("implementation", "deliverable", "evidence"):
        purpose.add_argument(
            f"--{option}", action="store_const", const=option, dest="purpose"
        )
    parser.add_argument("--attempt")
    parser.add_argument("--branch")
    parser.add_argument(
        "--branch-mode",
        choices=("existing", "create", "scrap", "refactor"),
        default="existing",
    )
    parser.add_argument("--commit")
    parser.add_argument("--tree")
    parser.add_argument("--recover")
    parser.add_argument("--generation", type=int)
    identity = uuid4().hex
    try:
        options = parser.parse_args(arguments)
        if bool(options.commit) != bool(options.tree) or bool(options.recover) != (
            options.generation is not None
        ):
            raise ValueError("Provide complete source or recovery coordinates.")
        repo = Repository(Path.cwd(), "refs/heads/aitm-binding-probe")
        installation, _ = _active_installation(repo)
        source = (
            SourceSnapshot(commit=options.commit, tree=options.tree)
            if options.commit
            else None
        )
        request = BindRequest(
            installation,
            StoryRef(story=options.story),
            BindingPurpose(options.purpose or "planning"),
            options.session,
            tuple(options.path),
            options.attempt,
            options.branch,
            source,
            options.branch_mode,
        )
        workspace = Workspace(installation)
        if options.recover is None:
            binding = workspace.bind(request)
            evidence = (binding.model_dump_json(),)
        else:
            binding, export = workspace.recover_binding(
                request, options.recover, options.generation
            )
            evidence = (binding.model_dump_json(), str(export))
        return CommandResult(
            operation_id=binding.identity,
            local=LocalOutcome.COMPLETED,
            evidence=evidence,
        )
    except BindingConflict as error:
        return CommandResult(
            operation_id=identity, local=LocalOutcome.CONFLICT, evidence=(str(error),)
        )
    except (OSError, AuthorityUnavailable) as error:
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
