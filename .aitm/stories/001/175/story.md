---
schema: "aitm.story/v0"
id: 175
title: "[#133 T38] Rehearse conditional repair and fresh trunk proof"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/175"
parent: 133
children: []
blocking: [176, 177]
blocked-by: [173]
created: "2026-11-10T16:52:26Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T38", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "53860aaedd7dc0632a74478e0cf7d2fae85da7403bc4a87bcafcca4b24d0e80c"}
---

# [#133 T38] Rehearse conditional repair and fresh trunk proof

[GitHub issue #175](https://github.com/kburson/aitm/issues/175) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L789)

**Required predecessors** [T36 #173](../173/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T38. Rehearse conditional repair and fresh trunk proof — 4h, P1, T36

**Owns** disposable broken-base repair fixture and bound host trace.
**Interface** incident, admitted exact repair, actual host outcome
and current-trunk full proof for T39.

- [ ] Reuse T23's qualified broken-base fixture. Require full pass
  on the exact combined repair candidate. Reconcile an ambiguous
  mutation and replay the conditional head/base race fixtures from
  T21. A partial repair and an unapproved resulting tree are refused.
- [ ] Run the full suite on the confirmed current trunk. Retain
  the verified transition to workspace update, with ordinary
  merges and code work still stopped for the test incident.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
