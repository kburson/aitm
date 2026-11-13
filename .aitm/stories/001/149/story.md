---
schema: "aitm.story/v0"
id: 149
title: "[#133 T12] Verify shard receipts and inventories"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/149"
parent: 133
children: []
blocking: [150]
blocked-by: [146, 147, 148]
created: "2026-11-10T16:51:24Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T12", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "8dfe6540f8ce14d5a83d22dbd8b275e90fe31f9ad159f3ebf4bab7022d69e6de"}
---

# [#133 T12] Verify shard receipts and inventories

[GitHub issue #149](https://github.com/kburson/aitm/issues/149) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L350)

**Required predecessors** [T09 #146](../146/story.md), [T10 #147](../147/story.md), [T11 #148](../148/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T12. Verify shard receipts and inventories — 4h, P1, T09/T10/T11

**Owns** `tools/ci/tia/receipts.py`, `test_tia_receipts.py`.
**Interface** `verify_receipts(plan, collection, receipts, trusted_base, dispositions) -> Results`.

- [ ] `test_exact_attempt_union_rejects_forgery_or_duplicate` and
  `test_negative_receipt_survives_missing_shard` separate gate
  completeness from an independently verified failure.
- [ ] Reconcile assignments, inventory, policy scopes, required
  outcomes, independently qualified complete collection, and
  same-run/attempt authenticated artifacts. Refuse truncated or
  unverifiable collection in full or selected mode. Record
  candidate removals or runtime degradation against applicable base
  obligations. V(receipts) passes with partial rerun, stale base,
  absent mandatory ID, unexpected skip and extra ID.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
