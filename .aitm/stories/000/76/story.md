---
schema: "aitm.story/v0"
id: 76
title: "[Core C71] Bounded Refine split and kind invalidation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/76"
parent: 2
children: []
blocking: [38, 40, 66]
blocked-by: [37, 26, 35, 36]
created: "2026-11-09T13:42:07Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c71-bounded-refine-split-and-kind-invalidation"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C71", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "749fbce4b86eb57cc4fdbed702c0d287e7d9ff7815cedeab909fe8558c1e098f"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C71] Bounded Refine split and kind invalidation

**GitHub issue:** [kburson/aitm#76](https://github.com/kburson/aitm/issues/76) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C71 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c71-bounded-refine-split-and-kind-invalidation). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C28 / #37](../37/story.md), [C22 / #26](../26/story.md), [C26 / #35](../35/story.md), [C27 / #36](../36/story.md).

**Blocking:** [C29 / #38](../38/story.md), [C31 / #40](../40/story.md), [C67 / #66](../66/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3.5 h · **Depends on:** C28, C22, C26, C27 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C28. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/splitting.py; src/aitm_core/machine/transitions.py; src/aitm_core/machine/guards.py; src/aitm_core/cli/split.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c71.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `split_leaf(request: SplitRequest) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_refine_split drives split --reason --scope-file on an oversized pre-Develop Refine story/defect/spike. One CAS keeps the permanent ID, records core.kind.changed and revised scope, returns to Backlog and invalidates effective old design/plan/JIT/estimate applicability while retaining all history. Reject expansion children, an existing attempt, unresolved execution/identity and bad relationships. A concurrent source/state change forces reevaluation or retained conflict. New own aggregate design and Refine estimate are required; Plan exit requires accepted nonempty child coverage, not conversion alone. For later Plan/JIT oversizing exercise the existing design-rework edge from Plan/JIT to Backlog, then Backlog→Refine before split; no Plan→Refine edge or post-attempt conversion. Use already delivered normal graduation/link to attach children; split dispatches no remote issue call.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c71.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** The 3.5 h budget reuses transaction, edge, description and acceptance primitives; general kind editing is out of scope. Wire the production route and guard invalidation at the listed call sites.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: The 3.5 h budget reuses transaction, edge, description and acceptance primitives; general kind editing is out of scope. Wire the production route and guard invalidation at the listed call sites.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:07Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `749fbce4b86eb57cc4fdbed702c0d287e7d9ff7815cedeab909fe8558c1e098f`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
