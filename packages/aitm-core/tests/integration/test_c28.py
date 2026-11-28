"""The installed C28 route fences, syncs and publishes through real Git."""

from hashlib import sha256
from json import dumps, loads
from pathlib import Path

from aitm_core.cli.lifecycle import handle
from aitm_core.events import core_reducers, fold
from aitm_core.models.operations import (
    AuthorityOrigin,
    PreflightOutcome,
    PreflightResult,
)
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.objects import Repository
from tests.integration.test_c08 import (
    DEFAULT,
    PLANNING,
    PLANNING_REMOTE,
    WORKFLOW,
    commit_file,
    configured_settings,
    git,
)
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.unit.test_c15 import EVENTS, graduated

PLAN = ".aitm/stories/000/16/plan/current.md"
PROFILE = b"""schema = "aitm.workflow/v1"
id = "project"
contract = "core.hosted-delivery/v1"

[lifecycle]
terminal = "closed"
non_delivery = "closed"
reopen_design = "design"
reopen_plan = "plan"

[recovery]
design_rework = "design"
implementation_rework = "dev"
trip = "plan"
scope_pivot = "plan"

[[states]]
id = "design"
label = "Design"

[[states]]
id = "plan"
label = "Prepare work"
onExit = ["core.plan.pickup-basis-current"]

[[states]]
id = "dev"
label = "Implement"
onEnter = ["core.dev.binding-ready"]

[[states]]
id = "review"
label = "Check"
onEnter = ["core.dev.review-candidate-current"]
onExit = ["core.closeout.complete"]

[[states]]
id = "closed"
label = "Close"
onEnter = ["core.closeout.terminal-disposition-valid"]

[[edges]]
from = "plan"
to = "dev"
operation = "core.attempt.begin-or-resume"

[[edges]]
from = "review"
to = "closed"
operation = "core.story.finalize-delivery"
"""


def test_installed_transition_fences_started_attempts_and_keeps_authored_sync_on_refusal(
    topology, monkeypatch
):
    installation = topology.policy.installation
    commit_file(topology.code, WORKFLOW, PROFILE)
    settings = configured_settings(topology.genesis).replace(
        'mode = "enforce"', 'mode = "advisory"'
    )
    commit_file(topology.code, ".aitm.toml", settings.encode())
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    initial = loads(graduated())
    initial["data"]["initial_state"] = {
        "workflow_id": "project",
        "revision": sha256(PROFILE).hexdigest(),
        "state_id": "plan",
        "label": "Prepare work",
    }
    topology.advance_planning(EVENTS, dumps(initial).encode() + b"\n")
    topology.advance_planning(PLAN, b"Shared plan\n")
    admission = preflight_policy(installation)
    assert admission.policy is not None, admission.reason
    _record_installation(installation, admission.policy.revision)
    local = topology.local
    bound = cli(local, "bind", "16", "--session", "writer", "--path", PLAN)
    assert bound["local"] == "completed", bound
    lease = loads(bound["evidence"][0])
    options = (
        "16",
        "--binding",
        lease["identity"],
        "--generation",
        str(lease["generation"]),
        "--session",
        "writer",
    )
    workspace_plan = local / PLAN
    workspace_plan.write_bytes(b"First authored edit\n")
    first = cli(local, "promote", *options)
    assert first["local"] == "completed", first
    assert any(
        "Completed transition prerequisite operation" in line
        for line in first["evidence"]
    )
    repository = Repository(local, PLANNING)
    recorded = repository.read_blobs(repository.tip().tree, (EVENTS, PLAN))
    assert recorded[PLAN] == b"First authored edit\n"
    state = fold(recorded[EVENTS].splitlines(keepends=True), core_reducers())
    assert state.domains["lifecycle"].workflow_state.state_id == "dev"
    attempts = state.domains["attempts"]
    started = attempts.attempts[attempts.current_attempt]
    assert started.started.provisional and len(started.clocks) == 1

    workspace_plan.write_bytes(b"Second authored edit\n")
    before = repository.tip().revision
    unavailable = cli(local, "promote", *options)
    assert unavailable["local"] == "unavailable", unavailable
    assert unavailable["evidence"] == ["attempt-preflight-unavailable"]
    assert repository.tip().revision == before

    calls = []

    def attempt_preflight(context):
        calls.append((context.operation.intent.kind, context.snapshot.revision))
        return PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.FIXTURE
        )

    monkeypatch.chdir(local)
    illegal = handle(
        ("promote",),
        (*options, "--target", "closed"),
        ports=ServicePorts(attempt_preflight=attempt_preflight),
    )
    assert illegal.local == "refused", illegal
    assert calls == [("state.transition", before), ("workspace-sync", before)]
    after = repository.read_blobs(repository.tip().tree, (EVENTS, PLAN))
    assert after[PLAN] == b"Second authored edit\n"
    assert after[EVENTS] == recorded[EVENTS]
    remote = Path(git(local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == repository.tip().revision

    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    shared = topology.advance_planning(PLAN, b"Competing shared edit\n")
    workspace_plan.write_bytes(b"Unpublished competing local edit\n")
    guard_calls = []
    blocked = handle(
        ("promote",),
        (*options, "--target", "review"),
        ports=ServicePorts(
            attempt_preflight=attempt_preflight,
            story_exit_guards=guard_calls.append,
        ),
    )
    assert blocked.local == "conflict", blocked.evidence
    assert not guard_calls
    assert workspace_plan.read_bytes() == b"Unpublished competing local edit\n"
    assert git(remote, "rev-parse", PLANNING) == shared
    assert git(remote, "show", f"{shared}:{PLAN}") == "Competing shared edit"
    assert (
        repository.read_blobs(repository.tip().tree, (EVENTS,))[EVENTS]
        == recorded[EVENTS]
    )
