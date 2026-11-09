---
schema: "aitm.story/v0"
id: 74
title: "[Core C74] Entity-scoped editing and graduation handoff"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/74"
parent: 2
children: []
blocking: [25, 26, 27, 40, 50, 66]
blocked-by: [21, 22, 24]
created: "2026-11-09T13:42:06Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c74-entity-scoped-editing-and-graduation-handoff"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C74", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "b924929379782a37195c7b63b264e4c3cf2fb3e9afdfd81c721676886d3fb46a"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C74] Entity-scoped editing and graduation handoff

**GitHub issue:** [kburson/aitm#74](https://github.com/kburson/aitm/issues/74) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C74 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c74-entity-scoped-editing-and-graduation-handoff). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C16 / #21](../21/story.md), [C17 / #22](../22/story.md), [C19 / #24](../24/story.md).

**Blocking:** [C20 / #25](../25/story.md), [C22 / #26](../26/story.md), [C21 / #27](../27/story.md), [C31 / #40](../40/story.md), [C43 / #50](../50/story.md), [C67 / #66](../66/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3.5 h · **Depends on:** C16, C17, C19 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C16, C17, C19. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/entities.py; src/aitm_core/store/workspace.py; src/aitm_core/store/sync.py; src/aitm_core/drafts.py; src/aitm_core/cli/drafts.py; src/aitm_core/cli/sync.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c74.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `open_entity(handle: EntityRef) -> Binding; sync_entity(handle, expected_generation) -> SyncResult; finalize_entity_binding(source, outcome) -> BindingDisposition`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_entity_authoring drives idea open and draft open, real sync --entity/unbind --entity, edits and repeated saves without a story number. Expected-base conflict retains both versions; wrong owner/stale generation/escape/generated metadata refuses. The finalization seam computes a validated binding disposition for the caller's same source-finalization CAS; it makes no independent commit. Graduation/discard includes it to end/fence the exact binding and preserve unsynced conflicts, never silently retargeting the open editor to a numbered story. Unbind failure remains recoverable. Reuse C16/C17 primitives and a small temporary-repository fixture; do not duplicate the binding engine.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c74.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf completes pre-story editing, not a second authoring system. C22 later proves graduation invokes the seam with actual issue finalization; discard is exercised here.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: This leaf completes pre-story editing, not a second authoring system. C22 later proves graduation invokes the seam with actual issue finalization; discard is exercised here.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:06Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `b924929379782a37195c7b63b264e4c3cf2fb3e9afdfd81c721676886d3fb46a`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
