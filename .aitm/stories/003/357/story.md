---
schema: "aitm.story/v0"
id: 357
title: "[Spike] Classify tests into execution categories"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/357"
parent: 356
children: []
blocking: [358, 359]
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

# [Spike] Classify tests into execution categories

[GitHub issue #357](https://github.com/kburson/aitm/issues/357) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 270. Priority P2. Size S.

Question: which collected tests belong in fast unit, slow unit, local integration, and systems integration, and which collected tests fit none of those four?

Use the #285 family inventory and the current collected tests. Publish a written classification with a witness for each placement and an explicit list of the tests that fit none.

## Bound

This is research for #356. Write the classification. The suite, the hosted path map, and CI stay unchanged.

## Handoff

#358 and #359 stay blocked until this receipt is accepted.
