---
schema: "aitm.story/v0"
id: 146
title: "[#133 T09] Implement qualified execution observation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/146"
parent: 133
children: []
blocking: [149, 168]
blocked-by: [144, 145]
created: "2026-11-10T16:51:17Z"
updated: "2026-11-12T20:20:39Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T09", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "96f92716c462213744f98c10b0db9cc163f768fe3bd4bbe4bf9f56644378389d"}
---

# [#133 T09] Implement qualified execution observation

[GitHub issue #146](https://github.com/kburson/aitm/issues/146) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L305)

**Required predecessors** [T07 #144](../144/story.md), [T08 #145](../145/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T09. Implement qualified execution observation — 4h, P1, T07/T08

**Owns** `tools/ci/tia/observe.py`, `test_tia_observe.py` and the
qualified T07 execution adapter.
**Interface** `observe(candidate, collection, assigned_ids, runner_identity) -> Observations`.

- [ ] `test_candidate_cannot_supply_authoritative_outcomes` and
  `test_failure_observed_if_worker_exits_before_finalize` verify
  positive and negative evidence for the assigned subset.
- [ ] Keep controller, credentials and evidence channel outside
  candidate code. Match runtime observation to the prior complete
  collection and exact assignment. V(observe) and native qualification
  repeat on the exact implementation. Split or replan before Develop
  if the approved mechanism exceeds four hours.

## Qualification hold

Backlog / BLOCKED. #144 and #145 ended without qualifying collection and execution. A qualified replacement is required. [Current replan](../133/plan/2026-11-12-133-advisory-and-qualification-replan.md).

## Pickup order

Rank 50 is the next unresolved story. Its trusted collection and execution qualification hold remains active. [Rank order](../../001/133/plan/2026-11-12-133-rank-order.md).
