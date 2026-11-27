---
schema: "aitm.story/v0"
id: 505
title: "[Core C95] Test selection policy and execution receipt"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/505"
parent: 481
children: []
blocking: [65, 241, 482, 483, 484, 487, 488, 489, 491, 517]
blocked-by: [14, 42]
created: "2026-11-27T04:49:10Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C95"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":481,"design_sources":[2],"scope_entry":"C95","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C95] Test selection policy and execution receipt

**GitHub issue:** [#505](https://github.com/kburson/aitm/issues/505)

## Current scope and parent

Parent: #481. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/verification/selection.py` · `resolve_test_selection(request, policy, registry) -> SelectionDecision`. `tests/integration/test_c95.py` binds selector obligations, policy and fallback to the exact capture. Prove baseline fallback and hold for unavailable and no successful fallback laundering for failed execution or invalid proof.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #42, #43, #44, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #14, #42.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #481 with scope entry **C95**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
