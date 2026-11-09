---
schema: "aitm.story/v0"
id: 68
title: "[Core C52] Entrypoint performance and unit-isolation budgets"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/68"
parent: 2
children: []
blocking: [69]
blocked-by: [23, 65, 60, 56, 61, 62, 66, 67, 59]
created: "2026-11-09T08:04:18Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c52-entrypoint-performance-and-unit-isolation-budgets"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C52", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "e0dae14d85ca05687d6297e1083ea2b03f395ab3e88ef20802acfec8e8bcaf20"}
---

# [Core C52] Entrypoint performance and unit-isolation budgets

**GitHub issue:** [kburson/aitm#68](https://github.com/kburson/aitm/issues/68) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C52 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c52-entrypoint-performance-and-unit-isolation-budgets), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C18 / #23](../23/story.md), [C49 / #65](../65/story.md), [C50 / #60](../60/story.md), [C51 / #56](../56/story.md), [C65 / #61](../61/story.md), [C66 / #62](../62/story.md), [C67 / #66](../66/story.md), [C68 / #67](../67/story.md), [C70 / #59](../59/story.md).

**Blocking:** [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C18, C49, C50, C51, C65, C66, C67, C68, C70 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/performance/test_budgets.py; docs/learn/core-performance.md.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `measure_entrypoint(fixture: BenchmarkFixture) -> BudgetReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_budgets: declared warm-cache laptop show/list/explain <150ms including interpreter; local transition <1s; measure the entire MemoryBackend unit suite <10s by launching its pytest command from this non-unit performance lane; C01 tests/unit/conftest.py traps child-suite subprocess/network access from the first unit test. Record corpus/hardware/OS/repeats and cold rebuild/remote/actions/push/total wall separately. Keep Git patch replay C24 in integration lane. The parent performance test records complete child-suite wall time including collection/startup, exit status and collection count; it lives outside tests/unit and its own process launch is permitted. CI also runs the unit directory directly under the same C01 guards. C52 never adds a subprocess test inside the unit suite. The warm explain budget covers C78's full guard-explaining installed path, including lazy guard/extension loading and interpreter startup; no freshness-only shortcut or suppressed unknown/pending information is allowed.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/performance/test_budgets.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf measures and performs only bounded lazy-import corrections. Any substantive failed budget becomes explicitly bounded replan, never subtraction of startup or hidden optimization scope.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: This leaf measures and performs only bounded lazy-import corrections. Any substantive failed budget becomes explicitly bounded replan, never subtraction of startup or hidden optimization scope.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:18Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `e0dae14d85ca05687d6297e1083ea2b03f395ab3e88ef20802acfec8e8bcaf20`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C52",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "b33a5ffdc93bf67a668dbbb8cf413c9d3b9a4c2c5f297f610db98b63a1953518"
}
```
