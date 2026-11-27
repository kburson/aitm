---
schema: "aitm.story/v0"
id: 512
title: "[Core C106] Integrate governed PR decisions on trunk"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/512"
parent: 489
children: []
blocking: [490]
blocked-by: [238, 241]
created: "2026-11-27T04:49:16Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C106"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C106] Integrate governed PR decisions on trunk

**GitHub issue:** [#512](https://github.com/kburson/aitm/issues/512)

## Current scope and parent

Parent: #489. Core coordination: #2. State: Backlog.

Integration owner for governed PR decisions. Run exact-candidate equivalence, push/merge authorization, composed-source and retirement proofs against the combined tree. Review and land the slice on trunk.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #238, #239, #511, #241, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 2 implementation agent-hours including verification and review. **Blocked by:** #238, #241.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.
