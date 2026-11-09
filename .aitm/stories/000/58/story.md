---
schema: "aitm.story/v0"
id: 58
title: "[Core C64] Deterministic two-clone qualification fixtures"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/58"
parent: 2
children: []
blocking: [59, 60, 61, 62]
blocked-by: [17, 18, 27, 50]
created: "2026-11-09T08:03:32Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c64-deterministic-two-clone-qualification-fixtures"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C64", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "6138278a4c4ec472dde990c22fc48246f25475451e6a577d5e0e4c199cfed47b"}
---

# [Core C64] Deterministic two-clone qualification fixtures

**GitHub issue:** [kburson/aitm#58](https://github.com/kburson/aitm/issues/58) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C64 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c64-deterministic-two-clone-qualification-fixtures), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C10 / #18](../18/story.md), [C21 / #27](../27/story.md), [C43 / #50](../50/story.md).

**Blocking:** [C70 / #59](../59/story.md), [C50 / #60](../60/story.md), [C65 / #61](../61/story.md), [C66 / #62](../62/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C09, C10, C21, C43 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/support/shared_store.py; tests/integration/test_shared_fixture.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `SharedStoreFixture(clones, remote, barriers, faults); run_schedule(seed, steps) -> ScheduleTrace`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_shared_fixture: disposable two-clone/remote construction, explicit barriers, seeded schedule replay and operation/command capture; prove a blocked worker is released deterministically and cleanup preserves failure evidence. Fault hooks delegate existing producer injection seams for publication ACK, allocation, stale action and repair; test each hook once. This leaf builds infrastructure only, not the full product race matrix. Import support through C01 tests.support.shared_store and its delivered importlib/test-package configuration; no unlisted path hack or pytest config edit is needed.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_shared_fixture.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No live service, generic scheduler or new product recovery behavior. Consumers reuse this delivered harness and producer fixtures.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No live service, generic scheduler or new product recovery behavior. Consumers reuse this delivered harness and producer fixtures.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:32Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
