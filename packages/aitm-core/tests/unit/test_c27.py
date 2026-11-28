"""Pickup evidence, provisional attempt reconciliation and phase estimates."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from aitm_core.attempts import attach_attempt_evidence
from aitm_core.estimates import observe_estimate
from aitm_core.jit import Baseline, Coverage, assess_jit
from aitm_core.models.attempts import (
    AttemptRecord,
    AttemptStarted,
    ClockChanged,
    SourceSnapshot,
)
from aitm_core.models.lifecycle import Estimate

PLAN = "a" * 64
SOURCE = SourceSnapshot(commit="1" * 40, tree="2" * 40)
NEW_SOURCE = SourceSnapshot(commit="3" * 40, tree="4" * 40)


def test_jit_scope_requires_current_identity_and_complete_related_change_evidence():
    original = Baseline(kind="source", snapshot=SOURCE)
    current = Baseline(kind="source", snapshot=NEW_SOURCE)
    coverage = Coverage(
        baseline=original,
        plan_digest=PLAN,
        plan_generation=1,
        attempt="a1",
        attempt_generation=2,
        paths=("src/core",),
    )

    def assess(baseline=original, **changes):
        return assess_jit(
            coverage,
            baseline,
            **(
                dict(
                    plan_digest=PLAN,
                    plan_generation=1,
                    attempt="a1",
                    attempt_generation=2,
                )
                | changes
            ),
        )

    assert assess()
    assert assess(current, descendant=True, changed_paths=("src/other.py",))
    assert not assess(current, descendant=True, changed_paths=("src/core/sub.py",))
    assert not assess(current, descendant=True, changed_paths=("src",))
    assert not assess(current, descendant=True)
    assert not assess(current, changed_paths=())
    assert not assess(plan_digest="b" * 64)
    assert not assess(plan_generation=2)
    assert not assess(attempt="a2")
    assert not assess(attempt_generation=3)
    assert not assess(Baseline(kind="deliverable", snapshot=SOURCE))
    assert not assess_jit(
        coverage.model_copy(update={"complete": False}),
        original,
        plan_digest=PLAN,
        plan_generation=1,
        attempt="a1",
        attempt_generation=2,
    )


def test_attempt_attachment_preserves_clock_allowance_and_historical_start():
    started = AttemptStarted(
        attempt="a1",
        generation=1,
        plan_generation=None,
        source=None,
        binding=None,
        allowance_millis=10_000,
        provisional=True,
    )
    clock = ClockChanged.model_validate(
        {
            "attempt": "a1",
            "generation": 1,
            "cause_event_id": "event-1",
            "from": None,
            "to": "active",
            "observed_at": datetime(2026, 11, 28, tzinfo=UTC),
            "used_millis": 0,
        }
    )
    original = AttemptRecord(
        started=started,
        generation=1,
        binding=None,
        allowance_millis=10_000,
        used_millis=500,
        clocks=(clock,),
    )
    update = dict(
        attempt="a1", generation=1, plan_generation=2, source=SOURCE, binding="b"
    )
    attached = attach_attempt_evidence(original, **update)
    assert attached.started == original.started
    assert attached.binding == "b"
    assert attached.source == SOURCE
    assert attached.plan_generation == 2
    assert attached.generation == original.generation
    assert attached.clocks == original.clocks
    assert attached.used_millis == original.used_millis
    assert attached.allowance_millis == original.allowance_millis
    assert attach_attempt_evidence(attached, **update) == attached
    with pytest.raises(ValueError, match="retained"):
        attach_attempt_evidence(attached, **(update | {"source": NEW_SOURCE}))
    with pytest.raises(ValueError, match="generation"):
        attach_attempt_evidence(original, **(update | {"generation": 2}))


def test_refine_observation_requires_design_and_retains_the_proposal():
    proposal = Estimate(phase="decomposition", agent_hours=12, size="L", priority="P1")
    current = {"decomposition": proposal}
    refine = Estimate(phase="refine", agent_hours=12, size="L", priority="P1")
    with pytest.raises(ValueError, match="design"):
        observe_estimate(
            current,
            refine,
            kind="epic",
            design_accepted=False,
            source="proposal",
            rationale="adopted",
        )
    updated = observe_estimate(
        current,
        refine,
        kind="epic",
        design_accepted=True,
        source="proposal",
        rationale="adopted",
    )
    assert updated["decomposition"] is proposal
    assert updated["refine"].source == "proposal"
    assert updated["refine"].rationale == "adopted"
    assert updated["refine"].priority == "P1"
    assert "refine" not in current


def test_in_process_attempt_reconcile_obeys_transaction_preflight():
    from hashlib import sha256

    from aitm_core.cli.plan import run_jit, run_reconcile
    from aitm_core.documents import canonicalize
    from aitm_core.events import core_reducers, fold
    from aitm_core.models.binding import StoryRef
    from aitm_core.models.common import LocalOutcome
    from aitm_core.models.documents import DocumentSchema
    from aitm_core.models.events import EventActor, EventEnvelope
    from aitm_core.models.operations import (
        AuthorityOrigin,
        OperationOwner,
        PreflightOutcome,
        PreflightResult,
        WriteAuthorization,
        story_event_path,
    )
    from aitm_core.planning_evidence import PlanningContext
    from aitm_core.services import ServicePorts
    from aitm_core.store.memory_backend import MemoryBackend

    story = 36
    event_path = story_event_path(story)
    plan_path = ".aitm/stories/000/36/plan/pickup.md"
    plan_bytes = b"---\nschema: aitm.doc/v1\nstory: 36\nrole: plan\n---\n# Pickup\n"
    identity = canonicalize(plan_bytes, DocumentSchema())
    at = "2026-11-28T08:00:00Z"
    digest = sha256()
    events = (
        (
            "graduate",
            "core.story.graduated",
            {
                "kind": "story",
                "source_kind": "draft",
                "source_id": "draft-1",
                "source_digest": PLAN,
                "issue": "example/work#36",
                "initial_state": {
                    "workflow_id": "default",
                    "revision": PLAN,
                    "state_id": "dev",
                    "label": "Develop",
                },
            },
        ),
        (
            "plan",
            "core.doc.accepted",
            {
                "role": "plan",
                "path": plan_path,
                "canonical_version": "aitm.authored-content/v1",
                "canonical_digest": identity.canonical_sha256,
                "raw_digest": identity.raw_sha256,
                "review_refs": ["review-1"],
                "levels": ["sar"],
                "policy_digest": PLAN,
                "source_planning_sha": SOURCE.commit,
                "plan_generation": 1,
            },
        ),
        (
            "start",
            "core.attempt.started",
            {
                "attempt": "a1",
                "generation": 1,
                "allowance_millis": 500,
                "plan_generation": None,
                "source": None,
                "binding": None,
                "provisional": True,
            },
        ),
        (
            "start",
            "core.attempt.clock.changed",
            {
                "attempt": "a1",
                "generation": 1,
                "cause_event_id": "event-3",
                "from": None,
                "to": "active",
                "observed_at": at,
                "used_millis": 0,
            },
        ),
    )
    records = []
    for index, (operation_id, event_type, data) in enumerate(events, 1):
        raw = (
            EventEnvelope(
                v=1,
                id=f"event-{index}",
                ts=at,
                type=event_type,
                story=story,
                actor=EventActor(kind="agent"),
                operation_id=operation_id,
                sequence=index,
                prior_log_digest=digest.hexdigest(),
                data=data,
            )
            .model_dump_json(exclude_none=True)
            .encode()
            + b"\n"
        )
        digest.update(raw)
        records.append(raw)
    log = b"".join(records)

    def preflight(context):
        assert len(context.attempts) == 1
        assert context.operation.category.value == "normal"
        return PreflightResult(outcome=outcome, origin=AuthorityOrigin.FIXTURE)

    store = MemoryBackend(
        {event_path: log, plan_path: plan_bytes},
        ports=ServicePorts(
            write_authorization=lambda *_: WriteAuthorization(
                allowed=True, origin=AuthorityOrigin.FIXTURE
            ),
            attempt_preflight=preflight,
        ),
    )
    before = store.snapshot()
    owner = OperationOwner(actor=EventActor(kind="agent"), binding="b", generation=1)
    request = PlanningContext(
        backend=store,
        snapshot=before,
        owner=owner,
        policy_digest=PLAN,
        operation_id="reconcile-c27",
        at=at,
        publish=store.transact,
        scope=StoryRef(story=story),
        source=SOURCE,
    )
    coverage = Coverage(
        baseline=Baseline(kind="source", snapshot=SOURCE),
        plan_digest=identity.canonical_sha256,
        plan_generation=1,
        attempt="a1",
        attempt_generation=1,
        paths=("src",),
    )
    outcome = PreflightOutcome.PASSED
    jit_context = replace(request, operation_id="jit-c27")
    assert run_jit(jit_context, coverage).local == LocalOutcome.COMPLETED
    before = store.snapshot()
    request = replace(request, snapshot=before)

    outcome = PreflightOutcome.BLOCKED
    assert (
        run_reconcile(request, attempt="a1", generation=1).local == LocalOutcome.REFUSED
    )
    assert store.snapshot() == before

    outcome = PreflightOutcome.PASSED
    assert (
        run_reconcile(request, attempt="a1", generation=1).local
        == LocalOutcome.COMPLETED
    )
    persisted = store.read(store.snapshot(), (event_path,))[event_path]
    final = fold(persisted.splitlines(keepends=True), core_reducers())
    attempt = final.domains["attempts"].attempts["a1"]
    assert attempt.reconciliation.plan_generation == 1
    assert attempt.source == SOURCE
    assert attempt.allowance_millis == 500
    assert len(attempt.clocks) == 1
    jit = final.domains["lifecycle"].jit
    assert jit.baseline_snapshot == SOURCE
    assert jit.coverage_paths == ("src",)
    assert jit.attempt_generation == 1
