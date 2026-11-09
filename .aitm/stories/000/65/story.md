---
schema: "aitm.story/v0"
id: 65
title: "[Core C49] Core-only nominal lifecycle qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/65"
parent: 2
children: []
blocking: [66, 67, 68, 69]
blocked-by: [20, 23, 24, 26, 35, 36, 40, 42, 45, 46, 49, 50, 51, 52, 57, 63, 27, 18, 48, 55, 64]
created: "2026-11-09T08:04:06Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c49-core-only-nominal-lifecycle-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C49", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "bef8bb31e99862b432f75bd1f90cca80b174c0a5df331629ea3e0b4b7c859082"}
---

# [Core C49] Core-only nominal lifecycle qualification

**GitHub issue:** [kburson/aitm#65](https://github.com/kburson/aitm/issues/65) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C49 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c49-core-only-nominal-lifecycle-qualification), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C12 / #20](../20/story.md), [C18 / #23](../23/story.md), [C19 / #24](../24/story.md), [C22 / #26](../26/story.md), [C26 / #35](../35/story.md), [C27 / #36](../36/story.md), [C31 / #40](../40/story.md), [C35 / #42](../42/story.md), [C38 / #45](../45/story.md), [C39 / #46](../46/story.md), [C42 / #49](../49/story.md), [C43 / #50](../50/story.md), [C44 / #51](../51/story.md), [C45 / #52](../52/story.md), [C61 / #57](../57/story.md), [C62 / #63](../63/story.md), [C21 / #27](../27/story.md), [C10 / #18](../18/story.md), [C41 / #48](../48/story.md), [C48 / #55](../55/story.md), [C63 / #64](../64/story.md).

**Blocking:** [C67 / #66](../66/story.md), [C68 / #67](../67/story.md), [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C12, C18, C19, C22, C26, C27, C31, C35, C38, C39, C42, C43, C44, C45, C61, C62, C21, C10, C41, C48, C63 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_core_walk.py; tests/fixtures/reviews/; docs/learn/core-cli-walk.md.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_core_walk(fixture_policy, local_repository) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_complete_cli_walk: installed init/config commit/rerun, idea/draft/local graduation, genuine imported design/plan review fixtures, estimates/JIT, tagged source change, test, independent source review, observed authorized fixture merge and retro yield delivered Done. Negative missing/stale proof retains failures. No SDK/GitHub; every action is real installed CLI, not direct helper substitution. The nominal init --local walk asserts publication not-applicable. A separate test_default_publication_pending uses a remote-configured disposable store and verifies promote without --push attempts default publication and reports retryable pending after simulated ACK loss. Deliver the matching nominal-walk tutorial; exceptional lifecycle and broad route audits have separate owners C68 and C67.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_core_walk.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Qualification only; no late feature implementation. Reuse reviewed producer fixtures and preserve honest fixture-policy assurance.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Qualification only; no late feature implementation. Reuse reviewed producer fixtures and preserve honest fixture-policy assurance.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:06Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
