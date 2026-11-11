import subprocess
import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from tools.story_dashboard import timing
from tools.story_dashboard.attribution import (
    TimingFacts,
    TimingGap,
    TimingObservation,
    TimingScope,
    TimingSource,
    resolve_timing,
)
from tools.story_dashboard.evidence import (
    Estimate,
    Event,
    Gap,
    PlanningTree,
    Story,
    read_tree,
)

START = datetime(2026, 11, 10, 9, tzinfo=UTC)
PIN = "17761cc1928fd916cf32a9c078d4a742bfcb32b8"
ROOT = Path(__file__).resolve().parents[3]


def stamp(minute):
    return START + timedelta(minutes=minute)


def millis(minute):
    return int(stamp(minute).timestamp()) * 1000


def observation(
    key,
    start,
    end,
    *,
    story=186,
    actor="actor-a",
    phase="implement",
    role="implementer",
    attempt="attempt-a",
    turn="turn-a",
    kind="agent-turn",
    coverage="complete",
    checkpoint=None,
):
    return TimingObservation(
        ("v1", "aitm", key),
        TimingScope(story, "aitm", actor, phase, role, attempt),
        kind,
        None if start is None else millis(start),
        None if end is None else millis(end),
        turn,
        coverage,
        "verified-" + kind,
        "missing-boundary" if coverage == "partial" else None,
        (
            TimingSource(
                f".aitm/stories/001/{story}/attachments/timing/{key}-{story}.json",
                "a" * 64,
                f"manual:{key}",
                recorded_at=stamp(210),
                checkpoint_at=None if checkpoint is None else stamp(checkpoint),
            ),
        ),
    )


def event(story, minute, state, **data):
    return Event(
        story,
        "core.state.entered",
        stamp(minute),
        {"state": state} | data,
        f".aitm/stories/001/{story}/events.jsonl:{minute}",
        stamp(minute),
        None,
        0,
        None,
    )


def tree(
    *, as_of=240, states=None, events=(), estimates=None, gaps=(), descendants=None
):
    states = {181: "done", 186: "develop", 187: "develop"} if states is None else states
    if descendants is None:
        descendants = {181: (186, 187), 186: (), 187: ()}
    return PlanningTree(
        "a" * 40,
        START,
        stamp(as_of),
        {
            story: Story(
                story, str(story), state, None, f".aitm/stories/001/{story}/story.md"
            )
            for story, state in states.items()
        },
        events,
        estimates or {},
        {186: 181, 187: 181},
        descendants,
        (),
        (),
        None,
        gaps,
        {},
        {},
    )


def project(planning, *rows, gaps=(), readback=None):
    return timing.project_timing(
        planning, TimingFacts(rows, gaps, {}, readback or {}, planning.gaps)
    )


class TimingMetrics(unittest.TestCase):
    def test_parallel_wait_and_elapsed_scopes(self):
        rows = project(
            tree(descendants={181: (186, 187, 186), 186: (), 187: ()}),
            observation("a", 0, 90),
            observation("b", 30, 120, story=187, actor="actor-b"),
            observation(
                "coord", 150, 165, story=181, actor="actor-c", role="coordinator"
            ),
            observation("tool", 15, 25, kind="tool"),
            observation("unattended", 180, 200, kind="tool"),
            observation("wait-a", 120, 145, kind="owner-wait"),
            observation(
                "wait-b", 130, 150, story=187, actor="actor-b", kind="owner-wait"
            ),
            observation(
                "kickoff", 0, None, story=181, kind="workflow-start", phase="all-phase"
            ),
            observation(
                "delivery",
                None,
                165,
                story=181,
                kind="workflow-delivered",
                phase="all-phase",
            ),
        )
        epic = rows[181]
        self.assertEqual(epic.all_phase_elapsed.milliseconds, 9_900_000)
        self.assertEqual(epic.working_wall.milliseconds, 8_100_000)
        self.assertEqual(epic.actual.milliseconds, 11_700_000)
        self.assertEqual(epic.direct_actual.milliseconds, 900_000)
        self.assertEqual(epic.descendant_actual.milliseconds, 10_800_000)
        self.assertEqual(epic.owner_wait.milliseconds, 1_800_000)
        self.assertEqual(rows[186].owner_wait.milliseconds, 1_500_000)
        self.assertIsNone(epic.implementation_elapsed.milliseconds)
        self.assertEqual(epic.actual.coverage, "complete")
        self.assertEqual(epic.actual.evidence_through, stamp(165))
        self.assertEqual(epic.owner_wait.evidence_through, stamp(150))
        self.assertEqual(rows[186].actual.evidence_through, stamp(90))
        self.assertEqual(
            {source.source_ref for source in rows[186].actual.sources},
            {"manual:a", "manual:tool"},
        )
        self.assertEqual(
            [
                (row.scope.story, row.scope.role, row.milliseconds)
                for row in epic.contributions
            ],
            [
                (181, "coordinator", 900_000),
                (186, "implementer", 5_400_000),
                (187, "implementer", 5_400_000),
            ],
        )

    def test_exclusions_apply_only_to_the_evidenced_actor_and_direct_scope(self):
        rows = project(
            tree(),
            observation("a", 0, 15),
            observation("b", 15, 30, story=187),
            observation("c", 10, 25, actor="actor-c"),
            observation("wait", 10, 25, kind="owner-wait"),
            observation("other-role", 0, 10, kind="idle", role="reviewer"),
            observation("other-attempt", 0, 10, kind="idle", attempt="attempt-b"),
            observation("other-phase", 0, 10, kind="idle", phase="review"),
            observation("idle", 0, 2, kind="idle", phase=None, role=None, attempt=None),
        )
        self.assertEqual(rows[186].direct_actual.milliseconds, 1_380_000)
        self.assertEqual(rows[187].direct_actual.milliseconds, 900_000)
        self.assertEqual(rows[181].actual.milliseconds, 2_280_000)
        self.assertEqual(rows[181].working_wall.milliseconds, 1_680_000)
        self.assertEqual(rows[181].actual.coverage, "partial")
        self.assertEqual(rows[181].owner_wait.milliseconds, 900_000)

    def test_wait_watermark_missing_response_and_exact_start_pending(self):
        known = observation("known", 10, 20, kind="owner-wait")
        pending = observation(
            "pending",
            30,
            None,
            kind="pending-wait",
            turn="req-a",
            coverage="partial",
            checkpoint=35,
        )
        missing = observation(
            "missing",
            50,
            None,
            kind="owner-request",
            turn="req-b",
        )
        rows = project(
            tree(),
            known,
            pending,
            missing,
            observation(
                "same-point",
                35,
                None,
                story=187,
                kind="pending-wait",
                coverage="partial",
                checkpoint=35,
            ),
            observation(
                "no-checkpoint",
                45,
                None,
                story=187,
                kind="pending-wait",
                coverage="partial",
                turn="req-c",
            ),
        )
        self.assertEqual(rows[186].owner_wait.milliseconds, 900_000)
        self.assertEqual(rows[186].owner_wait.coverage, "partial")
        self.assertTrue(rows[186].owner_wait.pending)
        self.assertEqual(rows[186].owner_wait.evidence_through, stamp(50))
        self.assertIsNone(rows[187].owner_wait.milliseconds)
        self.assertEqual(rows[187].owner_wait.coverage, "unknown")
        self.assertTrue(rows[187].owner_wait.pending)
        self.assertEqual(rows[187].owner_wait.evidence_through, stamp(45))

        paired = project(
            tree(),
            observation("request", 30, None, kind="owner-request", turn="req-a"),
            observation("response", None, 40, kind="owner-response", turn="req-a"),
            pending,
        )[186].owner_wait
        self.assertEqual(paired.milliseconds, 600_000)
        self.assertFalse(paired.pending)
        self.assertEqual(paired.coverage, "complete")

        incomplete_resolution = project(
            tree(),
            pending,
            observation(
                "bad-response",
                None,
                None,
                kind="owner-response",
                turn="req-a",
                coverage="partial",
            ),
        )[186].owner_wait
        self.assertIsNone(incomplete_resolution.milliseconds)
        self.assertFalse(incomplete_resolution.pending)

        for coverage, amount in [("complete", 0), ("partial", None)]:
            with self.subTest(coverage=coverage):
                zero = project(
                    tree(),
                    observation(
                        "req-zero", 30, None, kind="owner-request", coverage=coverage
                    ),
                    observation("resp-zero", None, 30, kind="owner-response"),
                )[186].owner_wait
                self.assertEqual(zero.milliseconds, amount)

    def test_wait_scope_conflict_and_missing_exclusion_stay_partial(self):
        rows = project(
            tree(),
            observation("work", 0, 30),
            observation("request", 10, None, kind="owner-request", turn="req-a"),
            observation(
                "response",
                None,
                20,
                kind="owner-response",
                turn="req-a",
                phase="review",
            ),
        )
        self.assertIsNone(rows[186].owner_wait.milliseconds)
        self.assertEqual(rows[186].actual.milliseconds, 1_800_000)
        self.assertEqual(rows[186].actual.coverage, "partial")
        self.assertIn("owner-request-scope-conflict", rows[186].owner_wait.reasons)

        rows = project(
            tree(),
            observation("work", 0, 10),
            observation("late", 12, None, kind="owner-request", turn="req-a"),
            observation(
                "other-role",
                2,
                None,
                kind="owner-request",
                turn="req-b",
                role="reviewer",
            ),
        )
        self.assertEqual(rows[186].actual.coverage, "complete")
        self.assertIsNone(rows[186].owner_wait.milliseconds)

    def test_gap_in_workflow_state_does_not_hide_proven_elapsed(self):
        broken = replace(event(186, 15, "review"), data={"state": []})
        rows = project(
            tree(
                states={186: "done"},
                events=(event(186, 10, "develop"), broken, event(186, 20, "done")),
                gaps=(Gap(186, "invalid-state", broken.source),),
            ),
        )
        self.assertEqual(rows[186].implementation_elapsed.milliseconds, 600_000)
        self.assertEqual(rows[186].implementation_elapsed.coverage, "partial")
        self.assertIn("invalid-state", rows[186].implementation_elapsed.reasons)

    def test_elapsed_age_and_attempt_selection(self):
        states = {181: "done", 186: "develop", 187: "done"}
        events = (
            event(186, 10, "develop"),
            event(186, 20, "done"),
            event(186, 30, "backlog"),
            event(186, 40, "develop"),
            event(186, 50, "test"),
            event(186, 55, "develop", **{"from": "test"}),
            event(187, 30, "develop", attempt="attempt-a"),
            event(187, 45, "done", attempt="attempt-b"),
        )
        rows = project(
            tree(states=states, events=events),
            observation(
                "start", 5, None, story=186, kind="workflow-start", phase="all-phase"
            ),
            observation(
                "start-epic",
                1,
                None,
                story=181,
                kind="workflow-start",
                phase="all-phase",
            ),
        )
        self.assertIsNone(rows[181].all_phase_elapsed.milliseconds)
        self.assertIsNone(rows[181].all_phase_age.milliseconds)
        self.assertIsNone(rows[186].all_phase_elapsed.milliseconds)
        self.assertEqual(rows[186].all_phase_age.milliseconds, 14_100_000)
        self.assertEqual(rows[186].implementation_age.milliseconds, 12_000_000)
        self.assertEqual(rows[186].implementation_age.evidence_through, stamp(40))
        self.assertIsNone(rows[187].all_phase_elapsed.milliseconds)
        self.assertIsNone(rows[187].implementation_elapsed.milliseconds)
        self.assertIsNone(rows[187].implementation_age.milliseconds)

    def test_later_typed_attempt_has_age_until_its_own_delivery(self):
        rows = (
            observation("start-old", 10, None, kind="workflow-start"),
            observation("finish-old", None, 25, kind="workflow-delivered"),
            observation(
                "start-current", 30, None, kind="workflow-start", attempt="attempt-b"
            ),
        )
        active = project(tree(), *rows)[186]
        self.assertIsNone(active.implementation_elapsed.milliseconds)
        self.assertEqual(active.implementation_age.milliseconds, 12_600_000)
        self.assertEqual(active.implementation_age.evidence_through, stamp(30))

        delivered = project(
            tree(states={186: "done"}),
            *rows,
            observation(
                "finish-current",
                None,
                45,
                kind="workflow-delivered",
                attempt="attempt-b",
            ),
        )[186]
        self.assertEqual(delivered.implementation_elapsed.milliseconds, 900_000)
        self.assertIsNone(delivered.implementation_age.milliseconds)

    def test_known_wait_phase_against_unknown_work_phase_marks_partial(self):
        row = project(
            tree(),
            observation("work", 5, 25, phase=None),
            observation("wait", 10, 20, kind="owner-wait"),
        )[186]
        self.assertEqual(row.actual.milliseconds, 1_200_000)
        self.assertEqual(row.actual.coverage, "partial")
        self.assertIn("unresolved-work-exclusion-scope", row.actual.reasons)
        self.assertEqual(row.owner_wait.milliseconds, 600_000)
        self.assertEqual(row.owner_wait.coverage, "complete")

    def test_plan_reset_does_not_resurrect_implementation_age(self):
        row = project(
            tree(
                states={186: "plan"},
                events=(
                    event(186, 10, "develop", attempt="attempt-a"),
                    event(186, 20, "plan", **{"from": "develop"}),
                ),
            ),
            observation("old-start", 10, None, kind="workflow-start"),
            observation("kickoff", 1, None, kind="workflow-start", phase="all-phase"),
        )[186]
        self.assertIsNone(row.implementation_age.milliseconds)
        self.assertIsNone(row.implementation_elapsed.milliseconds)
        self.assertEqual(row.all_phase_age.milliseconds, 14_340_000)

    def test_backlog_and_ready_for_plan_can_have_all_phase_age(self):
        for state in ("backlog", "ready-for-plan"):
            with self.subTest(state=state):
                row = project(
                    tree(states={186: state}),
                    observation(
                        "kickoff", 10, None, kind="workflow-start", phase="all-phase"
                    ),
                    observation("old-start", 20, None, kind="workflow-start"),
                )[186]
                self.assertEqual(row.all_phase_age.milliseconds, 13_800_000)
                self.assertIsNone(row.implementation_age.milliseconds)

    def test_conflicting_same_attempt_delivery_boundaries_remain_unknown(self):
        start = observation("start", 10, None, kind="workflow-start")
        first = observation("delivery-a", None, 20, kind="workflow-delivered")
        second = observation("delivery-b", None, 25, kind="workflow-delivered")
        conflict = project(tree(), start, first, second)[186]
        self.assertIsNone(conflict.implementation_elapsed.milliseconds)
        self.assertIsNone(conflict.implementation_age.milliseconds)
        self.assertIn(
            "conflicting-implementation-finish", conflict.implementation_elapsed.reasons
        )
        self.assertEqual(
            {ref.source_ref for ref in conflict.implementation_elapsed.sources},
            {"manual:start", "manual:delivery-a", "manual:delivery-b"},
        )

        corroborated = project(
            tree(), start, first, replace(second, end_ms=millis(20))
        )[186]
        self.assertEqual(corroborated.implementation_elapsed.milliseconds, 600_000)
        self.assertEqual(corroborated.implementation_elapsed.coverage, "complete")

    def test_conflicting_same_attempt_starts_remain_unknown(self):
        row = project(
            tree(),
            observation("start-a", 10, None, kind="workflow-start"),
            observation("start-b", 12, None, kind="workflow-start"),
            observation("delivery", None, 20, kind="workflow-delivered"),
        )[186]
        self.assertIsNone(row.implementation_elapsed.milliseconds)
        self.assertIsNone(row.implementation_age.milliseconds)
        self.assertIn(
            "conflicting-implementation-start", row.implementation_elapsed.reasons
        )

    def test_wholly_held_turn_gap_does_not_change_independent_coverage(self):
        held = observation("held", 10, 20)
        for code in ("cross-story-overlap", "legacy-overlap"):
            with self.subTest(code=code):
                gap = TimingGap(
                    186,
                    code,
                    held.scope,
                    held.identity,
                    held.start_ms,
                    held.end_ms,
                    held.sources,
                )
                row = project(
                    tree(
                        states={186: "done"},
                        events=(event(186, 5, "develop"), event(186, 25, "done")),
                    ),
                    observation("wait", 8, 9, kind="owner-wait"),
                    gaps=(gap,),
                )[186]
                self.assertIsNone(row.actual.milliseconds)
                self.assertIn(code, row.actual.reasons)
                self.assertEqual(row.owner_wait.milliseconds, 60_000)
                self.assertEqual(row.owner_wait.coverage, "complete")
                self.assertEqual(row.implementation_elapsed.milliseconds, 1_200_000)
                self.assertEqual(row.implementation_elapsed.coverage, "complete")

    def test_coverage_keeps_attribution_and_ancestry_gaps(self):
        work = observation("work", 5, 15)
        held = TimingGap(
            186,
            "cross-story-overlap",
            work.scope,
            work.identity,
            millis(15),
            millis(20),
            work.sources,
        )
        rows = project(
            tree(
                gaps=(Gap(181, "ancestry-missing", ".aitm/stories/001/188/story.md"),)
            ),
            work,
            gaps=(held,),
        )
        self.assertEqual(rows[186].actual.milliseconds, 600_000)
        self.assertEqual(rows[186].actual.coverage, "partial")
        self.assertIn("cross-story-overlap", rows[186].actual.reasons)
        self.assertEqual(rows[181].actual.coverage, "partial")
        self.assertIn("ancestry-missing", rows[181].actual.reasons)
        self.assertIn("unmeasured-descendant", rows[181].actual.reasons)
        self.assertIsNone(rows[187].actual.milliseconds)

    def test_usage_receipt_gaps_do_not_change_timing_coverage(self):
        usage = replace(
            event(186, 20, "review"),
            kind="core.evidence.recorded",
            data={
                "kind": "story-usage-receipt",
                "path": "attachments/timing/batch-186.json",
            },
        )
        receipt_path = ".aitm/stories/001/186/attachments/timing/batch-186.json"
        work = observation("work", 5, 15)
        pinned = tree(
            events=(usage,),
            gaps=(Gap(186, "receipt-missing", receipt_path),),
        )
        self.assertEqual(project(pinned, work)[186].actual.coverage, "complete")

        timing_claim = replace(
            usage,
            source=usage.source + "1",
            data=usage.data | {"kind": "story-timing-receipt"},
        )
        conflicting = replace(
            pinned,
            events=(usage, timing_claim),
            gaps=(Gap(186, "registration-conflict", usage.source),),
        )
        self.assertEqual(project(conflicting, work)[186].actual.coverage, "partial")

    def test_conflicting_typed_work_dimensions_are_counted_once(self):
        row = project(
            tree(), observation("a", 0, 10), observation("b", 5, 15, phase="review")
        )[186]
        self.assertEqual(row.actual.milliseconds, 900_000)
        self.assertEqual(
            {part.scope.phase: part.milliseconds for part in row.contributions},
            {"implement": 300_000, None: 300_000, "review": 300_000},
        )
        self.assertFalse(row.calibration.eligible)

    def test_calibration_requires_exact_estimate_scope_and_complete_actual(self):
        estimate_event = replace(
            event(186, 0, "develop"),
            kind="core.estimate.set",
            data={
                "scope": {
                    "phase": "implement",
                    "roles": ["implementer"],
                    "actors": ["actor-a"],
                    "attempt": "attempt-a",
                    "basis": "verified-agent-turn",
                }
            },
        )
        estimate = Estimate(
            Decimal("1.25"), "S", "implement", ("implementer",), estimate_event.source
        )
        work = observation("work", 10, 20)
        base = tree(
            states={186: "done"},
            events=(
                estimate_event,
                event(186, 5, "develop", attempt="attempt-a"),
                event(186, 25, "done", attempt="attempt-a"),
            ),
            estimates={186: estimate},
        )
        for change, eligible in [
            ({}, True),
            ({"scope": replace(work.scope, phase="review")}, False),
            ({"scope": replace(work.scope, role="reviewer")}, False),
            ({"scope": replace(work.scope, attempt="attempt-b")}, False),
            ({"scope": replace(work.scope, actor="actor-b")}, False),
            ({"basis": "other-basis"}, False),
            ({"coverage": "partial"}, False),
        ]:
            with self.subTest(change=change):
                projected = project(base, replace(work, **change))[186]
                self.assertEqual(projected.calibration.eligible, eligible)
                self.assertEqual(
                    projected.calibration.estimate_source, estimate_event.source
                )
        missing = project(replace(base, events=()), work)[186]
        self.assertFalse(missing.calibration.eligible)
        open_attempt = project(replace(base, events=base.events[:-1]), work)[186]
        self.assertFalse(open_attempt.calibration.eligible)
        outside_attempt = project(base, observation("late", 20, 30))[186]
        self.assertFalse(outside_attempt.calibration.eligible)

    def test_real_seed_parity_at_historical_pin(self):
        available = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", PIN + "^{commit}"],
            capture_output=True,
            check=False,
        )
        if available.returncode:
            self.skipTest("historical planning commit is absent from this checkout")
        pinned = read_tree(ROOT, PIN, datetime(2026, 11, 10, 21, tzinfo=UTC))
        facts = resolve_timing(pinned)
        self.assertEqual(len(facts.legacy_readback), 10)
        spans = sorted(
            (row.scope.actor, row.start_ms, row.end_ms)
            for row in facts.observations
            if row.identity[0] == "legacy"
        )
        self.assertEqual(len(spans), 114)
        for (actor, _, end), (next_actor, next_start, _) in zip(spans, spans[1:]):
            if actor == next_actor:
                self.assertLessEqual(end, next_start)

        projected = timing.project_timing(pinned, facts)
        for story, readback in facts.legacy_readback.items():
            with self.subTest(story=story):
                self.assertEqual(
                    tuple(
                        child
                        for child in pinned.descendants[story]
                        if child in facts.legacy_readback
                    ),
                    readback.counted_children,
                )
                row = projected[story]
                self.assertEqual(row.direct_actual.milliseconds, readback.direct_ms)
                self.assertEqual(row.actual.milliseconds, readback.inclusive_ms)
                self.assertEqual(row.actual.coverage, "partial")
                self.assertEqual(row.actual.evidence_through, readback.evidence_through)
                self.assertTrue(
                    all(part.scope.phase is None for part in row.contributions)
                )
                self.assertFalse(row.calibration.eligible)
        self.assertEqual(projected[111].implementation_elapsed.milliseconds, 774_000)
        self.assertEqual(projected[111].implementation_elapsed.coverage, "complete")
        self.assertIsNone(projected[111].all_phase_elapsed.milliseconds)

        changed = replace(pinned, descendants=pinned.descendants | {100: (111,)})
        changed_actual = timing.project_timing(changed, facts)[100].actual
        self.assertEqual(changed_actual.milliseconds, 6_865_084)
        self.assertIn("legacy-descendants-changed", changed_actual.reasons)


if __name__ == "__main__":
    unittest.main()
