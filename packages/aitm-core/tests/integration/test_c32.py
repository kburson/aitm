"""Qualify installed execution admission against the authoritative Git ref."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from threading import Event

from aitm_core.activity import ActivityObservation, ingest_activity
from aitm_core.events import core_reducers, fold
from aitm_core.execution.admission import AdmissionService, ExecutionRequest
from aitm_core.execution.executor import (
    Executor,
    ProcessOutcome,
    cancel,
    dispatch,
    observe_result,
)
from aitm_core.ext.api import ProducerRef
from aitm_core.models.attempts import AttemptStarted, ClockChanged, ExecutionCandidate
from aitm_core.models.binding import Binding
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.operations import story_event_path
from aitm_core.relationships import EventContext, read_graph
from aitm_core.rules.trips import _append
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.setup.journal import state_directory
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import (
    DEFAULT,
    PLANNING,
    PLANNING_REMOTE,
    WORKFLOW,
    commit_file,
    empty_planning_root,
    git,
    identify,
)
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned
from tests.integration.test_c16 import cli
from tests.integration.test_c22 import OWNER, STAMP
from tests.integration.test_c28 import PROFILE
from tests.support.c07 import installation, settings_at
from tests.unit.test_c15 import graduated


def installed_attempt(topology):
    anchor = topology.policy.installation
    code = commit_file(topology.code, WORKFLOW, PROFILE)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    return bind_attempt(anchor, code, topology.advance_planning)


def bind_attempt(anchor, code, advance_planning):
    initial = loads(graduated())
    initial["data"]["initial_state"] = {
        "workflow_id": "project",
        "revision": sha256(PROFILE).hexdigest(),
        "state_id": "dev",
        "label": "Implement",
    }
    raw = dumps(initial).encode() + b"\n"
    event_path = story_event_path(16)
    advance_planning(event_path, raw)
    policy = preflight_policy(anchor).policy
    assert policy is not None
    state_directory(anchor.repository).mkdir(parents=True, exist_ok=True)
    _record_installation(anchor, policy.revision)
    root = anchor.repository.root
    tree = anchor.repository.read_tree(code).tree
    result = cli(
        root,
        "bind",
        "16",
        "--implementation",
        "--session",
        "writer",
        "--attempt",
        "fixture-attempt",
        "--branch",
        "refs/heads/verification",
        "--branch-mode",
        "create",
        "--commit",
        code,
        "--tree",
        tree,
    )
    assert result["local"] == "completed", result["evidence"]
    binding = Binding.model_validate_json(result["evidence"][0])
    anchor = replace(anchor, repository=Repository(Path(binding.worktree), PLANNING))
    attempt = AttemptStarted(
        attempt=binding.attempt,
        generation=binding.generation,
        plan_generation=1,
        source=binding.source,
        binding=binding.identity,
        allowance_millis=3000,
    )
    clock = ClockChanged(
        attempt=attempt.attempt,
        generation=attempt.generation,
        cause_event_id="fixture-c32:open:16",
        **{"from": None, "to": "active"},
        observed_at=datetime.fromisoformat(STAMP),
        used_millis=0,
    )
    event = EventContext("fixture-c32", OWNER, STAMP, policy.source.digest)
    state = fold(raw.splitlines(keepends=True), core_reducers())
    entered = _append(
        event,
        state,
        raw,
        [
            ("core.attempt.started", attempt, "open"),
            ("core.attempt.clock.changed", clock, "clock"),
        ],
    )
    opened, clock_record = entered.records
    wire = loads(clock_record)
    wire["data"]["from"] = None
    advance_planning(event_path, raw + opened + b"\n" + dumps(wire).encode() + b"\n")
    return anchor, binding


def overrun_activity(request):
    producer = ProducerRef(
        id="fixture.engagement",
        version=1,
        measurement_contract="engaged-interval/v1",
        coverage_class="measured-engagement",
    )
    start = datetime.fromisoformat(STAMP)
    end = start + timedelta(seconds=4)
    return ingest_activity(
        producer,
        (
            ActivityObservation(
                source_id="c32-engaged",
                actor="fixture-agent",
                actor_kind="agent",
                session=request.session,
                attempt=request.attempt,
                generation=request.generation,
                binding=request.binding,
                observed_at=start,
                recorded_at=end,
                ended_at=end,
                evidence=("fixture-result",),
            ),
        ),
    ).records


def test_admit_stop_orders(topology, tmp_path, monkeypatch):
    anchor, binding = installed_attempt(topology)
    worktree = Path(binding.worktree)
    git(worktree, "switch", "-q", "verification")
    revision = commit_file(worktree, "candidate.txt", b"Exact candidate\n")
    candidate = anchor.repository.read_tree(revision)
    request = ExecutionRequest(
        story=16,
        attempt=binding.attempt,
        generation=binding.generation,
        binding=binding.identity,
        session=binding.session,
        request_id="verify-exact",
        action_key="managed-verification",
        executor="fixture-executor",
        candidate=ExecutionCandidate(
            source={"commit": candidate.revision, "tree": candidate.tree}
        ),
    )
    service = AdmissionService(anchor)
    authority = preflight_policy(anchor)
    assert authority.outcome == LocalOutcome.COMPLETED, authority.evidence
    assert authority.views.planning.observed_commit == anchor.repository.tip().revision
    assert authority.views.shared.valid_tip == anchor.repository.tip().revision, (
        authority.evidence
    )
    result = service.admit(request)
    assert result.command.local == LocalOutcome.COMPLETED, result.command.evidence
    assert result.command.publication == PublicationOutcome.VERIFIED
    admission = result.admission
    assert admission is not None and admission.request == request
    tip = anchor.repository.tip()
    attempt = read_graph(anchor.repository, tip).states[16].domains["attempts"]
    history = attempt.attempts[binding.attempt].executions[admission.execution_id]
    assert [entry.phase for entry in history] == ["prepared", "admitted"]
    assert history[-1].source == binding.source
    assert history[-1].candidate == request.candidate
    assert service.admit(request).admission == admission
    assert anchor.repository.tip() == tip

    launched = []

    def launch(selected):
        launched.append(selected.request_id)
        return lambda: ProcessOutcome(outcome="passed", proof="fixture-result")

    executor = Executor(request.executor, launch)
    first = dispatch(service, admission, executor)
    assert first.effective and first.observed.outcome == "passed", first
    assert not dispatch(service, admission, executor).effective
    assert launched == [request.request_id]

    before_cancel = request.model_copy(update={"request_id": "cancel-before-launch"})
    held = service.admit(before_cancel).admission
    assert held is not None
    assert cancel(service, held).state == "prevented"
    assert not dispatch(service, held, executor).effective
    assert launched == [request.request_id]

    lost = request.model_copy(update={"request_id": "lost-result"})
    issued = service.admit(lost).admission
    assert issued is not None

    def lose_result(selected):
        launched.append(selected.request_id)

        def wait():
            raise OSError("Result channel closed after launch")

        return wait

    uncertain = dispatch(service, issued, Executor(request.executor, lose_result))
    assert uncertain.observed.phase == "uncertain" and not uncertain.effective
    assert not dispatch(service, issued, executor).effective
    reconciled = observe_result(
        service, issued, ProcessOutcome("passed", "fixture-recovered-output")
    )
    assert reconciled.observed.phase == "finished" and not reconciled.effective
    assert launched == [request.request_id, lost.request_id]

    running = service.admit(
        request.model_copy(update={"request_id": "cancel-after-launch"})
    ).admission
    assert running is not None

    cancelled = cancel_during_launch(service, running, monkeypatch)
    assert cancelled.observed.outcome == "passed" and not cancelled.effective

    tip = anchor.repository.tip()
    commit_file(worktree, "candidate.txt", b"Superseded candidate\n")
    stale = request.model_copy(update={"request_id": "stale"})
    assert service.admit(stale).command.local == LocalOutcome.REFUSED
    assert anchor.repository.tip() == tip

    code = anchor.repository.read_tree(git(worktree, "rev-parse", "HEAD"))
    current = request.model_copy(
        update={
            "request_id": "overrun-after-result",
            "candidate": ExecutionCandidate(
                source={"commit": code.revision, "tree": code.tree}
            ),
        }
    )
    first_admission = service.admit(current).admission
    assert first_admission is not None
    also_admitted = service.admit(
        current.model_copy(update={"request_id": "admitted-before-stop"})
    ).admission
    assert also_admitted is not None
    other = cloned(topology, tmp_path).policy.installation
    other_root = other.repository.root
    git(other_root, "fetch", "-q", str(worktree), binding.branch)
    git(other_root, "switch", "-q", "-c", "verification", "FETCH_HEAD")
    mirror = binding.model_copy(
        update={
            "worktree": str(other_root),
            "git_directory": git(other_root, "rev-parse", "--absolute-git-dir"),
        }
    )
    mirror_workspace = Workspace(other)
    with mirror_workspace.lock():
        mirror_workspace.persist(mirror)
    stale_worker = AdmissionService(other)
    assert stale_worker.admit(also_admitted.request).admission == also_admitted
    stale_tip = other.repository.tip()
    passed_late = Executor(
        current.executor,
        lambda request: (
            lambda: ProcessOutcome(
                "passed", "fixture-overrun", overrun_activity(request)
            )
        ),
    )
    losing = current.model_copy(update={"request_id": "losing-admission"})
    push = Publisher._push
    stop_results = []

    def stop_before_shared_push(publisher, candidate, expected):
        if publisher.repository == other.repository and not stop_results:
            staged = other.repository.read_tree(candidate)
            staged_attempt = (
                read_graph(other.repository, staged)
                .states[16]
                .domains["attempts"]
                .attempts[current.attempt]
            )
            assert (
                staged_attempt.executions[losing.execution_id][-1].phase == "admitted"
            )
            stop_results.append(dispatch(service, first_admission, passed_late))
        return push(publisher, candidate, expected)

    with monkeypatch.context() as patch:
        patch.setattr(Publisher, "_push", stop_before_shared_push)
        lost_admission = stale_worker.admit(losing)
    assert lost_admission.admission is None
    assert lost_admission.command.publication == PublicationOutcome.PENDING
    (stopped,) = stop_results
    assert not stopped.effective and stopped.observed.outcome == "passed", stopped
    tip = anchor.repository.tip()
    latest = read_graph(anchor.repository, tip).states[16]
    attempt = latest.domains["attempts"].attempts[current.attempt]
    assert attempt.closed and attempt.clock_mode == "terminal-closed"
    assert losing.execution_id not in attempt.executions
    assert (
        attempt.executions[also_admitted.execution_id][-1].phase == "cancel-requested"
    )
    retained = latest.domains["evidence"].facts["core.activity.recorded"][0].payload
    assert retained.provenance.binding == current.binding
    assert retained.provenance.generation == current.generation
    assert retained.provenance.source_id == "c32-engaged"
    assert (
        service.admit(current.model_copy(update={"request_id": "stop-first"})).admission
        is None
    )
    assert not dispatch(service, also_admitted, executor).effective
    assert launched == [request.request_id, lost.request_id]
    assert anchor.repository.tip() == tip

    rejected_tip = other.repository.tip()
    assert rejected_tip != stale_tip and rejected_tip != tip
    remote = git(other_root, "remote", "get-url", PLANNING_REMOTE)
    git(other_root, "remote", "set-url", PLANNING_REMOTE, str(tmp_path / "offline"))
    offline = dispatch(stale_worker, also_admitted, executor)
    assert offline.command.local == LocalOutcome.UNAVAILABLE and not offline.effective
    assert other.repository.tip() == rejected_tip
    assert (
        git(topology.planning, "ls-remote", "origin", PLANNING).split()[0]
        == tip.revision
    )
    git(other_root, "remote", "set-url", PLANNING_REMOTE, remote)
    assert not dispatch(stale_worker, also_admitted, executor).effective
    assert other.repository.read_tree(tip.revision).tree == tip.tree
    assert launched == [request.request_id, lost.request_id]

    check_local_only_admission(tmp_path, executor)


def cancel_during_launch(service, admission, monkeypatch):
    entered_launch = Event()
    attempted_lock = Event()
    acquired_lock = Event()
    finished_cancel = Event()
    cancellation = []
    lock = Workspace.lock

    @contextmanager
    def instrument(workspace):
        cancelling = entered_launch.is_set() and not attempted_lock.is_set()
        if cancelling:
            attempted_lock.set()
        with lock(workspace):
            if cancelling:
                acquired_lock.set()
            yield

    def launch(_request):
        entered_launch.set()
        assert attempted_lock.wait(15)
        assert not acquired_lock.wait(0.15)

        def wait():
            assert finished_cancel.wait(30)
            return ProcessOutcome("passed", "cancel-race-result")

        return wait

    def revoke():
        cancellation.append(cancel(service, admission))
        finished_cancel.set()

    with monkeypatch.context() as patch, ThreadPoolExecutor(max_workers=2) as pool:
        patch.setattr(Workspace, "lock", instrument)
        observing = pool.submit(
            dispatch, service, admission, Executor(admission.request.executor, launch)
        )
        assert entered_launch.wait(30)
        pool.submit(revoke).result(timeout=45)
        result = observing.result(timeout=45)

    assert acquired_lock.is_set()
    assert [result.state for result in cancellation] == ["pending"]
    return result


def check_local_only_admission(tmp_path, executor):
    root = tmp_path / "local-only"
    root.mkdir()
    git(root, "init", "-q", "-b", "trunk")
    identify(root)
    genesis = empty_planning_root(root)
    git(root, "update-ref", PLANNING, genesis)
    commit_file(root, ".aitm.toml", settings_at(genesis).encode())
    code = commit_file(root, WORKFLOW, PROFILE)
    repo = Repository(root, PLANNING)
    local = installation(repo, genesis)

    def advance(path, value):
        current = repo.tip()
        result = repo.create_commit(current, {path: value}, "seed local attempt")
        git(root, "update-ref", PLANNING, result.revision, current.revision)

    anchor, binding = bind_attempt(local, code, advance)
    git(root, "switch", "-q", "verification")
    service = AdmissionService(anchor)
    request = ExecutionRequest(
        story=16,
        attempt=binding.attempt,
        generation=binding.generation,
        binding=binding.identity,
        session=binding.session,
        request_id="local-only",
        action_key="managed-verification",
        executor=executor.identity,
        candidate=ExecutionCandidate(source=binding.source),
    )
    issued = service.admit(request)
    assert issued.command.publication == PublicationOutcome.NOT_APPLICABLE
    assert issued.admission is not None, issued.command.evidence
    assert dispatch(service, issued.admission, executor).effective

    captured = request.model_copy(
        update={
            "request_id": "captured",
            "candidate": request.candidate.model_copy(
                update={"capture_manifest": "b" * 64}
            ),
        }
    )
    assert service.admit(captured).command.local == LocalOutcome.REFUSED
    manifest = captured.candidate.capture_manifest
    qualified = replace(
        service,
        verify_capture=lambda selected: selected.candidate.capture_manifest == manifest,
    )
    admission = qualified.admit(captured).admission
    assert admission is not None
    manifest = "c" * 64
    stale = dispatch(qualified, admission, executor)
    assert stale.command.local == LocalOutcome.REFUSED and not stale.effective

    failed = service.admit(
        request.model_copy(update={"request_id": "failed-overrun"})
    ).admission
    assert failed is not None

    def fail_after_source_moves(request):
        def wait():
            commit_file(root, "candidate.txt", b"New candidate after process start\n")
            return ProcessOutcome(
                "failed", "fixture-stale-failure", overrun_activity(request)
            )

        return wait

    late_failure = dispatch(
        service, failed, Executor(request.executor, fail_after_source_moves)
    )
    assert late_failure.observed.outcome == "failed" and not late_failure.effective
    latest = read_graph(repo, repo.tip()).states[16]
    assert latest.domains["attempts"].attempts[request.attempt].closed
    assert (
        latest.domains["evidence"].facts["core.trip.recorded"][-1].payload.cause
        == "time-limit"
    )
