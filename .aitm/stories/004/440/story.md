---
schema: "aitm.story/v0"
id: 440
title: "Capture provider-reported Claude Code usage"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/440"
parent: 435
children: []
blocking: [444, 445]
blocked-by: [438]
created: "2026-11-25T03:17:28Z"
updated: "2026-11-25T13:10:41.926Z"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/trusted-pr-449.json", "attachments/pr-449-test-mix.json", "attachments/pr-449-source-review.md", "attachments/claude-native-qualification.json", "attachments/timing/435-native-engagement-backfill-20261125-440.json"]}
expansions: []
trips: []
---

# Capture provider-reported Claude Code usage

[GitHub #440](https://github.com/kburson/aitm/issues/440) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Normalize per-result usage, deduplicated finalized requests, cache fields and partial cancelled results. Qualify supported configured interactive and recovery routes.

## Dependencies

- #438

## Implementation

[PR #449](https://github.com/kburson/aitm/pull/449) contains the Claude Code usage adapter. Independent review and native qualification passed on the candidate. Hosted CI and the full product unit-test gate precede merge.

## Delivery

[PR #449](https://github.com/kburson/aitm/pull/449) merged to `trunk`. GitHub closed #440 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).

## Refinement

**Size M. Estimate 2.5 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>). [Partial engagement receipt](attachments/timing/435-native-engagement-backfill-20261125-440.json).
