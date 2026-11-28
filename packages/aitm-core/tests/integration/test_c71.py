"""The installed split reads authored scope and publishes one real Git CAS batch."""

from hashlib import sha256
from json import dumps, loads
from pathlib import Path

from aitm_core.description import description_path
from aitm_core.events import core_reducers, fold
from aitm_core.services import preflight_policy
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

REFINE = b'[[states]]\nid = "refine"\nlabel = "Shape the work"\n\n'


def test_installed_split_publishes_scope_and_invalidations_in_one_commit(topology):
    installation = topology.policy.installation
    profile = PROFILE.replace(
        b'[[states]]\nid = "plan"', REFINE + b'[[states]]\nid = "plan"'
    )
    profile = profile.replace(b'label = "Design"', b'label = "Aggregate Design"')
    commit_file(topology.code, WORKFLOW, profile)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    genesis = loads(graduated())
    genesis["data"]["initial_state"] = {
        "workflow_id": "project",
        "revision": sha256(profile).hexdigest(),
        "state_id": "refine",
        "label": "Shape the work",
    }
    raw = dumps(genesis).encode() + b"\n"
    facts = (
        (
            "core.description.set",
            {
                "title": "Preserve permanent identity",
                "as": "operator",
                "want": "a bound scope",
                "so_that": "delivery can be split",
                "scope": "Original",
                "content_hash": "d" * 64,
            },
        ),
        (
            "core.estimate.set",
            {
                "phase": "refine",
                "agent_hours": 6.0,
                "size": "M",
                "priority": "P1",
            },
        ),
    )
    for sequence, (kind, fact) in enumerate(facts, 2):
        event = genesis | {
            "id": f"seed-{sequence}",
            "type": kind,
            "operation_id": f"seed-{sequence}",
            "sequence": sequence,
            "prior_log_digest": sha256(raw).hexdigest(),
            "data": fact,
        }
        raw += dumps(event).encode() + b"\n"
    topology.advance_planning(EVENTS, raw)
    admission = preflight_policy(installation)
    assert admission.policy is not None, admission.reason
    _record_installation(installation, admission.policy.revision)
    local = topology.local
    bound = cli(local, "bind", "16", "--session", "splitter")
    assert bound["local"] == "completed", bound
    lease = loads(bound["evidence"][0])
    scope = local / "proposed-aggregate-scope.md"
    scope.write_text("Deliver the two scoped outcomes.\n")
    repository = Repository(local, PLANNING)
    before = repository.tip()
    trunk = git(local, "rev-parse", DEFAULT)
    reply = cli(
        local,
        "split",
        "16",
        "--binding",
        lease["identity"],
        "--generation",
        str(lease["generation"]),
        "--session",
        "splitter",
        "--reason",
        "Oversized",
        "--scope-file",
        str(scope),
    )
    assert reply["local"] == "completed" and reply["publication"] == "verified", reply
    after = repository.tip()
    assert repository.parent(after) == before.revision
    updated = repository.read_blobs(after.tree, (EVENTS, description_path(16)))
    assert scope.read_bytes() in updated[description_path(16)]
    story = fold(updated[EVENTS].splitlines(keepends=True), core_reducers()).domains[
        "lifecycle"
    ]
    assert story.story_id == 16 and story.kind == "epic"
    assert (
        story.workflow_state.state_id == "design"
        and story.workflow_state.label == "Aggregate Design"
    )
    assert story.split.invalidated_estimates == ("refine",)
    assert not story.estimates and story.description.scope == scope.read_text()
    assert git(local, "rev-parse", DEFAULT) == trunk
    remote = Path(git(local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == after.revision
