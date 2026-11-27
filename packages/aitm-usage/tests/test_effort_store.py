import importlib
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime, timedelta, tzinfo
from threading import Barrier
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_effort_trail import effort_snapshot
from test_ledger import _QueryRows

from aitm_usage.types import Availability, SourceRef, TokenCounts, _encode

PROJECT = UUID(int=1)
ATTEMPT = UUID(int=2)
RUN = UUID(int=3)
STAMP = datetime(2026, 11, 24, tzinfo=UTC)


def ref(digit):
    return SourceRef("hmac-sha256:" + "0" * 64 + ":" + digit * 64)


@pytest.fixture
def effort():
    return importlib.import_module("aitm_usage.effort")


@pytest.fixture
def enrollment(effort):
    return effort.Enrollment(PROJECT, RUN, ATTEMPT, effort.Role.WORKER, story=12)


@pytest.fixture
def receipt(effort):
    return effort.UsageReceipt(
        project_id=PROJECT,
        attempt_id=ATTEMPT,
        turn=effort.NativeTurn("codex", "1.0", "exec", ref("1"), ref("2"), ref("3")),
        source_sha256="4" * 64,
        observed_at=STAMP,
        revision=1,
        coverage=Availability.PARTIAL,
        outcome=effort.Outcome.INTERRUPTED,
        tokens=TokenCounts(total_tokens=0),
        scope=effort.UsageScope.BOUNDED,
    )


def test_replays_are_idempotent_across_restart(effort, enrollment, receipt, tmp_path):
    path = tmp_path / "effort.db"
    store = effort.EffortStore(path, PROJECT)
    assert store.enroll(enrollment) is effort.Disposition.INSERTED
    enrolled_only = store.snapshot()
    assert enrolled_only.enrollments == (enrollment,) and not enrolled_only.attributed
    assert store.ingest(receipt) is effort.Disposition.INSERTED
    snapshot = store.snapshot()

    reopened = effort.EffortStore(path, PROJECT)
    assert reopened.enroll(enrollment) is effort.Disposition.REPLAYED
    assert reopened.ingest(receipt) is effort.Disposition.REPLAYED
    assert reopened.snapshot() == snapshot
    assert snapshot.attributed[0].story == 12
    assert snapshot.attributed[0].receipt.tokens.total_tokens == 0

    # Exercise the provider-native price receipt through the same durable
    # replay and conflict path as the ordinary usage receipt above.
    from test_effort_grok import ENROLLMENT as grok_enrollment
    from test_effort_grok import TICKS, settled_grok_usage

    first, changed = settled_grok_usage()
    grok_path = tmp_path / "grok.db"
    grok = effort.EffortStore(grok_path, grok_enrollment.project_id)
    assert grok.enroll(grok_enrollment) is effort.Disposition.INSERTED
    assert grok.ingest(first) is effort.Disposition.INSERTED
    grok = effort.EffortStore(grok_path, grok_enrollment.project_id)
    assert grok.ingest(first) is effort.Disposition.REPLAYED
    assert grok.snapshot().attributed[0].receipt == first
    assert grok.ingest(changed) is effort.Disposition.CONFLICTED
    assert grok.snapshot().attributed[0].receipt.grok_cost_usd_ticks == TICKS


def test_out_of_order_refinement_waits_for_exact_lineage(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", PROJECT)
    store.enroll(enrollment)
    receipt = replace(receipt, scope=effort.UsageScope.UNKNOWN)
    final = replace(
        receipt,
        revision=2,
        previous_digest=receipt.digest,
        scope=effort.UsageScope.BOUNDED,
        coverage=Availability.COMPLETE,
        tokens=TokenCounts(total_tokens=42),
    )
    assert store.ingest(final) is effort.Disposition.PENDING
    assert not store.snapshot().attributed
    assert store.snapshot().pending == (final,)
    assert store.ingest(receipt) is effort.Disposition.REFINED
    snapshot = store.snapshot()
    assert not snapshot.pending
    assert [row.receipt for row in snapshot.attributed] == [final]
    assert store.ingest(receipt) is effort.Disposition.REPLAYED
    lost = replace(
        final, revision=3, previous_digest=final.digest, tokens=TokenCounts()
    )
    assert store.ingest(lost) is effort.Disposition.CONFLICTED
    assert store.snapshot().attributed[0].receipt == final


def test_cross_project_and_cross_attempt_turn_reuse_are_isolated(
    effort, enrollment, receipt, tmp_path
):
    path = tmp_path / "effort.db"
    store = effort.EffortStore(path, PROJECT)
    store.enroll(enrollment)
    store.ingest(receipt)
    with pytest.raises(effort.EffortError, match="project"):
        effort.EffortStore(path, UUID(int=91))
    with pytest.raises(effort.EffortError, match="project"):
        store.ingest(replace(receipt, project_id=UUID(int=91)))

    new_attempt = UUID(int=9)
    store.enroll(replace(enrollment, attempt_id=new_attempt, story=13))
    conflicting = replace(receipt, attempt_id=new_attempt)
    assert store.ingest(conflicting) is effort.Disposition.CONFLICTED
    assert store.ingest(conflicting) is effort.Disposition.REPLAYED
    snapshot = store.snapshot()
    assert [row.receipt for row in snapshot.attributed] == [receipt]
    assert len(snapshot.conflicts) == 1


def test_conflicting_incomplete_chain_records_gap_without_replacing_prior_usage(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", PROJECT)
    store.enroll(enrollment)
    bad = replace(receipt, revision=2, previous_digest="e" * 64)
    assert store.ingest(bad) is effort.Disposition.PENDING
    assert store.ingest(receipt) is effort.Disposition.INSERTED
    snapshot = store.snapshot()
    assert not snapshot.pending
    assert [row.receipt for row in snapshot.attributed] == [receipt]
    assert snapshot.conflicts[0].reason == "revision-lineage"
    assert store.ingest(bad) is effort.Disposition.REPLAYED


def test_parallel_local_writers_publish_one_observation(
    effort, enrollment, receipt, tmp_path
):
    path = tmp_path / "effort.db"
    store = effort.EffortStore(path, PROJECT)
    store.enroll(enrollment)
    ready = Barrier(2, timeout=10)

    def ingest():
        worker = effort.EffortStore(path, PROJECT)
        ready.wait()
        return worker.ingest(receipt)

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: ingest(), range(2)))
    assert set(results) == {effort.Disposition.INSERTED, effort.Disposition.REPLAYED}
    assert len(store.snapshot().attributed) == 1


def test_ingest_rolls_back_receipt_and_effective_projection_together(
    effort, enrollment, receipt, tmp_path
):
    path = tmp_path / "effort.db"
    store = effort.EffortStore(path, PROJECT)
    store.enroll(enrollment)
    baseline = store.snapshot()
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TRIGGER fail_effective BEFORE INSERT ON effective "
            "BEGIN SELECT RAISE(ABORT, 'test publication failure'); END"
        )
    with pytest.raises(sqlite3.IntegrityError, match="test publication failure"):
        store.ingest(receipt)
    assert store.snapshot() == baseline
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TRIGGER fail_effective")
    assert store.ingest(receipt) is effort.Disposition.INSERTED


def test_strict_wire_format_and_provenance(effort, receipt):
    encoded = receipt.to_json()
    assert effort.UsageReceipt.from_json(encoded) == receipt
    with pytest.raises(ValueError):
        effort.UsageReceipt.from_json(
            encoded.replace('"revision":1', '"revision":true')
        )
    with pytest.raises(ValueError):
        effort.UsageReceipt.from_json(
            encoded.replace('"revision":1', '"revision":1,"raw":"/tmp/raw"')
        )
    with pytest.raises(ValueError):
        effort.UsageReceipt.from_json(
            encoded.replace('"revision":1', '"revision":1,"revision":1')
        )
    with pytest.raises(ValueError):
        replace(receipt, source_sha256="/tmp/raw")


def test_late_receipt_keeps_original_story_after_same_session_switch(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", enrollment.project_id)
    attempt_b = UUID(int=30)
    store.enroll(enrollment)
    store.enroll(replace(enrollment, attempt_id=attempt_b, story=13))
    receipt_b = replace(
        receipt, attempt_id=attempt_b, turn=replace(receipt.turn, turn=ref("e"))
    )
    store.ingest(receipt_b)
    store.ingest(receipt)
    assert {
        row.receipt.attempt_id: row.story for row in store.snapshot().attributed
    } == {
        enrollment.attempt_id: 12,
        attempt_b: 13,
    }


def test_unattached_link_is_immutable_authorized_and_idempotent(
    effort, enrollment, receipt, tmp_path
):
    path = tmp_path / "effort.db"
    store = effort.EffortStore(path, enrollment.project_id)
    store.enroll(replace(enrollment, story=None, epic=7))
    store.ingest(receipt)
    assert store.snapshot().attributed[0].story is None
    link = effort.Attribution(
        enrollment.project_id, receipt.observation_id, 7, 12, ref("a")
    )
    with pytest.raises(effort.EffortError, match="project"):
        store.attribute(replace(link, project_id=UUID(int=90)))
    with pytest.raises(effort.EffortError, match="epic"):
        store.attribute(replace(link, epic=8))

    assert store.attribute(link) is effort.Disposition.INSERTED
    reopened = effort.EffortStore(path, enrollment.project_id)
    snapshot = reopened.snapshot()
    assert reopened.attribute(link) is effort.Disposition.REPLAYED
    assert reopened.snapshot() == snapshot
    assert snapshot.attributed[0].story == 12
    assert snapshot.attributed[0].epic == 7
    assert snapshot.attributed[0].attribution == link
    assert reopened.attribute(replace(link, story=13)) is effort.Disposition.CONFLICTED
    assert reopened.snapshot().attributed[0].story == 12


def test_mixed_turn_never_inherits_story_or_accepts_late_link(
    effort, enrollment, receipt, monkeypatch
):
    mixed = replace(receipt, scope=effort.UsageScope.MIXED)
    assert effort_snapshot((enrollment, mixed)).attributed[0].story is None
    store = effort.EffortStore.__new__(effort.EffortStore)
    store.project_id = enrollment.project_id
    monkeypatch.setattr(store, "_transaction", lambda *, write: nullcontext(object()))

    def effective(db, observation):
        assert observation == mixed.observation_id
        return mixed

    monkeypatch.setattr(store, "_effective", effective)
    link = effort.Attribution(
        enrollment.project_id, mixed.observation_id, None, 12, ref("b")
    )
    with pytest.raises(effort.EffortError, match="scope"):
        store.attribute(link)


def test_different_agent_can_continue_same_story_with_fresh_session(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", enrollment.project_id)
    successor = UUID(int=31)
    store.enroll(enrollment)
    store.ingest(receipt)
    store.enroll(replace(enrollment, attempt_id=successor))
    store.ingest(
        replace(
            receipt, attempt_id=successor, turn=replace(receipt.turn, session=ref("8"))
        )
    )
    rows = store.snapshot().attributed
    assert len(rows) == 2
    assert all(row.story == 12 for row in rows)
    assert len({row.receipt.turn.session for row in rows}) == 2


def test_existing_foreign_database_is_never_adopted_or_modified(
    effort, enrollment, tmp_path
):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE existing_data (value TEXT)")
        db.execute("INSERT INTO existing_data VALUES ('keep')")
    before = path.read_bytes()
    with pytest.raises(effort.EffortError, match="effort database"):
        effort.EffortStore(path, enrollment.project_id)
    assert path.read_bytes() == before


def test_missing_scope_does_not_bind_to_enrolled_story(effort, enrollment, receipt):
    undecided = effort.UsageReceipt(
        receipt.project_id,
        receipt.attempt_id,
        receipt.turn,
        receipt.source_sha256,
        receipt.observed_at,
        1,
        receipt.coverage,
        receipt.outcome,
        receipt.tokens,
    )
    assert effort_snapshot((enrollment, undecided)).attributed[0].story is None


def test_new_turn_without_new_attempt_is_a_conflict(
    effort, enrollment, receipt, monkeypatch
):
    from unittest.mock import Mock

    other = replace(receipt, turn=replace(receipt.turn, turn=ref("f")))
    store = effort.EffortStore.__new__(effort.EffortStore)
    store.project_id = enrollment.project_id
    responses = {
        "SELECT 1 FROM conflicts WHERE digest=?": [],
        "SELECT 1 FROM pending WHERE digest=?": [],
        "SELECT digest FROM revisions WHERE observation=? AND revision=?": [],
        "SELECT observation FROM effective WHERE attempt=? AND observation<>?": [
            (receipt.observation_id,),
        ],
        "SELECT 1 FROM scope_markers WHERE "
        "(observation=? AND attempt<>?) OR (attempt=? AND observation<>?)": [],
    }

    def execute(query, options):
        if "SELECT observation FROM effective" in query:
            assert options == (str(enrollment.attempt_id), other.observation_id)
        return _QueryRows(responses[" ".join(query.split())])

    db = SimpleNamespace(execute=execute)
    monkeypatch.setattr(store, "_effective", Mock(return_value=None))
    monkeypatch.setattr(store, "_enrollment", Mock(return_value=enrollment))
    monkeypatch.setattr(store, "_advance_generation", Mock())
    conflict = Mock()
    monkeypatch.setattr(store, "_conflict", conflict)
    assert store._ingest(db, other) is effort.Disposition.CONFLICTED
    conflict.assert_called_once_with(db, other, "turn-attempt")


def test_snapshot_retains_enrolled_attempts_without_usage(
    effort, enrollment, monkeypatch
):
    store = effort.EffortStore.__new__(effort.EffortStore)
    store.project_id = enrollment.project_id
    responses = {
        "sqlite_schema": [("scope_markers",), ("handoffs",)],
        "scope_markers": [],
        "handoffs": [],
        "enrollments": [(_encode(enrollment, type(enrollment)),)],
        "effective": [],
        "pending": [],
        "conflicts": [],
    }

    def execute(query):
        return responses[query.split(" FROM ", 1)[1].split()[0]]

    monkeypatch.setattr(
        store, "_transaction", lambda: nullcontext(SimpleNamespace(execute=execute))
    )
    monkeypatch.setattr(store, "_generation", lambda _: 5)
    snapshot = store.snapshot()
    assert snapshot.enrollments == (enrollment,)
    assert not snapshot.attributed


def test_pending_evidence_for_another_turn_moves_to_conflict_on_binding(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", enrollment.project_id)
    store.enroll(enrollment)
    other = replace(
        receipt,
        turn=replace(receipt.turn, turn=ref("f")),
        revision=2,
        previous_digest="b" * 64,
    )
    assert store.ingest(other) is effort.Disposition.PENDING
    assert store.ingest(receipt) is effort.Disposition.INSERTED
    snapshot = store.snapshot()
    assert not snapshot.pending
    assert snapshot.conflicts[0].receipt == other
    assert snapshot.conflicts[0].reason == "turn-attempt"
    rejected = replace(other, revision=1, previous_digest=None)
    assert store.ingest(rejected) is effort.Disposition.CONFLICTED
    assert [row.receipt for row in store.snapshot().attributed] == [receipt]


def test_pending_collision_cannot_suppress_revision_with_valid_predecessor(
    effort, enrollment, receipt, tmp_path
):
    store = effort.EffortStore(tmp_path / "effort.db", enrollment.project_id)
    store.enroll(enrollment)
    wrong = replace(receipt, revision=2, previous_digest="e" * 64)
    correct = replace(
        receipt,
        revision=2,
        previous_digest=receipt.digest,
        coverage=Availability.COMPLETE,
        tokens=TokenCounts(total_tokens=42),
    )
    assert store.ingest(wrong) is effort.Disposition.PENDING
    assert store.ingest(correct) is effort.Disposition.PENDING
    assert store.ingest(receipt) is effort.Disposition.REFINED
    snapshot = store.snapshot()
    assert snapshot.pending == ()
    assert snapshot.attributed[0].receipt == correct
    assert snapshot.conflicts[0].receipt == wrong
    assert snapshot.conflicts[0].reason == "revision-lineage"
    assert store.ingest(wrong) is effort.Disposition.REPLAYED
    assert store.ingest(correct) is effort.Disposition.REPLAYED


def test_exact_recovery_can_refine_unknown_scope_and_keep_usage(
    effort, enrollment, receipt
):
    unknown_scope = replace(
        receipt, scope=effort.UsageScope.UNKNOWN, coverage=Availability.COMPLETE
    )
    assert effort_snapshot((enrollment, unknown_scope)).attributed[0].story is None
    recovered = replace(
        unknown_scope,
        scope=effort.UsageScope.BOUNDED,
        revision=2,
        previous_digest=unknown_scope.digest,
    )
    assert effort.EffortStore._revision_conflict(unknown_scope, recovered) is None
    assert effort_snapshot((enrollment, recovered)).attributed[0].story == 12
    assert recovered.tokens == unknown_scope.tokens


def test_refinement_cannot_erase_observed_counts(effort, receipt):
    lost = replace(
        receipt,
        revision=2,
        previous_digest=receipt.digest,
        coverage=Availability.COMPLETE,
        tokens=TokenCounts(),
    )
    assert effort.EffortStore._revision_conflict(receipt, lost) == "revision-usage"


def test_intervals_compare_actual_time_across_repeated_local_hour(effort, receipt):
    class FoldZone(tzinfo):
        def utcoffset(self, value):
            return timedelta(hours=-4 - value.fold)

        def dst(self, value):
            return timedelta(hours=1 - value.fold)

    zone = FoldZone()
    start = datetime(2026, 11, 1, 1, 50, tzinfo=zone, fold=0)
    end = datetime(2026, 11, 1, 1, 10, tzinfo=zone, fold=1)
    observed = replace(
        receipt,
        started_at=start,
        ended_at=end,
        time_basis=effort.TimeBasis.NATIVE,
    )
    assert observed.ended_at - observed.started_at == timedelta(minutes=20)
    assert effort.UsageReceipt.from_json(observed.to_json()) == observed
