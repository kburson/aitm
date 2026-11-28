"""Installed entry points for unnumbered ideas and drafts."""

import argparse
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from aitm_core.drafts import CreateEntity, CreationFailed, Intake
from aitm_core.entities import open_entity
from aitm_core.models.binding import EntityRef
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.models.events import EventActor
from aitm_core.models.operations import OperationOwner
from aitm_core.services import UnavailablePort, load_installation, preflight_policy
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace


class IntakeResult(CommandResult):
    entity: EntityRef | None = None
    entities: tuple[EntityRef, ...] = ()


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    identity = uuid4().hex
    kind = route[0]
    action = route[-1]
    if action not in {"add", "new", "discard", "list", "open"}:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(f"Core route is unavailable: {' '.join(route)}",),
        )

    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    if action in {"add", "new"}:
        parser.add_argument("title")
        parser.add_argument("--body-file", type=Path)
        parser.add_argument("--tag", action="append", default=[])
    if action in {"discard", "open"}:
        parser.add_argument("handle")
    if action == "discard":
        parser.add_argument("--reason", required=True)
    if action == "open":
        parser.add_argument("--session", required=True)
        parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--anchor", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--installation", type=Path)
    try:
        options = parser.parse_args(arguments)
        if options.anchor is None and action != "open":
            raise UnavailablePort("Supply the trusted store anchor with --anchor.")
        return _apply(identity, kind, action, options)
    except CreationFailed as error:
        return error.command
    except BindingConflict as error:
        outcome, reason = LocalOutcome.CONFLICT, str(error)
    except (argparse.ArgumentError, ValueError) as error:
        outcome, reason = LocalOutcome.INTEGRITY_ERROR, str(error)
    except (GitCommandError, OSError, UnavailablePort) as error:
        outcome, reason = LocalOutcome.UNAVAILABLE, str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(reason,))


def _apply(
    identity: str, kind: str, action: str, options: argparse.Namespace
) -> CommandResult:
    if options.anchor is None:
        installation, _ = _active_installation(
            Repository(options.repository, "refs/heads/aitm-entity-probe")
        )
        repository = installation.repository
    else:
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
    intake = Intake(
        installation,
        repository.read_tree(revision),
        prepared.policy.source.digest,
        OperationOwner(actor=EventActor(kind="tool", harness="aitm-cli")),
        datetime.now(UTC),
    )
    if action == "list":
        entities = intake.list_entities(kind)
        return IntakeResult(
            operation_id=identity,
            local=LocalOutcome.COMPLETED,
            entities=entities,
            evidence=tuple(f"{ref.identity} {ref.document}" for ref in entities),
        )
    if action == "open":
        ref = intake.resolve_entity(kind, options.handle)
        binding = open_entity(
            Workspace(installation), ref, options.session, tuple(options.path)
        )
        return IntakeResult(
            operation_id=binding.identity,
            local=LocalOutcome.COMPLETED,
            entity=ref,
            evidence=(binding.model_dump_json(),),
        )
    if action == "discard":
        result = intake.discard_draft(options.handle, options.reason)
        return _message(
            result.command,
            result.reason or f"Discard operation {result.command.operation_id}.",
        )

    body = options.body_file.read_text(encoding="utf-8") if options.body_file else ""
    request = CreateEntity(options.title, body, tuple(options.tag))
    entity = (
        intake.create_idea(request) if kind == "idea" else intake.create_draft(request)
    )
    command = _message(entity.command, f"{entity.identity} {entity.document}")
    return IntakeResult(
        **command.model_dump(),
        entity=EntityRef(identity=entity.identity, document=entity.document),
    )


def _message(command: CommandResult, message: str) -> CommandResult:
    if message in command.evidence:
        return command
    return command.model_copy(update={"evidence": (*command.evidence, message)})
