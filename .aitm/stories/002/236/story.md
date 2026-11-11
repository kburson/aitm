---
schema: "aitm.story/v0"
id: 236
title: "[Core C84] Dependent admission and retirement fence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/236"
parent: 2
children: []
blocking: [237, 241]
blocked-by: [234]
created: "2026-11-11T15:58:16Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c84"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C84", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C84] Dependent admission and retirement fence

[GitHub issue #236](https://github.com/kburson/aitm/issues/236) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

A shared order for parent-incarnation admissions and retirement, consumed by provisioning, retarget and terminal cleanup.

**Estimate** 3.5 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C81 / #234](../234/story.md).

**Blocking** [C83 / #237](../237/story.md), [C88 / #241](../241/story.md).

**Owned areas** src/aitm_core/managed/retirement_fence.py; packages/aitm-core/tests/integration/test_c84.py.

## Acceptance criteria

- [ ] Race child provisioning, reparent and retarget against retirement at an unchanged parent OID. A winning dependent holds the ref and a winning fence rejects later dependency admission. In-flight or uncontrolled host routes remain pending. Restart reproduces the same admission order.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c84).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
