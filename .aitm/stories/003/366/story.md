---
schema: "aitm.story/v0"
id: 366
title: "Show the scheduled-failure flag when it is checked"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/366"
parent: 362
children: []
blocking: []
blocked-by: [365]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-23T00:07:10Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-21-366-delivery-plan.md", "plan/2026-11-22-366-checkpoint.md"], "attachments": ["attachments/2026-11-22-366-trusted-pr-421.json", "attachments/2026-11-22-366-live-check.json"]}
expansions: []
trips: []
---

# Show the scheduled-failure flag when it is checked

[GitHub issue #366](https://github.com/kburson/aitm/issues/366) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 660. Priority P2. Size S.

Provide a read-only check of the flag delivered by #365 for both a person and an agent. Begin development after #365 is delivered.

## Acceptance

- Show the exact failing attempt and timestamp when active, a clear statement when clear, and a distinct unavailable result for unreadable, invalid or uninitialized state. Human and machine output share one validated record and document its as-of time.
- Exercise all three results with an isolated record and verify the deployed check against an authentic scheduled run.
- Deliver the PR to `trunk` with canonical CI, trusted verification and an independent Grok PR review on the current candidate before merging. Record readback and replay evidence for epic acceptance.

[Delivery plan](plan/2026-11-21-366-delivery-plan.md).

[Pickup and test checkpoint](plan/2026-11-22-366-checkpoint.md).

[Verified delivery and sign-off](retro/2026-11-22-366-sign-off.md).
