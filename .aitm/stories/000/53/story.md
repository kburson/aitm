---
schema: "aitm.story/v0"
id: 53
title: "[Core C46] Legacy inventory and deterministic v0 adapters"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/53"
parent: 2
children: []
blocking: [54, 228]
blocked-by: [5, 11, 34, 33, 75, 78]
created: "2026-11-09T08:03:11Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C46", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "abc9d63f1fbc4d33f4651d652b78f807d268a73d3c5eaa0287f85ac68f219a25"}
---

# [Core C46] Legacy inventory and deterministic v0 adapters

**GitHub issue:** [kburson/aitm#53](https://github.com/kburson/aitm/issues/53) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C46 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C03 / #5](../5/story.md), [C06 / #11](../11/story.md), [C25 / #34](../34/story.md), [C58 / #33](../33/story.md), [C72 / #75](../75/story.md), [C77 / #78](../78/story.md).

**Blocking:** [C47 / #54](../54/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C03, C06, C25, C58, C72, C77 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/migration/v0.py; src/aitm_core/migration/inventory.py; tests/fixtures/v0/; src/aitm_core/models/migration.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c46.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `inventory_v0(tip: str) -> MigrationInventory; map_v0(inventory) -> MappedRecords; MigrationReceiptV1(input_tip, declaration_hash, adapter, deviations, input_hashes, payload_tree_hash); CutoverBuilder.preview(inventory, declaration, build_context) -> CutoverTree`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_actual_v0: copy pinned actual #1/#2 including all review/backfill/refinement and later leaf-bootstrap records; map same-time state-entered, reciprocal links, null-story draft facts and actor spelling deterministically. Legacy headers fill only absent facts with source/conflict checks; never parse generated details. Early migrate v0 --dry-run emits complete input inventory, planned transformations/deviations and explicitly unbound output values before an exact declaration exists, with no ref, journal, identity or allocation mutation. It declares a pure CutoverBuilder.preview(inventory, declaration, build_context) port; until C48 provides it, predicted output hashes stay unavailable rather than invented. Receipt payload hash excludes the receipt path itself; schema includes exact declaration/prefix and source inventory identities. Inventory every observed event/envelope/data/header shape across the pinned current corpus, not only #1/#2. Pair dependency-added(blocked_by) and dependent-added(blocking) with reciprocal/cycle checks; map bootstrap plan-entry source/alias and parent-plan-decomposition→decomposition proposal, plan-origin/priority and non-runtime provenance without inventing CLI execution or a v1 descriptor. Absolute last-worktree becomes an opaque legacy display ID with unresolved host association; raw source remains retained, never used to select a checkout. Missing required mappings or ambiguous issuance aliases block the affected safe operation; optional unknown data stays opaque. Delegate explicit legacy kind normalization to C77, retaining header path/hash in mapped initial graduation/kind facts and surfacing
  missing/unknown/contradictory values as required unresolved inventory. test_actual_v0_kind checks actual #1/#2 remain epic and no split is synthesized. This is bounded adapter integration over C77's delivered pure mapping, not additional kind-parser implementation inside the already 4 h C46 leaf.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c46.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Freeze source path/hash/license and explicit deviations. Optional opaque/incomplete records survive; required contradictions block safe apply.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Freeze source path/hash/license and explicit deviations. Optional opaque/incomplete records survive; required contradictions block safe apply.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:11Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `abc9d63f1fbc4d33f4651d652b78f807d268a73d3c5eaa0287f85ac68f219a25`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C46",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "335501a9a314721c76f1f4d6588f3ddb1886a98c13fdae1c97fe64d8d23584f1"
}
```
