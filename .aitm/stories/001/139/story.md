---
schema: "aitm.story/v0"
id: 139
title: "[#133 T02] Classify the pytest inventory"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/139"
parent: 133
children: []
blocking: [141, 142, 144, 147, 148]
blocked-by: [138]
created: "2026-11-10T16:50:59Z"
updated: "2026-11-10T22:24:31Z"
last-branch: "codex/aitm-139-inventory"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-10-139-classify-pytest-inventory-design.md"], "plan": ["plan/2026-11-10-139-classify-pytest-inventory.md", "plan/2026-11-10-139-jit.md", "plan/reviews/spr-2026-11-10-jit/review-manifest.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T02", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "ade97a158a01113fdd6c0651f09b46de587adb902a86e0d8908c371e4c5edd54"}
---

# [#133 T02] Classify the pytest inventory

[GitHub issue #139](https://github.com/kburson/aitm/issues/139) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L187)

**Required predecessors** [T01 #138](../138/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T02. Classify the pytest inventory — 3.5h, P1, T01

**Owns** `tools/ci/tia/inventory.py`, `tools/ci/tia/suites.json`,
`test_tia_inventory.py`. **Interface**
`classify(collection, suite_policy) -> Inventory`. Its input is a
local advisory observation or a hosted `CollectionProof`; preserve
that distinction in the inventory identity.

- [ ] Add `test_classification_preserves_parametrized_platform_ids`
  and `test_unclassified_or_duplicate_fails`. A parameterized test
  stays unique per required platform, and APFS/ACL and shared process
  groups keep explicit obligations.
- [ ] Encode approved unit, integration and system rules and preserve
  #103 required tests, optional skips, CLI subprocesses and CI helper
  ownership. V(inventory) passes and the full classified inventory
  reconciles with the serial baseline.

## Accepted leaf design

[Design](design/2026-11-10-139-classify-pytest-inventory-design.md) · [Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

The design adopts the accepted #133 contract for this leaf.

## Accepted Plan and JIT

[Implementation plan](plan/2026-11-10-139-classify-pytest-inventory.md) · [JIT pickup](plan/2026-11-10-139-jit.md) ·
[Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

Refinement verified **3.5 implementation agent-hours**, size M, P1,
with Rank 20 preserved. Classify the delivered pytest inventory with a versioned policy and focused reconciliation tests.
The JIT pins trunk `a495d60a87ac4ca764f019dc266e579f13f1787e` for intended attempt 1.
The GitHub Project is in Planning.

Before Develop, recheck the reviewed inputs and bind an isolated source
worktree to the authorized attempt.

## Attempt 1

Authorized implementation on `codex/aitm-139-inventory` from trunk `a495d60a87ac4ca764f019dc266e579f13f1787e`. Worktree `aitm-139-dev`, implementer `codex-collaboration:/root/impl139`, closure owner Codex coordinator. Proceed through Test, independent source review, required gate disposition, verified delivery and Close.

## Accepted target refresh

[Exact JIT and taxonomy delta](plan/2026-11-10-139-jit-target-refresh.md) · [Independent SPR](plan/reviews/spr-2026-11-10-target-refresh.md).

The #182 merge added 119 test IDs, including two explicit integration
module rules. Develop attempt 1 refreshes its target to
`49865245d175ce6c52913738f2c9a42c0abea632`. Its frozen source and validation
remain separate evidence.
