---
schema: "aitm.story/v0"
id: 493
title: "[Epic] Agent Cost Capture package"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/493"
parent: 1
children: [230, 519, 520, 521]
blocking: []
blocked-by: []
created: "2026-11-27T04:48:59Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 13.75, "size": "Feature"}
priority: null
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "COST"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Agent Cost Capture package

**GitHub issue:** [#493](https://github.com/kburson/aitm/issues/493)

## Scope

Deliver the independently installable and versioned Agent Cost Capture package. Preserve the separate Core release path and exact source/wheel receipts.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #521. Require verified sibling deliveries #519, #520, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Live #230 qualification follows the package delivery when the plugin is selected. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: None.

## Children

- #519 · COST1 · 4 h
- #520 · COST2 · 3.5 h
- #521 · COST3 · 3 h
- #230 · COST4 · 3.25 h

Estimate: **13.75 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
