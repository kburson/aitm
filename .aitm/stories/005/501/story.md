---
schema: "aitm.story/v0"
id: 501
title: "[Core C93] Standalone, epic and child-JIT basis evaluator"
kind: "story"
state: done
issue: "https://github.com/kburson/aitm/issues/501"
parent: 478
children: []
blocking: [502]
blocked-by: [35, 36, 75]
created: "2026-11-27T04:49:06Z"
updated: "2026-11-28T07:14:24.194936+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C93"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-28-pickup.md", "plan/2026-11-28-pr-582-verification.md", "plan/2026-11-28-pr-582-source-sar.md", "plan/2026-11-28-pr-582-hosted.json", "plan/2026-11-28-pr-582-verifier.json", "plan/2026-11-28-pr-582-premerge-verifier.json", "plan/2026-11-28-pr-582-source-sar.json", "plan/2026-11-28-pr-582-branch-gates.json", "plan/2026-11-28-pr-582-delivery.json", "plan/2026-11-28-pr-582-native-link.json", "plan/2026-11-28-pr-582-readiness.json"], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":478,"design_sources":[2],"scope_entry":"C93","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
linked-pr: "https://github.com/kburson/aitm/pull/582"
---

# [Core C93] Standalone, epic and child-JIT basis evaluator

**GitHub issue:** [#501](https://github.com/kburson/aitm/issues/501)

## Current scope and parent

Parent: #478. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/machine/pickup_basis.py` · `evaluate_pickup_basis(snapshot, request) -> PickupBasisResult`. `tests/integration/test_c93.py` distinguishes standalone, epic, and child JIT, binds the current reviewed parent entry and source, and rejects a stale or wrong parent entry.

**Estimate:** 3.5 implementation agent-hours including verification and review. **Blocked by:** #35, #36, #75.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **30** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #478 with scope entry **C93**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).


## Scoped manual pickup and verified delivery

[Scoped JIT](plan/2026-11-28-pickup.md) · [Coordinator sign-off and Agent Cost](retro/2026-11-28-delivery.md) · [Native Linked PR #582](https://github.com/kburson/aitm/pull/582).
