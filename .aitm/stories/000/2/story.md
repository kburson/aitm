---
schema: aitm.story/v0
id: 2
title: "[Epic] aitm-core: story store, state machine, CLI, extension API"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/2
parent: 1
children: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 74, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 75, 37, 76, 38, 39, 40, 41, 42, 77, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 78, 53, 54, 55, 56, 57, 58, 59, 60, 63, 64, 79, 80, 61, 62, 81, 65, 82, 66, 67, 68, 69, 70, 71, 72, 228, 229]
blocking: []
blocked-by: []
created: 2026-11-08T19:24:20Z
updated: "2026-11-11T14:41:24Z"
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: { agent-hours: 257.5, size: XL }
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

Historical initial bottom-up Plan estimate: **220.5 h across 70 P1/S leaves**, all ≤4 h, published `55b94bbe77a19002ff077c122560cf185652d25c`. [Ordered leaf ledger, dependencies and parallel waves](plan/leaf-stories.md). This revision records the Plan estimate separately from the original 180 h Refine estimate. Acceptance is the scoped planning review outcome, not unavailable runtime exact-content policy acceptance or child readiness. [Completion report](plan/planning-completion.md).

Native acceptance is recorded separately from the [fresh full-file reread procedure limitation](plan/review-procedure-audit.md). That historical question was answered by the owner's separate-validation instruction and is fulfilled by the new records below; the completed old review cap was not extended.

## Separate full-file validation and current plan

Design published `3702cfde855e7a2345e12439f19cc2ee9ebe7291`; current plan published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. Both separate native XPR validations used Astra-6/ExtraHigh author and Opus 5.5/high reviewer, with full actual fresh input retrieval verified each round. [Current plan review](plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). Current Plan estimate: **257.5 h / 79 leaves**, all ≤4 h. Initial Refine and earlier Plan facts remain retained.

[Design phase retrospective](design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md), [plan phase retrospective](plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md), [current leaf ledger](plan/leaf-stories.md) and [reconciliation receipt](plan/leaf-reconciliation-receipt.json). These are phase retrospectives, not epic Review→Done sign-off. Historical Backlog, owner choices and C6 prerequisites remain. Stop before implementation.


## Production timing qualification from #181

[#228 Legacy timing replay](../../002/228/story.md) and [#229 Native Actual](../../002/229/story.md) qualify dashboard use of the existing Core contracts after #72. They are post-release follow-ups and do not extend the #72 release acceptance. #51 remains the Core receiver and outcome owner. The accepted Core plan remains the source for its existing implementation leaves.
