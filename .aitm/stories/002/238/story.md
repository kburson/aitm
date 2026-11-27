---
schema: "aitm.story/v0"
id: 238
title: "[Core C85] Terminal managed PR and worktree retirement"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/238"
parent: 489
children: []
blocking: [240, 512]
blocked-by: [80, 237]
created: "2026-11-11T15:58:17Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c85"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C85", "parent": 489}
---

# [Core C85] Terminal managed PR and worktree retirement

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#489](https://github.com/kburson/aitm/issues/489). Key: C85. Estimate: **4 h**. Blocked by: #80, #237.

Register composed source for Dev, mount pickup and governed PR operations through the shared catalog, and require local proof before push and current hosted CI/XPR for merge. Retirement happens after verified closeout under its retained dependent fence. C100/C101 prove the mounted order and parity.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #238](https://github.com/kburson/aitm/issues/238) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Replay-safe terminal retirement orchestration using the dependent fence, exact receipts and owning worktree manager.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C79 / #80](../../000/80/story.md), [C83 / #237](../237/story.md).

**Blocking** [C87 / #240](../240/story.md).

**Owned areas** src/aitm_core/managed/retire.py; packages/aitm-core/tests/integration/test_c85.py.

## Acceptance criteria

- [ ] After completion or abandonment, reconcile effects, retain a merged PR and delivery mapping, close an open abandoned PR and retire only the bound exact ref and owned worktree. Verify outstanding dependents, conditional delete or hold, host retarget invalidation, and a recoverable scrap source before deletion. Lost responses resume the same terminal intent.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c85).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
