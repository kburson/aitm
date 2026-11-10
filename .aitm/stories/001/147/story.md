---
schema: "aitm.story/v0"
id: 147
title: "[#133 T10] Bind gate changes and inventory dispositions"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/147"
parent: 133
children: []
blocking: [149]
blocked-by: [139, 140]
created: "2026-11-10T16:51:19Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T10", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "49891b6867d122424f43f5b34fd4337a2cb5dc93c6325696b48d4f868f5ec76d"}
---

# [#133 T10] Bind gate changes and inventory dispositions

[GitHub issue #147](https://github.com/kburson/aitm/issues/147) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L320)

**Required predecessors** [T02 #139](../139/story.md), [T03 #140](../140/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T10. Bind gate changes and inventory dispositions — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/controls.py`, `test_tia_controls.py`.
**Interface** `qualify_controls(base, candidate, approvals) -> ControlDisposition`
and `applicable_inventory(reference, target, dispositions) -> Inventory`.

- [ ] `test_control_edit_requires_full_and_independent_disposition`
  holds a gate-defining diff until the trusted approval binds exact
  source, control and scope. A candidate cannot amend its own rules.
- [ ] `test_reference_inventory_requires_intervening_dispositions`
  compares current exact scope to an older qualified reference
  only through verified ordered dispositions. Reject stale, missing
  or wrong-scope approval. V(controls) passes. T12/T14/T15/T24/T34
  consume these same rules for ordinary, scheduled, repair and selected
  paths, without inventing a new approval source.
