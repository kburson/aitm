---
schema: "aitm.story/v0"
id: 77
title: "[Core C73] Source-review envelope and independence validation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/77"
parent: 2
children: []
blocking: [45]
blocked-by: [12, 21, 8, 32]
created: "2026-11-09T13:42:08Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c73-source-review-envelope-and-independence-validation"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C73", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "ca1734e797629a9965ca7d2728487b24ff9d91d6f510d9a862b603bd180dc095"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C73] Source-review envelope and independence validation

**GitHub issue:** [kburson/aitm#77](https://github.com/kburson/aitm/issues/77) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C73 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c73-source-review-envelope-and-independence-validation). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C07 / #12](../12/story.md), [C16 / #21](../21/story.md), [C56 / #8](../8/story.md), [C57 / #32](../32/story.md).

**Blocking:** [C38 / #45](../45/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3 h · **Depends on:** C07, C16, C56, C57 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/source_review.py; src/aitm_core/reviews/source_record.py; packages/aitm-core/tests/unit/test_c73.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `validate_source_review(record, responses, binding_history, policy) -> ValidatedSourceReview`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_source_review_record parses aitm.source-review/v1: stable ID/story/attempt/reviewed generation, repository/base/head/tree/input-manifest or deliverable digest/baseline, participant identities/provenance, verdict, findings/dispositions, immutable response paths/digests and assurance. Retain/cross-check actual bytes; reject path escape, changed identity bytes, omitted implementing session, self-review, incomparable identity, source mismatch and unresolved required finding. Independence checks every implementing session from retained bindings, not caller claims; optional distinct-provider and allowed-assurance policy are enforced. Preserve declared-manual limits and require observation proof for provider claims. Recovery lineage may map unchanged-source generation explicitly, never by ignoring it. These are pure typed/bundle validation tests; activation and event writes belong to C38.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c73.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reuse C57 compare_participants and its explicit unknown relation, not a second heuristic. No provider endpoint or authentication claim is invented.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Reuse C57 compare_participants and its explicit unknown relation, not a second heuristic. No provider endpoint or authentication claim is invented.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:08Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `ca1734e797629a9965ca7d2728487b24ff9d91d6f510d9a862b603bd180dc095`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
