---
schema: "aitm.story/v0"
id: 164
title: "[#133 T27] Enroll workspaces and issue bounded decisions"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/164"
parent: 133
children: []
blocking: [165]
blocked-by: [154]
created: "2026-11-10T16:51:59Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T27", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "5bf284000da3eb69e67d8a5ff57ef8ab1e7bd74db505a89b6404ff65b890cd20"}
---

# [#133 T27] Enroll workspaces and issue bounded decisions

[GitHub issue #164](https://github.com/kburson/aitm/issues/164) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L611)

**Required predecessors** [T17 #154](../154/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T27. Enroll workspaces and issue bounded decisions — 4h, P1, T17

**Owns** `tools/ci/tia/workspaces.py`, `test_tia_workspaces.py`.
**Interface** `enroll(identity, generation) -> Workspace` and
`admit(workspace, operation, now) -> Lease | Denial`.

- [ ] `test_disconnect_or_withdrawal_retains_roster_obligation` and
  `test_expired_or_wrong_generation_lease_refuses` exercise identity
  reuse, late enrollment and a disconnected runner.
- [ ] Snapshot the roster at stop. Allow only scoped diagnosis,
  repair, review, and later update under the appropriate phase.
  Proposed bound is a fresh decision per mutation batch with a
  60-second maximum lease and an earlier safe interruption point
  where supported. V(workspaces) passes. Unavailable authority
  refuses fresh ordinary mutations. T27 tests a local decision
  function only. T33 calls it in the live entry point after T20's
  current continuity proof and T32's applicable fix check.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
