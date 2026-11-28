"""Installed adapters for review open, turn, and complete."""

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from aitm_core.events import UnavailableReducer
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
    repository_path,
)
from aitm_core.reviews.native import validate_bundle
from aitm_core.reviews.policy import ReviewPolicy
from aitm_core.reviews.topology import IdentityBinding, IdentityMapping, Participant
from aitm_core.reviews.turns import (
    OpenReviewRequest,
    ReviewConflict,
    ReviewContext,
    complete_review,
    load_level,
    open_review,
    record_turn,
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

_RECORD = re.compile(r"review-([1-9][0-9]*)-[0-9a-f]{24}")


def _mapping(source: Path) -> IdentityMapping:
    try:
        value = json.loads(source.read_bytes())
        entries = tuple(
            IdentityBinding(
                Participant(**item["participant"]),
                item["session_id"],
                item["provider_family"],
            )
            for item in value["bindings"]
        )
        if not isinstance(value["evidence"], str):
            raise ValueError("identity mapping requires an evidence reference")
        for entry in entries:
            if not all(
                isinstance(part, str)
                for part in (
                    entry.participant.namespace,
                    entry.participant.session,
                    entry.participant.provider,
                    entry.session_id,
                    entry.provider_family,
                )
            ):
                raise ValueError("identity mapping fields must be strings")
        return IdentityMapping(value["evidence"], entries)
    except (TypeError, KeyError) as error:
        raise ValueError("invalid review identity mapping") from error


def _apply(command: str, arguments: argparse.Namespace, identity: str) -> CommandResult:
    anchor = StoreAnchor.model_validate_json(arguments.anchor.read_bytes())
    repo = Repository(arguments.repository, anchor.planning_ref)
    installation = load_installation(repo, anchor, arguments.installation)
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
    store = backend(repo, anchor)
    snapshot = store.read_tree(revision)
    owner = OperationOwner(actor=EventActor(kind="tool", harness="aitm-cli"))

    def publish(operation, expected):
        def authorize(candidate, change):
            return WriteAuthorization(
                allowed=candidate == owner and change == operation.change,
                origin=AuthorityOrigin.REGISTERED,
            )

        return mutate(
            installation,
            operation,
            expected,
            ports=ServicePorts(write_authorization=authorize),
        )

    context = ReviewContext(
        store,
        snapshot,
        owner,
        prepared.policy.source.digest,
        identity,
        datetime.now(UTC).isoformat(),
        publish,
    )
    if command == "open":
        repository_path(arguments.doc)
        root = repo.root.resolve()
        document = (root / arguments.doc).resolve(strict=True)
        document.relative_to(root)
        level = open_review(
            OpenReviewRequest(
                context,
                arguments.story,
                arguments.doc,
                arguments.level,
                document.read_bytes(),
            )
        )
        assert level.result is not None
        result = level.result
    else:
        record = _RECORD.fullmatch(arguments.record)
        if record is None:
            raise ValueError("expected a live review capsule record ID")
        level = load_level(context, int(record[1]), arguments.record)
        if command == "turn":
            result = record_turn(level, arguments.response.read_bytes())
        else:
            policies = prepared.policy.config.review.documents
            policy = ReviewPolicy(policies.assurances, _mapping(arguments.identity_map))
            result = complete_review(level, validate_bundle(arguments.bundle, policy))
    evidence = result.reason or f"Review record {level.record_id}."
    return result.command.model_copy(
        update={"evidence": (*result.command.evidence, evidence)}
    )


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    identity = uuid4().hex
    command = route[-1]
    parser = argparse.ArgumentParser(prog=f"aitm review {command}", exit_on_error=False)
    parser.add_argument("--anchor", type=Path, required=True)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--installation", type=Path)
    if command == "open":
        parser.add_argument("--story", required=True, type=int)
        parser.add_argument("--doc", required=True)
        parser.add_argument("--level", required=True, choices=("sar", "spr", "xpr"))
    else:
        parser.add_argument("--record", required=True)
        if command == "turn":
            parser.add_argument("--response", required=True, type=Path)
        else:
            parser.add_argument("--bundle", required=True, type=Path)
            parser.add_argument("--identity-map", required=True, type=Path)
    try:
        options = parser.parse_args(arguments)
        return _apply(command, options, identity)
    except ReviewConflict as error:
        status, detail = LocalOutcome.CONFLICT, str(error)
    except (GitCommandError, OSError, UnavailablePort, UnavailableReducer) as error:
        status, detail = LocalOutcome.UNAVAILABLE, str(error)
    except (argparse.ArgumentError, ValueError) as error:
        status, detail = LocalOutcome.INTEGRITY_ERROR, str(error)
    return CommandResult(operation_id=identity, local=status, evidence=(detail,))
