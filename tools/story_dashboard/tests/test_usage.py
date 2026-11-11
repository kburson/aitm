import unittest
from dataclasses import replace
from datetime import datetime
from decimal import Decimal, localcontext

import test_evidence as fixture

from tools.story_dashboard import evidence

SELECTOR = fixture.usage()["selector"]
LATER = "2026-11-10T20:30:00Z"


class UsageSelection(unittest.TestCase):
    def setUp(self):
        self.git = fixture.PlanningFixture()
        self.git.setUp()
        self.addCleanup(self.git.doCleanups)

    def usage_receipt(
        self,
        story,
        batch,
        *,
        price="0.10",
        selector=SELECTOR,
        coverage="complete",
        source_digest="a" * 64,
        recorded=fixture.EARLIER,
        supersedes=None,
        operator="operator-1",
        unregistered=False,
        mutate=None,
    ):
        value = fixture.usage(batch)
        value.update(
            project=selector["project"],
            subject=story,
            recorded_at_utc=recorded,
            source={"sha256": source_digest},
            selector=selector.copy(),
            usage={"tokens": {"input": 125, "output": 75}, "priced_usd": price},
            coverage=coverage,
        )
        value["verification"].update(
            verified_story=story,
            verified_at_utc=selector["cutoff_utc"],
            source_report_id=selector["report_id"],
            source_sha256=source_digest,
            selector=selector.copy(),
            pricing_basis=selector["pricing_basis"],
            coverage=coverage,
            sanitized_data_sha256=fixture.digest(fixture.raw(value["usage"])),
        )
        if supersedes is not None:
            value["supersedes"] = supersedes
        if mutate is not None:
            mutate(value)
        payload = fixture.raw(value)
        digest = fixture.digest(payload)
        path = f"attachments/timing/{batch}-{story}.json"
        self.git.put(path, payload, story)
        event = fixture.event(
            story,
            "core.evidence.recorded",
            {
                "kind": "story-usage-receipt",
                "path": path,
                "sha256": digest,
                "scope": {"story": story, "project": selector["project"]},
            },
            ts=recorded,
        )
        if operator is None:
            event["actor"].pop("on-behalf-of")
        else:
            event["actor"]["on-behalf-of"] = operator
        if not unregistered:
            self.git.append(story, event)
        return digest, event

    def tree(self):
        return evidence.read_tree(self.git.repo, self.git.commit(), fixture.AS_OF)

    def project(self, tree, selector=SELECTOR):
        from tools.story_dashboard import usage

        parsed = None if selector is None else usage.ReportSelector.from_dict(selector)
        return usage.select_usage(tree, parsed)

    def assert_unknown(self, measure):
        self.assertIsNone(measure.priced_usd)
        self.assertEqual(measure.coverage, "unknown")

    def test_select_one_registered_usage_report(self):
        self.git.story(181, children=(186, 187, 188))
        self.git.story(186, parent=181, children=(189,))
        self.git.story(187, parent=181)
        self.git.story(188, parent=181)
        self.git.story(189, parent=186)
        self.git.story(190)
        old, original = self.usage_receipt(186, "original")
        self.git.append(186, original)
        revised, revision = self.usage_receipt(
            186, "revision", price="0.20", supersedes=old, recorded=LATER
        )
        self.git.append(186, revision)
        direct, _ = self.usage_receipt(181, "epic", price="0.01")
        partial, _ = self.usage_receipt(
            188, "partial", price="0.03", coverage="partial"
        )
        nested, _ = self.usage_receipt(189, "nested", price="0.04")
        self.usage_receipt(190, "conflict-a")
        self.usage_receipt(190, "conflict-b", price="0.02")
        alternate = SELECTOR | {
            "report_id": "monitor-export-2",
            "cutoff_utc": LATER,
            "rate_card": "rates-2",
        }
        alternate_digest, _ = self.usage_receipt(
            186, "alternate", selector=alternate, price="7.30", recorded=LATER
        )
        # A repeated reference to the same nested descendant cannot inflate totals.
        tree = self.tree()
        self.assertEqual(tree.descendants[186], (189,))
        tree = replace(
            tree, descendants=tree.descendants | {181: (186, 187, 188, 189, 189)}
        )
        view = self.project(tree)
        self.assertEqual(view.source_sha256, "a" * 64)
        self.assertEqual(
            view.resolved_receipt_digests,
            tuple(sorted((direct, revised, partial, nested))),
        )
        self.assertEqual(view.stories[186].direct.priced_usd, Decimal("0.20"))
        self.assertEqual(view.stories[186].direct.receipt_digests, (revised,))
        self.assertEqual(view.stories[186].inclusive.priced_usd, Decimal("0.24"))
        self.assertEqual(view.stories[188].direct.coverage, "partial")
        self.assert_unknown(view.stories[187].direct)
        self.assert_unknown(view.stories[190].direct)
        self.assertEqual(view.stories[181].direct.coverage, "complete")
        rollup = view.stories[181].inclusive
        self.assertEqual(rollup.priced_usd, Decimal("0.28"))
        self.assertEqual(rollup.coverage, "partial")
        self.assertEqual(rollup.basis, "api-equivalent")
        self.assertEqual(
            rollup.evidence_through, datetime.fromisoformat(SELECTOR["cutoff_utc"])
        )
        self.assertEqual(rollup.receipt_digests, view.resolved_receipt_digests)
        self.assertIn(187, {gap.story for gap in rollup.gaps})
        other = self.project(tree, alternate)
        self.assertEqual(other.resolved_receipt_digests, (alternate_digest,))
        self.assertEqual(other.stories[186].direct.priced_usd, Decimal("7.30"))
        self.assert_unknown(other.stories[181].direct)
        for no_report in (None, SELECTOR | {"cutoff_utc": fixture.FUTURE}):
            missing = self.project(tree, no_report)
            self.assertEqual(missing.resolved_receipt_digests, ())
            self.assert_unknown(missing.stories[181].inclusive)

    def test_reference_only_source_cannot_assure_cost(self):
        self.git.story(186)
        digest, _ = self.usage_receipt(
            186,
            "reference-only",
            mutate=lambda value: value.update(source={"ref": "monitor:fixed-export"}),
        )
        tree = self.tree()
        self.assertEqual(
            tuple(receipt.registration.sha256 for receipt in tree.receipts), (digest,)
        )
        view = self.project(tree)
        self.assert_unknown(view.stories[186].direct)
        self.assert_unknown(view.stories[186].inclusive)
        self.assertEqual(view.resolved_receipt_digests, ())

    def test_missing_or_mismatched_verification_holds_cost(self):
        cases = (
            (
                "no-verification",
                lambda value: value.pop("verification"),
                "operator-1",
                False,
            ),
            (
                "flag",
                lambda value: value.update(verification=True),
                "operator-1",
                False,
            ),
            (
                "digest",
                lambda value: value["verification"].update(source_sha256="b" * 64),
                "operator-1",
                False,
            ),
            (
                "selector",
                lambda value: value["verification"]["selector"].update(rate_card="bad"),
                "operator-1",
                False,
            ),
            (
                "story",
                lambda value: value["verification"].update(verified_story=1),
                "operator-1",
                False,
            ),
            (
                "payload",
                lambda value: value["usage"].update(priced_usd="0.90"),
                "operator-1",
                False,
            ),
            ("operator", None, "different-operator", False),
            ("missing-principal", None, None, False),
            ("unregistered", None, "operator-1", True),
        )
        for story, (name, mutate, operator, unregistered) in enumerate(
            cases, start=200
        ):
            self.git.story(story)
            self.usage_receipt(
                story, name, mutate=mutate, operator=operator, unregistered=unregistered
            )
        view = self.project(self.tree())
        self.assertEqual(view.resolved_receipt_digests, ())
        for story, (name, _, _, _) in enumerate(cases, start=200):
            with self.subTest(name=name):
                self.assert_unknown(view.stories[story].direct)
                self.assert_unknown(view.stories[story].inclusive)

    def test_conflicting_verified_source_digests_hold_report(self):
        self.git.story(186)
        self.git.story(187)
        self.usage_receipt(186, "source-a")
        self.usage_receipt(187, "source-b", source_digest="b" * 64)
        view = self.project(self.tree())
        self.assertIsNone(view.source_sha256)
        self.assertEqual(view.resolved_receipt_digests, ())
        self.assert_unknown(view.stories[186].direct)
        self.assert_unknown(view.stories[187].direct)

    def test_supersession_requires_one_same_scope_chronological_chain(self):
        self.git.story(186)
        self.git.story(187)
        self.git.story(188)
        self.git.story(189)
        self.git.story(190)
        old, _ = self.usage_receipt(186, "fork-root")
        self.usage_receipt(186, "fork-a", supersedes=old, recorded=LATER)
        self.usage_receipt(186, "fork-b", supersedes=old, recorded=LATER)
        self.usage_receipt(187, "cross-story", supersedes=old, recorded=LATER)
        future, _ = self.usage_receipt(188, "later-root", recorded=LATER)
        self.usage_receipt(188, "backwards", supersedes=future)
        other, _ = self.usage_receipt(
            189, "other-report", selector=SELECTOR | {"report_id": "other"}
        )
        self.usage_receipt(189, "cross-report", supersedes=other, recorded=LATER)
        old, _ = self.usage_receipt(190, "chain-root")
        middle, _ = self.usage_receipt(
            190, "chain-middle", supersedes=old, recorded=LATER
        )
        head, _ = self.usage_receipt(
            190, "chain-head", price="0.75", supersedes=middle, recorded=LATER
        )
        view = self.project(self.tree())
        for story in (186, 187, 188, 189):
            self.assert_unknown(view.stories[story].direct)
        self.assertEqual(view.stories[190].direct.priced_usd, Decimal("0.75"))
        self.assertEqual(view.resolved_receipt_digests, (head,))

    def test_price_coverage_and_decimal_precision_are_independent(self):
        self.git.story(181, children=(186, 187, 188, 189))
        for story in (186, 187, 188, 189):
            self.git.story(story, parent=181)
        self.usage_receipt(
            181, "amount", price="99999999999999999999.999999999999999999"
        )
        self.usage_receipt(186, "amount", price="0.000000000000000002")
        self.usage_receipt(187, "unpriced", price=None, coverage="partial")
        self.usage_receipt(188, "zero", price="0")
        self.usage_receipt(189, "unknown", price="1.25", coverage="unknown")
        tree = self.tree()
        with localcontext() as context:
            context.prec = 2
            view = self.project(tree)
        self.assertEqual(
            view.stories[181].inclusive.priced_usd,
            Decimal("100000000000000000000.000000000000000001"),
        )
        self.assertEqual(view.stories[181].inclusive.coverage, "partial")
        self.assert_unknown(view.stories[187].direct)
        self.assertEqual(view.stories[188].direct.priced_usd, Decimal(0))
        self.assertEqual(view.stories[188].direct.coverage, "complete")
        self.assert_unknown(view.stories[189].direct)

    def test_usage_and_graph_gaps_do_not_inherit_timing_coverage(self):
        self.git.story(181, children=(186, 187))
        self.git.story(186, parent=181)
        self.usage_receipt(181, "epic")
        self.usage_receipt(186, "child")
        before = self.project(self.tree())
        self.assertEqual(before.stories[181].direct.coverage, "complete")
        self.assertEqual(before.stories[181].inclusive.coverage, "partial")
        self.assertIn(
            "ancestry-missing", {gap.code for gap in before.stories[181].inclusive.gaps}
        )
        bad_timing = self.git.register("broken", b"invalid timing")
        self.git.append(186, bad_timing)
        self.assertEqual(self.project(self.tree()), before)
        _, incomplete = self.usage_receipt(186, "incomplete")
        (self.git.root(186) / incomplete["data"]["path"]).unlink()
        after = self.project(self.tree())
        self.assertEqual(after.stories[186].direct.priced_usd, Decimal("0.10"))
        self.assertEqual(after.stories[186].direct.coverage, "partial")
        self.assertIn(
            "receipt-missing", {gap.code for gap in after.stories[186].direct.gaps}
        )

    def test_selector_identity_includes_every_dimension(self):
        self.git.story(186)
        self.usage_receipt(186, "only")
        tree = self.tree()
        for key, changed in (
            ("project", "other"),
            ("report_id", "other"),
            ("window_start_utc", "2026-11-10T19:01:00Z"),
            ("window_end_utc", "2026-11-10T19:59:00Z"),
            ("cutoff_utc", LATER),
            ("rate_card", "other"),
            ("pricing_basis", "other"),
        ):
            with self.subTest(key=key):
                view = self.project(tree, SELECTOR | {key: changed})
                self.assert_unknown(view.stories[186].direct)
                self.assertEqual(view.resolved_receipt_digests, ())
        equivalent = SELECTOR | {"cutoff_utc": "2026-11-10T20:00:00+00:00"}
        self.assertEqual(self.project(tree, equivalent), self.project(tree))
        self.assertEqual(self.project(tree, equivalent).selector.to_dict(), SELECTOR)
        for invalid in (
            {},
            SELECTOR | {"unexpected": None},
            SELECTOR | {"project": ["aitm"]},
            SELECTOR | {"report_id": "file:///private"},
            SELECTOR | {"cutoff_utc": "2026-11-10T20:00:00"},
            SELECTOR | {"window_start_utc": SELECTOR["window_end_utc"]},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.project(tree, invalid)
