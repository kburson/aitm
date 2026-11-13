---
schema: "aitm.story/v0"
id: 275
title: "[#146 Spike] Test a CI warning and manual stop workflow"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/275"
parent: 146
children: []
blocking: []
blocked-by: []
created: "2026-11-13T04:56:32Z"
updated: "2026-11-13T04:59:32Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#146 Spike] Test a CI warning and manual stop workflow

Test an advisory warning derived from canonical full trunk CI. Bind it to the exact SHA, run and attempt. Suppress duplicates, preserve a failure when another result is missing, and distinguish a fresh recovery run from stale green evidence. Outline single-repair ownership and manual pause and recovery. Keep #103 in force and leave production settings untouched.

Rank 50. #148 and #267 remain on hold.
