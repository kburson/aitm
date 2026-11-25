---
schema: "aitm.story/v0"
id: 439
title: "Capture provider-reported Codex usage"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/439"
parent: 435
children: []
blocking: [445]
blocked-by: [438]
created: "2026-11-25T03:17:26Z"
updated: "2026-11-25T13:10:41.926Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/trusted-pr-448.json", "attachments/pr-448-test-mix.json", "attachments/pr-448-source-review.md", "attachments/codex-native-qualification.json", "attachments/timing/435-native-engagement-backfill-20261125-439.json"]}
expansions: []
trips: []
---

# Capture provider-reported Codex usage

[GitHub #439](https://github.com/kburson/aitm/issues/439) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Normalize explicit headless completion and exact rollout lookup, verified resume deltas, cache and reasoning fields, and interrupted usage gaps. Qualify supported configured interactive and recovery routes.

## Dependencies

- #438

## Implementation

[PR #448](https://github.com/kburson/aitm/pull/448) contains the portable Codex adapter. Exact native qualification and the full product-suite gate remain part of review.

## Delivery

[PR #448](https://github.com/kburson/aitm/pull/448) merged to `trunk`. GitHub closed #439 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-24-delivery-sign-off.md).

## Refinement

**Size M. Estimate 3 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>). [Partial engagement receipt](attachments/timing/435-native-engagement-backfill-20261125-439.json).
