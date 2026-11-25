---
schema: "aitm.story/v0"
id: 444
title: "Reconcile AIPR companion usage receipts"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/444"
parent: 435
children: []
blocking: [445]
blocked-by: [437, 440, 441]
created: "2026-11-25T03:17:36Z"
updated: "2026-11-25T14:21:52.387Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-aipr-companions.md"], "attachments": ["attachments/444-live-aipr-companions.json", "attachments/pr-453-source-review.md", "attachments/trusted-pr-453.json", "attachments/pr-453-test-mix.json"]}
expansions: []
trips: []
---

# Reconcile AIPR companion usage receipts

[GitHub #444](https://github.com/kburson/aitm/issues/444) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Validate sealed decisions separately from usage. Exercise two rounds, delayed and reversed delivery, interruption and replay on existing qualified routes. Preserve failed Codex attempt usage and its sealed-review gap.

## Dependencies

- #437
- #440
- #441

## Refinement

**Size M. Estimate 3 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Implementation

[Companion receipt plan](plan/2026-11-25-aipr-companions.md).

[PR #453](https://github.com/kburson/aitm/pull/453) opened at `8a460de58119d09a1d0b38a834a623e154b3ab45`. The focused effort and catalog run passed 134 tests. [Hosted run](https://github.com/kburson/aitm/actions/runs/45632218637).

The [live pilot](attachments/444-live-aipr-companions.json) exercised two rounds on Claude and Grok and one interruption per provider. All six native receipts replayed byte-identically after reversed round delivery and SQLite reopen. Four sealed decisions were independently verified against the reviewer, artifact and response. All four disposable brokers read back offline.

The [independent source review](attachments/pr-453-source-review.md), [trusted verifier](attachments/trusted-pr-453.json), and all six hosted jobs passed on the same candidate.
