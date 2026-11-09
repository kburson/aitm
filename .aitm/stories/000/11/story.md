---
schema: "aitm.story/v0"
id: 11
title: "[Core C06] Planning history validation and worktree exclusion"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/11"
parent: 2
children: []
blocking: [12, 13, 18, 20, 21, 48, 53]
blocked-by: [10, 3]
created: "2026-11-09T08:00:10Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c06-planning-history-validation-and-worktree-exclusion"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C06", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "4bfafedd20eac429a96dd71d271818338756e2a0e9ae67e5651b0f27d671502e"}
---

# [Core C06] Planning history validation and worktree exclusion

**GitHub issue:** [kburson/aitm#11](https://github.com/kburson/aitm/issues/11) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C06 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c06-planning-history-validation-and-worktree-exclusion), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C05 / #10](../10/story.md), [C01 / #3](../3/story.md).

**Blocking:** [C07 / #12](../12/story.md), [C08 / #13](../13/story.md), [C10 / #18](../18/story.md), [C12 / #20](../20/story.md), [C16 / #21](../21/story.md), [C41 / #48](../48/story.md), [C46 / #53](../53/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C05, C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C01. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/validation.py; src/aitm_core/store/gate.py; src/aitm_core/services.py; src/aitm_core/cli/planning.py; packages/aitm-core/tests/integration/test_c06.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `validate_history(anchor: StoreAnchor, tip: str) -> ValidationReport; ref_gate(repo, target_ref: RefIdentity, purpose: RefMutationKind) -> ContextManager[Gate]; ForwardRepairVerifier(anchor, diagnosed_history, candidate) -> ValidationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_store_gate: empty-root/single-parent/data-path constraints; reject symlink/submodule/traversal/code/outside-path and code ancestry. Distinct review refs permitted. Serialize supported operations; inject external checkout between pre/post checks, retain both refs/index/unsynced bytes and fence publication. Wire ValidationGate into services.backend and planning validate; real planning validate and a normal GitBackend transaction must reject outside-path writes. No caller can omit the gate. Declare ForwardRepairVerifier as a mandatory typed validation seam for diagnosed repaired history; until C10 is installed, such history stays fenced. ref_gate(repo, target_ref, purpose) shares one clone lock but checks the exact target: planning validation is distinct from delivery content validation. Test missing ForwardRepairVerifier using an explicitly unregistered test composition; the negative case remains after C10 installation. Production registration proof belongs to C10 test_c10.py.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c06.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** The cooperative gate cannot prevent arbitrary transient external Git operations; diagnostics must state that limit.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: The cooperative gate cannot prevent arbitrary transient external Git operations; diagnostics must state that limit.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:10Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
