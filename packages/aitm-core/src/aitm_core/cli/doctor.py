"""Installed adapter for read-only Core readiness."""

from pathlib import Path
from uuid import uuid4

from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.setup.doctor import doctor
from aitm_core.setup.init import _active_installation
from aitm_core.setup.journal import read_proposal, state_directory
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    operation = uuid4().hex
    try:
        if arguments:
            raise ValueError("Run aitm doctor from the desired repository worktree.")
        repo = Repository(Path.cwd(), "refs/heads/aitm-doctor-probe")
        if not (state_directory(repo) / "installation.json").exists():
            proposal = read_proposal(repo)
            return CommandResult(
                operation_id=operation,
                local=LocalOutcome.COMPLETED if proposal else LocalOutcome.UNAVAILABLE,
                publication=PublicationOutcome.PENDING
                if proposal
                else PublicationOutcome.NOT_APPLICABLE,
                pending=("installation",),
                evidence=(
                    "Bootstrap awaits committed policy or planning publication."
                    if proposal
                    else "Installation authority is unavailable. Run aitm init.",
                ),
            )
        installation, _ = _active_installation(repo)
        report = doctor(installation)
        return CommandResult(
            operation_id=operation,
            local=LocalOutcome.COMPLETED,
            pending=report.pending,
            evidence=report.evidence,
        )
    except (OSError, ValueError, GitCommandError, ValidationRejected) as error:
        return CommandResult(
            operation_id=operation,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(str(error),),
        )
