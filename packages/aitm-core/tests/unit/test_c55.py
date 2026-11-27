"""Exercise C55 through typed causal envelopes and pure reduction fixtures."""

from hashlib import sha256
from itertools import groupby
from json import dumps

import pytest

from aitm_core.events import ReducerRegistry, StoryState, fold
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.events import EnvelopeError, validate_envelope
from aitm_core.reducers.attempts import (
    AttemptIntegrityError,
    attempt_schemas,
    fold_attempt,
    validate_boundary_batch,
)

TIME = "2026-11-27T08:00:00Z"
SOURCE = {"commit": "a" * 40, "tree": "b" * 40}
START = (
    "core.attempt.started",
    {
        "attempt": "a1",
        "generation": 1,
        "plan_generation": 2,
        "source": SOURCE,
        "binding": "binding-1",
        "allowance_millis": 60000,
    },
)
AUTHORITY = {
    "purpose": "evidence",
    "authority_id": "recovery-1",
    "attempt": "a1",
    "ended_generation": 1,
    "source": SOURCE,
    "allowed": [
        "managed-verification",
        "review-observation",
        "proof-reconciliation",
        "signoff",
    ],
}


def fact(kind, generation=1, **data):
    return kind, {"attempt": "a1", "generation": generation, **data}


def clock(cause, before, after, used=0, generation=1, **changes):
    return fact(
        "core.attempt.clock.changed",
        generation,
        **{
            "cause_event_id": cause,
            "from": before,
            "to": after,
            "observed_at": TIME,
            "used_millis": used,
            **changes,
        },
    )


def records(*batches):
    result = []
    digest = sha256()
    for op, batch in enumerate(batches, 1):
        for kind, data in batch:
            number = len(result) + 1
            raw = dumps(
                {
                    "v": 1,
                    "id": f"e{number}",
                    "ts": TIME,
                    "type": kind,
                    "story": 7,
                    "actor": {"kind": "agent"},
                    "operation_id": f"op{op}",
                    "sequence": number,
                    "prior_log_digest": digest.hexdigest(),
                    "data": data,
                }
            ).encode()
            result.append(validate_envelope(raw))
            digest.update(raw + b"\n")
    return result


def replay(*batches):
    registry = ReducerRegistry()
    for event_type in (*attempt_schemas(), "core.session.started"):
        registry.register(event_type, fold_attempt)
    for event_type in (
        "core.expansion.reserved",
        "core.expansion.reservation-resolved",
        "core.expansion.resolved",
        "core.review.recorded",
        "core.review.activated",
    ):
        registry.register(event_type, lambda state, event: state)
    events = records(*batches)
    for _, batch in groupby(events, lambda event: event.operation_id):
        validate_boundary_batch(batch)
    return fold(events, registry).domains["attempts"].attempts["a1"]


def start_clock():
    return START, clock("e1", None, "active")


def test_clock_event_has_one_explicit_four_segment_wire_name():
    started, boundary = records(start_clock())
    assert started.type == "core.attempt.started"
    assert boundary.type == "core.attempt.clock.changed"
    assert boundary.namespace == "core"
    state = fold_attempt(fold_attempt(StoryState(), started), boundary)
    assert state.domains["attempts"].attempts["a1"].clock_mode == "active"
    for kind in (
        "vendor.attempt.clock.changed",
        "core.attempt.clock.other",
        "core.attempt.clock.changed.extra",
        "core.attempt.Clock.changed",
        "prefix.core.attempt.clock.changed",
    ):
        with pytest.raises(EnvelopeError):
            records([(kind, {})])


def test_standalone_fold_keeps_attempts_in_the_same_story():
    (started,) = records([START])
    state = fold_attempt(StoryState(), started)
    foreign = validate_envelope(
        started.raw_record.replace(b'"story": 7', b'"story": 8')
    )
    with pytest.raises(AttemptIntegrityError, match="another story"):
        fold_attempt(state, foreign)


def execution(phase, **data):
    fields = {
        "execution_id": "exec-1",
        "request_id": "req-1",
        "action_key": "verify",
        "executor": "runner-1",
        "authority_store": "planning",
        "authority_ref": "refs/heads/planning",
        "expected_prior_version": "c" * 40,
        "admission_commit": "d" * 40 if phase not in {"prepared", "admitted"} else None,
        "outcome": phase if phase in {"finished", "uncertain"} else None,
        "source": SOURCE,
        "phase": phase,
    }
    return fact(
        "core.execution.recorded",
        **{**fields, **data},
    )


@pytest.mark.parametrize(
    "phases",
    [
        ("prepared",),
        ("prepared", "admitted"),
        ("prepared", "admitted", "started"),
        ("prepared", "admitted", "started", "cancel-requested"),
        ("prepared", "admitted", "started", "cancel-requested", "finished"),
        ("prepared", "admitted", "started", "uncertain"),
    ],
)
def test_attempt_reducers_keep_execution_phases_distinct(phases):
    batches = [
        [
            execution(
                phase,
                proof="proof-1"
                if phase in {"admitted", "finished", "uncertain"}
                else None,
            )
        ]
        for phase in phases
    ]
    result = replay(start_clock(), *batches)
    assert [entry.phase for entry in result.executions["exec-1"]] == list(phases)
    with pytest.raises(AttemptIntegrityError, match="execution phase"):
        replay(start_clock(), [execution("started")])


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"admission_commit": None}, "admission commit"),
        ({"authority_ref": "refs/heads/other"}, "authority"),
    ],
)
def test_execution_requires_the_same_authority_and_retained_admission(changes, error):
    with pytest.raises(AttemptIntegrityError, match=error):
        replay(
            start_clock(),
            [execution("prepared")],
            [execution("admitted", proof="admitted-proof")],
            [execution("started", **changes)],
        )


def test_no_child_resolution_and_effective_review_replay():
    reservation = [
        fact("core.expansion.reserved"),
        clock("e3", "active", "expansion-paused", 10),
    ]
    linked = [fact("core.expansion.reservation-resolved", disposition="linked")]
    no_child = [
        fact("core.expansion.reservation-resolved", disposition="no-child"),
        clock("e5", "expansion-paused", "active", 10),
    ]
    assert replay(start_clock(), reservation, linked).clock_mode == "expansion-paused"
    child = [
        fact("core.expansion.resolved"),
        clock("e6", "expansion-paused", "active", 10),
    ]
    assert replay(start_clock(), reservation, linked, child).clock_mode == "active"
    recorded = [fact("core.review.recorded")]
    assert replay(start_clock(), reservation, no_child, recorded).clock_mode == "active"
    active = [
        fact("core.review.activated"),
        clock("e8", "active", "review-stopped", 28),
    ]
    result = replay(start_clock(), reservation, no_child, recorded, active)
    assert result.clock_mode == "review-stopped" and result.used_millis == 28


@pytest.mark.parametrize("needs_verification", [False, True])
def test_recovery_binding_fences_ended_generation_and_keeps_allowance(
    needs_verification,
):
    closed = [
        fact(
            "core.attempt.closed",
            from_clock="active",
            disposition="unverified",
            reason="missing proof",
        ),
        clock("e3", "active", "terminal-closed", 100),
    ]
    reopened = [
        fact(
            "core.attempt.reopened",
            source=SOURCE,
            allowance_millis=60000,
            closure_reason="missing proof",
            authority=AUTHORITY,
        )
    ]
    pending = replay(start_clock(), closed, reopened)
    assert pending.generation == 1 and pending.clock_mode == "terminal-closed"
    assert pending.recovery.purpose == BindingPurpose.EVIDENCE
    binding = [
        fact(
            "core.session.started",
            generation=2,
            purpose="evidence",
            authority_id="recovery-1",
            binding="binding-2",
            source=SOURCE,
            needs_verification=needs_verification,
        )
    ]
    if needs_verification:
        binding.append(clock("e6", "terminal-closed", "active", 100, generation=2))
    resumed = replay(start_clock(), closed, reopened, binding)
    assert resumed.generation == 2 and resumed.allowance_millis == 60000
    assert resumed.used_millis == 100 and len(resumed.closures) == 1
    assert resumed.clock_mode == ("active" if needs_verification else "terminal-closed")
    with pytest.raises(AttemptIntegrityError, match="generation"):
        replay(start_clock(), closed, reopened, binding, [execution("prepared")])
    with pytest.raises(AttemptIntegrityError, match="allowance"):
        replay(
            start_clock(),
            closed,
            [
                fact(
                    "core.attempt.reopened",
                    source=SOURCE,
                    allowance_millis=120000,
                    closure_reason="missing proof",
                    authority=AUTHORITY,
                )
            ],
        )


@pytest.mark.parametrize(
    "batch",
    [
        [START],
        [clock("e99", None, "active")],
        [START, clock("e1", None, "active"), clock("e1", None, "active")],
        [START, clock("e1", None, "active", generation=2)],
        [START, clock("e1", None, "active", attempt="different")],
        [START, clock("e1", "terminal-closed", "active")],
        [START, clock("e1", None, "review-stopped")],
        [START, clock("e1", None, "active", observed_at="2026-11-27T08:01:00Z")],
        [START, clock("e1", None, "active", used=-1)],
    ],
)
def test_boundary_batch_rejects_missing_or_conflicting_causal_pairs(batch):
    with pytest.raises(AttemptIntegrityError):
        validate_boundary_batch(records(batch))


def test_boundary_cannot_reset_accumulated_usage_or_move_for_raw_verdict():
    with pytest.raises(AttemptIntegrityError, match="usage"):
        replay(
            start_clock(),
            [
                fact("core.expansion.reserved"),
                clock("e3", "active", "expansion-paused", 20),
            ],
            [
                fact("core.expansion.resolved"),
                clock("e5", "expansion-paused", "active", 10),
            ],
        )
    with pytest.raises(AttemptIntegrityError, match="causal"):
        validate_boundary_batch(
            records(
                [fact("core.review.recorded"), clock("e1", "active", "review-stopped")]
            )
        )
