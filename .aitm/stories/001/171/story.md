---
schema: "aitm.story/v0"
id: 171
title: "[#133 T34] Implement selected-mode gate in shadow"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/171"
parent: 133
children: []
blocking: [172, 173, 174]
blocked-by: [151]
created: "2026-11-10T16:52:16Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T34", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "039955f5690c9227a889b4a8c1d72b00fce43ce4c81b23417236bc4a39034373"}
---

# [#133 T34] Implement selected-mode gate in shadow

[GitHub issue #171](https://github.com/kburson/aitm/issues/171) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L729)

**Required predecessors** [T14 #151](../151/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T34. Implement selected-mode gate in shadow — 4h, P1, T14

**Owns** `tools/ci/tia/selected_gate.py`, `test_tia_selected_gate.py`,
and the selected-only advisory job in `.github/workflows/tia-shadow.yml`.
**Interface** `evaluate_selected(plan, candidate, exact_base) -> GateReport`.

- [ ] `test_full_exact_base_and_changed_line_floor` checks 89.5%
  fails, 90% passes, executable deletion with zero denominator
  chooses full, and unobserved runtime outcomes remain unknown.
- [ ] Apply proposed complete inventories and selected runtime
  comparison with full exact-base evidence; keep mandated helpers,
  child/wheel/file checks. A measured deficit fails, unverifiable
  scope chooses full if trustworthy, and a failed test blocks.
  Run an actual selected and a forced-fallback candidate in the
  read-only hosted shadow, with compatible trusted exact-base proof.
  V(selected_gate) and the hosted receipts pass without publishing
  required PR authority.
