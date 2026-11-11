---
schema: "aitm.story/v0"
id: 238
title: "[Core C85] Terminal managed PR and worktree retirement"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/238"
parent: 2
children: []
blocking: [240]
blocked-by: [80, 237]
created: "2026-11-11T15:58:17Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c85"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C85", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C85] Terminal managed PR and worktree retirement

[GitHub issue #238](https://github.com/kburson/aitm/issues/238) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Replay-safe terminal retirement orchestration using the dependent fence, exact receipts and owning worktree manager.

**Estimate** 4 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C79 / #80](../../000/80/story.md), [C83 / #237](../237/story.md).

**Blocking** [C87 / #240](../240/story.md).

**Owned areas** src/aitm_core/managed/retire.py; packages/aitm-core/tests/integration/test_c85.py.

## Acceptance criteria

- [ ] After completion or abandonment, reconcile effects, retain a merged PR and delivery mapping, close an open abandoned PR and retire only the bound exact ref and owned worktree. Verify outstanding dependents, conditional delete or hold, host retarget invalidation, and a recoverable scrap source before deletion. Lost responses resume the same terminal intent.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c85).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
