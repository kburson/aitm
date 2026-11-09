---
schema: "aitm.story/v0"
id: 6
title: "[Core C54] Lifecycle, relationships and document-state reducers"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/6"
parent: 2
children: []
blocking: [8, 9]
blocked-by: [4, 5]
created: "2026-11-09T07:59:49Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C54", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "dc033fb232c318bd9ddf522d231c51bd09c11c66eb284acaaa2d0bb288946f61"}
---

# [Core C54] Lifecycle, relationships and document-state reducers

**GitHub issue:** [kburson/aitm#6](https://github.com/kburson/aitm/issues/6) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C54 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C02 / #4](../4/story.md), [C03 / #5](../5/story.md).

**Blocking:** [C56 / #8](../8/story.md), [C04 / #9](../9/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C02, C03 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/lifecycle.py; src/aitm_core/reducers/lifecycle.py; packages/aitm-core/tests/unit/test_c54.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_lifecycle(state, event) -> StoryState; lifecycle_schemas() -> SchemaSet`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_lifecycle_reducers: initial/state/description/link/estimate/doc-accept/JIT/deliverable/signoff/disposition facts preserve typed state, reciprocal relation preconditions and source/version references; invalid edges/replacements/required fields reject. Pure event fixtures, no Git/process/network.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c54.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Producer guards/transactions remain in later leaves; this reducer never invents an accepted review or state transition.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Producer guards/transactions remain in later leaves; this reducer never invents an accepted review or state transition.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:49Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
