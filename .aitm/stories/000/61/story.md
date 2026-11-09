---
schema: "aitm.story/v0"
id: 61
title: "[Core C65] Execution fences and clock-rebuild qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/61"
parent: 2
children: []
blocking: [68, 69]
blocked-by: [58, 39, 40, 41, 42, 45, 49, 57, 79, 80]
created: "2026-11-09T08:03:45Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c65-execution-fences-and-clock-rebuild-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C65", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "4f91a91331bfb5fc2e5eada026da96bf619004141fa5da9aca95e1a1ad2ad1f4"}
---

# [Core C65] Execution fences and clock-rebuild qualification

**GitHub issue:** [kburson/aitm#61](https://github.com/kburson/aitm/issues/61) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C65 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c65-execution-fences-and-clock-rebuild-qualification), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C64 / #58](../58/story.md), [C30 / #39](../39/story.md), [C31 / #40](../40/story.md), [C32 / #41](../41/story.md), [C35 / #42](../42/story.md), [C38 / #45](../45/story.md), [C42 / #49](../49/story.md), [C61 / #57](../57/story.md), [C76 / #79](../79/story.md), [C79 / #80](../80/story.md).

**Blocking:** [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C64, C30, C31, C32, C35, C38, C42, C61, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_execution_races.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_execution_races(fixture: SharedStoreFixture) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** Using C64 and delivered producer cases, collect test_expansion_completion_fence (pending expansion versus actual test/promote/signoff), test_shared_stop_no_test_launch (published enforce stop versus offline test, no subprocess marker), test_trip_before_sync_and_pass (qualifying overrun before sync, CAS retry and completion), and test_reservation_and_review_rebuild (lost identity response resolved without child plus early verdict/later evidence-reconcile activation, discard private caches and rebuild pause/resume/stop from events). Retain workspace/results; no authored import, second launch or effective pass overtakes a stop. Four focused scenarios reuse contract-conforming activity and race hooks; no harness implementation here. Resolve the actual production StoryExitGuards edge evaluators from C76/C79; no fixture evaluator is installed. Before injected failures, establish the applicable positive source/receipt/review/delivery prerequisites through the real pipeline. Assert the specific intended refusal cause (expansion-pending, trip, admission-fenced or stale-generation as appropriate), and reject evaluator-unavailable as a satisfying outcome. This prevents missing composition from making negative assertions pass vacuously.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_execution_races.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No fabricated engagement, source-review authority or real provider capability; fixture evidence is explicit.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No fabricated engagement, source-review authority or real provider capability; fixture evidence is explicit.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:45Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `4f91a91331bfb5fc2e5eada026da96bf619004141fa5da9aca95e1a1ad2ad1f4`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C65",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "8b290dd1d7b9f8adfc111afa6e9ae328469c228c773131ea4b043c37a938e85f"
}
```
