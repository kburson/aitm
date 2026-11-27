---
schema: "aitm.story/v0"
id: 239
title: "[Core C86] Composed-source eligibility for integration delivery"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/239"
parent: 489
children: []
blocking: [241]
blocked-by: [80, 237]
created: "2026-11-11T15:58:19Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c86"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C86", "parent": 489}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":489,"design_sources":[2],"scope_entry":"C86","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C86] Composed-source eligibility for integration delivery

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#489](https://github.com/kburson/aitm/issues/489). Key: C86. Estimate: **4 h**. Blocked by: #80, #237.

Register composed source for Dev, mount pickup and governed PR operations through the shared catalog, and require local proof before push and current hosted CI/XPR for merge. Retirement happens after verified closeout under its retained dependent fence. C100/C101 prove the mounted order and parity.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #239](https://github.com/kburson/aitm/issues/239) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

A typed composed-source receipt and an explicitly scoped C76 guard path.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C79 / #80](../../000/80/story.md), [C83 / #237](../237/story.md).

**Blocking** [C88 / #241](../241/story.md).

**Owned areas** src/aitm_core/managed/composed_source.py and the C76 source guard extension; packages/aitm-core/tests/integration/test_c86.py.

## Acceptance criteria

- [ ] Drive Develop exit for the designated integration story with an exact nonempty delta mapped from verified child deliveries. Bind its literal upstream, pinned baseline, incarnation and exact head/tree. Test distinct nested non-default upstream and wrong-default/sibling, stale/empty/unexplained source, recorded versus foreign empty bootstrap, and separate current Test, independent Review and C41 admission.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c86).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **20** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #489 with scope entry **C86**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
