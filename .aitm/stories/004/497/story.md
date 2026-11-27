---
schema: "aitm.story/v0"
id: 497
title: "[Core C110] Integrate legacy policy dispositions and proof fixtures"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/497"
parent: 471
children: []
blocking: [12, 37, 80, 241, 472, 479, 484, 489]
blocked-by: [494, 495, 496]
created: "2026-11-27T04:49:03Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C110"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C110] Integrate legacy policy dispositions and proof fixtures

**GitHub issue:** [#497](https://github.com/kburson/aitm/issues/497)

## Current scope and parent

Parent: #471. Core coordination: #2. State: Backlog.

`docs/architecture/legacy-sdlc/policy-decisions.md` · integration owner. Verify every open crosswalk decision has a disposition, source or explicit uncertainty, named owner and earliest pickup gate. Preserve representative acceptance/refusal vectors for Core and separate provider handoffs. Land these inputs on trunk.

**Integration owner.** Prepare the authorized slice resource if applicable. Require exact sibling deliveries #494, #495, #496, slice proof, and the applicable trunk gates before landing. The sibling-delivery set gates merge and is separate from native code prerequisites.

**Estimate:** 3.5 implementation agent-hours including verification and review. **Blocked by:** #494, #495, #496.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.
