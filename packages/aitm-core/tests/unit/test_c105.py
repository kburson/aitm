"""Drive the composed lifecycle through two differently shaped policy snapshots."""

from dataclasses import replace
from hashlib import sha256
from json import dumps, loads

import pytest

from aitm_core.dispositions import DispositionRequest, dispose
from aitm_core.machine.obligations import HOSTED_DELIVERY, validate_profile
from aitm_core.machine.profile import load_profile
from aitm_core.machine.transitions import explain, transition
from aitm_core.models.common import LocalOutcome
from aitm_core.splitting import SplitRequest, split_leaf
from tests.unit.test_c28_transitions import PATH
from tests.unit.test_c28_transitions import context as context
from tests.unit.test_c71_split import replay, seeded, with_history
from tests.unit.test_c90_profile import snapshot
from tests.unit.test_c91 import document, registry


def workflow_document(housekeeping):
    model = document(housekeeping)
    model["id"] = "housekeeping" if housekeeping else "delivery"
    model["states"].insert(1, {"id": "refine", "label": "Refine the work"})
    if not housekeeping:
        model["states"].insert(2, {"id": "ready-for-plan", "label": "Await planning"})
    if housekeeping:
        model["lifecycle"].update(terminal="archive", non_delivery="archive")
        terminal = model["states"][-1]
        terminal.update(id="archive", label="Archive the record")
        model["edges"][-1]["to"] = "archive"

    def fields(values):
        return [
            f"{key} = {dumps(value)}"
            for key, value in values.items()
            if key != "source"
        ]

    rows = fields({key: model[key] for key in ("schema", "id", "contract")})
    for key in ("lifecycle", "recovery"):
        rows.extend(("", f"[{key}]", *fields(model[key])))
    for key in ("states", "edges"):
        for entry in model[key]:
            rows.extend(("", f"[[{key}]]", *fields(entry)))
    return "\n".join(rows) + "\n"


def loaded_request(context, profile, state):
    request = seeded(context, initial=state)
    existing = request.backend.read(request.backend.snapshot(), (PATH,))[PATH]
    prior = b""
    for index, line in enumerate(existing.splitlines()):
        record = loads(line)
        if index == 0:
            current = next(item for item in profile.states if item.id == state)
            record["data"]["initial_state"].update(
                workflow_id=profile.id,
                revision=profile.source.digest,
                state_id=state,
                label=current.label,
            )
        record["prior_log_digest"] = sha256(prior).hexdigest()
        prior += dumps(record).encode() + b"\n"
    return with_history(
        replace(request, profile=profile, registry=registry("enforce")), prior
    )


@pytest.mark.parametrize("housekeeping", [False, True], ids=["parking", "housekeeping"])
def test_composed_workflow_loads_and_routes_the_resolved_operations(
    context, housekeeping
):
    profile = load_profile(snapshot(workflow_document(housekeeping)))
    validated = validate_profile(profile, registry("enforce"), HOSTED_DELIVERY)
    assert validated.available, validated.problems
    assert ("ready-for-plan" in {state.id for state in profile.states}) != housekeeping

    from_refine = loaded_request(context, profile, "refine")
    split = split_leaf(
        SplitRequest(
            from_refine, "Two independently deliverable outcomes.", "Oversized", 4
        )
    )
    assert split.command.local == LocalOutcome.COMPLETED, split.reason
    epic = replay(from_refine)
    assert epic.kind == "epic"
    assert epic.workflow_state.state_id == validated.recovery.design_rework
    assert epic.story_id == 1 and not epic.estimates and not epic.accepted_documents

    outcome = dispose(
        DispositionRequest(
            replace(from_refine, operation_id="c105-explicit-disposal"),
            "abandoned",
            "The supported explicit terminal route.",
        )
    )
    assert outcome.command.local == LocalOutcome.COMPLETED, outcome.reason
    terminal = replay(from_refine).transitions[-1]
    assert terminal.to_state.state_id == validated.lifecycle.non_delivery
    assert terminal.edge.kind == "terminal" and terminal.disposition == "abandoned"

    final_edge = profile.ordinary_edges[-1]
    assert final_edge.source == ("housekeeping" if housekeeping else "review")
    assert final_edge.target == validated.lifecycle.terminal
    assert final_edge.operation == HOSTED_DELIVERY.finalize

    rework = replace(loaded_request(context, profile, "review"), direction="rework")
    before = rework.backend.snapshot()
    decision = explain(rework)
    assert (decision.source, decision.target, decision.operation) == (
        "review",
        validated.recovery.implementation_rework,
        HOSTED_DELIVERY.rework,
    )
    assert decision.outcome == LocalOutcome.UNAVAILABLE
    assert transition(rework).command.local == LocalOutcome.UNAVAILABLE
    assert rework.backend.snapshot() == before
