---
schema: "aitm.story/v0"
id: 40
title: "[Core C31] Trip ordering, replan decisions and human pivots"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/40"
parent: 2
children: []
blocking: [41, 42, 50, 59, 61, 65]
blocked-by: [28, 36, 37, 39, 15, 22]
created: "2026-11-09T08:02:14Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C31", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "b5a8d3aecc6416614ddd42a052ef568c564affa220416ecc38350dce9d55db35"}
---

# [Core C31] Trip ordering, replan decisions and human pivots

**GitHub issue:** [kburson/aitm#40](https://github.com/kburson/aitm/issues/40) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C31 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C23 / #28](../28/story.md), [C27 / #36](../36/story.md), [C28 / #37](../37/story.md), [C30 / #39](../39/story.md), [C14 / #15](../15/story.md), [C17 / #22](../22/story.md).

**Blocking:** [C32 / #41](../41/story.md), [C35 / #42](../42/story.md), [C43 / #50](../50/story.md), [C70 / #59](../59/story.md), [C65 / #61](../61/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C23, C27, C28, C30, C14, C17 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C14, C17. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/store/backend.py; src/aitm_core/store/sync.py; src/aitm_core/machine/transitions.py; src/aitm_core/rules/trips.py; src/aitm_core/pivots.py; src/aitm_core/cli/trips.py; packages/aitm-core/tests/integration/test_c31.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `preflight_attempt(context) -> TripResult; decide_trip(decision) -> OperationResult; pivot(human_context, change) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_trip_precedence: confirmed overrun/second/nested expansion wins before ordinary sync/action/pass, atomically fences origin/child and demotes in enforce; advisory reports. Rework keeps budget, accepted replacement resets; continue/fold/abandon child scope stays coherent. Known agent cannot override pivot via --as-human. Wire the C04 AttemptPreflight port into CommandService before ordinary authored sync/mutation, backend decision retry before every CAS, and before effective completion. Stop/reconciliation operations use a typed non-implementation category to avoid recursive normal guards while retaining integrity. Actual sync after a proven trip preserves unsynced workspace bytes without importing them first; injected retry rechecks the new stop. In its own test_c31.py, prove the production default resolves AttemptPreflight and exercise one representative real C28 promote pipeline with a qualifying stop. Its own deterministic unit/single-store cases retain second/nested expansion and CAS-retry semantics; it does not reproduce the three predecessor suites or construct new two-clone infrastructure. C70 separately owns C27 reconcile, C28 provisional-attempt/reconcile and C30 local/shared construction-failure/competing-clone/lost-ACK re-proofs after C64. Earlier deliberately-unregistered and fixture-composed suites remain valid unchanged. The 3.5 h estimate covers only this bounded trip/pivot/decision implementation, three wiring points and representative pipeline proof.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c31.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Expansion completion interpretation and second-trip cap remain open observations, not new default guards; actor heuristics are not authentication.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Expansion completion interpretation and second-trip cap remain open observations, not new default guards; actor heuristics are not authentication.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:14Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
