---
schema: "aitm.story/v0"
id: 63
title: "[Core C62] Epic aggregation and scope-resolution checkpoint"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/63"
parent: 2
children: []
blocking: [64, 79, 80, 81, 65]
blocked-by: [26, 38, 45, 49, 50]
created: "2026-11-09T08:03:57Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C62", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "9d18a59713d21301ebe3547e1d2daa9a2363b1c0015b5e8f400f899c87f73563"}
---

# [Core C62] Epic aggregation and scope-resolution checkpoint

**GitHub issue:** [kburson/aitm#63](https://github.com/kburson/aitm/issues/63) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C62 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

The baseline estimate of 3 implementation agent-hours (P1/S) comes from the [accepted parent plan](../2/plan/core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C22 / #26](../26/story.md), [C29 / #38](../38/story.md), [C38 / #45](../45/story.md), [C42 / #49](../49/story.md), [C43 / #50](../50/story.md).

**Blocking:** [C63 / #64](../64/story.md), [C76 / #79](../79/story.md), [C79 / #80](../80/story.md), [C78 / #81](../81/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C22, C29, C38, C42, C43 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C29, C43. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/aggregation.py; src/aitm_core/machine/kinds.py; packages/aitm-core/tests/integration/test_c62.py; src/aitm_core/services.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `aggregate_children(snapshot, epic) -> AggregateEvidence`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_epic_aggregate: real epic transitions start with accepted plan/child set despite mixed child states; later Test/Review rechecks required verification and delivered or explicitly scope-resolved children. Changed child scope invalidates assessment; abandoned/replaced dependency needs explicit dependent resolution. No epic clock/JIT/PR/test subprocess. Register aggregate_children in C29's AggregateEvidence port from services.py. The real promote cases use this production registration, not a test-only monkeypatch, and an explicitly missing slot stays unknown/unavailable. C29 owns the kind/edge dispatch; this leaf supplies its aggregate implementation without duplicating transitions.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c62.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Use one pinned related-story snapshot and CAS read-set; scope resolution is retained evidence, not blanket acceptance of abandoned work.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Use one pinned related-story snapshot and CAS read-set; scope resolution is retained evidence, not blanket acceptance of abandoned work.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:57Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `9d18a59713d21301ebe3547e1d2daa9a2363b1c0015b5e8f400f899c87f73563`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C62",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "21a4bfc15642d00f1432f0c4337cd2aeed254751c64116c2d1bba7eeeabd2825"
}
```

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

In the aggregate required-scope evaluator, require the explicitly designated integration delivery to satisfy its upstream obligation before closing the epic. Hold when the owner is abandoned pending accepted scope replacement or revision. Reject self-targets and keep pure aggregate behavior. Managed branch, delivery and source proof are separate leaves.

The current planning estimate is **4 implementation agent-hours** (P1/S). The baseline decomposition recorded **3 h**.

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.
