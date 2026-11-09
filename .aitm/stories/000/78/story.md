---
schema: "aitm.story/v0"
id: 78
title: "[Core C77] Legacy kind normalization and unresolved inventory"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/78"
parent: 2
children: []
blocking: [53]
blocked-by: [5, 6]
created: "2026-11-09T13:42:09Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c77-legacy-kind-normalization-and-unresolved-inventory"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C77", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "35eb268529173fb55c14fc63e78ad3206c3e738367554c25f2fc8712d42ffab5"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C77] Legacy kind normalization and unresolved inventory

**GitHub issue:** [kburson/aitm#78](https://github.com/kburson/aitm/issues/78) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C77 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c77-legacy-kind-normalization-and-unresolved-inventory). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C03 / #5](../5/story.md), [C54 / #6](../6/story.md).

**Blocking:** [C46 / #53](../53/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 2.5 h · **Depends on:** C03, C54 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/migration_kind.py; src/aitm_core/migration/kinds.py; packages/aitm-core/tests/unit/test_c77.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `map_legacy_kind(header, existing_facts, source_provenance) -> KindMapping`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_legacy_kind_mapping maps explicit legacy kind to the normalized initial graduation/kind fact, retaining header path and raw digest. Table vectors cover story/defect/spike/epic; #1/#2 sample headers remain epic. Missing, unknown or contradictory header/fact kinds produce unresolved required inventory, never a story default. No historical split is synthesized. This pure helper owns only kind resolution; C46 supplies pinned actual header bytes/provenance and integrates its unresolved entries, C48 blocks apply, and C51 proves actual whole-corpus folds. The model/result is reused by C46 rather than redefining MigrationInventory.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c77.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure in-memory vectors only; no Git/process/network in this unit lane. Retain the distinction between authoritative historical facts and header-derived backfill.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Pure in-memory vectors only; no Git/process/network in this unit lane. Retain the distinction between authoritative historical facts and header-derived backfill.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:09Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `35eb268529173fb55c14fc63e78ad3206c3e738367554c25f2fc8712d42ffab5`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
