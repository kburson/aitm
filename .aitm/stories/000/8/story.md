---
schema: "aitm.story/v0"
id: 8
title: "[Core C56] Evidence, action and provenance reducers with composition"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/8"
parent: 2
children: []
blocking: [9, 29, 77]
blocked-by: [4, 6, 7]
created: "2026-11-09T07:59:57Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c56-evidence-action-and-provenance-reducers-with-composition"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C56", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "a6c5c135e292c010c0ff6b2df760a98609fcd7a03ac852c88bef436d99f59bc3"}
---

# [Core C56] Evidence, action and provenance reducers with composition

**GitHub issue:** [kburson/aitm#8](https://github.com/kburson/aitm/issues/8) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C56 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c56-evidence-action-and-provenance-reducers-with-composition), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C02 / #4](../4/story.md), [C54 / #6](../6/story.md), [C55 / #7](../7/story.md).

**Blocking:** [C04 / #9](../9/story.md), [C24 / #29](../29/story.md), [C73 / #77](../77/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C02, C54, C55 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C02. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/models/evidence.py; src/aitm_core/reducers/evidence.py; src/aitm_core/events.py; packages/aitm-core/tests/unit/test_c56.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_evidence(state, event) -> StoryState; core_reducers() -> ReducerRegistry`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_complete_event_schema: every accepted-design event family has a payload schema and reducer or explicitly descriptive preserved fact; evidence/review-turn/action/outcome/usage provenance folds without duplicate authority. Compose C54/C55 through real fold and export complete JSON Schema. Include core.doc-review.opened and its source identity/time; a missing historical opening remains Unknown, not an invented runtime fact.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c56.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C56 alone updates the shared reducer registration after C54/C55; no unfinished placeholder reducer is production-enabled.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: C56 alone updates the shared reducer registration after C54/C55; no unfinished placeholder reducer is production-enabled.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:57Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `a6c5c135e292c010c0ff6b2df760a98609fcd7a03ac852c88bef436d99f59bc3`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C56",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "fad801716821dc5af9fc84865a9b0f236c75a3bd78498397920c950daa77780d"
}
```
