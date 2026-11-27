---
schema: "aitm.story/v0"
id: 6
title: "[Core C54] Lifecycle, relationships and document-state reducers"
kind: "story"
state: review
issue: "https://github.com/kburson/aitm/issues/6"
parent: 470
children: []
blocking: [8, 9, 78]
blocked-by: [4, 5]
created: "2026-11-09T07:59:49Z"
updated: "2026-11-27T08:57:06.323Z"
last-branch: "codex/core-6-lifecycle-reducers"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C54", "parent": 470}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":470,"design_sources":[2],"scope_entry":"C54","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C54] Lifecycle, relationships and document-state reducers

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#470](https://github.com/kburson/aitm/issues/470). Key: C54. Estimate: **3.5 h**. Blocked by: #4, #5.

Fold typed state and operation facts with pinned workflow provenance. Prove a renamed label, legacy state ID, and historical capability record remain reconstructable. Attempt start and close derive from typed boundary events.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#6](https://github.com/kburson/aitm/issues/6) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C54 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C02 / #4](../4/story.md), [C03 / #5](../5/story.md).

**Blocking:** [C56 / #8](../8/story.md), [C04 / #9](../9/story.md), [C77 / #78](../78/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C02, C03 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/lifecycle.py; src/aitm_core/reducers/lifecycle.py; packages/aitm-core/tests/unit/test_c54.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_lifecycle(state, event) -> StoryState; lifecycle_schemas() -> SchemaSet`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_lifecycle_reducers: initial/state/description/link/estimate/doc-accept/JIT/deliverable/signoff/disposition facts preserve typed state, reciprocal relation preconditions and source/version references; invalid edges/replacements/required fields reject. Pure event fixtures, no Git/process/network. Explicit graduation kind and source-kind draft|plan-entry are folded from facts. core.kind.changed records the bounded split invalidation, while decomposition/refine/plan/jit estimates remain distinct; a proposal cannot satisfy Refine. Preserve plan-entry source/provenance references and decomposition readiness status without claiming own-design acceptance.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c54.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Producer guards/transactions remain in later leaves; this reducer never invents an accepted review or state transition.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Producer guards/transactions remain in later leaves; this reducer never invents an accepted review or state transition.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:49Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `3a939072150c757328b8b98c6fbc8190c562282ed0ab6c012ca14135c2a264c7`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C54",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "dc033fb232c318bd9ddf522d231c51bd09c11c66eb284acaaa2d0bb288946f61"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #470 with scope entry **C54**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).

[Rank 40 pickup plan](plan/2026-11-27-pickup.md) pins the verified #4 and #5 deliveries.

[Accepted pickup review](plan/2026-11-27-pickup-review.md).

[Draft PR #532](https://github.com/kburson/aitm/pull/532) · [Delivery checklist](plan/delivery-checklist.md).
