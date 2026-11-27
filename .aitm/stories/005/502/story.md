---
schema: "aitm.story/v0"
id: 502
title: "[Core C94] Material child-JIT change reconciliation"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/502"
parent: 478
children: []
blocking: [37, 237, 479, 480, 484, 485, 486, 487, 488, 508]
blocked-by: [35, 501]
created: "2026-11-27T04:49:07Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C94"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":478,"design_sources":[2],"scope_entry":"C94","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C94] Material child-JIT change reconciliation

**GitHub issue:** [#502](https://github.com/kburson/aitm/issues/502)

## Current scope and parent

Parent: #478. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/machine/jit_scope.py` · `evaluate_jit_scope(parent_entry, jit_record, reviews) -> ScopeResult`. `tests/unit/test_c94.py` passes a recorded in-scope adjustment and blocks independent scope, criteria, commitment, and ambiguity cases. A review of an earlier reconciled digest cannot pass.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #36, #75, #501, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #35, #501.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #478 with scope entry **C94**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
