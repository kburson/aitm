---
schema: "aitm.story/v0"
id: 241
title: "[Core C88] Core policy for managed PR operations"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/241"
parent: 2
children: []
blocking: [242]
blocked-by: [48, 236, 239]
created: "2026-11-11T15:58:21Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c88"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C88", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C88] Core policy for managed PR operations

[GitHub issue #241](https://github.com/kburson/aitm/issues/241) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Provider-neutral admission for scoped observation, push/refresh, ready/retarget and merge, without a generic proxy.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C41 / #48](../../000/48/story.md), [C84 / #236](../236/story.md), [C86 / #239](../239/story.md).

**Blocking** [C89 / #242](../242/story.md).

**Owned areas** src/aitm_core/managed/operations.py; packages/aitm-core/tests/integration/test_c88.py.

## Acceptance criteria

- [ ] Use deterministic broker doubles to deny unqualified routes, stale runtime scope and cross-story operations. Scope observation to the bound PR and allowed evidence. Enforce dual-role target write policy, invalidation on retarget, C41 and default-only host prerequisites. Check that managed non-default delivery ignores the trunk hold, and a positive #158 boundary without qualified readiness holds integrated repair.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c88).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
