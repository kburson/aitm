---
schema: "aitm.story/v0"
id: 38
title: "[Core C29] Kind-specific guards and terminal dispositions"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/38"
parent: 2
children: []
blocking: [39, 40, 45, 49, 52, 63, 79, 81]
blocked-by: [37, 76]
created: "2026-11-09T08:02:06Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c29-kind-specific-guards-and-terminal-dispositions"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C29", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "1635a74cf76d80886f2446f425da74b33c9e692539c32b40e7f92bdd306a83ea"}
---

# [Core C29] Kind-specific guards and terminal dispositions

**GitHub issue:** [kburson/aitm#38](https://github.com/kburson/aitm/issues/38) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C29 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c29-kind-specific-guards-and-terminal-dispositions), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C28 / #37](../37/story.md), [C71 / #76](../76/story.md).

**Blocking:** [C30 / #39](../39/story.md), [C31 / #40](../40/story.md), [C38 / #45](../45/story.md), [C42 / #49](../49/story.md), [C45 / #52](../52/story.md), [C62 / #63](../63/story.md), [C76 / #79](../79/story.md), [C78 / #81](../81/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C28, C71 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C71. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/kinds.py; src/aitm_core/dispositions.py; src/aitm_core/cli/dispositions.py; packages/aitm-core/tests/integration/test_c29.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `kind_requirements(kind, slot) -> Requirements; dispose(request: DispositionRequest) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_kind_matrix: epic initial Develop does not need children already active or its own JIT/PR/test; later aggregation requires child evidence/resolved scope. Spike uses deliverable binding/validation. Abandoned/superseded/duplicate need reason and replacement where required; no automatic dependency satisfaction. test_kind_registration uses actual promote through production KindRequirements registration in services.py and the C28 guards/transitions call sites. Story/defect later exits dispatch to the required StoryExitGuards port; an absent required edge evaluator is unknown/unavailable until C76 (Develop) or C79 (Test/Review). Spike substitutions read registered immutable deliverable/validation/review/archive facts, never source-commit or story-test requirements. Epic Plan exit needs a nonempty accepted child set, Develop entry needs no binding/JIT/clock, and later exits call the typed AggregateEvidence port declared here, installed by C62. Before the later evidence producers exist, these integration cases explicitly seed authoritative typed fixture facts and inject fixture aggregate evidence; a separately unregistered aggregate port refuses. Production registration and normal entry are proved, not import-time side effects.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c29.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Producers of source/deliverable evidence are later leaves; guards consume typed applicability and fail unknown conditions honestly.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Producers of source/deliverable evidence are later leaves; guards consume typed applicability and fail unknown conditions honestly.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:06Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `1635a74cf76d80886f2446f425da74b33c9e692539c32b40e7f92bdd306a83ea`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C29",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "8f7bbdb233c2bb839bf40b544ba50f151591fd430da624f56010fd38fc72e797"
}
```
