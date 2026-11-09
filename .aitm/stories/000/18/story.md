---
schema: "aitm.story/v0"
id: 18
title: "[Core C10] Forward repair from maximal valid prefix"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/18"
parent: 2
children: []
blocking: [19, 55, 58, 65]
blocked-by: [13, 17, 11]
created: "2026-11-09T08:00:40Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c10-forward-repair-from-maximal-valid-prefix"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C10", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "a6dc347ed1914866bcbd7d17da859e9ab6f0eb84798d7ddf355ab4a5c3b0ec59"}
---

# [Core C10] Forward repair from maximal valid prefix

**GitHub issue:** [kburson/aitm#18](https://github.com/kburson/aitm/issues/18) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C10 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c10-forward-repair-from-maximal-valid-prefix), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C08 / #13](../13/story.md), [C09 / #17](../17/story.md), [C06 / #11](../11/story.md).

**Blocking:** [C11 / #19](../19/story.md), [C48 / #55](../55/story.md), [C64 / #58](../58/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C08, C09, C06 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/validation.py; src/aitm_core/services.py; src/aitm_core/store/repair.py; src/aitm_core/cli/planning.py; packages/aitm-core/tests/integration/test_c10.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `plan_repair(anchor, bad_tip) -> RepairPlan; apply_repair(plan, expected_tip) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_maximal_prefix: fetch P→valid unseen V→bad B; repair extends B restoring V payload, rejects older P, retains invalid tail and unpublished recovery refs. Fresh clone reproduces prefix/proof. Shared code ancestry remains fenced. Install the ForwardRepairVerifier seam in the normal history validator: independently recompute the trusted maximal valid prefix and exact restored payload/repair receipt, allowing only that proved restoration after the retained diagnosed invalid span. Run real planning repair, then planning validate in a fresh clone; reject forged receipt, older non-maximal restoration or unprovable/code-shared ancestry. No receipt nominates its own anchor. In test_c10.py prove the production default resolves ForwardRepairVerifier and accepts independently verified repair through a normal fresh validation; C06 deliberately-missing-slot cases still run unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c10.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Repair restores valid current data only; no reset, rewrite or fabricated anchor repair.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Repair restores valid current data only; no reset, rewrite or fabricated anchor repair.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:40Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
