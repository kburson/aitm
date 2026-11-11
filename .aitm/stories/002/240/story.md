---
schema: "aitm.story/v0"
id: 240
title: "[Core C87] Installed managed lifecycle commands and operation catalog"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/240"
parent: 2
children: []
blocking: [242]
blocked-by: [66, 235, 238]
created: "2026-11-11T15:58:20Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c87"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C87", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C87] Installed managed lifecycle commands and operation catalog

[GitHub issue #240](https://github.com/kburson/aitm/issues/240) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

One coordinated extension to the Core route registry and the installed managed lifecycle entry points.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C67 / #66](../../000/66/story.md), [C82 / #235](../235/story.md), [C85 / #238](../238/story.md).

**Blocking** [C89 / #242](../242/story.md).

**Owned areas** src/aitm_core/cli/catalog.py and managed_lifecycle.py; packages/aitm-core/tests/integration/test_c87.py.

## Acceptance criteria

- [ ] Run installed help and versioned catalog with explicit command, argument, capability and result schema parity. Invoke create/reconcile, pickup, backfill and terminal lifecycle against Core fixtures. Missing handlers or capability remain unavailable. The catalog cannot provide direct provider access.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c87).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
