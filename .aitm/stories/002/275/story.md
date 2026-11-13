---
schema: "aitm.story/v0"
id: 275
title: "[#146 Spike] Test a CI warning and manual stop workflow"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/275"
parent: 146
children: []
blocking: []
blocked-by: []
created: "2026-11-13T04:56:32Z"
updated: "2026-11-13T05:08:30Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/manifest.sha256", "plan/independent-review.md", "plan/advisory.py", "plan/rehearse.py", "plan/rehearsal.log", "plan/readback.json", "plan/graph-readback.py", "plan/graph-readback.log", "plan/graph-readback.json", "plan/2026-11-12-275-manual-stop-warning-findings.md"], "attachments": []}
expansions: []
trips: []
---

# [#146 Spike] Test a CI warning and manual stop workflow

Test an advisory warning derived from canonical full trunk CI. Bind it to the exact SHA, run and attempt. Suppress duplicates, preserve a failure when another result is missing, and distinguish a fresh recovery run from stale green evidence. Outline single-repair ownership and manual pause and recovery. Keep #103 in force and leave production settings untouched.

Rank 50. #148 and #267 remain on hold.

## Independently reviewed result

[Findings](plan/2026-11-12-275-manual-stop-warning-findings.md) · [Signed review](plan/independent-review.md) · [Evidence manifest](plan/manifest.sha256).
