"""Replay accepted Core facts through the installed registry."""

from hashlib import sha256
from json import dumps

import pytest

from aitm_core.events import (
    FoldIntegrityError,
    UnavailableReducer,
    core_event_schema,
    core_reducers,
    fold,
)
from aitm_core.reducers.attempts import AttemptIntegrityError
from aitm_core.reducers.evidence import EvidenceIntegrityError

STAMP = "2026-11-27T09:00:00Z"
DIGEST = "a" * 64
SOURCE = {"commit": "b" * 40, "tree": "c" * 40}
LEGACY = {
    "workflow_id": "configured",
    "revision": DIGEST,
    "state_id": "legacy.do",
    "label": "Implement",
    "capability": {"id": "workspace", "version": "2", "status": "unavailable"},
}
RENAMED = {**LEGACY, "label": "Develop", "revision": "b" * 64}
AGENT = {
    "host": "fixture",
    "provider": "provider",
    "model_id": "reviewer-model",
    "effort": "low",
    "session_id": None,
    "session_id_kind": "unknown",
}

CORE_TYPES = set(
    """
core.idea.created core.draft.created core.draft.discarded core.story.graduated
core.kind.changed core.design.invalidated core.state.changed core.guard.evaluated core.action.pending
core.action.completed core.action.failed core.session.started core.session.ended
core.attempt.started core.attempt.reconciled core.attempt.closed core.attempt.reopened core.attempt.clock.changed
core.execution.recorded core.estimate.set core.doc.accepted core.jit.recorded
core.expansion.reserved core.expansion.reservation-resolved core.expansion.recorded core.expansion.custody-recorded
core.expansion.resolved core.trip.recorded core.trip.decided core.pivot.recorded core.test.receipt
core.review.recorded core.review.activated core.review.invalidated core.doc-review.opened
core.doc-review.submitted core.doc-review.completed core.signoff.recorded core.link.changed
core.description.set core.deliverable.added core.deliverable.validated core.delivery.verified
core.outcome.recorded core.usage.recorded core.activity.recorded
""".split()
)


def records(*operations):
    prefix = sha256()
    result = []
    for index, events in enumerate(operations, 1):
        for kind, data in events:
            n = len(result) + 1
            raw = dumps(
                {
                    "v": 1,
                    "id": f"e{n}",
                    "ts": STAMP,
                    "type": kind,
                    "story": 8,
                    "actor": {"kind": "agent", "harness": "fixture"},
                    "operation_id": f"op{index}",
                    "sequence": n,
                    "prior_log_digest": prefix.hexdigest(),
                    "data": data,
                }
            ).encode()
            result.append(raw)
            prefix.update(raw + b"\n")
    return result


def fact(event, **data):
    return "core." + event, data


def boundary(cause, before, after, *, generation=1, used=0):
    return fact(
        "attempt.clock.changed",
        attempt="a1",
        generation=generation,
        cause_event_id=cause,
        **{"from": before, "to": after, "observed_at": STAMP, "used_millis": used},
    )


def graduation():
    return fact(
        "story.graduated",
        kind="story",
        source_kind="plan-entry",
        source_id="C56",
        source_digest=DIGEST,
        issue="#8",
        initial_state={**LEGACY, "state_id": "old.ready", "label": "Ready"},
    )


def start(cause):
    return [
        fact(
            "attempt.started",
            attempt="a1",
            generation=1,
            plan_generation=1,
            source=SOURCE,
            binding="binding-1",
            allowance_millis=3000,
        ),
        boundary(cause, None, "active"),
    ]


def test_complete_event_schema():
    schema = core_event_schema()
    exported = {item["properties"]["type"]["const"] for item in schema["oneOf"]}
    assert exported == CORE_TYPES
    for option in schema["oneOf"]:
        assert (
            "$ref" in option["properties"]["data"]
            or "anyOf" in option["properties"]["data"]
        )
    assert schema == core_event_schema()
    assert "$defs" in schema and "EventEnvelope" in schema["$defs"]
    with pytest.raises(UnavailableReducer, match="core.unknown.event"):
        fold(records([fact("unknown.event")]), core_reducers())


def test_installed_replay_reconstructs_historical_workflow_and_typed_attempt():
    initial = graduation()[1]["initial_state"]
    enter = fact(
        "state.changed",
        **{"from": initial, "to": LEGACY},
        edge={
            "id": "enter-implementation",
            "workflow_id": "configured",
            "revision": DIGEST,
            "source": "old.ready",
            "target": "legacy.do",
            "kind": "normal",
        },
        mode="enforce",
        attempt="a1",
    )
    rework = fact(
        "state.changed",
        **{"from": LEGACY, "to": RENAMED},
        edge={
            "id": "resume-implementation",
            "workflow_id": "configured",
            "revision": RENAMED["revision"],
            "source": "legacy.do",
            "target": "legacy.do",
            "kind": "rework",
        },
        mode="enforce",
        attempt="a1",
    )
    close = fact(
        "attempt.closed",
        attempt="a1",
        generation=1,
        from_clock="active",
        disposition="delivered",
        reason="verified",
    )
    stream = records(
        [graduation()],
        [enter, *start("e3")],
        [rework],
        [close, boundary("e6", "active", "terminal-closed", used=20)],
        [("other.ext.observed", {"original": True})],
    )
    state = fold(stream, core_reducers())
    assert fold(iter(stream), core_reducers()) == state
    history = state.domains["lifecycle"].state_history
    assert [item.state_id for item in history] == [
        "old.ready",
        "legacy.do",
        "legacy.do",
    ]
    assert [item.label for item in history] == ["Ready", "Implement", "Develop"]
    assert (
        history[1].revision == DIGEST and history[1].capability.status == "unavailable"
    )
    attempt = state.domains["attempts"].attempts["a1"]
    assert attempt.started.attempt == "a1" and attempt.clock_mode == "terminal-closed"
    assert attempt.closed and attempt.used_millis == 20
    assert state.opaque_events == (stream[-1],)


def test_boundary_batch_validation_keeps_event_retry_and_causal_order():
    stream = records(start("e1"))
    expected = fold(stream, core_reducers())
    assert fold([stream[0], *stream], core_reducers()) == expected
    with pytest.raises(FoldIntegrityError, match="different bytes"):
        fold(
            [*stream, stream[1].replace(b'"used_millis": 0', b'"used_millis": 1')],
            core_reducers(),
        )
    with pytest.raises(AttemptIntegrityError, match="missing clock"):
        fold(stream[:1], core_reducers())
    split = records([start("e1")[0]], [start("e1")[1]])
    with pytest.raises(AttemptIntegrityError, match="missing clock"):
        fold(split, core_reducers())


def test_review_record_only_becomes_effective_on_causal_activation():
    review = fact(
        "review.recorded",
        review_id="sar-1",
        verdict="pass",
        attempt="a1",
        generation=1,
        source=SOURCE,
        reviewer_ref="reviewer/independent-1",
        proof_refs=["review-proof"],
    )
    activation = {
        "review_id": "sar-1",
        "attempt": "a1",
        "generation": 1,
        "source": SOURCE,
        "policy_digest": DIGEST,
        "proof_refs": ["test-1"],
        "reason": "eligible",
    }
    begin = start("e1")
    raw_only = fold(records(begin, [review]), core_reducers())
    assert not raw_only.domains["evidence"].effective_reviews
    assert raw_only.domains["attempts"].attempts["a1"].clock_mode == "active"
    activate = [
        fact("review.activated", **activation),
        boundary("e4", "active", "review-stopped", used=20),
    ]
    active = fold(records(begin, [review], activate), core_reducers())
    assert "sar-1" in active.domains["evidence"].effective_reviews
    invalidate = [
        fact("review.invalidated", **activation, resumes_execution=True),
        boundary("e6", "review-stopped", "active", used=20),
    ]
    state = fold(records(begin, [review], activate, invalidate), core_reducers())
    assert not state.domains["evidence"].effective_reviews
    assert state.domains["attempts"].attempts["a1"].clock_mode == "active"
    wrong_source = {**activation, "source": {**SOURCE, "tree": "d" * 40}}
    with pytest.raises(EvidenceIntegrityError, match="matching passing receipt"):
        fold(
            records(
                begin, [review], [fact("review.activated", **wrong_source), activate[1]]
            ),
            core_reducers(),
        )


def test_action_outcome_and_usage_retain_distinct_provenance():
    action = {
        "origin_operation": "op2",
        "owner": "board",
        "action_id": "sync",
        "target_version": 2,
        "owner_version": "3",
        "attempt": None,
        "workflow": LEGACY,
    }
    failed = fact(
        "action.failed", **action, outcome="unavailable", proof_refs=["disabled"]
    )
    usage = {
        "producer": "fixture",
        "receipt_id": "cost-1",
        "unit": "token",
        "quantity": 9007199254740993,
        "availability": "observed",
        "proof_refs": ["provider-receipt"],
    }
    outcome = fact(
        "outcome.recorded",
        phase="close",
        workflow=LEGACY,
        disposition="unverified",
        actual_agent_hours=None,
        qualification="unknown",
        proof_refs=["waiver"],
    )
    actions = [[fact("action.pending", **action)], [failed]]
    stream = records(
        [graduation()], *actions, [outcome], [fact("usage.recorded", **usage)] * 2
    )
    state = fold(stream, core_reducers())
    evidence = state.domains["evidence"]
    entry = evidence.actions[("op2", "board", "sync", 2)]
    assert entry.result.outcome == "unavailable"
    assert entry.pending.workflow == entry.result.workflow
    assert len(evidence.usage) == 1
    assert evidence.usage["fixture", "cost-1"].quantity == 9007199254740993
    assert (
        evidence.facts["core.outcome.recorded"][0].payload.disposition == "unverified"
    )
    assert state.domains["lifecycle"].workflow_state.state_id == "old.ready"
    with pytest.raises(EvidenceIntegrityError, match="usage receipt"):
        fold(
            records(
                [fact("usage.recorded", **usage)],
                [fact("usage.recorded", **{**usage, "quantity": 13})],
            ),
            core_reducers(),
        )


def test_action_retry_keeps_all_operation_results_under_the_same_key():
    scope = {
        "origin_operation": "op1",
        "owner": "board",
        "action_id": "sync",
        "target_version": 1,
        "owner_version": "3",
        "attempt": None,
        "workflow": LEGACY,
    }
    pending = fact("action.pending", **scope)
    unavailable = fact(
        "action.failed", **scope, outcome="unavailable", proof_refs=["disabled"]
    )
    completed = fact(
        "action.completed", **scope, outcome="completed", proof_refs=["synced"]
    )
    distinct_failure = fact(
        "action.failed", **scope, outcome="failed", proof_refs=["denied"]
    )
    for conflicting in (distinct_failure, completed):
        with pytest.raises(EvidenceIntegrityError, match="conflicting action results"):
            fold(records([pending], [unavailable, conflicting]), core_reducers())
    with pytest.raises(EvidenceIntegrityError, match="completed action"):
        fold(
            records([pending], [unavailable], [completed], [distinct_failure]),
            core_reducers(),
        )

    observations = records([pending], [unavailable], [completed])
    state = fold([*observations, observations[1]], core_reducers())
    action = state.domains["evidence"].actions[("op1", "board", "sync", 1)]
    assert [(key, result.outcome) for key, result in action.results.items()] == [
        ("op2", "unavailable"),
        ("op3", "completed"),
    ]
    assert action.result.outcome == "completed"


def test_document_review_retains_opening_and_deduplicates_turns():
    key = {"record_id": "level-1", "level": "sar", "path": "plans/current.md"}
    opening = fact(
        "doc-review.opened",
        **key,
        raw_digest=DIGEST,
        content_digest=DIGEST,
        opened_at=STAMP,
        source_operation="op1",
        opened_by={"kind": "agent", "harness": "fixture"},
    )
    turn = fact(
        "doc-review.submitted",
        **key,
        round=1,
        role="reviewer",
        agent=AGENT,
        started_at=None,
        submitted_at=STAMP,
        start_basis="unknown",
        input_digest=DIGEST,
        response_path="reviews/response.md",
        source_digest=DIGEST,
        finding_ids=[],
        decision="pass",
    )
    completion = fact(
        "doc-review.completed",
        **key,
        rounds=1,
        outcome="exhausted",
        base_digest=DIGEST,
        final_digest=DIGEST,
        started_at=None,
        ended_at=STAMP,
        manifest_path="reviews/manifest.json",
    )
    state = fold(records([opening], [turn], [turn], [completion]), core_reducers())
    review = state.domains["evidence"].document_reviews["level-1"]
    assert review.opening.source_operation == "op1"
    assert (
        review.opening.opened_by.harness == "fixture"
        and review.opening.opened_at == STAMP
    )
    assert review.started_at == STAMP and len(review.turns) == 1
    legacy = fold(records([turn], [completion]), core_reducers())
    assert legacy.domains["evidence"].document_reviews["level-1"].started_at is None
    with pytest.raises(EvidenceIntegrityError, match="review turn"):
        fold(
            records(
                [turn],
                [
                    (turn[0], {**turn[1], "source_digest": "b" * 64}),
                ],
            ),
            core_reducers(),
        )


def test_composition_preserves_recovery_session_and_attempt_authority():
    close = [
        fact(
            "attempt.closed",
            attempt="a1",
            generation=1,
            from_clock="active",
            disposition="unverified",
            reason="missing evidence",
        ),
        boundary("e3", "active", "terminal-closed", used=12),
    ]
    reopen = [
        fact(
            "attempt.reopened",
            attempt="a1",
            generation=1,
            source=SOURCE,
            allowance_millis=3000,
            closure_reason="missing evidence",
            authority={
                "purpose": "evidence",
                "authority_id": "recover-1",
                "attempt": "a1",
                "ended_generation": 1,
                "source": SOURCE,
                "allowed": ["managed-verification"],
            },
        )
    ]
    bind = [
        fact(
            "session.started",
            attempt="a1",
            generation=2,
            source=SOURCE,
            purpose="evidence",
            authority_id="recover-1",
            binding="binding-2",
            needs_verification=True,
            session="session-2",
            worktree="tree-2",
            branch="codex/fixture",
            allowed_paths=[],
        ),
        boundary("e6", "terminal-closed", "active", generation=2, used=12),
    ]
    state = fold(records(start("e1"), close, reopen, bind), core_reducers())
    assert state.domains["attempts"].attempts["a1"].generation == 2
    assert (
        state.domains["evidence"].facts["core.session.started"][0].payload.session
        == "session-2"
    )
