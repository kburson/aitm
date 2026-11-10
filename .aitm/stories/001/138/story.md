---
schema: "aitm.story/v0"
id: 138
title: "[#133 T01] Pin the serial baseline"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/138"
parent: 133
children: []
blocking: [139]
blocked-by: []
created: "2026-11-10T16:50:57Z"
updated: "2026-11-10T20:54:26Z"
last-branch: "codex/aitm-138-serial-baseline"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/pin-serial-baseline-design.md"], "plan": ["plan/2026-11-10-138-pin-serial-baseline.md", "plan/2026-11-10-138-jit.md", "plan/reviews/spr-2026-11-10-jit/review-manifest.md", "plan/delivery-checklist.md"], "attachments": ["attachments/serial-baseline.md"]}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T01", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "116458afe27d4ab862a97146e04d72bbf6be8f13dc63b491adb1569f3aa8361e"}
---

# [#133 T01] Pin the serial baseline

[GitHub issue #138](https://github.com/kburson/aitm/issues/138) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L172)

**Required predecessors** None.

The planning estimate is 2.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T01. Pin the serial baseline — 2.5h, P1, no predecessor

**Owns** `tools/ci/tia/baseline.py`, `test_tia_baseline.py`, and the
sanitized baseline report. **Interface**
`build_baseline(verified_ci103, timings) -> Baseline`.

- [ ] Pin a green exact #103 trunk and PR candidate, package/CI helper
  inventories, coverage and child evidence, lock and toolchain. Use
  existing #103 verification and outcome custody. This comparison
  baseline cannot authorize the future gate. Retain
  cold and warm runs, with time and runner scope recorded separately.
- [ ] Make `test_baseline_rejects_mixed_attempts` fail first, then
  verify with V(baseline). A base/shard from another attempt cannot
  qualify; both timing samples retain actual measurements or Unknown.

## Accepted leaf design

[Exact design](design/pin-serial-baseline-design.md) · `sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b`.

[SAR](design/reviews/sar-2026-11-10-leaf-design/review-manifest.md) ·
[Independent SPR](design/reviews/spr-2026-11-10-leaf-design/review-manifest.md) ·
[Native XPR](design/reviews/xpr-2026-11-10-leaf-design/review-manifest.md).

## Refined scope and pickup boundary

Accepted own design at `sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b`.
Refine estimate **2.5 implementation agent-hours**, size S,
priority P1. Existing qualified #103 evidence is available. Work is limited to comparing exact attempts, projecting timing evidence, and the focused tests.

GitHub readback confirmed the parent in Dev, no inbound blockers, and
this leaf in Ready for Planning. Reserve an isolated source worktree
on `codex/aitm-138-serial-baseline` at pickup. This leaf owns
`tools/ci/tia/baseline.py` and `tools/ci/tests/test_tia_baseline.py`. These
paths are disjoint from [#140](../140/story.md). Keep the
existing shared CI workflow and gate policy as read-only inputs.
Both leaves can be planned and implemented concurrently after their
own plan, JIT, and implementation authority. If another merge advances
trunk, requalify the affected PR's exact base/head and required review.

## Accepted Plan and JIT

[Implementation plan](plan/2026-11-10-138-pin-serial-baseline.md) · [JIT pickup](plan/2026-11-10-138-jit.md) ·
[Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

Planning is complete for intended attempt 1 on trunk `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`.
The reviewed JIT pins the exact code baseline and delivery coverage.
The estimate remains **2.5 implementation agent-hours**, size S, P1.
The story remains in Planning. Before Develop, recheck applicability
and reserve the declared source worktree under separate authorization.

## Attempt 1

Authorized implementation on `codex/aitm-138-serial-baseline` from trunk `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`. Worktree `aitm-138-dev`, implementer `codex-collaboration:/root/impl138`, closure owner Codex coordinator. Stop before merge.
