---
schema: "aitm.story/v0"
id: 508
title: "[Core C96] Provision an integration resource in Plan"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/508"
parent: 485
children: []
blocking: [240, 486, 489, 490, 513]
blocked-by: [63, 237, 502]
created: "2026-11-27T04:49:13Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C96"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":485,"design_sources":[2],"scope_entry":"C96","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C96] Provision an integration resource in Plan

**GitHub issue:** [#508](https://github.com/kburson/aitm/issues/508)

## Current scope and parent

Parent: #485. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/managed/integration_resource.py` · `prepare_integration_resource(request) -> ResourceResult`. `tests/integration/test_c96.py` proves the qualified owner can provision an exact Plan-bound resource without child deliveries or an attempt clock, safely unlock child pickup, and reconcile the same role/claim on restart.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #234, #235, #236, #237, #509, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #63, #237, #502.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **60** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #485 with scope entry **C96**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
