---
schema: "aitm.story/v0"
id: 355
title: "Run the affected tests before commit"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/355"
parent: 351
children: []
blocking: []
blocked-by: [353, 354]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T19:41:49Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Run the affected tests before commit

[GitHub issue #355](https://github.com/kburson/aitm/issues/355) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 250. Priority P2. Size S.

Run the affected tests for the current uncommitted working tree before commit.

## Development

Use the list from the accepted #354 receipt and the process boundary from the accepted #353 receipt. An agent can run that list and get a pass or fail while the rest of the suite stays unrun. The hosted pull-request path map stays as #344 delivered it.

Stay blocked until #354 and #353 are accepted. When the process boundary cannot be met, record that result in this story and stop.
