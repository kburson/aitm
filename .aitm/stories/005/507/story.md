---
schema: "aitm.story/v0"
id: 507
title: "[Core C103] Uncertain-merge and post-delivery recovery fence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/507"
parent: 484
children: []
blocking: [65, 80, 241, 513]
blocked-by: [38, 40, 46]
created: "2026-11-27T04:49:12Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C103"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C103] Uncertain-merge and post-delivery recovery fence

**GitHub issue:** [#507](https://github.com/kburson/aitm/issues/507)

## Current scope and parent

Parent: #484. Core coordination: #2. State: Backlog.

`src/aitm_core/machine/delivery_fence.py` · `admit_after_delivery_observation(snapshot, operation) -> AdmissionResult`. `tests/integration/test_c103.py` denies incompatible operations during uncertain merge, reconciles the exact result, and allows only supported evidence and closeout after verified delivery.

**Estimate:** 3.5 implementation agent-hours including verification and review. **Blocked by:** #38, #40, #46.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.
