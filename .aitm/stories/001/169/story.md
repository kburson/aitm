---
schema: "aitm.story/v0"
id: 169
title: "[#133 T32] Verify workspace updates and release barrier"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/169"
parent: 133
children: []
blocking: [170]
blocked-by: [162, 167, 168]
created: "2026-11-10T16:52:11Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T32", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "4f46eb4c52f9d0bf96cc0f80268b2335df4759fa0e1c7b422c4dbc83eaf152c5"}
---

# [#133 T32] Verify workspace updates and release barrier

[GitHub issue #169](https://github.com/kburson/aitm/issues/169) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L691)

**Required predecessors** [T25 #162](../162/story.md), [T30 #167](../167/story.md), [T31 #168](../168/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T32. Verify workspace updates and release barrier — 4h, P1, T25/T30/T31

**Owns** `tools/ci/tia/restart.py`, `test_tia_restart.py`.
**Interface** `acknowledge(incident, effective_snapshot, fix_proof) -> WorkspaceReceipt`
and `release(incident, current_receipts) -> Decision`. Export
`check_effective(workspace, fresh_receipt, incident) -> Current | Hold`
for T33 to call before live lease issuance.

- [ ] `test_repaired_ancestry_with_bad_conflict_stays_held` and
  `test_final_workspace_receipt_reopens_only_current_stop` verify
  relevant working changes, disconnected workspace, and new failure
  between update and release.
- [ ] Use the incident regression probe on effective state as well
  as ancestry. Verify the T26 probe version and digest, bind workspace
  and generation, and recheck every
  current receipt before release and at next admission. Preserve
  user changes and never clear the roster by enrollment withdrawal.
  Consume the challenged receipt from T31 and re-observe effective
  state at release and next admission. A change after acknowledgment
  invalidates eligibility until the new proof verifies.
  V(restart) passes.
