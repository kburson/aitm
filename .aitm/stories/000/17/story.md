---
schema: "aitm.story/v0"
id: 17
title: "[Core C09] Publication replay and conflict recovery"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/17"
parent: 2
children: []
blocking: [18, 19, 22, 24, 25, 34, 37, 41, 50, 55, 58]
blocked-by: [9, 13, 16, 15]
created: "2026-11-09T08:00:36Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c09-publication-replay-and-conflict-recovery"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C09", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "697dbab4375d37bc7c8315f6cfaef995333220a54781ef68750e3650fa33dbe5"}
---

# [Core C09] Publication replay and conflict recovery

**GitHub issue:** [kburson/aitm#17](https://github.com/kburson/aitm/issues/17) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C09 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c09-publication-replay-and-conflict-recovery), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C04 / #9](../9/story.md), [C08 / #13](../13/story.md), [C15 / #16](../16/story.md), [C14 / #15](../15/story.md).

**Blocking:** [C10 / #18](../18/story.md), [C11 / #19](../19/story.md), [C17 / #22](../22/story.md), [C19 / #24](../24/story.md), [C20 / #25](../25/story.md), [C25 / #34](../34/story.md), [C28 / #37](../37/story.md), [C32 / #41](../41/story.md), [C43 / #50](../50/story.md), [C48 / #55](../55/story.md), [C64 / #58](../58/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C04, C08, C15, C14 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C14. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/cli/dispatch.py; src/aitm_core/store/publication.py; src/aitm_core/store/reconcile.py; packages/aitm-core/tests/integration/test_c09.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `publish(operation_id: str) -> PublicationResult; reconcile(operation_id: str, resolution: Resolution) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_publish_replay: two clones race disjoint operations, one FF push loses then safely replays whole operations with same IDs; related-story/policy/authored conflicts retain both sides. Lost ACK observes remote before retry. Local/pending/published states differ. Wire CommandService.execute so every ordinary mutating adapter attempts bounded publication after its local operation, even without --push. Real describe (C15) proves lost-ACK/pending output retains local completion; later C28/C49 prove the same path for promote. Read-only commands never invoke it.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c09.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No event union, stale positive guards or repetition of external side effects during replay.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No event union, stale positive guards or repetition of external side effects during replay.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:36Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
