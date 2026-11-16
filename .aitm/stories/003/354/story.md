---
schema: "aitm.story/v0"
id: 354
title: "Report the affected tests for the working tree"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/354"
parent: 351
children: []
blocking: [355]
blocked-by: [352]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T19:55:56Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
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
