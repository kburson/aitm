"""Structural authority boundaries in default and optional-closeout profiles."""

from types import SimpleNamespace

import pytest

from aitm_core.ext.api import CapabilitySlot, DirectiveRegistration
from aitm_core.ext.registry import load_extensions
from aitm_core.machine.obligations import HOSTED_DELIVERY, validate_profile
from aitm_core.machine.profile import WorkflowProfile

PICKUP = "core.plan.pickup-basis-current"
BINDING = "core.dev.binding-ready"
ATTEMPT = "core.attempt.begin-or-resume"
CANDIDATE = "core.dev.review-candidate-current"
TERMINAL = "core.closeout.terminal-disposition-valid"
CLOSEOUT = "core.closeout.complete"
FINALIZE = "core.story.finalize-delivery"
REWORK = "core.review.rework-authorized"
DIRECTIVE = "core.directive.author-closeout"
RECORDED = "core.closeout.record-evidence"
DELIVERY = "core.delivery.verified"


def document(housekeeping=False):
    states = [
        {"id": "design", "label": "Define"},
        {"id": "plan", "label": "Prepare", "onExit": [PICKUP]},
        {"id": "dev", "label": "Build", "onEnter": [BINDING], "onExit": [CANDIDATE]},
        {"id": "review", "label": "Inspect", "onEnter": [CANDIDATE]},
        {"id": "complete", "label": "Archive", "onEnter": [TERMINAL]},
    ]
    if housekeeping:
        states.insert(
            4, {"id": "housekeeping", "label": "Record delivery", "onEnter": [DELIVERY]}
        )
    closeout = states[-2]
    closeout.update(action=[DIRECTIVE, RECORDED], onExit=[CLOSEOUT])
    return {
        "schema": "aitm.workflow/v1",
        "id": "example",
        "contract": HOSTED_DELIVERY.id,
        "source": {
            "path": "workflow.toml",
            "revision": "a" * 40,
            "tree": "b" * 40,
            "digest": "c" * 64,
        },
        "lifecycle": {
            "terminal": "complete",
            "non_delivery": "complete",
            "reopen_design": "design",
            "reopen_plan": "plan",
        },
        "recovery": {
            "design_rework": "design",
            "implementation_rework": "dev",
            "trip": "plan",
            "scope_pivot": "plan",
        },
        "states": states,
        "edges": [
            {"from": "plan", "to": "dev", "operation": ATTEMPT},
            {
                "from": "review",
                "to": "dev",
                "kind": "rework",
                "guards": [REWORK],
                "operation": "core.attempt.resume-for-rework",
            },
            {"from": closeout["id"], "to": "complete", "operation": FINALIZE},
        ],
    }


def registry(mode, missing=None):
    policy = SimpleNamespace(
        config=SimpleNamespace(
            extensions=SimpleNamespace(enabled=()), guards=SimpleNamespace(mode=mode)
        )
    )
    guards = [
        CapabilitySlot(
            id=rule,
            version=1,
            kind="guard",
            placements=("onEnter", "onExit"),
            required_facts=("core.closeout.authored",) if rule == CLOSEOUT else (),
        )
        for rule in (PICKUP, BINDING, CANDIDATE, TERMINAL, CLOSEOUT, REWORK, DELIVERY)
        if rule != missing
    ]
    directive = DirectiveRegistration(
        slot=CapabilitySlot(
            id=DIRECTIVE, version=1, kind="directive", placements=("action",)
        ),
        markdown="directives/closeout.md",
    )
    recorded = CapabilitySlot(
        id=RECORDED,
        version=1,
        kind="action",
        placements=("action",),
        execution="requested",
        produced_evidence=("core.closeout.authored",),
    )
    return load_extensions(policy, builtins=[*guards, directive, recorded])


def validate(raw, mode="enforce", missing=None):
    return validate_profile(
        WorkflowProfile.model_validate(raw), registry(mode, missing), HOSTED_DELIVERY
    )


@pytest.mark.parametrize("housekeeping", [False, True])
def test_typed_destinations_and_capabilities_survive_renamed_labels(housekeeping):
    result = validate(document(housekeeping))
    assert result.valid and result.available
    assert result.lifecycle.terminal == "complete"
    assert result.lifecycle.reopen_design == "design"
    assert result.recovery.implementation_rework == "dev"
    assert result.recovery.scope_pivot == "plan"


@pytest.mark.parametrize("mode", ["enforce", "advisory"])
@pytest.mark.parametrize(
    ("section", "index", "field", "value", "code"),
    [
        ("edges", 0, "operation", None, "attempt-start"),
        ("states", 1, "onExit", [], "attempt-start"),
        ("states", 3, "onEnter", [], "exact-candidate"),
        ("edges", 2, "operation", None, "terminal-finalization"),
        ("states", 3, "onExit", [DIRECTIVE], "slot-kind"),
        ("edges", 1, "operation", ATTEMPT, "implementation-rework"),
    ],
)
def test_authority_obligations_hold_in_both_modes(
    mode, section, index, field, value, code
):
    raw = document()
    raw[section][index][field] = value
    result = validate(raw, mode)
    assert not result.valid
    assert code in {problem.code for problem in result.problems}


def test_nonsequential_terminal_route_cannot_bypass_review():
    raw = document()
    raw["states"][1]["onExit"].append(CLOSEOUT)
    raw["edges"].append(
        {"from": "plan", "to": "complete", "kind": "terminal", "operation": FINALIZE}
    )
    result = validate(raw)
    assert not result.valid
    assert "review-bypass" in {problem.code for problem in result.problems}


def test_reopen_binding_cannot_enter_review():
    raw = document()
    raw["lifecycle"]["reopen_plan"] = "review"
    assert not validate(raw).valid


def test_required_missing_capability_leaves_a_structural_profile_unavailable():
    result = validate(document(), missing=CANDIDATE)
    assert result.valid
    assert not result.available
    assert "capability-unavailable" in {problem.code for problem in result.problems}


def test_housekeeping_requires_verified_delivery_on_entry():
    raw = document(housekeeping=True)
    raw["states"][4]["onEnter"] = []
    assert "verified-delivery" in {problem.code for problem in validate(raw).problems}


def test_closeout_guard_needs_a_predecessor_that_can_produce_its_fact():
    raw = document()
    raw["states"][3]["action"].remove(RECORDED)
    raw["states"][4]["action"] = [RECORDED]
    assert "predecessor-fact" in {problem.code for problem in validate(raw).problems}
