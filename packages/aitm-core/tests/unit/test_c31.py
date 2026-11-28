"""Evaluate attempt-control rules against typed snapshots in process."""

from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256

import pytest

from aitm_core.activity import ActivityObservation, ingest_activity
from aitm_core.events import core_reducers, fold, validate_envelope
from aitm_core.ext.api import ProducerRef
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
from aitm_core.rules.trips import expansion_child, preflight_attempt
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

    ended = observed + timedelta(seconds=4)
    activity = ingest_activity(
        ProducerRef(
            id="fixture.engagement",
            version=1,
            measurement_contract="engaged-interval/v1",
            coverage_class="measured-engagement",
        ),
        (
            ActivityObservation(
                source_id="child-proof",
                actor="fixture-agent",
                actor_kind="agent",
                session="fixture",
                attempt="fixture-attempt",
                generation=1,
                binding="fixture-binding",
                observed_at=observed,
                recorded_at=ended,
                ended_at=ended,
                evidence=("fixture",),
            ),
        ),
    ).records
    normal = ctx.operation.model_copy(
        update={
            "intent": ctx.operation.intent.model_copy(
                update={"kind": "state.transition", "payload": b"{}"}
            ),
        }
    )
    overrun = preflight_attempt(
        replace(ctx, operation=normal), graph, activity, ended, "enforce"
    )
    assert (overrun.origin, overrun.child, overrun.cause) == (16, 17, "time-limit")
    assert overrun.proof == ("child-proof",)

    from aitm_core.models.attempts import AttemptClosed

    origin = graph.states[16]
    previous_state = origin.domains["attempts"]
    previous = previous_state.attempts["fixture-attempt"]
    closed = previous.model_copy(
        update={
            "closed": True,
            "closures": (
                AttemptClosed(
                    attempt="fixture-attempt",
                    generation=1,
                    disposition="pivot",
                    from_clock="active",
                    reason="Continue child under the new plan",
                ),
            ),
        }
    )
    renewed = previous.model_copy(
        update={
            "started": previous.started.model_copy(update={"attempt": "replacement"}),
        }
    )
    attempts = previous_state.model_copy(
        update={
            "current_attempt": "replacement",
            "attempts": {"fixture-attempt": closed, "replacement": renewed},
        }
    )
    lifecycle = origin.domains["lifecycle"]
    linked = lifecycle.model_copy(
        update={
            "relationships": lifecycle.relationships.model_copy(
                update={"blocked_by": (17,)}
            ),
        }
    )
    carried = replace(
        origin, domains={**origin.domains, "attempts": attempts, "lifecycle": linked}
    )
    assert expansion_child(carried, "replacement") == 17
    removed = replace(carried, domains={**carried.domains, "lifecycle": lifecycle})
    assert expansion_child(removed, "replacement") is None


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


def test_registered_preflight_retains_unknown_activity_for_scoped_attempt():
    _, graph = make_graph()
    story = 16
    path = story_event_path(story)
    reads = (ReadExpectation(path=path, digest=sha256(graph.logs[path]).hexdigest()),)
    operation = Operation(
        operation_id="probe-unknown",
        owner=OperationOwner(actor=EventActor(kind="tool", harness="fixture")),
        policy_digest="a" * 64,
        category=OperationCategory.NORMAL,
        change=RelatedWriteSet(read_set=reads),
        intent=FinalizationIntent(
            kind="state.transition",
            version=1,
            payload=b"{}",
            related_preconditions=reads,
        ),
    )
    attempt = graph.states[story].domains["attempts"].attempts["fixture-attempt"]
    context = OperationContext(
        operation, Snapshot("fixture", "a" * 40, "b" * 40), (attempt,)
    )
    result = preflight_attempt(
        context, graph, None, datetime.fromisoformat(STAMP), "enforce"
    )
    assert result.preflight.outcome == PreflightOutcome.PASSED
    assert result.preflight.reason == "activity-unknown"
    assert result.cause is None and result.measured_millis is None


def test_trip_decision_pins_stopped_custody_and_rejects_contradiction():
    from aitm_core.models.attempts import SourceSnapshot
    from aitm_core.models.binding import EntityRef
    from aitm_core.models.config import BacklogIssuer
    from aitm_core.models.evidence import ExpansionCustody, TripRecorded
    from aitm_core.models.identity import DraftSource
    from aitm_core.providers.backlog import GraduationIntent
    from aitm_core.providers.identity import reservation_root
    from aitm_core.rules.trips import STOP_CATEGORIES, decide_trip

    profile, graph = make_graph()
    story = 16
    source = DraftSource(
        entity=EntityRef(
            identity="draft-one", document=".aitm/drafts/2026-11/draft-one/draft.md"
        ),
        snapshot=SourceSnapshot(commit="c" * 40, tree="d" * 40),
        draft_tree="e" * 40,
        document_digest="a" * 64,
    )
    intent = GraduationIntent(
        operation_id="held",
        source=source,
        shared=False,
        issuer=BacklogIssuer(
            backlog="local", backlog_repository="fixture", numbering_namespace="issues"
        ),
    )
    snapshot = Snapshot("fixture", "a" * 40, "b" * 40)
    owner = OperationOwner(actor=EventActor(kind="tool", harness="fixture"))
    event = EventContext("fixture-custody", owner, STAMP, "a" * 64)
    state = graph.states[story]
    attempt = state.domains["attempts"].attempts["fixture-attempt"]
    attempts = state.domains["attempts"].model_copy(
        update={
            "attempts": {
                attempt.started.attempt: attempt.model_copy(update={"closed": True})
            }
        }
    )
    coordinates = dict(attempt=attempt.started.attempt, generation=1)
    entries = {
        "core.expansion.reserved": ExpansionReserved(
            **coordinates,
            reservation="held",
            intent=intent.model_dump_json(),
            holder="fixture-binding",
        ),
        "core.expansion.custody-recorded": ExpansionCustody(
            **coordinates,
            reservation="held",
            semantic_key=source.semantic_key,
            disposition="no-child",
            authority="local-allocation",
            verified_at=snapshot.revision,
            proof_refs=(f"local-allocation-fenced:{snapshot.revision}",),
        ),
        "core.trip.recorded": TripRecorded(
            **coordinates,
            cause="second-expansion",
            coverage="qualified-expansion",
            detected_at=STAMP,
            proof_refs=("fixture",),
        ),
    }
    fact_rows = {
        name: (
            ObservedFact(
                validate_envelope(event.encode(story, name, state, fact, name)), fact
            ),
        )
        for name, fact in entries.items()
    }
    graph.states[story] = replace(
        state,
        domains={
            **state.domains,
            "attempts": attempts,
            "evidence": EvidenceState(story, facts=fact_rows),
        },
    )
    analysis = ".aitm/stories/000/16/plan/analysis.md"
    issuer = f"{reservation_root(source.semantic_key)}/issue.json"
    body = {**graph.logs, analysis: b"Accepted analysis"}

    class RepositoryFixture:
        def read_blobs(self, _tree, paths):
            return {path: body.get(path) for path in paths}

    def decision():
        return decide_trip(
            RepositoryFixture(),
            snapshot,
            graph,
            profile,
            "enforce",
            owner,
            "a" * 64,
            story,
            "refactor",
            analysis,
            "Change the scope",
            at=datetime.fromisoformat(STAMP),
        )

    operation = decision()
    reads = {entry.path: entry.digest for entry in operation.change.read_set}
    assert (
        reads[story_event_path(story)]
        == sha256(graph.logs[story_event_path(story)]).hexdigest()
    )
    assert issuer in reads and reads[issuer] is None
    body[issuer] = b"Concurrent positive issuer receipt"
    changed = evaluate_operation(
        operation,
        snapshot,
        RepositoryFixture().read_blobs(snapshot.tree, reads),
        ports=ServicePorts(),
        categories=STOP_CATEGORIES,
    )
    assert (
        changed.outcome == LocalOutcome.CONFLICT
        and changed.reason == "read-set-changed"
    )
    with pytest.raises(ValueError, match="Positive issuance contradicts"):
        decision()
