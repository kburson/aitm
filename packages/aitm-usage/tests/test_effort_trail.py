import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from aitm_usage.effort import (
    Disposition,
    EffortError,
    EffortStore,
    Enrollment,
    Handoff,
    MarkerKind,
    NativeTurn,
    Outcome,
    Role,
    RollupTarget,
    ScopeMarker,
    TimeBasis,
    UsageReceipt,
    UsageScope,
    WorkflowWindow,
    rollup,
)
from aitm_usage.effort.store import Snapshot
from aitm_usage.types import Availability, SourceRef, TokenCounts, _encode

PROJECT = UUID(int=442)
RUN = UUID(int=435)
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def ref(value):
    return SourceRef(f"hmac-sha256:{'a' * 64}:{sha256(value.encode()).hexdigest()}")


def instant(ms):
    return EPOCH + timedelta(milliseconds=ms)


def evidence(name, start=1000, end=2000, *, session="one", story=1, **changes):
    enrolled = Enrollment(PROJECT, RUN, uuid4(), Role.WORKER, story, 435)
    return enrolled, UsageReceipt(
        PROJECT,
        enrolled.attempt_id,
        NativeTurn("codex", "1", "test", ref("account"), ref(session), ref(name)),
        "b" * 64,
        instant(10_000),
        1,
        Availability.COMPLETE,
        Outcome.COMPLETED,
        TokenCounts(total_tokens=10),
        UsageScope.BOUNDED,
        started_at=instant(start),
        ended_at=instant(end),
        time_basis=TimeBasis.NATIVE,
        **changes,
    )


def marker(receipt, kind, ms):
    return ScopeMarker(
        PROJECT,
        receipt.attempt_id,
        receipt.turn,
        kind,
        ref("clock"),
        instant(ms),
        ref(f"{receipt.observation_id}:{kind}"),
    )


def target(story=None):
    return RollupTarget(PROJECT, epic=435, story=story)


def effort_snapshot(*pairs, pending_enrollments=(), markers=(), links=()):
    enrollments = tuple(enrollment for enrollment, _ in pairs) + pending_enrollments
    (project,) = {enrollment.project_id for enrollment in enrollments}
    starts = {row.turn.identity for row in markers if row.kind is MarkerKind.START}
    ends = {row.turn.identity for row in markers if row.kind is MarkerKind.END}
    open_scopes = starts - ends
    links_by_observation = {link.observation_id: link for link in links}
    attributed = tuple(
        EffortStore._story_observation(
            receipt.to_json(),
            _encode(enrollment, Enrollment),
            _encode(link, type(link)) if link is not None else None,
            receipt.observation_id in open_scopes,
        )
        for enrollment, receipt in pairs
        for link in (links_by_observation.get(receipt.observation_id),)
    )
    return Snapshot(
        project,
        0,
        enrollments,
        attributed,
        (),
        (),
        tuple(markers),
    )


def test_markers_handoff_and_late_receipt_preserve_original_story(tmp_path):
    database = tmp_path / "effort.db"
    store = EffortStore(database, PROJECT)
    old, prior = evidence("old")
    new, successor = evidence("new", 4000, 5000, session="two")
    other, later = evidence("later", 3000, 4000, session="three", story=2)
    for enrolled in (old, new, other):
        store.enroll(enrolled)

    start = marker(prior, MarkerKind.START, 900)
    end = marker(prior, MarkerKind.END, 2100)
    with pytest.raises(EffortError):
        store.mark_scope(end)
    assert store.mark_scope(start) == Disposition.INSERTED
    assert store.mark_scope(start) == Disposition.REPLAYED
    impostor = replace(prior, turn=replace(prior.turn, turn=ref("other-turn")))
    assert store.ingest(impostor) == Disposition.CONFLICTED
    with pytest.raises(EffortError):
        store.mark_scope(marker(impostor, MarkerKind.END, 2200))
    assert store.mark_scope(end) == Disposition.INSERTED

    for receipt, before, after in ((later, 2800, 4100), (successor, 3900, 5200)):
        store.mark_scope(marker(receipt, MarkerKind.START, before))
        store.mark_scope(marker(receipt, MarkerKind.END, after))
    handoff = Handoff(PROJECT, prior.turn, successor.turn, ref("handoff"))
    with pytest.raises(EffortError):
        store.handoff(replace(handoff, successor=later.turn))
    assert store.handoff(handoff) == Disposition.INSERTED
    assert store.handoff(handoff) == Disposition.REPLAYED
    assert store.ingest(later) == Disposition.INSERTED
    assert store.ingest(successor) == Disposition.INSERTED
    assert store.ingest(prior) == Disposition.INSERTED
    assert store.ingest(prior) == Disposition.REPLAYED
    snapshot = EffortStore(database, PROJECT).snapshot()
    assert snapshot.handoffs == (handoff,)
    assert rollup(snapshot, target(1)).total.observations == 2
    assert rollup(snapshot, target(2)).total.observations == 1
    assert rollup(snapshot, target(1)).total.engaged == timedelta(seconds=2)


def test_open_and_mixed_turns_are_unassigned():
    enrolled, receipt = evidence("turn")
    start = marker(receipt, MarkerKind.START, 900)
    end = marker(receipt, MarkerKind.END, 2100)
    bounded = (enrolled, receipt)
    snapshot = effort_snapshot(bounded, markers=(start,))
    assert snapshot.attributed[0].story is None
    result = rollup(snapshot, target())
    assert result.total.observations == 0
    assert result.unassigned_observations == 1
    assert (
        rollup(
            effort_snapshot(bounded, markers=(start, end)), target()
        ).total.observations
        == 1
    )

    enrolled, receipt = evidence("mixed")
    receipt = replace(receipt, scope=UsageScope.MIXED)
    snapshot = effort_snapshot(
        bounded,
        (enrolled, receipt),
        markers=(
            start,
            end,
            marker(receipt, MarkerKind.START, 900),
            marker(receipt, MarkerKind.END, 2100),
        ),
    )
    result = rollup(snapshot, target())
    assert result.total.observations == 1
    assert result.unassigned_observations == 1
    assert rollup(snapshot, RollupTarget(PROJECT)).total.usage_gaps == 1


def test_nested_disjoint_usage_and_overlapping_sessions():
    parent, inclusive = evidence("aggregate", 1000, 4000)
    direct, own = evidence("direct", 1000, 3000)
    child, nested = evidence("nested", 2000, 3000, session="worker")
    retry, repeated = evidence("another", 2000, 4000)
    inclusive = replace(
        inclusive,
        scope=UsageScope.INCLUSIVE,
        schema="aitm.effort.receipt/v3",
        tokens=TokenCounts(total_tokens=100),
    )
    snapshot = effort_snapshot(
        (parent, inclusive),
        (replace(direct, parent_attempt_id=parent.attempt_id), own),
        (replace(child, parent_attempt_id=parent.attempt_id), nested),
        (retry, repeated),
    )
    separate = rollup(snapshot, target())
    assert separate.total.working_wall is None
    assert separate.total.workflow_elapsed is None
    aligned = rollup(
        snapshot,
        target(),
        clocks={
            row.receipt.observation_id: ref("clock") for row in snapshot.attributed
        },
    )
    assert aligned.total.observed_tokens == 30
    assert aligned.total.inclusive_observations == 1
    assert aligned.total.usage_gaps == 1
    assert aligned.total.engaged == timedelta(seconds=4)
    assert aligned.total.working_wall == timedelta(seconds=3)
    assert aligned.by_role[Role.WORKER].observed_tokens == 30
    assert aligned.by_provider["codex"].observed_tokens == 30


def test_missing_time_unknown_counts_and_project_authority():
    enrolled, receipt = evidence("unknown")
    partial = replace(
        receipt, tokens=TokenCounts(), coverage=Availability.PARTIAL, ended_at=None
    )
    snapshot = effort_snapshot(
        (enrolled, partial),
        pending_enrollments=(replace(enrolled, attempt_id=uuid4()),),
    )
    assert rollup(snapshot, target()).total.observed_tokens is None
    assert rollup(snapshot, target()).total.engaged is None
    assert rollup(snapshot, target()).total.clock_gaps == 1
    assert rollup(snapshot, target()).total.price_gaps == 1
    assert rollup(snapshot, target()).unsettled_attempts == 1
    with pytest.raises(EffortError):
        rollup(snapshot, replace(target(), project_id=uuid4()))


def test_published_epic_trail_fixture(tmp_path):
    from aitm_usage.effort import Attribution

    path = Path(__file__).parent / "fixtures" / "effort" / "epic-trail-433.json"
    fixture = json.loads(path.read_text(encoding="utf-8"))
    expected = fixture["rollup"]
    stories = {name: index for index, name in enumerate(expected["children"], 1)}
    db = EffortStore(tmp_path / "effort.db", PROJECT)
    receipts = {}
    clocks = {}
    late = None
    for row in expected["observations"]:
        scope = row["original_scope"]
        provider = row["provider"]
        role = {
            "nested-worker": Role.WORKER,
            "late-attributed-research": Role.RESEARCHER,
            "control": Role.RESEARCHER,
        }.get(row["role"], row["role"])
        enrollment, receipt = evidence(
            row["native_turn_ref"],
            *row["time_ms"],
            session=row["session_ref"],
            story=stories.get(scope),
        )
        enrollment = replace(
            enrollment,
            role=Role(role),
            epic=435 if scope else None,
            parent_attempt_id=(
                receipts["parallel-worker-a-retry"].attempt_id
                if row["role"] == "nested-worker"
                else None
            ),
        )
        receipt = replace(
            receipt,
            turn=replace(receipt.turn, provider=provider),
            tokens=TokenCounts(total_tokens=row["observed_tokens"]),
            scope=(
                UsageScope.MIXED
                if row["exclusion_kind"] == "mixed-boundary"
                else UsageScope.BOUNDED
            ),
        )
        price = row["native_price"]
        if provider == "grok" and price:
            receipt = replace(
                receipt,
                schema="aitm.effort.receipt/v2",
                grok_cost_usd_ticks=price["value"],
                grok_cache_creation_tokens=row["tokens"]["cache_creation_input_tokens"],
            )
        receipts[row["attempt"]] = receipt
        clocks[receipt.observation_id] = ref("clock")
        db.enroll(enrollment)
        assignment = fixture["assignment_markers"].get(row["attempt"])
        if assignment and "start_ms" in assignment:
            db.mark_scope(marker(receipt, MarkerKind.START, assignment["start_ms"]))
            db.mark_scope(marker(receipt, MarkerKind.END, assignment["end_ms"]))
        db.ingest(receipt)
        if scope is None and row["effective_scope"]:
            late = Attribution(
                PROJECT,
                receipt.observation_id,
                435,
                stories[row["effective_scope"]],
                ref("link"),
            )
    assert late is not None
    db.handoff(
        Handoff(
            PROJECT,
            receipts["parallel-worker-b-handoff"].turn,
            receipts["parallel-successor"].turn,
            ref("handoff"),
        )
    )

    def compare(snapshot, selected, values, bounds=None):
        window = WorkflowWindow(ref("clock"), *map(instant, bounds)) if bounds else None
        actual = rollup(snapshot, selected, clocks=clocks, workflow=window).total
        assert actual.observations == values["observations"]
        assert actual.observed_tokens == values["observed_tokens"]
        assert actual.engaged == timedelta(milliseconds=values["engaged_ms"])
        assert actual.working_wall == timedelta(milliseconds=values["working_wall_ms"])
        if bounds:
            assert actual.workflow_elapsed == timedelta(
                milliseconds=values["workflow_elapsed_ms"]
            )

    compare(db.snapshot(), target(), fixture["late_attribution"]["before_epic"])
    assert db.attribute(late) == Disposition.INSERTED
    assert db.attribute(late) == Disposition.REPLAYED
    snapshot = db.snapshot()
    compare(
        snapshot,
        target(),
        expected["epic_inclusive"],
        (
            fixture["epic_workflow_markers"]["start_ms"],
            fixture["epic_workflow_markers"]["last_child_close_ms"],
        ),
    )
    epic = rollup(snapshot, target(), clocks=clocks)
    assert epic.total.boundary_gaps == 0
    assert epic.total.clock_gaps == 0
    assert epic.unassigned_observations == 0
    groups = {
        Role.ORCHESTRATOR: ("orchestrator",),
        Role.WORKER: ("worker", "nested-worker"),
        Role.REVIEWER: ("reviewer",),
        Role.RESEARCHER: ("late-attributed-research",),
    }
    for role, labels in groups.items():
        totals = epic.by_role[role]
        assert totals.observations == sum(
            expected["roles"][label]["observations"] for label in labels
        )
        assert totals.observed_tokens == sum(
            expected["roles"][label]["observed_tokens"] for label in labels
        )
        assert totals.engaged == timedelta(
            milliseconds=sum(expected["roles"][label]["engaged_ms"] for label in labels)
        )
        assert totals.working_wall == timedelta(
            milliseconds=expected["roles"][labels[0]]["working_wall_ms"]
        )
    for provider, totals in epic.by_provider.items():
        assigned = [
            row
            for row in expected["observations"]
            if row["provider"] == provider and row["effective_scope"]
        ]
        assert totals.observations == len(assigned)
        assert totals.observed_tokens == sum(row["observed_tokens"] for row in assigned)
    assert set(epic.by_provider) == {"codex", "claude", "grok"}
    for scope, values in expected["children"].items():
        compare(
            snapshot,
            target(stories[scope]),
            values,
            fixture["workflow_boundaries"][scope],
        )


def test_clock_domains_require_explicit_alignment():
    from aitm_usage.effort.store import Snapshot, StoryObservation

    one, first = evidence("first", 1000, 3000)
    two, second = evidence("second", 2000, 4000)
    second = replace(second, time_basis=TimeBasis.CALLER)
    snapshot = Snapshot(
        PROJECT,
        1,
        (one, two),
        tuple(
            StoryObservation(receipt, enrolled, 1, 435, None)
            for enrolled, receipt in ((one, first), (two, second))
        ),
        (),
        (),
    )
    totals = rollup(snapshot, target()).total
    assert totals.engaged is None
    assert totals.working_wall is None
    assert totals.clock_domains == 2
    workflow = WorkflowWindow(ref("clock"), instant(500), instant(5000))
    totals = rollup(snapshot, target(), workflow=workflow).total
    assert totals.observed_tokens == 20
    assert totals.workflow_elapsed is None
    assert totals.workflow_clock_gap
    clocks = {receipt.observation_id: ref("clock") for receipt in (first, second)}
    totals = rollup(snapshot, target(), clocks=clocks).total
    assert totals.engaged == timedelta(seconds=3)
    assert totals.working_wall == timedelta(seconds=3)


def test_inclusive_grok_receipt_round_trips_without_duplicating_price():
    from aitm_usage.effort.store import Snapshot, StoryObservation

    parent, inclusive = evidence("aggregate", 1000, 5000, session="parent")
    child, bounded = evidence("child", 2000, 3000, session="child")
    inclusive = replace(
        inclusive,
        turn=replace(inclusive.turn, provider="grok"),
        schema="aitm.effort.receipt/v3",
        scope=UsageScope.INCLUSIVE,
        tokens=TokenCounts(total_tokens=90),
        grok_cost_usd_ticks=400,
        grok_cache_creation_tokens=1,
    )
    assert UsageReceipt.from_json(inclusive.to_json()) == inclusive
    with pytest.raises(ValueError):
        replace(inclusive, schema="aitm.effort.receipt/v2")
    bounded = replace(
        bounded,
        turn=replace(bounded.turn, provider="grok"),
        schema="aitm.effort.receipt/v2",
        grok_cost_usd_ticks=0,
        grok_cache_creation_tokens=0,
    )
    snapshot = Snapshot(
        PROJECT,
        1,
        (parent, child),
        tuple(
            StoryObservation(receipt, enrolled, 1, 435, None)
            for enrolled, receipt in ((parent, inclusive), (child, bounded))
        ),
        (),
        (),
    )
    clocks = {receipt.observation_id: ref("clock") for receipt in (inclusive, bounded)}
    totals = rollup(snapshot, target(), clocks=clocks).total
    assert totals.observed_tokens == 10
    assert totals.engaged == timedelta(seconds=5)
    assert totals.working_wall == timedelta(seconds=4)
    assert totals.grok_cost_usd_ticks == 0
    assert totals.price_gaps == 1
    assert totals.inclusive_observations == 1


@pytest.mark.parametrize(
    ("started", "ended"),
    [(1000, 4000), (None, 900), (3000, None)],
    ids=["crossing", "partial-before", "partial-after"],
)
def test_receipt_crossing_comparable_markers_leaves_a_boundary_gap(started, ended):
    enrolled, receipt = evidence("crossing")
    receipt = replace(
        receipt,
        started_at=None if started is None else instant(started),
        ended_at=None if ended is None else instant(ended),
    )
    snapshot = effort_snapshot(
        (enrolled, receipt),
        markers=(
            marker(receipt, MarkerKind.START, 1000),
            marker(receipt, MarkerKind.END, 1500),
        ),
    )
    clocks = {receipt.observation_id: ref("clock")}
    totals = rollup(snapshot, target(), clocks=clocks).total
    assert totals.observed_tokens is None
    assert totals.engaged is None
    assert totals.working_wall is None
    assert totals.boundary_gaps == 1
    assert totals.usage_gaps == 1

    unaligned = rollup(snapshot, target()).total
    assert unaligned.observed_tokens == 10
    assert unaligned.boundary_gaps == 1


def test_handoff_rejects_wrong_project_time_and_conflicting_relink(tmp_path):
    store = EffortStore(tmp_path / "effort.db", PROJECT)
    turns = []
    for name, start, end in (
        ("predecessor", 2000, 3000),
        ("successor", 3000, 4000),
        ("early", 1000, 2000),
    ):
        enrollment, receipt = evidence(name, start, end, session=name)
        turns.append(receipt.turn)
        store.enroll(enrollment)
        first = marker(receipt, MarkerKind.START, start)
        final = marker(receipt, MarkerKind.END, end)
        with pytest.raises(EffortError):
            store.mark_scope(replace(first, project_id=uuid4()))
        store.mark_scope(first)
        assert (
            store.mark_scope(replace(first, at=instant(start + 1)))
            == Disposition.CONFLICTED
        )
        with pytest.raises(EffortError):
            store.mark_scope(replace(final, clock=ref("unaligned")))
        store.mark_scope(final)
        assert store.mark_scope(final) == Disposition.REPLAYED
    predecessor, successor, early = turns
    with pytest.raises(EffortError, match="Detach follows attach"):
        store.handoff(Handoff(PROJECT, predecessor, early, ref("invalid")))
    handoff = Handoff(PROJECT, predecessor, successor, ref("handoff"))
    with pytest.raises(EffortError):
        store.handoff(replace(handoff, project_id=uuid4()))
    assert store.handoff(handoff) == Disposition.INSERTED
    assert store.handoff(replace(handoff, proof=ref("new"))) == Disposition.CONFLICTED
