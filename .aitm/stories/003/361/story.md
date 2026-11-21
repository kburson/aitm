---
schema: "aitm.story/v0"
id: 361
title: "Schedule the category-shard full sweep"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/361"
parent: 356
children: []
blocking: []
blocked-by: [360]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-21T23:40:10Z"
last-branch: "codex/361-schedule-category-sweep"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-20-361-delivery-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Schedule the category-shard full sweep

[GitHub issue #361](https://github.com/kburson/aitm/issues/361) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 610. Priority P2. Size S.

Schedule the category-shard full sweep delivered by #360.

## Development

One scheduled workflow runs that sweep. Pull-request test selection, merge holds, workspace pause, and the failure flag stay outside this story. The flag epic is #362. It watches a scheduled run and does not block this story.

Stay blocked until #360 is accepted.

## Acceptance criteria

- Add one scheduled trigger to the accepted #360 workflow on the default branch, with a recorded cadence, overlap policy and a way to disable just the scheduled trigger.
- Observe a real schedule-triggered run. Record expected slot, actual registration and start times, exact source, shard receipts and the aggregate verdict. A manual rehearsal can prove execution wiring.
- Identify how a maintainer recognizes a missed or incomplete slot and finds the corresponding run or absence of one. Leave failure flag, merge hold and workspace pause to their own scope.

[Delivery plan](plan/2026-11-20-361-delivery-plan.md).
