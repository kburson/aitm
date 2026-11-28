"""Installed production kind selection and terminal disposition on a real Git store."""

from hashlib import sha256
from json import dumps, loads
from pathlib import Path

from aitm_core.cli.lifecycle import handle
from aitm_core.documents import canonicalize
from aitm_core.events import core_reducers, fold
from aitm_core.machine.guards import GuardDecision
from aitm_core.models.decomposition import PlanEntry
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.operations import story_event_path
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.objects import Repository
from tests.integration.test_c08 import (
    DEFAULT,
    PLANNING,
    PLANNING_REMOTE,
    WORKFLOW,
    commit_file,
    git,
)
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c16 import cli
from tests.integration.test_c28 import PROFILE
from tests.unit.test_c15 import EVENTS, graduated
from tests.unit.test_c72 import FIRST

PLAN = ".aitm/stories/000/16/plan/current.md"
DESIGN = ".aitm/stories/000/16/design/current.md"


def append(raw, name, facts):
    initial = loads(raw.splitlines()[0])
    sequence = len(raw.splitlines()) + 1
    row = initial | {
        "id": f"proof-{sequence}",
        "ts": initial["ts"],
        "type": name,
        "operation_id": f"proof-{sequence}",
        "sequence": sequence,
        "prior_log_digest": sha256(raw).hexdigest(),
        "data": facts,
    }
    return raw + dumps(row).encode() + b"\n"


def test_installed_epic_uses_accepted_scope_and_explicit_nondelivery(
    topology, monkeypatch
):
    installation = topology.policy.installation
    commit_file(topology.code, WORKFLOW, PROFILE)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    observed = preflight_policy(installation)
    assert observed.policy is not None, observed.reason
    policy = observed.policy.source.digest
    plan = (
        b"---\n"
        + dumps(
            {
                "schema": "aitm.doc/v1",
                "story": 16,
                "role": "plan",
                "decomposition": {"first": FIRST},
            }
        ).encode()
        + b"\n---\nAccepted project plan.\n"
    )
    plan_identity = canonicalize(plan, DocumentSchema())
    parent = loads(graduated())
    parent["data"].update(
        kind="epic",
        initial_state={
            "workflow_id": "project",
            "revision": sha256(PROFILE).hexdigest(),
            "state_id": "plan",
            "label": "Prepare work",
        },
    )
    parent_stream = append(
        dumps(parent).encode() + b"\n",
        "core.doc.accepted",
        {
            "role": "plan",
            "path": PLAN,
            "canonical_version": "aitm.authored-content/v1",
            "canonical_digest": plan_identity.canonical_sha256,
            "raw_digest": plan_identity.raw_sha256,
            "review_refs": ["accepted"],
            "levels": ["xpr"],
            "policy_digest": policy,
            "source_planning_sha": "a" * 40,
            "plan_generation": 1,
        },
    )
    design = b'---\n{"schema":"aitm.doc/v1","story":16,"role":"design"}\n---\nAccepted design.\n'
    design_identity = canonicalize(design, DocumentSchema())
    parent_stream = append(
        parent_stream,
        "core.doc.accepted",
        {
            "role": "design",
            "path": DESIGN,
            "canonical_version": "aitm.authored-content/v1",
            "canonical_digest": design_identity.canonical_sha256,
            "raw_digest": design_identity.raw_sha256,
            "review_refs": ["accepted"],
            "levels": ["xpr"],
            "policy_digest": policy,
            "source_planning_sha": "a" * 40,
            "plan_generation": 1,
        },
    )
    empty = {"parent": None, "children": [], "blocked_by": [], "blocking": []}
    parent_stream = append(
        parent_stream,
        "core.link.changed",
        {
            "before": empty,
            "after": empty | {"children": [17]},
        },
    )
    child = loads(graduated())
    child["story"] = 17
    child["data"].update(
        source_kind="plan-entry",
        source_id="16:first",
        source_digest=PlanEntry.model_validate_json(dumps(FIRST)).digest,
        issue="local-17",
        parent=16,
        initial_state=parent["data"]["initial_state"]
        | {"state_id": "design", "label": "Design"},
    )
    child_path = story_event_path(17)
    child_raw = dumps(child).encode() + b"\n"
    topology.advance_planning(child_path, child_raw)
    topology.advance_planning(EVENTS, parent_stream)
    topology.advance_planning(PLAN, plan)
    topology.advance_planning(DESIGN, design)
    prepared = preflight_policy(installation)
    assert (
        prepared.policy is not None
        and prepared.policy.revision == observed.policy.revision
    )
    _record_installation(installation, prepared.policy.revision)
    local = topology.local

    bound = cli(local, "bind", "16", "--session", "epic-owner", "--path", PLAN)
    assert bound["local"] == "completed", bound["evidence"]
    lease = loads(bound["evidence"][0])
    options = (
        "16",
        "--binding",
        lease["identity"],
        "--generation",
        str(lease["generation"]),
        "--session",
        "epic-owner",
    )
    pickup = cli(local, "promote", *options)
    assert pickup["local"] == "completed" and pickup["publication"] == "verified", (
        pickup
    )
    repository = Repository(local, PLANNING)

    def replay():
        current = repository.read_blobs(repository.tip().tree, (EVENTS,))[EVENTS]
        return fold(current.splitlines(keepends=True), core_reducers())

    active = replay()
    assert active.domains["lifecycle"].workflow_state.state_id == "dev"
    assert "attempts" not in active.domains
    missing_port = cli(local, "promote", *options)
    assert missing_port["local"] == "refused", missing_port
    assert replay().domains["lifecycle"].workflow_state.state_id == "dev"
    calls = []

    def aggregate(call):
        calls.append(call)
        return GuardDecision("pass", "aggregate-fixture-current")

    monkeypatch.chdir(local)
    review = handle(
        ("promote",), options, ports=ServicePorts(aggregate_evidence=aggregate)
    )
    assert review.local == "completed", review
    assert calls and calls[-1].identifier == "core.dev.review-candidate-current"
    assert replay().domains["lifecycle"].workflow_state.state_id == "review"
    disposed = cli(
        local,
        "duplicate",
        *options,
        "--reason",
        "Duplicate scope",
        "--replacement",
        "17",
    )
    assert disposed["local"] == "completed" and disposed["publication"] == "verified", (
        disposed
    )
    last = replay().domains["lifecycle"].transitions[-1]
    assert last.to_state.terminal and last.to_state.state_id == "closed"
    assert last.disposition == "duplicate" and last.replacement_story == 17
    assert (
        repository.read_blobs(repository.tip().tree, (child_path,))[child_path]
        == child_raw
    )
    remote = Path(git(local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == repository.tip().revision
