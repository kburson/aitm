---
schema: "aitm.story/v0"
id: 360
title: "Run a CI full sweep as category shards"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/360"
parent: 356
children: []
blocking: [361]
blocked-by: [359]
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

# Run a CI full sweep as category shards

[GitHub issue #360](https://github.com/kburson/aitm/issues/360) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 300. Priority P2. Size S.

Run a CI full sweep as the same category shards delivered locally by #359.

## Development

A full CI sweep starts those suites as parallel jobs. The ordinary pull-request path map stays the short check. This story adds no schedule, no merge hold, and no failure flag.

Stay blocked until #359 is accepted. The schedule is #361.
