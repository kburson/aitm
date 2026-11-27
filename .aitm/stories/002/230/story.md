---
schema: "aitm.story/v0"
id: 230
title: "[Core] Qualify Usage Monitor Cost integration"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/230"
parent: 493
children: []
blocking: [259]
blocked-by: [51, 459, 521]
created: "2026-11-11T14:37:29Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
estimate: {"agent-hours": 3.25, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-11-230-cost-dependency-replan.md", "plan/2026-11-11-230-cost-dependency-replan-review.md"], "attachments": []}
expansions: []
trips: []
scope-transfer: {"story": 181, "key": "C04", "publication": "20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b", "path": ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"}
---

# [Core] Qualify Usage Monitor Cost integration

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#493](https://github.com/kburson/aitm/issues/493). Key: COST4. Estimate: **3.25 h**. Blocked by: #51, #459, #521.

Retain live Cost qualification outside M1 after #51, #459 and the compatible package when selected. The package source and wheel precede this observation.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

[GitHub issue #230](https://github.com/kburson/aitm/issues/230) · [Owner epic #2](https://github.com/kburson/aitm/issues/2)

## Scope

This carries forward C04 from the owner-approved #181 scope transfer. The live qualification of the #459 planning usage producer belongs to #2. The 3.25 h estimate is preliminary and subject to refinement and JIT. #181's local delivery closes independently.

## Acceptance criteria

- [ ] Qualify the pinned story report and compatible export for the exact project, story, attempt, window, cutoff, rate digest and basis. Reconcile direct and inclusive priced and unpriced usage with retained coverage.
- [ ] Verify compatibility with the Core C44 receiver under replay, delayed evidence, rate revision and ambiguous delivery. Keep the original usage and pricing provenance. Exclude unauthenticated or foreign inputs from qualified Cost.
- [ ] Verify tool duration alone adds no Cost and Actual can qualify without usage. This follow-up qualifies the shared contract. #459 supplies the producer and #51 owns Core ingress.

## Evidence and prerequisites

- [Reviewed Slice C section](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c04-bind-cost-and-compatible-usage-ingress) and [completed C01 evidence](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md).
- Runtime prerequisites #51 and #459. Preserve the release, scope and authority gates in the reviewed section.

[Dependency replan](plan/2026-11-11-230-cost-dependency-replan.md) · [Independent review](plan/2026-11-11-230-cost-dependency-replan-review.md)

## Current producer dependency

The owner-approved #455 replan replaces the old #123/#124 producer dependencies with [#459](https://github.com/kburson/aitm/issues/459), the fixture-qualified planning usage producer. #51 and this story's live receiver qualification remain the Core gates. [Verified rebaseline](../../001/100/plan/2026-11-25-100-session-owned-scope-disposition.md).
