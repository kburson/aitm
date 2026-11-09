---
schema: "aitm.story/v0"
id: 86
title: "[Usage U13] Draft aliases, ancestry and direct/inclusive rollups"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/86"
parent: 83
children: []
blocking: [90, 91]
blocked-by: [85]
created: "2026-11-09T14:42:17Z"
updated: "2026-11-09T19:11:37+00:00"
last-branch: "codex/aitm-usage-u13"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md", "plan/recovery-plan.md", "plan/recovery-jit.md", "plan/recovery-pickup-review.md", "plan/accounting-integration-jit.md", "plan/accounting-integration-source-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U13", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "266835e43f20043047ae4394ffdb2aa6eb88c119d7a5b71676f37eed1650e2bc"}
---

# [Usage U13] Draft aliases, ancestry and direct/inclusive rollups

[GitHub issue](https://github.com/kburson/aitm/issues/86) · [Parent #83](../83/story.md) · Review

**Required predecessors** [#85](../85/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{rollup,cli}.py`, `tests/test_rollup.py`.

**Contract** `rollup(root: ItemKey, view: LedgerView) -> UsageRollup`. Queue alias and parent commands through U02's inbox. Preserve revisions of ancestry and graduation aliases and compute inclusive totals from distinct canonical descendants. Represent known Decimal price and a separate Unknown count.

- [ ] Write `test_graduation_and_inclusive_rollup` with an epic, two children, an alias from draft to issue, epic batch usage and per-child usage. Assert each observation contributes once, previous as-of results remain intact and cycles or contradictory aliases are refused. Exercise real CLI publication of alias and parent commands. Use price fixtures until U06 supplies accounting.
- [ ] Run `test_rollup.py` to show failure, implement the rollup and alias/ancestry commands, then pass leaf verification.

## Accepted amendment

[Revised implementation plan](../83/plan/usage-capture-replan.md). Extend types.py with typed draft alias and ancestry records and their static codecs. Edit only the corresponding command dispatch cases in scopes.py and use the existing revision store. Prove sequence-specific rollup, corrections and cycle refusal after restart.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Accepted relationship admission amendment](../83/plan/usage-capture-relationship-replan.md). Source candidate `544844a190dc86a92d3db565e73b383125651da5` is preserved in the #86 worktree.

## Repair pickup

[Plan](plan/recovery-plan.md) · [JIT](plan/recovery-jit.md) · [Independent acceptance](plan/recovery-pickup-review.md). Resume in the preserved source worktree.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

[Accounting integration resume evidence](plan/accounting-integration-jit.md).

[Accounting integration stage evidence](plan/accounting-integration-source-review.md).
