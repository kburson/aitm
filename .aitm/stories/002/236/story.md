---
schema: "aitm.story/v0"
id: 236
title: "[Core C84] Dependent admission and retirement fence"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/236"
parent: 485
children: []
blocking: [237, 241]
blocked-by: [234]
created: "2026-11-11T15:58:16Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c84"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C84", "parent": 485}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":485,"design_sources":[2],"scope_entry":"C84","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C84] Dependent admission and retirement fence

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#485](https://github.com/kburson/aitm/issues/485). Key: C84. Estimate: **3.5 h**. Blocked by: #234.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #236](https://github.com/kburson/aitm/issues/236) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

A shared order for parent-incarnation admissions and retirement, consumed by provisioning, retarget and terminal cleanup.

**Estimate** 3.5 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C81 / #234](../234/story.md).

**Blocking** [C83 / #237](../237/story.md), [C88 / #241](../241/story.md).

**Owned areas** src/aitm_core/managed/retirement_fence.py; packages/aitm-core/tests/integration/test_c84.py.

## Acceptance criteria

- [ ] Race child provisioning, reparent and retarget against retirement at an unchanged parent OID. A winning dependent holds the ref and a winning fence rejects later dependency admission. In-flight or uncontrolled host routes remain pending. Restart reproduces the same admission order.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c84).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **30** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #485 with scope entry **C84**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
