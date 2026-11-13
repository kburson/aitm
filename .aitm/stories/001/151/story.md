---
schema: "aitm.story/v0"
id: 151
title: "[#133 T14] Run the full and TIA shadow workflow"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/151"
parent: 133
children: []
blocking: [171]
blocked-by: [142, 150]
created: "2026-11-10T16:51:29Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T14", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "dafad92695a04e2c25e319329c1dbc3e876353d915ea6997c3cb7faf1a4bbbea"}
---

# [#133 T14] Run the full and TIA shadow workflow

[GitHub issue #151](https://github.com/kburson/aitm/issues/151) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L380)

**Required predecessors** [T05 #142](../142/story.md), [T13 #150](../150/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T14. Run the full and TIA shadow workflow — 4h, P1, T05/T13

**Owns** `.github/workflows/tia-shadow.yml`,
`tools/ci/tia/hosted.py`, `test_tia_hosted.py`.
**Interface** `shadow(candidate, policy) -> AdvisoryReport`.

- [ ] `test_shadow_cannot_publish_merge_authority` and
  `test_sharded_comparison_requires_identical_candidate` assert
  equal serial/shard node, outcome, line/branch and child proof.
- [ ] Expose package/lane/shard as separate hosted jobs. Keep #103
  as required, publish read-only summaries and exact witness paths.
  Derive hosted assignments only from qualified collection. Force
  full on T10 gate changes and show unresolved approvals hold.
  V(hosted) and an isolated hosted serial versus sharded run pass.
  Do not move the required gate in this story.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
