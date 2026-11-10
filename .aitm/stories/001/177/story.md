---
schema: "aitm.story/v0"
id: 177
title: "[#133 T40] Rehearse exact repair of a merge-only hold"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/177"
parent: 133
children: []
blocking: [178]
blocked-by: [174, 175]
created: "2026-11-10T16:52:32Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T40", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "f3586714427173b99adc84bc133ddde415af8d51ce1af0325ca652c760639a5b"}
---

# [#133 T40] Rehearse exact repair of a merge-only hold

[GitHub issue #177](https://github.com/kburson/aitm/issues/177) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L823)

**Required predecessors** [T37 #174](../174/story.md), [T38 #175](../175/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T40. Rehearse exact repair of a merge-only hold — 3.5h, P1, T37/T38

**Owns** the isolated broken-scheduled-setup repair and release trace.
**Interface** bound merge-only recovery proof for T41.

- [ ] Use T37's broken scheduled setup, with no verified failing test.
  Record the appointed owner's substantiation of the trunk control
  cause. Bind the single exact repair PR to the current hold version,
  with independent gate-change disposition.
- [ ] Require T24's full candidate proof and T22's conditional host
  mutation. Run a fresh full suite on confirmed current trunk. Retain
  refusal while another recorded cause is unresolved, then the
  verified merge-only release with no workspace-update phase.
