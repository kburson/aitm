---
schema: "aitm.story/v0"
id: 365
title: "Record the scheduled-failure flag"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/365"
parent: 362
children: []
blocking: [366]
blocked-by: [363, 364]
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

# Record the scheduled-failure flag

[GitHub issue #365](https://github.com/kburson/aitm/issues/365) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 650. Priority P2. Size S.

Record one flag from the run named by the accepted #363 receipt, in the place named by the accepted #364 receipt.

## Development

Set the flag when that run fails. Clear it when a later run of the same workflow passes. Store the run identity and the time. Merges, workspace pause, and repair-owner nomination stay outside this story. This story does not create the watched run.

Stay blocked until #363 and #364 are accepted. When #363 names a run that is not in production yet, stay blocked until that run exists.
