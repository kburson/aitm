"""Qualify installed execution admission against the authoritative Git ref."""

from dataclasses import replace
from datetime import datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

from aitm_core.events import core_reducers, fold
from aitm_core.execution.admission import AdmissionService, ExecutionRequest
from aitm_core.models.attempts import AttemptStarted, ClockChanged, ExecutionCandidate
from aitm_core.models.binding import Binding
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.operations import story_event_path
from aitm_core.relationships import EventContext, read_graph
from aitm_core.rules.trips import _append
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.objects import Repository
from tests.integration.test_c08 import DEFAULT, PLANNING, WORKFLOW, commit_file, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.integration.test_c22 import OWNER, STAMP
from tests.integration.test_c28 import PROFILE
from tests.unit.test_c15 import graduated


def installed_attempt(topology):
    anchor = topology.policy.installation
    code = commit_file(topology.code, WORKFLOW, PROFILE)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    initial = loads(graduated())
    initial["data"]["initial_state"] = {
        "workflow_id": "project",
        "revision": sha256(PROFILE).hexdigest(),
        "state_id": "dev",
        "label": "Implement",
    }
    raw = dumps(initial).encode() + b"\n"
    event_path = story_event_path(16)
    topology.advance_planning(event_path, raw)
    policy = preflight_policy(anchor).policy
    assert policy is not None
    _record_installation(anchor, policy.revision)
    tree = git(topology.code, "rev-parse", f"{code}^{{tree}}")
    result = cli(
        topology.local,
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
    topology.advance_planning(
        event_path, raw + opened + b"\n" + dumps(wire).encode() + b"\n"
    )
    return anchor, binding


def test_admit_stop_orders(topology):
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

    commit_file(worktree, "candidate.txt", b"Superseded candidate\n")
    stale = request.model_copy(update={"request_id": "stale"})
    assert service.admit(stale).command.local == LocalOutcome.REFUSED
    assert anchor.repository.tip() == tip
