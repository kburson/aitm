---
schema: "aitm.story/v0"
id: 234
title: "[Core C81] Managed incarnation reservation and effect claims"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/234"
parent: 2
children: []
blocking: [235, 236]
blocked-by: [21, 25, 26, 50, 58, 233]
created: "2026-11-11T15:58:15Z"
updated: "2026-11-11T16:06:06Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c81"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C81", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C81] Managed incarnation reservation and effect claims

[GitHub issue #234](https://github.com/kburson/aitm/issues/234) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Stable resource identity and durable per-effect claims for pre-pickup, current session and terminal service roles.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C16 / #21](../../000/21/story.md), [C20 / #25](../../000/25/story.md), [C22 / #26](../../000/26/story.md), [C43 / #50](../../000/50/story.md), [C64 / #58](../../000/58/story.md), [C80 / #233](../233/story.md).

**Blocking** [C82 / #235](../235/story.md), [C84 / #236](../236/story.md).

**Owned areas** src/aitm_core/managed/incarnations.py and claims.py; packages/aitm-core/tests/integration/test_c81.py.

## Acceptance criteria

- [ ] Reuse the C64 two-clone fixture. Race different operation and incarnation proposals for one permanent story/repository/role. One CAS slot wins. Ordinary rebind keeps the incarnation and fences the old session. Duplicate effects share one claim, unsent claims emit zero writes, and sent ambiguous effects hold until positive adoption or proven safe replay. Reject foreign lookalikes and same-ref/OID reuse while the old request can land.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c81).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
