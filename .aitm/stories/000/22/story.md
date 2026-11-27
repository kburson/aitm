---
schema: "aitm.story/v0"
id: 22
title: "[Core C17] Allowlisted sync and authored conflict resolution"
kind: "story"
state: review
issue: "https://github.com/kburson/aitm/issues/22"
parent: 475
children: []
blocking: [27, 35, 37, 40, 50, 55, 60, 74, 500]
blocked-by: [15, 17, 20, 21]
created: "2026-11-09T08:00:58Z"
updated: "2026-11-27T22:59:06.223114+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-27-pickup.md", "plan/2026-11-27-pr-564-d7881169-verification.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C17", "parent": 475}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":475,"design_sources":[2],"scope_entry":"C17","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C17] Allowlisted sync and authored conflict resolution

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#475](https://github.com/kburson/aitm/issues/475). Key: C17. Estimate: **4 h**. Blocked by: #15, #17, #20, #21.

Retain the historical deliverable and proof where they remain applicable. Apply the parent, estimate, and dependencies in this section.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#22](https://github.com/kburson/aitm/issues/22) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C17 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C14 / #15](../15/story.md), [C16 / #21](../21/story.md), [C12 / #20](../20/story.md).

**Blocking:** [C74 / #74](../74/story.md), [C21 / #27](../27/story.md), [C26 / #35](../35/story.md), [C28 / #37](../37/story.md), [C31 / #40](../40/story.md), [C43 / #50](../50/story.md), [C48 / #55](../55/story.md), [C50 / #60](../60/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C09, C14, C16, C12 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/sync.py; src/aitm_core/cli/sync.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c17.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `sync(binding, selected: PathSelection) -> SyncResult; unbind(binding) -> UnbindResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_sync: only owned authored inputs imported; scratch/generated/event/extension mutations diagnosed; explicit deletions cannot erase history; stale base retains both bodies. Failed unbind sync remains recoverable; rebind cannot redirect an old session. Invoke PendingActionRunner after the committed sync/publication result through its C04 port; until C43 installs the runner, report pending/unavailable without claiming completion. Test absent PendingActionRunner by explicitly unregistering that slot in test composition; do not assert that the evolving production default remains absent after C43. Expose the entity-scoped sync/unbind adapter seam over the same binding/base checks; C74 wires the opened-entity route and proves its positive behavior. An absent entity handler is unavailable, never a loose arbitrary-directory import. test_sync_reconcile_cli runs real sync --reconcile <operation-id> on a retained publication conflict, presents both versions and submits an explicit scoped resolution through C09.reconcile. It appends a new operation with supersession lineage; the old operation stays unpublished with its local evidence intact. Lost ACK reconciles that resolving operation once. test_sync_push_cli proves --push requests the same bounded default publication path, including retryable pending, without a second hidden sync or altered evidence. C17 owns both adapters in cli/sync.py; C09 remains their already-delivered library producer.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c17.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reservation is clone-local; cross-clone conflicts remain publication conflicts, not a claimed global lock.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Reservation is clone-local; cross-clone conflicts remain publication conflicts, not a claimed global lock.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:58Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `acddad31ff6b429120b096c2756d878e67ce743a771e8792d4f3affafa615d71`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C17",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "928612fd62de40a6677080136505c2b3cb8cb5686a9b0b3fb44ad2e44786f0b3"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #475 with scope entry **C17**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
