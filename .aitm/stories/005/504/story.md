---
schema: "aitm.story/v0"
id: 504
title: "[Core C105] Integrate configured state transitions on trunk"
kind: "story"
state: done
issue: "https://github.com/kburson/aitm/issues/504"
parent: 479
children: []
blocking: [480, 482, 483, 484, 485, 486, 487, 488]
blocked-by: [38, 76, 503]
created: "2026-11-27T04:49:09Z"
updated: "2026-11-28T09:12:54.387721+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C105"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-28-pickup.md", "plan/2026-11-28-pr-584-verification.md", "plan/2026-11-28-pr-584-source-sar.md", "plan/2026-11-28-pr-584-hosted.json", "plan/2026-11-28-pr-584-verifier.json", "plan/2026-11-28-pr-584-premerge-verifier.json", "plan/2026-11-28-pr-584-source-sar.json", "plan/2026-11-28-pr-584-branch-gates.json", "plan/2026-11-28-pr-584-delivery.json", "plan/2026-11-28-pr-584-native-link.json", "plan/2026-11-28-pr-584-readiness.json"], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":479,"design_sources":[2],"scope_entry":"C105","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
linked-pr: "https://github.com/kburson/aitm/pull/584"
---

# [Core C105] Integrate configured state transitions on trunk

**GitHub issue:** [#504](https://github.com/kburson/aitm/issues/504)

## Current scope and parent

Parent: #479. Core coordination: #2. State: Ready for Planning.

Integration owner for configured transitions. Prove the composed loader, terminal/rework routing, and split through the transition route and its typed decision result. Review and land the slice on trunk.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #503, #37, #76, #38, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 2 implementation agent-hours including verification and review. **Blocked by:** #38, #76, #503.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **50** · **P1/S** · **2 agent-hours**. Design accepted for this manual workflow through issue #479 with scope entry **C105**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).


## Verified delivery

[Scoped JIT](plan/2026-11-28-pickup.md) · [Coordinator sign-off and Agent Cost](retro/2026-11-28-delivery.md) · [Native Linked PR #584](https://github.com/kburson/aitm/pull/584).
