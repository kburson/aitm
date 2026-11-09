---
schema: "aitm.story/v0"
id: 15
title: "[Core C14] Constrained extension writes and retained unknown data"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/15"
parent: 2
children: []
blocking: [17, 22, 35, 40, 64]
blocked-by: [9, 14, 13]
created: "2026-11-09T08:00:28Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c14-constrained-extension-writes-and-retained-unknown-data"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C14", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "f2f1bd77e7d06cf35776b2c6ca101d7c155b54c1c89562c417906382e4a26fba"}
---

# [Core C14] Constrained extension writes and retained unknown data

**GitHub issue:** [kburson/aitm#15](https://github.com/kburson/aitm/issues/15) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C14 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c14-constrained-extension-writes-and-retained-unknown-data), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C04 / #9](../9/story.md), [C13 / #14](../14/story.md), [C08 / #13](../13/story.md).

**Blocking:** [C09 / #17](../17/story.md), [C17 / #22](../22/story.md), [C26 / #35](../35/story.md), [C31 / #40](../40/story.md), [C63 / #64](../64/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C04, C13, C08 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C08. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/ext/ownership.py; src/aitm_core/ext/adapters.py; src/aitm_core/services.py; src/aitm_core/store/backend.py; packages/aitm-core/tests/unit/test_c14.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `authorize_write(owner: OwnerRef, change: Change) -> AuthorizedChange; resolve_adapter(owner, version) -> AdapterResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_ownership: real glob overlap with core/other owners, path-type changes, symlink escape and namespace mismatch fail at transaction boundary. Disabled/older records retain exact bytes; missing action/guard owner stays unavailable, not complete. Install WriteAuthorizer in the production transaction ingress and drive an extension write through the real operation API, proving reserved-path refusal before any tree/ref mutation. In test_c14.py prove production transaction ingress resolves the real WriteAuthorizer, while C04 explicitly unregistered-slot negative cases remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c14.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Trusted in-process extensions are not a hostile-code sandbox; preserve original action versions during replay.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Trusted in-process extensions are not a hostile-code sandbox; preserve original action versions during replay.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:28Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
