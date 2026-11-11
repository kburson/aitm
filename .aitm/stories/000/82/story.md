---
schema: "aitm.story/v0"
id: 82
title: "[Core C75] Plan-entry graduation and provenance reconciliation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/82"
parent: 2
children: []
blocking: [66, 69, 235]
blocked-by: [75, 27, 26, 37, 40, 58, 64, 79, 80]
created: "2026-11-09T13:42:14Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c75-plan-entry-graduation-and-provenance-reconciliation"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C75", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "f165431a5c590a27f3fedaac03ea5dc3d4998e6271999343b83e9fc9b3f6888e"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C75] Plan-entry graduation and provenance reconciliation

**GitHub issue:** [kburson/aitm#82](https://github.com/kburson/aitm/issues/82) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C75 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c75-plan-entry-graduation-and-provenance-reconciliation). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C72 / #75](../75/story.md), [C21 / #27](../27/story.md), [C22 / #26](../26/story.md), [C28 / #37](../37/story.md), [C31 / #40](../40/story.md), [C64 / #58](../58/story.md), [C63 / #64](../64/story.md), [C76 / #79](../79/story.md), [C79 / #80](../80/story.md).

**Blocking:** [C67 / #66](../66/story.md), [C59 / #69](../69/story.md), [C82 / #235](../../002/235/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3.5 h · **Depends on:** C72, C21, C22, C28, C31, C64, C63, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C22, C79. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/decompose.py; src/aitm_core/graduation.py; src/aitm_core/cli/decompose.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c75.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `decompose(epic, entry, expected_plan) -> GraduationResult; reconcile_decomposition(child, expected_source, proposed_source) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_decompose_once uses C64's shared-store harness and actual installed decompose --entry --expected-plan. C72 freezes typed source and C20/C21/C22 reserve/issue/finalize one Backlog child per parent/key with explicit kind, reciprocal parent and decomposition estimate, no draft creation. Two clones/lost ACK/retry after plan revision cannot issue a second child; changed source is retained pending reconciliation. Resolve descriptor dependency keys to permanent IDs via cycle-checked links; unresolved required entries remain visible blockers. test_decomposition_reconcile retains old/new scope and identities, applies explicit scoped reconciliation and invalidates affected description/design/plan applicability; it cannot invent renewed acceptance or auto-overwrite authored files. Own leaf design and explicit Refine estimate are still required. Prove ordinary graduation uses the same generic source predicate and that a missing plan-source adapter returns unavailable before dispatch. Register the C72 applicability service and production source route at the listed sites.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c75.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** 3.5 h integrates already tested descriptor, allocator, relations and publication contracts using C64 fixtures; no new allocator or inherited review mechanism. It lands after C63 to serialize services/graduation wiring, before CLI/release qualification.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: 3.5 h integrates already tested descriptor, allocator, relations and publication contracts using C64 fixtures; no new allocator or inherited review mechanism. It lands after C63 to serialize services/graduation wiring, before CLI/release qualification.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:14Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `f165431a5c590a27f3fedaac03ea5dc3d4998e6271999343b83e9fc9b3f6888e`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

This leaf supplies a prerequisite interface to the managed lifecycle amendment.

New dependent leaves [C82 / #235](../../002/235/story.md).

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.
