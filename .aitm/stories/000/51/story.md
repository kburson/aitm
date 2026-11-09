---
schema: "aitm.story/v0"
id: 51
title: "[Core C44] Estimate lineage, usage and learning outcomes"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/51"
parent: 2
children: []
blocking: [65, 66]
blocked-by: [28, 36, 49]
created: "2026-11-09T08:03:03Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C44", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "af858b3a966ae189b96fab9d3ae3bd9be52761609c89ff1bb39bb29bb01f5397"}
---

# [Core C44] Estimate lineage, usage and learning outcomes

**GitHub issue:** [kburson/aitm#51](https://github.com/kburson/aitm/issues/51) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C44 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C23 / #28](../28/story.md), [C27 / #36](../36/story.md), [C42 / #49](../49/story.md).

**Blocking:** [C49 / #65](../65/story.md), [C67 / #66](../66/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C23, C27, C42 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C42. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/outcomes.py; src/aitm_core/usage.py; packages/aitm-core/tests/unit/test_c44.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `ingest_usage(source, payload) -> OperationResult; triad(story) -> TriadStatus; report_outcomes(snapshot) -> OutcomeReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_triads: original Refine/Plan/JIT retained separately, Close binds delivered/attempted source and qualified actuals/lessons. Duplicate usage with same identity dedups, contradictory payload conflicts; unavailable time/cost and imported/incomplete triads stay excluded from complete calibration. Consume C42 atomic Close outcome through public reporting; C44 adds usage ingestion/triad queries and never becomes a delayed signoff writer. Shared outcomes.py query additions follow C42 source delivery. Expose reporting through the typed query API; no new outcomes CLI route is introduced in M1.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c44.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No rubric/ML implementation; distinguish engaged hours, planning spans, tool duration, wall time and provider units.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No rubric/ML implementation; distinguish engaged hours, planning spans, tool duration, wall time and provider units.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:03Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `af858b3a966ae189b96fab9d3ae3bd9be52761609c89ff1bb39bb29bb01f5397`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C44",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "f2d78e974e1d689be029d77cc71f8327f9003bd9ae924845c3f125c92044c966"
}
```
