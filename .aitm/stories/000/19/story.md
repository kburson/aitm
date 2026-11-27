---
schema: "aitm.story/v0"
id: 19
title: "[Core C11] Crash-resumable init and reconfiguration"
kind: "story"
state: done
issue: "https://github.com/kburson/aitm/issues/19"
linked-pr: "https://github.com/kburson/aitm/pull/561"
parent: 475
children: []
blocking: [20, 54, 510]
blocked-by: [12, 17, 18]
created: "2026-11-09T08:00:45Z"
updated: "2026-11-27T21:47:07.315283+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c11-crash-resumable-init-and-reconfiguration"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-27-pickup.md", "plan/2026-11-27-pr-561-verification.md", "plan/2026-11-27-pr-561-r2-verification.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C11", "parent": 475}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":475,"design_sources":[2],"scope_entry":"C11","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C11] Crash-resumable init and reconfiguration

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#475](https://github.com/kburson/aitm/issues/475). Key: C11. Estimate: **4 h**. Blocked by: #12, #17, #18.

Resolve the configured workflow from the same anchored default commit as policy; delegate parsing to C90 and cutover to C98. Verify story-worktree substitution cannot change authority.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#19](https://github.com/kburson/aitm/issues/19) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C11 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c11-crash-resumable-init-and-reconfiguration), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C07 / #12](../12/story.md), [C09 / #17](../17/story.md), [C10 / #18](../18/story.md).

**Blocking:** [C12 / #20](../20/story.md), [C47 / #54](../54/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C07, C09, C10 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C10. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/setup/init.py; src/aitm_core/setup/journal.py; src/aitm_core/cli/setup.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c11.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `prepare_init(request: InitRequest) -> BootstrapProposal; resume_init(id) -> InitResult; reconfigure(proposal) -> AdoptionResult; InitHooks.install(context) port`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_init_resume: one UUID/genesis across interruption and rerun; prepare config without committing it; before landed anchor no remote publication/routine writes; afterward publish and protect. Fresh clone pending until original objects publish; explicit replacement proposal if irretrievable. Local-only and remote cases. The init pipeline calls its declared hook/doctor/provider steps; unavailable steps remain reported. C12 supplies and wires hook installation; readiness never silently marks an absent installer applied. Own --planning-branch <name> (default planning), the interactive accept/type prompt and validated Git-ref syntax. Refuse equality with the detected default branch. Refuse existing local or remote names unless complete history/store identity matches the trusted anchor or this same init journal; name existence alone is never reuse authority. Exercise a non-default records ref end to end through init, committed configuration, publication and ordinary mutation; no downstream code hard-codes planning. Test missing hook/doctor/provider steps in explicitly unregistered test compositions; C12 later proves production hook registration in test_c12.py without rewriting this negative vector. test_reconfigure_continuity exercises valid old/new anchor adoption, invalid/unprovable replacement refusal and an issuer/namespace switch that preserves every issued ID/provider reference. Ordinary delivered settings cannot bypass the adoption fence. Provider doubles prove the generic contract; no live GitHub claim.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c11.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Do not mutate global settings or overwrite foreign config; production adoption is not performed by this leaf.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Do not mutate global settings or overwrite foreign config; production adoption is not performed by this leaf.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:45Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `c7657057cf43e6d10b7eaff90a6a8ace780770dc7fa63a0c813acf89c30b4813`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C11",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "91bf6beaca831e39148d18eb70f0ecd3b9bbcb26f695ba7262c8bff9fb783ce4"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **10** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #475 with scope entry **C11**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
