---
schema: "aitm.story/v0"
id: 140
title: "[#133 T03] Resolve exact Git changes"
kind: "story"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/140"
parent: 133
children: []
blocking: [141, 147]
blocked-by: []
created: "2026-11-10T16:51:02Z"
updated: "2026-11-10T20:20:16Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/resolve-exact-git-changes-design.md"], "plan": ["plan/2026-11-10-140-resolve-exact-git-changes.md", "plan/2026-11-10-140-jit.md", "plan/reviews/spr-2026-11-10-jit/review-manifest.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T03", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "e32dead37553daa9b2dda1850688f4ec780517b4fd028345544e794f4872a101"}
---

# [#133 T03] Resolve exact Git changes

[GitHub issue #140](https://github.com/kburson/aitm/issues/140) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L204)

**Required predecessors** None.

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T03. Resolve exact Git changes — 3h, P1, no predecessor

**Owns** `tools/ci/tia/snapshot.py`, `test_tia_snapshot.py`.
**Interface** `resolve(repo, request) -> tuple[Snapshot, Snapshot]`.

- [ ] `test_hosted_diff_matches_tested_tree` refuses a mismatched base
  or head, and `test_local_staged_untracked_rename_and_deleted_paths`
  binds both endpoints and content before and after reading.
- [ ] Use Git trees and NUL-delimited paths for hosted mode. Hash the
  effective local tracked and relevant untracked contents and return
  uncertainty if they change mid-read. V(snapshot) passes with
  missing objects, path escape and non-ASCII path fixtures.

## Accepted leaf design

[Exact design](design/resolve-exact-git-changes-design.md) · `sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248`.

[SAR](design/reviews/sar-2026-11-10-leaf-design/review-manifest.md) ·
[Independent SPR](design/reviews/spr-2026-11-10-leaf-design/review-manifest.md) ·
[Native XPR](design/reviews/xpr-2026-11-10-leaf-design/review-manifest.md).

## Refined scope and pickup boundary

Accepted own design at `sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248`.
Refine estimate **3 implementation agent-hours**, size M,
priority P1. One read-only Git resolver owns two bounded input modes and fixtures for path identity, endpoint changes, and snapshot drift.

GitHub readback confirmed the parent in Dev, no inbound blockers, and
this leaf in Ready for Planning. Reserve an isolated source worktree
on `codex/aitm-140-git-snapshot` at pickup. This leaf owns
`tools/ci/tia/snapshot.py` and `tools/ci/tests/test_tia_snapshot.py`. These
paths are disjoint from [#138](../138/story.md). Keep the
existing shared CI workflow and gate policy as read-only inputs.
Both leaves can be planned and implemented concurrently after their
own plan, JIT, and implementation authority. If another merge advances
trunk, requalify the affected PR's exact base/head and required review.

## Accepted Plan and JIT

[Implementation plan](plan/2026-11-10-140-resolve-exact-git-changes.md) · [JIT pickup](plan/2026-11-10-140-jit.md) ·
[Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

Planning is complete for intended attempt 1 on trunk `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`.
The reviewed JIT pins the exact code baseline and delivery coverage.
The estimate remains **3 implementation agent-hours**, size M, P1.
The story remains in Planning. Before Develop, recheck applicability
and reserve the declared source worktree under separate authorization.
