"""Single-use execution admission against the installed planning authority."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

import rfc8785

from aitm_core.models.attempts import (
    AttemptBoundary,
    AttemptRecord,
    AttemptState,
    BindingPurpose,
    ExecutionCandidate,
    ExecutionRecorded,
    ObjectId,
    Positive,
    SourceSnapshot,
    Text,
)
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.relationships import EventContext, StoryGraph, read_graph
from aitm_core.rules.trips import _append, admission_commit, current_attempt
from aitm_core.services import ServicePorts, mutate, preflight_policy
from aitm_core.store.backend import OperationResult, Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness, _direct_ref, _is_ancestor
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError
from aitm_core.store.workspace import AuthorityUnavailable, BindingConflict, Workspace


class ExecutionRequest(AttemptBoundary):
    story: Positive
    binding: Text
    session: Text
    request_id: Text
    action_key: Text
    executor: Text
    candidate: ExecutionCandidate

    @property
    def execution_id(self) -> str:
        return sha256(
            rfc8785.dumps(
                [
                    self.story,
                    self.attempt,
                    self.generation,
                    self.binding,
                    self.session,
                    self.request_id,
                ]
            )
        ).hexdigest()


@dataclass(frozen=True, slots=True)
class Admission:
    request: ExecutionRequest
    execution_id: str
    authority_store: str
    authority_ref: str
    admission_commit: ObjectId


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    command: CommandResult
    admission: Admission | None = None


@dataclass(frozen=True, slots=True)
class _View:
    snapshot: Snapshot
    policy: str
    graph: StoryGraph
    attempt: AttemptRecord


@dataclass(frozen=True, slots=True)
class AdmissionService:
    installation: Installation
    ports: ServicePorts = ServicePorts()
    verify_capture: Callable[[ExecutionRequest], bool] | None = None

    @property
    def workspace(self) -> Workspace:
        return Workspace(self.installation)

    def _view(self, request: ExecutionRequest, *, historical: bool = False) -> _View:
        policy = preflight_policy(self.installation, ports=self.ports)
        repo = self.installation.repository
        snapshot = repo.tip()
        shared = policy.views.shared
        if (
            policy.outcome != LocalOutcome.COMPLETED
            or policy.policy is None
            or policy.views.planning.observed_commit != snapshot.revision
            or policy.views.code_freshness
            not in (Freshness.FRESH, Freshness.LOCAL_ONLY)
            or self.installation.store.planning_remote is not None
            and (
                shared is None
                or shared.status != ContinuityStatus.VERIFIED
                or shared.valid_tip != snapshot.revision
            )
        ):
            raise AuthorityUnavailable("Fresh execution authority is unavailable.")
        graph = read_graph(repo, snapshot)
        state = graph.states.get(request.story)
        attempt = current_attempt(state) if state is not None else None
        if historical and state is not None:
            domain = state.domains.get("attempts")
            attempt = (
                domain.attempts.get(request.attempt)
                if isinstance(domain, AttemptState)
                else None
            )
        if (
            attempt is None
            or attempt.started.attempt != request.attempt
            or (
                not historical
                and (attempt.generation, attempt.binding)
                != (request.generation, request.binding)
            )
        ):
            raise BindingConflict(
                "Execution requires the current attempt and generation."
            )
        return _View(snapshot, policy.policy.source.digest, graph, attempt)

    def _check_candidate(
        self, request: ExecutionRequest, attempt: AttemptRecord
    ) -> SourceSnapshot:
        binding = self.workspace.require(
            StoryRef(story=request.story),
            request.binding,
            request.generation,
            request.session,
        )
        if (
            binding.purpose != BindingPurpose.IMPLEMENTATION
            or binding.attempt != request.attempt
            or binding.source is None
            or binding.source != attempt.source
            or binding.branch is None
            or attempt.closed
            or attempt.clock_mode != "active"
            or (attempt.started.provisional and attempt.reconciliation is None)
        ):
            raise BindingConflict(
                "Execution requires the current active implementation binding."
            )
        repo = self.installation.repository
        source = request.candidate.source
        if (
            _direct_ref(repo, binding.branch) != source.commit
            or repo.read_tree(source.commit).tree != source.tree
            or _is_ancestor(repo, binding.source.commit, source.commit) is not True
        ):
            raise BindingConflict(
                "The exact execution candidate is stale or unrelated."
            )
        if request.candidate.capture_manifest is not None and (
            self.verify_capture is None or self.verify_capture(request) is not True
        ):
            raise BindingConflict("The exact capture manifest is unavailable or stale.")
        return binding.source

    def _history(self, view: _View, request: ExecutionRequest):
        history = view.attempt.executions.get(request.execution_id, ())
        if history:
            first = history[0]
            if (
                first.request_id != request.request_id
                or first.generation != request.generation
                or first.action_key != request.action_key
                or first.executor != request.executor
                or first.candidate != request.candidate
                or first.authority_store != self.installation.store.store_uuid
                or first.authority_ref != self.installation.store.planning_ref
            ):
                raise BindingConflict(
                    "The retained execution request has different authority."
                )
        return history

    def _receipt(self, view: _View, request: ExecutionRequest, fact: ExecutionRecorded):
        commit = admission_commit(
            self.installation.repository, view.snapshot, view.graph, request.story, fact
        )
        return Admission(
            request, fact.execution_id, fact.authority_store, fact.authority_ref, commit
        )

    def _build(
        self,
        view: _View,
        request: ExecutionRequest,
        kind: str,
        *facts,
        observations=(),
        category=OperationCategory.NORMAL,
    ):
        owner = OperationOwner(
            actor=EventActor(kind="tool", harness="aitm-core", session=request.session),
            binding=request.binding,
            generation=request.generation,
        )
        context = EventContext(
            uuid4().hex, owner, datetime.now(UTC).isoformat(), view.policy
        )
        path = story_event_path(request.story)
        raw = view.graph.logs[path]
        reads = (ReadExpectation(path=path, digest=sha256(raw).hexdigest()),)
        append = _append(
            context,
            view.graph.states[request.story],
            raw,
            [
                *(("core.execution.recorded", fact, fact.phase) for fact in facts),
                *(
                    ("core.activity.recorded", fact, f"activity-{i}")
                    for i, fact in enumerate(observations)
                ),
            ],
            include_null_data=bool(observations),
        )
        return Operation(
            operation_id=context.operation,
            owner=owner,
            policy_digest=view.policy,
            category=category,
            intent=FinalizationIntent(
                kind=kind,
                version=1,
                payload=facts[-1].model_dump_json().encode(),
                related_preconditions=reads,
            ),
            change=RelatedWriteSet(read_set=reads, events=(append,)),
        )

    def _commit(self, view: _View, operation: Operation) -> OperationResult:
        def authorize(owner, change):
            return WriteAuthorization(
                allowed=owner == operation.owner and change == operation.change,
                origin=AuthorityOrigin.REGISTERED,
            )

        ports = replace(self.ports, write_authorization=authorize)
        categories = None
        if operation.category == OperationCategory.STOP_RECONCILIATION:

            def check(context):
                return PreflightResult(
                    outcome=PreflightOutcome.PASSED
                    if context.operation == operation
                    else PreflightOutcome.BLOCKED,
                    origin=AuthorityOrigin.REGISTERED,
                )

            ports = replace(ports, attempt_preflight=check)
            categories = {(operation.intent.kind, 1): operation.category}

        return mutate(
            self.installation,
            operation,
            view.snapshot,
            ports=ports,
            categories=categories,
        )

    def _published(self, command: CommandResult) -> bool:
        expected = (
            PublicationOutcome.VERIFIED
            if self.installation.store.planning_remote is not None
            else PublicationOutcome.NOT_APPLICABLE
        )
        return (
            command.local == LocalOutcome.COMPLETED and command.publication == expected
        )

    def _result(self, request: ExecutionRequest, outcome: LocalOutcome, reason: str):
        return CommandResult(
            operation_id=request.execution_id, local=outcome, evidence=(reason,)
        )

    def admit(self, request: ExecutionRequest) -> AdmissionResult:
        """Grant one exact request using the current authority ref and attempt tail."""
        try:
            with self.workspace.lock():
                view = self._view(request)
                source: SourceSnapshot = self._check_candidate(request, view.attempt)
                history = self._history(view, request)
                if history:
                    admission = self._receipt(view, request, history[0])
                    command = CommandResult(
                        operation_id=request.execution_id,
                        local=LocalOutcome.COMPLETED,
                        publication=PublicationOutcome.VERIFIED
                        if self.installation.store.planning_remote is not None
                        else PublicationOutcome.NOT_APPLICABLE,
                    )
                    return AdmissionResult(command, admission)
                prepared = ExecutionRecorded(
                    attempt=request.attempt,
                    generation=request.generation,
                    execution_id=request.execution_id,
                    request_id=request.request_id,
                    action_key=request.action_key,
                    executor=request.executor,
                    authority_store=self.installation.store.store_uuid,
                    authority_ref=self.installation.store.planning_ref,
                    expected_prior_version=view.snapshot.revision,
                    source=source,
                    candidate=request.candidate,
                    phase="prepared",
                )
                admitted = prepared.model_copy(
                    update={
                        "phase": "admitted",
                        "proof": f"planning:{view.snapshot.revision}",
                    }
                )
                operation = self._build(
                    view, request, "core.execution.admit", prepared, admitted
                )
                result = self._commit(view, operation)
                if not self._published(result.command):
                    return AdmissionResult(result.command)
                verified = self._view(request)
                history = self._history(verified, request)
                if not history:
                    raise AuthorityUnavailable(
                        "The exact admission is absent from authoritative readback."
                    )
                return AdmissionResult(
                    result.command, self._receipt(verified, request, history[0])
                )
        except (AuthorityUnavailable, GitCommandError, OSError) as error:
            return AdmissionResult(
                self._result(request, LocalOutcome.UNAVAILABLE, str(error))
            )
        except BindingConflict as error:
            return AdmissionResult(
                self._result(request, LocalOutcome.REFUSED, str(error))
            )
        except ValueError as error:
            return AdmissionResult(
                self._result(request, LocalOutcome.INTEGRITY_ERROR, str(error))
            )
