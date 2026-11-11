import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_evidence as fixture

from tools.story_dashboard import snapshot


class SnapshotFixture(unittest.TestCase):
    def setUp(self):
        self.git = fixture.PlanningFixture()
        self.git.setUp()
        self.addCleanup(self.git.doCleanups)
        output = tempfile.TemporaryDirectory()
        self.addCleanup(output.cleanup)
        self.out = Path(output.name)
        self.git.story(181, children=(186, 187))
        self.git.story(
            186,
            parent=181,
            estimate='{"agent-hours":2.5,"size":"M","scope":{"phase":"implement","roles":["implementer"]}}',
        )
        self.git.story(187, parent=181)
        receipt = fixture.timing()
        self.git.append(
            186,
            fixture.event(
                186,
                "core.state.entered",
                {"state": "develop"},
                ts="2026-11-10T19:56:00Z",
            ),
            fixture.event(
                186, "core.state.entered", {"state": "done"}, ts="2026-11-10T19:59:00Z"
            ),
            self.git.register("batch-1", fixture.raw(receipt)),
        )
        self.pin = self.git.commit()

    def run_cli(self, repo, output, *, pin=None, selector=None, env=None):
        args = [
            sys.executable,
            "-m",
            "tools.story_dashboard.snapshot",
            "--repo",
            str(repo),
            "--commit",
            pin or self.pin,
            "--as-of",
            fixture.STAMP,
            "--output",
            str(output),
        ]
        if selector is not None:
            args += ["--usage-report", str(selector)]
        return subprocess.run(args, capture_output=True, text=True, env=env)

    def assert_pass(self, run):
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_rebuild_seed_snapshot_byte_for_byte(self):
        second = self.out / "second-reader"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-local", str(self.git.repo), str(second)],
            check=True,
        )
        first_out, second_out = self.out / "first", self.out / "second"
        self.assert_pass(self.run_cli(self.git.repo, first_out))
        self.assert_pass(self.run_cli(second, second_out))
        raw = (first_out / "snapshot.json").read_bytes()
        validation = (first_out / "validation.json").read_bytes()
        self.assertEqual(raw, (second_out / "snapshot.json").read_bytes())
        self.assertEqual(validation, (second_out / "validation.json").read_bytes())
        self.assertTrue(raw.endswith(b"\n"))
        self.assertEqual(
            json.loads(validation)["snapshot_sha256"], hashlib.sha256(raw).hexdigest()
        )
        view = json.loads(raw)
        self.assertEqual(view["schema"], "aitm.story-dashboard/v1")
        self.assertEqual(view["repository"], "kburson/aitm")
        self.assertEqual(view["planning"]["commit"], self.pin)
        self.assertEqual(view["planning"]["as_of_utc"], fixture.STAMP)
        self.assertEqual([r["id"] for r in view["stories"]], [181, 186, 187])
        epic, child, unmeasured = view["stories"]
        self.assertEqual(child["estimate"]["agent_hours"], "2.5")
        self.assertEqual(child["estimate"]["phase"], "implement")
        self.assertEqual(child["estimate"]["roles"], ["implementer"])
        self.assertEqual(
            child["last_progress"]["evidence"]["url"],
            f"https://github.com/kburson/aitm/blob/{self.pin}/.aitm/stories/001/186/events.jsonl#L2",
        )
        self.assertIsNone(child["cost"]["inclusive"]["priced_usd"])
        self.assertEqual(child["cost"]["inclusive"]["coverage"], "unknown")
        self.assertEqual(
            child["timing"]["implementation_elapsed"]["milliseconds"], 180000
        )
        self.assertIsNone(child["timing"]["all_phase_elapsed"]["milliseconds"])
        self.assertEqual(
            epic["timing"]["actual"]["milliseconds"],
            child["timing"]["actual"]["milliseconds"],
        )
        self.assertEqual(epic["timing"]["actual"]["coverage"], "partial")
        self.assertIsNone(unmeasured["timing"]["actual"]["milliseconds"])
        (first_out / "snapshot.json").write_text("interrupted replacement")
        self.assertNotEqual(
            json.loads(validation)["snapshot_sha256"],
            hashlib.sha256((first_out / "snapshot.json").read_bytes()).hexdigest(),
        )
        self.assert_pass(self.run_cli(self.git.repo, first_out))
        self.assertEqual(raw, (first_out / "snapshot.json").read_bytes())

    def test_selected_usage_keeps_exact_decimal_and_independent_cutoff(self):
        receipt = fixture.usage()
        self.git.append(
            186,
            self.git.register(
                "report-1", fixture.raw(receipt), kind="story-usage-receipt"
            ),
        )
        pin = self.git.commit()
        selector = self.out / "selector.json"
        selector.write_bytes(fixture.raw(receipt["selector"]))
        out = self.out / "priced"
        self.assert_pass(self.run_cli(self.git.repo, out, pin=pin, selector=selector))
        first = (out / "snapshot.json").read_bytes()
        self.assert_pass(self.run_cli(self.git.repo, out, pin=pin, selector=selector))
        self.assertEqual(first, (out / "snapshot.json").read_bytes())
        view = json.loads(first)
        row = next(r for r in view["stories"] if r["id"] == 186)
        self.assertEqual(view["usage_report"]["source_sha256"], "a" * 64)
        self.assertEqual(row["cost"]["direct"]["priced_usd"], "0.00125")
        self.assertEqual(row["cost"]["direct"]["evidence_through_utc"], fixture.EARLIER)
        self.assertNotEqual(
            row["timing"]["actual"]["evidence_through_utc"], fixture.EARLIER
        )

    def test_output_rejects_worktrees_and_artifact_symlinks(self):
        other = self.out / "different-repository"
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        alias = self.out / "alias"
        alias.symlink_to(other, target_is_directory=True)
        env = {
            **os.environ,
            "GIT_CEILING_DIRECTORIES": str(other),
            "GIT_DIR": str(self.out / "bogus"),
        }
        for output in (self.git.repo / "new", other / "nested" / "new", alias / "new"):
            with self.subTest(output=output):
                result = self.run_cli(self.git.repo, output, env=env)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(output.exists())
        independent = self.out / "outside"
        independent.mkdir()
        tracked = other / "leave-alone.json"
        tracked.write_bytes(b"keep")
        (independent / "validation.json").symlink_to(tracked)
        result = self.run_cli(self.git.repo, independent)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(tracked.read_bytes(), b"keep")
        self.assertFalse((independent / "snapshot.json").exists())

    def test_bad_pin_and_duplicate_usage_selector_keys_fail_before_output(self):
        output = self.out / "future"
        result = self.run_cli(self.git.repo, output, pin="HEAD")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(output.exists())
        selector = self.out / "selector.json"
        selector.write_text('{"project":"aitm","project":"other"}')
        result = self.run_cli(self.git.repo, output, selector=selector)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(output.exists())

    def test_commit_source_links_are_canonical(self):
        root = "https://github.com/kburson/aitm/blob/" + self.pin + "/"
        self.assertEqual(
            snapshot.evidence_link(self.pin, ".aitm/stories/001/186/events.jsonl:2"),
            root + ".aitm/stories/001/186/events.jsonl#L2",
        )
        for source in (
            "manual:opaque",
            "../secret",
            ".aitm/stories/001/186/../187/story.md",
            ".aitm/stories/001/186/events.jsonl:0",
            ".aitm/stories/001/186/events.jsonl:01",
        ):
            with self.subTest(source=source):
                self.assertIsNone(snapshot.evidence_link(self.pin, source))
