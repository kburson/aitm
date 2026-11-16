---
schema: "aitm.story/v0"
id: 352
title: "[Spike] Name the condition that blocks local test selection"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/352"
parent: 351
children: []
blocking: [354]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T19:41:49Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Name the condition that blocks local test selection

[GitHub issue #352](https://github.com/kburson/aitm/issues/352) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 220. Priority P2. Size S.

Question: on current trunk, what single condition prevents a local plan from naming the tests for one uncommitted production edit?

Known observations to test: `python -m tools.ci.tia.local --plan` returns unavailable, and `tools/ci/path_map.py` selects from committed trees, so an uncommitted edit is invisible. Name the blocking condition and the smallest investigation result that lets a later story name those tests.

## Bound

This is research for #351. Write the finding. Production code, the hosted path map, and CI stay unchanged.

Read #143, #267, #339, `tools/ci/tia/local.py`, and `tools/ci/path_map.py`.

## Handoff

#354 implements the accepted finding. It stays blocked until this receipt is accepted.
