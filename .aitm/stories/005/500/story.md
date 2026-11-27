---
schema: "aitm.story/v0"
id: 500
title: "[Core C104] Integrate installed setup and binding on trunk"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/500"
parent: 475
children: []
blocking: [476, 477, 478, 479, 480, 481, 482, 483, 485, 486, 487, 488]
blocked-by: [20, 22]
created: "2026-11-27T04:49:05Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C104"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C104] Integrate installed setup and binding on trunk

**GitHub issue:** [#500](https://github.com/kburson/aitm/issues/500)

## Current scope and parent

Parent: #475. Core coordination: #2. State: Backlog.

Integration owner for installation and binding. Run #20/#21/#22 installed proofs against the exact composed tree. Review and land the installation slice on trunk with verified source mapping.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #19, #20, #21, #22, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 2 implementation agent-hours including verification and review. **Blocked by:** #20, #22.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.
