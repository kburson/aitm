"""Installed managed verification entry point."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.verification.run import run_verification


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = argparse.ArgumentParser(prog="aitm test", exit_on_error=False)
    parser.add_argument("story", type=int)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    try:
        args = parser.parse_args(arguments)
        installation, _ = _active_installation(
            Repository(Path.cwd(), "refs/heads/aitm-test-probe")
        )
        return run_verification(
            installation, args.story, args.binding, args.generation, args.session
        )
    except (argparse.ArgumentError, OSError, ValueError, GitCommandError) as error:
        return CommandResult(
            operation_id=uuid4().hex, local=LocalOutcome.REFUSED, evidence=(str(error),)
        )
