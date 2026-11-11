---
schema: "aitm.story/v0"
id: 233
title: "[Core C80] Managed provider contracts and capability results"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/233"
parent: 2
children: []
blocking: [234]
blocked-by: [14]
created: "2026-11-11T15:58:14Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c80"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C80", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C80] Managed provider contracts and capability results

[GitHub issue #233](https://github.com/kburson/aitm/issues/233) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Typed effect and capability boundary shared by Core, the GitHub adapter and runtime.

**Estimate** 3.5 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C13 / #14](../../000/14/story.md).

**Blocking** [C81 / #234](../234/story.md).

**Owned areas** src/aitm_core/providers/managed.py and GitHostProvider extension registration; packages/aitm-core/tests/unit/test_c80.py.

## Acceptance criteria

- [ ] Exercise registration of scoped provisioning, observation, readiness, delivery and retirement capabilities, typed pending/unsupported/refused results and receipts. Missing or unqualified capability stays unavailable. No provider endpoints are called.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c80).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
