---
schema: "aitm.story/v0"
id: 235
title: "[Core C82] Explicit target backfill for graduated stories"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/235"
parent: 485
children: []
blocking: [237, 240]
blocked-by: [82, 234]
created: "2026-11-11T15:58:15Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c82"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C82", "parent": 485}
---

# [Core C82] Explicit target backfill for graduated stories

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#485](https://github.com/kburson/aitm/issues/485). Key: C82. Estimate: **3 h**. Blocked by: #82, #234.

Reserve or backfill exact target and incarnation at pickup. Separate published branch and draft effect claims and their ambiguity recovery. Do not accept provisioning CI as candidate proof. Verify a supported bootstrap commit has the same tree.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #235](https://github.com/kburson/aitm/issues/235) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Published target backfill entry point independent of branch creation, with deterministic read-set and validation.

**Estimate** 3 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C75 / #82](../../000/82/story.md), [C81 / #234](../234/story.md).

**Blocking** [C83 / #237](../237/story.md), [C87 / #240](../240/story.md).

**Owned areas** src/aitm_core/managed/targets.py; packages/aitm-core/tests/integration/test_c82.py.

## Acceptance criteria

- [ ] Exercise authorized publication for an existing numbered story. Resolve the literal repository/ref and optional target incarnation. Deny unauthorized, absent, self, sibling, stale and implicit-default substitutions. Identical backfill is replay-safe and an ambiguous old target leaves provisioning pending.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c82).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
