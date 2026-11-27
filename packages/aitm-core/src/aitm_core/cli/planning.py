"""Installed planning-history inspection commands."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    StoreAnchor,
)
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
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--installation", type=Path)
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
        if options.refresh:
            return _refresh_validation(identity, repository, anchor, options)
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


def _refresh_validation(
    identity: str,
    repository: Repository,
    anchor: StoreAnchor,
    options: argparse.Namespace,
) -> CommandResult:
    from aitm_core.services import load_installation, preflight_policy
    from aitm_core.store.continuity import ContinuityStatus
    from aitm_core.store.fetch import Freshness

    installation = load_installation(repository, anchor, options.installation)
    preflight = preflight_policy(installation)
    views = preflight.views
    shared = views.shared
    incomplete = views.code_freshness in (Freshness.STALE, Freshness.UNKNOWN) or (
        shared is not None
        and (
            shared.status in (ContinuityStatus.STALE, ContinuityStatus.UNKNOWN)
            or shared.local_diverged
        )
    )
    publication = (
        PublicationOutcome.PENDING if incomplete else PublicationOutcome.NOT_APPLICABLE
    )
    evidence = (*preflight.evidence, COOPERATIVE_LIMIT)
    if preflight.outcome != LocalOutcome.COMPLETED:
        return CommandResult(
            operation_id=identity,
            local=preflight.outcome,
            publication=publication,
            evidence=evidence,
        )
    admitted = installation.policy_ref(views.local)
    tip = options.tip or views.planning.observed_commit
    if admitted is None or tip is None:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            publication=publication,
            evidence=(*evidence, "No admitted code and planning view is available."),
        )
    validator_anchor = anchor.model_copy(update={"code_default_ref": admitted})
    report = validate_history(validator_anchor, tip, repository=repository)
    message = report.reason or f"Validated planning history at {report.tip}."
    return CommandResult(
        operation_id=identity,
        local=report.outcome,
        publication=publication,
        evidence=(*evidence, message),
    )
