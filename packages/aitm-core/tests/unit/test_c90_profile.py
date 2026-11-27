"""C90 pure tests over workflow bytes supplied by the pinned policy port."""

from types import SimpleNamespace

import pytest

from aitm_core.config import CommittedFile
from aitm_core.machine.profile import ProfileUnavailable, load_profile

PATH = ".aitm/workflows/ordered.toml"
WORKFLOW = """schema = "aitm.workflow/v1"
id = "delivery"
contract = "core.hosted-delivery/v1"

[lifecycle]
terminal = "complete"
non_delivery = "complete"
reopen_design = "plan"
reopen_plan = "plan"

[recovery]
design_rework = "plan"
implementation_rework = "build"
trip = "plan"
scope_pivot = "plan"

[[states]]
id = "plan"
label = "Ready to implement"
onEnter = ["core.design.current", "core.scope.accepted"]
action = ["core.directive.plan"]
onExit = ["core.plan.current"]

[[states]]
id = "build"
label = "Develop"

[[states]]
id = "review"
label = "Review and verify"

[[states]]
id = "complete"
label = "Done"

[[states]]
id = "archive"
label = "Retained for local policy"

[[edges]]
from = "plan"
to = "build"
prepare = ["core.dev.prepare-binding"]
guards = ["core.dev.ready"]
operation = "core.attempt.begin-or-resume"

[[edges]]
from = "review"
to = "build"
kind = "rework"
operation = "core.attempt.resume-for-rework"

[[edges]]
from = "complete"
to = "plan"
kind = "reopen"
operation = "core.story.reopen"
"""


def snapshot(document=WORKFLOW, configured=PATH):
    raw = document.encode() if isinstance(document, str) else document
    return SimpleNamespace(
        revision="a" * 40,
        tree="b" * 40,
        workflow=CommittedFile(PATH, raw),
        config=SimpleNamespace(workflow=SimpleNamespace(file=configured)),
    )


def test_ordered_rules_and_provenance_are_from_one_pinned_document():
    policy = snapshot()
    profile = load_profile(policy)
    assert profile.id == "delivery"
    assert profile.contract == "core.hosted-delivery/v1"
    assert profile.source.path == PATH
    assert profile.source.revision == policy.revision
    assert profile.source.tree == policy.tree
    assert profile.source.digest == policy.workflow.digest
    assert [state.id for state in profile.states] == [
        "plan",
        "build",
        "review",
        "complete",
        "archive",
    ]
    assert profile.states[0].label == "Ready to implement"
    assert profile.states[0].on_enter == ("core.design.current", "core.scope.accepted")
    assert profile.states[0].action == ("core.directive.plan",)
    assert profile.states[0].on_exit == ("core.plan.current",)
    assert profile.lifecycle.terminal == "complete"
    assert profile.recovery.trip == "plan"


def test_ordinary_graph_overlays_declared_behavior_and_stops_at_terminal():
    profile = load_profile(snapshot())
    assert [(edge.source, edge.target) for edge in profile.ordinary_edges] == [
        ("plan", "build"),
        ("build", "review"),
        ("review", "complete"),
    ]
    first = profile.ordinary_edges[0]
    assert first.operation == "core.attempt.begin-or-resume"
    assert first.prepare == ("core.dev.prepare-binding",)
    assert first.guards == ("core.dev.ready",)
    assert [(edge.source, edge.target, edge.kind) for edge in profile.transitions][
        -2:
    ] == [
        ("review", "build", "rework"),
        ("complete", "plan", "reopen"),
    ]


def test_renaming_label_preserves_state_identity_but_changes_source_digest():
    old = load_profile(snapshot())
    new = load_profile(
        snapshot(WORKFLOW.replace('label = "Develop"', 'label = "Build"'))
    )
    assert old.states[1].id == new.states[1].id == "build"
    assert old.states[1].label == "Develop" and new.states[1].label == "Build"
    assert old.source.digest != new.source.digest
    assert old.ordinary_edges == new.ordinary_edges


@pytest.mark.parametrize(
    ("before", "after", "reason"),
    [
        ('"aitm.workflow/v1"', '"aitm.workflow/v2"', "schema"),
        ('id = "archive"', 'id = "build"', "duplicate state"),
        ('trip = "plan"', 'trip = "unknown"', "unknown state"),
        ('non_delivery = "complete"', 'non_delivery = "build"', "non_delivery"),
        ('to = "build"\nprepare', 'to = "unknown"\nprepare', "unknown state"),
        ('to = "build"\nprepare', 'to = "review"\nprepare', "ordered"),
        ('kind = "reopen"', 'kind = "rework"', "terminal"),
        ('kind = "rework"', 'kind = "unregistered"', "kind"),
        ('id = "delivery"', 'id = "delivery"\nsource = "foreign"', "source"),
        (
            '["core.directive.plan"]',
            '["core.directive.plan", "core.directive.plan"]',
            "duplicate",
        ),
    ],
)
def test_malformed_profile_fails_at_its_pinned_source(before, after, reason):
    with pytest.raises(ProfileUnavailable, match=reason) as caught:
        load_profile(snapshot(WORKFLOW.replace(before, after, 1)))
    assert PATH in str(caught.value)


def test_declared_edges_cannot_repeat_one_source_target_pair():
    same_edge = '\n[[edges]]\nfrom = "plan"\nto = "build"\nkind = "rework"\n'
    with pytest.raises(ProfileUnavailable, match="duplicate edge"):
        load_profile(snapshot(WORKFLOW + same_edge))


def test_invalid_toml_and_non_utf8_are_typed_profile_refusals():
    for raw in ('schema="broken', b"\xff\xfe"):
        with pytest.raises(ProfileUnavailable, match=PATH):
            load_profile(snapshot(raw))


def test_policy_selected_path_must_equal_committed_workflow_path():
    with pytest.raises(ProfileUnavailable, match="configured"):
        load_profile(snapshot(configured=".aitm/workflows/other.toml"))
