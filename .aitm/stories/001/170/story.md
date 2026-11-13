---
schema: "aitm.story/v0"
id: 170
title: "[#133 T33] Enforce current workspace proof on live admission"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/170"
parent: 133
children: []
blocking: [173, 174, 176]
blocked-by: [169]
created: "2026-11-10T16:52:13Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T33", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "8b582f47ca459a1cb23e86b8163015ddbe686c25def194239d87a7a74f6a0967"}
---

# [#133 T33] Enforce current workspace proof on live admission

[GitHub issue #170](https://github.com/kburson/aitm/issues/170) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L713)

**Required predecessors** [T32 #169](../169/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T33. Enforce current workspace proof on live admission — 3.5h, P1, T32

**Owns** the workspace admission composition in
`tools/ci/tia/authority_io.py`, the T29/T30 native entry-point adapters'
admission wiring, and `test_tia_live_admission.py`.
**Interface** `admit_live(request, continuity, fix_observer) -> Lease | Denial`.

- [ ] `test_live_entry_denies_store_only_or_stale_workspace` proves
  the real lease entry point requires T20 continuity, then T32's
  fresh applicable proof, then T27's operation policy.
- [ ] Run an ordinary native mutation after a valid acknowledgment
  followed by a reverted effective state. Refuse the mutation.
  Refuse a newly enrolled or reopened workspace with stale base and
  admit the same operation only after its fix proof verifies.
  V(live_admission) and the enrolled native smoke pass.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
