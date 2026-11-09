---
schema: "aitm.story/v0"
id: 50
title: "[Core C43] Durable resident-action queue and replay"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/50"
parent: 2
children: []
blocking: [58, 64, 65]
blocked-by: [17, 14, 22, 37, 42, 40]
created: "2026-11-09T08:02:58Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c43-durable-resident-action-queue-and-replay"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C43", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "fa5a19732396fde50308e0331d8cc60e72f204d3d7efe4886824939db2b0cbd2"}
---

# [Core C43] Durable resident-action queue and replay

**GitHub issue:** [kburson/aitm#50](https://github.com/kburson/aitm/issues/50) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C43 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c43-durable-resident-action-queue-and-replay), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C13 / #14](../14/story.md), [C17 / #22](../22/story.md), [C28 / #37](../37/story.md), [C35 / #42](../42/story.md), [C31 / #40](../40/story.md).

**Blocking:** [C64 / #58](../58/story.md), [C63 / #64](../64/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C09, C13, C17, C28, C35, C31 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C35, C31. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/actions.py; src/aitm_core/cli/actions.py; src/aitm_core/services.py; src/aitm_core/store/sync.py; src/aitm_core/cli/sync.py; packages/aitm-core/tests/integration/test_c43.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `run_pending(snapshot, registry) -> ActionBatchResult; retry_action(key: ActionKey) -> ActionResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_action_recovery: crash before first call leaves pending record; missing/disabled version stays unavailable. Shared action runs only after publication and uses latest state; stale retry/lost ACK and provider monotonic-or-fenced contract tested with doubles. Local no-op projection records completion. Install the PendingActionRunner port. Real aitm sync discovers/retries a durable action after crash before first call, and actions retry uses the identical owner/version/key route; no helper-only qualification. In test_c43.py prove production sync/actions resolve PendingActionRunner; C17 deliberately-unregistered-slot negative vectors remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c43.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** M2 owns actual hosted endpoint proof; core must not claim fake-provider tests demonstrate GitHub safety.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: M2 owns actual hosted endpoint proof; core must not claim fake-provider tests demonstrate GitHub safety.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:58Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
