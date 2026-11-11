import json
import re
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import test_evidence as fixture

from tools.story_dashboard import render, snapshot
from tools.story_dashboard.evidence import read_tree
from tools.story_dashboard.usage import ReportSelector

HOSTILE_TEXT = '</ScRiPt><template id="untrusted-markup">Story & evidence</template>'


class RendererFixture(unittest.TestCase):
    def setUp(self):
        self.git = fixture.PlanningFixture()
        self.git.setUp()
        self.addCleanup(self.git.doCleanups)
        output = tempfile.TemporaryDirectory()
        self.addCleanup(output.cleanup)
        self.out = Path(output.name)
        self.git.story(181, children=(186, 187))
        self.git.story(186, parent=181)
        self.git.story(187, parent=181)
        self.git.story(188)

        timing = fixture.timing()
        first = timing["observations"][0]
        timing["observations"].append(
            first
            | {
                "actor": "agent-2",
                "turn": "turn-2",
                "role": "reviewer",
                "observation_id": "checkpoint-1.turn-2",
            }
        )
        timing["observations"].extend(
            [
                first
                | {
                    "observation_id": "checkpoint-1.pending",
                    "turn": "request-1",
                    "kind": "pending-wait",
                    "coverage": "partial",
                    "missing_reason": "awaiting-owner",
                    "start_utc": "2026-11-10T19:59:00Z",
                    "end_utc": None,
                    "recorded_at_utc": fixture.EARLIER,
                },
            ]
        )
        usage = fixture.usage()
        self.git.append(
            186,
            fixture.event(
                186,
                "core.estimate.set",
                {
                    "agent_hours": 2.5,
                    "size": "M",
                    "scope": {
                        "phase": "implement",
                        "roles": ["implementer"],
                        "basis": "planned",
                    },
                },
                ts="2026-11-10T19:52:00Z",
            ),
            fixture.event(
                186,
                "core.state.entered",
                {"state": "develop"},
                ts="2026-11-10T19:56:00Z",
            ),
            fixture.event(
                186,
                "core.state.entered",
                {"state": "done"},
                ts="2026-11-10T19:59:00Z",
            ),
            self.git.register("batch-1", fixture.raw(timing)),
            self.git.register(
                "report-1", fixture.raw(usage), kind="story-usage-receipt"
            ),
        )
        self.git.append(
            187,
            fixture.event(187, "core.state.entered", {"state": "plan"}),
        )
        self.pin = self.git.commit()
        self.view = snapshot.build_snapshot(
            read_tree(self.git.repo, self.pin, fixture.AS_OF),
            ReportSelector.from_dict(usage["selector"]),
        )

    def link(self, path):
        return {"path": path, "url": snapshot.evidence_link(self.pin, path)}

    def adversarial(self):
        epic, child, _, _ = self.view["stories"]
        child["title"] = HOSTILE_TEXT
        actual = child["timing"]["actual"]
        actual["evidence"] += [
            self.link(".aitm/stories/001/186/events.jsonl:3"),
            {"path": HOSTILE_TEXT, "url": "https://example.invalid/untrusted"},
        ]
        canonical = self.link(".aitm/stories/001/186/events.jsonl:1")
        url = canonical["url"]
        hostile = {
            "foreign-pin": url.replace(self.pin, "f" * 40),
            "path-disagrees": url.replace("/186/", "/187/"),
            "line-disagrees": url.replace("#L1", "#L2"),
            "userinfo": url.replace("github.com", "operator@github.com"),
            "port": url.replace("github.com", "github.com:443"),
            "query": url.replace("#L1", "?view=1#L1"),
            "empty-query": url.replace("#L1", "?#L1"),
            "duplicate-slash": url.replace("/blob/", "//blob/"),
            "dot-segment": url.replace("/blob/", "/./blob/"),
            "encoded-segment": url.replace("/blob/", "/%62lob/"),
            "different-scheme": url.replace("https:", "http:"),
            "hidden-control": url.replace("/blob/", "/bl\tob/"),
        }
        actual["evidence"] += [
            canonical | {"url": destination, "source_ref": case}
            for case, destination in hostile.items()
        ]
        epic["timing"]["actual"]["evidence"].append(canonical)
        # A gap source is a different link-bearing A05 object from a priced receipt.
        child["cost"]["inclusive"]["gaps"].append(
            {"story": 186, "code": "fixture-gap", "evidence": canonical}
        )
        return self.view

    def run_cli(self, source, output):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.story_dashboard.render",
                "--snapshot",
                str(source),
                "--output",
                str(output),
            ],
            capture_output=True,
            text=True,
        )

    def test_offline_render_and_escaped_evidence(self):
        view = self.adversarial()
        html = render.render(view)
        match = re.search(
            r'<script id="snapshot-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        embedded = match[1]
        self.assertNotIn("<", embedded)
        self.assertNotIn('id="untrusted-markup"', html)
        self.assertNotIn("https://example.invalid/untrusted", html)
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("default-src 'none'", html)
        self.assertIn("sha256-", html)
        self.assertNotRegex(html, r"<(?:script|img|link)\b[^>]*\b(?:src|href)=")
        decoded = json.loads(embedded)
        self.assertEqual(decoded["schema"], snapshot.SCHEMA)
        self.assertEqual(decoded["planning"], view["planning"])
        self.assertEqual(decoded["usage_report"], view["usage_report"])
        epic, child, unmeasured, _ = decoded["stories"]
        self.assertEqual(child["title"], HOSTILE_TEXT)
        self.assertEqual(child["timing"]["actual"]["milliseconds"], 120_000)
        self.assertEqual(child["timing"]["working_wall"]["milliseconds"], 60_000)
        self.assertEqual(
            child["timing"]["implementation_elapsed"]["milliseconds"], 180_000
        )
        self.assertIsNone(child["timing"]["all_phase_elapsed"]["milliseconds"])
        self.assertTrue(child["timing"]["owner_wait"]["pending"])
        self.assertEqual(epic["timing"]["actual"]["coverage"], "partial")
        self.assertIsNone(unmeasured["timing"]["actual"]["evidence_through_utc"])
        self.assertEqual(child["cost"]["inclusive"]["priced_usd"], "0.00125")
        self.assertEqual(
            child["last_progress"]["evidence"],
            self.link(".aitm/stories/001/186/events.jsonl:3"),
        )
        self.assertEqual(
            child["estimate"]["evidence"],
            self.link(".aitm/stories/001/186/events.jsonl:1"),
        )
        self.assertEqual(
            epic["timing"]["actual"]["evidence"][-1],
            self.link(".aitm/stories/001/186/events.jsonl:1"),
        )
        self.assertTrue(
            child["cost"]["inclusive"]["evidence"][0]["url"].endswith(
                "/report-1-186.json"
            )
        )
        self.assertIsNotNone(child["cost"]["inclusive"]["gaps"][-1]["evidence"]["url"])
        evidence = child["timing"]["actual"]["evidence"]
        self.assertIn(self.link(".aitm/stories/001/186/events.jsonl:3"), evidence)
        self.assertTrue(
            all(
                item["url"] is None
                for item in evidence
                if item.get("source_ref")
                in {
                    "foreign-pin",
                    "path-disagrees",
                    "line-disagrees",
                    "userinfo",
                    "port",
                    "query",
                    "empty-query",
                    "duplicate-slash",
                    "dot-segment",
                    "encoded-segment",
                    "different-scheme",
                    "hidden-control",
                }
            )
        )
        self.assertEqual(evidence[-13], {"path": HOSTILE_TEXT, "url": None})
        self.assertEqual(
            view["stories"][1]["timing"]["actual"]["evidence"][-13]["url"],
            "https://example.invalid/untrusted",
        )
        self.assertEqual(render.render(view), html)

    def test_cli_rejects_output_aliases_and_preserves_input_and_prior_output(self):
        source = self.out / "snapshot.json"
        payload = fixture.raw(self.view)
        source.write_bytes(payload)
        safe = self.out / "dashboard.html"
        result = self.run_cli(source, safe)
        self.assertEqual(result.returncode, 0, result.stderr)
        baseline = safe.read_bytes()
        alias = self.out / "input-alias.html"
        alias.symlink_to(source)
        repo_alias = self.out / "worktree-alias"
        repo_alias.symlink_to(self.git.repo, target_is_directory=True)
        inside = self.git.repo / "protected.html"
        inside.write_bytes(b"preserve")
        file_alias = self.out / "tracked-target.html"
        file_alias.symlink_to(inside)
        for output in (source, alias, inside, repo_alias / "new.html", file_alias):
            with self.subTest(output=output):
                result = self.run_cli(source, output)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(source.read_bytes(), payload)
                self.assertEqual(inside.read_bytes(), b"preserve")
                self.assertFalse((self.git.repo / "new.html").exists())
        for invalid in (
            self.view | {"schema": "aitm.story-dashboard/v2"},
            self.view | {"repository": "elsewhere/aitm"},
            self.view | {"planning": self.view["planning"] | {"commit": "HEAD"}},
            self.view | {"stories": [self.view["stories"][0] | {"id": True}]},
            self.view | {"stories": [self.view["stories"][0] | {"descendants": [999]}]},
        ):
            source.write_bytes(fixture.raw(invalid))
            result = self.run_cli(source, safe)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(safe.read_bytes(), baseline)
        source.write_bytes(b'{"schema":"first","schema":"second"}')
        result = self.run_cli(source, safe)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(safe.read_bytes(), baseline)

    def test_invalid_used_fields_fail_before_generating_html(self):
        cases = {}
        usage = deepcopy(self.view)
        usage["usage_report"]["selector"]["cutoff_utc"] = {"text": "not a UTC string"}
        cases["usage clock"] = usage
        progress = deepcopy(self.view)
        progress["stories"][1]["last_progress"]["occurred_at_utc"] = 12345
        cases["progress clock"] = progress
        contributions = deepcopy(self.view)
        contributions["stories"][1]["timing"]["contributions"][0]["story"] = (
            "../issues/187"
        )
        cases["noncanonical contribution story"] = contributions
        foreign = deepcopy(self.view)
        foreign["stories"][1]["timing"]["contributions"][0]["story"] = 999
        cases["absent contribution story"] = foreign
        for case, view in cases.items():
            with self.subTest(case=case), self.assertRaises(ValueError):
                render.render(view)

    def test_unknown_nested_fields_cannot_copy_private_exports_to_html(self):
        top = deepcopy(self.view)
        top["provider_export"] = {"raw_transcript": "PRIVATE_TOP_CANARY"}
        story = deepcopy(self.view)
        story["stories"][1]["provider_export"] = {
            "raw_transcript": "PRIVATE_STORY_CANARY"
        }
        measure = deepcopy(self.view)
        measure["stories"][1]["timing"]["actual"]["raw_export"] = {
            "prompt": "PRIVATE_MEASURE_CANARY"
        }
        evidence = deepcopy(self.view)
        evidence["stories"][1]["timing"]["actual"]["evidence"][0]["raw_export"] = {
            "prompt": "PRIVATE_SOURCE_CANARY"
        }
        for scope, view in (
            ("top", top),
            ("story", story),
            ("measure", measure),
            ("evidence", evidence),
        ):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                render.render(view)

    def test_malformed_detail_values_cannot_crash_a_disclosure(self):
        reason = deepcopy(self.view)
        reason["stories"][1]["timing"]["actual"]["evidence"][0]["reason"] = {
            "toString": False
        }
        bases = deepcopy(self.view)
        bases["stories"][1]["timing"]["actual"]["bases"] = [{"toString": False}]
        coverage_notes = deepcopy(self.view)
        coverage_notes["stories"][1]["timing"]["actual"]["reasons"] = [False]
        gap = deepcopy(self.view)
        gap["stories"][1]["cost"]["inclusive"]["gaps"].append(
            {
                "story": 186,
                "code": {"toString": False},
                "evidence": self.link(".aitm/stories/001/186/events.jsonl:3"),
            }
        )
        for scope, view in (
            ("reason", reason),
            ("basis", bases),
            ("coverage", coverage_notes),
            ("gap", gap),
        ):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                render.render(view)


if __name__ == "__main__":
    unittest.main()
