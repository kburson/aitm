---
schema: "aitm.story/v0"
id: 56
title: "[Core C51] Real review/migration and second-clone qualification"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/56"
parent: 486
children: []
blocking: [66, 68, 69, 228, 487, 491]
blocked-by: [23, 55]
created: "2026-11-09T08:03:24Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C51", "parent": 486}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":486,"design_sources":[2],"scope_entry":"C51","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C51] Real review/migration and second-clone qualification

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#486](https://github.com/kburson/aitm/issues/486). Key: C51. Estimate: **4 h**. Blocked by: #23, #55.

Carry legacy state and accepted design, attempt, candidate and operation provenance into the owned migration fixture. C98 supplies the live-workflow mapping policy and refusal cases. Preserve original event identities and exact accepted bytes.

Integration owner. Trunk admission requires verified deliveries: #78, #53, #54, #55, #510.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#56](https://github.com/kburson/aitm/issues/56) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C51 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C48 / #55](../55/story.md), [C18 / #23](../23/story.md).

**Blocking:** [C67 / #66](../66/story.md), [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C48, C18 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_v0_cutover.py; tests/integration/test_review_import.py; docs/learn/core-migration.md.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `qualify_cutover(legacy_fixture, declared_policy) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cutover_fresh_clone: actual portable/native #1/#2 plus created leaf fixtures reconstruct every version; live/backfill duplicates normalize once; legacy namespace retained. Clone before/after cutover resumes same identity; compare all input/output hashes and unknown coverage; exact-content missing levels remain unaccepted. Snapshot all refs/journal/allocation files before/after dry-run and prove no mutation. Fresh validator rejects modified declaration/receipt or an undeclared extra legacy commit; exact output payload hash excludes receipt path. Rebuild index from adopted files and compare all query results to tree authority. After binding the exact declaration, run read-only preview and actual fixture apply using the same construction inputs and compare every predicted output/hash, mapped event and accepted snapshot to the actual payload (receipt excluded). Before declaration, verify unavailable output hashes are explicitly marked; neither mode allocates/ref-mutates during dry-run. test_full_corpus_inventory pins the complete current tree and representative decomposed leaves in addition to #1/#2. Every observed required shape has a collected mapping vector, including both dependency directions, historical decomposition estimate, manual provenance, legacy worktree paths and no duplicate plan-entry issuance alias. Compare full source inventory before/after migration; unsupported required shapes cannot disappear. test_migrated_kinds folds actual migrated #1/#2 as epics with header provenance, keeps all known leaf kinds and their old sources, and proves aggregate estimates do not trigger the leaf four-hour rule. Missing/unknown/contradictory kinds
  refuse cutover without mutation and no historical split event is invented. Reuse C77/C46 fixtures and C48 constructor.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_v0_cutover.py packages/aitm-core/tests/integration/test_review_import.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Fixture policy only. Historical blocked/unsubmitted attempts remain evidence, never upgraded to accepted during import.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Fixture policy only. Historical blocked/unsubmitted attempts remain evidence, never upgraded to accepted during import.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:24Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `66c148d074db63fbb86360c992cfeb36cdd6889be2d2da1df518e241b7199b05`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C51",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "88abe31c6df678c12697ba4ee90dc16ef49d87f93e294007d089d516f6e1413e"
}
```

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **60** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #486 with scope entry **C51**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
