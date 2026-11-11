---
schema: "aitm.story/v0"
id: 239
title: "[Core C86] Composed-source eligibility for integration delivery"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/239"
parent: 2
children: []
blocking: [241]
blocked-by: [80, 237]
created: "2026-11-11T15:58:19Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c86"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C86", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C86] Composed-source eligibility for integration delivery

[GitHub issue #239](https://github.com/kburson/aitm/issues/239) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

A typed composed-source receipt and an explicitly scoped C76 guard path.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C79 / #80](../../000/80/story.md), [C83 / #237](../237/story.md).

**Blocking** [C88 / #241](../241/story.md).

**Owned areas** src/aitm_core/managed/composed_source.py and the C76 source guard extension; packages/aitm-core/tests/integration/test_c86.py.

## Acceptance criteria

- [ ] Drive Develop exit for the designated integration story with an exact nonempty delta mapped from verified child deliveries. Bind its literal upstream, pinned baseline, incarnation and exact head/tree. Test distinct nested non-default upstream and wrong-default/sibling, stale/empty/unexplained source, recorded versus foreign empty bootstrap, and separate current Test, independent Review and C41 admission.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c86).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
