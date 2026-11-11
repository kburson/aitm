---
schema: "aitm.story/v0"
id: 47
title: "[Core C40] Reviewed squash and rebase transformation plans"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/47"
parent: 2
children: []
blocking: [48, 79]
blocked-by: [46]
created: "2026-11-09T08:02:45Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c40-reviewed-squash-and-rebase-transformation-plans"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C40", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "a36e70f85863a4007b8b1c0928f3c4ed8032bf853dd2415871825f764f70ea61"}
---

# [Core C40] Reviewed squash and rebase transformation plans

**GitHub issue:** [kburson/aitm#47](https://github.com/kburson/aitm/issues/47) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C40 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c40-reviewed-squash-and-rebase-transformation-plans), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C39 / #46](../46/story.md).

**Blocking:** [C41 / #48](../48/story.md), [C76 / #79](../79/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/delivery/transforms.py; packages/aitm-core/tests/integration/test_c40.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `plan_transformation(inputs: DeliveryInputs, method: DeliveryMethod) -> ApprovedTransformation`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_transform_mapping: pinned pretarget/base/source yield reproducible approved tree/commit mapping for squash/rebase; changed target or conflict requires new reviewed result, not strategy-name acceptance. External transformation without adequate proof remains pending.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c40.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Planning transformation never mutates target. Record approved source/result and authority separately for C41.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Planning transformation never mutates target. Record approved source/result and authority separately for C41.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:45Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `a36e70f85863a4007b8b1c0928f3c4ed8032bf853dd2415871825f764f70ea61`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C40",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "a36e70f85863a4007b8b1c0928f3c4ed8032bf853dd2415871825f764f70ea61"
}
```

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

Keep the exact reviewed transform contract. C86 consumes the mapping for any verified bootstrap rewrite or omission. The managed wrapper remains a separate consumer.

The current planning estimate is **3 implementation agent-hours** (P1/S). The baseline decomposition recorded **3 h**.

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.
