---
schema: "aitm.story/v0"
id: 479
title: "[Epic] Core — Configured state transitions"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/479"
parent: 1
children: [37, 38, 76, 503, 504]
blocking: []
blocked-by: [15, 23, 27, 35, 497, 500, 502]
created: "2026-11-27T04:48:46Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 17.5, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP10"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Configured state transitions

**GitHub issue:** [#479](https://github.com/kburson/aitm/issues/479)

## Scope

Load two differently shaped workflows and prove typed guards, directives, terminal routes and split/recovery destinations.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #504. Require verified sibling deliveries #503, #37, #76, #38, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #15, #23, #27, #35, #497, #500, #502.

## Children

- #503 · C91 · 4 h
- #37 · C28 · 4 h
- #76 · C71 · 3.5 h
- #38 · C29 · 4 h
- #504 · C105 · 2 h

Estimate: **17.5 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
