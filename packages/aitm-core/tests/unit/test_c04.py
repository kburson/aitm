"""Exercise the installed backend contract with explicit fixture services."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
from json import dumps

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.evidence import GuardEvaluated
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.services import ServicePorts
from aitm_core.store.memory_backend import MemoryBackend

STAMP = "2026-11-27T12:00:00Z"
OWNER = OperationOwner(
    actor=EventActor(kind="agent", harness="fixture"), binding="binding-9", generation=1
)
POLICY = "a" * 64
BODY = ".aitm/stories/000/9/story.md"
RELATED = ".aitm/stories/000/10/story.md"


def allow_fixture(owner, change):
    assert owner == OWNER
    assert isinstance(change, RelatedWriteSet)
    return WriteAuthorization(allowed=True, origin=AuthorityOrigin.FIXTURE)


PORTS = ServicePorts(write_authorization=allow_fixture)


def wire(
    story, operation_id, sequence, before=b"", kind="fixture.note.appended", data=None
):
    return dumps(
        {
            "v": 1,
            "id": f"{story}-{sequence}",
            "ts": STAMP,
            "type": kind,
            "story": story,
            "actor": OWNER.actor.model_dump(exclude_none=True),
            "operation_id": operation_id,
            "sequence": sequence,
            "prior_log_digest": sha256(before).hexdigest(),
            "data": data or {},
        }
    ).encode()


def proposal(
    backend,
    snapshot,
    operation_id="update-1",
    *,
    changes=((BODY, b"new"),),
    events=(),
    kind="story.update",
    category=OperationCategory.NORMAL,
):
    paths = {p for p, _ in changes}
    paths.update(e.path for e in events)
    for path in tuple(paths):
        if path.startswith(".aitm/stories/"):
            story = int(path.split("/")[3])
            paths.add(story_event_path(story))
    blobs = backend.read(snapshot, sorted(paths))
    read_set = tuple(
        ReadExpectation(
            path=path, digest=sha256(blob).hexdigest() if blob is not None else None
        )
        for path, blob in blobs.items()
    )
    return Operation(
        operation_id=operation_id,
        owner=OWNER,
        policy_digest=POLICY,
        category=category,
        intent=FinalizationIntent(
            kind=kind, version=1, related_preconditions=(), payload=b"{}"
        ),
        change=RelatedWriteSet(
            read_set=read_set,
            writes=tuple(
                BlobWrite(path=path, content=content) for path, content in changes
            ),
            events=events,
        ),
    )


@pytest.fixture
def backend():
    return MemoryBackend({BODY: b"old", RELATED: b"related before"}, ports=PORTS)


def test_operation_cas(backend):
    before = backend.snapshot()
    note = EventAppend(story=9, records=(wire(9, "update-1", 1),))
    operation = proposal(
        backend,
        before,
        changes=((BODY, b"new"), (RELATED, b"related after")),
        events=(note,),
    ).model_copy(update={"pending_actions": ("project.readback",)})
    stale = proposal(backend, before, "stale", changes=((RELATED, b"stale"),))

    accepted = backend.transact(operation, before)

    assert accepted.command.local == LocalOutcome.COMPLETED
    assert accepted.command.pending == ("project.readback",)
    assert accepted.preflight.outcome == PreflightOutcome.NOT_APPLICABLE
    assert accepted.authorization.origin == AuthorityOrigin.FIXTURE
    assert backend.read(before, (BODY, RELATED, note.path)) == {
        BODY: b"old",
        RELATED: b"related before",
        note.path: None,
    }
    assert backend.read(accepted.snapshot, (BODY, RELATED, note.path)) == {
        BODY: b"new",
        RELATED: b"related after",
        note.path: note.records[0] + b"\n",
    }
    assert backend.transact(operation, accepted.snapshot) == accepted

    different_intent = operation.intent.model_copy(
        update={"payload": b'{"different":true}'}
    )
    reused = operation.model_copy(update={"intent": different_intent})
    assert (
        backend.transact(reused, accepted.snapshot).command.local
        == LocalOutcome.INTEGRITY_ERROR
    )
    binding = OWNER.model_copy(update={"generation": 2})
    assert (
        backend.transact(
            operation.model_copy(update={"owner": binding}), accepted.snapshot
        ).command.local
        == LocalOutcome.INTEGRITY_ERROR
    )
    assert backend.transact(stale, before).command.local == LocalOutcome.CONFLICT
    assert backend.transact(stale, accepted.snapshot).reason == "read-set-changed"
    assert backend.snapshot() == accepted.snapshot


def test_refusal_retains_guards_without_applying_effects(backend):
    before = backend.snapshot()
    note = EventAppend(story=9, records=(wire(9, "update-1", 1),))
    operation = proposal(
        backend, before, changes=((BODY, b"forbidden"),), events=(note,)
    )
    guard = GuardEvaluated(
        operation=operation.operation_id,
        read_set_digest=operation.change.read_set_digest,
        policy_digest=operation.policy_digest,
        workflow={
            "workflow_id": "fixture",
            "revision": POLICY,
            "state_id": "refine",
            "label": "Refine",
        },
        slot="source-exit",
        guard="fixture.readiness",
        guard_version="1",
        ok=False,
        code="missing",
        mode="enforce",
    )
    refused = operation.model_copy(
        update={"guards": (guard,), "pending_actions": ("project.readback",)}
    )

    result = backend.transact(refused, before)

    assert result.command.local == LocalOutcome.REFUSED
    assert result.guards == (guard,)
    assert result.command.pending == ()
    assert result.snapshot != before
    assert result.snapshot.tree != before.tree
    assert backend.read(result.snapshot, (BODY, note.path)) == {
        BODY: b"old",
        note.path: None,
    }
    assert backend.transact(refused, result.snapshot) == result


def test_append_validates_all_streams_before_commit(backend):
    before = backend.snapshot()
    valid = EventAppend(story=9, records=(wire(9, "update-1", 1),))
    invalid = EventAppend(story=10, records=(wire(10, "update-1", 2),))
    operation = proposal(
        backend, before, changes=((RELATED, b"new"),), events=(valid, invalid)
    )

    assert (
        backend.transact(operation, before).command.local
        == LocalOutcome.INTEGRITY_ERROR
    )
    assert backend.snapshot() == before
    assert backend.read(before, (RELATED, valid.path, invalid.path)) == {
        RELATED: b"related before",
        valid.path: None,
        invalid.path: None,
    }

    first = proposal(backend, before, events=(valid,))
    snapshot = backend.transact(first, before).snapshot
    prefix = valid.records[0] + b"\n"
    second = EventAppend(story=9, records=(wire(9, "update-2", 2, prefix),))
    follow_up = proposal(backend, snapshot, "update-2", events=(second,))
    result = backend.transact(follow_up, snapshot)
    assert result.command.local == LocalOutcome.COMPLETED
    assert (
        backend.read(result.snapshot, (valid.path,))[valid.path]
        == prefix + second.records[0] + b"\n"
    )
    assert backend.read(snapshot, (valid.path,))[valid.path] == prefix


def test_same_snapshot_has_one_concurrent_winner(backend):
    before = backend.snapshot()
    operations = [
        proposal(backend, before, "left", changes=((BODY, b"left"),)),
        proposal(backend, before, "right", changes=((BODY, b"right"),)),
    ]
    with ThreadPoolExecutor(max_workers=2) as workers:
        results = tuple(
            workers.map(lambda op: backend.transact(op, before), operations)
        )
    assert {r.command.local for r in results} == {
        LocalOutcome.COMPLETED,
        LocalOutcome.CONFLICT,
    }
    winner = next(r for r in results if r.command.local == LocalOutcome.COMPLETED)
    assert winner.snapshot == backend.snapshot()
    assert backend.read(before, (BODY,))[BODY] == b"old"


def test_tree_and_preconditions_reject_an_invalid_update_atomically(backend):
    before = backend.snapshot()
    op = proposal(
        backend,
        before,
        changes=((BODY, b"new"), (BODY + "/nested", b"conflict")),
    )
    assert backend.transact(op, before).command.local == LocalOutcome.INTEGRITY_ERROR
    invalid = op.change.model_copy(update={"read_set": ()})
    assert (
        backend.transact(
            op.model_copy(update={"change": invalid}), before
        ).command.local
        == LocalOutcome.INTEGRITY_ERROR
    )
    assert backend.snapshot() == before


def test_write_authority_distinguishes_absence_refusal_and_registered_result():
    def deny(owner, change):
        return WriteAuthorization(
            allowed=False, origin=AuthorityOrigin.REGISTERED, reason="scope"
        )

    def allow_registered(owner, change):
        allowed = owner == OWNER and tuple(write.path for write in change.writes) == (
            BODY,
        )
        return WriteAuthorization(allowed=allowed, origin=AuthorityOrigin.REGISTERED)

    registered = replace(PORTS, write_authorization=allow_registered)
    for ports, expected in (
        (replace(registered, write_authorization=None), LocalOutcome.UNAVAILABLE),
        (replace(registered, write_authorization=deny), LocalOutcome.REFUSED),
        (registered, LocalOutcome.COMPLETED),
    ):
        store = MemoryBackend({BODY: b"old"}, ports=ports)
        snapshot = store.snapshot()
        result = store.transact(proposal(store, snapshot), snapshot)
        assert result.command.local == expected
        if expected != LocalOutcome.COMPLETED:
            assert store.snapshot() == snapshot
        if expected == LocalOutcome.UNAVAILABLE:
            assert result.authorization is None
        else:
            assert result.authorization.origin == AuthorityOrigin.REGISTERED


def attempt_bytes():
    started = (
        wire(
            9,
            "start",
            1,
            kind="core.attempt.started",
            data={
                "attempt": "attempt-9",
                "generation": 1,
                "plan_generation": 1,
                "source": {"commit": "b" * 40, "tree": "c" * 40},
                "binding": "binding-9",
                "allowance_millis": 3000,
            },
        )
        + b"\n"
    )
    clock = wire(
        9,
        "start",
        2,
        started,
        "core.attempt.clock.changed",
        {
            "attempt": "attempt-9",
            "generation": 1,
            "cause_event_id": "9-1",
            "from": None,
            "to": "active",
            "observed_at": STAMP,
            "used_millis": 0,
        },
    )
    return started + clock + b"\n"


@pytest.mark.parametrize("kind", ["attempt.reconcile", "expand"])
def test_attempt_mutation_requires_the_installed_preflight(kind):
    def blocked(context):
        assert context.operation.category == OperationCategory.NORMAL
        assert context.attempts[0].started.attempt == "attempt-9"
        return PreflightResult(outcome=PreflightOutcome.BLOCKED, reason="trip")

    ports = replace(PORTS, attempt_preflight=blocked)
    for composition, expected in (
        (replace(ports, attempt_preflight=None), LocalOutcome.UNAVAILABLE),
        (ports, LocalOutcome.REFUSED),
    ):
        store = MemoryBackend(
            {BODY: b"old", story_event_path(9): attempt_bytes()}, ports=composition
        )
        before = store.snapshot()
        result = store.transact(proposal(store, before, kind=kind), before)
        assert result.command.local == expected
        assert store.snapshot() == before


@pytest.mark.parametrize(
    ("kind", "category"),
    [
        ("authoring.sync", OperationCategory.AUTHORED_SYNC),
        ("stop.reconcile", OperationCategory.STOP_RECONCILIATION),
        ("attempt.recover", OperationCategory.RECOVERY),
    ],
)
def test_special_categories_require_the_exact_declared_capability(kind, category):
    scope = {(kind, 1): category}
    files = {BODY: b"old", story_event_path(9): attempt_bytes()}
    store = MemoryBackend(files, ports=PORTS, categories=scope)
    before = store.snapshot()
    borrowed = proposal(store, before, kind="expand", category=category)
    assert store.transact(borrowed, before).command.local == LocalOutcome.REFUSED
    current = proposal(store, before, kind=kind, category=category)
    assert store.transact(current, before).command.local == LocalOutcome.UNAVAILABLE

    def fixture_preflight(context):
        assert context.operation.category == category
        return PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.FIXTURE
        )

    authorized = MemoryBackend(
        files,
        ports=replace(PORTS, attempt_preflight=fixture_preflight),
        categories=scope,
    )
    pinned = authorized.snapshot()
    operation = proposal(authorized, pinned, kind=kind, category=category)
    accepted = authorized.transact(operation, pinned)
    assert accepted.command.local == LocalOutcome.COMPLETED
    assert accepted.preflight.origin == AuthorityOrigin.FIXTURE
    retagged = operation.model_copy(update={"category": OperationCategory.NORMAL})
    assert (
        authorized.transact(retagged, pinned).command.local
        == LocalOutcome.INTEGRITY_ERROR
    )
