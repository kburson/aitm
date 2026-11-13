---
schema: "aitm.story/v0"
id: 173
title: "[#133 T36] Rehearse PR isolation and escaped-defect fencing"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/173"
parent: 133
children: []
blocking: [175]
blocked-by: [162, 170, 171]
created: "2026-11-10T16:52:21Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T36", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "4a0e152aaef5e9553b767d686216175a03ec69f5ae3f8838ab2f5b2aa9f51ec4"}
---

# [#133 T36] Rehearse PR isolation and escaped-defect fencing

[GitHub issue #173](https://github.com/kburson/aitm/issues/173) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L763)

**Required predecessors** [T25 #162](../162/story.md), [T33 #170](../170/story.md), [T34 #171](../171/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T36. Rehearse PR isolation and escaped-defect fencing — 3.5h, P1, T25/T33/T34

**Owns** isolated PR and escaped-defect fixture and bound host trace.
**Interface** a verified test-stop scenario for T38.

- [ ] Validate and actually merge an independent PR and observe
  its agent continue while a separate failed PR remains blocked.
- [ ] Prove verified scheduled test failure and a second verified
  cause hold already-green, queued and alternate update routes.
  Record ordinary delivery deferral and exact stopped state.
  Retain scoped host and agent receipts for both scenarios.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
