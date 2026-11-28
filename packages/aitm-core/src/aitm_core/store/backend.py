"""Shared snapshot, operation evaluation and store service contracts."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Protocol, cast

from aitm_core.events import StoryState, UnavailableReducer, core_reducers, fold
from aitm_core.models.attempts import AttemptRecord, AttemptState
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.events import validate_envelope
from aitm_core.models.evidence import GuardEvaluated
from aitm_core.models.lifecycle import StateChange
from aitm_core.models.operations import (
    EventAppend,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
    story_scope,
)
from aitm_core.services import ServicePorts, UnavailablePort

type Blobs = Mapping[str, bytes | None]
type OperationCategories = Mapping[tuple[str, int], OperationCategory]


@dataclass(frozen=True, slots=True)
class Snapshot:
    store: str
    revision: str
    tree: str


@dataclass(frozen=True, slots=True)
class OperationContext:
    operation: Operation
    snapshot: Snapshot
    attempts: tuple[AttemptRecord, ...]


@dataclass(frozen=True, slots=True)
class OperationResult:
    command: CommandResult
    snapshot: Snapshot
    reason: str | None = None
    guards: tuple[GuardEvaluated, ...] = ()
    preflight: PreflightResult | None = None
    authorization: WriteAuthorization | None = None


class Backend(Protocol):
    def snapshot(self) -> Snapshot: ...

    def read(self, snapshot: Snapshot, paths: Sequence[str]) -> Blobs: ...

    def transact(self, op: Operation, expected: Snapshot) -> OperationResult: ...


class WriteAuthorizer(Protocol):
    def __call__(
        self, owner: OperationOwner, change: RelatedWriteSet
    ) -> WriteAuthorization: ...


class AttemptPreflight(Protocol):
    def __call__(self, context: OperationContext) -> PreflightResult: ...


class PendingActionRunner(Protocol):
    def __call__(self, snapshot: Snapshot) -> tuple[CommandResult, ...]: ...


@dataclass(frozen=True, slots=True)
class OperationEvaluation:
    outcome: LocalOutcome
    reason: str | None = None
    preflight: PreflightResult | None = None
    authorization: WriteAuthorization | None = None
    guards: tuple[GuardEvaluated, ...] = ()
    writes: Blobs = field(default_factory=dict)
    record: bool = False


def _read_attempts(blobs: Blobs) -> tuple[AttemptRecord, ...]:
    attempts = []
    for path, data in blobs.items():
        story = story_scope(path)
        if story is None or path != story_event_path(story) or not data:
            continue
        state = _replay(story, data)
        attempt = state.domains.get("attempts")
        if isinstance(attempt, AttemptState) and attempt.current_attempt is not None:
            attempts.append(attempt.attempts[attempt.current_attempt])
    return tuple(attempts)


def _replay(story: int, data: bytes) -> StoryState:
    state = fold(data.splitlines(keepends=True), core_reducers())
    if state.story_id not in (None, story):
        raise ValueError("event stream belongs to another story")
    return state


def _apply_events(
    op: Operation, append: EventAppend, before: bytes, read_set_digest: str
) -> bytes:
    existing = {validate_envelope(line).id for line in before.splitlines(keepends=True)}
    records = []
    for raw in append.records:
        event = validate_envelope(raw)
        if event.story != append.story or event.operation_id != op.operation_id:
            raise ValueError("event is outside the operation's story or identity")
        if event.actor != op.owner.actor:
            raise ValueError("event actor disagrees with operation authority")
        if event.policy_digest not in (None, op.policy_digest):
            raise ValueError("event policy differs from the operation")
        if event.read_set_digest not in (None, read_set_digest):
            raise ValueError("event read set differs from the operation")
        if event.id in existing:
            raise ValueError("event identity is already present")
        records.append(raw.removesuffix(b"\n") + b"\n")
        existing.add(event.id)
    separator = b"\n" if before and not before.endswith(b"\n") else b""
    full = before + separator + b"".join(records)
    _replay(append.story, full)
    return full


def _preflight(context: OperationContext, ports: ServicePorts) -> PreflightResult:
    if not context.attempts:
        return PreflightResult(outcome=PreflightOutcome.NOT_APPLICABLE)
    check = ports.attempt_preflight
    if not callable(check):
        return PreflightResult(
            outcome=PreflightOutcome.UNAVAILABLE, reason="attempt-preflight-unavailable"
        )
    try:
        outcome = cast(AttemptPreflight, check)(context)
    except UnavailablePort as error:
        return PreflightResult(outcome=PreflightOutcome.UNAVAILABLE, reason=str(error))
    if (
        not isinstance(outcome, PreflightResult)
        or outcome.outcome == PreflightOutcome.NOT_APPLICABLE
    ):
        return PreflightResult(
            outcome=PreflightOutcome.UNAVAILABLE, reason="attempt-preflight-unqualified"
        )
    return outcome


def _advisory_transition(op: Operation, failures: tuple[GuardEvaluated, ...]) -> bool:
    if (
        op.intent.kind != "state.transition"
        or op.owner.extension is not None
        or op.change.writes
        or op.pending_actions
        or len(op.change.events) != 1
        or any(
            guard.mode != "advisory" or guard.slot == "prepare" for guard in failures
        )
    ):
        return False
    try:
        change = StateChange.model_validate_json(op.intent.payload)
        if (
            change.mode != "advisory"
            or change.edge.kind != "normal"
            or change.to_state.terminal
        ):
            return False
        records = tuple(validate_envelope(raw) for raw in op.change.events[0].records)
        if any(
            event.type
            not in {
                "core.guard.evaluated",
                "core.attempt.started",
                "core.attempt.clock.changed",
                "core.state.changed",
            }
            for event in records
        ):
            return False
        observed = tuple(
            event.data for event in records if event.type == "core.guard.evaluated"
        )
        transitions = tuple(
            event.data for event in records if event.type == "core.state.changed"
        )
        return transitions == (
            change.model_dump(mode="json", by_alias=True),
        ) and observed == tuple(guard.model_dump(mode="json") for guard in op.guards)
    except ValueError:
        return False


def evaluate_operation(
    op: Operation,
    snapshot: Snapshot,
    blobs: Blobs,
    *,
    ports: ServicePorts,
    categories: OperationCategories,
) -> OperationEvaluation:
    """Evaluate against pinned blobs and prepare one atomic store update."""
    category = categories.get(
        (op.intent.kind, op.intent.version), OperationCategory.NORMAL
    )
    if op.category != category:
        return OperationEvaluation(
            LocalOutcome.REFUSED, "operation-category-out-of-scope"
        )
    for read in op.change.read_set:
        blob = blobs[read.path]
        digest = sha256(blob).hexdigest() if blob is not None else None
        if digest != read.digest:
            return OperationEvaluation(LocalOutcome.CONFLICT, "read-set-changed")

    check = ports.write_authorization
    if not callable(check):
        return OperationEvaluation(
            LocalOutcome.UNAVAILABLE, "write-authorizer-unavailable"
        )
    try:
        authorization = cast(WriteAuthorizer, check)(op.owner, op.change)
    except UnavailablePort as error:
        return OperationEvaluation(LocalOutcome.UNAVAILABLE, str(error))
    if not isinstance(authorization, WriteAuthorization):
        return OperationEvaluation(
            LocalOutcome.UNAVAILABLE, "write-authority-unqualified"
        )
    if not authorization.allowed:
        return OperationEvaluation(
            LocalOutcome.REFUSED, authorization.reason, authorization=authorization
        )

    if authorization.extension != op.owner.extension or (
        op.owner.extension is not None
        and set(authorization.owned_paths) != {item.path for item in op.change.writes}
    ):
        return OperationEvaluation(
            LocalOutcome.UNAVAILABLE, "extension-write-authority-unqualified"
        )

    try:
        context = OperationContext(op, snapshot, _read_attempts(blobs))
    except UnavailableReducer as error:
        return OperationEvaluation(LocalOutcome.UNAVAILABLE, str(error))
    except ValueError as error:
        return OperationEvaluation(LocalOutcome.INTEGRITY_ERROR, str(error))
    preflight = _preflight(context, ports)
    if preflight.outcome in (PreflightOutcome.UNAVAILABLE, PreflightOutcome.BLOCKED):
        outcome = (
            LocalOutcome.UNAVAILABLE
            if preflight.outcome == PreflightOutcome.UNAVAILABLE
            else LocalOutcome.REFUSED
        )
        return OperationEvaluation(outcome, preflight.reason, preflight, authorization)

    read_set_digest = op.change.read_set_digest
    if any(
        guard.operation != op.operation_id
        or guard.policy_digest != op.policy_digest
        or guard.read_set_digest != read_set_digest
        for guard in op.guards
    ):
        return OperationEvaluation(
            LocalOutcome.INTEGRITY_ERROR,
            "guard-evidence-mismatch",
            preflight,
            authorization,
        )
    failures = tuple(guard for guard in op.guards if not guard.ok)
    if failures and not _advisory_transition(op, failures):
        return OperationEvaluation(
            LocalOutcome.REFUSED,
            "guard-refused",
            preflight,
            authorization,
            op.guards,
            record=True,
        )

    writes = {item.path: item.content for item in op.change.writes}
    try:
        for append in op.change.events:
            writes[append.path] = _apply_events(
                op, append, blobs[append.path] or b"", read_set_digest
            )
    except UnavailableReducer as error:
        return OperationEvaluation(
            LocalOutcome.UNAVAILABLE, str(error), preflight, authorization
        )
    except ValueError as error:
        return OperationEvaluation(
            LocalOutcome.INTEGRITY_ERROR, str(error), preflight, authorization
        )
    return OperationEvaluation(
        LocalOutcome.COMPLETED,
        preflight=preflight,
        authorization=authorization,
        guards=op.guards,
        writes=writes,
        record=True,
    )
