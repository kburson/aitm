---
schema: "aitm.story/v0"
id: 503
title: "[Core C91] Typed obligation placement and structural validation"
kind: "story"
state: done
issue: "https://github.com/kburson/aitm/issues/503"
parent: 479
children: []
blocking: [37, 65, 80, 504, 509]
blocked-by: [14, 498]
created: "2026-11-27T04:49:08Z"
updated: "2026-11-28T07:54:26.470288+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C91"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-28-pickup.md", "plan/2026-11-28-pr-585-verification.md", "plan/2026-11-28-pr-585-source-sar.md", "plan/2026-11-28-pr-585-hosted.json", "plan/2026-11-28-pr-585-verifier.json", "plan/2026-11-28-pr-585-premerge-verifier.json", "plan/2026-11-28-pr-585-source-sar.json", "plan/2026-11-28-pr-585-branch-gates.json", "plan/2026-11-28-pr-585-delivery.json", "plan/2026-11-28-pr-585-native-link.json", "plan/2026-11-28-pr-585-readiness.json"], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":479,"design_sources":[2],"scope_entry":"C91","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
linked-pr: "https://github.com/kburson/aitm/pull/585"
---

# [Core C91] Typed obligation placement and structural validation

**GitHub issue:** [#503](https://github.com/kburson/aitm/issues/503)

## Current scope and parent

Parent: #479. Core coordination: #2. State: Ready for Planning.

`src/aitm_core/machine/obligations.py` · `validate_profile(profile, registry, contract) -> ProfileValidation`. `tests/unit/test_c91.py` rejects a bypass of attempt start, exact candidate, terminal finalization, or required slot type in either mode. Explicit typed terminal and recovery destinations resolve even when labels change.

**Estimate:** 4 implementation agent-hours including verification and review. **Blocked by:** #14, #498.

[Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md). The parent plan does not establish this child’s Design, Plan, JIT applicability, or implementation authority.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **10** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #479 with scope entry **C91**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).


## Verified delivery

[Scoped JIT](plan/2026-11-28-pickup.md) · [Coordinator sign-off and Agent Cost](retro/2026-11-28-delivery.md) · [Native Linked PR #585](https://github.com/kburson/aitm/pull/585).
