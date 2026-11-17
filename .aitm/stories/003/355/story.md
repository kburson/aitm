---
schema: "aitm.story/v0"
id: 355
title: "Run the affected tests before commit"
kind: "story"
state: "blocked"
issue: "https://github.com/kburson/aitm/issues/355"
parent: 351
children: []
blocking: []
blocked-by: [353, 354, 368]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-17T00:53:39Z"
last-branch: "codex/355-precommit-execution"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-16-355-pre-commit-execution-plan.md", "plan/reviews/2026-11-16-355-plan-sar.md", "plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-review-manifest.md", "plan/2026-11-16-355-execution-qualification.md"], "attachments": ["attachments/2026-11-16-355-execution-qualification.json"]}
expansions: []
trips: []
---

# Run the affected tests before commit

[GitHub issue #355](https://github.com/kburson/aitm/issues/355) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 470. Priority P2. Size S.

Run the affected tests for the current uncommitted working tree before commit.

## Development

Use the list from the accepted #354 receipt and the process boundary from the accepted #353 receipt. An agent can run that list and get a pass or fail while the rest of the suite stays unrun. The hosted pull-request path map stays as #344 delivered it.

Stay blocked until #354 and #353 are accepted. When the process boundary cannot be met, record that result in this story and stop.

## Implementation planning

#353 is accepted and #354 is delivered. [Qualification-first plan](plan/2026-11-16-355-pre-commit-execution-plan.md) · [Plan SAR](plan/reviews/2026-11-16-355-plan-sar.md).

## Develop

Opus 5.5 at high effort accepted the exact plan in round two after both findings were resolved. Develop starts at the execution qualification checkpoint. [XPR manifest](plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-review-manifest.md) · [Final reviewer verdict](plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-reviewer-response-2.md).

## Execution qualification hold

The delivered #354 report reproduced all 30 pinned obligations. The strict local execution boundary and scoped assignment authority were unavailable. The accepted plan stops at this checkpoint and records the owner scope decision. [Qualification hold](plan/2026-11-16-355-execution-qualification.md) · [Machine receipt](attachments/2026-11-16-355-execution-qualification.json).

Stay blocked until [#368](../368/story.md) passes independent review of the integrated live qualification.
