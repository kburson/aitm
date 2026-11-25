---
schema: "aitm.story/v0"
id: 444
title: "Reconcile AIPR companion usage receipts"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/444"
parent: 435
children: []
blocking: [445]
blocked-by: [437, 440, 441]
created: "2026-11-25T03:17:36Z"
updated: "2026-11-25T13:10:41.926Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
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
