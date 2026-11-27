import json
from dataclasses import replace
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from test_effort_trail import PROJECT, evidence, ref

from aitm_usage.effort import (
    Disposition,
    EffortError,
    EffortStore,
    Outcome,
    ReviewBinding,
    Role,
)
from aitm_usage.effort.store import Snapshot, StoryObservation
from aitm_usage.types import Availability, TokenCounts


def _record(row):
    from aitm_usage.effort.review_receipts import (
        ReviewAttempt,
        ReviewIdentity,
        SealedDecision,
        Verdict,
    )

    enrollment, usage = evidence(row["turn"], session=row["session"], story=444)
    enrollment = replace(
        enrollment,
        run_id=uuid5(NAMESPACE_URL, row["run"]),
        attempt_id=uuid5(NAMESPACE_URL, row["attempt"]),
        role=Role.REVIEWER,
        review=ReviewBinding(ref(row["review"]), row["round"]),
    )
    ticks = row["grok_cost_usd_ticks"]
    status = row["usage_status"]
    usage = replace(
        usage,
        attempt_id=enrollment.attempt_id,
        turn=replace(usage.turn, provider=row["provider"]),
        tokens=TokenCounts(total_tokens=row["observed_tokens"]),
        coverage=Availability.COMPLETE if status == "settled" else Availability.PARTIAL,
        outcome={
            "settled": Outcome.COMPLETED,
            "partial": Outcome.INTERRUPTED,
            "failed": Outcome.FAILED,
        }[status],
        schema="aitm.effort.receipt/v1" if ticks is None else "aitm.effort.receipt/v2",
        grok_cost_usd_ticks=ticks,
        grok_cache_creation_tokens=None if ticks is None else 0,
    )
    identity = ReviewIdentity(enrollment, ref(row["session"]), row["artifact_sha256"])
    attempt = ReviewAttempt(identity, usage.observation_id)
    decision = (
        None
        if row["decision"] is None
        else SealedDecision(
            identity,
            Verdict(row["decision"]),
            row["response_sha256"],
            ref(row["attempt"]),
        )
    )
    return attempt, decision, usage


@pytest.fixture
def records():
    source = Path(__file__).parent / "fixtures/effort/aipr-companions-431-434.json"
    return [_record(row) for row in json.loads(source.read_bytes())["attempts"]]


def snapshot_for(*enrollments, usage=(), pending=()):
    enrollment_by_attempt = {row.attempt_id: row for row in enrollments}
    attributed = tuple(
        StoryObservation(receipt, enrollment, enrollment.story, enrollment.epic, None)
        for receipt in usage
        for enrollment in (enrollment_by_attempt[receipt.attempt_id],)
    )
    return Snapshot(PROJECT, 0, tuple(enrollments), attributed, pending, ())


def test_qualified_rounds_reconcile_independent_delivery_and_replay(records, tmp_path):
    from aitm_usage.effort.review_receipts import reconcile_review_receipts

    db = tmp_path / "effort.db"
    store = EffortStore(db, PROJECT)
    attempts = [row[0] for row in records]
    decisions = [row[1] for row in records if row[1] is not None]
    for attempt in attempts:
        store.enroll(attempt.identity.enrollment)
    before = reconcile_review_receipts(store.snapshot(), attempts, decisions)
    assert sum(row.decision is not None for row in before) == 4
    assert all(row.usage is None for row in before)

    for _, _, usage in reversed(records):
        assert store.ingest(usage) is Disposition.INSERTED
    reopened = EffortStore(db, PROJECT, read_only=True)
    snapshot = reopened.snapshot()
    usage_first = reconcile_review_receipts(snapshot, attempts, ())
    assert all(row.decision is None and row.usage is not None for row in usage_first)
    after = reconcile_review_receipts(snapshot, reversed(attempts), reversed(decisions))
    settled = [row for row in after if row.decision is not None]
    assert len(settled) == 4
    assert sum(row.usage.tokens.total_tokens for row in settled) == 893_942
    assert {
        (row.usage.turn.provider, row.attempt.identity.enrollment.review.round)
        for row in settled
    } == {
        ("claude", 1),
        ("claude", 2),
        ("grok", 1),
        ("grok", 2),
    }
    assert sum(row.usage.grok_cost_usd_ticks or 0 for row in settled) == 2_046_419_200
    interrupted = [row for row in after if row.usage.outcome is Outcome.INTERRUPTED]
    assert sum(row.usage.tokens.total_tokens for row in interrupted) == 217_433
    assert all(row.decision is None for row in interrupted)
    failed = [row for row in after if row.usage.outcome is Outcome.FAILED]
    assert sorted(row.usage.tokens.total_tokens for row in failed) == [60_807, 93_587]
    assert all(row.decision is None for row in failed)

    original = db.read_bytes()
    for _, _, usage in records:
        assert store.ingest(usage) is Disposition.REPLAYED
    assert (
        reconcile_review_receipts(reopened.snapshot(), attempts * 2, decisions * 2)
        == after
    )
    assert db.read_bytes() == original


def test_companion_rejects_wrong_identity_seal_and_native_turn(records):
    from aitm_usage.effort.review_receipts import reconcile_review_receipts

    attempt, decision, usage = records[0]
    identity = attempt.identity
    enrollment = identity.enrollment
    snapshot = snapshot_for(enrollment, usage=(usage,))
    for wrong in (
        replace(identity, reviewer=ref("wrong-reviewer")),
        replace(identity, artifact_sha256="0" * 64),
        replace(
            identity,
            enrollment=replace(enrollment, review=replace(enrollment.review, round=2)),
        ),
        replace(
            identity,
            enrollment=replace(enrollment, run_id=uuid5(NAMESPACE_URL, "other-run")),
        ),
        replace(
            identity,
            enrollment=replace(
                enrollment, project_id=uuid5(NAMESPACE_URL, "other-project")
            ),
        ),
    ):
        with pytest.raises(EffortError, match="decision binding"):
            reconcile_review_receipts(
                snapshot, [attempt], [replace(decision, identity=wrong)]
            )
    with pytest.raises(EffortError, match="conflicting sealed"):
        reconcile_review_receipts(
            snapshot, [attempt], [decision, replace(decision, response_sha256="1" * 64)]
        )
    with pytest.raises(EffortError, match="native observation"):
        reconcile_review_receipts(
            snapshot, [replace(attempt, observation_id="2" * 64)], [decision]
        )
    unbound = reconcile_review_receipts(
        snapshot, [replace(attempt, observation_id=None)], [decision]
    )[0]
    assert unbound.decision == decision and unbound.usage is None


def test_same_review_round_cannot_claim_two_seals(records):
    from aitm_usage.effort.review_receipts import reconcile_review_receipts

    attempt, decision, _ = records[0]
    enrollment = attempt.identity.enrollment
    retry = replace(enrollment, attempt_id=uuid5(NAMESPACE_URL, "retry"))
    retry_identity = replace(attempt.identity, enrollment=retry)
    retry_attempt = replace(attempt, identity=retry_identity, observation_id=None)
    retry_decision = replace(decision, identity=retry_identity, seal=ref("retry"))
    with pytest.raises(EffortError, match="conflicting sealed"):
        reconcile_review_receipts(
            snapshot_for(enrollment, retry),
            [attempt, retry_attempt],
            [decision, retry_decision],
        )


def test_pending_usage_restores_lineage_without_changing_decision(records):
    from aitm_usage.effort.review_receipts import reconcile_review_receipts

    attempt, decision, first = records[0]
    successor = replace(
        first, revision=2, previous_digest=first.digest, source_sha256="c" * 64
    )
    enrollment = attempt.identity.enrollment
    (pending,) = reconcile_review_receipts(
        snapshot_for(enrollment, pending=(successor,)), [attempt], [decision]
    )
    assert pending.decision == decision
    assert pending.usage is None and pending.pending_usage_revisions == 1

    (settled,) = reconcile_review_receipts(
        snapshot_for(enrollment, usage=(successor,)), [attempt], [decision, decision]
    )
    assert settled.decision == decision
    assert settled.usage == successor and settled.pending_usage_revisions == 0
    assert settled.usage.tokens == first.tokens
