---
schema: "aitm.story/v0"
id: 482
title: "[Epic] Core — Source review, delivery and sign-off evidence"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/482"
parent: 1
children: [45, 46, 47, 48, 49, 77]
blocking: []
blocked-by: [8, 13, 31, 35, 500, 504, 505]
created: "2026-11-27T04:48:49Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 21.5, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP13"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Source review, delivery and sign-off evidence

**GitHub issue:** [#482](https://github.com/kburson/aitm/issues/482)

## Scope

Bind review to exact source, verify target mutation and recover the sign-off inputs.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #48. Require verified sibling deliveries #77, #45, #46, #47, #49, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #8, #13, #31, #35, #500, #504, #505.

## Children

- #77 · C73 · 3 h
- #45 · C38 · 4 h
- #46 · C39 · 3.5 h
- #47 · C40 · 3 h
- #48 · C41 · 4 h
- #49 · C42 · 4 h

Estimate: **21.5 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
