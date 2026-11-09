---
schema: "aitm.story/v0"
id: 26
title: "[Core C22] Graduation and atomic relationships"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/26"
parent: 2
children: []
blocking: [27, 37, 39, 63, 65]
blocked-by: [16, 25]
created: "2026-11-09T08:01:14Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c22-graduation-and-atomic-relationships"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C22", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "6c4e34f9f32455cc17838a4046880a59d110f850c3b3e398cceee4b13221ce9e"}
---

# [Core C22] Graduation and atomic relationships

**GitHub issue:** [kburson/aitm#26](https://github.com/kburson/aitm/issues/26) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C22 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c22-graduation-and-atomic-relationships), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C15 / #16](../16/story.md), [C20 / #25](../25/story.md).

**Blocking:** [C21 / #27](../27/story.md), [C28 / #37](../37/story.md), [C30 / #39](../39/story.md), [C62 / #63](../63/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C15, C20 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/graduation.py; src/aitm_core/relationships.py; src/aitm_core/cli/stories.py; packages/aitm-core/tests/integration/test_c22.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `build_graduation(intent, draft: DraftSnapshot, candidate: CandidateIdentity, finalization: FinalizationIntent) -> Operation; finalize_external_identity(reservation, expected_draft, finalization: FinalizationIntent) -> OperationResult; link(change) -> OperationResult; materialize_finalization(intent, chosen_child, pinned_snapshot) -> RelatedWriteSet; register_finalizer(kind, version, handler) -> FinalizerRegistry`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_graduate_links: exact draft moves with original facts/attachments, numbered story initialization and parent reciprocal links commit together. Concurrent draft edit conflicts; parent/dependency/replacement cycles and self-links refuse. Resume returns same issued identity. Supply the pure construction seam (number, exact draft move, initialized story, reciprocal relations and initial projection identity) before C21 local authority. External issuance may remain retained pending finalization; the local path may not expose such a partial permanent ID. FinalizationIntent is durable typed semantic input, not pre-rendered writes or a serialized callback. Core dispatches its registered kind/version through materialize_finalization(intent, chosen_child, pinned_snapshot) -> RelatedWriteSet after choosing the candidate. Ordinary graduation yields empty related changes; C30 supplies the expansion finalizer. The external finalizer first obtains the actual reconciled issuer identity, then materializes and atomically commits the same related facts after rechecking current origin reservation; a fenced origin retains issued identity pending scope reconciliation, never attaches it automatically.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c22.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Epic parent and expanded_from remain separate; dependent needs explicit resolution for non-delivered terminal outcomes.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Epic parent and expanded_from remain separate; dependent needs explicit resolution for non-delivered terminal outcomes.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:14Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
