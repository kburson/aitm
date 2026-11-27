"""Installed adapter for the structured description operation."""

import argparse
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from aitm_core.description import (
    DescriptionInput,
    DescriptionTarget,
    describe,
    description_path,
)
from aitm_core.events import UnavailableReducer
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.services import (
    ServicePorts,
    UnavailablePort,
    backend,
    load_installation,
    mutate,
    preflight_policy,
)
from aitm_core.store.objects import GitCommandError, Repository


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    identity = uuid4().hex
    parser = argparse.ArgumentParser(prog="aitm describe", exit_on_error=False)
    parser.add_argument("story", type=int)
    parser.add_argument("--title", required=True)
    parser.add_argument("--as", dest="actor", required=True)
    parser.add_argument("--want", required=True)
    parser.add_argument("--so-that", required=True)
    parser.add_argument("--scope-file", type=Path, required=True)
    parser.add_argument("--anchor", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--installation", type=Path)
    try:
        options = parser.parse_args(arguments)
        if options.story < 1:
            raise ValueError("describe requires a positive story ID")
        fields = DescriptionInput(
            title=options.title,
            actor=options.actor,
            want=options.want,
            so_that=options.so_that,
            scope=options.scope_file.read_bytes().decode("utf-8"),
        )
        if options.anchor is None:
            return CommandResult(
                operation_id=identity,
                local=LocalOutcome.UNAVAILABLE,
                evidence=("Supply the trusted store anchor with --anchor.",),
            )
        return _apply(identity, options, fields)
    except (argparse.ArgumentError, ValueError) as error:
        outcome = LocalOutcome.INTEGRITY_ERROR
        evidence = str(error)
    except (GitCommandError, OSError, UnavailablePort, UnavailableReducer) as error:
        outcome = LocalOutcome.UNAVAILABLE
        evidence = str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(evidence,))


def _apply(
    identity: str, options: argparse.Namespace, fields: DescriptionInput
) -> CommandResult:
    anchor = StoreAnchor.model_validate_json(options.anchor.read_bytes())
    repository = Repository(options.repository, anchor.planning_ref)
    installation = load_installation(repository, anchor, options.installation)
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
    store = backend(repository, anchor)
    snapshot = store.read_tree(revision)
    paths = (story_event_path(options.story), description_path(options.story))
    owner = OperationOwner(actor=EventActor(kind="tool", harness="aitm-cli"))
    operation = describe(
        DescriptionTarget(
            options.story,
            store.read(snapshot, paths),
            owner,
            prepared.policy.source.digest,
            identity,
            datetime.now(UTC).isoformat(),
        ),
        fields,
    )

    def authorize(
        candidate: OperationOwner, change: RelatedWriteSet
    ) -> WriteAuthorization:
        allowed = candidate == owner and change == operation.change
        return WriteAuthorization(
            allowed=allowed,
            origin=AuthorityOrigin.REGISTERED,
            reason=None
            if allowed
            else "write is outside the structured description operation",
        )

    result = mutate(
        installation,
        operation,
        snapshot,
        ports=ServicePorts(write_authorization=authorize),
    )
    message = (
        result.reason or f"Recorded structured description for story {options.story}."
    )
    return result.command.model_copy(
        update={"evidence": (*result.command.evidence, message)}
    )
