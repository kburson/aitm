---
schema: "aitm.story/v0"
id: 176
title: "[#133 T39] Rehearse workspace pause and restart"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/176"
parent: 133
children: []
blocking: [178]
blocked-by: [170, 175]
created: "2026-11-10T16:52:29Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T39", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "d0108142ad713a0db0ced3d16f89554d0a667190a7657176c2572844d08f679a"}
---

# [#133 T39] Rehearse workspace pause and restart

[GitHub issue #176](https://github.com/kburson/aitm/issues/176) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L803)

**Required predecessors** [T33 #170](../170/story.md), [T38 #175](../175/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T39. Rehearse workspace pause and restart — 4h, P1, T33/T38

**Owns** three-clone rehearsal fixtures, restart qualification
receipt and operator runbook under `tools/ci/tia/`.
**Interface** an authenticated trace joining the T38 incident and
trunk proof to every workspace acknowledgment and release.

- [ ] Enroll Codex Desktop on the affected base, Claude Code on an
  earlier base, and a third native session on a separate clone that
  disconnects before notification. Preserve locks and changes.
  Exercise invalid conflict result, stale generation, withdrawal and
  older incident receipt on that roster. Release must refuse while
  any current acknowledgment is missing or invalid.
- [ ] Verify the disconnected workspace can return with the fix
  effective and provide the final acknowledgment before reopening.
  Retain the positive release trace and a separate bound stopped
  fixture with one outstanding receipt as input to T41. T41 owns
  rollback evidence. Keep this rehearsal isolated from live protection,
  schedule and authority mode.
