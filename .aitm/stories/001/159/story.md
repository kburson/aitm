---
schema: "aitm.story/v0"
id: 159
title: "[#133 T22] Implement conditional merge and reconciliation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/159"
parent: 133
children: []
blocking: [161]
blocked-by: [157, 158]
created: "2026-11-10T16:51:48Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T22", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "886d87ceb40b0e6bd88f83fd8488493067d70132132b057f8fe0c80bd4f17266"}
---

# [#133 T22] Implement conditional merge and reconciliation

[GitHub issue #159](https://github.com/kburson/aitm/issues/159) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L528)

**Required predecessors** [T20 #157](../157/story.md), [T21 #158](../158/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T22. Implement conditional merge and reconciliation — 4h, P1, T20/T21

**Owns** `tools/ci/tia/merge.py`, `test_tia_merge.py`.
**Interface** `authorize_merge(request, incident, full_or_pr_proof) -> Intent`
and `reconcile(intent, provider_readback) -> MergeResult`.

- [ ] `test_head_or_base_moved_at_mutation_refuses`,
  `test_stop_between_intent_and_dispatch_and_during_uncertain_merge`, and
  `test_timeout_reconciles_without_duplicate_merge` assert exactness.
- [ ] Apply only T21's qualified method. Validate review, protection,
  base/head, tree, incident version and actor separation. Serialize
  reservation, final admission and dispatch with stop recording. Use
  T20's live continuity gate and admit only the bound exact repair in
  the current version. Test that an unauthorized or second full-pass
  candidate is refused. Cancel
  unsent stale intents. Keep an in-flight unknown intent and the stop
  fence durable. Admit no subsequent merge while ordering remains
  unknown. A conclusively earlier host commit becomes incident
  baseline evidence. Hold on
  drift or unexpected tree. V(merge) and the disposable host
  replay pass before any use as authority.
