"""Exercise operation policy without external processes, repositories or services."""

from dataclasses import replace
from hashlib import sha256
from json import dumps, loads

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.models.evidence import GuardEvaluated
from aitm_core.models.operations import (
    AuthorityOrigin,
    EventAppend,
    OperationCategory,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    story_event_path,
)
from aitm_core.services import UnavailablePort
from aitm_core.store.git_backend import GitBackend
from aitm_core.store.memory_backend import MemoryBackend
from tests.support.c05 import FixtureGate
from tests.unit.test_c04 import (
    BODY,
    POLICY,
    PORTS,
    RELATED,
    attempt_bytes,
    proposal,
    wire,
)
from tests.unit.test_c05 import CommitStore

EVENTS = story_event_path(9)


def unexpected_call(*arguments):
    pytest.fail(f"unexpected authority call with {arguments!r}")


def test_default_category_does_not_borrow_authority_from_another_intent_version():
    backend = MemoryBackend(
        {BODY: b"old"},
        ports=replace(PORTS, write_authorization=unexpected_call),
        categories={("authoring.sync", 1): OperationCategory.AUTHORED_SYNC},
    )
    before = backend.snapshot()
    operation = proposal(
        backend, before, kind="authoring.sync", category=OperationCategory.AUTHORED_SYNC
    )
    operation = operation.model_copy(
        update={"intent": operation.intent.model_copy(update={"version": 2})}
    )
    result = backend.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.REFUSED,
        "operation-category-out-of-scope",
    )
    assert backend.snapshot() == before


def test_normal_tag_cannot_bypass_a_registered_special_category():
    backend = MemoryBackend(
        {BODY: b"old"},
        ports=replace(PORTS, write_authorization=unexpected_call),
        categories={("attempt.recover", 1): OperationCategory.RECOVERY},
    )
    before = backend.snapshot()
    result = backend.transact(proposal(backend, before, kind="attempt.recover"), before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.REFUSED,
        "operation-category-out-of-scope",
    )
    assert backend.snapshot() == before


def test_changed_absence_expectation_conflicts_before_authorization():
    backend = MemoryBackend(
        {BODY: b""}, ports=replace(PORTS, write_authorization=unexpected_call)
    )
    before = backend.snapshot()
    operation = proposal(backend, before)
    operation = operation.model_copy(
        update={
            "change": operation.change.model_copy(
                update={
                    "read_set": tuple(
                        ReadExpectation(path=read.path, digest=None)
                        if read.path == BODY
                        else read
                        for read in operation.change.read_set
                    )
                }
            )
        }
    )
    result = backend.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.CONFLICT,
        "read-set-changed",
    )
    assert backend.read(before, (BODY,)) == {BODY: b""}


def test_attempt_free_operation_does_not_call_configured_preflight():
    backend = MemoryBackend(
        {BODY: b"old"}, ports=replace(PORTS, attempt_preflight=unexpected_call)
    )
    before = backend.snapshot()
    result = backend.transact(proposal(backend, before), before)
    assert result.command.local == LocalOutcome.COMPLETED
    assert result.preflight.outcome == PreflightOutcome.NOT_APPLICABLE


def unbound_authorizer(*_arguments):
    raise UnavailablePort("write_authorization")


@pytest.mark.parametrize(
    "authorizer,reason",
    [
        pytest.param(
            lambda *_: True, "write-authority-unqualified", id="untyped-allow"
        ),
        pytest.param(
            unbound_authorizer,
            "Core service is unavailable: write_authorization",
            id="withdrawn-authority",
        ),
    ],
)
def test_invalid_authorizer_response_does_not_admit_an_operation(authorizer, reason):
    backend = MemoryBackend(
        {BODY: b"old"}, ports=replace(PORTS, write_authorization=authorizer)
    )
    before = backend.snapshot()
    result = backend.transact(proposal(backend, before), before)
    assert (result.command.local, result.reason) == (LocalOutcome.UNAVAILABLE, reason)
    assert result.authorization is None
    assert result.preflight is None
    assert backend.snapshot() == before


def unbound_preflight(_context):
    raise UnavailablePort("attempt_preflight")


@pytest.mark.parametrize(
    "preflight,reason",
    [
        pytest.param(
            lambda _: True, "attempt-preflight-unqualified", id="untyped-pass"
        ),
        pytest.param(
            lambda _: PreflightResult(outcome=PreflightOutcome.NOT_APPLICABLE),
            "attempt-preflight-unqualified",
            id="claimed-inapplicable-for-live-attempt",
        ),
        pytest.param(
            unbound_preflight,
            "Core service is unavailable: attempt_preflight",
            id="withdrawn-preflight",
        ),
        pytest.param(
            lambda _: PreflightResult(
                outcome=PreflightOutcome.UNAVAILABLE, reason="measurement-missing"
            ),
            "measurement-missing",
            id="typed-unavailability",
        ),
    ],
)
def test_live_attempt_requires_qualified_preflight_evidence(preflight, reason):
    backend = MemoryBackend(
        {BODY: b"old", EVENTS: attempt_bytes()},
        ports=replace(PORTS, attempt_preflight=preflight),
    )
    before = backend.snapshot()
    result = backend.transact(proposal(backend, before), before)
    assert (result.command.local, result.reason) == (LocalOutcome.UNAVAILABLE, reason)
    assert result.preflight.outcome == PreflightOutcome.UNAVAILABLE
    assert result.authorization.allowed
    assert backend.snapshot() == before


def test_qualified_preflight_receives_the_exact_pinned_transaction_context():
    seen = []

    def registered(context):
        seen.append(context)
        return PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.REGISTERED
        )

    backend = MemoryBackend(
        {BODY: b"old", EVENTS: attempt_bytes()},
        ports=replace(PORTS, attempt_preflight=registered),
    )
    before = backend.snapshot()
    operation = proposal(backend, before)
    result = backend.transact(operation, before)
    (context,) = seen
    assert result.command.local == LocalOutcome.COMPLETED
    assert result.preflight.origin == AuthorityOrigin.REGISTERED
    assert context.operation == operation and context.snapshot == before
    (attempt,) = context.attempts
    assert attempt.started.attempt == "attempt-9"
    assert attempt.started.binding == "binding-9"


def event_bytes(
    envelope_story=9, operation="update-1", sequence=1, prefix=b"", **fields
):
    return dumps(
        loads(wire(envelope_story, operation, sequence, prefix)) | fields
    ).encode()


def guard_for(operation, /, **fields):
    return GuardEvaluated.model_validate(
        {
            "operation": operation.operation_id,
            "read_set_digest": operation.change.read_set_digest,
            "policy_digest": operation.policy_digest,
            "workflow": {
                "workflow_id": "fixture",
                "revision": POLICY,
                "state_id": "develop",
                "label": "Dev",
            },
            "slot": "source-exit",
            "guard": "fixture.scope",
            "guard_version": "1",
            "ok": True,
            "code": "verified",
            "mode": "enforce",
        }
        | fields
    )


@pytest.mark.parametrize(
    "unbound",
    [
        pytest.param({"operation": "other-operation"}, id="different-operation"),
        pytest.param({"read_set_digest": "b" * 64}, id="different-consulted-evidence"),
        pytest.param({"policy_digest": "b" * 64}, id="different-policy"),
    ],
)
def test_passing_guard_must_bind_current_operation_evidence(unbound):
    backend = MemoryBackend({BODY: b"old"}, ports=PORTS)
    before = backend.snapshot()
    operation = proposal(backend, before)
    operation = operation.model_copy(
        update={"guards": (guard_for(operation, **unbound),)}
    )
    result = backend.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "guard-evidence-mismatch",
    )
    assert not result.guards
    assert backend.snapshot() == before


def test_success_retains_guard_proof_and_verified_pending_work():
    backend = MemoryBackend({BODY: b"old"}, ports=PORTS)
    before = backend.snapshot()
    operation = proposal(backend, before)
    guard = guard_for(operation)
    operation = operation.model_copy(
        update={"guards": (guard,), "pending_actions": ("readback",)}
    )
    result = backend.transact(operation, before)
    assert result.command.local == LocalOutcome.COMPLETED
    assert result.guards == (guard,)
    assert result.command.pending == ("readback",)
    assert backend.transact(operation, before) == result


@pytest.mark.parametrize(
    "fields,reason",
    [
        pytest.param(
            {"story": 10}, "outside the operation's story or identity", id="wrong-story"
        ),
        pytest.param(
            {"operation_id": "foreign"},
            "outside the operation's story or identity",
            id="wrong-operation",
        ),
        pytest.param({"actor": {"kind": "human"}}, "actor disagrees", id="wrong-actor"),
        pytest.param({"policy_digest": "b" * 64}, "policy differs", id="wrong-policy"),
        pytest.param(
            {"read_set_digest": "b" * 64}, "read set differs", id="wrong-read-evidence"
        ),
    ],
)
def test_appended_events_cannot_borrow_transaction_authority(fields, reason):
    backend = MemoryBackend({BODY: b"old", RELATED: b"old-related"}, ports=PORTS)
    before = backend.snapshot()
    row = event_bytes(**fields)
    operation = proposal(
        backend,
        before,
        changes=((RELATED, b"changed"),),
        events=(EventAppend(story=9, records=(row,)),),
    )
    result = backend.transact(operation, before)
    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert reason in result.reason
    assert backend.snapshot() == before
    assert backend.read(before, (EVENTS, RELATED)) == {
        EVENTS: None,
        RELATED: b"old-related",
    }


def test_append_refuses_identity_already_retained_in_event_stream():
    first = event_bytes() + b"\n"
    backend = MemoryBackend({BODY: b"old", EVENTS: first}, ports=PORTS)
    before = backend.snapshot()
    reuse = event_bytes(operation="second", sequence=2, prefix=first, id="9-1")
    result = backend.transact(
        proposal(
            backend, before, "second", events=(EventAppend(story=9, records=(reuse,)),)
        ),
        before,
    )
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "event identity is already present",
    )
    assert backend.read(backend.snapshot(), (EVENTS,)) == {EVENTS: first}


def test_duplicate_event_inside_one_append_batch_refuses_both():
    backend = MemoryBackend({BODY: b"old"}, ports=PORTS)
    before = backend.snapshot()
    first = event_bytes() + b"\n"
    duplicate = event_bytes(sequence=2, prefix=first, id="9-1")
    operation = proposal(
        backend, before, events=(EventAppend(story=9, records=(first, duplicate)),)
    )
    result = backend.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "event identity is already present",
    )
    assert backend.snapshot() == before


def test_existing_stream_bound_to_other_story_refuses_related_writes():
    foreign = event_bytes(envelope_story=10) + b"\n"
    backend = MemoryBackend({BODY: b"old", EVENTS: foreign}, ports=PORTS)
    before = backend.snapshot()
    result = backend.transact(proposal(backend, before), before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "event stream belongs to another story",
    )
    assert backend.read(backend.snapshot(), (BODY, EVENTS)) == {
        BODY: b"old",
        EVENTS: foreign,
    }


def test_reading_a_foreign_snapshot_cannot_disclose_local_blob_bytes():
    first = MemoryBackend({BODY: b"first"}, ports=PORTS)
    second = MemoryBackend({BODY: b"second"}, ports=PORTS)
    with pytest.raises(KeyError):
        first.read(second.snapshot(), (BODY,))


def test_foreign_snapshot_cannot_authorize_memory_write_even_for_identical_trees():
    first = MemoryBackend({BODY: b"same"}, ports=PORTS)
    second = MemoryBackend({BODY: b"same"}, ports=PORTS)
    before = first.snapshot()
    foreign = second.snapshot()
    assert foreign.tree == before.tree
    result = first.transact(proposal(first, before), foreign)
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "unknown-snapshot",
    )
    assert first.snapshot() == before


def test_delete_preserves_old_snapshot_and_is_replayable():
    backend = MemoryBackend({BODY: b"old"}, ports=PORTS)
    before = backend.snapshot()
    operation = proposal(backend, before, changes=((BODY, None),))
    result = backend.transact(operation, before)
    assert result.command.local == LocalOutcome.COMPLETED
    assert backend.read(before, (BODY,)) == {BODY: b"old"}
    assert backend.read(result.snapshot, (BODY,)) == {BODY: None}
    assert backend.transact(operation, before) == result


def test_disabled_authorizer_does_not_record_failure_as_operation_completion():
    def authorizer(owner, change):
        return available(owner, change)

    available = unbound_authorizer
    backend = MemoryBackend(
        {BODY: b"old"}, ports=replace(PORTS, write_authorization=authorizer)
    )
    before = backend.snapshot()
    operation = proposal(backend, before)
    assert backend.transact(operation, before).command.local == LocalOutcome.UNAVAILABLE
    assert backend.snapshot() == before

    available = PORTS.write_authorization
    assert backend.transact(operation, before).command.local == LocalOutcome.COMPLETED


def test_git_backend_refuses_store_owned_record_destinations():
    repository = CommitStore({})
    gate = FixtureGate()
    backend = GitBackend(repository, gate, ports=PORTS)
    before = backend.snapshot()
    operation = proposal(
        backend, before, changes=((".aitm/operations/forged.json", b"fake"),)
    )
    result = backend.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "operation records are owned by the store",
    )
    assert backend.snapshot() == before
    assert gate.observed == [(before, None)]
    assert set(repository.commits) == {before.revision}


@pytest.mark.parametrize(
    "bad_record",
    [
        pytest.param(b"{broken-json", id="unparseable-record"),
        pytest.param(b"{}", id="unbound-record"),
    ],
)
def test_git_backend_does_not_overwrite_unreadable_operation_record(bad_record):
    path = f".aitm/operations/{sha256(b'update-1').hexdigest()}.json"
    repository = CommitStore({BODY: b"old", path: bad_record})
    gate = FixtureGate()
    backend = GitBackend(repository, gate, ports=PORTS)
    before = backend.snapshot()
    operation = proposal(backend, before)
    result = backend.transact(operation, before)
    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert result.command.pending == ()
    assert backend.read(before, (BODY, path)) == {BODY: b"old", path: bad_record}
    assert gate.observed == [(before, None)]
    assert backend.snapshot() == before


def test_git_backend_does_not_replay_record_when_parent_evidence_disagrees():
    repository = CommitStore({BODY: b"old"})
    backend = GitBackend(repository, FixtureGate(), ports=PORTS)
    before = backend.snapshot()
    operation = proposal(backend, before)
    result = backend.transact(operation, before)
    assert result.command.local == LocalOutcome.COMPLETED
    repository.parents[result.snapshot.revision] = "unrelated"
    recovered = backend.transact(operation, before)
    assert (recovered.command.local, recovered.reason) == (
        LocalOutcome.INTEGRITY_ERROR,
        "operation record does not match its commit parent",
    )
    assert recovered.snapshot == result.snapshot


def test_git_backend_queries_no_objects_after_mandatory_gate_refusal(monkeypatch):
    def refused_gate(repository, target):
        assert target == repository.ref
        raise OSError("lock unavailable")

    repository = CommitStore({BODY: b"old"})
    allowed = GitBackend(repository, FixtureGate(), ports=PORTS)
    before = allowed.snapshot()
    operation = proposal(allowed, before)
    for operation_name in ("tip", "read_tree", "read_blobs", "create_commit"):
        monkeypatch.setattr(repository, operation_name, unexpected_call)
    blocked = GitBackend(repository, refused_gate, ports=PORTS)
    result = blocked.transact(operation, before)
    assert (result.command.local, result.reason) == (
        LocalOutcome.UNAVAILABLE,
        "lock unavailable",
    )
    assert repository.current == before
