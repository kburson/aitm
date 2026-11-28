"""C28 exercises the transition service through the pinned CAS contract."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from aitm_core.events import EMPTY_LOG_DIGEST, core_reducers, fold
from aitm_core.ext.api import CapabilitySlot
from aitm_core.ext.registry import load_extensions
from aitm_core.machine.guards import GuardDecision
from aitm_core.machine.profile import WorkflowProfile
from aitm_core.machine.transitions import TransitionRequest, explain, transition
from aitm_core.models.common import LocalOutcome
from aitm_core.models.events import EventActor, EventEnvelope
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
)
from aitm_core.services import ServicePorts
from aitm_core.store.memory_backend import MemoryBackend
from tests.unit.test_c91 import BINDING, CANDIDATE, CLOSEOUT, PICKUP, TERMINAL, document

PATH = ".aitm/stories/000/1/events.jsonl"
NOW = "2026-11-28T08:00:00+00:00"


@pytest.fixture
def context():
    raw = document()
    raw["states"][3]["action"] = []
    raw["edges"].pop(1)
    profile = WorkflowProfile.model_validate(raw)
    state = {
        "workflow_id": profile.id,
        "revision": profile.source.digest,
        "state_id": "plan",
        "label": "Prepare",
    }
    owner = OperationOwner(
        actor=EventActor(kind="tool", harness="test"), binding="b", generation=1
    )
    history = (
        EventEnvelope(
            v=1,
            id="initial",
            ts=NOW,
            type="core.story.graduated",
            story=1,
            actor=owner.actor,
            operation_id="initial",
            sequence=1,
            prior_log_digest=EMPTY_LOG_DIGEST,
            data={
                "kind": "story",
                "source_kind": "draft",
                "source_id": "fixture",
                "source_digest": "a" * 64,
                "issue": "local:1",
                "delivery_target": {
                    "repository": "destination",
                    "ref": "refs/heads/trunk",
                },
                "initial_state": state,
            },
        )
        .model_dump_json(exclude_none=True)
        .encode()
        + b"\n"
    )
    ports = ServicePorts(
        write_authorization=lambda owner, change: WriteAuthorization(
            allowed=True, origin=AuthorityOrigin.REGISTERED
        )
    )
    backend = MemoryBackend({PATH: history}, ports=ports)
    registry = load_extensions(
        SimpleNamespace(config=SimpleNamespace(extensions=SimpleNamespace(enabled=()))),
        builtins=[
            CapabilitySlot(
                id=rule, version=1, kind="guard", placements=("onEnter", "onExit")
            )
            for rule in (PICKUP, BINDING, CANDIDATE, CLOSEOUT, TERMINAL)
        ],
    )
    return TransitionRequest(
        story=1,
        operation_id="test-transition",
        owner=owner,
        at=NOW,
        backend=backend,
        profile=profile,
        registry=registry,
        policy_digest="e" * 64,
        mode="enforce",
        guard=lambda call: GuardDecision("blocked", "unbound"),
        allowance_millis=1000,
    )


def replay(request):
    raw = request.backend.read(request.backend.snapshot(), (PATH,))[PATH]
    return fold(raw.splitlines(keepends=True), core_reducers())


def test_explain_and_enforce_share_guard_evaluation(context):
    details = explain(context)
    assert details.source == "plan" and details.target == "dev"
    assert [(guard.slot, guard.guard) for guard in details.guards] == [
        ("onExit", PICKUP),
        ("onEnter", BINDING),
    ]
    assert all(not guard.ok for guard in details.guards)
    assert transition(context).command.local == LocalOutcome.REFUSED
    assert replay(context).domains["lifecycle"].workflow_state.state_id == "plan"
    assert "attempts" not in replay(context).domains


def test_advisory_advances_with_one_atomic_provisional_attempt_and_clock(context):
    request = replace(context, mode="advisory")
    result = transition(request)
    assert result.command.local == LocalOutcome.COMPLETED, result.reason
    state = replay(request)
    assert state.domains["lifecycle"].workflow_state.state_id == "dev"
    attempts = state.domains["attempts"]
    current = attempts.attempts[attempts.current_attempt]
    assert current.started.provisional and current.clock_mode == "active"
    assert len(current.clocks) == 1
    guard_events = state.domains["evidence"].facts["core.guard.evaluated"]
    assert len(guard_events) == 2
    assert all(not event.payload.ok for event in guard_events)
    assert transition(request).command.local == LocalOutcome.COMPLETED
    assert len(replay(request).domains["attempts"].attempts) == 1


def test_illegal_edge_and_missing_hard_prepare_remain_refused_in_advisory(context):
    result = transition(replace(context, mode="advisory", target="complete"))
    assert result.command.local == LocalOutcome.REFUSED
    assert replay(context).domains["lifecycle"].workflow_state.state_id == "plan"


def test_conflict_repins_and_reevaluates(context):
    calls = []
    original = context.backend.transact

    def guard(call):
        calls.append((call.snapshot.revision, call.identifier))
        return GuardDecision("blocked", "unbound")

    def transact(operation, snapshot):
        if len(calls) == 2:
            return replace(
                original(
                    operation.model_copy(
                        update={"operation_id": "interference", "guards": ()}
                    ),
                    snapshot,
                ),
                command=SimpleNamespace(local=LocalOutcome.CONFLICT),
            )
        return original(operation, snapshot)

    # Reuse the backend's operation receipt to advance the snapshot without a state write.
    context.backend.transact = transact
    result = transition(replace(context, guard=guard))
    assert result.command.local == LocalOutcome.REFUSED
    assert [rule for _, rule in calls] == [PICKUP, BINDING, PICKUP, BINDING]


def test_phase_order_repins_after_authored_sync(context):
    trace = []

    def phase(name):
        trace.append(name)
        return None

    request = replace(
        context,
        before_sync=lambda: phase("preflight"),
        sync=lambda: phase("sync"),
        guard=lambda call: (
            trace.append(call.identifier) or GuardDecision("blocked", "hold")
        ),
    )
    assert transition(request).command.local == LocalOutcome.REFUSED
    assert trace == ["preflight", "sync", PICKUP, BINDING]


@pytest.mark.parametrize("stale", [None, "target", "identity", "attempt", "snapshot"])
def test_exact_pickup_proof_can_supply_child_generation_and_pinned_related_reads(
    context, stale
):
    from aitm_core.machine.guards import ImplementationBinding
    from aitm_core.models.attempts import SourceSnapshot
    from aitm_core.models.operations import ReadExpectation

    source = SourceSnapshot(commit="a" * 40, tree="b" * 40)
    absence = ReadExpectation(path=".aitm/stories/000/2/events.jsonl", digest=None)

    def guard(call):
        if call.identifier == PICKUP:
            return GuardDecision(
                "pass",
                "jit-current",
                reads=(absence,),
                plan_generation=2,
                source=source,
            )
        proof = ImplementationBinding(
            snapshot=call.snapshot,
            story=call.story.story_id,
            identity=context.owner.binding,
            generation=context.owner.generation,
            branch="refs/heads/story/one",
            source=source,
            target=call.story.graduation.delivery_target,
            attempt="prepared-attempt",
        )
        obsolete = {
            "target": replace(
                proof,
                target=proof.target.model_copy(update={"ref": "refs/heads/stale"}),
            ),
            "identity": replace(proof, identity="retired-lease"),
            "attempt": replace(proof, attempt="retired-attempt"),
            "snapshot": replace(
                proof, snapshot=replace(proof.snapshot, revision="stale")
            ),
        }
        return GuardDecision("pass", "bound", binding=obsolete.get(stale, proof))

    candidate = replace(
        context,
        guard=guard,
        binding_ref="refs/heads/story/one",
        binding_attempt="prepared-attempt",
        source=source,
    )
    result = transition(candidate)
    if stale is not None:
        assert result.command.local == LocalOutcome.REFUSED
        assert any(
            guard.code.endswith("implementation-binding-unqualified")
            for guard in result.guards
        )
        assert "attempts" not in replay(candidate).domains
        return
    assert result.command.local == LocalOutcome.COMPLETED, result.reason
    state = replay(candidate)
    attempts = state.domains["attempts"]
    attempt = attempts.attempts[attempts.current_attempt]
    assert not attempt.started.provisional
    assert attempt.started.plan_generation == 2 and attempt.source == source
    assert attempt.started.attempt == "prepared-attempt"
    assert len({item.read_set_digest for item in result.guards}) == 1


def test_mismatched_related_evidence_is_an_integrity_error_even_in_advisory(context):
    from aitm_core.models.operations import ReadExpectation

    absent = ReadExpectation(path=".aitm/stories/000/2/events.jsonl", digest="a" * 64)
    request = replace(
        context,
        mode="advisory",
        guard=lambda call: GuardDecision("pass", "claimed", reads=(absent,)),
    )
    result = transition(request)
    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert "pinned evidence" in result.reason
    assert replay(request).domains["lifecycle"].workflow_state.state_id == "plan"


def test_missing_transition_preparation_never_becomes_advisory_authority(context):
    raw = document()
    raw["states"][3]["action"] = []
    raw["edges"].pop(1)
    raw["edges"][0]["prepare"] = ["core.dev.prepare-binding"]
    request = replace(
        context, mode="advisory", profile=WorkflowProfile.model_validate(raw)
    )
    result = transition(request)
    assert result.command.local == LocalOutcome.UNAVAILABLE
    assert any(guard.slot == "prepare" for guard in result.guards)
    assert "attempts" not in replay(request).domains


def test_plan_admission_checks_current_design_refinement_and_selected_capacity(context):
    from aitm_core.documents import canonicalize
    from aitm_core.machine.guards import GuardCall, core_guard
    from aitm_core.models.documents import DocumentSchema
    from aitm_core.models.lifecycle import DocumentAcceptance, Estimate

    story = replay(context).domains["lifecycle"]
    raw = (
        b'---\n{"schema":"aitm.doc/v1","story":1,"role":"design","title":"Approved"}'
        b"\n---\nApproved project design.\n"
    )
    path = ".aitm/stories/000/1/design/current.md"
    document_hash = canonicalize(raw, DocumentSchema())
    design = DocumentAcceptance(
        role="design",
        path=path,
        canonical_version="aitm.authored-content/v1",
        canonical_digest=document_hash.canonical_sha256,
        raw_digest=document_hash.raw_sha256,
        review_refs=("review",),
        levels=("xpr",),
        policy_digest=context.policy_digest,
        source_planning_sha="a" * 40,
        plan_generation=1,
    )
    basic = GuardCall(
        "core.plan.admission-ready",
        1,
        "onEnter",
        context.backend.snapshot(),
        story,
        context.profile.ordinary_edges[0],
        {path: raw},
        context.policy_digest,
    )

    def good(call):
        return GuardDecision("pass", "kind-qualified")

    def evaluate(call, capacity=None):
        return core_guard(
            call,
            leaf_hours=4,
            kind_requirements=good,
            story_exit_guards=None,
            planning_capacity=capacity,
        )

    assert evaluate(basic).code == "design-acceptance"
    with_design = story.model_copy(update={"accepted_documents": {"design": design}})
    assert evaluate(replace(basic, story=with_design)).code == "refinement"
    priority_missing = Estimate.model_construct(
        phase="refine", agent_hours=4, size="S", priority=""
    )
    missing = with_design.model_copy(update={"estimates": {"refine": priority_missing}})
    assert evaluate(replace(basic, story=missing)).code == "refinement"
    estimate = Estimate(phase="refine", agent_hours=4.0, size="S", priority="P1")
    current = with_design.model_copy(update={"estimates": {"refine": estimate}})
    eligible = replace(basic, story=current)
    assert evaluate(eligible).status == "pass"
    assert (
        evaluate(
            replace(
                eligible,
                blobs={
                    path: raw.replace(b"Approved project design", b"Changed design")
                },
            )
        ).status
        == "blocked"
    )
    selected = replace(eligible, identifier="core.plan.capacity-current")
    assert evaluate(selected).status == "unavailable"
    assert (
        evaluate(selected, lambda call: GuardDecision("blocked", "pool-full")).code
        == "pool-full"
    )
