---
schema: "aitm.story/v0"
id: 155
title: "[#133 T18] Fence authority restore with independent continuity"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/155"
parent: 133
children: []
blocking: [156]
blocked-by: [154]
created: "2026-11-10T16:51:38Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T18", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "1b16ee640fb366cab5f98f21bb66a4e25c4ae0fefdfc10b34b27d7a360ae5234"}
---

# [#133 T18] Fence authority restore with independent continuity

[GitHub issue #155](https://github.com/kburson/aitm/issues/155) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L450)

**Required predecessors** [T17 #154](../154/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T18. Fence authority restore with independent continuity — 3.5h, P1, T17

**Owns** `tools/ci/tia/continuity.py`, `test_tia_continuity.py`.
**Interface** `verify_continuity(local, witness) -> Current | RecoveryHold`
and `record_tail(event, expected_tail) -> ContinuityWitness`.

- [ ] `test_restore_pre_stop_snapshot_with_green_host_stays_held`
  restores old SQLite while a workspace is disconnected and an
  intent unresolved. Verify canonical incident, roster and intent
  survive or ordinary work and merges stay held.
- [ ] Publish the critical ordered event/intent tail with compare-
  and-swap to a separately protected append-only audit ref using a
  distinct trusted identity. Bind the roster and pending mutation
  commitment before emitting an allowance or dispatch. Reconcile
  local/witness disagreement from the retained canonical sequence.
  No receipt or dispatch is issued while the witness is unavailable
  or history is incomplete. V(continuity) passes, including lost
  witness, stale restore and interrupted checkpoint.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
