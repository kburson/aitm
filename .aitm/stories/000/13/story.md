---
schema: "aitm.story/v0"
id: 13
title: "[Core C08] Candidate fetch and shared-history continuity"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/13"
parent: 2
children: []
blocking: [15, 17, 18, 23]
blocked-by: [11, 12]
created: "2026-11-09T08:00:19Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c08-candidate-fetch-and-shared-history-continuity"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C08", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "8162080179b323d7d23d4c5656a3e2622bdb5d51e314e593030d5bba78182d07"}
---

# [Core C08] Candidate fetch and shared-history continuity

**GitHub issue:** [kburson/aitm#13](https://github.com/kburson/aitm/issues/13) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C08 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c08-candidate-fetch-and-shared-history-continuity), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C06 / #11](../11/story.md), [C07 / #12](../12/story.md).

**Blocking:** [C14 / #15](../15/story.md), [C09 / #17](../17/story.md), [C10 / #18](../18/story.md), [C18 / #23](../23/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C06, C07 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C07. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/continuity.py; src/aitm_core/store/fetch.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c08.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `observe_shared(anchor, observation: RefObservation) -> SharedFrontier; refresh_refs(policy) -> RefreshResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_shared_frontier: rollback, deletion and valid sibling fence; valid unpublished divergence remains reconcilable; invalid descendant remains quarantined continuity checkpoint. Crash journal/ref updates, corrupt journal, first-clone rollback limitation and separate remote topology are visible. Wire services.refresh and the policy preflight: normal mutators refresh outside guards, cached reads do not, explicit --refresh uses the same candidate validator. Real command test rejects a story-edited policy and diagnoses stale remote preflight.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c08.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Never let a fetched receipt nominate its own anchor or replace the independently observed frontier.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Never let a fetched receipt nominate its own anchor or replace the independently observed frontier.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:19Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `8162080179b323d7d23d4c5656a3e2622bdb5d51e314e593030d5bba78182d07`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C08",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "98010d6bc41e67fc2e29330d569a5532eab4a92cf5c6bea0a01bfab7adb243ce"
}
```
