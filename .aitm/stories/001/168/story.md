---
schema: "aitm.story/v0"
id: 168
title: "[#133 T31] Produce trusted workspace update observations"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/168"
parent: 133
children: []
blocking: [169]
blocked-by: [146, 163, 165]
created: "2026-11-10T16:52:09Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T31", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "8f0e3e29e4a70f952c6fef824ff571feff453491ce4314a877dbc6be25c7974f"}
---

# [#133 T31] Produce trusted workspace update observations

[GitHub issue #168](https://github.com/kburson/aitm/issues/168) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L675)

**Required predecessors** [T09 #146](../146/story.md), [T26 #163](../163/story.md), [T28 #165](../165/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T31. Produce trusted workspace update observations — 4h, P1, T09/T26/T28

**Owns** `tools/ci/tia/workspace_observe.py`,
`test_tia_workspace_observe.py`.
**Interface** `observe_workspace(challenge, workspace, probe) -> WorkspaceReceipt`.

- [ ] `test_forged_or_replayed_fix_claim_is_denied` binds a fresh
  authority challenge, identity, generation, incident, repaired
  base, effective working-state digest and incident regression result.
- [ ] Measure tracked and relevant local changes and run the
  current T26 authority-bound probe through the qualified
  observation route. Refuse a stale or client-supplied probe or
  observation, and rebind on an incident version change. Qualify a real
  enrolled workspace, including an effective-state change during
  measurement. V(workspace_observe) and the native proof pass.
