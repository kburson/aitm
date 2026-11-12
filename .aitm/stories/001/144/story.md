---
schema: "aitm.story/v0"
id: 144
title: "[#133 T07] Qualify trusted pytest observation"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/144"
parent: 133
children: []
blocking: [145, 146]
blocked-by: [139]
created: "2026-11-10T16:51:12Z"
updated: "2026-11-12T01:57:47Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-11-144-trusted-pytest-observation-design.md", "design/reviews/spr-2026-11-11-wave30-design/review-manifest.md"], "plan": ["plan/2026-11-11-144-refinement.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T07", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "638dc7c738badde978b3799404e9210cef3c1a5798f1f0591fd6274ef0dee1ad"}
---

# [#133 T07] Qualify trusted pytest observation

[GitHub issue #144](https://github.com/kburson/aitm/issues/144) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L268)

**Required predecessors** [T02 #139](../139/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T07. Qualify trusted pytest observation — 3.5h, P1, T02

**Owns** spike report and disposable fixtures, with no production
observer. **Interface** a pinned host/runner capability receipt,
attack cases, and a bounded controller design or an explicit refusal.

- [ ] In an isolated qualified macOS/APFS runner, distinguish
  candidate-writable output from an externally observed runner.
  Exercise forged same-shape receipt, removed test during collection,
  fake pass through in-process hooks, and authenticated failure with
  a missing sibling shard. Include native child-process coverage.
- [ ] Prototype an independently controlled observer and receipt
  channel under a separate principal. Qualify complete collection
  before assignment and actual execution afterward. In particular,
  hide a newly collected ID before assignment and substitute a pass
  after assignment. Require a trusted completeness check or refusal
  in both full and selected modes. Document what arbitrary
  candidate code in a pytest process can still influence. Passing
  fixture output or artifact provenance alone cannot prove actual
  test execution. If the boundary cannot resist the cases, stop
  T08/T09 and their descendants. Keep #103 and local advisory available
  and return the boundary to design review.

## Wave 3 refinement draft

Rank 30. The required predecessors are Closed as completed and marked Done. [Refinement draft](plan/2026-11-11-144-refinement-draft.md).

## Wave 30 leaf design and refinement

- [Design](design/2026-11-11-144-trusted-pytest-observation-design.md) · SHA-256 `04489f58b31a1904e9e6f0926a6ed9a9e2c00f4362f55d95343863cc1240a8cc`
- [Refinement](plan/2026-11-11-144-refinement.md) · SHA-256 `0eccbc15c939aba16526993429bf6b3b1937ece8988430f4ed9ee489587e615d`
- [Independent review](design/reviews/spr-2026-11-11-wave30-design/review-manifest.md)
