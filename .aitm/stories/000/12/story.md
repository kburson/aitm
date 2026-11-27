---
schema: "aitm.story/v0"
id: 12
title: "[Core C07] Committed configuration and routing anchors"
kind: "story"
state: test
issue: "https://github.com/kburson/aitm/issues/12"
parent: 472
children: []
blocking: [13, 14, 19, 21, 30, 54, 75, 77, 498]
blocked-by: [5, 11, 497]
created: "2026-11-09T08:00:15Z"
updated: "2026-11-27T13:31:24.407Z"
last-branch: "codex/core-12-committed-policy"
last-worktree: "/Users/kpburson/.codex/worktrees/aitm-core-470/trunk"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c07-committed-configuration-and-routing-anchors"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C07", "parent": 472}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":472,"design_sources":[2],"scope_entry":"C07","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C07] Committed configuration and routing anchors

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#472](https://github.com/kburson/aitm/issues/472). Key: C07. Estimate: **3.5 h**. Blocked by: #5, #11, #497.

Resolve the configured workflow from the same anchored default commit as policy; delegate parsing to C90 and cutover to C98. Verify story-worktree substitution cannot change authority.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#12](https://github.com/kburson/aitm/issues/12) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C07 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c07-committed-configuration-and-routing-anchors), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C03 / #5](../5/story.md), [C06 / #11](../11/story.md).

**Blocking:** [C08 / #13](../13/story.md), [C13 / #14](../14/story.md), [C11 / #19](../19/story.md), [C16 / #21](../21/story.md), [C33 / #30](../30/story.md), [C72 / #75](../75/story.md), [C73 / #77](../77/story.md), [C47 / #54](../54/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C03, C06 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/config.py; src/aitm_core/models/config.py; src/aitm_core/store/installation.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c07.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `resolve_policy(anchor: Installation, refresh: RefreshResult) -> PolicySnapshot; classify_change(old, new) -> PolicyChange`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_policy_authority: story-edited limits/mode/commands are ignored; anchored code/default/store/issuer changes require reconfigure; tip-effective fields apply on next pinned policy evaluation. No remote/local ambiguity or unsupported policy silently defaults. StoreAnchor/RefreshResult structural types come from C01; wire services.policy from committed config. RefreshResult is an input port, not a future dependency on C08 implementation. Validate review.documents.design_coverage=own-document and the separate review.source schema/independence/assurance fields. Missing or unsupported inherited coverage stays unavailable; labeled fixture values are not product defaults. A delivered issuer/anchor change fences both modes; tip-effective githost configuration cannot redirect the anchored store.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c07.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure resolution consumes fetched facts; C08 owns network refresh and stale/unknown freshness.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Pure resolution consumes fetched facts; C08 owns network refresh and stale/unknown freshness.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:15Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `8883c9016590560fb001fc98412ed06776b428c10bd63d1c311044901ce0ee72`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C07",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "8a343aa194a10d8c251b0c378da1df31f7b1b8e6b1c845853383dfec9db4a58e"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #472 with scope entry **C07**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
