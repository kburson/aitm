---
schema: "aitm.story/v0"
id: 39
title: "[Core C30] Expansion reservation and resolution"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/39"
parent: 2
children: []
blocking: [40, 59, 60, 61]
blocked-by: [25, 27, 26, 28, 37]
created: "2026-11-09T08:02:10Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c30-expansion-reservation-and-resolution"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C30", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "174c7566f6f401881b6ebc0ba56c94dedbe04f55f1e9c4408ad19c0d744fa2fe"}
---

# [Core C30] Expansion reservation and resolution

**GitHub issue:** [kburson/aitm#39](https://github.com/kburson/aitm/issues/39) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C30 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c30-expansion-reservation-and-resolution), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C20 / #25](../25/story.md), [C21 / #27](../27/story.md), [C22 / #26](../26/story.md), [C23 / #28](../28/story.md), [C28 / #37](../37/story.md).

**Blocking:** [C31 / #40](../40/story.md), [C70 / #59](../59/story.md), [C50 / #60](../60/story.md), [C65 / #61](../61/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C20, C21, C22, C23, C28 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/rules/expansion.py; src/aitm_core/cli/expand.py; packages/aitm-core/tests/integration/test_c30.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reserve_expansion(origin, intent) -> OperationResult; resolve_expansion(origin, proof) -> OperationResult; build_expansion_related(finalization, chosen_child, snapshot) -> RelatedWriteSet`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_expansion_gap: reservation atomically consumes allowance, blocks/pauses origin before identity call; delayed/lost response and finalization never expose unblocked gap. Cancellation needs non-issuance/fencing proof, child delivery/disposition resolution updates all related facts. Local expansion uses C21 graduate_local with C22 construction: after the earlier allowance/pause reservation, materialize the durable FinalizationIntent into RelatedWriteSet using the exact live origin attempt/reservation and the actual chosen child, replace reservation block with child block, and append expansion/clock facts in the same child-number/story CAS. Real expand in local-only and shared stores tests construction failure, competing clone and lost ACK: no permanent number/usable child before authority, one child per intent and no unblocked interval. External uncertain issuance remains the distinct C20 protocol. Own build_expansion_related(finalization, chosen_child, snapshot) and register the core expansion finalizer with C22. Both local candidate retries and external lost-response finalization call it after identity selection. Assert origin block, expansion events, reciprocal child facts and projection identity all name the winning child ID; no duplicate finalization or attachment to a fenced origin and no unblocked interval. These pre-C31 real expand tests explicitly inject the declared typed fixture preflight into test-only service composition. expand is category normal and always requires preflight, including second/nested requests; no stop/recovery exemption is introduced. C70 repeats the local/shared construction-failure, competing-clone and lost-ACK vectors with actual production preflight using C64 fixtures.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c30.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Second/nested request detection is C31; no child ID must not mean no reservation.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Second/nested request detection is C31; no child ID must not mean no reservation.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:10Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
