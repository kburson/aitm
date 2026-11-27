"""Pin graduated story, relationship and accepted-plan replay invariants."""

import pytest

from aitm_core.reducers.lifecycle import LifecycleIntegrityError
from tests.unit.test_c54 import (
    COMMIT,
    DIGEST,
    GRADUATION,
    INITIAL,
    REFINE,
    acceptance,
    estimate,
    move,
    replay,
)


def test_lifecycle_facts_cannot_establish_story_identity_without_graduation():
    with pytest.raises(LifecycleIntegrityError, match="recorded graduation"):
        replay(estimate("refine", 2))


def test_second_graduation_cannot_replace_story_origin():
    kind, data = GRADUATION
    other_origin = kind, {**data, "source_id": "another-plan-entry"}
    with pytest.raises(
        LifecycleIntegrityError, match="invalid recorded story graduation"
    ):
        replay(GRADUATION, other_origin)


def test_graduation_cannot_start_in_a_terminal_state():
    kind, data = GRADUATION
    terminal = kind, {**data, "initial_state": {**INITIAL, "terminal": True}}
    with pytest.raises(
        LifecycleIntegrityError, match="invalid recorded story graduation"
    ):
        replay(terminal)


@pytest.mark.parametrize(
    "relationships",
    [
        pytest.param({"parent": 6}, id="own-parent"),
        pytest.param({"children": [6]}, id="own-child"),
        pytest.param({"blocking": [6]}, id="blocks-itself"),
    ],
)
def test_relationships_refuse_self_edges_in_each_role(relationships):
    change = "core.link.changed", {"before": {"parent": 470}, "after": relationships}
    with pytest.raises(LifecycleIntegrityError, match="self-relationship"):
        replay(GRADUATION, change)


@pytest.mark.parametrize(
    "relationships",
    [
        pytest.param({"parent": 5, "children": [5]}, id="parent-is-child"),
        pytest.param({"blocking": [4], "blocked_by": [4]}, id="opposite-dependency"),
    ],
)
def test_relationships_do_not_accept_incompatible_local_edges(relationships):
    change = "core.link.changed", {"before": {"parent": 470}, "after": relationships}
    with pytest.raises(LifecycleIntegrityError, match="contradictory local"):
        replay(GRADUATION, change)


def test_recorded_edge_cannot_switch_to_another_workflow():
    target = {**REFINE, "workflow_id": "unrelated-workflow"}
    with pytest.raises(LifecycleIntegrityError, match="edge disagrees"):
        replay(GRADUATION, move(target=target))


def test_reopen_edge_is_refused_from_an_active_state():
    event, data = move()
    edge = {**data["edge"], "kind": "reopen"}
    with pytest.raises(LifecycleIntegrityError, match="invalid recorded reopen"):
        replay(GRADUATION, (event, {**data, "edge": edge}))


@pytest.mark.parametrize(
    "disposition, replacement",
    [
        pytest.param("superseded", None, id="superseded-without-replacement"),
        pytest.param("delivered", 8, id="ordinary-completion-with-replacement"),
    ],
)
def test_terminal_replacement_must_agree_with_disposition(disposition, replacement):
    event, data = move(
        target={**REFINE, "terminal": True},
        disposition=disposition,
        replacement_story=replacement,
    )
    edge = {**data["edge"], "kind": "terminal"}
    with pytest.raises(LifecycleIntegrityError, match="replacement presence"):
        replay(GRADUATION, (event, {**data, "edge": edge}))


def test_jit_without_an_accepted_plan_cannot_certify_source():
    jit = (
        "core.jit.recorded",
        {
            "plan_digest": DIGEST,
            "plan_generation": 1,
            "code_baseline": COMMIT,
            "attempt": "a1",
            "coverage_paths": ["src/core.py"],
            "coverage_status": "complete",
            "outcome": "accepted",
            "reviewed_revisions": [COMMIT],
        },
    )
    with pytest.raises(LifecycleIntegrityError, match="current accepted plan"):
        replay(GRADUATION, acceptance("design", DIGEST), jit)
