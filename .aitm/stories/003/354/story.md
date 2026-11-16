---
schema: "aitm.story/v0"
id: 354
title: "Report the affected tests for the working tree"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/354"
parent: 351
children: []
blocking: [355]
blocked-by: [352]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T22:15:04Z"
last-branch: "codex/354-working-tree-report"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-16-354-working-tree-obligations-plan.md", "plan/reviews/2026-11-16-354-plan-sar.md", "plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-review-manifest.md", "plan/2026-11-16-354-develop-checkpoint.md"], "attachments": ["attachments/2026-11-16-354-local-report-probe.json"]}
expansions: []
trips: []
---

# Report the affected tests for the working tree

[GitHub issue #354](https://github.com/kburson/aitm/issues/354) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 460. Priority P2. Size S.

Report the tests affected by the current uncommitted working tree.

## Development

Implement the accepted receipt from #352. An agent can read the report before commit. The report executes no tests. The hosted pull-request path map stays as #344 delivered it.

Stay blocked until #352 is accepted. When that receipt says no trustworthy list can be named, record that result in this story and stop.

## Bound

This story delivers the report. It does not run the tests. Running them is #355, which also waits on #353.

## Implementation planning

#352 is accepted and closed. [Implementation plan](plan/2026-11-16-354-working-tree-obligations-plan.md) · [Plan SAR](plan/reviews/2026-11-16-354-plan-sar.md).

## Develop

Opus 5.5 at high effort accepted the exact implementation plan in round two after five findings were resolved. Develop starts on `codex/354-working-tree-report`. #355 remains blocked by #354. [XPR manifest](plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-review-manifest.md) · [Final reviewer verdict](plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-reviewer-response-2.md).

[Implementation and local proof](plan/2026-11-16-354-develop-checkpoint.md).
