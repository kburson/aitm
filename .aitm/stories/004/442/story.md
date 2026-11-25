---
schema: "aitm.story/v0"
id: 442
title: "Roll up epic trails, handoffs and overlapping agent effort"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/442"
parent: 435
children: []
blocking: [443]
blocked-by: [437]
created: "2026-11-25T03:17:32Z"
updated: "2026-11-25T13:27:16.081Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "L"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-trail-rollup.md"], "attachments": ["attachments/trusted-pr-451.json", "attachments/pr-451-test-mix.json", "attachments/pr-451-source-review.md", "attachments/timing/442-delivery-native-engagement-20261125-442.json"]}
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

## Refinement

**Size L. Estimate 3.5 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Delivery

[PR #451](https://github.com/kburson/aitm/pull/451) merged to `trunk`. GitHub closed #442 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).

## Actual agent engagement

**31m 10.362s observed (0.5195 agent-hours), partial coverage.** Codex delivery contributed 18m 43.685s, independent Codex review contributed 2m 19.041s, and Grok review contributed 10m 7.636s across four attempts. [Timing receipt](attachments/timing/442-delivery-native-engagement-20261125-442.json).

The sum includes in-turn tool work and independent reviewer turns, including concurrent turns. It excludes 3m 0.017s of explicit passive CI waits. The interrupted Grok attempt is measured through its last retained progress. The Claude review launches did not retain native turn boundaries, so Claude engagement remains unknown. The evidence ends at 2026-11-25T13:24:02.021Z.
