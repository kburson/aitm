---
schema: "aitm.story/v0"
id: 21
title: "[Core C16] Authoring and implementation bindings"
kind: "story"
state: review
issue: "https://github.com/kburson/aitm/issues/21"
parent: 475
children: []
blocking: [22, 30, 36, 41, 52, 57, 74, 77, 234]
blocked-by: [11, 12, 16]
created: "2026-11-09T08:00:54Z"
updated: "2026-11-27T22:33:18.233951+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c16-authoring-and-implementation-bindings"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-27-pickup.md", "plan/2026-11-27-pr-563-8be7f05e-verification.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C16", "parent": 475}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":475,"design_sources":[2],"scope_entry":"C16","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C16] Authoring and implementation bindings

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#475](https://github.com/kburson/aitm/issues/475). Key: C16. Estimate: **4 h**. Blocked by: #11, #12, #16.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#21](https://github.com/kburson/aitm/issues/21) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C16 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c16-authoring-and-implementation-bindings), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C06 / #11](../11/story.md), [C07 / #12](../12/story.md), [C15 / #16](../16/story.md).

**Blocking:** [C17 / #22](../22/story.md), [C74 / #74](../74/story.md), [C33 / #30](../30/story.md), [C27 / #36](../36/story.md), [C32 / #41](../41/story.md), [C73 / #77](../77/story.md), [C45 / #52](../52/story.md), [C61 / #57](../57/story.md), [C81 / #234](../../002/234/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C06, C07, C15 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/store/workspace.py; src/aitm_core/models/binding.py; src/aitm_core/cli/bind.py; packages/aitm-core/tests/integration/test_c16.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `bind(request: BindRequest) -> Binding; recover_binding(id, expected_generation) -> Binding; bind_purpose(purpose: BindingPurpose, authority: AuthorityRef) -> Binding`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_binding_generation: competing bind refuses, recovery exports unsynced bytes then fences old holder; planning binding cannot select default branch for implementation. Explicit existing branch, scrap new branch/refactor retained branch and stale receipt generation cases. Implement planning/implementation/deliverable/evidence purposes from C55. Evidence purpose requires an existing validated RecoveryAuthority and rejects implementation/expand/target-mutation capabilities; absent authority refuses. Later C61 produces that authority, not a new bypass flag. The Binding model distinguishes StoryRef from stable EntityRef and permits an entity-authored path allowlist without allocating a story number. Entity open/save/finalization integration is C74; purpose and generation checks remain the same core primitive, not a separate lock implementation.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c16.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Never create/remove/reset registered worktrees; use branch selection with explicit pinned baseline and allowed paths.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Never create/remove/reset registered worktrees; use branch selection with explicit pinned baseline and allowed paths.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:54Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `43d374033e1889fd4d602422dc63f58bb487230e363fd38ade5afa0ffaf43a03`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C16",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "ba43c7279c929657ff07d7af4efb9151ef82c135073d406fd6f58e03115aa1c5"
}
```

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

Keep authoring and session binding generation behavior. C81 separately owns a stable managed incarnation that survives an ordinary C16 rebind. C83 owns the hosted pickup prerequisite.

The current planning estimate is **4 implementation agent-hours** (P1/S). The baseline decomposition recorded **4 h**.

New dependent leaves [C81 / #234](../../002/234/story.md).

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **30** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #475 with scope entry **C16**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
