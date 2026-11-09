---
schema: "aitm.story/v0"
id: 22
title: "[Core C17] Allowlisted sync and authored conflict resolution"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/22"
parent: 2
children: []
blocking: [27, 35, 37, 40, 50, 55, 60]
blocked-by: [17, 15, 21, 20]
created: "2026-11-09T08:00:58Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C17", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "928612fd62de40a6677080136505c2b3cb8cb5686a9b0b3fb44ad2e44786f0b3"}
---

# [Core C17] Allowlisted sync and authored conflict resolution

**GitHub issue:** [kburson/aitm#22](https://github.com/kburson/aitm/issues/22) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C17 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C14 / #15](../15/story.md), [C16 / #21](../21/story.md), [C12 / #20](../20/story.md).

**Blocking:** [C21 / #27](../27/story.md), [C26 / #35](../35/story.md), [C28 / #37](../37/story.md), [C31 / #40](../40/story.md), [C43 / #50](../50/story.md), [C48 / #55](../55/story.md), [C50 / #60](../60/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C09, C14, C16, C12 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/sync.py; src/aitm_core/cli/sync.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c17.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `sync(binding, selected: PathSelection) -> SyncResult; unbind(binding) -> UnbindResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_sync: only owned authored inputs imported; scratch/generated/event/extension mutations diagnosed; explicit deletions cannot erase history; stale base retains both bodies. Failed unbind sync remains recoverable; rebind cannot redirect an old session. Invoke PendingActionRunner after the committed sync/publication result through its C04 port; until C43 installs the runner, report pending/unavailable without claiming completion. Test absent PendingActionRunner by explicitly unregistering that slot in test composition; do not assert that the evolving production default remains absent after C43.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c17.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reservation is clone-local; cross-clone conflicts remain publication conflicts, not a claimed global lock.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Reservation is clone-local; cross-clone conflicts remain publication conflicts, not a claimed global lock.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:58Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
