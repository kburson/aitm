import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from tools.story_dashboard import evidence

STAMP = "2026-11-10T21:00:00Z"
AS_OF = datetime.fromisoformat(STAMP)
EARLIER = "2026-11-10T20:00:00Z"
FUTURE = "2026-11-10T22:00:00Z"


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def event(story, kind, data, ts=EARLIER):
    return {"v": 0, "type": kind, "ts": ts, "story": story, "data": data}


def timing(batch="batch-1", subject=186):
    return {
        "schema": "aitm.story-timing-receipt/v1",
        "project": "aitm",
        "subject": subject,
        "batch": batch,
        "recorded_at_utc": EARLIER,
        "source": {"ref": "manual:checkpoint-1"},
        "observations": [
            {
                "observation_id": "checkpoint-1.turn-1",
                "actor": "agent-1",
                "turn": "turn-1",
                "phase": "implement",
                "role": "implementer",
                "attempt": "attempt-1",
                "kind": "agent-turn",
                "coverage": "complete",
                "basis": "verified-turn-boundaries",
                "start_utc": "2026-11-10T19:58:00Z",
                "end_utc": "2026-11-10T19:59:00Z",
            }
        ],
    }


def usage(batch="report-1"):
    selector = {
        "project": "aitm",
        "report_id": "report-1",
        "window_start_utc": "2026-11-10T19:00:00Z",
        "window_end_utc": EARLIER,
        "cutoff_utc": EARLIER,
        "rate_card": "rates-1",
        "pricing_basis": "api-equivalent",
    }
    direct = {"tokens": {"input": 125, "output": 75}, "priced_usd": "0.00125"}
    return {
        "schema": "aitm.story-usage-receipt/v1",
        "project": "aitm",
        "subject": 186,
        "batch": batch,
        "recorded_at_utc": EARLIER,
        "source": {"sha256": "a" * 64},
        "selector": selector,
        "usage": direct,
        "coverage": "complete",
        "verification": {
            "operator_ref": "operator-1",
            "verified_at_utc": EARLIER,
            "source_report_id": "report-1",
            "source_sha256": "a" * 64,
            "verified_story": 186,
            "selector": selector,
            "pricing_basis": "api-equivalent",
            "coverage": "complete",
            "sanitized_data_sha256": digest(raw(direct)),
        },
    }


class PlanningFixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Planning Fixture")
        self.git("config", "user.email", "fixture@example.invalid")

    def git(self, *args):
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        env.update(GIT_AUTHOR_DATE=STAMP, GIT_COMMITTER_DATE=STAMP)
        return (
            subprocess.check_output(["git", "-C", str(self.repo), *args], env=env)
            .decode()
            .strip()
        )

    def root(self, story):
        return self.repo / ".aitm" / "stories" / f"{story // 100:03d}" / str(story)

    def story(self, story, *, parent=None, children=(), estimate="{}", extra=""):
        root = self.root(story)
        root.mkdir(parents=True, exist_ok=True)
        (root / "story.md").write_text(
            f'---\nschema: "aitm.story/v0"\nid: {story}\ntitle: "Story {story}"\n'
            f'state: "backlog"\nparent: {json.dumps(parent)}\nchildren: {json.dumps(children)}\n'
            f'updated: "{EARLIER}"\nestimate: {estimate}\n{extra}---\n\nBody\n'
        )
        (root / "events.jsonl").touch()

    def append(self, story, *events):
        with (self.root(story) / "events.jsonl").open("ab") as output:
            for row in events:
                output.write((row if isinstance(row, bytes) else raw(row)) + b"\n")

    def put(self, path, payload, story=186):
        output = self.root(story) / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        return output

    def register(self, batch, payload, *, kind="story-timing-receipt", **overrides):
        path = f"attachments/timing/{batch}-186.json"
        record = event(
            186,
            "core.evidence.recorded",
            {
                "kind": kind,
                "path": path,
                "sha256": digest(payload),
                "scope": {"story": 186, "project": "aitm"},
            },
        )
        record["data"].update(overrides)
        self.put(path, payload)
        return record

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture", "--allow-empty")
        return self.git("rev-parse", "HEAD")

    def cli(self, pin, *args):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.story_dashboard.evidence",
                "--repo",
                str(self.repo),
                "--commit",
                pin,
                "--as-of",
                STAMP,
                *map(str, args),
            ],
            capture_output=True,
            text=True,
        )

    def test_pinned_tree_and_receipt_registration(self):
        self.story(181, children=(186, 187))
        self.story(186, parent=181, estimate='{ "agent-hours": 3.75, "size": "M" }')
        self.story(187, parent=181, estimate="{ agent-hours: 2.5, size: S }")
        first = self.register("batch-1", raw(timing()))
        self.put("attachments/timing/stray-186.json", raw(timing("stray")))
        escape = self.register(
            "escape", raw(timing("escape")), path="../escape-186.json"
        )
        mismatch = self.register("mismatch", raw(timing("mismatch")), sha256="0" * 64)
        future = self.register("future", raw(timing("future")))
        future["ts"] = FUTURE
        duplicate = self.register(
            "duplicate",
            raw(timing("duplicate")).replace(
                b'"project":"aitm"',
                b'"project":"aitm","project":"other"',
            ),
        )
        conflict = self.register("conflict", raw(timing("conflict")))
        revision = self.register(
            "conflict", raw(timing("conflict") | {"source": {"ref": "manual:revised"}})
        )
        wrong = self.register("wrong", raw(timing("wrong", subject=187)))
        unbound = self.register(
            "scope", raw(timing("scope")), scope={"story": 187, "project": "aitm"}
        )
        missing = self.register("missing", raw(timing("missing")))
        (self.root(186) / missing["data"]["path"]).unlink()
        self.append(
            186,
            first,
            first,
            escape,
            mismatch,
            future,
            duplicate,
            conflict,
            revision,
            wrong,
            unbound,
            missing,
            event(
                186,
                "core.estimate.set",
                {
                    "agent_hours": 3.75,
                    "phase": "refine",
                    "scope": {"phase": "implement", "roles": ["implementer"]},
                },
            ),
            event(186, "core.state.entered", {"state": "test"}),
            event(186, "core.state.entered", {"state": "done"}, FUTURE),
        )
        self.append(
            187,
            event(187, "core.estimate.set", {"agent_hours": 2.5, "phase": "refine"}),
        )
        pin = self.commit()
        self.append(186, event(186, "core.state.entered", {"state": "done"}))
        self.commit()
        (self.root(186) / first["data"]["path"]).write_text("dirty")
        tree = evidence.read_tree(self.repo, pin, AS_OF)
        self.assertEqual([receipt.batch for receipt in tree.receipts], ["batch-1"])
        self.assertEqual(len(tree.registrations), 1)
        self.assertEqual(tree.descendants[181], (186, 187))
        self.assertEqual(tree.stories[186].state, "test")
        self.assertEqual(tree.estimates[186].phase, "implement")
        self.assertEqual(tree.estimates[186].roles, ("implementer",))
        self.assertIsNone(tree.estimates[187].phase)
        self.assertEqual(str(tree.estimates[187].agent_hours), "2.5")
        self.assertEqual(
            {gap.code for gap in tree.gaps},
            {
                "invalid-registration",
                "receipt-digest",
                "future-event",
                "invalid-receipt",
                "registration-conflict",
                "receipt-missing",
            },
        )
        self.assertTrue(all(gap.story == 186 for gap in tree.gaps))
        with self.assertRaisesRegex(ValueError, "cutoff"):
            evidence.read_tree(self.repo, pin, datetime.fromisoformat(EARLIER))

    def test_legacy_core_headers_and_direct_validator(self):
        self.story(2, children=(186,), estimate="{ agent-hours: 257.5, size: XL }")
        path = self.root(2) / "story.md"
        path.write_text(
            path.read_text()
            .replace(f'updated: "{EARLIER}"', f"updated: {EARLIER}")
            .replace(
                'state: "backlog"',
                f"state: backlog\ncreated: {EARLIER}",
            )
        )
        self.story(186, parent=2)
        payload = raw(timing())
        self.append(186, self.register("batch-1", payload))
        tree = evidence.read_tree(self.repo, self.commit(), AS_OF)
        self.assertEqual(tree.descendants[2], (186,))
        self.assertEqual(str(tree.estimates[2].agent_hours), "257.5")
        self.assertEqual(tree.gaps, ())
        with self.assertRaisesRegex(ValueError, "noncanonical receipt path"):
            evidence.validate_receipt(
                payload, replace(tree.registrations[0], path="../batch-1-186.json")
            )

    def test_offline_git_pins_and_regular_bounded_blobs(self):
        self.story(186)
        for batch in ("symlink", "oversize"):
            row = self.register(batch, raw(timing(batch)))
            path = self.root(186) / row["data"]["path"]
            if batch == "symlink":
                path.unlink()
                path.symlink_to("elsewhere.json")
            else:
                path.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
            self.append(186, row)
        pin = self.commit()
        self.git("tag", "-am", "tag", "release")
        bogus = "f" * 40
        self.git("update-ref", f"refs/heads/{bogus}", pin)
        self.append(186, event(186, "core.state.entered", {"state": "done"}))
        replacement = self.commit()
        self.git("replace", pin, replacement)
        for invalid in (
            "HEAD",
            bogus,
            pin[:12],
            pin.upper(),
            self.git("rev-parse", "HEAD^{tree}"),
            self.git("rev-parse", "release"),
        ):
            with self.subTest(pin=invalid), self.assertRaises(ValueError):
                evidence.read_tree(self.repo, invalid, AS_OF)
        with patch.dict(
            os.environ,
            {"GIT_DIR": "/does-not-exist", "GIT_WORK_TREE": "/does-not-exist"},
        ):
            tree = evidence.read_tree(self.repo, pin, AS_OF)
        self.assertEqual({gap.code for gap in tree.gaps}, {"receipt-blob"})
        self.assertEqual(tree.stories[186].state, "backlog")
        self.git("config", "remote.upstream.promisor", "true")
        self.git("config", "remote.upstream.url", "https://invalid.example")
        with self.assertRaisesRegex(ValueError, "partial or promisor"):
            evidence.read_tree(self.repo, pin, AS_OF)

    def test_ancestry_cycles_and_dependency_are_not_edges(self):
        self.story(181, children=(186,))
        self.story(186, parent=181)
        self.story(187, parent=188)
        self.story(188, parent=187)
        self.story(189, parent=1000)
        self.story(190)
        self.append(181, event(181, "core.link.dependent-added", {"blocking": 190}))
        self.append(186, event(186, "core.link.parent-set", {"parent": 190}))
        tree = evidence.read_tree(self.repo, self.commit(), AS_OF)
        self.assertEqual(tree.parents, {186: 190})
        self.assertEqual(tree.descendants[181], ())
        self.assertEqual(tree.descendants[190], (186,))
        self.assertEqual(
            {(g.story, g.code) for g in tree.gaps},
            {
                (187, "ancestry-cycle"),
                (188, "ancestry-cycle"),
                (189, "ancestry-missing"),
            },
        )

    def test_legacy_seed_is_the_single_registered_exception(self):
        self.story(181)
        self.story(186)
        payload = b'{"historic":"fixture"}'
        self.assertEqual(
            evidence.LEGACY_SHA256,
            "8d619b606cfd0142c46da7402ee52c20b95d3a78725894c12cc385309342b139",
        )
        path = "attachments/2026-11-10-actual-backfill.json"
        self.put(path, payload, 181)
        self.put("attachments/companion.md", b"not timing", 181)
        seed = {
            "kind": "historical-actual-backfill",
            "evidence": ["attachments/companion.md", path],
            "receipt_sha256": digest(payload),
        }
        self.append(
            181,
            event(181, "core.evidence.recorded", seed),
            event(181, "core.evidence.recorded", seed, STAMP),
        )
        self.append(186, event(186, "core.evidence.recorded", seed))
        valid = self.commit()
        self.append(
            181,
            event(181, "core.evidence.recorded", seed | {"receipt_sha256": "0" * 64}),
        )
        conflict = self.commit()
        with patch.object(evidence, "LEGACY_SHA256", digest(payload)):
            tree = evidence.read_tree(self.repo, valid, AS_OF)
            self.assertEqual(tree.legacy_seed, payload)
            self.assertEqual(
                [(g.story, g.code) for g in tree.gaps], [(186, "invalid-legacy-seed")]
            )
            held = evidence.read_tree(self.repo, conflict, AS_OF)
            self.assertIsNone(held.legacy_seed)
            self.assertIn("legacy-conflict", {gap.code for gap in held.gaps})

    def test_usage_schema_and_prospective_validation(self):
        self.story(186)
        row = self.register("report-1", raw(usage()), kind="story-usage-receipt")
        receipt_path = self.root(186) / row["data"]["path"]
        event_path = self.repo / "event.json"
        event_path.write_bytes(raw(row))
        pin = self.commit()
        result = self.cli(pin, "--receipt", receipt_path, "--registration", event_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["prospective"]["schema"],
            "aitm.story-usage-receipt/v1",
        )
        self.assertEqual(self.cli(pin, "--receipt", receipt_path).returncode, 2)
        self.append(186, row)
        new_pin = self.commit()
        loaded = evidence.read_tree(self.repo, new_pin, AS_OF)
        self.assertEqual(loaded.receipts[0].verification["verified_story"], 186)
        self.assertEqual(
            self.cli(
                new_pin, "--receipt", receipt_path, "--registration", event_path
            ).returncode,
            0,
        )
        wrong = usage()
        wrong["verification"]["sanitized_data_sha256"] = "b" * 64
        receipt_path.write_bytes(raw(wrong))
        row["data"]["sha256"] = digest(raw(wrong))
        event_path.write_bytes(raw(row))
        self.assertEqual(
            self.cli(
                pin, "--receipt", receipt_path, "--registration", event_path
            ).returncode,
            2,
        )
        superseding = usage()
        superseding["source"]["ref"] = "export:ref"
        receipt_path.write_bytes(raw(superseding))
        row["data"]["sha256"] = digest(raw(superseding))
        event_path.write_bytes(raw(row))
        self.assertEqual(
            self.cli(
                new_pin, "--receipt", receipt_path, "--registration", event_path
            ).returncode,
            2,
        )

    def test_future_receipt_evidence_held(self):
        self.story(186)
        payload = timing()
        payload["observations"][0]["end_utc"] = FUTURE
        self.append(186, self.register("batch-1", raw(payload)))
        tree = evidence.read_tree(self.repo, self.commit(), AS_OF)
        self.assertFalse(tree.receipts)
        self.assertEqual(
            [(gap.story, gap.code) for gap in tree.gaps], [(186, "future-receipt")]
        )
