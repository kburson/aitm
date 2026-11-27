---
schema: "aitm.story/v0"
id: 480
title: "[Epic] Core — Attempt control and verification preparation"
kind: "epic"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/480"
parent: 1
children: [30, 31, 39, 40, 41]
blocking: []
blocked-by: [13, 15, 23, 27, 500, 502, 504]
created: "2026-11-27T04:48:47Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 18.0, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP11"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":1,"design_sources":[1,2],"scope_entry":"EP11","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Epic] Core — Attempt control and verification preparation

**GitHub issue:** [#480](https://github.com/kburson/aitm/issues/480)

## Scope

Fence a stopped attempt, prove single-use admission, and prepare exact captured inputs offline.

Parent: #1. Core coordination: #2. State: Ready for Planning.

## Delivery

Integration owner: #31. Require verified sibling deliveries #39, #40, #41, #30, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #13, #15, #23, #27, #500, #502, #504.

## Children

- #39 · C30 · 4 h
- #40 · C31 · 4 h
- #41 · C32 · 3.5 h
- #30 · C33 · 3 h
- #31 · C34 · 3.5 h

Estimate: **18 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **110** · **P1/Feature** · **18 agent-hours**. Design accepted for this manual workflow through issue #1 with scope entry **EP11**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
