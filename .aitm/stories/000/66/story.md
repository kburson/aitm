---
schema: "aitm.story/v0"
id: 66
title: "[Core C67] Complete installed CLI surface audit"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/66"
parent: 487
children: []
blocking: [68, 69, 240, 488, 490, 491]
blocked-by: [51, 56, 64, 65, 74, 76, 79, 80, 81, 82]
created: "2026-11-09T08:04:10Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c67-complete-installed-cli-surface-audit"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C67", "parent": 487}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":487,"design_sources":[2],"scope_entry":"C67","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C67] Complete installed CLI surface audit

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#487](https://github.com/kburson/aitm/issues/487). Key: C67. Estimate: **3 h**. Blocked by: #51, #56, #64, #65, #74, #76, #79, #80, #81, #82.

Explain current directive, proof, blocked or unavailable reason and eligible operation without a write. Exercise default, parkingless and Housekeeping local profiles, including a restarted authored closeout. Keep the base CLI audit independent of later real hosted mounting.

Integration owner. Trunk admission requires verified deliveries: #51, #52, #57, #65, #67.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#66](https://github.com/kburson/aitm/issues/66) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C67 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c67-complete-installed-cli-surface-audit), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C49 / #65](../65/story.md), [C51 / #56](../56/story.md), [C63 / #64](../64/story.md), [C44 / #51](../51/story.md), [C71 / #76](../76/story.md), [C74 / #74](../74/story.md), [C75 / #82](../82/story.md), [C76 / #79](../79/story.md), [C78 / #81](../81/story.md), [C79 / #80](../80/story.md).

**Blocking:** [C52 / #68](../68/story.md), [C59 / #69](../69/story.md), [C87 / #240](../../002/240/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C49, C51, C63, C44, C71, C74, C75, C76, C78, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_cli_surface.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `audit_cli_surface(required_routes) -> RouteCoverageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cli_surface parametrizes every route and option in the complete CLI map: installed lazy registration, help, argument validation and versioned JSON/unavailable statuses. Assert init --planning-branch and all documented global/route options are exposed; no new unmapped command is shipped. Collect a route-to-positive-operational-test ledger from C49/C50/C51/C65/C66/C68/C59 instead of claiming help alone proves behavior. Future suite names are declared references; Gate C/D validates their actual collection once all owners are delivered. The positive operational ledger additionally includes C71 split, C74 entity editing and C75 decompose/provenance reconciliation; help/argument coverage alone is insufficient. The positive ledger also collects C17::test_sync_reconcile_cli/test_sync_push_cli, C29::test_kind_registration, C30::test_expansion_finalizer_registration, C62::test_epic_aggregate, C76's source and C79's Test/Review exit vectors and C78::test_installed_explain. An unavailable or parse-only route cannot satisfy this ledger.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_cli_surface.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** A missing command/wiring returns to its owning leaf; this audit cannot implement absent product behavior.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: A missing command/wiring returns to its owning leaf; this audit cannot implement absent product behavior.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:10Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `f218b6d432fee065f46b34ba7441c8cfd416d352d9a7a8e8ed9f158e2f816097`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C67",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "2b3e83bb81e6ffa5a8d44ad26364deb12ee229d838ef3b6012795d557d71d341"
}
```

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

This leaf supplies a prerequisite interface to the managed lifecycle amendment.

New dependent leaves [C87 / #240](../../002/240/story.md).

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **60** · **P1/S** · **3 agent-hours**. Design accepted for this manual workflow through issue #487 with scope entry **C67**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
