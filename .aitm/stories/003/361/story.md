---
schema: "aitm.story/v0"
id: 361
title: "Schedule the category-shard full sweep"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/361"
parent: 356
children: []
blocking: []
blocked-by: [360]
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

# Schedule the category-shard full sweep

[GitHub issue #361](https://github.com/kburson/aitm/issues/361) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 310. Priority P2. Size S.

Schedule the category-shard full sweep delivered by #360.

## Development

One scheduled workflow runs that sweep. Pull-request test selection, merge holds, workspace pause, and the failure flag stay outside this story. The flag epic is #362. It watches a scheduled run and does not block this story.

Stay blocked until #360 is accepted.
