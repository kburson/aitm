---
schema: "aitm.story/v0"
id: 162
title: "[#133 T25] Bind repair delivery to current trunk"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/162"
parent: 133
children: []
blocking: [163, 169, 173, 174]
blocked-by: [161]
created: "2026-11-10T16:51:54Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T25", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "ccd39e2cfbd67bd67a495118d7d55141a97375071186fd5eebf115e634d73c37"}
---

# [#133 T25] Bind repair delivery to current trunk

[GitHub issue #162](https://github.com/kburson/aitm/issues/162) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L582)

**Required predecessors** [T24 #161](../161/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T25. Bind repair delivery to current trunk — 3.5h, P1, T24

**Owns** `tools/ci/tia/recovery.py`, `test_tia_recovery.py`.
**Interface** `accept_recovery(incident, delivered, full_proof, live) -> Decision`.

- [ ] `test_old_scheduled_failure_can_recognize_exact_landed_fix`
  requires full PR evidence and actual causal proof.
  `test_stale_full_pass_cannot_open_rollout` exercises wrong tree,
  older incident and protection drift.
- [ ] Dispatch full validation on the confirmed repair result;
  update on current trunk only. A verified external/scheduling
  interruption requires diagnosis plus fresh full pass. A repaired
  failing-test incident still requires workspace delivery. V(recovery) passes.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
