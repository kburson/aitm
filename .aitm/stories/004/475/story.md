---
schema: "aitm.story/v0"
id: 475
title: "[Epic] Core — Installation and worktree binding"
kind: "epic"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/475"
parent: 1
children: [19, 20, 21, 22, 500]
blocking: []
blocked-by: [13, 15, 23]
created: "2026-11-27T04:48:43Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 17.0, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP06"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":1,"design_sources":[1,2],"scope_entry":"EP06","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Epic] Core — Installation and worktree binding

**GitHub issue:** [#475](https://github.com/kburson/aitm/issues/475)

## Scope

Init a disposable store, bind a story and reconcile authored sync without foreign worktree effects.

Parent: #1. Core coordination: #2. State: Ready for Planning.

## Delivery

Integration owner: #500. Require verified sibling deliveries #19, #20, #21, #22, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #13, #15, #23.

## Children

- #19 · C11 · 4 h
- #20 · C12 · 3 h
- #21 · C16 · 4 h
- #22 · C17 · 4 h
- #500 · C104 · 2 h

Estimate: **17 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **60** · **P1/Feature** · **17 agent-hours**. Design accepted for this manual workflow through issue #1 with scope entry **EP06**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
