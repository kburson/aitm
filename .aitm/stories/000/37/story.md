---
schema: "aitm.story/v0"
id: 37
title: "[Core C28] State transitions and atomic guard outcomes"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/37"
parent: 2
children: []
blocking: [76, 38, 39, 40, 50, 59, 79, 81, 82]
blocked-by: [16, 26, 35, 36, 22, 27, 17, 75]
created: "2026-11-09T08:02:02Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c28-state-transitions-and-atomic-guard-outcomes"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C28", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "68c6f2e4ba76f2e12ef3369efa0e36d87678979ceed511a4e3aa9347279ad31f"}
---

# [Core C28] State transitions and atomic guard outcomes

**GitHub issue:** [kburson/aitm#37](https://github.com/kburson/aitm/issues/37) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C28 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c28-state-transitions-and-atomic-guard-outcomes), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C15 / #16](../16/story.md), [C22 / #26](../26/story.md), [C26 / #35](../35/story.md), [C27 / #36](../36/story.md), [C17 / #22](../22/story.md), [C21 / #27](../27/story.md), [C09 / #17](../17/story.md), [C72 / #75](../75/story.md).

**Blocking:** [C71 / #76](../76/story.md), [C29 / #38](../38/story.md), [C30 / #39](../39/story.md), [C31 / #40](../40/story.md), [C43 / #50](../50/story.md), [C70 / #59](../59/story.md), [C76 / #79](../79/story.md), [C78 / #81](../81/story.md), [C75 / #82](../82/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C15, C22, C26, C27, C17, C21, C09, C72 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C21, C09. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/cli/dispatch.py; src/aitm_core/machine/states.py; src/aitm_core/machine/transitions.py; src/aitm_core/machine/guards.py; src/aitm_core/cli/lifecycle.py; packages/aitm-core/tests/integration/test_c28.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `transition(request: TransitionRequest) -> OperationResult; explain(snapshot, story) -> TransitionExplanation`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_transition_matrix: eight-state edges and entry/exit slots evaluated core then stable extensions on one pinned read-set. Enforce refusal records no transition; advisory advances with failed guards; illegal edge/integrity never waived. CAS race re-evaluates all related predicates. Real advisory promote to Develop with absent plan and implementation-unbound creates one provisional attempt/clock and failed guards. Later accepted plan, bind --implementation and attempt reconcile preserve attempt ID, cumulative coverage and consumed allowance. Own the normal state-command pipeline: C04 typed preflight first (declared fixture until C31 installs the real implementation), then C17 sync of eligible bound authored inputs as a separate saved/reported operation, then pin a fresh planning/policy/read-set before transition evaluation. Authored-sync has its own operation category so it does not recursively request pre-sync. A sync conflict retains both versions and prevents the normal transition; successful sync is not rolled back by a later guard refusal. Run these real CLI/Git/binding/sync cases in integration, with the preflight fixture explicitly supplied to the test service composition. Separately assert an attempt-bearing command returns preflight-unavailable with that slot deliberately unregistered in an explicit test service composition; no permissive fallback is enabled. The transition matrix itself may use MemoryBackend within this integration suite. C31 proves one representative real promote/qualifying-stop pipeline; C70 separately qualifies provisional-attempt/reconcile behavior with actual production preflight. The complete early-state matrix
  covers Backlog description/own-design acceptance, Refine estimate/size/priority and Ready dependency satisfaction for all kinds. Four-hour leaf-size applies to story/defect/spike; an epic may have a larger aggregate estimate. Plan-entry provenance/readiness uses the C72 port, not parent-plan acceptance as a leaf design pass. Its pre-C75 producer tests explicitly inject that typed implementation; C75 proves actual production registration and unavailable behavior without rewriting those fixtures. Declare the typed KindRequirements and StoryExitGuards ports used by the transition evaluator. C29 installs kind selection/substitutions; C76 installs story/defect Develop-exit source evaluation and C79 installs Test/Review composites in the same edge-dispatched StoryExitGuards port. Unknown/missing required evaluation cannot become pass; enforce refuses, advisory records unknown, and integrity rules remain mandatory. Earlier fixture-composed producer tests explicitly inject these typed ports; no default permissive implementation. C28 explain returns a TransitionExplanation over that same pinned evaluator; C78 owns its installed read-command wiring.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c28.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Resident action identities are persisted in transaction; action execution belongs to C43, never an unrecorded callback.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Resident action identities are persisted in transaction; action execution belongs to C43, never an unrecorded callback.

Use the declared typed preflight fixture until C31 supplies the production implementation; production attempt-bearing mutations remain unavailable meanwhile. C31 proves the representative real pipeline; C70 qualifies reconcile/provisional/expansion consumers with actual preflight and C64 fixtures.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:02Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `68c6f2e4ba76f2e12ef3369efa0e36d87678979ceed511a4e3aa9347279ad31f`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C28",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "1b0a5b1f08e1ec4395be15dd6b57d9a348665ae2599c43051f446eb9d0c47216"
}
```
