---
schema: aitm.story/v0
id: 2
title: "[Epic] aitm-core: story store, state machine, CLI, extension API"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/2
parent: 1
children: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
blocking: []
blocked-by: []
created: 2026-11-08T19:24:20Z
updated: 2026-11-09T08:17:42Z
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: { agent-hours: 220.5, size: XL }
priority: P1
original-estimate: { agent-hours: 180, size: XL, priority: P1, source: refinement.md }
origin: .aitm/drafts/2026-11/20261108-1310-core
files:
  draft: draft.md
  events: events.jsonl
  design: [design/core-design.md]
  plan: [plan/core-implementation-plan.md]
  attachments: []
expansions: []
trips: []
---

# [Epic] aitm-core: story store, state machine, CLI, extension API

**GitHub issue:** [kburson/aitm#2](https://github.com/kburson/aitm/issues/2)

## User story

As a developer running agents on stories
I want a core that stores every story's records on the `planning` branch and walks stories through the state machine
So that state, timing and evidence are recorded by the tool, never repaired by hand

## Scope

`aitm-core`: the `.aitm/` story store (ideas, drafts, stories), git-plumbing writes to `planning`, the rebuildable SQLite index, the state machine (entry guards, resident actions, exit guards), the one-expansion limit and trip rule, advisory and enforce modes, the `aitm` CLI, the extension API, and the git-host and backlog provider interfaces. GitHub itself lives in a separate extension.

## Metadata

- **Origin:** [`draft.md`](draft.md), from the master brainstorm [`../1/draft.md`](../1/draft.md)
- **Created:** 2026-11-08

## Dependencies

- **Parent:** [#1](../1/story.md) · **Blocking:** none · **Blocked by:** none

<details><summary>State history (generated from events.jsonl)</summary>

```json
[
  { "ts": "2026-11-08T19:24:20Z", "state": "backlog", "from": null }
]
```

</details>

## Refinement

Initial Refine estimate: **180 implementation agent-hours**, **XL epic**, **P1**. [Rationale and provenance](refinement.md). The [implementation plan](plan/core-implementation-plan.md) completed the authorized SAR → manual SPR → native XPR sequence; historical Backlog state is retained until supported reconciliation. No implementation is authorized.

## Accepted implementation decomposition

Bottom-up Plan estimate: **220.5 h across 70 P1/S leaves**, all ≤4 h, published `55b94bbe77a19002ff077c122560cf185652d25c`. [Ordered leaf ledger, dependencies and parallel waves](plan/leaf-stories.md). This revision records the Plan estimate separately from the original 180 h Refine estimate. Acceptance is the scoped planning review outcome, not unavailable runtime exact-content policy acceptance or child readiness. [Completion report](plan/planning-completion.md).

Native acceptance is recorded separately from the [fresh full-file reread procedure limitation](plan/review-procedure-audit.md). The owner decision about additional explicit validation remains before implementation; the completed plan review cap was not extended.
