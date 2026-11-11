---
schema: aitm.story/v0
id: 1
title: "[Epic] aitm product: Python rewrite of ai-task-manager"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/1
parent: null
children: [2]
blocking: []
blocked-by: []
created: 2026-11-08T19:24:00Z
updated: 2026-11-11T14:41:24Z
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: { agent-hours: null, size: null }
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm
files:
  draft: draft.md
  events: events.jsonl
  design: [design/architecture.md]
  plan: [plan/master-plan.md]
  attachments: [attachments/transcript.md, attachments/research-ai-task-manager-survey.md]
expansions: []
trips: []
---

# [Epic] aitm product: Python rewrite of ai-task-manager

**GitHub issue:** [kburson/aitm#1](https://github.com/kburson/aitm/issues/1)

## User story

As a developer delivering software with AI agents
I want a lightweight, harness-agnostic story workflow whose records live in git
So that stories move from idea to Done without the tool itself becoming the blocker

## Scope

Root epic for the aitm product: a Python rewrite of ai-task-manager as a core plus extensions. Holds the architecture design and the master plan. Each section is a child epic with its own design and plan, written just in time.

## Metadata

- **Origin:** brainstorm session 2026-11-08 — [`draft.md`](draft.md)
- **Created:** 2026-11-08

## Dependencies

- **Parent:** none · **Blocking:** none · **Blocked by:** none
- **Children:** [#2 aitm-core](../2/story.md)

<details><summary>State history (generated from events.jsonl)</summary>

```json
[
  { "ts": "2026-11-08T19:24:00Z", "state": "backlog", "from": null }
]
```

</details>

## Accepted architecture and master plan

[Architecture](design/architecture.md) completed SAR/SPR/XPR. [Master plan](plan/master-plan.md) was reconciled to the accepted core design and accepted by the authorized SAR, published `ca14c5de346235488d71f223c226385ad8a290f5`. [SAR collateral](plan/reviews/sar-2026-11-09-master-plan/review-manifest.md). Historical Backlog and open owner choices remain; no implementation, production cutover or epic closure is implied.


## Story dashboard production intake from #181

- M2 owns [C05 board projection](../../../drafts/2026-11/20261108-1310-github-extension/draft.md#c05-intake-from-181).
- M6 owns [C06 hosted viewer](../../../drafts/2026-11/20261108-1310-viewer/draft.md#c06-intake-from-181).
- M8 owns [C07 estimate calibration](../../../drafts/2026-11/20261108-1310-rubric/draft.md#c07-intake-from-181).

These are backlog inputs to the existing milestone drafts. [#2](../2/story.md) owns timing qualification and [#100](../../001/100/story.md) owns Cost compatibility. [The #181 transfer](../../001/181/attachments/2026-11-11-production-scope-transfer.md) records the end-to-end dependency map.
