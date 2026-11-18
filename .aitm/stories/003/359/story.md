---
schema: "aitm.story/v0"
id: 359
title: "Run a local full sweep as category shards"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/359"
parent: 356
children: []
blocking: [360]
blocked-by: [357, 358]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T23:38:27Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Run a local full sweep as category shards

[GitHub issue #359](https://github.com/kburson/aitm/issues/359) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 590. Priority P2. Size S.

Run a local full sweep as the category shards named by the accepted #357 and #358 receipts.

## Development

An agent can start one local full sweep and have the categories run in parallel. The ordinary affected-test command remains the short path. This story adds no CI job and no schedule.

Stay blocked until #357 and #358 are accepted.
