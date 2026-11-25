---
schema: "aitm.story/v0"
id: 441
title: "Capture provider-reported Grok Build usage"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/441"
parent: 435
children: []
blocking: [444, 445]
blocked-by: [438]
created: "2026-11-25T03:17:30Z"
updated: "2026-11-25T12:59:30Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/trusted-pr-450.json", "attachments/pr-450-test-mix.json", "attachments/pr-450-source-review.md", "attachments/grok-native-qualification.json"]}
expansions: []
trips: []
---

# Capture provider-reported Grok Build usage

[GitHub #441](https://github.com/kburson/aitm/issues/441) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Normalize per-process and exact retained turn usage. Preserve opaque turn identity, cancellation gaps and native ticks. Qualify supported configured interactive and recovery routes.

## Dependencies

- #438

## Implementation

[PR #450](https://github.com/kburson/aitm/pull/450) contains the portable Grok Build adapter. Exact native evidence, independent review and full-product CI gate delivery.

## Delivery

[PR #450](https://github.com/kburson/aitm/pull/450) merged to `trunk`. GitHub closed #441 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).
