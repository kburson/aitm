---
schema: "aitm.story/v0"
id: 484
title: "[Epic] Core — Installed lifecycle guards and recovery"
kind: "epic"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/484"
parent: 1
children: [79, 80, 81, 82, 506, 507]
blocking: []
blocked-by: [15, 23, 27, 31, 48, 58, 497, 502, 504, 505]
created: "2026-11-27T04:48:51Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 21.5, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP15"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":1,"design_sources":[1,2],"scope_entry":"EP15","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Epic] Core — Installed lifecycle guards and recovery

**GitHub issue:** [#484](https://github.com/kburson/aitm/issues/484)

## Scope

Exercise the installed guard and explanation paths, same-attempt rework, and post-delivery mutation fencing.

Parent: #1. Core coordination: #2. State: Ready for Planning.

## Delivery

Integration owner: #81. Require verified sibling deliveries #79, #80, #82, #506, #507, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #15, #23, #27, #31, #48, #58, #497, #502, #504, #505.

## Children

- #79 · C76 · 3 h
- #80 · C79 · 4 h
- #81 · C78 · 4 h
- #82 · C75 · 3.5 h
- #506 · C102 · 3.5 h
- #507 · C103 · 3.5 h

Estimate: **21.5 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **150** · **P1/Feature** · **21.5 agent-hours**. Design accepted for this manual workflow through issue #1 with scope entry **EP15**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
