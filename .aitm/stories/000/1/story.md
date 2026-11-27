---
schema: aitm.story/v0
id: 1
title: "[Epic] aitm product: Python rewrite of ai-task-manager"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/1
parent: null
children: [2, 247, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 522, 523, 524]
blocking: []
blocked-by: []
created: 2026-11-08T19:24:00Z
updated: "2026-11-27T06:05:49.247Z"
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

- M2 [#524](https://github.com/kburson/aitm/issues/524) owns [C05 board projection](../../005/524/draft.md#c05-intake-from-181).
- M6 [Viewer #247](../../002/247/story.md) owns [C06 hosted viewer](../../002/247/draft.md#c06-intake-from-181).
- M8 owns [C07 estimate calibration](../../005/523/draft.md#c07-intake-from-181).

These are backlog inputs to the existing milestone drafts. [#2](../2/story.md) owns timing qualification and [#100](../../001/100/story.md) owns Cost compatibility. [The #181 transfer](../../001/181/attachments/2026-11-11-production-scope-transfer.md) records the end-to-end dependency map.

## M6 Viewer graduation

[Viewer Epic #247](../../002/247/story.md) carries the M6 master-plan scope. Its backlog and reviewed preview evidence are retained in its own planning record.

## M7 and M8 graduation

- [M7 History import #522](../../005/522/story.md) delivers the validated corpus. It depends on [#72](https://github.com/kburson/aitm/issues/72) and scoped M2 source access or an approved equivalent.
- [M8 Estimation rubric #523](../../005/523/story.md) consumes Core estimate and outcome lineage from [#51](https://github.com/kburson/aitm/issues/51), the qualified release [#72](https://github.com/kburson/aitm/issues/72), qualified Actual from [#229](https://github.com/kburson/aitm/issues/229), and the validated history from [#522](https://github.com/kburson/aitm/issues/522). [#228](https://github.com/kburson/aitm/issues/228) is the alternate measurement route if separately qualified and reconciled.

The dependency direction is M7 to M8. M7 publishes the corpus under a neutral contract and runs independently of the rubric. The linked design specs are drafts. [Graduation readback](plan/2026-11-26-m7-m8-graduation.json).

## M2 graduation and M7 source access

[M2 #524](../../005/524/story.md) is under #1, with a [draft design](../../005/524/design/github-extension-design.md). Its bounded source-access child [#525](https://github.com/kburson/aitm/issues/525) qualifies independently and is the native source-access blocker for M7 [#522](https://github.com/kburson/aitm/issues/522). [#72](https://github.com/kburson/aitm/issues/72) remains the Core release prerequisite. [Graduation and dependency readback](plan/2026-11-27-m2-graduation.json).

## M2, M7 and M8 reviewed sizing

[Accepted XPRs and implementation order](plan/2026-11-27-m2-m7-m8-xpr-and-sizing.md) records Rank 250 for M2 #524, 260 for M7 #522, and 270 for M8 #523. #525 can land as soon as its Core release prerequisite and source qualification are satisfied.
