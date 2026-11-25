from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from aitm_usage.effort.receipts import (
    NativeTurn,
    Outcome,
    Role,
    UsageReceipt,
    UsageScope,
)
from aitm_usage.effort.store import Disposition, EffortError
from aitm_usage.types import Availability, TokenCounts

PROJECT = UUID(int=1)
SESSION = UUID(int=2)
OWNER = UUID(int=3)
CHILD = UUID(int=4)
STAMP = datetime(2026, 11, 25, tzinfo=UTC)
REMOTE = "https://example.invalid/owner/project.git"


@pytest.fixture
def session_api():
    from aitm_usage.effort import session

    return session


def layout(session_api, path):
    store = session_api.SessionStore(path, PROJECT)
    store.select(SESSION, 457, REMOTE, epic=456)
    launch = store.reference("launch", "private-canary")
    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        *(store.reference("test", item) for item in ("account", "session", "turn")),
    )
    store.expect(SESSION, OWNER, Role.ORCHESTRATOR, launch)
    store.expect(SESSION, CHILD, Role.WORKER, launch, parent=OWNER)
    return store, launch, turn


def test_switch_restart_and_replay_keep_the_dispatch_story(session_api, tmp_path):
    database = tmp_path / "effort.db"
    store, launch, turn = layout(session_api, database)
    store.select(SESSION, 458, REMOTE, epic=456)
    reopened = session_api.SessionStore(database, PROJECT)
    assert (
        reopened.expect(
            SESSION, CHILD, Role.WORKER, launch, parent=OWNER
        ).enrollment.story
        == 457
    )
    with pytest.raises(EffortError, match="launch"):
        reopened.bind(SESSION, CHILD, reopened.reference("launch", "wrong"), turn)
    reopened.bind(SESSION, CHILD, launch, turn)
    with pytest.raises(EffortError, match="binding"):
        reopened.bind(SESSION, CHILD, launch, replace(turn, turn=launch))
    assert reopened.status(SESSION)[CHILD] == "pending-evidence"
    assert (
        reopened.expect(SESSION, UUID(int=5), Role.REVIEWER, launch).enrollment.story
        == 458
    )
    with pytest.raises(EffortError, match="remote"):
        reopened.select(SESSION, 458, "https://example.invalid/other.git")


def test_revision_publication_whitelists_and_waits_for_predecessor(
    session_api, tmp_path
):
    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    store.bind(SESSION, CHILD, launch, turn)
    first = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "a" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
        scope=UsageScope.BOUNDED,
    )
    second = replace(
        first,
        revision=2,
        previous_digest=first.digest,
        coverage=Availability.COMPLETE,
        tokens=TokenCounts(input_tokens=12, output_tokens=3),
    )
    assert store.accept(SESSION, second) is Disposition.PENDING
    assert store.public_receipts(SESSION) == ()
    assert store.accept(SESSION, first) is Disposition.REFINED
    public = store.public_receipts(SESSION)
    assert len(public) == 2
    rows = [session_api.validate_public_receipt(payload) for payload in public]
    assert [row["revision"] for row in rows] == [1, 2]
    assert rows[1]["story"] == 457 and rows[1]["tokens"]["output_tokens"] == 3
    assert rows[0]["identity"] == rows[1]["identity"]
    assert all(
        turn.account.value.encode() not in payload and CHILD.hex.encode() not in payload
        for payload in public
    )
    with pytest.raises(EffortError, match="exact"):
        store.accept(SESSION, replace(first, turn=replace(turn, turn=launch)))
    assert store.status(SESSION)[CHILD] == "observed"
    assert store.status(SESSION)[OWNER] == "pending-binding"


def test_store_refuses_cross_project_and_hides_unknown_usage(session_api, tmp_path):
    database = tmp_path / "effort.db"
    store, launch, turn = layout(session_api, database)
    with pytest.raises(EffortError, match="project"):
        session_api.SessionStore(database, UUID(int=99))
    with pytest.raises(EffortError, match="session"):
        store.bind(UUID(int=99), OWNER, launch, turn)
    store.bind(SESSION, OWNER, launch, turn)
    receipt = UsageReceipt(
        PROJECT,
        OWNER,
        turn,
        "b" * 64,
        STAMP,
        1,
        Availability.UNKNOWN,
        Outcome.INTERRUPTED,
        TokenCounts(),
        scope=UsageScope.BOUNDED,
    )
    store.accept(SESSION, receipt)
    assert store.status(SESSION)[OWNER] == "unavailable"
    (payload,) = store.public_receipts(SESSION)
    data = session_api.validate_public_receipt(payload)
    assert data["model"] is None and data["rate_inputs"] is None
    with pytest.raises(ValueError):
        session_api.validate_public_receipt(
            payload[:-1] + b',"private_path":"/tmp/canary"}'
        )


def test_session_cli_registers_expectation_before_provider(
    session_api, tmp_path, capsys
):
    import json

    from aitm_usage.effort.cli import main

    database = tmp_path / "effort.db"
    args = ["--database", str(database), "--project", str(PROJECT)]
    assert main(args + ["session-select", str(SESSION), "457", REMOTE]) == 0
    assert (
        main(
            args
            + ["session-expect", str(SESSION), str(OWNER), "orchestrator", "launch"]
        )
        == 0
    )
    assert main(args + ["session-status", str(SESSION)]) == 0
    assert json.loads(capsys.readouterr().out) == {str(OWNER): "pending-binding"}


@pytest.mark.parametrize("prebind", [False, True])
def test_supervised_launch_settles_automatically_and_will_not_repeat(
    session_api, tmp_path, prebind
):
    import asyncio
    import sys
    from pathlib import Path

    from aitm_usage.effort.capture import HarnessCommand, Observation

    store, launch, turn = layout(session_api, tmp_path / "effort.db")

    class Observes:
        def observe(self, event):
            assert event.stdout.splitlines() == [b"finished"]
            assert store.status(SESSION)[CHILD] == (
                "pending-evidence" if prebind else "pending-binding"
            )
            return Observation(
                Outcome.COMPLETED,
                UsageReceipt(
                    PROJECT,
                    CHILD,
                    turn,
                    "e" * 64,
                    STAMP,
                    1,
                    Availability.COMPLETE,
                    Outcome.COMPLETED,
                    TokenCounts(total_tokens=12),
                    scope=UsageScope.BOUNDED,
                ),
            )

    command = HarnessCommand((sys.executable, "-c", "print('finished')"), Path.cwd())
    assert asyncio.run(
        store.run_owned(
            SESSION,
            CHILD,
            launch,
            Observes(),
            command,
            expected_turn=turn if prebind else None,
        )
    ).observation.receipt
    assert store.status(SESSION)[CHILD] == "observed"
    with pytest.raises(EffortError, match="already dispatched"):
        asyncio.run(store.run_owned(SESSION, CHILD, launch, Observes(), command))


def test_unknown_scope_and_open_markers_withhold_publication(session_api, tmp_path):
    from aitm_usage.effort.assignments import MarkerKind, ScopeMarker

    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    store.bind(SESSION, CHILD, launch, turn)
    unknown = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "e" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
    )
    store.accept(SESSION, unknown)
    assert store.public_receipts(SESSION) == ()
    assert store.snapshot().attributed[0].story is None
    owner_turn = replace(turn, turn=launch)
    store.bind(SESSION, OWNER, launch, owner_turn)
    start = ScopeMarker(
        PROJECT, OWNER, owner_turn, MarkerKind.START, launch, STAMP, turn.account
    )
    store.mark_scope(start)
    bounded = replace(
        unknown, attempt_id=OWNER, turn=owner_turn, scope=UsageScope.BOUNDED
    )
    store.accept(SESSION, bounded)
    assert store.public_receipts(SESSION) == ()
    store.mark_scope(replace(start, kind=MarkerKind.END))
    (payload,) = store.public_receipts(SESSION)
    for value in ("desktop", "0.171.0-alpha.13.2"):
        with pytest.raises(ValueError):
            session_api.validate_public_receipt(
                payload.replace(value.encode(), b"CANARY_PRIVATE_VALUE")
            )


def test_frozen_batch_survives_story_and_revision_changes(session_api, tmp_path):
    from aitm_usage.effort.session_cli import _batch, _read_batch

    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    store.bind(SESSION, CHILD, launch, turn)
    first = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "a" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
        scope=UsageScope.BOUNDED,
    )
    store.accept(SESSION, first)
    handoff = tmp_path / "batch.json"
    handoff.write_bytes(_batch(store, SESSION, 457))
    store.select(SESSION, 458, REMOTE)
    store.accept(SESSION, replace(first, revision=2, previous_digest=first.digest))
    other_writer = session_api.SessionStore(tmp_path / "other-writer.db", PROJECT)
    other_writer.select(SESSION, 457, REMOTE)
    (entry,) = _read_batch(handoff, other_writer, 457)
    assert entry.revision == 1
    assert entry.data == store.public_receipts(SESSION)[0]
    with pytest.raises(EffortError, match="batch"):
        _read_batch(handoff, other_writer, 458)


def test_review_companion_keeps_sealed_decision_independent(session_api, tmp_path):
    from aitm_usage.effort.receipts import ReviewBinding
    from aitm_usage.effort.review_receipts import (
        ReviewAttempt,
        ReviewIdentity,
        SealedDecision,
        Verdict,
    )

    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    attempt_id = UUID(int=7)
    expected = store.expect(
        SESSION,
        attempt_id,
        Role.REVIEWER,
        launch,
        review=ReviewBinding(turn.account, 1),
    )
    store.bind(SESSION, attempt_id, launch, turn)
    identity = ReviewIdentity(expected.enrollment, turn.session, "a" * 64)
    attempt = ReviewAttempt(identity, turn.identity)
    decision = SealedDecision(identity, Verdict.ACCEPTED, "b" * 64, turn.turn)
    assert store.review_companion(SESSION, attempt, decision).usage is None
    usage = UsageReceipt(
        PROJECT,
        attempt_id,
        turn,
        "c" * 64,
        STAMP,
        1,
        Availability.COMPLETE,
        Outcome.COMPLETED,
        TokenCounts(total_tokens=12),
        scope=UsageScope.BOUNDED,
    )
    store.accept(SESSION, usage)
    result = store.review_companion(SESSION, attempt, decision)
    assert result.decision == decision and result.usage == usage
    with pytest.raises(EffortError, match="exact session"):
        store.review_companion(SESSION, replace(attempt, observation_id="e" * 64), None)


def test_late_scope_proof_redacts_historical_usage_without_losing_lineage(
    session_api, tmp_path
):
    from hashlib import sha256

    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    store.bind(SESSION, CHILD, launch, turn)
    first = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "e" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
    )
    future = replace(
        first, revision=2, previous_digest=first.digest, scope=UsageScope.BOUNDED
    )
    assert store.accept(SESSION, future) is Disposition.PENDING
    assert store.public_receipts(SESSION) == ()
    assert store.accept(SESSION, first) is Disposition.REFINED
    redacted, final = store.public_receipts(SESSION)
    assert all(
        value is None
        for value in session_api.validate_public_receipt(redacted)["tokens"].values()
    )
    row = session_api.validate_public_receipt(final)
    assert row["tokens"]["input_tokens"] == 12
    assert row["previous_receipt_sha256"] == sha256(redacted).hexdigest()
