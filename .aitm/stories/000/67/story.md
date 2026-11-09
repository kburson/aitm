---
schema: "aitm.story/v0"
id: 67
title: "[Core C68] Lifecycle reconciliation and limited-rerun qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/67"
parent: 2
children: []
blocking: [68, 69]
blocked-by: [65, 57]
created: "2026-11-09T08:04:14Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c68-lifecycle-reconciliation-and-limited-rerun-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C68", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "1913dd11e25c934ee4854d578e532e4883c5debe89d3f6dd2683c52e2987413c"}
---

# [Core C68] Lifecycle reconciliation and limited-rerun qualification

**GitHub issue:** [kburson/aitm#67](https://github.com/kburson/aitm/issues/67) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C68 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c68-lifecycle-reconciliation-and-limited-rerun-qualification), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C49 / #65](../65/story.md), [C61 / #57](../57/story.md).

**Blocking:** [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C49, C61 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_lifecycle_recovery.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_lifecycle_recovery(fixture_policy) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_authored_sync_and_late_activation: installed promote on edited bound accepted plan saves a distinct sync operation, repins and refuses stale acceptance; concurrent authored-base conflict retains both versions and no transition. An early pass remains ineffective until evidence reconcile activates once at the later observed time. test_provisional_attempt: advisory absent-plan/unbound Develop followed by accepted plan/bind/attempt reconcile retains attempt identity, clock and allowance. test_evidence_only_rerun: unchanged unverified Done gains a new limited evidence generation, old one remains fenced, real test/activation yields genuine later interval before signoff. Reuse producer and C49 fixture data; no duplicate harness.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_lifecycle_recovery.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Scope is exactly three integration scenarios over delivered C27/C28/C38/C42/C61 behavior; unavailable prerequisites remain blockers.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Scope is exactly three integration scenarios over delivered C27/C28/C38/C42/C61 behavior; unavailable prerequisites remain blockers.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:14Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `1913dd11e25c934ee4854d578e532e4883c5debe89d3f6dd2683c52e2987413c`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C68",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "1913dd11e25c934ee4854d578e532e4883c5debe89d3f6dd2683c52e2987413c"
}
```
