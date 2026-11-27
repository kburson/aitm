---
schema: "aitm.story/v0"
id: 514
title: "[Core C101] CLI/MCP parity and hosted restart refusals"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/514"
parent: 490
children: []
blocking: []
blocked-by: [81, 242, 499, 513]
created: "2026-11-27T04:49:18Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C101"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":490,"design_sources":[2],"scope_entry":"C101","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C101] CLI/MCP parity and hosted restart refusals

**GitHub issue:** [#514](https://github.com/kburson/aitm/issues/514)

## Current scope and parent

Parent: #490. Core coordination: #2. State: Ready for Planning.

`tests/integration/test_c101.py` · installed CLI/MCP parity and restart scenarios. Use identical versioned operations, refuse direct managed effects on the qualified route, and replay interrupted post-merge closeout while refusing trip demotion, pivot, and abandon. Real host proof remains with M2/M3.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #240, #242, #513, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #81, #242, #499, #513.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #490 with scope entry **C101**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
