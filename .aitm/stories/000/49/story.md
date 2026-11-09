---
schema: "aitm.story/v0"
id: 49
title: "[Core C42] Atomic sign-off and retained evidence reconstruction"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/49"
parent: 2
children: []
blocking: [51, 52, 57, 63, 79, 80, 61, 62, 65]
blocked-by: [38, 45, 46]
created: "2026-11-09T08:02:54Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c42-atomic-sign-off-and-retained-evidence-reconstruction"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C42", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "857dc46e8bc5842f827b804a610b6a68595a3d317453676ebed11571d4d89c88"}
---

# [Core C42] Atomic sign-off and retained evidence reconstruction

**GitHub issue:** [kburson/aitm#49](https://github.com/kburson/aitm/issues/49) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C42 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c42-atomic-sign-off-and-retained-evidence-reconstruction), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C29 / #38](../38/story.md), [C38 / #45](../45/story.md), [C39 / #46](../46/story.md).

**Blocking:** [C44 / #51](../51/story.md), [C45 / #52](../52/story.md), [C61 / #57](../57/story.md), [C62 / #63](../63/story.md), [C76 / #79](../79/story.md), [C79 / #80](../80/story.md), [C65 / #61](../61/story.md), [C66 / #62](../62/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C29, C38, C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C38. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/reviews/activation.py; src/aitm_core/outcomes.py; src/aitm_core/signoff.py; src/aitm_core/evidence.py; src/aitm_core/cli/evidence.py; packages/aitm-core/tests/integration/test_c42.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `build_close_outcome(snapshot, retro) -> Outcome; signoff(retro: RetroInput) -> OperationResult; reconcile_evidence(request) -> EvidenceResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_signoff_atomic: current review/delivery/applicable prior lifecycle proof and proposed retro close in one transaction, never require prior signoff; missing earlier conditions yield Done/unverified without satisfying delivered dependency. Reconstruct derived receipts only from retained authoritative proof; preserve already stopped clock. Missing actual proof returns typed rerun requirement for C61, not a fabricated pass. C42 owns construction of the complete typed Close outcome from C56 schema, current estimate/attempt/source/coverage/retro facts. Real signoff commits outcome, retrospective, session end, Done and related-story resolution with one operation ID/CAS; refusal or crash before CAS leaves none, retry after CAS returns the single whole close. No later callback appends the missing outcome. Wire evidence reconcile to C38 reconcile_review after retaining/reconstructing applicable proof and running current preflight. It may activate a single retained early verdict only in Review with current prerequisites, recording the genuine later clock stop without a second verdict. A missing real test reports the managed rerun route and never activates prematurely. Any producer test here that crosses a story/defect Develop/Test/Review exit uses an explicitly composed typed StoryExitGuards fixture until C76/C79 deliver the real evaluators. An explicitly unregistered required edge must refuse as unavailable; no permissive production default. C49/C68 and C65/C66 later re-prove the relevant paths with actual C76/C79 registrations and specific guard causes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c42.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C42 owns signoff/reconstruction, C61 owns evidence-only reopening and managed rerun. No hidden human gate or extension of the implementation clock through retrospective time.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: C42 owns signoff/reconstruction, C61 owns evidence-only reopening and managed rerun. No hidden human gate or extension of the implementation clock through retrospective time.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:54Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `857dc46e8bc5842f827b804a610b6a68595a3d317453676ebed11571d4d89c88`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C42",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "77ea28eda3e67296624843b24f0cb24b1ab76fa85d2bd6b7b2b87fa22153bc0b"
}
```
