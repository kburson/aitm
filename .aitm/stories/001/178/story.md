---
schema: "aitm.story/v0"
id: 178
title: "[#133 T41] Rehearse rollback with a live stop"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/178"
parent: 133
children: []
blocking: []
blocked-by: [172, 176, 177]
created: "2026-11-10T16:52:35Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T41", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "2b7b05fcda546242f59dd6e5399a90a9a8886e63f532cab761551fef6a756df3"}
---

# [#133 T41] Rehearse rollback with a live stop

[GitHub issue #178](https://github.com/kburson/aitm/issues/178) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L837)

**Required predecessors** [T35 #172](../172/story.md), [T39 #176](../176/story.md), [T40 #177](../177/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T41. Rehearse rollback with a live stop — 3h, P1, T35/T39/T40

**Owns** `tools/ci/tia/rollback.py`, `test_tia_rollback.py` and the
disposable rollback report.
**Interface** `change_validation_mode(mode, incident, proof) -> Decision`.

- [ ] `test_full_fallback_preserves_live_stop_and_roster` switches
  simulated selected validation to full with a verified test stop
  and an outstanding workspace receipt. Prove the stop persists,
  ordinary merges and work remain fenced, and the roster is intact.
- [ ] Exercise the policy transition in the isolated rehearsal.
  Restoring selected validation requires fresh control qualification
  and separate authorization. V(rollback) and the bound trace pass.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
