---
schema: "aitm.story/v0"
id: 9
title: "[Core C04] Typed operations and MemoryBackend semantics"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/9"
parent: 2
children: []
blocking: [10, 15, 16, 17]
blocked-by: [4, 6, 7, 8]
created: "2026-11-09T08:00:01Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c04-typed-operations-and-memorybackend-semantics"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C04", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "a1ab7e794e9a693ac7a295fa5df4ac82684a3900343040a5bad037fa217882a4"}
---

# [Core C04] Typed operations and MemoryBackend semantics

**GitHub issue:** [kburson/aitm#9](https://github.com/kburson/aitm/issues/9) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C04 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 4 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c04-typed-operations-and-memorybackend-semantics), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C02 / #4](../4/story.md), [C54 / #6](../6/story.md), [C55 / #7](../7/story.md), [C56 / #8](../8/story.md).

**Blocking:** [C05 / #10](../10/story.md), [C14 / #15](../15/story.md), [C15 / #16](../16/story.md), [C09 / #17](../17/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 4 h · **Depends on:** C02, C54, C55, C56 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/operations.py; src/aitm_core/store/backend.py; src/aitm_core/store/memory_backend.py; packages/aitm-core/tests/unit/test_c04.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `Backend.read(snapshot: Snapshot, paths: Sequence[str]) -> Blobs; transact(op: Operation, expected: Snapshot) -> OperationResult; RelatedWriteSet(read_set, writes, events); FinalizationIntent(kind, version, related_preconditions, payload); WriteAuthorizer(owner, change) and PendingActionRunner(snapshot) ports; AttemptPreflight(context: OperationContext) -> PreflightResult; OperationCategory(normal, authored_sync, stop_reconciliation, recovery)`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_operation_cas: refusal records guards without transition; identical operation retry returns prior result, changed payload errors; stale read-set re-evaluates or conflicts, related-story update is atomic. Memory and later Git backends run same behavioral cases. Freeze category and applicability vectors: no attempt in the pinned read-set gives explicit not-applicable; attempt-bearing implementation mutation without installed AttemptPreflight reports unavailable. Stop/reconciliation and recovery categories have explicit narrow capabilities, not a blanket preflight bypass. Every pre-C31 attempt-bearing producer, explicitly C27 reconcile, C28 transitions and C30 expansion, uses an injected typed fixture preflight in test-only service composition; normal production remains unavailable when that required implementation is absent. attempt reconcile and expand both use category normal and require preflight; neither borrows stop_reconciliation/recovery to bypass trips. Stop/reconciliation categories cover only their separately declared narrow operations. WriteAuthorizer absence likewise refuses production writes before C14; C04–C08 backend tests use explicit fixture authority, not a shipped allow-all default. Test missing/fixture/real-registration distinctions and immutable category propagation across retries. Keep missing WriteAuthorizer and AttemptPreflight negative tests stable by deliberately unregistering the named slot in a test composition; do not assert permanent absence in the evolving production default.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c04.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Do not build a blind file-map API or a MemoryBackend with weaker semantics.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Do not build a blind file-map API or a MemoryBackend with weaker semantics.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:01Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `a1ab7e794e9a693ac7a295fa5df4ac82684a3900343040a5bad037fa217882a4`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C04",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "a1ab7e794e9a693ac7a295fa5df4ac82684a3900343040a5bad037fa217882a4"
}
```
