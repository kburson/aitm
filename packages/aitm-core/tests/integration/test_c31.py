"""Prove a qualifying trip stops the installed authored-sync pipeline."""

from datetime import datetime, timedelta
from hashlib import sha256
from json import dumps, loads

from aitm_core.activity import ActivityObservation, ingest_activity
from aitm_core.cli.lifecycle import handle
from aitm_core.cli.trips import handle as attempt_control
from aitm_core.ext.api import ProducerRef
from aitm_core.models.attempts import ExecutionRecorded, SourceSnapshot
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import LocalOutcome
from aitm_core.models.operations import story_event_path
from aitm_core.relationships import EventContext, read_graph
from aitm_core.rules.trips import _append
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import DEFAULT, PLANNING, WORKFLOW, commit_file, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.integration.test_c22 import OWNER, STAMP, with_attempt
from tests.integration.test_c28 import PLAN, PROFILE
from tests.unit.test_c15 import graduated


def test_trip_precedence(topology, monkeypatch):
    installation = topology.policy.installation
    repository = installation.repository
    commit_file(topology.code, WORKFLOW, PROFILE)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    event_path = story_event_path(16)
    initial = loads(graduated())
    initial["data"]["initial_state"] = {
        "workflow_id": "project",
        "revision": sha256(PROFILE).hexdigest(),
        "state_id": "dev",
        "label": "Develop",
    }
    topology.advance_planning(
        event_path, with_attempt(dumps(initial).encode() + b"\n", 16)
    )
    topology.advance_planning(PLAN, b"Shared plan\n")
    observed = preflight_policy(installation)
    assert observed.policy is not None
    before_admission = repository.tip()
    graph = read_graph(repository, before_admission)
    execution = ExecutionRecorded(
        attempt="fixture-attempt",
        generation=1,
        execution_id="fixture-execution",
        request_id="fixture-request",
        action_key="managed-verification",
        executor="fixture",
        authority_store=before_admission.store,
        authority_ref=repository.ref,
        expected_prior_version=before_admission.revision,
        source=SourceSnapshot(commit="b" * 40, tree="c" * 40),
        phase="prepared",
    )
    context = EventContext(
        "fixture-admission", OWNER, STAMP, observed.policy.source.digest
    )
    updated = _append(
        context,
        graph.states[16],
        graph.logs[event_path],
        [
            ("core.execution.recorded", execution, "prepared"),
            (
                "core.execution.recorded",
                execution.model_copy(
                    update={"phase": "admitted", "proof": "fixture-authority"},
                ),
                "admitted",
            ),
        ],
    )
    admission = topology.advance_planning(
        event_path, graph.logs[event_path] + b"\n".join(updated.records) + b"\n"
    )
    _record_installation(installation, observed.policy.revision)
    bound = cli(topology.local, "bind", "16", "--session", "writer", "--path", PLAN)
    assert bound["local"] == "completed", bound
    lease = loads(bound["evidence"][0])
    workspace = Workspace(installation)
    with workspace.lock():
        authority = workspace.lookup(StoryRef(story=16))
        assert authority.identity == lease["identity"]
        workspace.persist(authority.model_copy(update={"identity": "fixture-binding"}))
    lease["identity"] = "fixture-binding"
    local_plan = topology.local / PLAN
    local_plan.write_bytes(b"Unpublished authored bytes\n")
    monkeypatch.chdir(topology.local)
    observed_at = datetime.fromisoformat(STAMP)
    ended = observed_at + timedelta(seconds=4)
    producer = ProducerRef(
        id="fixture.engagement",
        version=1,
        measurement_contract="engaged-interval/v1",
        coverage_class="measured-engagement",
    )
    activity = ingest_activity(
        producer,
        (
            ActivityObservation(
                source_id="fixture-interval",
                actor="fixture-agent",
                actor_kind="agent",
                session="writer",
                attempt="fixture-attempt",
                generation=1,
                binding="fixture-binding",
                observed_at=observed_at,
                recorded_at=ended,
                ended_at=ended,
                evidence=("fixture-proof",),
            ),
        ),
    ).records
    result = handle(
        ("promote",),
        (
            "16",
            "--binding",
            lease["identity"],
            "--generation",
            str(lease["generation"]),
            "--session",
            "writer",
        ),
        ports=ServicePorts(activity_observations=lambda _context: activity),
    )
    assert result.local == LocalOutcome.REFUSED, result
    graph = read_graph(repository, repository.tip())
    evidence = graph.states[16].domains["evidence"]
    assert evidence.facts["core.trip.recorded"][-1].payload.cause == "time-limit"
    attempt = graph.states[16].domains["attempts"].attempts["fixture-attempt"]
    assert attempt.closed and attempt.clock_mode == "terminal-closed"
    cancelled = attempt.executions["fixture-execution"][-1]
    assert (cancelled.phase, cancelled.admission_commit) == (
        "cancel-requested",
        admission,
    )
    assert cancelled.outcome is None
    assert graph.stories[16].workflow_state.state_id == "plan"
    assert (
        repository.read_blobs(repository.tip().tree, (PLAN,))[PLAN] == b"Shared plan\n"
    )
    assert local_plan.read_bytes() == b"Unpublished authored bytes\n"

    stopped = repository.tip()
    returned = handle(
        ("promote",),
        (
            "16",
            "--binding",
            lease["identity"],
            "--generation",
            str(lease["generation"]),
            "--session",
            "writer",
        ),
        ports=ServicePorts(activity_observations=lambda _context: activity),
    )
    assert returned.local != LocalOutcome.COMPLETED
    assert repository.tip() == stopped

    analysis = ".aitm/stories/000/16/plan/trip-fixture.md"
    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    topology.advance_planning(
        analysis, b"# Trip analysis\n\nA smaller replacement plan.\n"
    )
    recorded = attempt_control(
        ("trip", "decide"),
        (
            "16",
            "--decision",
            "refactor",
            "--analysis",
            analysis,
            "--rationale",
            "Carry the verified work",
            "--binding",
            lease["identity"],
            "--generation",
            str(lease["generation"]),
            "--session",
            "writer",
        ),
    )
    assert recorded.local == LocalOutcome.COMPLETED, recorded
    latest = read_graph(repository, repository.tip()).states[16]
    assert (
        latest.domains["evidence"].facts["core.trip.decided"][-1].payload.decision
        == "refactor"
    )
    assert latest.domains["attempts"].attempts["fixture-attempt"].closed
    assert local_plan.read_bytes() == b"Unpublished authored bytes\n"
