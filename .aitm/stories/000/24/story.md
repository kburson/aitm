---
schema: "aitm.story/v0"
id: 24
title: "[Core C19] Ideas, drafts and atomic discard"
kind: "story"
state: done
issue: "https://github.com/kburson/aitm/issues/24"
parent: 476
children: []
blocking: [25, 65, 74]
blocked-by: [16, 17]
created: "2026-11-09T08:01:06Z"
updated: "2026-11-28T00:39:52.405+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c19-ideas-drafts-and-atomic-discard"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-27-pickup.md", "plan/2026-11-27-pr-568-verification.md", "plan/2026-11-27-pr-568-verifier.json"], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C19", "parent": 476}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":476,"design_sources":[2],"scope_entry":"C19","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C19] Ideas, drafts and atomic discard

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#476](https://github.com/kburson/aitm/issues/476). Key: C19. Estimate: **2.5 h**. Blocked by: #16, #17.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#24](https://github.com/kburson/aitm/issues/24) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C19 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c19-ideas-drafts-and-atomic-discard), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C15 / #16](../16/story.md).

**Blocking:** [C74 / #74](../74/story.md), [C20 / #25](../25/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C09, C15 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/paths.py; src/aitm_core/drafts.py; src/aitm_core/cli/drafts.py; packages/aitm-core/tests/integration/test_c19.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `create_idea(input) -> EntityRef; create_draft(input) -> EntityRef; discard_draft(handle, reason) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_draft_identity: timestamp/slug collision gets checked suffix, stable IDs disambiguate handles, ambiguous bare slug lists candidates. Discard atomically removes live folder and adds per-draft tombstone with retained attachment/tree hashes. Discard retry uses stable entity/operation identity, colliding tombstone names receive a checked suffix, and graduated entities cannot be discarded. C74 adds open-entity binding/finalization checks on these same operations.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c19.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No shared append file, silent scratch import or deletion of graduated/retained history.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: No shared append file, silent scratch import or deletion of graduated/retained history.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:06Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `0d93c88041437f96c473441e8e7e2b830095940479d4812a70b2cbc487597e55`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C19",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "904013a954ddba91ba0dd345dfa1f90de078185e7792562b63a9be4d78cc847e"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **10** · **P1/S** · **2.5 agent-hours**. Design accepted for this manual workflow through issue #476 with scope entry **C19**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).

## Scoped JIT pickup

[Manual bootstrap pickup](plan/2026-11-27-pickup.md) under the owner’s #476 delivery assignment. Develop is a manual projection. No runtime transition or implementation clock was started.

## Source candidate

[Draft #568](https://github.com/kburson/aitm/pull/568) targets the #476 integration branch. Both hosted workflows are required before readiness.

[Exact hosted verification](plan/2026-11-27-pr-568-verification.md) passed and #568 was marked ready for independent SAR.

#568 returned to draft for three intake corrections. The revised source is back in hosted Test.

The revised #568 passed both exact hosted workflows and trusted verification before returning to independent review.

#568 returned to draft after independent round 2. The revised replay and collision recovery are in hosted Test.

The replay and collision fixes passed hosted qualification. #568 returned to independent review on the new exact tree.

## Verified delivery

Native [Linked PR #568](https://github.com/kburson/aitm/pull/568). [Independent exact SAR PASS](plan/2026-11-27-pr-568-source-sar.md) · [Delivery sign-off, receipts and Agent Cost](retro/2026-11-27-delivery.md).
