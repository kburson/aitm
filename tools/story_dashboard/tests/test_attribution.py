import json
import unittest
from dataclasses import replace
from datetime import datetime
from unittest.mock import patch

import test_evidence as fixture

from tools.story_dashboard import attribution, evidence


def utc(minute):
    return f"2026-11-10T19:{minute:02d}:00Z"


def millis(minute):
    return int(datetime.fromisoformat(utc(minute)).timestamp()) * 1000


def observation(key, start, end, **overrides):
    return {
        "observation_id": key,
        "actor": "actor-a",
        "turn": "turn-a",
        "phase": "implement",
        "role": "implementer",
        "attempt": "attempt-a",
        "kind": "agent-turn",
        "coverage": "complete",
        "basis": "verified-turn",
        "start_utc": None if start is None else utc(start),
        "end_utc": None if end is None else utc(end),
    } | overrides


class TimingAttribution(unittest.TestCase):
    def setUp(self):
        self.git = fixture.PlanningFixture()
        self.git.setUp()
        self.addCleanup(self.git.doCleanups)
        self.git.story(181, children=(186, 187, 188))
        for story in (186, 187, 188):
            self.git.story(story, parent=181)

    def receipt(
        self, story, batch, rows, *, project="aitm", recorded=fixture.EARLIER, **fields
    ):
        value = {
            "schema": evidence.TIMING_SCHEMA,
            "project": project,
            "subject": story,
            "batch": batch,
            "recorded_at_utc": recorded,
            "source": {"ref": f"manual:{batch}"},
            "observations": rows,
        } | fields
        payload = fixture.raw(value)
        digest = fixture.digest(payload)
        path = f"attachments/timing/{batch}-{story}.json"
        self.git.put(path, payload, story)
        self.git.append(
            story,
            fixture.event(
                story,
                "core.evidence.recorded",
                {
                    "kind": "story-timing-receipt",
                    "path": path,
                    "sha256": digest,
                    "scope": {"story": story, "project": project},
                },
                ts=recorded,
            ),
        )
        return digest

    def load(self):
        return evidence.read_tree(self.git.repo, self.git.commit(), fixture.AS_OF)

    def seed(self, payload, *, register=True, event_digest=None):
        self.git.put(evidence.LEGACY_PATH, payload, 181)
        if register:
            self.git.append(
                181,
                fixture.event(
                    181,
                    "core.evidence.recorded",
                    {
                        "kind": "historical-actual-backfill",
                        "evidence": [evidence.LEGACY_PATH],
                        "receipt_sha256": event_digest or fixture.digest(payload),
                    },
                ),
            )

    def test_stable_observation_and_seed_overlap(self):
        row = observation("stable", 0, 10)
        self.receipt(186, "capture-a", [row])
        self.receipt(
            186,
            "capture-b",
            [row | {"start_utc": utc(0).replace("Z", "+00:00")}],
            recorded=fixture.STAMP,
        )
        tree = self.load()
        facts = attribution.resolve_timing(tree)
        self.assertEqual(len(facts.observations), 1)
        found = facts.observations[0]
        self.assertEqual(found.identity, ("v1", "aitm", "stable"))
        self.assertEqual(found.scope.story, 186)
        self.assertEqual(found.scope.role, "implementer")
        self.assertEqual(len(found.sources), 2)
        self.assertEqual(found.recorded_at, datetime.fromisoformat(fixture.EARLIER))
        self.assertEqual(
            facts,
            attribution.resolve_timing(replace(tree, receipts=tree.receipts[::-1])),
        )

        self.receipt(187, "scope-conflict", [row | {"role": "reviewer"}])
        self.receipt(186, "role-conflict", [row | {"role": "coordinator"}])
        self.receipt(186, "payload-conflict", [row | {"end_utc": utc(11)}])
        held = attribution.resolve_timing(self.load())
        self.assertFalse(held.observations)
        self.assertEqual(
            {(g.story, g.scope.role, g.code) for g in held.gaps},
            {
                (186, "implementer", "identity-conflict"),
                (187, "reviewer", "identity-conflict"),
                (186, "coordinator", "identity-conflict"),
            },
        )

    def test_cross_story_overlap_holds_only_the_shared_time(self):
        self.receipt(186, "first", [observation("first", 0, 10)])
        self.receipt(187, "second", [observation("second", 5, 15)])
        self.receipt(188, "unattended", [observation("unattended", 1, 14, kind="tool")])
        self.receipt(186, "in-turn", [observation("in-turn", 2, 4, kind="tool")])
        self.receipt(188, "parallel", [observation("parallel", 5, 14, actor="actor-b")])
        self.receipt(
            188, "other-project", [observation("first", 3, 14)], project="other"
        )
        facts = attribution.resolve_timing(self.load())
        spans = {
            (o.identity[1], o.identity[-1]): (o.start_ms, o.end_ms, o.coverage)
            for o in facts.observations
        }
        self.assertEqual(
            spans,
            {
                ("aitm", "first"): (millis(0), millis(5), "partial"),
                ("aitm", "second"): (millis(10), millis(15), "partial"),
                ("aitm", "unattended"): (millis(1), millis(14), "complete"),
                ("aitm", "in-turn"): (millis(2), millis(4), "complete"),
                ("aitm", "parallel"): (millis(5), millis(14), "complete"),
                ("other", "first"): (millis(3), millis(14), "complete"),
            },
        )
        self.assertEqual(
            {(g.story, g.code, g.start_ms, g.end_ms) for g in facts.gaps},
            {
                (186, "cross-story-overlap", millis(5), millis(10)),
                (187, "cross-story-overlap", millis(5), millis(10)),
            },
        )
        scope = next(
            o.scope
            for o in facts.observations
            if o.identity[-1] == "first" and o.scope.story == 186
        )
        self.assertEqual(facts.scopes[scope].coverage, "partial")

    def test_multiple_overlaps_leave_each_unaffected_fragment(self):
        self.receipt(186, "long", [observation("long", 0, 20)])
        self.receipt(187, "two", [observation("a", 3, 5), observation("b", 9, 12)])
        self.receipt(188, "touching", [observation("touch", 20, 21)])
        facts = attribution.resolve_timing(self.load())
        self.assertEqual(
            [
                (o.start_ms, o.end_ms)
                for o in facts.observations
                if o.identity[-1] == "long"
            ],
            [
                (millis(0), millis(3)),
                (millis(5), millis(9)),
                (millis(12), millis(20)),
            ],
        )
        self.assertEqual(
            {o.identity[-1] for o in facts.observations}, {"long", "touch"}
        )

    def test_a_held_identity_can_still_expose_a_cross_story_conflict(self):
        self.receipt(186, "ambiguous-a", [observation("reused", 0, 6)])
        self.receipt(186, "ambiguous-b", [observation("reused", 1, 6)])
        self.receipt(187, "different-key", [observation("different", 4, 10)])
        facts = attribution.resolve_timing(self.load())
        self.assertEqual(
            [(o.scope.story, o.start_ms, o.end_ms) for o in facts.observations],
            [(187, millis(6), millis(10))],
        )
        self.assertEqual(
            {(g.story, g.code) for g in facts.gaps},
            {
                (186, "identity-conflict"),
                (187, "cross-story-overlap"),
            },
        )

    def test_pending_checkpoint_and_incomplete_evidence(self):
        start = observation("start", 0, None, kind="workflow-start")
        waiting = observation(
            "waiting",
            2,
            None,
            kind="pending-wait",
            coverage="partial",
            missing_reason="awaiting-response",
        )
        missing = observation(
            "missing",
            None,
            None,
            kind="missing",
            coverage="unknown",
            missing_reason="lost-endpoints",
        )
        self.receipt(186, "delayed", [start, waiting, missing], recorded=fixture.STAMP)
        facts = attribution.resolve_timing(self.load())
        by_key = {o.identity[-1]: o for o in facts.observations}
        self.assertEqual(
            by_key["waiting"].evidence_through, datetime.fromisoformat(utc(2))
        )
        self.assertEqual(by_key["waiting"].recorded_at, fixture.AS_OF)
        self.assertIsNone(by_key["missing"].evidence_through)
        self.assertIsNone(by_key["start"].end_ms)
        self.assertTrue(any(g.code == "missing-evidence" for g in facts.gaps))
        self.receipt(186, "checkpoint-a", [waiting | {"recorded_at_utc": utc(10)}])
        self.receipt(186, "checkpoint-b", [waiting | {"recorded_at_utc": utc(15)}])
        pending = next(
            o
            for o in attribution.resolve_timing(self.load()).observations
            if o.kind == "pending-wait"
        )
        self.assertEqual(pending.recorded_at, datetime.fromisoformat(utc(10)))
        self.assertEqual(pending.evidence_through, datetime.fromisoformat(utc(15)))

    def test_unsupported_supersession_holds_only_bound_target(self):
        target = self.receipt(186, "target", [observation("original", 0, 3)])
        other = self.receipt(187, "other", [observation("other", 4, 6)])
        self.receipt(186, "bound", [observation("new", 0, 4)], supersedes=target)
        self.receipt(188, "foreign", [observation("foreign", 4, 6)], supersedes=other)
        self.receipt(188, "absent", [observation("absent", 7, 9)], supersedes="a" * 64)
        facts = attribution.resolve_timing(self.load())
        self.assertEqual([o.identity[-1] for o in facts.observations], ["other"])
        self.assertEqual(
            {(g.story, g.identity[-1], g.code) for g in facts.gaps},
            {
                (186, "original", "unsupported-revision"),
                (186, "new", "unsupported-revision"),
                (188, "foreign", "unsupported-revision"),
                (188, "absent", "unsupported-revision"),
            },
        )

    def test_legacy_admission_and_overlap_preserve_unaffected_direct_evidence(self):
        seed = fixture.raw(
            {
                "schema": "aitm.story-actual-backfill/v0",
                "story": 181,
                "evidence_through_utc": utc(20),
                "entries": {
                    "186": {
                        "direct": {"milliseconds": 600000},
                        "milliseconds": 900000,
                        "counted_children": [187],
                        "coverage": "Partial",
                        "direct_intervals": [
                            {
                                "actor": "legacy-a",
                                "turn": "legacy-turn",
                                "start": utc(0),
                                "end": utc(10),
                                "milliseconds": 600000,
                                "source": "retained turn",
                                "reason": "original basis",
                            }
                        ],
                    }
                },
            }
        )
        self.receipt(
            186,
            "new",
            [observation("later", 5, 15), observation("tool", 1, 4, kind="tool")],
        )
        seed_digest = fixture.digest(seed)
        with (
            patch.object(evidence, "LEGACY_SHA256", seed_digest),
            patch.object(attribution, "LEGACY_SHA256", seed_digest),
        ):
            self.seed(seed, register=False)
            unregistered = attribution.resolve_timing(self.load())
            self.assertFalse(unregistered.legacy_readback)
            self.seed(seed, event_digest="f" * 64)
            rejected = attribution.resolve_timing(self.load())
            self.assertFalse(rejected.legacy_readback)
            self.assertTrue(rejected.input_gaps)
            # Replace the fixture's invalid journal with the one valid registration.
            (self.git.root(181) / "events.jsonl").write_text("")
            self.seed(seed)
            facts = attribution.resolve_timing(self.load())
        historical = next(o for o in facts.observations if o.identity[0] == "legacy")
        self.assertEqual(
            (historical.start_ms, historical.end_ms), (millis(0), millis(5))
        )
        self.assertEqual(
            (historical.scope.phase, historical.scope.role, historical.scope.attempt),
            (None, None, None),
        )
        self.assertEqual(historical.evidence_through, datetime.fromisoformat(utc(20)))
        self.assertEqual(historical.basis, "retained turn")
        self.assertEqual(historical.sources[0].reason, "original basis")
        later = next(o for o in facts.observations if o.identity[-1] == "later")
        self.assertEqual(
            (later.start_ms, later.end_ms, later.coverage),
            (millis(10), millis(15), "partial"),
        )
        self.assertEqual(len([g for g in facts.gaps if g.code == "legacy-overlap"]), 2)
        readback = facts.legacy_readback[186]
        self.assertEqual(
            (readback.direct_ms, readback.inclusive_ms, readback.counted_children),
            (600000, 900000, (187,)),
        )

    def test_bad_legacy_format_leaves_v1_observations_available(self):
        self.receipt(186, "v1", [observation("valid", 0, 3)])
        payload = json.dumps({"schema": "unexpected"}).encode()
        self.seed(payload)
        digest = fixture.digest(payload)
        with (
            patch.object(evidence, "LEGACY_SHA256", digest),
            patch.object(attribution, "LEGACY_SHA256", digest),
        ):
            facts = attribution.resolve_timing(self.load())
        self.assertEqual([o.identity[-1] for o in facts.observations], ["valid"])
        self.assertEqual(
            [(g.story, g.code) for g in facts.gaps], [(181, "invalid-legacy-seed")]
        )
