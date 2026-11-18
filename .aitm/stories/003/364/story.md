---
schema: "aitm.story/v0"
id: 364
title: "[Spike] Find where a person and an agent can read one flag"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/364"
parent: 362
children: []
blocking: [365]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T23:38:27Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Find where a person and an agent can read one flag

[GitHub issue #364](https://github.com/kburson/aitm/issues/364) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 640. Priority P2. Size S.

Question: where can one current flag be stored so a person and an agent can both read it, while the flag stays off the merge route, off required status checks, and outside workspace control?

Name one place and the exact fields a check would read. Explain how that place leaves merges and workspaces unaffected.

## Bound

This is research for #362. Write the finding. Publish no flag and leave branch protection unchanged.

## Handoff

#365 stores the flag in the place this receipt names.
