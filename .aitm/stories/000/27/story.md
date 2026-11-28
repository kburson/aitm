---
schema: "aitm.story/v0"
id: 27
title: "[Core C21] Shared local number allocation"
kind: "story"
state: develop
issue: "https://github.com/kburson/aitm/issues/27"
parent: 476
children: []
blocking: [37, 39, 58, 65, 82, 478, 479, 480, 483, 484, 485, 487]
blocked-by: [22, 26, 74]
created: "2026-11-09T08:01:19Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c21-shared-local-number-allocation"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C21", "parent": 476}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":476,"design_sources":[2],"scope_entry":"C21","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C21] Shared local number allocation

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#476](https://github.com/kburson/aitm/issues/476). Key: C21. Estimate: **4 h**. Blocked by: #22, #26, #74.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

Integration owner. Trunk admission requires verified deliveries: #24, #74, #25, #26.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#27](https://github.com/kburson/aitm/issues/27) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C21 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c21-shared-local-number-allocation), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C22 / #26](../26/story.md), [C17 / #22](../22/story.md), [C74 / #74](../74/story.md).

**Blocking:** [C28 / #37](../37/story.md), [C30 / #39](../39/story.md), [C64 / #58](../58/story.md), [C49 / #65](../65/story.md), [C75 / #82](../82/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C22, C17, C74 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C74, C22. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/providers/local.py; src/aitm_core/services.py; src/aitm_core/cli/stories.py; packages/aitm-core/tests/integration/test_c21.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `graduate_local(intent: GraduationIntent, finalization: FinalizationIntent) -> GraduationResult; project_latest(publication, key) -> ActionResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_allocator_two_clones: real graduate invokes C22 build_graduation inside one candidate operation; inject failure after number proposal/before construction and assert no permanent ID, moved draft, usable numbered story or partial relationship/action exists. Local CAS atomically commits all surfaces; shared mode exposes ID only after verified publication. Two drafts race for one number, loser rebuilds complete transaction under same semantic intent; lost ACK observes result. Same draft exposes one ID; offline candidates stay unissued. Pass FinalizationIntent to C22 construction after choosing each candidate. Every losing-number retry re-runs materialize_finalization with the newly chosen child ID and fresh snapshot; never reuse a RelatedWriteSet containing the old candidate. No caller may expose a proposed number before the complete operation is authoritative.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c21.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C21 implements the C13 LocalGraduationAuthority.graduate(intent, finalization) method by delegating to graduate_local, and wires it into the existing graduate adapter. Allocation is internal candidate construction, never a separately exposed durable local ID; externally issued pending identities retain their distinct C20/C22 semantics.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: C21 implements the C13 LocalGraduationAuthority.graduate(intent, finalization) method by delegating to graduate_local, and wires it into the existing graduate adapter. Allocation is internal candidate construction, never a separately exposed durable local ID; externally issued pending identities retain their distinct C20/C22 semantics.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:19Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `24532ff332ae5b1380ca0797c05b586afed95900e5d97772b923cf1c08c780c7`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C21",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "302119a3538e086b05314396e3ab01b6736bf5295a63339516e2abc22ea10fb4"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **50** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #476 with scope entry **C21**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).

[Scoped manual JIT pickup](plan/2026-11-27-pickup.md).
