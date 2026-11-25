---
schema: "aitm.story/v0"
id: 442
title: "Roll up epic trails, handoffs and overlapping agent effort"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/442"
parent: 435
children: []
blocking: [443]
blocked-by: [437]
created: "2026-11-25T03:17:32Z"
updated: "2026-11-25T13:10:41Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-trail-rollup.md"], "attachments": []}
expansions: []
trips: []
---

# Roll up epic trails, handoffs and overlapping agent effort

[GitHub #442](https://github.com/kburson/aitm/issues/442) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Validate story marker lifecycle and detach/attach with exact native boundaries. Sum disjoint usage, session engagement and interval-union wall time without double counting. Reconcile the #433 fixture.

## Dependencies

- #437

## Implementation

[PR #451](https://github.com/kburson/aitm/pull/451) implements the [trail rollup plan](plan/2026-11-25-trail-rollup.md). Delivery requires independent review and trusted verification for the current candidate.
