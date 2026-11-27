"""In-memory implementation of the pinned planning-store transaction contract."""

from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import PurePosixPath
from threading import Lock
from uuid import uuid4

import rfc8785
from pydantic import ValidationError

from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.operations import Operation, repository_path
from aitm_core.services import ServicePorts
from aitm_core.store.backend import (
    Blobs,
    OperationCategories,
    OperationEvaluation,
    OperationResult,
    Snapshot,
    evaluate_operation,
)


def _check_tree(files: Mapping[str, bytes]) -> None:
    for path in files:
        if any(parent.as_posix() in files for parent in PurePosixPath(path).parents):
            raise ValueError("a repository path cannot be both a directory and a blob")


class MemoryBackend:
    def __init__(
        self,
        files: Mapping[str, bytes] | None = None,
        *,
        ports: ServicePorts | None = None,
        categories: OperationCategories | None = None,
    ) -> None:
        initial = {
            repository_path(path): content for path, content in (files or {}).items()
        }
        if any(not isinstance(content, bytes) for content in initial.values()):
            raise TypeError("snapshot files require immutable bytes")
        _check_tree(initial)
        self._store = uuid4().hex
        self._lock = Lock()
        self._ports = ports if ports is not None else ServicePorts()
        self._categories = dict(categories or {})
        self._versions: dict[Snapshot, dict[str, bytes]] = {}
        self._results: dict[str, tuple[str, OperationResult]] = {}
        self._current = self._snapshot_for(initial)
        self._versions[self._current] = initial

    def _snapshot_for(
        self,
        files: Mapping[str, bytes],
        operation: tuple[str, str] | None = None,
    ) -> Snapshot:
        hashes = {path: sha256(blob).hexdigest() for path, blob in files.items()}
        operations = {name: digest for name, (digest, _) in self._results.items()}
        if operation is not None:
            identity, digest = operation
            operations[identity] = digest
        tree = sha256(
            rfc8785.dumps({"files": hashes, "operations": operations})
        ).hexdigest()
        return Snapshot(self._store, str(len(self._versions)), tree)

    def snapshot(self) -> Snapshot:
        with self._lock:
            return self._current

    def read(self, snapshot: Snapshot, paths: Sequence[str]) -> Blobs:
        with self._lock:
            files = self._versions[snapshot]
            return {path: files.get(repository_path(path)) for path in paths}

    def _retry(self, op: Operation, digest: str) -> OperationResult | None:
        previous = self._results.get(op.operation_id)
        if previous is None:
            return None
        prior_digest, result = previous
        if prior_digest == digest:
            return result
        return self._result(
            op,
            self._current,
            OperationEvaluation(
                LocalOutcome.INTEGRITY_ERROR, "operation-identity-reused"
            ),
        )

    def _result(
        self, op: Operation, snapshot: Snapshot, evaluation: OperationEvaluation
    ) -> OperationResult:
        pending = (
            op.pending_actions if evaluation.outcome == LocalOutcome.COMPLETED else ()
        )
        return OperationResult(
            CommandResult(
                operation_id=op.operation_id, local=evaluation.outcome, pending=pending
            ),
            snapshot,
            evaluation.reason,
            evaluation.guards,
            evaluation.preflight,
            evaluation.authorization,
        )

    def transact(self, op: Operation, expected: Snapshot) -> OperationResult:
        try:
            op = Operation.model_validate(op)
            digest = op.request_digest
        except (ValidationError, rfc8785.CanonicalizationError):
            return self._result(
                op,
                self.snapshot(),
                OperationEvaluation(LocalOutcome.INTEGRITY_ERROR, "invalid-operation"),
            )
        with self._lock:
            if expected not in self._versions:
                return self._result(
                    op,
                    self._current,
                    OperationEvaluation(
                        LocalOutcome.INTEGRITY_ERROR, "unknown-snapshot"
                    ),
                )
            if (previous := self._retry(op, digest)) is not None:
                return previous
            if expected != self._current:
                return self._result(
                    op,
                    self._current,
                    OperationEvaluation(LocalOutcome.CONFLICT, "snapshot-changed"),
                )
            files = self._versions[expected]
            blobs = {item.path: files.get(item.path) for item in op.change.read_set}

        evaluation = evaluate_operation(
            op, expected, blobs, ports=self._ports, categories=self._categories
        )
        with self._lock:
            if (previous := self._retry(op, digest)) is not None:
                return previous
            if expected != self._current:
                return self._result(
                    op,
                    self._current,
                    OperationEvaluation(LocalOutcome.CONFLICT, "snapshot-changed"),
                )
            if not evaluation.record:
                return self._result(op, expected, evaluation)
            updated = dict(files)
            for path, value in evaluation.writes.items():
                if value is None:
                    updated.pop(path, None)
                else:
                    updated[path] = value
            try:
                _check_tree(updated)
            except ValueError as error:
                return self._result(
                    op,
                    expected,
                    OperationEvaluation(LocalOutcome.INTEGRITY_ERROR, str(error)),
                )
            snapshot = self._snapshot_for(updated, (op.operation_id, digest))
            result = self._result(op, snapshot, evaluation)
            self._versions[snapshot] = updated
            self._results[op.operation_id] = (digest, result)
            self._current = snapshot
            return result
