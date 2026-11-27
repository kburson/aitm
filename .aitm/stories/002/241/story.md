---
schema: "aitm.story/v0"
id: 241
title: "[Core C88] Core policy for managed PR operations"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/241"
parent: 489
children: []
blocking: [242, 512]
blocked-by: [48, 236, 239, 497, 505, 507, 511]
created: "2026-11-11T15:58:21Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c88"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C88", "parent": 489}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":489,"design_sources":[2],"scope_entry":"C88","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C88] Core policy for managed PR operations

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#489](https://github.com/kburson/aitm/issues/489). Key: C88. Estimate: **4 h**. Blocked by: #48, #236, #239, #497, #505, #507, #511.

Register composed source for Dev, mount pickup and governed PR operations through the shared catalog, and require local proof before push and current hosted CI/XPR for merge. Retirement happens after verified closeout under its retained dependent fence. C100/C101 prove the mounted order and parity.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #241](https://github.com/kburson/aitm/issues/241) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Provider-neutral admission for scoped observation, push/refresh, ready/retarget and merge, without a generic proxy.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C41 / #48](../../000/48/story.md), [C84 / #236](../236/story.md), [C86 / #239](../239/story.md).

**Blocking** [C89 / #242](../242/story.md).

**Owned areas** src/aitm_core/managed/operations.py; packages/aitm-core/tests/integration/test_c88.py.

## Acceptance criteria

- [ ] Use deterministic broker doubles to deny unqualified routes, stale runtime scope and cross-story operations. Scope observation to the bound PR and allowed evidence. Enforce dual-role target write policy, invalidation on retarget, C41 and default-only host prerequisites. Check that managed non-default delivery ignores the trunk hold, and a positive #158 boundary without qualified readiness holds integrated repair.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c88).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #489 with scope entry **C88**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
