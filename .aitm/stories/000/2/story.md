---
schema: aitm.story/v0
id: 2
title: "[Epic] aitm-core: story store, state machine, CLI, extension API"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/2
parent: 1
children: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 74, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 75, 37, 76, 38, 39, 40, 41, 42, 77, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 78, 53, 54, 55, 56, 57, 58, 59, 60, 63, 64, 79, 80, 61, 62, 81, 65, 82, 66, 67, 68, 69, 70, 71, 72, 228, 229, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 230]
blocking: [247]
blocked-by: [456]
created: 2026-11-08T19:24:20Z
updated: "2026-11-26T15:06:19.931Z"
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: { agent-hours: 297.25, size: XL }
priority: P1
original-estimate: { agent-hours: 180, size: XL, priority: P1, source: refinement.md }
origin: .aitm/drafts/2026-11/20261108-1310-core
files:
  draft: draft.md
  events: events.jsonl
  design: [design/core-design.md, design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md]
  plan: [plan/core-implementation-plan.md, plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md]
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

- **Parent:** [#1](../1/story.md) · **Blocking:** [#247 M6 Viewer](../../002/247/story.md) · **Producer prerequisite:** [#456](../../004/456/story.md), Completed

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

## Governed PR lifecycle amendment

The [reviewed amendment](plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) and [review collateral](plan/reviews/governed-pr-lifecycle/review-cycle.md) were published at `8939d9fff17599fe644604b5b267625b4bc5621f`. The [child reconciliation](plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md) records the new Core leaves, retained IDs, updated estimates, and native dependency readback.

The Core implementation estimate is **297.25 h across 89 bounded leaves**. #228 and #229 retain their separate 7.5 h preliminary post-release scope. The GitHub and harness qualifications have separate package handoffs. #159 remains blocked by #157 and #158. Epic and leaf lifecycle authority remains at the existing planning boundary.

## Usage Monitor Cost integration

Completed [#456](https://github.com/kburson/aitm/issues/456) satisfies the Core producer prerequisite and replaces the retired #100 edge. #230 remains the Core child for live qualification of the #459 planning usage producer against #51. #230 has a separate preliminary estimate and lies outside the accepted M1 release scope. [Producer delivery sign-off](https://github.com/kburson/aitm/blob/2ec8bca0934c62bbb44866ea57fb5c2776960c0c/.aitm/stories/004/456/retro/2026-11-26-delivery-sign-off.md) · [Reviewed dependency replan](https://github.com/kburson/aitm/blob/3e43229baecb7d1d3346df9d3012f1eacf821b39/.aitm/stories/002/230/plan/2026-11-11-230-cost-dependency-replan.md).

## Configured workflow amendment and delivery replan

The [accepted design amendment](design/2026-11-26-configured-workflow-amendment-draft.md) and its XPR were published at [07755fa0](https://github.com/kburson/aitm/commit/07755fa0bf8e5fabdcadbce0eb31a126b5cc6303). The [implementation-plan revision](plan/2026-11-26-configured-workflow-implementation-plan.md), [legacy rule crosswalk](plan/2026-11-26-legacy-rule-crosswalk.md), and [mini-epic ledger](plan/2026-11-26-core-mini-epic-ledger.md) propose replacing the single integration sequence with bounded trunk deliveries. Claude Opus 5.5 accepted the revised plan in round two of [XPR](plan/reviews/plan/2026-11-27-2026-11-26-configured-workflow-implementation-plan-review-d69706914b83ab63954983955c19e200/review-d69706914b83ab63954983955c19e200-review-manifest.md). The reviewed ledger keeps the 89 existing M1 issue IDs and proposes 22 Core mini-epics with 110 children and 386.5 estimated agent-hours. Earlier accepted plans remain historical. Native parentage and issue scopes still reflect the prior decomposition pending reconciliation.

## Behavior-driven testing

Use the independently reviewed [Core testing standard](../../002/286/plan/2026-11-14-286-core-behavior-test-standard.md) when planning and reviewing Core leaves.

## #133 no longer blocks Core

On 2026-11-16 the owner removed #133 from this epic's blockers. The test-feedback replacement is [#340](../../003/340/story.md) and [#341](../../003/341/story.md).
