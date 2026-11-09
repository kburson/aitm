---
schema: "aitm.story/v0"
id: 23
title: "[Core C18] Snapshot index and read-only queries"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/23"
parent: 2
children: []
blocking: [56, 81, 65, 68]
blocked-by: [4, 13]
created: "2026-11-09T08:01:02Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c18-snapshot-index-and-read-only-queries"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C18", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "6b5d95b9e618d4d5c3aa6f59d679792a3ca122d8ed2503c6739fa272db5602a3"}
---

# [Core C18] Snapshot index and read-only queries

**GitHub issue:** [kburson/aitm#23](https://github.com/kburson/aitm/issues/23) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C18 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c18-snapshot-index-and-read-only-queries), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C02 / #4](../4/story.md), [C08 / #13](../13/story.md).

**Blocking:** [C51 / #56](../56/story.md), [C78 / #81](../81/story.md), [C49 / #65](../65/story.md), [C52 / #68](../68/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C02, C08 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/index/schema.py; src/aitm_core/index/build.py; src/aitm_core/index/query.py; src/aitm_core/cli/read.py; src/aitm_core/context.py; packages/aitm-core/tests/integration/test_c18.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `index_snapshot(tree: str) -> IndexView; query(snapshot, filter: Query) -> QueryResult; discuss(story, snapshot) -> ContextPacket`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_index_snapshot: WAL rebuild swap and concurrent readers never mix trees; missing/corrupt/locked index falls back to exact tree with equivalent results. FTS covers titles/descriptions/ideas/drafts/lessons; warm reads neither fetch nor publish. Real show/list/search/explain/discuss commands expose pinned freshness; --refresh invokes C08 explicitly, index rebuild uses the same snapshot. Discuss exports context and suggested harness command only, never calls a model. Until C78 supplies the full transition explanation adapter, explain reports that required explanation capability unavailable, alongside pinned freshness; it must not present the partial query view as a complete guard explanation. Other read commands remain usable. Its permanent missing-capability vector explicitly unregisters that handler in test composition.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c18.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Performance budget is checked in C52; avoid eager imports and hidden authoring claims now.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Performance budget is checked in C52; avoid eager imports and hidden authoring claims now.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:02Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `6b5d95b9e618d4d5c3aa6f59d679792a3ca122d8ed2503c6739fa272db5602a3`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C18",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "e2ae3cbf40079d029936f3586ca78eba514492ce81a94a162d21ddfcaf67bf6f"
}
```
