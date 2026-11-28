"""Installed review import and exact-content acceptance adapters."""

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from aitm_core.cli.review_turns import _mapping
from aitm_core.events import UnavailableReducer
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
    repository_path,
    story_scope,
)
from aitm_core.reviews.acceptance import DocumentInput, ReviewRecord, accept_document
from aitm_core.reviews.importer import ReviewImport, import_review
from aitm_core.reviews.native import validate_bundle
from aitm_core.reviews.policy import ReviewPolicy
from aitm_core.reviews.portable import reconstruct_bundle
from aitm_core.reviews.turns import LevelRecord, ReviewConflict, ReviewContext
from aitm_core.services import (
    ServicePorts,
    UnavailablePort,
    backend,
    mutate,
    preflight_policy,
)
from aitm_core.setup.init import _active_installation
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace, read_workspace

_RECORD = re.compile(r"[A-Za-z0-9_-]{1,128}")
_BASE = re.compile(r"[a-f0-9]{64}")
_SUPPORTED_DOC_ASSURANCES = (
    "declared-manual",
    "native-consensus-authority-unavailable",
)


def _parser(command: str):
    parser = argparse.ArgumentParser(prog=command, exit_on_error=False)
    parser.add_argument("--story", type=int, required=True)
    parser.add_argument("--doc", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--identity-map", type=Path)
    parser.add_argument("--legacy-session-namespace")
    return parser


def _setup(arguments: argparse.Namespace, identity: str):
    repository_path(arguments.doc)
    if story_scope(arguments.doc) != arguments.story:
        raise ReviewConflict("review document belongs to another story")
    repository = Repository(Path.cwd(), "refs/heads/aitm-review-probe")
    installation, _ = _active_installation(repository)
    workspace = Workspace(installation)
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
    store = backend(workspace.repo, installation.store)
    snapshot = store.read_tree(revision)
    owner = OperationOwner(
        actor=EventActor(kind="tool", harness="aitm-cli", session=arguments.session),
        binding=arguments.binding,
        generation=arguments.generation,
    )
    shared = prepared.views.shared
    observed_publication = PublicationOutcome.PENDING
    if installation.store.planning_remote is None:
        observed_publication = PublicationOutcome.NOT_APPLICABLE
    elif (
        shared is not None
        and shared.status == ContinuityStatus.VERIFIED
        and shared.valid_tip == revision
    ):
        observed_publication = PublicationOutcome.VERIFIED

    def publish(operation, expected):
        def authorize(candidate, change):
            return WriteAuthorization(
                allowed=candidate == owner and operation.change == change,
                origin=AuthorityOrigin.REGISTERED,
            )

        return mutate(
            installation,
            operation,
            expected,
            ports=ServicePorts(write_authorization=authorize),
        )

    return (
        workspace,
        ReviewContext(
            store,
            snapshot,
            owner,
            prepared.policy.source.digest,
            identity,
            datetime.now(UTC).isoformat(),
            publish,
        ),
        prepared.policy.config.review,
        observed_publication,
    )


def _review_policy(arguments):
    if arguments.identity_map is None:
        raise ValueError(
            "supply an explicit identity mapping to qualify review participants"
        )
    raw = arguments.identity_map.read_bytes()
    with TemporaryDirectory(prefix="aitm-review-identities-") as tmp:
        frozen = Path(tmp) / "identities.json"
        frozen.write_bytes(raw)
        mapping = _mapping(frozen)
    return ReviewPolicy(
        _SUPPORTED_DOC_ASSURANCES,
        mapping,
        legacy_session_namespace=arguments.legacy_session_namespace,
    ), raw


def _import(arguments: argparse.Namespace, identity: str) -> CommandResult:
    prepared = _setup(arguments, identity)
    if isinstance(prepared, CommandResult):
        return prepared
    workspace, context, policy, observed_publication = prepared
    expected = None if arguments.expected_base == "absent" else arguments.expected_base
    if expected is not None and _BASE.fullmatch(expected) is None:
        raise ValueError("expected-base requires the current raw SHA-256 or absent")
    if arguments.record is not None and _RECORD.fullmatch(arguments.record) is None:
        raise ValueError("invalid retained review record identity")
    bundle = reconstruct_bundle(arguments.folder)
    eligible = False
    if bundle.manifest.outcome != "round-cap":
        selected, _ = _review_policy(arguments)
        bundle = validate_bundle(arguments.folder, selected)
        eligible = bundle.assurance in policy.documents.assurances
    result = import_review(
        ReviewImport(
            context=context,
            workspace=workspace,
            story=arguments.story,
            path=arguments.doc,
            binding_id=arguments.binding,
            generation=arguments.generation,
            session=arguments.session,
            record_id=arguments.record,
            project_authored=eligible,
            observed_publication=observed_publication,
        ),
        bundle,
        expected,
    ).command
    if not eligible and result.local == LocalOutcome.COMPLETED:
        return result.model_copy(
            update={
                "evidence": (
                    *result.evidence,
                    "Review retained without current acceptance eligibility.",
                ),
            }
        )
    return result


def _retained_review(workspace, context, story, path, record_id, policy):
    if _RECORD.fullmatch(record_id) is None:
        raise ValueError("review evidence must identify a retained capsule")
    capsule = LevelRecord(context, story, record_id, path, "sar").capsule
    raw_paths = workspace.repo._git(
        "ls-tree",
        "-r",
        "--name-only",
        "-z",
        context.snapshot.tree,
        "--",
        f"{capsule}/",
    )
    paths = tuple(value.decode("utf-8") for value in raw_paths.split(b"\0") if value)
    if not paths:
        raise ReviewConflict("retained review capsule is unavailable")
    blobs = context.backend.read(context.snapshot, paths)
    with TemporaryDirectory(prefix="aitm-retained-review-") as tmp:
        root = Path(tmp)
        for name in paths:
            prefix = f"{capsule}/"
            if not name.startswith(prefix):
                raise ReviewConflict("review collateral escaped its retained capsule")
            file = name.removeprefix(prefix)
            repository_path(file)
            if file == "base.md" or file.startswith("timing/"):
                continue
            target = root / file
            value = blobs[name]
            if value is None:
                raise ReviewConflict("retained review collateral changed")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        if reconstruct_bundle(root).manifest.outcome == "round-cap":
            return None, paths
        review = validate_bundle(root, policy)
    return ReviewRecord(record_id, review), paths


def _accept(role, arguments: argparse.Namespace, identity: str) -> CommandResult:
    prepared = _setup(arguments, identity)
    if isinstance(prepared, CommandResult):
        return prepared
    workspace, context, policy, _ = prepared
    # First recover the supported assurance actually evidenced by each
    # capsule. The committed acceptance policy then selects which evidence
    # can satisfy a level under the current policy revision.
    selected, raw_mapping = _review_policy(arguments)
    with workspace.lock():
        bound = workspace.require(
            StoryRef(story=arguments.story),
            arguments.binding,
            arguments.generation,
            arguments.session,
        )
        if bound.purpose != BindingPurpose.PLANNING:
            raise BindingConflict("document acceptance requires a planning binding")
        raw = context.backend.read(context.snapshot, (arguments.doc,))[arguments.doc]
        owned = next((item for item in bound.paths if item.path == arguments.doc), None)
        if (
            owned is None
            or raw is None
            or read_workspace(Path(bound.worktree), arguments.doc) != raw
        ):
            raise BindingConflict(
                "acceptance requires the current bound authored bytes"
            )
        records = []
        proof_paths = []
        for record_id in dict.fromkeys(arguments.review):
            record, paths = _retained_review(
                workspace, context, arguments.story, arguments.doc, record_id, selected
            )
            if record is not None:
                records.append(record)
            proof_paths.extend(paths)
        result = accept_document(
            role,
            tuple(records),
            DocumentInput(arguments.story, arguments.doc, role, raw),
            policy,
            context=context,
            proof_paths=tuple(dict.fromkeys(proof_paths)),
            identity_mapping=raw_mapping,
            legacy_session_namespace=arguments.legacy_session_namespace,
        )
        return result.command


def _handle(parser, arguments, run) -> CommandResult:
    identity = uuid4().hex
    try:
        return run(parser.parse_args(arguments), identity)
    except (BindingConflict, ReviewConflict) as error:
        status, detail = LocalOutcome.CONFLICT, str(error)
    except (OSError, UnavailablePort, UnavailableReducer, GitCommandError) as error:
        status, detail = LocalOutcome.UNAVAILABLE, str(error)
    except (ValueError, argparse.ArgumentError) as error:
        status, detail = LocalOutcome.INTEGRITY_ERROR, str(error)
    return CommandResult(operation_id=identity, local=status, evidence=(detail,))


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = _parser("aitm review import")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--expected-base", required=True)
    parser.add_argument("--record")
    return _handle(parser, arguments, _import)


def accept(role, arguments: tuple[str, ...]) -> CommandResult:
    parser = _parser(f"aitm {role} accept")
    parser.add_argument("--review", action="append", required=True)
    return _handle(
        parser, arguments, lambda options, identity: _accept(role, options, identity)
    )
