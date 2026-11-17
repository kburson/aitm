---
schema: "aitm.story/v0"
id: 351
title: "Select the tests affected by uncommitted work"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/351"
parent: null
children: [352, 353, 354, 355, 368]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-17T12:19:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-16-351-local-tia-spike-plan.md", "plan/reviews/2026-11-16-351-spike-plan-sar.md"], "attachments": []}
expansions: []
trips: []
---

# Select the tests affected by uncommitted work

[GitHub issue #351](https://github.com/kburson/aitm/issues/351) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 430. Priority P2. Size Feature.

Decompose one claim out of #133 into an independent epic. Deliver local test selection so an agent runs the tests affected by uncommitted work before commit.

#133 delivered the hosted pull-request path map in #340, #341, and #344. This epic leaves that map in place. It is an independent follow-on. It is not a child of #133.

## Research, then development

Spike stories answer one question and create no production software. Feature stories deliver the behavior those accepted findings describe. A feature stays blocked until every spike receipt it depends on is accepted.

1. #352 names the condition that blocks local test selection.
2. #353 names the process boundary a trusted pre-commit run needs.
3. #354 reports the affected tests. It is blocked by #352.
4. #355 runs that list before commit. It requires #354, #353, and #368.
5. [#368](../368/story.md) qualifies the protected local runner, independent observer, and scoped assignment for #355.

## Starting material

Read #138, #139, #140, #141, #142, #143, #147, #267, #288, and #339. Read `tools/ci/tia/local.py` and `tools/ci/path_map.py` on current trunk. The hosted map is evidence to learn from.

Development does not start from this epic. Codex picks up the child stories after the blockers are accepted.

## Spike pickup

[Investigation plan](plan/2026-11-16-351-local-tia-spike-plan.md) · [Plan SAR passed](plan/reviews/2026-11-16-351-spike-plan-sar.md).


## Accepted spike findings

- #352 passed independent review after two rounds. The stock command first needs its import path wired. Once it starts, the candidate suite policy refuses before collection. The exact probe established 30 pinned mapped obligations for the audited module. Fresh candidate collection and general completeness require separate evidence. [Finding](../352/plan/2026-11-16-352-findings.md) · [Review verdict](../352/plan/reviews/2026-11-16-352-independent-findings-review.md).
- #353 passed independent review on the first round. Cooperative local results can use direct process exit plus a matching worker receipt. Trusted results require qualified outcome observation and custody outside candidate authority. [Finding](../353/plan/2026-11-16-353-findings.md) · [Review verdict](../353/plan/reviews/2026-11-16-353-independent-findings-review.md).

#354 may proceed to feature planning. Run SAR on its implementation plan before Develop. #355 needs #354's delivered interface and its own reviewed qualification plan for the process boundary.

## Develop

Epic planning and deep-dive assessment are complete. Project 24 records Rank 430, Priority P2, Size Feature, and all five children. #354 is delivered; #355 and #368 remain open and blocked at the accepted qualification boundary. GitHub Project status advanced from Planning to Dev after the issue-planning and metadata preflight.
