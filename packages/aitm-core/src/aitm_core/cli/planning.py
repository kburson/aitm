"""Installed planning-history inspection commands."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.store.gate import COOPERATIVE_LIMIT
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import validate_history


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    identity = uuid4().hex
    if route != ("planning", "validate"):
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(
                "The planning repair route requires the forward repair capability.",
            ),
        )
    parser = argparse.ArgumentParser(prog="aitm planning validate", exit_on_error=False)
    parser.add_argument("--anchor", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--tip")
    try:
        options = parser.parse_args(arguments)
        if options.anchor is None:
            return CommandResult(
                operation_id=identity,
                local=LocalOutcome.UNAVAILABLE,
                evidence=(
                    "Supply the trusted store anchor with --anchor.",
                    COOPERATIVE_LIMIT,
                ),
            )
        anchor = StoreAnchor.model_validate_json(options.anchor.read_bytes())
        repository = Repository(options.repository, anchor.planning_ref)
        tip = options.tip or repository.tip().revision
        report = validate_history(anchor, tip, repository=repository)
    except (argparse.ArgumentError, ValueError) as error:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.INTEGRITY_ERROR,
            evidence=(str(error),),
        )
    except (GitCommandError, OSError) as error:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(str(error),),
        )
    message = report.reason or f"Validated planning history at {report.tip}."
    return CommandResult(
        operation_id=identity,
        local=report.outcome,
        evidence=(message, COOPERATIVE_LIMIT),
    )
