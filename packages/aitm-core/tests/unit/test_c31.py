"""Evaluate attempt-control rules against typed snapshots in process."""

from dataclasses import replace
from datetime import datetime
from hashlib import sha256

import pytest

from aitm_core.events import core_reducers, fold, validate_envelope
from aitm_core.machine.profile import load_profile
from aitm_core.models.common import LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.evidence import ExpansionRecorded, ExpansionReserved
from aitm_core.models.operations import (
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.pivots import HumanContext, pivot
from aitm_core.reducers.evidence import EvidenceState, ObservedFact
from aitm_core.relationships import EventContext, StoryGraph
from aitm_core.rules.expansion import ExpansionAuthority
from aitm_core.rules.trips import preflight_attempt
from aitm_core.services import ServicePorts
from aitm_core.store.backend import OperationContext, Snapshot, evaluate_operation
from tests.integration.test_c22 import STAMP, with_attempt
from tests.unit.test_c15 import graduated
from tests.unit.test_c90_profile import snapshot as policy_snapshot


def make_graph():
    from json import dumps, loads

    profile = load_profile(policy_snapshot())
    logs = {}
    states = {}
    for number in (16, 17):
        root = loads(graduated())
        root["story"] = number
        root["data"]["initial_state"] = {
            "workflow_id": profile.id,
            "revision": profile.source.digest,
            "state_id": "build",
            "label": next(
                state.label for state in profile.states if state.id == "build"
            ),
        }
        raw = with_attempt(dumps(root).encode() + b"\n", number)
        logs[story_event_path(number)] = raw
        states[number] = fold(raw.splitlines(keepends=True), core_reducers())
    return profile, StoryGraph(
        {story: state.domains["lifecycle"] for story, state in states.items()},
        states,
        logs,
    )


def test_second_and_nested_expansion_use_durable_relationship_proof():
    _, graph = make_graph()
    owner = OperationOwner(actor=EventActor(kind="tool", harness="fixture"))
    scope = graph.states[16]
    event = EventContext("fixture", owner, STAMP, "a" * 64)
    hold = ExpansionReserved(
        attempt="fixture-attempt",
        generation=1,
        reservation="first",
        intent="first",
        holder="fixture",
    )
    child = ExpansionRecorded(
        attempt="fixture-attempt",
        generation=1,
        reservation="first",
        child=17,
        kind="defect",
        reason="Fixture work",
    )
    evidence = EvidenceState(
        16,
        facts={
            "core.expansion.reserved": (
                ObservedFact(
                    validate_envelope(
                        event.encode(16, "core.expansion.reserved", scope, hold, "held")
                    ),
                    hold,
                ),
            ),
            "core.expansion.recorded": (
                ObservedFact(
                    validate_envelope(
                        event.encode(
                            16, "core.expansion.recorded", scope, child, "child"
                        )
                    ),
                    child,
                ),
            ),
        },
    )
    graph.states[16] = replace(scope, domains={**scope.domains, "evidence": evidence})
    observed = datetime.fromisoformat(STAMP)
    for story, cause in ((16, "second-expansion"), (17, "nested-expansion")):
        fact = ExpansionAuthority(
            origin=story,
            attempt="fixture-attempt",
            generation=1,
            reservation="another",
            kind="story",
            draft_handle="draft",
            reason="A new expansion",
            issuer_route="local",
        )
        reads = (
            ReadExpectation(
                path=story_event_path(story),
                digest=sha256(graph.logs[story_event_path(story)]).hexdigest(),
            ),
        )
        operation = Operation(
            operation_id="another",
            owner=owner,
            policy_digest="a" * 64,
            category=OperationCategory.NORMAL,
            change=RelatedWriteSet(read_set=reads),
            intent=FinalizationIntent(
                kind="expand",
                version=1,
                payload=fact.model_dump_json().encode(),
                related_preconditions=reads,
            ),
        )
        snapshot = Snapshot("fixture", "a" * 40, "b" * 40)
        scope_attempt = (
            graph.states[story].domains["attempts"].attempts["fixture-attempt"]
        )
        ctx = OperationContext(operation, snapshot, (scope_attempt,))
        decision = preflight_attempt(ctx, graph, None, observed, "enforce")
        assert (decision.origin, decision.child, decision.cause) == (16, 17, cause)
        assert decision.preflight.outcome == PreflightOutcome.BLOCKED
        advisory = preflight_attempt(ctx, graph, None, observed, "advisory")
        assert (
            advisory.cause == cause
            and advisory.preflight.outcome == PreflightOutcome.PASSED
        )


def test_human_pivot_requires_interactive_authority_and_records_separate_reason():
    from aitm_core.models.operations import AuthorityOrigin, WriteAuthorization
    from aitm_core.rules.trips import STOP_CATEGORIES

    profile, graph = make_graph()
    human = OperationOwner(actor=EventActor(kind="human", harness="fixture"))
    for actor in (
        HumanContext(False, False),
        HumanContext(True, True),
        HumanContext(True, False, True),
    ):
        with pytest.raises(ValueError, match="interactive human"):
            pivot(
                actor,
                graph,
                profile,
                "enforce",
                human,
                "a" * 64,
                16,
                "Change",
                "Smaller scope",
            )
    operation = pivot(
        HumanContext(True, False),
        graph,
        profile,
        "enforce",
        human,
        "a" * 64,
        16,
        "Change",
        "Smaller scope",
        at=datetime.fromisoformat(STAMP),
    )
    result = evaluate_operation(
        operation,
        Snapshot("fixture", "a" * 40, "b" * 40),
        graph.logs,
        ports=ServicePorts(
            write_authorization=lambda _owner, _change: WriteAuthorization(
                allowed=True,
                origin=AuthorityOrigin.FIXTURE,
            )
        ),
        categories=STOP_CATEGORIES,
    )
    assert result.outcome == LocalOutcome.COMPLETED, result.reason
    state = fold(
        result.writes[story_event_path(16)].splitlines(keepends=True), core_reducers()
    )
    assert (
        state.domains["lifecycle"].workflow_state.state_id
        == profile.recovery.scope_pivot
    )
    assert state.domains["attempts"].attempts["fixture-attempt"].closed
    assert set(state.domains["evidence"].facts) == {"core.pivot.recorded"}
