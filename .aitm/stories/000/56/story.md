---
schema: "aitm.story/v0"
id: 56
title: "[Core C51] Real review/migration and second-clone qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/56"
parent: 2
children: []
blocking: [66, 68, 69]
blocked-by: [55, 23]
created: "2026-11-09T08:03:24Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C51", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "88abe31c6df678c12697ba4ee90dc16ef49d87f93e294007d089d516f6e1413e"}
---

# [Core C51] Real review/migration and second-clone qualification

**GitHub issue:** [kburson/aitm#56](https://github.com/kburson/aitm/issues/56) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C51 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C48 / #55](../55/story.md), [C18 / #23](../23/story.md).

**Blocking:** [C67 / #66](../66/story.md), [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C48, C18 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_v0_cutover.py; tests/integration/test_review_import.py; docs/learn/core-migration.md.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `qualify_cutover(legacy_fixture, declared_policy) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cutover_fresh_clone: actual portable/native #1/#2 plus created leaf fixtures reconstruct every version; live/backfill duplicates normalize once; legacy namespace retained. Clone before/after cutover resumes same identity; compare all input/output hashes and unknown coverage; exact-content missing levels remain unaccepted. Snapshot all refs/journal/allocation files before/after dry-run and prove no mutation. Fresh validator rejects modified declaration/receipt or an undeclared extra legacy commit; exact output payload hash excludes receipt path. Rebuild index from adopted files and compare all query results to tree authority. After binding the exact declaration, run read-only preview and actual fixture apply using the same construction inputs and compare every predicted output/hash, mapped event and accepted snapshot to the actual payload (receipt excluded). Before declaration, verify unavailable output hashes are explicitly marked; neither mode allocates/ref-mutates during dry-run.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_v0_cutover.py packages/aitm-core/tests/integration/test_review_import.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Fixture policy only. Historical blocked/unsubmitted attempts remain evidence, never upgraded to accepted during import.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Fixture policy only. Historical blocked/unsubmitted attempts remain evidence, never upgraded to accepted during import.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:24Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
