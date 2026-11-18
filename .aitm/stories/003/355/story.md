---
schema: "aitm.story/v0"
id: 355
title: "Run the affected tests before commit"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/355"
parent: 351
children: []
blocking: []
blocked-by: [353, 354]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T13:52:04Z"
last-branch: "planning"
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

## Owner scope decision

The owner accepted the [#368](../368/story.md) HOLD and removed it as a blocker. GitHub closed #368 as Completed at 2026-11-18T02:10:27Z. Project 24 shows Done and Delivered for the completed investigation. #355 delivers the cooperative advisory run from #353: a separate pytest process, the operating-system exit, and a complete receipt matched to the #354 list, labeled advisory. #353 and #354 stay accepted prerequisites. [Decision](../368/plan/2026-11-18-368-owner-scope-decision.md) · [Closure receipt](../368/plan/closure-receipt.json).

## Test

The cooperative runner is in [PR #369](https://github.com/kburson/aitm/pull/369), targeting trunk at `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`. GitHub confirmed head `81a6602a7b045f081f597b0e0b3e6480258d01ff`, with clean local source tree `4dffcbcfdfca38febd63463124f2f5e140e70c1d`. [Advisory delivery plan](plan/2026-11-18-355-advisory-delivery.md) · [Hosted CI](https://github.com/kburson/aitm/actions/runs/44306782506).

The initial candidate entered rework after independent source review reproduced a dropped incomplete worker receipt and skipped final snapshot readback. The replacement retains parsed worker receipts on evidence refusal and always performs the final readback after attempting the worker invocation. [Replacement CI](https://github.com/kburson/aitm/actions/runs/44308197226).

A follow-up source review reproduced uv writing cache files in the inspected checkout under a repo-local XDG cache. The final candidate resolves uv's cache and redirects any cache inside the inspected or frozen checkout to scratch. [Final candidate CI](https://github.com/kburson/aitm/actions/runs/44308912626).

The hosted macOS queue is investigated by [#371](../371/story.md) under [#370](../370/story.md). #355 continues the accepted advisory command.

## Hosted verification hold

The [independent source review](plan/reviews/2026-11-18-355-source-review.md) passed for PR #369 head `2bd902dbd982188e00e0f21a5b5c3565699c332d` and tree `594971b04a905027b72cac36425dd34c5b16e63e`. The exact advisory proof passed all 30 assigned tests. The first hosted attempt had a base/candidate runner-image mismatch. The next two attempts exhausted hosted macOS arm64 runner capacity with zero Python steps. The [trusted verifier](plan/2026-11-18-355-final-capacity-hold.json) holds the exact candidate. #355 stays in Test until the unchanged workflow can produce and authenticate a successful same-head attempt. #351 remains open. [Latest hosted attempt](https://github.com/kburson/aitm/actions/runs/44308912626/attempts/3).

The owner-requested [retry](https://github.com/kburson/aitm/actions/runs/44308912626/attempts/4) acquired both macOS runners. Candidate Python passed and trusted base Python reached its eight-minute execution limit. The [verifier returned HOLD](plan/2026-11-18-355-attempt-4-verifier-hold.json).
