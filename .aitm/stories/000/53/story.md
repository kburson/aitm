---
schema: "aitm.story/v0"
id: 53
title: "[Core C46] Legacy inventory and deterministic v0 adapters"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/53"
parent: 2
children: []
blocking: [54]
blocked-by: [5, 11, 34, 33]
created: "2026-11-09T08:03:11Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C46", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "335501a9a314721c76f1f4d6588f3ddb1886a98c13fdae1c97fe64d8d23584f1"}
---

# [Core C46] Legacy inventory and deterministic v0 adapters

**GitHub issue:** [kburson/aitm#53](https://github.com/kburson/aitm/issues/53) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C46 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C03 / #5](../5/story.md), [C06 / #11](../11/story.md), [C25 / #34](../34/story.md), [C58 / #33](../33/story.md).

**Blocking:** [C47 / #54](../54/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C03, C06, C25, C58 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/migration/v0.py; src/aitm_core/migration/inventory.py; tests/fixtures/v0/; src/aitm_core/models/migration.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c46.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `inventory_v0(tip: str) -> MigrationInventory; map_v0(inventory) -> MappedRecords; MigrationReceiptV1(input_tip, declaration_hash, adapter, deviations, input_hashes, payload_tree_hash); CutoverBuilder.preview(inventory, declaration, build_context) -> CutoverTree`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_actual_v0: copy pinned actual #1/#2 including all review/backfill/refinement and later leaf-bootstrap records; map same-time state-entered, reciprocal links, null-story draft facts and actor spelling deterministically. Legacy headers fill only absent facts with source/conflict checks; never parse generated details. Early migrate v0 --dry-run emits complete input inventory, planned transformations/deviations and explicitly unbound output values before an exact declaration exists, with no ref, journal, identity or allocation mutation. It declares a pure CutoverBuilder.preview(inventory, declaration, build_context) port; until C48 provides it, predicted output hashes stay unavailable rather than invented. Receipt payload hash excludes the receipt path itself; schema includes exact declaration/prefix and source inventory identities.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c46.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Freeze source path/hash/license and explicit deviations. Optional opaque/incomplete records survive; required contradictions block safe apply.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Freeze source path/hash/license and explicit deviations. Optional opaque/incomplete records survive; required contradictions block safe apply.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:11Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
