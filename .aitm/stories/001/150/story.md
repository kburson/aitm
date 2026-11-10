---
schema: "aitm.story/v0"
id: 150
title: "[#133 T13] Combine coverage and timing"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/150"
parent: 133
children: []
blocking: [151, 152]
blocked-by: [149]
created: "2026-11-10T16:51:26Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T13", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "7724b7f2c6a045eb859429666e4c497af510c1b4a95e25ee376d6e223565ab38"}
---

# [#133 T13] Combine coverage and timing

[GitHub issue #150](https://github.com/kburson/aitm/issues/150) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L366)

**Required predecessors** [T12 #149](../149/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T13. Combine coverage and timing — 3.5h, P1, T12

**Owns** `tools/ci/tia/aggregate.py`, `test_tia_aggregate.py`.
**Interface** `aggregate(results, coverage, spans) -> GateReport`.

- [ ] `test_coverage_union_preserves_line_branch_and_child` rejects
  a wrong-tree child receipt and distinguishes 89.5% from 90%.
  `test_elapsed_envelope_is_not_sum` tests overlapping shards.
- [ ] Reuse #103 product/helper and wheel checks with exact compatible
  source and the unrounded 90% floor per active product package. Keep
  all three elapsed envelopes and separate queue,
  setup, execution and collector spans. V(aggregate) passes against
  the baseline and deliberately mismatched coverage.
