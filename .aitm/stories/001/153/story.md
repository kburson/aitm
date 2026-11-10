---
schema: "aitm.story/v0"
id: 153
title: "[#133 T16] Define the line incident reducer"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/153"
parent: 133
children: []
blocking: [154]
blocked-by: [152]
created: "2026-11-10T16:51:33Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T16", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "3a25746972c4921aea0b67a6cc6d974e725384a03118bc96ce348795476820f0"}
---

# [#133 T16] Define the line incident reducer

[GitHub issue #153](https://github.com/kburson/aitm/issues/153) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L413)

**Required predecessors** [T15 #152](../152/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T16. Define the line incident reducer — 3.5h, P1, T15

**Owns** `tools/ci/tia/incident.py`, `test_tia_incident.py`.
**Interface** `reduce_incident(state, event) -> Incident` with typed owner appointment,
repair-candidate binding and external-cause disposition.

- [ ] `test_pr_failure_is_local`, `test_second_failure_advances_stop_version`,
  and `test_verified_skip_or_floor_miss_holds_merges_only` distinguish
  false, missing and complete outcomes.
- [ ] Fold ordered facts idempotently, with verified test failure
  taking precedence over merge-only holds. Version distinct unresolved
  causes and fence stale repair, recovery and workspace evidence.
  Persist the appointed owner and exactly one eligible repair PR
  identity, head, base, tree and incident version. Bind a source
  repair under a merge-only hold only after that owner substantiates
  the trunk-source/control cause. Reject unauthorized appointments,
  old assignments and a second full-passing PR.
  V(incident) passes for late pass, duplicate and wrong repository.
