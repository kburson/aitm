"""Kind applicability and terminal transactions share the configured engine."""

from dataclasses import replace
from json import loads

import pytest

from aitm_core.dispositions import DispositionRequest, dispose
from aitm_core.machine.guards import GuardDecision
from aitm_core.machine.kinds import kind_requirements
from aitm_core.machine.transitions import transition
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.common import LocalOutcome
from tests.unit.test_c28_transitions import PATH
from tests.unit.test_c28_transitions import context as context
from tests.unit.test_c71_split import replay, seeded


@pytest.mark.parametrize(
    ("kind", "purpose", "attempt", "evidence"),
    [
        ("story", BindingPurpose.IMPLEMENTATION, True, "source"),
        ("defect", BindingPurpose.IMPLEMENTATION, True, "source"),
        ("spike", BindingPurpose.DELIVERABLE, True, "deliverable"),
        ("epic", None, False, "aggregate"),
    ],
)
def test_typed_kind_matrix(kind, purpose, attempt, evidence):
    result = kind_requirements(kind, "implementation")
    assert (result.binding, result.attempt, result.evidence) == (
        purpose,
        attempt,
        evidence,
    )


def test_epic_uses_qualified_plan_entry_without_implementation_binding_or_clock(
    context,
):
    request = seeded(context, initial="plan", kind="epic")
    answer = transition(
        replace(
            request, guard=lambda call: GuardDecision("pass", "qualified-epic-plan")
        )
    )
    assert answer.command.local == LocalOutcome.COMPLETED, answer.reason
    raw = request.backend.read(request.backend.snapshot(), (PATH,))[PATH]
    assert "core.attempt.started" not in raw.decode()
    assert replay(request).workflow_state.state_id == "dev"


@pytest.mark.parametrize("disposition", ["abandoned", "superseded", "duplicate"])
def test_nondelivery_requires_reason_and_applicable_replacement_then_uses_typed_terminal(
    context, disposition
):
    original = seeded(context)
    blank = dispose(DispositionRequest(original, disposition, " "))
    assert blank.command.local == LocalOutcome.REFUSED
    if disposition != "abandoned":
        absent = dispose(
            DispositionRequest(original, disposition, "Exact reason", replacement=2)
        )
        assert absent.command.local == LocalOutcome.REFUSED
        self_reference = dispose(
            DispositionRequest(
                original, disposition, "Invalid replacement", replacement=1
            )
        )
        assert self_reference.command.local == LocalOutcome.REFUSED
    else:
        landed = dispose(DispositionRequest(original, disposition, "Project cancelled"))
        assert landed.command.local == LocalOutcome.COMPLETED, landed.reason
        last = replay(original).transitions[-1]
        assert last.disposition == "abandoned" and last.to_state.state_id == "complete"
        stored = original.backend.read(original.backend.snapshot(), (PATH,))[PATH]
        assert loads(stored.splitlines()[-1])["type"] == "core.state.changed"


def test_unverified_terminal_is_explicit_and_requires_advisory(context):
    request = seeded(context, initial="review")
    enforced = dispose(DispositionRequest(request, "unverified", "Insufficient proof"))
    assert enforced.command.local == LocalOutcome.REFUSED
    admitted = dispose(
        DispositionRequest(
            replace(request, mode="advisory"), "unverified", "Insufficient proof"
        )
    )
    assert admitted.command.local == LocalOutcome.COMPLETED, admitted.reason
    assert replay(request).transitions[-1].disposition == "unverified"


def test_spike_uses_current_deliverable_validation_review_and_archive(context):
    from hashlib import sha256

    from aitm_core.events import core_reducers, fold
    from aitm_core.machine.guards import GuardCall
    from aitm_core.machine.kinds import evaluate_kind_guard
    from tests.unit.test_c28_transitions import NOW
    from tests.unit.test_c71_split import append_events

    request = seeded(context, initial="dev", kind="spike")
    snapshot = request.backend.snapshot()
    raw = request.backend.read(snapshot, (PATH,))[PATH]
    source = {"commit": "a" * 40, "tree": "b" * 40}
    resource = {"attempt": "spike-attempt", "generation": 1}
    document = b"Qualified research outcome.\n"
    path = ".aitm/stories/000/1/attachments/research.md"
    digest = sha256(document).hexdigest()
    raw = append_events(
        raw,
        request.owner,
        1,
        "spike-start",
        [
            (
                "core.attempt.started",
                resource
                | {
                    "plan_generation": 1,
                    "binding": "b",
                    "allowance_millis": 5000,
                    "provisional": False,
                    "source": source,
                },
            ),
            (
                "core.attempt.clock.changed",
                resource
                | {
                    "cause_event_id": "spike-start:1",
                    "from": None,
                    "to": "active",
                    "observed_at": NOW,
                    "used_millis": 0,
                },
            ),
            (
                "core.deliverable.added",
                {
                    "deliverable_id": "study",
                    "path": path,
                    "raw_digest": digest,
                    "canonical_digest": digest,
                    "attempt": resource["attempt"],
                    "source_snapshot": source["commit"],
                },
            ),
        ],
        policy=request.policy_digest,
    )
    validation = resource | {
        "deliverable_id": "study",
        "deliverable_digest": digest,
        "input_baseline": source["commit"],
        "check_policy": request.policy_digest,
        "result": "pass",
        "proof_refs": [digest],
    }
    raw = append_events(
        raw,
        request.owner,
        1,
        "validate-spike",
        [
            ("core.deliverable.validated", validation),
        ],
    )

    def check(name, body=raw, content=document):
        replay = fold(body.splitlines(keepends=True), core_reducers())
        return evaluate_kind_guard(
            GuardCall(
                name,
                1,
                "onExit",
                snapshot,
                replay.domains["lifecycle"],
                request.profile.ordinary_edges[-1],
                {PATH: body, path: content},
                request.policy_digest,
            ),
            source=None,
            aggregate=None,
        )

    candidate = "core.dev.review-candidate-current"
    closeout = "core.closeout.complete"
    assert check(candidate).status == "pass"
    assert check(candidate, content=b"Changed").code == "deliverable-content-drifted"
    assert check(closeout).code == "current-deliverable-review-unavailable"

    review = resource | {
        "review_id": "accepted-study",
        "source": source,
        "proof_refs": [digest],
    }
    reviewed = append_events(
        raw,
        request.owner,
        1,
        "review-spike",
        [
            (
                "core.review.recorded",
                review | {"verdict": "pass", "reviewer_ref": "independent"},
            ),
            (
                "core.review.activated",
                review
                | {"policy_digest": request.policy_digest, "reason": "Accepted scope"},
            ),
            (
                "core.attempt.clock.changed",
                resource
                | {
                    "cause_event_id": "review-spike:2",
                    "from": "active",
                    "to": "review-stopped",
                    "observed_at": NOW,
                    "used_millis": 0,
                },
            ),
        ],
    )
    assert check(closeout, reviewed).code == "deliverable-archive-unavailable"
    archived = append_events(
        reviewed,
        request.owner,
        1,
        "archive-spike",
        [
            (
                "core.delivery.verified",
                resource
                | {
                    "source": None,
                    "deliverable_digest": digest,
                    "target": "archive",
                    "result_ref": "artifact:study",
                    "result_digest": digest,
                    "method": "retained-archive",
                    "proof_refs": [digest],
                },
            ),
        ],
        policy=request.policy_digest,
    )
    assert check(closeout, archived).code == "deliverable-archive-current"


def test_terminal_closure_keeps_attempt_fence_and_clock_atomic(context):
    from aitm_core.events import core_reducers, fold
    from aitm_core.models.operations import (
        AuthorityOrigin,
        PreflightOutcome,
        PreflightResult,
        WriteAuthorization,
    )
    from aitm_core.services import ServicePorts
    from aitm_core.store.memory_backend import MemoryBackend
    from tests.unit.test_c28_transitions import NOW
    from tests.unit.test_c71_split import append_events, with_history

    request = seeded(context, initial="dev")
    base = request.backend.read(request.backend.snapshot(), (PATH,))[PATH]
    identity = {"attempt": "in-flight", "generation": 1}
    started = append_events(
        base,
        request.owner,
        1,
        "attempt-start",
        [
            (
                "core.attempt.started",
                identity
                | {
                    "plan_generation": None,
                    "source": None,
                    "binding": None,
                    "allowance_millis": 1000,
                    "provisional": True,
                },
            ),
            (
                "core.attempt.clock.changed",
                identity
                | {
                    "cause_event_id": "attempt-start:1",
                    "from": None,
                    "to": "active",
                    "observed_at": NOW,
                    "used_millis": 0,
                },
            ),
        ],
    )
    without_port = with_history(request, started)
    denied = dispose(DispositionRequest(without_port, "abandoned", "Close open work"))
    assert denied.command.local == LocalOutcome.UNAVAILABLE
    assert replay(without_port).workflow_state.state_id == "dev"
    ports = ServicePorts(
        write_authorization=lambda owner, change: WriteAuthorization(
            allowed=True,
            origin=AuthorityOrigin.REGISTERED,
        ),
        attempt_preflight=lambda call: PreflightResult(
            outcome=PreflightOutcome.PASSED,
            origin=AuthorityOrigin.FIXTURE,
        ),
    )
    qualified = replace(request, backend=MemoryBackend({PATH: started}, ports=ports))
    outcome = dispose(DispositionRequest(qualified, "abandoned", "Close open work"))
    assert outcome.command.local == LocalOutcome.COMPLETED, outcome.reason
    data = qualified.backend.read(outcome.snapshot, (PATH,))[PATH]
    observed = fold(data.splitlines(keepends=True), core_reducers())
    attempt = observed.domains["attempts"].attempts["in-flight"]
    assert attempt.closed and attempt.clock_mode == "terminal-closed"
    assert len(attempt.clocks) == 2 and attempt.closures[-1].disposition == "abandoned"
    assert observed.domains["lifecycle"].transitions[-1].disposition == "abandoned"
