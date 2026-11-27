---
schema: "aitm.story/v0"
id: 240
title: "[Core C87] Installed managed lifecycle commands and operation catalog"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/240"
parent: 490
children: []
blocking: [242]
blocked-by: [66, 235, 238, 508, 509]
created: "2026-11-11T15:58:20Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c87"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C87", "parent": 490}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":490,"design_sources":[2],"scope_entry":"C87","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C87] Installed managed lifecycle commands and operation catalog

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#490](https://github.com/kburson/aitm/issues/490). Key: C87. Estimate: **4 h**. Blocked by: #66, #235, #238, #508, #509.

Register composed source for Dev, mount pickup and governed PR operations through the shared catalog, and require local proof before push and current hosted CI/XPR for merge. Retirement happens after verified closeout under its retained dependent fence. C100/C101 prove the mounted order and parity.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #240](https://github.com/kburson/aitm/issues/240) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

One coordinated extension to the Core route registry and the installed managed lifecycle entry points.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C67 / #66](../../000/66/story.md), [C82 / #235](../235/story.md), [C85 / #238](../238/story.md).

**Blocking** [C89 / #242](../242/story.md).

**Owned areas** src/aitm_core/cli/catalog.py and managed_lifecycle.py; packages/aitm-core/tests/integration/test_c87.py.

## Acceptance criteria

- [ ] Run installed help and versioned catalog with explicit command, argument, capability and result schema parity. Invoke create/reconcile, pickup, backfill and terminal lifecycle against Core fixtures. Missing handlers or capability remain unavailable. The catalog cannot provide direct provider access.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c87).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **10** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #490 with scope entry **C87**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
