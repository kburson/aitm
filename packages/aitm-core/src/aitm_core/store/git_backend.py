"""Planning transactions backed by pinned Git trees and literal-ref CAS."""

from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import DIGEST
from aitm_core.models.evidence import GuardEvaluated
from aitm_core.models.operations import Operation, PreflightResult, WriteAuthorization
from aitm_core.services import ServicePorts
from aitm_core.store.backend import (
    Blobs,
    OperationCategories,
    OperationEvaluation,
    OperationResult,
    Snapshot,
    evaluate_operation,
)
from aitm_core.store.objects import GitCommandError, Repository, UnknownTree

_RECORD_ROOT = ".aitm/operations"


class ValidationRejected(ValueError):
    """The injected planning validation gate refused the candidate."""


type ValidateCandidate = Callable[[Snapshot, Snapshot | None], None]


class ValidationGate(Protocol):
    """Own validation and exclusion for the full literal-ref transaction."""

    def __call__(
        self, repository: Repository, target_ref: str
    ) -> AbstractContextManager[ValidateCandidate]: ...


class _Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["aitm.operation-record/v1"] = "aitm.operation-record/v1"
    request_digest: DIGEST
    base: str
    command: CommandResult
    reason: str | None
    guards: tuple[GuardEvaluated, ...]
    preflight: PreflightResult | None
    authorization: WriteAuthorization | None

    def result(self, snapshot: Snapshot) -> OperationResult:
        return OperationResult(
            self.command,
            snapshot,
            self.reason,
            self.guards,
            self.preflight,
            self.authorization,
        )


def _record_path(operation_id: str) -> str:
    return f"{_RECORD_ROOT}/{sha256(operation_id.encode('utf-8')).hexdigest()}.json"


class GitBackend:
    def __init__(
        self,
        repository: Repository,
        gate: ValidationGate,
        *,
        ports: ServicePorts | None = None,
        categories: OperationCategories | None = None,
    ) -> None:
        if not callable(gate):
            raise TypeError("a planning ValidationGate is required")
        self.repository = repository
        self._gate = gate
        self._ports = ports if ports is not None else ServicePorts()
        self._categories = dict(categories or {})

    def snapshot(self) -> Snapshot:
        return self.repository.tip()

    def read_tree(self, oid: str) -> Snapshot:
        return self.repository.read_tree(oid)

    def read(self, snapshot: Snapshot, paths: Sequence[str]) -> Blobs:
        if snapshot != self.read_tree(snapshot.revision):
            raise ValueError("snapshot does not match a pinned tree in this repository")
        return self.repository.read_blobs(snapshot.tree, paths)

    def _failure(
        self, op: Operation, snapshot: Snapshot, outcome: LocalOutcome, reason: str
    ) -> OperationResult:
        return OperationResult(
            CommandResult(operation_id=op.operation_id, local=outcome), snapshot, reason
        )

    def _recover(
        self, op: Operation, digest: str, record_path: str, current: Snapshot
    ) -> OperationResult | None:
        raw = self.repository.read_blobs(current.tree, (record_path,))[record_path]
        if raw is None:
            return None
        record = _Record.model_validate_json(raw)
        if (
            record.command.operation_id != op.operation_id
            or record.request_digest != digest
        ):
            return self._failure(
                op, current, LocalOutcome.INTEGRITY_ERROR, "operation-identity-reused"
            )
        origin = self.repository.record_origin(current, record_path)
        if self.repository.parent(origin) != record.base:
            raise ValueError("operation record does not match its commit parent")
        return record.result(origin)

    def _record(
        self,
        op: Operation,
        digest: str,
        current: Snapshot,
        evaluation: OperationEvaluation,
    ) -> _Record:
        completed = evaluation.outcome is LocalOutcome.COMPLETED
        pending = op.pending_actions if completed else ()
        authorization = evaluation.authorization
        if (
            not completed
            and authorization is not None
            and authorization.extension is not None
        ):
            authorization = authorization.model_copy(
                update={"extension": None, "owned_paths": ()}
            )
        return _Record(
            request_digest=digest,
            base=current.revision,
            command=CommandResult(
                operation_id=op.operation_id, local=evaluation.outcome, pending=pending
            ),
            reason=evaluation.reason,
            guards=evaluation.guards,
            preflight=evaluation.preflight,
            authorization=authorization,
        )

    def _extension_path_conflict(self, current: Snapshot, op: Operation) -> bool:
        from aitm_core.store.validation import _entries

        writes = {item.path for item in op.change.writes}
        if not writes:
            return False
        existing = _entries(self.repository, current)
        occupied = writes | existing.keys()
        return any(
            any(str(parent) in occupied for parent in PurePosixPath(path).parents)
            or any(other.startswith(path + "/") for other in occupied)
            for path in writes
        )

    def transact(self, op: Operation, expected: Snapshot) -> OperationResult:
        current = expected
        try:
            op = Operation.model_validate(op)
            digest = op.request_digest
            record_path = _record_path(op.operation_id)
            with self._gate(self.repository, self.repository.ref) as validate:
                current = self.snapshot()
                validate(current, None)
                try:
                    known = self.read_tree(expected.revision)
                except UnknownTree:
                    known = None
                if expected != known:
                    return self._failure(
                        op, current, LocalOutcome.INTEGRITY_ERROR, "unknown-snapshot"
                    )
                prior = self._recover(op, digest, record_path, current)
                if prior is not None:
                    return prior
                if expected != current:
                    return self._failure(
                        op, current, LocalOutcome.CONFLICT, "snapshot-changed"
                    )
                if any(
                    item.path == _RECORD_ROOT
                    or item.path.startswith(_RECORD_ROOT + "/")
                    for item in op.change.writes
                ):
                    raise ValidationRejected("operation records are owned by the store")
                if op.owner.extension is not None and self._extension_path_conflict(
                    current, op
                ):
                    return self._failure(
                        op,
                        current,
                        LocalOutcome.REFUSED,
                        "extension write would change a path type",
                    )
                read_paths = tuple(read.path for read in op.change.read_set)
                evidence = self.repository.read_blobs(current.tree, read_paths)
                evaluation = evaluate_operation(
                    op,
                    current,
                    evidence,
                    ports=self._ports,
                    categories=self._categories,
                )
                record = self._record(op, digest, current, evaluation)
                if not evaluation.record:
                    return record.result(current)

                writes = {
                    **evaluation.writes,
                    record_path: record.model_dump_json().encode("utf-8"),
                }
                candidate = self.repository.create_commit(
                    current, writes, op.operation_id
                )
                validate(current, candidate)
                if not self.repository.compare_and_swap(
                    candidate.revision, current.revision
                ):
                    return self._failure(
                        op, self.snapshot(), LocalOutcome.CONFLICT, "snapshot-changed"
                    )
                current = candidate
                observed = self.snapshot()
                if observed != candidate:
                    return OperationResult(
                        CommandResult(
                            operation_id=op.operation_id,
                            local=LocalOutcome.CONFLICT,
                            evidence=(
                                f"Planning tip advanced to {observed.revision}.",
                            ),
                            recovery="Reconcile the retained commit by operation ID.",
                        ),
                        candidate,
                        "ref-advanced-after-cas",
                    )
                return record.result(candidate)
        except (GitCommandError, OSError) as error:
            return self._failure(op, current, LocalOutcome.UNAVAILABLE, str(error))
        except ValueError as error:
            return self._failure(op, current, LocalOutcome.INTEGRITY_ERROR, str(error))
