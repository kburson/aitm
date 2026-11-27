---
schema: "aitm.story/v0"
id: 499
title: "[Core C92] Versioned Markdown directive resolution"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/499"
parent: 473
children: []
blocking: [37, 65, 81, 242, 514]
blocked-by: [14, 498]
created: "2026-11-27T04:49:05Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C92"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":473,"design_sources":[2],"scope_entry":"C92","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C92] Versioned Markdown directive resolution

**GitHub issue:** [#499](https://github.com/kburson/aitm/issues/499)

## Current scope and parent

Parent: #473. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/ext/directives.py` · `resolve_directive(registry, snapshot, capability_id) -> DirectiveView`. `tests/unit/test_c92.py` returns exact content identity, applicable scope and requested evidence, keeps disabled versions unavailable, and proves reading dispatches no effect.

**Estimate:** 3.5 implementation agent-hours including verification and review. **Blocked by:** #14, #498.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **50** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #473 with scope entry **C92**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
