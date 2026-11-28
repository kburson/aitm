"""Publish whole planning operations through the anchored Git route."""

from base64 import b64decode
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from json import dumps, loads
from os import fsdecode

from aitm_core.models.common import LocalOutcome
from aitm_core.models.operations import Operation
from aitm_core.services import ServicePorts, UnavailablePort, backend, preflight_policy
from aitm_core.store.backend import OperationCategories, Snapshot, evaluate_operation
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness
from aitm_core.store.git_backend import (
    GitBackend,
    _Record,
    _record_path,
)
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError


class PublicationStatus(StrEnum):
    NOT_APPLICABLE = "not-applicable"
    PENDING = "pending"
    PUBLISHED = "published"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class PublicationResult:
    operation_id: str
    status: PublicationStatus
    shared_tip: str | None = None
    recovery_ref: str | None = None
    reason: str | None = None
    local_completed: bool = False


class ReplayConflict(ValueError):
    """The complete original request cannot be proved on the new prefix."""


class Publisher:
    def __init__(
        self,
        installation: Installation,
        ports: ServicePorts | None = None,
        categories: OperationCategories | None = None,
    ) -> None:
        self.installation = installation
        self.repository = installation.repository
        self.ports = ports or ServicePorts()
        self.categories = categories or {}
        self.remote = installation.store.planning_remote
        route = dumps(
            [installation.store.store_uuid, self.remote, self.repository.ref],
            separators=(",", ":"),
        )
        self.namespace = sha256(route.encode()).hexdigest()

    def _request_ref(self, identity: str) -> str:
        digest = sha256(identity.encode()).hexdigest()
        return f"refs/aitm/publication/{self.namespace}/{digest}"

    def _retain_ref(self, ref: str, oid: str) -> None:
        repo = self.repository
        created = repo._run("update-ref", "--no-deref", ref, oid, "0" * repo.oid_length)
        if created.returncode:
            existing = repo._git("show-ref", "--hash", "--verify", ref).strip()
            if existing != oid.encode("ascii"):
                raise ReplayConflict(
                    "retained publication identity disagrees with the request"
                )

    def retain_request(self, operation: Operation) -> None:
        if self.remote is None:
            return
        data = operation.model_dump_json().encode()
        oid = self.repository._git("hash-object", "-w", "--stdin", data=data)
        self._retain_ref(
            self._request_ref(operation.operation_id), oid.decode().strip()
        )

    def retain_supersession(
        self, original: Operation, replacement: Operation, retained_revision: str
    ) -> None:
        """Link exact requests beside the replacement without altering its bytes."""
        self.retain_request(replacement)
        lineage = dumps(
            {
                "schema": "aitm.publication-supersession/v1",
                "supersedes": original.operation_id,
                "original_request": original.request_digest,
                "retained_revision": retained_revision,
                "replacement": replacement.operation_id,
                "replacement_request": replacement.request_digest,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        oid = self.repository._git("hash-object", "-w", "--stdin", data=lineage)
        self._retain_ref(
            self._lineage_ref(replacement.operation_id), oid.decode().strip()
        )

    def _lineage_ref(self, identity: str) -> str:
        return self._request_ref(identity).replace(
            "/publication/", "/publication-lineage/", 1
        )

    def request(self, identity: str) -> Operation:
        try:
            raw = self.repository._git("cat-file", "blob", self._request_ref(identity))
            wire = loads(raw)
            wire["intent"]["payload"] = b64decode(
                wire["intent"]["payload"], altchars=b"-_", validate=True
            )
            for write in wire["change"]["writes"]:
                if write["content"] is not None:
                    write["content"] = b64decode(
                        write["content"], altchars=b"-_", validate=True
                    )
            for event in wire["change"]["events"]:
                event["records"] = tuple(
                    b64decode(record, altchars=b"-_", validate=True)
                    for record in event["records"]
                )
            for name in ("read_set", "writes", "events"):
                wire["change"][name] = tuple(wire["change"][name])
            wire["intent"]["related_preconditions"] = tuple(
                wire["intent"]["related_preconditions"]
            )
            wire["guards"] = tuple(wire["guards"])
            wire["pending_actions"] = tuple(wire["pending_actions"])
            operation = Operation.model_validate(wire, strict=False)
            if operation.operation_id != identity:
                raise ReplayConflict(
                    "retained publication request names another operation"
                )
            return operation
        except ReplayConflict:
            raise
        except (GitCommandError, ValueError, KeyError, TypeError) as error:
            raise ReplayConflict(
                "the exact retained publication request is unavailable or invalid"
            ) from error

    def _committed_record(self, snapshot: Snapshot, identity: str) -> _Record | None:
        path = _record_path(identity)
        raw = self.repository.read_blobs(snapshot.tree, (path,))[path]
        return _Record.model_validate_json(raw) if raw is not None else None

    def record(self, snapshot: Snapshot, operation: Operation) -> _Record | None:
        record = self._committed_record(snapshot, operation.operation_id)
        if record is None:
            return None
        if (
            record.command.operation_id != operation.operation_id
            or record.request_digest != operation.request_digest
            or record.command.local != LocalOutcome.COMPLETED
        ):
            raise ReplayConflict(
                "published operation identity has incompatible evidence"
            )
        return record

    def _recovery_ref(self, revision: str) -> str:
        return f"refs/aitm/recovery/c09-{self.namespace}/{revision}"

    def _replay(
        self, target: GitBackend, original: Snapshot, shared: Snapshot, policy
    ) -> tuple[Snapshot, str]:
        from aitm_core.ext.ownership import ExtensionWriteAuthorizer
        from aitm_core.ext.registry import load_extensions

        repo = self.repository
        original_ref = self._recovery_ref(original.revision)
        self._retain_ref(original_ref, original.revision)
        revisions = (
            repo._git(
                "rev-list",
                "--first-parent",
                "--reverse",
                f"{shared.revision}..{original.revision}",
            )
            .decode()
            .splitlines()
        )
        registry = load_extensions(policy, self.ports.extension_declarations)
        current = shared
        for revision in revisions:
            old = repo.read_tree(revision)
            subject = (
                repo._git("show", "-s", "--format=%s", revision).decode().rstrip("\n")
            )
            prefix = "AITM operation "
            if not subject.startswith(prefix):
                raise ReplayConflict("local history contains an unqualified operation")
            operation = self.request(subject.removeprefix(prefix))
            record = self.record(old, operation)
            if (
                record is None
                or record.base != repo.parent(old)
                or record.authorization is None
                or not record.authorization.allowed
            ):
                raise ReplayConflict(
                    "retained operation does not match its local commit"
                )
            if self.record(current, operation) is not None:
                continue
            if operation.policy_digest != policy.source.digest:
                raise ReplayConflict("the committed policy changed before publication")
            if operation.guards:
                raise ReplayConflict(
                    "the retained operation requires fresh guard qualification"
                )
            if operation.intent.kind in {"core.draft.created", "core.draft.discarded"}:
                from aitm_core.drafts import draft_replay_conflict

                conflict = draft_replay_conflict(repo, current, operation)
                if conflict is not None:
                    raise ReplayConflict(conflict)
            if operation.intent.kind == "core.graduated":
                from aitm_core.graduation import graduation_replay_conflict

                conflict = graduation_replay_conflict(repo, current, operation)
                if conflict is not None:
                    raise ReplayConflict(conflict)
            paths = tuple(item.path for item in operation.change.read_set)
            destinations = {
                entry.path
                for entry in (*operation.change.writes, *operation.change.events)
            }
            if not destinations.issubset(paths):
                raise ReplayConflict("retained operation omits a write precondition")
            pinned = repo.read_blobs(current.tree, paths)
            authorizer = ExtensionWriteAuthorizer(
                registry, core=lambda _owner, _change: record.authorization
            )
            evaluation = evaluate_operation(
                operation,
                current,
                pinned,
                ports=replace(self.ports, write_authorization=authorizer),
                categories=self.categories,
            )
            if evaluation.outcome != LocalOutcome.COMPLETED:
                raise ReplayConflict(
                    evaluation.reason or "operation preconditions changed"
                )
            replayed = target._record(
                operation, operation.request_digest, current, evaluation
            )
            current = repo.create_commit(
                current,
                {
                    **evaluation.writes,
                    _record_path(
                        operation.operation_id
                    ): replayed.model_dump_json().encode(),
                },
                operation.operation_id,
            )
        return current, original_ref

    def _push(self, tip: str, expected_shared: str) -> None:
        assert self.remote is not None
        repo = self.repository
        if repo._run("merge-base", "--is-ancestor", expected_shared, tip).returncode:
            raise ReplayConflict("publication must extend the observed shared tip")
        endpoint = fsdecode(
            repo._git("remote", "get-url", "--", self.remote).removesuffix(b"\n")
        )
        # The lease binds the observed ref across the transport race. The checked
        # ancestry above ensures every update admitted by the lease is a fast-forward.
        repo._run(
            "push",
            "--porcelain",
            f"--force-with-lease={repo.ref}:{expected_shared}",
            "--",
            endpoint,
            f"{tip}:{repo.ref}",
        )

    def publish(self, operation_id: str) -> PublicationResult:
        if self.remote is None:
            return PublicationResult(operation_id, PublicationStatus.NOT_APPLICABLE)
        shared_tip = recovery = None
        local_completed = False
        original = None
        repo = self.repository
        try:
            original = repo.tip()
            record = self._committed_record(original, operation_id)
            local_completed = (
                record is not None
                and record.command.operation_id == operation_id
                and record.command.local == LocalOutcome.COMPLETED
            )
            operation = self.request(operation_id)
            first_shared = None
            for attempt in range(3):
                observed = preflight_policy(self.installation, ports=self.ports)
                shared = observed.views.shared
                fresh = observed.views.code_freshness in {
                    Freshness.FRESH,
                    Freshness.LOCAL_ONLY,
                }
                if (
                    observed.outcome != LocalOutcome.COMPLETED
                    or observed.policy is None
                    or not fresh
                    or shared is None
                    or shared.status != ContinuityStatus.VERIFIED
                    or shared.valid_tip is None
                ):
                    return PublicationResult(
                        operation_id,
                        PublicationStatus.PENDING,
                        shared_tip,
                        recovery,
                        observed.reason
                        or "a fresh validated shared planning tip is unavailable",
                        local_completed=local_completed,
                    )
                shared_tip = shared.valid_tip
                published = repo.read_tree(shared_tip)
                if self.record(published, operation) is not None:
                    return PublicationResult(
                        operation_id,
                        PublicationStatus.PUBLISHED,
                        shared_tip,
                        recovery,
                        local_completed=True,
                    )
                if attempt == 2 or shared_tip == first_shared:
                    break
                first_shared = shared_tip
                code = observed.views.local
                policy_ref = self.installation.policy_ref(code)
                if policy_ref is None or code.observed_commit is None:
                    break
                if operation.policy_digest != observed.policy.source.digest:
                    raise ReplayConflict(
                        "the committed policy changed before publication"
                    )
                store = self.installation.store.model_copy(
                    update={"code_default_ref": policy_ref}
                )
                target = backend(
                    repo,
                    store,
                    ports=self.ports,
                    categories=self.categories,
                    code_pin=(policy_ref, code.observed_commit),
                )
                with target._gate(repo, repo.ref) as gate:
                    local = repo.tip()
                    gate(local, None)
                    if self.record(local, operation) is None:
                        raise ReplayConflict("no matching local operation to publish")
                    candidate = local
                    if repo._run(
                        "merge-base", "--is-ancestor", shared_tip, local.revision
                    ).returncode:
                        recovery = self._recovery_ref(local.revision)
                        candidate, recovery = self._replay(
                            target, local, published, observed.policy
                        )
                        gate(local, candidate)
                        if not repo.compare_and_swap(
                            candidate.revision, local.revision
                        ):
                            raise ReplayConflict(
                                "local planning moved during publication replay"
                            )
                    self._push(candidate.revision, shared_tip)
            return PublicationResult(
                operation_id,
                PublicationStatus.PENDING,
                shared_tip,
                recovery,
                "remote observation has not verified publication",
                local_completed=local_completed,
            )
        except ReplayConflict as error:
            if local_completed and original is not None and recovery is None:
                try:
                    recovery = self._recovery_ref(original.revision)
                    self._retain_ref(recovery, original.revision)
                except (GitCommandError, OSError, ValueError):
                    recovery = None
            return PublicationResult(
                operation_id,
                PublicationStatus.CONFLICT,
                shared_tip,
                recovery,
                str(error),
                local_completed=local_completed,
            )
        except (
            GitCommandError,
            OSError,
            UnavailablePort,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            return PublicationResult(
                operation_id,
                PublicationStatus.PENDING,
                shared_tip,
                recovery,
                str(error),
                local_completed=local_completed,
            )
