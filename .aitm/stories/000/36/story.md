---
schema: "aitm.story/v0"
id: 36
title: "[Core C27] Attempts, JIT coverage and estimates"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/36"
parent: 2
children: []
blocking: [37, 40, 51, 57, 59, 65]
blocked-by: [21, 28, 35]
created: "2026-11-09T08:01:58Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c27-attempts-jit-coverage-and-estimates"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C27", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "61806d99c8f445c5dc2a7f98a409fd5048aa43b98f0b03b101532a3f9b1f452e"}
---

# [Core C27] Attempts, JIT coverage and estimates

**GitHub issue:** [kburson/aitm#36](https://github.com/kburson/aitm/issues/36) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C27 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c27-attempts-jit-coverage-and-estimates), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C16 / #21](../21/story.md), [C23 / #28](../28/story.md), [C26 / #35](../35/story.md).

**Blocking:** [C28 / #37](../37/story.md), [C31 / #40](../40/story.md), [C44 / #51](../51/story.md), [C61 / #57](../57/story.md), [C70 / #59](../59/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C16, C23, C26 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/attempts.py; src/aitm_core/jit.py; src/aitm_core/estimates.py; src/aitm_core/cli/plan.py; packages/aitm-core/tests/unit/test_c27.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `record_jit(request: JitRequest) -> OperationResult; assess_jit(plan, attempt, baseline, changes) -> JitResult; reconcile_attempt(attempt, plan, binding) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_jit_scope: unchanged or proven unrelated descendant baseline passes; touched dependencies, incomplete coverage, non-descendant, old plan/generation/attempt require fresh JIT. Refine/Plan/JIT estimates retain original source and priority; epic size not limited to four hours. Define provisional attempt evidence attachment operation reconcile_attempt(attempt, plan, binding): same attempt/clock/allowance is retained; only actual scope/trip replan creates new generation. CLI attempt reconcile persists those facts. JIT supports research/deliverable input baseline as well as source code. The pre-C31 in-process MemoryBackend CLI reconcile proof injects the declared typed preflight fixture; attempt reconcile is category normal and requires preflight. No subprocess/Git is introduced into this unit lane. C70 repeats its positive and refusal behavior with the actual installed preflight after C64 supplies shared fixtures.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c27.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Accepted parent plan is not automatic leaf acceptance; initial provisional advisory attempt never resets budget when evidence arrives.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Accepted parent plan is not automatic leaf acceptance; initial provisional advisory attempt never resets budget when evidence arrives.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:58Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
