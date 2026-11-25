---
schema: "aitm.story/v0"
id: 438
title: "Session-scoped capture and exact-recovery interface"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/438"
parent: 435
children: []
blocking: [439, 440, 441]
blocked-by: [436, 437]
created: "2026-11-25T03:17:24Z"
updated: "2026-11-25T13:10:41.926Z"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/trusted-pr-447.json", "attachments/pr-447-test-mix.json", "attachments/pr-447-source-review.md", "attachments/timing/435-native-engagement-backfill-20261125-438.json"]}
expansions: []
trips: []
---

# Session-scoped capture and exact-recovery interface

[GitHub #438](https://github.com/kburson/aitm/issues/438) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Expose a bounded Python interface around already-installed provider harnesses and exact recovery. Capture terminal outcomes independently from exit status. Keep sandbox defaults and sign-in intact.

## Dependencies

- #436
- #437

## Implementation

[PR #447](https://github.com/kburson/aitm/pull/447) contains the shared capture and exact-recovery interface. Provider-specific adapters remain in #439–#441.

## Delivery

[PR #447](https://github.com/kburson/aitm/pull/447) merged to `trunk`. GitHub closed #438 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-24-delivery-sign-off.md).

## Refinement

**Size M. Estimate 2.5 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>). [Partial engagement receipt](attachments/timing/435-native-engagement-backfill-20261125-438.json).
