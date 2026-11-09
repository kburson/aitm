---
schema: "aitm.story/v0"
id: 55
title: "[Core C48] Atomic migration apply and accepted-snapshot binding"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/55"
parent: 2
children: []
blocking: [56, 65]
blocked-by: [17, 22, 35, 54, 18]
created: "2026-11-09T08:03:20Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c48-atomic-migration-apply-and-accepted-snapshot-binding"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C48", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "3869d4fb316e357b97e54b06e5a30d1f6263ef879109a4eb6d237aa8ab1fef6a"}
---

# [Core C48] Atomic migration apply and accepted-snapshot binding

**GitHub issue:** [kburson/aitm#55](https://github.com/kburson/aitm/issues/55) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C48 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c48-atomic-migration-apply-and-accepted-snapshot-binding), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C17 / #22](../22/story.md), [C26 / #35](../35/story.md), [C47 / #54](../54/story.md), [C10 / #18](../18/story.md).

**Blocking:** [C51 / #56](../56/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C09, C17, C26, C47, C10 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C10. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/migration/apply.py; src/aitm_core/migration/bindings.py; src/aitm_core/store/validation.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c48.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `apply_adoption(declaration, expected_tip) -> MigrationResult; build_cutover(inventory, declaration, build_context) -> CutoverTree`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cutover_cas: build/validate whole tree off-ref; checkout exclusion and exact declaration recheck; crash before/after CAS and competing clone return one result. Preserve snapshots before metadata rewrite, map canonical bindings per level without upgrading old digests. Move root README prose/provenance under .aitm, remove active root exception. Construct MigrationReceiptV1 over deterministic output payload excluding its own path, then validate whole tree. Wire bounded-legacy/cutover verification into the normal fresh-history validator; reject forged extension of approved legacy prefix, altered declaration/receipt/payload and extra deviations. Own one pure build_cutover(inventory, declaration, build_context) -> CutoverTree used by both bound dry-run preview and apply, and wire the C46 preview port. Build context pins schema-defined deterministic serialization/provenance inputs; actual apply/publication observations live in the separate receipt, not unpredictable payload fields. Preserve source occurrence precision. With identical pinned inputs/declaration/context, preview and apply must agree on mapped facts, raw accepted snapshots, regenerated views and receipt-excluded payload tree hash. Apply may not implement a second transformation path.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c48.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No renumbering, precision fabrication, lost ignored/untracked work, reset or direct writes after committed migration.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No renumbering, precision fabrication, lost ignored/untracked work, reset or direct writes after committed migration.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:20Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
