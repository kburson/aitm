---
schema: "aitm.story/v0"
id: 488
title: "[Epic] Core — Concurrency and recovery qualification"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/488"
parent: 1
children: [59, 60, 61, 62]
blocking: []
blocked-by: [31, 48, 58, 66, 81, 500, 502, 504, 505]
created: "2026-11-27T04:48:55Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 13.0, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP19"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Concurrency and recovery qualification

**GitHub issue:** [#488](https://github.com/kburson/aitm/issues/488)

## Scope

Use shared fixtures to prove ordered stops, delivery and store races with the real Core dispatchers.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #62. Require verified sibling deliveries #61, #59, #60, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #31, #48, #58, #66, #81, #500, #502, #504, #505.

## Children

- #61 · C65 · 3.5 h
- #62 · C66 · 3.5 h
- #59 · C70 · 3 h
- #60 · C50 · 3 h

Estimate: **13 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
