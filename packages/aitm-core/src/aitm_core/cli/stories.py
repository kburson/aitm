"""Installed graduation and graph link commands."""

import argparse
from pathlib import Path
from uuid import uuid4

from aitm_core.graduation import (
    GraduationConflict,
    GraduationService,
    completed_record,
    ordinary_finalization,
)
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.events import EventActor
from aitm_core.models.lifecycle import StoryKind
from aitm_core.models.operations import OperationOwner
from aitm_core.providers.backlog import GraduationResult, LocalGraduationAuthority
from aitm_core.providers.identity import (
    IdentityAuthority,
    IdentityConflict,
    IdentityProvider,
    ReservationRecord,
)
from aitm_core.relationships import GraphConflict, LinkRequest
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import _entries
from aitm_core.store.workspace import BindingConflict


class GraduateCommand(CommandResult):
    issue: int | None = None


def handle(
    route: tuple[str, ...],
    arguments: tuple[str, ...],
    *,
    identity_provider: IdentityProvider | None = None,
    local_authority: LocalGraduationAuthority | None = None,
) -> CommandResult:
    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    if route == ("link",):
        parser.add_argument("story", type=int)
        link = parser.add_mutually_exclusive_group(required=True)
        link.add_argument("--parent", type=int)
        link.add_argument("--blocked-by", type=int)
        parser.add_argument("--remove", action="store_true")
    elif route == ("graduate", "resume"):
        parser.add_argument("operation")
    else:
        parser.add_argument("--draft", required=True)
        parser.add_argument(
            "--kind", choices=("story", "defect", "spike", "epic"), default="story"
        )
        parser.add_argument("--parent", type=int)
        parser.add_argument("--target")
    identity = uuid4().hex
    try:
        args = parser.parse_args(arguments)
        installation, _ = _active_installation(
            Repository(Path.cwd(), "refs/heads/aitm-graduation-probe")
        )
        service = GraduationService(
            installation,
            OperationOwner(actor=EventActor(kind="tool", harness="aitm-cli")),
        )
        if route == ("link",):
            relation = "parent" if args.parent is not None else "blocked-by"
            other = args.parent if args.parent is not None else args.blocked_by
            return service.link(
                LinkRequest(
                    story=args.story, other=other, relation=relation, remove=args.remove
                )
            ).command
        if route == ("graduate", "resume"):
            if identity_provider is None:
                return _unavailable(identity)
            return resume_external(service, identity_provider, args.operation)
        if local_authority is None and identity_provider is None:
            return _unavailable(identity)
        target = DeliveryTarget(
            repository=installation.code_repository,
            ref=args.target
            or installation.code_remote_ref
            or installation.store.code_default_ref,
        )
        kind: StoryKind = args.kind
        intent = service.prepare_draft(
            args.draft, identity, target, kind=kind, parent=args.parent
        )
        if local_authority is not None:
            graduated = local_authority.graduate(intent, ordinary_finalization())
            return _command(graduated)
        assert identity_provider is not None
        authority = IdentityAuthority(installation, identity_provider)
        return _external(service, authority, authority.reserve_identity(intent))
    except (
        BindingConflict,
        GraduationConflict,
        IdentityConflict,
        GraphConflict,
    ) as error:
        outcome, message = LocalOutcome.CONFLICT, str(error)
    except (GitCommandError, OSError) as error:
        outcome, message = LocalOutcome.UNAVAILABLE, str(error)
    except (argparse.ArgumentError, ValueError) as error:
        outcome, message = LocalOutcome.INTEGRITY_ERROR, str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(message,))


def _unavailable(identity: str) -> CommandResult:
    return CommandResult(
        operation_id=identity,
        local=LocalOutcome.UNAVAILABLE,
        evidence=("The installed graduation authority is unavailable.",),
    )


def _command(result: GraduationResult) -> CommandResult:
    return GraduateCommand(
        **result.command.model_dump(),
        issue=result.issue.number if result.issue else None,
    )


def resume_external(
    service: GraduationService, provider: IdentityProvider, operation: str
) -> CommandResult:
    repository = service.installation.repository
    snapshot = service.snapshot(service.policy())
    paths = tuple(
        path
        for path in _entries(repository, snapshot)
        if path.startswith(".aitm/identity/") and path.endswith("/reservation.json")
    )
    for raw in repository.read_blobs(snapshot.tree, paths).values():
        assert raw is not None
        reservation = ReservationRecord.model_validate_json(raw).reservation
        if operation in {reservation.intent.operation_id, reservation.key}:
            return _external(
                service, IdentityAuthority(service.installation, provider), reservation
            )
    raise GraduationConflict("The retained external graduation intent was not found.")


def _external(service, authority, reservation) -> CommandResult:
    intent = reservation.intent
    finalization = (
        intent.finalization.to_intent()
        if intent.finalization is not None
        else ordinary_finalization()
    )
    result = service.finalize_external_identity(authority, reservation, finalization)
    issue = None
    if (
        result.command.local == LocalOutcome.COMPLETED
        and result.command.publication != PublicationOutcome.PENDING
    ):
        snapshot = service.snapshot(service.policy())
        record = completed_record(
            service.installation.repository, snapshot, intent.source
        )
        if record is None:
            raise GraduationConflict("Graduation has no verified identity record.")
        issue = record.issue
    return _command(
        GraduationResult(intent=intent, command=result.command, issue=issue)
    )
