---
schema: "aitm.story/v0"
id: 75
title: "[Core C72] Typed decomposition descriptors and applicability"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/75"
parent: 2
children: []
blocking: [37, 53, 82]
blocked-by: [5, 12, 25, 35, 36]
created: "2026-11-09T13:42:07Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c72-typed-decomposition-descriptors-and-applicability"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C72", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "c291805b48e01fb13932df320b15a231fb409bcbe712f43671a6957a2c8970e2"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C72] Typed decomposition descriptors and applicability

**GitHub issue:** [kburson/aitm#75](https://github.com/kburson/aitm/issues/75) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C72 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c72-typed-decomposition-descriptors-and-applicability). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C03 / #5](../5/story.md), [C07 / #12](../12/story.md), [C20 / #25](../25/story.md), [C26 / #35](../35/story.md), [C27 / #36](../36/story.md).

**Blocking:** [C28 / #37](../37/story.md), [C46 / #53](../53/story.md), [C75 / #82](../82/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3.5 h · **Depends on:** C03, C07, C20, C26, C27 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C26. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/models/decomposition.py; src/aitm_core/decomposition.py; src/aitm_core/reviews/acceptance.py; packages/aitm-core/tests/unit/test_c72.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `prepare_plan_entry(snapshot, epic, key, expected_plan) -> FrozenSource; assess_decomposition(child, parent_snapshot) -> ApplicabilityResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_plan_entry_contract validates the accepted v1 semantic decomposition map: stable unique entry keys, kind, structured description/scope, estimate/size/priority and dependency keys. Canonical descriptor bytes/digest and accepted parent design/plan digests bind the source; arbitrary Markdown cannot be inferred as a descriptor. Entity key (store UUID,parent,key) survives plan revisions, while changed source requires reconciliation. Missing references/cycles/unsupported schema refuse. Own-document policy never accepts parent-only coverage; missing/unsupported coverage stays unavailable. Decomposition proposal does not satisfy Refine; parent design/plan changes produce stale applicability even if entry text is unchanged. Implement the C26 applicability port using pinned typed facts and MemoryBackend, without issuing identities or invoking Git/network.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c72.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure preparation/applicability has a separate gate from C75's live identity and CLI integration. Do not add inherited-design coverage or synthesize historical drafts.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Pure preparation/applicability has a separate gate from C75's live identity and CLI integration. Do not add inherited-design coverage or synthesize historical drafts.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:07Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `c291805b48e01fb13932df320b15a231fb409bcbe712f43671a6957a2c8970e2`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
