"""Import only generation-bound authored data through Core's normal store service."""

import os
from dataclasses import dataclass, replace
from json import loads
from pathlib import Path, PurePosixPath
from typing import Iterable
from uuid import uuid4

from aitm_core.documents import _GENERATED_KEYS, _parse, canonicalize
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import Binding, StoryRef, allows_authored
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    repository_path,
    story_event_path,
)
from aitm_core.services import ServicePorts, mutate, preflight_policy
from aitm_core.store.backend import Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.gate import _atomic_write
from aitm_core.store.publication import PublicationStatus, Publisher
from aitm_core.store.reconcile import Resolution, reconcile
from aitm_core.store.workspace import (
    BindingConflict,
    Workspace,
    _materialize,
    _parent,
    digest,
    read_workspace,
)

CATEGORIES = {("workspace-sync", 1): OperationCategory.AUTHORED_SYNC}


@dataclass(frozen=True, slots=True)
class PathSelection:
    paths: tuple[str, ...] = ()
    deletions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SyncResult:
    command: CommandResult
    binding: Binding
    changed: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class UnbindResult(SyncResult):
    """Return the sync outcome with the binding's final release disposition."""


def _select(binding: Binding, selected: PathSelection) -> tuple[str, ...]:
    if binding.purpose == BindingPurpose.EVIDENCE:
        raise ValueError("Evidence-only bindings have no authored sync authority.")
    allowed = {item.path for item in binding.paths}
    paths = tuple(dict.fromkeys((*selected.paths, *selected.deletions)))
    for path in paths:
        repository_path(path)
        if path not in allowed or not allows_authored(binding.scope, path):
            raise ValueError(f"Unbound or non-authored selection {path}.")
    return paths or tuple(sorted(allowed))


def _validate_authored(
    binding: Binding, path: str, previous: bytes | None, content: bytes
) -> None:
    if not path.endswith(".md"):
        return
    content.decode("utf-8")
    typed = content.startswith((b"---\n", b"---\r\n"))
    typed_before = previous is not None and previous.startswith((b"---\n", b"---\r\n"))
    if not typed and not typed_before:
        return
    if not typed:
        raise ValueError(f"Cannot strip authored document identity at {path}.")
    parsed = _parse(content)
    canonicalize(content, DocumentSchema())
    if (
        isinstance(binding.scope, StoryRef)
        and parsed.header["story"] != binding.scope.story
    ):
        raise ValueError(f"Authored document belongs to another story at {path}.")
    prior_header = _parse(previous).header if typed_before else {}
    for key in _GENERATED_KEYS:
        if parsed.header.get(key) != prior_header.get(key):
            raise ValueError(
                f"Generated field {key} cannot be written by sync at {path}."
            )
    if typed_before and parsed.header.get("role") != prior_header.get("role"):
        raise ValueError(f"Document role is immutable at {path}.")


def _diagnostics(
    binding: Binding, current: Snapshot, workspace: Workspace
) -> tuple[str, ...]:
    root = Path(binding.worktree)
    if isinstance(binding.scope, StoryRef):
        prefix = PurePosixPath(story_event_path(binding.scope.story)).parent.as_posix()
    else:
        prefix = str(PurePosixPath(binding.scope.document).parent)
    known = {entry.path for entry in binding.paths}

    def visit(directory: int, relative: str):
        with os.scandir(directory) as entries:
            children = sorted(
                (entry.name, entry.is_dir(follow_symlinks=False)) for entry in entries
            )
        for name, is_directory in children:
            path = f"{relative}/{name}"
            if is_directory:
                child = os.open(
                    name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
                )
                try:
                    yield from visit(child, path)
                finally:
                    os.close(child)
            elif path not in known:
                yield path

    try:
        with _parent(root, f"{prefix}/.aitm-scan") as (directory, _):
            others = tuple(visit(directory, prefix))
    except FileNotFoundError:
        return ()
    except OSError as error:
        raise BindingConflict("Cannot inspect the contained authored scope.") from error
    valid = []
    evidence = []
    for path in others:
        try:
            normalized = repository_path(path)
            normalized.encode("utf-8")
        except (ValueError, UnicodeError):
            evidence.append(
                "Ignored an unbound workspace path with an unsupported name."
            )
        else:
            valid.append(normalized)
    others = tuple(valid)
    committed = workspace.repo.read_blobs(current.tree, others)
    for path in others:
        try:
            actual = read_workspace(root, path)
        except BindingConflict:
            actual = object()
        if actual != committed[path]:
            evidence.append(f"Ignored unbound workspace path {path}.")
    return tuple(evidence)


def _recovery(
    workspace: Workspace,
    binding: Binding,
    versions: dict[str, tuple[bytes | None, bytes | None]],
    identity: str,
) -> Path:
    root = workspace.state / "sync-recovery" / binding.identity / identity
    root.mkdir(parents=True, exist_ok=False)
    manifest = {}
    for path, (local, shared) in versions.items():
        for label, data in (("local", local), ("shared", shared)):
            if data is not None:
                _materialize(root, f"{label}/{path}", data)
        manifest[path] = {"local": digest(local), "shared": digest(shared)}
    _atomic_write(
        root / "receipt.json",
        {
            "binding": binding.identity,
            "generation": binding.generation,
            "paths": manifest,
        },
    )
    return root


def _receipt(workspace: Workspace, binding: Binding) -> Path:
    return (
        workspace.state
        / "sync-pending"
        / f"{binding.identity}-{binding.generation}.json"
    )


def _ports(binding: Binding, ports: ServicePorts) -> ServicePorts:
    allowed = {item.path for item in binding.paths}

    def authorize(owner: OperationOwner, change: RelatedWriteSet) -> WriteAuthorization:
        accepted = (
            owner.binding == binding.identity
            and owner.generation == binding.generation
            and owner.actor.session == binding.session
            and owner.extension is None
            and not change.events
            and all(
                item.path in allowed and allows_authored(binding.scope, item.path)
                for item in change.writes
            )
        )
        return WriteAuthorization(
            allowed=accepted,
            origin=AuthorityOrigin.REGISTERED,
            reason=None if accepted else "Outside the active authored binding.",
        )

    return replace(ports, write_authorization=authorize)


def _operation(
    binding: Binding,
    policy: str,
    shared: dict[str, bytes | None],
    writes: dict[str, bytes | None],
    identity: str,
) -> Operation:
    reads = tuple(
        ReadExpectation(path=path, digest=digest(data))
        for path, data in sorted(shared.items())
    )
    return Operation(
        operation_id=identity,
        owner=OperationOwner(
            actor=EventActor(kind="tool", harness="aitm-cli", session=binding.session),
            binding=binding.identity,
            generation=binding.generation,
        ),
        policy_digest=policy,
        category=OperationCategory.AUTHORED_SYNC,
        intent=FinalizationIntent(
            kind="workspace-sync",
            version=1,
            related_preconditions=reads,
            payload=b"explicit bound authored selection",
        ),
        change=RelatedWriteSet(
            read_set=reads,
            writes=tuple(
                BlobWrite(path=path, content=data)
                for path, data in sorted(writes.items())
            ),
        ),
    )


def _verify(workspace: Workspace, binding: Binding) -> Binding:
    return workspace.require(
        binding.scope, binding.identity, binding.generation, binding.session
    )


def _pin(workspace: Workspace, binding: Binding, paths: Iterable[str]) -> Binding:
    current = workspace.repo.tip()
    paths = set(paths)
    data = workspace.repo.read_blobs(current.tree, tuple(sorted(paths)))
    updated = tuple(
        item.model_copy(
            update={"digest": digest(data[item.path]), "revision": current.revision}
        )
        if item.path in paths
        and read_workspace(Path(binding.worktree), item.path) == data[item.path]
        else item
        for item in binding.paths
    )
    value = binding.model_copy(update={"paths": updated})
    workspace.persist(value)
    return value


def _actions(
    ports: ServicePorts, snapshot: Snapshot, command: CommandResult
) -> CommandResult:
    runner = ports.action_retry
    if not callable(runner):
        return command.model_copy(
            update={
                "evidence": (
                    *command.evidence,
                    "Pending action runner is unavailable.",
                ),
                "pending": tuple(dict.fromkeys((*command.pending, "action-retry"))),
            }
        )
    try:
        results = runner(snapshot)
    except (OSError, RuntimeError, ValueError) as error:
        return command.model_copy(
            update={
                "evidence": (
                    *command.evidence,
                    f"Pending action runner failed after the store result. {error}",
                ),
                "pending": tuple(dict.fromkeys((*command.pending, "action-retry"))),
            }
        )
    return command.model_copy(
        update={
            "evidence": (
                *command.evidence,
                *(line for result in results for line in result.evidence),
            ),
            "pending": tuple(
                dict.fromkeys(
                    (
                        *command.pending,
                        *(item for result in results for item in result.pending),
                        *(
                            f"action:{result.operation_id}"
                            for result in results
                            if result.local != LocalOutcome.COMPLETED
                            or result.publication == PublicationOutcome.PENDING
                        ),
                    )
                )
            ),
        }
    )


def _retry_pending(
    workspace: Workspace, binding: Binding, ports: ServicePorts
) -> SyncResult | None:
    pending = _receipt(workspace, binding)
    if not pending.exists():
        return None
    data = loads(pending.read_bytes())
    identity = data["operation"]
    publisher = Publisher(workspace.installation, _ports(binding, ports), CATEGORIES)
    operation = publisher.request(identity)
    if (
        operation.owner.binding != binding.identity
        or operation.owner.generation != binding.generation
    ):
        raise BindingConflict("Pending publication belongs to a stale binding.")
    result = publisher.publish(identity)
    if result.status != PublicationStatus.PUBLISHED:
        if result.recovery_ref is not None and result.recovery_ref != data.get(
            "recovery"
        ):
            _atomic_write(
                pending, {"operation": identity, "recovery": result.recovery_ref}
            )
        return SyncResult(
            CommandResult(
                operation_id=identity,
                local=LocalOutcome.COMPLETED
                if result.local_completed
                else LocalOutcome.CONFLICT,
                publication=PublicationOutcome.PENDING,
                pending=("publication",),
                evidence=(result.reason or "Bound publication remains pending.",),
                recovery=result.recovery_ref,
            ),
            binding,
        )
    updated = _pin(
        workspace, binding, (write.path for write in operation.change.writes)
    )
    pending.unlink()
    return SyncResult(
        _actions(
            ports,
            workspace.repo.tip(),
            CommandResult(
                operation_id=identity,
                local=LocalOutcome.COMPLETED,
                publication=PublicationOutcome.VERIFIED,
                evidence=("Verified the retained authored publication.",),
            ),
        ),
        updated,
        tuple(write.path for write in operation.change.writes),
    )


def _sync(
    workspace: Workspace, binding: Binding, selected: PathSelection, ports: ServicePorts
) -> SyncResult:
    identity = uuid4().hex
    paths = _select(binding, selected)
    retried = _retry_pending(workspace, binding, ports)
    if retried is not None:
        return retried
    authority = preflight_policy(workspace.installation, ports=ports)
    if authority.outcome != LocalOutcome.COMPLETED or authority.policy is None:
        return SyncResult(
            CommandResult(
                operation_id=identity,
                local=LocalOutcome.INTEGRITY_ERROR,
                publication=authority.publication,
                evidence=authority.evidence,
            ),
            binding,
        )
    repo = workspace.repo
    current = repo.tip()
    if authority.views.planning.observed_commit != current.revision:
        raise BindingConflict("The planning view changed while authoring was pinned.")
    shared = repo.read_blobs(current.tree, paths)
    evidence = _diagnostics(binding, current, workspace)
    base = {item.path: item.digest for item in binding.paths}
    root = Path(binding.worktree)
    conflicts = {}
    writes = {}
    for path in paths:
        local = read_workspace(root, path)
        if path in selected.deletions and local is not None:
            return SyncResult(
                CommandResult(
                    operation_id=identity,
                    local=LocalOutcome.REFUSED,
                    evidence=(
                        *evidence,
                        f"Remove the workspace file before selecting its deletion at {path}.",
                    ),
                ),
                binding,
            )
        if local == shared[path] or digest(local) == base[path]:
            continue
        if local is None and path not in selected.deletions:
            return SyncResult(
                CommandResult(
                    operation_id=identity,
                    local=LocalOutcome.REFUSED,
                    evidence=(
                        *evidence,
                        f"Deletion requires explicit selection for {path}.",
                    ),
                ),
                binding,
            )
        if digest(shared[path]) != base[path]:
            conflicts[path] = (local, shared[path])
            continue
        if local is not None:
            _validate_authored(binding, path, shared[path], local)
        writes[path] = local
    if conflicts:
        saved = _recovery(workspace, binding, conflicts, identity)
        return SyncResult(
            CommandResult(
                operation_id=identity,
                local=LocalOutcome.CONFLICT,
                evidence=(*evidence, "Authored bases changed. Preserved both bodies."),
                recovery=str(saved),
            ),
            binding,
        )
    if not writes:
        updated = _pin(workspace, binding, paths)
        return SyncResult(
            CommandResult(
                operation_id=identity,
                local=LocalOutcome.COMPLETED,
                evidence=(*evidence, "No selected authored changes."),
            ),
            updated,
        )
    if isinstance(binding.scope, StoryRef):
        event = story_event_path(binding.scope.story)
        shared.update(repo.read_blobs(current.tree, (event,)))
    operation = _operation(
        binding, authority.policy.source.digest, shared, writes, identity
    )
    result = mutate(
        workspace.installation,
        operation,
        current,
        ports=_ports(binding, ports),
        categories=CATEGORIES,
    )
    command = result.command.model_copy(
        update={"evidence": (*result.command.evidence, *evidence)}
    )
    if command.local != LocalOutcome.COMPLETED:
        return SyncResult(command, binding)
    if command.publication == PublicationOutcome.PENDING:
        _atomic_write(
            _receipt(workspace, binding),
            {"operation": identity, "recovery": command.recovery},
        )
        command = command.model_copy(
            update={"pending": (*command.pending, "publication")}
        )
    else:
        binding = _pin(workspace, binding, writes)
    return SyncResult(_actions(ports, result.snapshot, command), binding, tuple(writes))


def sync(
    workspace: Workspace,
    binding: Binding,
    selected: PathSelection,
    *,
    ports: ServicePorts | None = None,
) -> SyncResult:
    with workspace.lock():
        return _sync(
            workspace, _verify(workspace, binding), selected, ports or ServicePorts()
        )


def unbind(
    workspace: Workspace,
    binding: Binding,
    selected: PathSelection = PathSelection(),
    *,
    ports: ServicePorts | None = None,
) -> UnbindResult:
    with workspace.lock():
        binding = _verify(workspace, binding)
        if binding.purpose == BindingPurpose.EVIDENCE:
            if selected.paths or selected.deletions:
                raise ValueError(
                    "Evidence-only bindings have no authored sync authority."
                )
            closed = binding.model_copy(update={"active": False})
            workspace.persist(closed)
            return UnbindResult(
                CommandResult(
                    operation_id=uuid4().hex,
                    local=LocalOutcome.COMPLETED,
                    evidence=("Released the evidence-only binding.",),
                ),
                closed,
            )
        result = _sync(workspace, binding, selected, ports or ServicePorts())
        outcome = UnbindResult(result.command, result.binding, result.changed)
        if (
            outcome.command.local != LocalOutcome.COMPLETED
            or outcome.command.publication == PublicationOutcome.PENDING
        ):
            return outcome
        remaining = Path(binding.worktree)
        if any(
            digest(read_workspace(remaining, item.path)) != item.digest
            for item in outcome.binding.paths
        ):
            return replace(
                outcome,
                command=outcome.command.model_copy(
                    update={
                        "local": LocalOutcome.CONFLICT,
                        "evidence": (
                            *outcome.command.evidence,
                            "Unselected authored changes remain. The binding stays active.",
                        ),
                    }
                ),
            )
        closed = outcome.binding.model_copy(update={"active": False})
        workspace.persist(closed)
        return replace(outcome, binding=closed)


def reconcile_sync(
    workspace: Workspace,
    binding: Binding,
    original_id: str,
    retained: str | None,
    expected_shared: str | None,
    selected: PathSelection,
    resolve: bool,
    *,
    ports: ServicePorts | None = None,
) -> SyncResult:
    ports = ports or ServicePorts()
    with workspace.lock():
        binding = _verify(workspace, binding)
        repo = workspace.repo
        publisher = Publisher(
            workspace.installation, _ports(binding, ports), CATEGORIES
        )
        original = publisher.request(original_id)
        paths = {row.path for row in original.change.writes}
        selected_paths = (
            _select(binding, selected)
            if selected.paths or selected.deletions
            else _select(binding, PathSelection(tuple(sorted(paths))))
        )
        if (
            original.intent.kind != "workspace-sync"
            or original.owner.binding != binding.identity
            or original.owner.generation != binding.generation
            or not paths
            or paths != set(selected_paths)
        ):
            raise BindingConflict(
                "The retained operation does not match the selected bound scope."
            )
        authority = preflight_policy(workspace.installation, ports=ports)
        frontier = authority.views.shared
        if (
            authority.outcome != LocalOutcome.COMPLETED
            or authority.policy is None
            or frontier is None
            or frontier.status != ContinuityStatus.VERIFIED
            or frontier.valid_tip is None
            or (expected_shared is not None and frontier.valid_tip != expected_shared)
        ):
            raise BindingConflict(
                "Reconciliation requires the current verified shared tip."
            )
        if retained is None:
            intent = loads(_receipt(workspace, binding).read_bytes())
            reference = intent.get("recovery")
            if intent.get("operation") != original_id or not isinstance(reference, str):
                raise BindingConflict(
                    "No retained bound publication matches this operation."
                )
            if not reference.startswith("refs/aitm/recovery/"):
                raise BindingConflict("The retained recovery ref is not recognized.")
            retained = (
                repo._git("show-ref", "--verify", "--hash", reference).strip().decode()
            )
        kept = repo.read_tree(retained)
        published = repo.read_tree(frontier.valid_tip)
        retained_ref = publisher._recovery_ref(kept.revision)
        if (
            repo._git("show-ref", "--verify", "--hash", retained_ref).strip().decode()
            != kept.revision
            or publisher.record(kept, original) is None
        ):
            raise BindingConflict(
                "The retained revision does not contain the original operation."
            )
        saved = repo.read_blobs(kept.tree, tuple(sorted(paths)))
        shared = repo.read_blobs(published.tree, tuple(sorted(paths)))
        identity = uuid4().hex
        if not resolve:
            path = _recovery(
                workspace,
                binding,
                {key: (saved[key], shared[key]) for key in sorted(paths)},
                identity,
            )
            return SyncResult(
                CommandResult(
                    operation_id=original_id,
                    local=LocalOutcome.CONFLICT,
                    evidence=(
                        "Review both retained versions and submit the explicit scoped resolution.",
                    ),
                    recovery=str(path),
                ),
                binding,
            )
        bodies = dict(shared)
        writes = {}
        for path in sorted(paths):
            content = read_workspace(Path(binding.worktree), path)
            if content is not None and path in selected.deletions:
                raise BindingConflict(
                    f"Remove the workspace file before selecting its deletion at {path}."
                )
            if content is None and path not in selected.deletions:
                raise BindingConflict(
                    f"Resolution requires a body or explicit deletion for {path}."
                )
            if content is not None:
                _validate_authored(binding, path, shared[path], content)
            writes[path] = content
        if isinstance(binding.scope, StoryRef):
            event = story_event_path(binding.scope.story)
            bodies.update(repo.read_blobs(published.tree, (event,)))
        operation = _operation(
            binding, authority.policy.source.digest, bodies, writes, identity
        )
        outcome = reconcile(
            workspace.installation,
            original_id,
            Resolution(kept.revision, published.revision, operation),
            ports=_ports(binding, ports),
            categories=CATEGORIES,
        )
        if outcome.command.local != LocalOutcome.COMPLETED:
            return SyncResult(outcome.command, binding)
        if outcome.command.publication == PublicationOutcome.PENDING:
            _atomic_write(
                _receipt(workspace, binding),
                {"operation": identity, "recovery": outcome.command.recovery},
            )
        else:
            _receipt(workspace, binding).unlink(missing_ok=True)
            binding = _pin(workspace, binding, paths)
        return SyncResult(
            _actions(ports, outcome.snapshot, outcome.command),
            binding,
            tuple(sorted(paths)),
        )
