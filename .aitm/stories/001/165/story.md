---
schema: "aitm.story/v0"
id: 165
title: "[#133 T28] Qualify native workspace controls"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/165"
parent: 133
children: []
blocking: [166, 168]
blocked-by: [157, 164]
created: "2026-11-10T16:52:01Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T28", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "2191bf4dce9293de8c0943387b9a4ac6758f9b07a720d64dd1edb00b8a95f5b3"}
---

# [#133 T28] Qualify native workspace controls

[GitHub issue #165](https://github.com/kburson/aitm/issues/165) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L629)

**Required predecessors** [T20 #157](../157/story.md), [T27 #164](../164/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T28. Qualify native workspace controls — 3.5h, P1, T20/T27

**Owns** disposable native harness fixtures and capability report.
**Interface** a pinned registration, guarded operation, notification
and observation route per harness or explicit refusal.

- [ ] Probe actual Codex Desktop and Claude Code builds and scoped
  native PreToolUse/pickup and resume routes for an enrolled identity.
  Test safe interruption, a command or edit with no fresh lease, and
  missed notification. Confirm no unguarded mutation surface is admitted.
- [ ] Prove a trusted local observer under a separate identity can
  take a challenged effective snapshot and run an authority-bound
  fixture probe
  without accepting candidate-authored truth. Establish how a live
  admitted session receives stop via trusted notification and how a
  disconnected session is fenced at its next guarded boundary. A
  failed capability blocks that adapter or the observation leaf.
