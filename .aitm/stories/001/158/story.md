---
schema: "aitm.story/v0"
id: 158
title: "[#133 T21] Qualify the GitHub merge fence"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/158"
parent: 133
children: []
blocking: [159]
blocked-by: []
created: "2026-11-10T16:51:45Z"
updated: "2026-11-10T21:59:41Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-10-158-qualify-github-merge-fence-design.md"], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T21", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "4c57ac72e211b052a8b7ffee538b492427775b5dc3f365a1640c80f72ac54742"}
---

# [#133 T21] Qualify the GitHub merge fence

[GitHub issue #158](https://github.com/kburson/aitm/issues/158) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L507)

**Required predecessors** None.

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T21. Qualify the GitHub merge fence — 3.5h, P1, no predecessor

**Owns** spike report and disposable repository rules evidence.
**Interface** receipt for one qualified GitHub merge method or refusal.

- [ ] In an owner-authorized disposable repo, test a dedicated
  trusted actor, host-enforced exclusive target updates, and a
  head-conditional PR merge. Require proof that the tested tree
  is the exact result of the permitted merge method.
- [ ] Exercise direct push, web/API, other automation, queue,
  head/base movement at mutation, stop between reservation and
  dispatch, and ambiguous in-flight ordinary merge concurrent with a
  stop. Prove the host commit and stop can be ordered. An unsent
  superseded request cannot dispatch. An ambiguous request fences all
  further mutations until readback establishes whether it committed
  before the stop or cannot commit. Reject any route where an ordinary
  update can still commit after the stop. A read followed by an
  unrestricted write, status cache or local epoch alone is insufficient.
  If the host cannot enforce the boundary, hold T22 and its
  descendants. Do not change AITM's production protection.

## Accepted leaf design

[Design](design/2026-11-10-158-qualify-github-merge-fence-design.md) · [Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

The design adopts the accepted #133 contract for this leaf.
