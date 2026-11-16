---
schema: "aitm.story/v0"
id: 351
title: "Select the tests affected by uncommitted work"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/351"
parent: null
children: [352, 353, 354, 355]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T19:41:49Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Select the tests affected by uncommitted work

[GitHub issue #351](https://github.com/kburson/aitm/issues/351) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 210. Priority P2. Size Feature.

Decompose one claim out of #133 into an independent epic. Deliver local test selection so an agent runs the tests affected by uncommitted work before commit.

#133 delivered the hosted pull-request path map in #340, #341, and #344. This epic leaves that map in place. It is an independent follow-on. It is not a child of #133.

## Research, then development

Spike stories answer one question and create no production software. Feature stories deliver the behavior those accepted findings describe. A feature stays blocked until every spike receipt it depends on is accepted.

1. #352 names the condition that blocks local test selection.
2. #353 names the process boundary a trusted pre-commit run needs.
3. #354 reports the affected tests. It is blocked by #352.
4. #355 runs that list before commit. It is blocked by #354 and #353.

## Starting material

Read #138, #139, #140, #141, #142, #143, #147, #267, #288, and #339. Read `tools/ci/tia/local.py` and `tools/ci/path_map.py` on current trunk. The hosted map is evidence to learn from.

Development does not start from this epic. Codex picks up the child stories after the blockers are accepted.
