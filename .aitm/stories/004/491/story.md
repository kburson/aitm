---
schema: "aitm.story/v0"
id: 491
title: "[Epic] Core — Core packaging and release qualification"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/491"
parent: 1
children: [68, 69, 70, 71, 72]
blocking: []
blocked-by: [8, 23, 56, 58, 62, 66, 81, 505]
created: "2026-11-27T04:48:57Z"
updated: "2026-11-27T05:03:04.452Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 15.5, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP22"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Core — Core packaging and release qualification

**GitHub issue:** [#491](https://github.com/kburson/aitm/issues/491)

## Scope

Land package, workflows and checker incrementally; separately qualify the exact released wheel. The release check follows the source landing.

Parent: #1. Core coordination: #2. State: Backlog.

## Delivery

Integration owner: #71. Require verified sibling deliveries #68, #69, #70, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Release qualification #72 runs after the source landing. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #8, #23, #56, #58, #62, #66, #81, #505.

## Children

- #68 · C52 · 3 h
- #69 · C59 · 3 h
- #70 · C53 · 3.5 h
- #71 · C69 · 3.5 h
- #72 · C60 · 2.5 h

Estimate: **15.5 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).
