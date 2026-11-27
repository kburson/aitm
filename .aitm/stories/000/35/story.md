---
schema: "aitm.story/v0"
id: 35
title: "[Core C26] CAS review import and exact-content acceptance"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/35"
parent: 477
children: []
blocking: [36, 37, 55, 65, 75, 76, 478, 479, 482, 486, 487, 501, 502]
blocked-by: [15, 22, 33, 34]
created: "2026-11-09T08:01:54Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c26-cas-review-import-and-exact-content-acceptance"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C26", "parent": 477}
---

# [Core C26] CAS review import and exact-content acceptance

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#477](https://github.com/kburson/aitm/issues/477). Key: C26. Estimate: **4 h**. Blocked by: #15, #22, #33, #34.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

Integration owner. Trunk admission requires verified deliveries: #29, #32, #33, #34.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#35](https://github.com/kburson/aitm/issues/35) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C26 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c26-cas-review-import-and-exact-content-acceptance), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C14 / #15](../15/story.md), [C17 / #22](../22/story.md), [C25 / #34](../34/story.md), [C58 / #33](../33/story.md).

**Blocking:** [C27 / #36](../36/story.md), [C72 / #75](../75/story.md), [C28 / #37](../37/story.md), [C71 / #76](../76/story.md), [C48 / #55](../55/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C14, C17, C25, C58 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/importer.py; src/aitm_core/reviews/acceptance.py; src/aitm_core/cli/review_import.py; src/aitm_core/cli/design.py; src/aitm_core/cli/plan.py; packages/aitm-core/tests/integration/test_c26.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `import_review(binding, bundle, expected_base) -> OperationResult; evaluate_acceptance(doc, policy, records) -> AcceptanceResult; accept_document(role, validated_review, expected_doc, policy) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_exact_content: SAR(A) SPR(B) XPR(C) cannot accept C under exact-content three-level policy; add missing levels on C, edit to D recomputes all obligations. Metadata-only rewrite preserves canonical binding. Stale FUR/collateral conflicts and immutable original overwrite refuse. Drive real design accept --review and plan accept --review: persist core.doc.accepted only for validated current content/policy, with plan generation; import/evaluation alone does not append acceptance or satisfy guard. Own-document coverage is explicit: parent plan acceptance alone cannot satisfy a child design guard, and missing/unsupported coverage policy is unavailable. Consume the typed decomposition applicability port declared here (C72 implements it) for plan-entry children; an absent required port cannot infer freshness. Ordinary draft-origin cases do not require that port.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c26.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Production level matrix remains owner-open; fixture policy explicitly permits manual/native-unavailable assurance. Scoped exception requires committed authority/digest/validity.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Production level matrix remains owner-open; fixture policy explicitly permits manual/native-unavailable assurance. Scoped exception requires committed authority/digest/validity.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:54Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `60ff6b1629c42a401e65def14af6fcafd0014091c3984080ce01c35b75ba91f0`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C26",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "37d70ab81afd753bf33d179d4cdd3eb4353abe8df558ca0c529fea062ec6a264"
}
```
