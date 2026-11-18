---
schema: "aitm.story/v0"
id: 366
title: "Show the scheduled-failure flag when it is checked"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/366"
parent: 362
children: []
blocking: []
blocked-by: [365]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T13:52:04Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Show the scheduled-failure flag when it is checked

[GitHub issue #366](https://github.com/kburson/aitm/issues/366) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 600. Priority P2. Size S.

Show the current flag when a person or an agent checks it.

## Development

The check returns the failing run and the time recorded by #365, or a clear statement that the flag is unset. The check recommends no repair. Merges, workspace pause, and assignment stay outside this story.

Stay blocked until #365 is accepted.
