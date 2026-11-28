"""Use a durable admission once and distinguish retained outputs from effective success."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Literal
from uuid import uuid4

from aitm_core.activity import ActivityEvidence
from aitm_core.execution.admission import Admission, AdmissionService, ExecutionRequest
from aitm_core.models.attempts import ExecutionRecorded
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.evidence import ActivityProvenance, ActivityRecorded
from aitm_core.models.operations import OperationCategory, PreflightOutcome
from aitm_core.store.backend import OperationContext, _preflight
from aitm_core.store.gate import RefIdentity, RefMutationKind, ref_gate
from aitm_core.store.objects import GitCommandError
from aitm_core.store.workspace import AuthorityUnavailable, BindingConflict


@dataclass(frozen=True, slots=True)
class ProcessOutcome:
    outcome: Literal["passed", "failed", "cancelled"]
    proof: str
    activity: tuple[ActivityEvidence, ...] = ()


@dataclass(frozen=True, slots=True)
class Executor:
    """Create the process under the launch lock, then wait outside it."""

    identity: str
    launch: Callable[[ExecutionRequest], Callable[[], ProcessOutcome]]


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    command: CommandResult
    observed: ExecutionRecorded | None = None
    effective: bool = False
    report: ProcessOutcome | None = None


@dataclass(frozen=True, slots=True)
class CancellationResult:
    command: CommandResult
    state: Literal["prevented", "pending", "finished", "unavailable"]


def _retained(service: AdmissionService, admission: Admission, *, historical=False):
    request = admission.request
    view = service._view(request, historical=historical)
    history = service._history(view, request)
    if not history or service._receipt(view, request, history[0]) != admission:
        raise BindingConflict("The admission does not match retained authority.")
    return view, history


def _failure(service, admission, error):
    if isinstance(error, BindingConflict):
        outcome = LocalOutcome.REFUSED
    elif isinstance(error, (AuthorityUnavailable, GitCommandError, OSError)):
        outcome = LocalOutcome.UNAVAILABLE
    else:
        outcome = LocalOutcome.INTEGRITY_ERROR
    return service._result(admission.request, outcome, str(error))


def _observation(service, view, admission, fact, observations=()):
    return service._commit(
        view,
        service._build(
            view,
            admission.request,
            "core.execution.observe",
            fact,
            observations=observations,
            category=OperationCategory.STOP_RECONCILIATION,
        ),
    ).command


def cancel(service: AdmissionService, admission: Admission) -> CancellationResult:
    """Revoke an unlaunched admission or retain a cooperative running cancellation."""
    request = admission.request
    try:
        with service.workspace.lock():
            service.workspace.require(
                StoryRef(story=request.story),
                request.binding,
                request.generation,
                request.session,
            )
            view, history = _retained(service, admission, historical=True)
            latest = history[-1]
            started = any(fact.phase == "started" for fact in history)
            state = "pending" if started else "prevented"
            if latest.phase in {"admitted", "started"}:
                observed = latest.model_copy(
                    update={
                        "phase": "cancel-requested",
                        "admission_commit": admission.admission_commit,
                        "proof": None,
                        "outcome": None,
                    }
                )
                command = _observation(service, view, admission, observed)
                return CancellationResult(
                    command, state if service._published(command) else "unavailable"
                )
            command = service._result(
                request, LocalOutcome.COMPLETED, "Cancellation readback."
            )
            if latest.phase == "finished":
                return CancellationResult(command, "finished")
            return CancellationResult(command, state)
    except (ValueError, OSError, GitCommandError) as error:
        return CancellationResult(_failure(service, admission, error), "unavailable")


def _qualified_report(report):
    return (
        isinstance(report, ProcessOutcome)
        and report.outcome in {"passed", "failed", "cancelled"}
        and isinstance(report.proof, str)
        and bool(report.proof.strip())
        and isinstance(report.activity, tuple)
        and all(isinstance(row, ActivityEvidence) for row in report.activity)
    )


def _record_result(service, admission, outcome, *, allow_effective):
    request = admission.request
    activity = (
        tuple(
            item
            for item in outcome.activity
            if item.qualified
            and (
                item.observation.session,
                item.observation.attempt,
                item.observation.generation,
                item.observation.binding,
            )
            == (request.session, request.attempt, request.generation, request.binding)
        )
        if outcome is not None
        else ()
    )
    facts = tuple(
        ActivityRecorded(
            producer=item.producer.id,
            session=row.session,
            attempt=row.attempt,
            observed_at=row.observed_at.isoformat(),
            ended_at=row.ended_at.isoformat() if row.ended_at is not None else None,
            recorded_at=row.recorded_at.isoformat(),
            coverage=item.producer.coverage_class,
            freshness="retained",
            provenance=ActivityProvenance(
                source_id=row.source_id,
                actor=row.actor,
                actor_kind=row.actor_kind,
                binding=row.binding,
                generation=row.generation,
                producer_version=item.producer.version,
                measurement_contract=item.producer.measurement_contract,
                proof_refs=row.evidence,
            ),
        )
        for item in activity
        for row in (item.observation,)
    )
    for _ in range(2):
        view, history = _retained(service, admission, historical=True)
        latest = history[-1]
        if (
            not any(fact.phase == "started" for fact in history)
            or latest.phase not in {"started", "cancel-requested", "uncertain"}
            or latest.phase == "uncertain"
            and outcome is None
        ):
            return ExecutionResult(
                service._result(
                    request,
                    LocalOutcome.REFUSED,
                    "No unsettled launch can accept this result.",
                ),
                latest,
            )
        observed = latest.model_copy(
            update={
                "phase": "finished" if outcome is not None else "uncertain",
                "outcome": outcome.outcome if outcome is not None else "unavailable",
                "proof": outcome.proof
                if outcome is not None
                else "The claimed launch has no qualified result.",
            }
        )
        command = _observation(service, view, admission, observed, facts)
        if command.local != LocalOutcome.CONFLICT:
            break
    if not service._published(command):
        return ExecutionResult(command, report=outcome)

    try:
        view, history = _retained(service, admission)
        if history[-1] != observed:
            return ExecutionResult(command, observed)
        probe = service._build(view, request, "core.execution.effectiveness", observed)
        checked = _preflight(
            OperationContext(probe, view.snapshot, (view.attempt,)),
            replace(service.ports, attempt_installation=service.installation),
        )
        if (
            checked.outcome != PreflightOutcome.PASSED
            or not allow_effective
            or outcome is None
            or outcome.outcome != "passed"
            or latest.phase != "started"
        ):
            return ExecutionResult(command, observed)
        service._check_candidate(request, view.attempt)
        unchanged = service.installation.repository.tip() == view.snapshot
        return ExecutionResult(command, observed, unchanged)
    except (ValueError, OSError, GitCommandError):
        return ExecutionResult(command, observed)


def observe_result(
    service: AdmissionService, admission: Admission, outcome: ProcessOutcome
) -> ExecutionResult:
    """Reconcile exact diagnostic output on a spent admission without dispatch."""
    request = admission.request
    if not _qualified_report(outcome):
        return ExecutionResult(
            service._result(
                request, LocalOutcome.REFUSED, "The result observation is unqualified."
            )
        )
    try:
        with service.workspace.lock():
            service.workspace.require(
                StoryRef(story=request.story),
                request.binding,
                request.generation,
                request.session,
            )
            return _record_result(service, admission, outcome, allow_effective=False)
    except (ValueError, OSError, GitCommandError) as error:
        return ExecutionResult(_failure(service, admission, error), report=outcome)


def dispatch(
    service: AdmissionService, admission: Admission, executor: Executor
) -> ExecutionResult:
    """Grant one launch, then retain its outcome before considering effective success."""
    request = admission.request
    if executor.identity != request.executor:
        return ExecutionResult(
            service._result(
                request,
                LocalOutcome.REFUSED,
                "The executor differs from the admission.",
            )
        )
    workspace = service.workspace
    repository = service.installation.repository
    wait = None
    try:
        with workspace.lock():
            view, history = _retained(service, admission)
            latest = history[-1]
            if latest.phase != "admitted":
                return ExecutionResult(
                    service._result(
                        request,
                        LocalOutcome.REFUSED,
                        "Launch authority was already used or cancelled.",
                    ),
                    latest,
                )
            service._check_candidate(request, view.attempt)
            started = latest.model_copy(
                update={
                    "phase": "started",
                    "admission_commit": admission.admission_commit,
                    "proof": f"launch-claim:{uuid4().hex}",
                }
            )
            claim = service._commit(
                view, service._build(view, request, "core.execution.start", started)
            ).command
            if not service._published(claim):
                return ExecutionResult(claim)
            view, history = _retained(service, admission)
            with ref_gate(
                repository, RefIdentity(repository.ref), RefMutationKind.PLANNING
            ) as gate:
                if gate.before != view.snapshot or history[-1] != started:
                    raise BindingConflict(
                        "Authority moved after the single-use launch claim."
                    )
                service._check_candidate(request, view.attempt)
                try:
                    wait = executor.launch(request)
                except Exception:
                    # An adapter can fail after it has already created the process.
                    pass
    except (ValueError, OSError, GitCommandError) as error:
        return ExecutionResult(_failure(service, admission, error))

    outcome = None
    if callable(wait):
        try:
            reported = wait()
            if _qualified_report(reported):
                outcome = reported
        except Exception:
            pass
    try:
        with workspace.lock():
            return _record_result(service, admission, outcome, allow_effective=True)
    except (ValueError, OSError, GitCommandError) as error:
        return ExecutionResult(_failure(service, admission, error), report=outcome)
