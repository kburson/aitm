---
schema: "aitm.story/v0"
id: 510
title: "[Core C98] Versioned workflow cutover and reconciliation"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/510"
parent: 486
children: []
blocking: []
blocked-by: [19, 38, 55, 80, 237]
created: "2026-11-27T04:49:14Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C98"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":486,"design_sources":[2],"scope_entry":"C98","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C98] Versioned workflow cutover and reconciliation

**GitHub issue:** [#510](https://github.com/kburson/aitm/issues/510)

## Current scope and parent

Parent: #486. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/machine/cutover.py` · `reconcile_workflow_revision(request) -> CutoverResult`. `tests/integration/test_c98.py` maps early, active, and terminal records in a second clone, retains exact history, resumes a verified merge during closeout, and holds unresolved resource identity, unknown state, or pending host effects.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #19, #38, #55, #80, #237.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **50** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #486 with scope entry **C98**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
