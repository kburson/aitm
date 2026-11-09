---
schema: "aitm.story/v0"
id: 40
title: "[Core C31] Trip ordering, replan decisions and human pivots"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/40"
parent: 2
children: []
blocking: [41, 42, 50, 59, 79, 61, 65, 82]
blocked-by: [28, 36, 37, 39, 15, 22, 76, 74, 38]
created: "2026-11-09T08:02:14Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C31", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "fcb1317d050bb41815f1cadae215f504eb637f1cd7aff29ed22023cd0d297a71"}
---

# [Core C31] Trip ordering, replan decisions and human pivots

**GitHub issue:** [kburson/aitm#40](https://github.com/kburson/aitm/issues/40) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C31 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C23 / #28](../28/story.md), [C27 / #36](../36/story.md), [C28 / #37](../37/story.md), [C30 / #39](../39/story.md), [C14 / #15](../15/story.md), [C17 / #22](../22/story.md), [C71 / #76](../76/story.md), [C74 / #74](../74/story.md), [C29 / #38](../38/story.md).

**Blocking:** [C32 / #41](../41/story.md), [C35 / #42](../42/story.md), [C43 / #50](../50/story.md), [C70 / #59](../59/story.md), [C76 / #79](../79/story.md), [C65 / #61](../61/story.md), [C49 / #65](../65/story.md), [C75 / #82](../82/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C23, C27, C28, C30, C14, C17, C71, C74, C29 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C30, C14, C74, C29. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/store/backend.py; src/aitm_core/store/sync.py; src/aitm_core/machine/transitions.py; src/aitm_core/rules/trips.py; src/aitm_core/pivots.py; src/aitm_core/cli/trips.py; packages/aitm-core/tests/integration/test_c31.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `preflight_attempt(context) -> TripResult; decide_trip(decision) -> OperationResult; pivot(human_context, change) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_trip_precedence: confirmed overrun/second/nested expansion wins before ordinary sync/action/pass, atomically fences origin/child and demotes in enforce; advisory reports. Rework keeps budget, accepted replacement resets; continue/fold/abandon child scope stays coherent. Known agent cannot override pivot via --as-human. Wire the C04 AttemptPreflight port into CommandService before ordinary authored sync/mutation, backend decision retry before every CAS, and before effective completion. Stop/reconciliation operations use a typed non-implementation category to avoid recursive normal guards while retaining integrity. Actual sync after a proven trip preserves unsynced workspace bytes without importing them first; injected retry rechecks the new stop. In its own test_c31.py, prove the production default resolves AttemptPreflight and exercise one representative real C28 promote pipeline with a qualifying stop. Its own deterministic unit/single-store cases retain second/nested expansion and CAS-retry semantics; it does not reproduce the three predecessor suites or construct new two-clone infrastructure. C70 separately owns C27 reconcile, C28 provisional-attempt/reconcile and C30 local/shared construction-failure/competing-clone/lost-ACK re-proofs after C64. Earlier deliberately-unregistered and fixture-composed suites remain valid unchanged. The 4 h estimate covers only this bounded trip/pivot/decision implementation, three wiring points and representative pipeline proof. test_human_pivot uses a controlled genuine interactive-actor fixture, alongside known-agent/tool and --as-human refusal. Verify separate core.pivot.recorded (no fabricated trip),
  atomic affected origin/child Plan demotion, admission fences/cancellation status, coherent child disposition and fresh next accepted-plan attempt. Outcomes preserve pivot versus planning-failure attribution and the stated actor-authentication limit.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c31.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Expansion completion interpretation and second-trip cap remain open observations, not new default guards; actor heuristics are not authentication.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Expansion completion interpretation and second-trip cap remain open observations, not new default guards; actor heuristics are not authentication.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:14Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `fcb1317d050bb41815f1cadae215f504eb637f1cd7aff29ed22023cd0d297a71`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C31",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "b5a8d3aecc6416614ddd42a052ef568c564affa220416ecc38350dce9d55db35"
}
```
