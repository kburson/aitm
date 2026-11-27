---
schema: "aitm.story/v0"
id: 233
title: "[Core C80] Managed provider contracts and capability results"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/233"
parent: 473
children: []
blocking: [234, 511]
blocked-by: [14]
created: "2026-11-11T15:58:14Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c80"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C80", "parent": 473}
---

# [Core C80] Managed provider contracts and capability results

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#473](https://github.com/kburson/aitm/issues/473). Key: C80. Estimate: **3.5 h**. Blocked by: #14.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #233](https://github.com/kburson/aitm/issues/233) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Typed effect and capability boundary shared by Core, the GitHub adapter and runtime.

**Estimate** 3.5 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C13 / #14](../../000/14/story.md).

**Blocking** [C81 / #234](../234/story.md).

**Owned areas** src/aitm_core/providers/managed.py and GitHostProvider extension registration; packages/aitm-core/tests/unit/test_c80.py.

## Acceptance criteria

- [ ] Exercise registration of scoped provisioning, observation, readiness, delivery and retirement capabilities, typed pending/unsupported/refused results and receipts. Missing or unqualified capability stays unavailable. No provider endpoints are called.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c80).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
