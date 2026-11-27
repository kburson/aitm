---
schema: "aitm.story/v0"
id: 472
title: "[Epic] Core — Trusted Git story store"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/472"
parent: 1
children: [9, 10, 11, 12, 13]
blocking: []
blocked-by: [8, 497]
created: "2026-11-27T04:48:39Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 19.0, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP03"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Trusted Git story store

**GitHub issue:** [#472](https://github.com/kburson/aitm/issues/472)

## Scope

Read and atomically write a pinned local store and refuse an untrusted fetch candidate.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #13. Require verified sibling deliveries #9, #10, #11, #12, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #8, #497.

## Children

- #9 · C04 · 4 h
- #10 · C05 · 4 h
- #11 · C06 · 3.5 h
- #12 · C07 · 3.5 h
- #13 · C08 · 4 h

Estimate: **19 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
