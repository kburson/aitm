---
schema: "aitm.story/v0"
id: 235
title: "[Core C82] Explicit target backfill for graduated stories"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/235"
parent: 2
children: []
blocking: [237, 240]
blocked-by: [82, 234]
created: "2026-11-11T15:58:15Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c82"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C82", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C82] Explicit target backfill for graduated stories

[GitHub issue #235](https://github.com/kburson/aitm/issues/235) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Published target backfill entry point independent of branch creation, with deterministic read-set and validation.

**Estimate** 3 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C75 / #82](../../000/82/story.md), [C81 / #234](../234/story.md).

**Blocking** [C83 / #237](../237/story.md), [C87 / #240](../240/story.md).

**Owned areas** src/aitm_core/managed/targets.py; packages/aitm-core/tests/integration/test_c82.py.

## Acceptance criteria

- [ ] Exercise authorized publication for an existing numbered story. Resolve the literal repository/ref and optional target incarnation. Deny unauthorized, absent, self, sibling, stale and implicit-default substitutions. Identical backfill is replay-safe and an ambiguous old target leaves provisioning pending.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c82).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
