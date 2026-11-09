---
schema: "aitm.story/v0"
id: 60
title: "[Core C50] Shared-store conflicts and publication recovery qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/60"
parent: 2
children: []
blocking: [68, 69]
blocked-by: [58, 22, 39]
created: "2026-11-09T08:03:41Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c50-shared-store-conflicts-and-publication-recovery-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C50", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "7fd21eae240091faed932551b8955043425202bcf2f6dc3ba7815d0b81a99de9"}
---

# [Core C50] Shared-store conflicts and publication recovery qualification

**GitHub issue:** [kburson/aitm#60](https://github.com/kburson/aitm/issues/60) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C50 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c50-shared-store-conflicts-and-publication-recovery-qualification), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C64 / #58](../58/story.md), [C17 / #22](../22/story.md), [C30 / #39](../39/story.md).

**Blocking:** [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C64, C17, C30 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_shared_store.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_shared_matrix(disposable_remotes) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_eight_by_fifty: eight disjoint stories ×50 real CLI syncs retain all work using C64 barriers. test_conflicting_inputs covers same-story/related-policy/authored conflicts with both versions retained. test_publication_recovery covers the existing ACK-loss, allocator, stale-action and maximal-valid-prefix repair hooks through two clones; deterministic fault fixtures are reused, not rebuilt. No execution/delivery races are owned here.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_shared_store.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Bounded shared-store matrix over delivered behavior; missing production semantics return to their owning leaf/replan.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Bounded shared-store matrix over delivered behavior; missing production semantics return to their owning leaf/replan.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:41Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
