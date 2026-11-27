---
schema: aitm.story/v0
id: 2
title: "[Epic] aitm-core: story store, state machine, CLI, extension API"
kind: epic
state: ready-for-plan
issue: https://github.com/kburson/aitm/issues/2
parent: 1
children: [228, 229]
blocking: [247]
blocked-by: [456]
created: 2026-11-08T19:24:20Z
updated: "2026-11-27T14:41:12.161Z"
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: {"agent-hours": 4, "size": "S", "scope": "direct coordination"}
priority: "P3"
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
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":1,"design_sources":[1],"scope_entry":"#2","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
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
  { "ts": "2026-11-08T19:24:20Z", "state": "backlog", "from": null },
  {"ts": "2026-11-27T05:40:34.192Z", "state": "refine", "from": "backlog"}
]
```

</details>

## Refinement

**Current refinement.** #2’s direct coordination scope is size **S**, estimated at **4 agent-hours**, at **Rank 230**. [Sizing basis](2026-11-26-coordination-and-follow-up-refinement.md). The **386.5 implementation agent-hours** are the delivery total for 110 stories in 22 sibling mini-epics under #1. The two direct children, #228 and #229, are post-release timing follow-ups with their own **7.5 h** combined estimate. [Accepted delivery ledger](plan/2026-11-26-core-mini-epic-ledger.md) · [Historical rollup and initial Project readback](2026-11-26-refinement-refresh.md).

The original **180 h / XL / P1** Refine estimate and its earlier scope remain historical. [Initial rationale](refinement.md).

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

The [accepted design amendment](design/2026-11-26-configured-workflow-amendment-draft.md) and its XPR were published at [07755fa0](https://github.com/kburson/aitm/commit/07755fa0bf8e5fabdcadbce0eb31a126b5cc6303). The [implementation-plan revision](plan/2026-11-26-configured-workflow-implementation-plan.md), [legacy rule crosswalk](plan/2026-11-26-legacy-rule-crosswalk.md), and [mini-epic ledger](plan/2026-11-26-core-mini-epic-ledger.md) propose replacing the single integration sequence with bounded trunk deliveries. Claude Opus 5.5 accepted the revised plan in round two of [XPR](plan/reviews/plan/2026-11-27-2026-11-26-configured-workflow-implementation-plan-review-d69706914b83ab63954983955c19e200/review-d69706914b83ab63954983955c19e200-review-manifest.md). The reviewed ledger keeps the 89 existing M1 issue IDs and proposes 22 Core mini-epics with 110 children and 386.5 estimated agent-hours. Earlier accepted plans remain historical. GitHub and planning were reconciled to the accepted ledger. #2 coordinates the rollout without a shared integration branch. The mini-epics are under #1; #228 and #229 remain direct children. The implementation estimate is separate from planning effort and Cost.

## Behavior-driven testing

Use the independently reviewed [Core testing standard](../../002/286/plan/2026-11-14-286-core-behavior-test-standard.md) when planning and reviewing Core leaves.

## #133 no longer blocks Core

On 2026-11-16 the owner removed #133 from this epic's blockers. The test-feedback replacement is [#340](../../003/340/story.md) and [#341](../../003/341/story.md).

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](plan/2026-11-26-core-native-reconciliation-receipt.json).

## Implementation ranks

[Dependency-ordered ranks](plan/2026-11-26-core-implementation-ranks.md) mirror Project #24. Epic ranks and within-epic child ranks advance in steps of 10.

## Agent Cost

<!-- aitm-core-2-cost-active -->

Planning and reconciliation evidence is recorded in [the planning effort receipt](attachments/2026-11-26-core-planning-effort.md).

**Known Standard API-equivalent subtotal:** USD 10.8370112. **Verified billed cost:** Unknown. All observed planning usage is attributed to #2.

| Work | Provider/model | Cached input | New input | Output | Standard API-equivalent USD |
| --- | --- | ---: | ---: | ---: | ---: |
| Initial legacy/current-plan assessment | Codex / gpt-6.2-sol | 547,840 | 74,761 | 4,694 | $0.251246 |
| Runtime workflow and planning paths | Codex / gpt-6.2-sol | 88,448 | 2,695 | 1,386 | $0.028095 |
| Dev, Review and guardrails | Codex / gpt-6.2-sol | 91,008 | 2,198 | 1,289 | $0.026387 |
| Design amendment draft | Codex / gpt-6.2-sol | 965,120 | 99,231 | 10,187 | $0.396844 |
| JIT policy and design XPR author | Codex / gpt-6.2-sol | 5,730,048 | 47,149 | 8,508 | $0.752383 |
| Core replan and plan XPR author | Codex / gpt-6.2-sol | 12,050,688 | 87,962 | 27,664 | $1.657633 |
| GitHub and planning reconciliation | Codex / gpt-6.2-sol | 18,030,208 | 86,034 | 32,781 | $3.892932 |
| Design builder check | Codex / gpt-6.2-sol | 194,304 | 28,354 | 1,586 | $0.091998 |
| Legacy crosswalk subagent | Codex / gpt-6.2-sol | 887,936 | 59,762 | 12,317 | $0.331488 |
| Workflow delta subagent | Codex / gpt-6.2-sol | 757,760 | 51,522 | 4,522 | $0.224040 |
| Live inventory subagent | Codex / gpt-6.2-sol | 660,736 | 55,086 | 3,997 | $0.216216 |
| Native reconciliation verifier | Codex / gpt-6.2-sol | 577,152 | 44,299 | 4,282 | $0.189133 |
| Design XPR reviewer | Claude / claude-opus-5-5 | 837,888 | 89,357 | 14,759 | $1.177486 |
| Plan XPR reviewer | Claude / claude-opus-5-5 | 1,398,439 | 112,977 | 20,889 | $1.601132 |

## Core kickoff — 2026-11-27

**Planning at kickoff** · then rank **10** · **P3/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #1 with scope entry **#2**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md). Coordination is P3 on Project #24. The earlier planning header showed P1. The Core delivery slices and timing follow-ups retain P1.

## Dependency rank correction

Project #24 rank **230**. Current status **Ready for Planning**. See the [product dependency map](../../000/1/plan/2026-11-27-product-rank-scale.md) for the verified prerequisites.
