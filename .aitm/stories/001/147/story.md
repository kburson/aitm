---
schema: "aitm.story/v0"
id: 147
title: "[#133 T10] Bind gate changes and inventory dispositions"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/147"
parent: 133
children: []
blocking: [149]
blocked-by: [139, 140]
created: "2026-11-10T16:51:19Z"
updated: "2026-11-12T02:33:03Z"
last-branch: "codex/aitm-wave30-147"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-11-147-bind-gate-changes-design.md", "design/reviews/spr-2026-11-11-wave30-design/review-manifest.md"], "plan": ["plan/2026-11-11-147-refinement.md", "plan/2026-11-11-147-bind-gate-changes.md", "plan/2026-11-11-147-jit.md", "plan/reviews/spr-2026-11-11-wave30-jit/review-manifest.md", "plan/local-validation.md", "plan/delivery-checklist.md", "plan/local-focused-nodeids.txt", "plan/hosted-readback-a9f97f937369.json", "plan/hosted-signature-a9f97f937369.json", "plan/verifier-hold-a9f97f937369.json", "plan/reviews/2026-11-11-147-source-owner-assessment.md", "plan/local-validation-r2.md", "plan/local-focused-nodeids-r2.txt", "plan/delivery-checklist-r2.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T10", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "49891b6867d122424f43f5b34fd4337a2cb5dc93c6325696b48d4f868f5ec76d"}
---

# [#133 T10] Bind gate changes and inventory dispositions

[GitHub issue #147](https://github.com/kburson/aitm/issues/147) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L320)

**Required predecessors** [T02 #139](../139/story.md), [T03 #140](../140/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T10. Bind gate changes and inventory dispositions — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/controls.py`, `test_tia_controls.py`.
**Interface** `qualify_controls(base, candidate, approvals) -> ControlDisposition`
and `applicable_inventory(reference, target, dispositions) -> Inventory`.

- [ ] `test_control_edit_requires_full_and_independent_disposition`
  holds a gate-defining diff until the trusted approval binds exact
  source, control and scope. A candidate cannot amend its own rules.
- [ ] `test_reference_inventory_requires_intervening_dispositions`
  compares current exact scope to an older qualified reference
  only through verified ordered dispositions. Reject stale, missing
  or wrong-scope approval. V(controls) passes. T12/T14/T15/T24/T34
  consume these same rules for ordinary, scheduled, repair and selected
  paths, without inventing a new approval source.

## Wave 3 refinement draft

Rank 30. The required predecessors are Closed as completed and marked Done. [Refinement draft](plan/2026-11-11-147-refinement-draft.md).

## Wave 30 leaf design and refinement

- [Design](design/2026-11-11-147-bind-gate-changes-design.md) · SHA-256 `b4df3f9233e71f90627fee92f4031664122560739a63c2810310863611660746`
- [Refinement](plan/2026-11-11-147-refinement.md) · SHA-256 `db9524f3e5b595c4e4bfee2d537728eca3831c341cd1f43f4f2bf41dea08aeba`
- [Independent review](design/reviews/spr-2026-11-11-wave30-design/review-manifest.md)

## Wave 30 Plan and JIT

- [Plan](plan/2026-11-11-147-bind-gate-changes.md) · SHA-256 `08d5840595fa108bae1929e7d36ca3cba1425b507432652bfad36eb1d7917af9`
- [Jit](plan/2026-11-11-147-jit.md) · SHA-256 `f70f836effa5e66c30acc0be0f53ca38a19501a62511055748f47d7b389300c2`
- [Independent review](plan/reviews/spr-2026-11-11-wave30-jit/review-manifest.md)

## Wave 30 candidate validation

[Source PR](https://github.com/kburson/aitm/pull/261) · [Local validation](plan/local-validation.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `a9f97f937369192b6f565f6d5cec1e26340358ab`, branch tree `b3aef9e5f6b75aa987f443bc6133d5a243147011`, target base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Hosted exact-candidate verification and independent review are pending.

### First candidate and rework

The first candidate completed six hosted jobs with authenticated signature custody. Its independent source assessment required correction, so the story returned to Develop within the same attempt. [Hosted readback](plan/hosted-readback-a9f97f937369.json) · [Signature](plan/hosted-signature-a9f97f937369.json) · [Source assessment](plan/reviews/2026-11-11-147-source-owner-assessment.md).

## Wave 30 replacement candidate validation

[Source PR](https://github.com/kburson/aitm/pull/261) · [Local validation](plan/local-validation-r2.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `0d8f8ea353d71ab19802e882ceecbd105e6837ae`, branch tree `9699130f9be8411cb2a5646197e803956b1ef1b3`, target base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Hosted exact-candidate verification and independent review are pending.
