---
schema: "aitm.story/v0"
id: 48
title: "[Core C41] Admitted target mutation and exact-result recovery"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/48"
parent: 2
children: []
blocking: [62, 65]
blocked-by: [41, 47, 11, 46]
created: "2026-11-09T08:02:49Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c41-admitted-target-mutation-and-exact-result-recovery"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C41", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "7813ce14a39b136b17977c1f56f74d8d34d6deede4743b5003b5c2d9f7c4dd0c"}
---

# [Core C41] Admitted target mutation and exact-result recovery

**GitHub issue:** [kburson/aitm#48](https://github.com/kburson/aitm/issues/48) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C41 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c41-admitted-target-mutation-and-exact-result-recovery), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C32 / #41](../41/story.md), [C40 / #47](../47/story.md), [C06 / #11](../11/story.md), [C39 / #46](../46/story.md).

**Blocking:** [C66 / #62](../62/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C32, C40, C06, C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06, C39. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/gate.py; src/aitm_core/delivery/mutate.py; src/aitm_core/delivery/reconcile.py; src/aitm_core/cli/deliver.py; packages/aitm-core/tests/integration/test_c41.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `execute_delivery(intent: DeliveryIntent, admission) -> DeliveryResult; reconcile_delivery(intent) -> DeliveryResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_delivery_once: durable intent/admission precede expected-head CAS on non-checked-out target; checked-out target refuses. Crash after CAS recovers exact result through retained intent/history despite later target advance; invalidation/cancellation cannot authorize second mutation. Use C06 ref_gate with DELIVERY_TARGET around exact target-head CAS, inventory immediately before/after, and preserve target refs/index/unsynced bytes on detected out-of-band checkout. Fence further mutation/publication eligibility and require explicit reconciliation without reset; an already-landed result stays retained historical evidence. Real Git fixture injects external checkout across CAS as well as serializes supported operations; a pre-existing checked-out target alone is not sufficient proof.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c41.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Test authority is explicit disposable fixture authority; implementation never assumes a review pass permits real trunk delivery.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Test authority is explicit disposable fixture authority; implementation never assumes a review pass permits real trunk delivery.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:49Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
