---
schema: "aitm.story/v0"
id: 474
title: "[Epic] Core — Store readback and publication recovery"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/474"
parent: 1
children: [16, 17, 18, 23]
blocking: []
blocked-by: [8, 13, 15]
created: "2026-11-27T04:48:42Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 14.5, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP05"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Store readback and publication recovery

**GitHub issue:** [#474](https://github.com/kburson/aitm/issues/474)

## Scope

Show a deterministic fresh-clone view, lost-publish recovery and forward-only repair.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #23. Require verified sibling deliveries #16, #17, #18, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #8, #13, #15.

## Children

- #16 · C15 · 2.5 h
- #23 · C18 · 4 h
- #17 · C09 · 4 h
- #18 · C10 · 4 h

Estimate: **14.5 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
