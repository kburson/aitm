---
schema: "aitm.story/v0"
id: 57
title: "[Core C61] Scoped evidence-only recovery and real rerun"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/57"
parent: 2
children: []
blocking: [61, 65, 67]
blocked-by: [21, 36, 41, 42, 45, 49, 52]
created: "2026-11-09T08:03:28Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c61-scoped-evidence-only-recovery-and-real-rerun"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C61", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "6b4a7422e590ec719fd12a84a7cbc34af79e4e9f224ef064f708594ae6602875"}
---

# [Core C61] Scoped evidence-only recovery and real rerun

**GitHub issue:** [kburson/aitm#57](https://github.com/kburson/aitm/issues/57) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C61 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c61-scoped-evidence-only-recovery-and-real-rerun), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C16 / #21](../21/story.md), [C27 / #36](../36/story.md), [C32 / #41](../41/story.md), [C35 / #42](../42/story.md), [C38 / #45](../45/story.md), [C42 / #49](../49/story.md), [C45 / #52](../52/story.md).

**Blocking:** [C65 / #61](../61/story.md), [C49 / #65](../65/story.md), [C68 / #67](../67/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C16, C27, C32, C35, C38, C42, C45 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C45. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/recovery.py; src/aitm_core/cli/evidence.py; src/aitm_core/cli/bind.py; packages/aitm-core/tests/integration/test_c61.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reopen_evidence(story, source) -> RecoveryAuthority; recover_missing_proof(authority) -> RecoveryResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_evidence_only_rerun: real reopen --for evidence from unchanged Done/unverified retains old disposition/waivers/signoff, used budget and allowance. bind --evidence grants new generation via C16, then real admission/test yields later eligible interval and activation before new signoff. Old, tripped, pivoted or superseded generation refuses. Evidence-only binding cannot edit source, expand or mutate target; reconstruction of existing valid receipt leaves stopped clock unchanged. Shared mode obeys published admission/stop order.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c61.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No source change is hidden inside evidence recovery. Normal same-attempt rework fences recovery generation; true replan creates fresh attempt only under accepted policy.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No source change is hidden inside evidence recovery. Normal same-attempt rework fences recovery generation; true replan creates fresh attempt only under accepted policy.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:28Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
