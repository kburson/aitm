---
schema: "aitm.story/v0"
id: 363
title: "[Spike] Identify the run a failure flag should watch"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/363"
parent: 362
children: []
blocking: [365]
blocked-by: []
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

# [Spike] Identify the run a failure flag should watch

[GitHub issue #363](https://github.com/kburson/aitm/issues/363) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 570. Priority P2. Size S.

Question: which current workflow is the scheduled build this flag should watch, and what is absent when no production scheduled run exists?

Name the repository, workflow file, and event. When the run does not exist yet, name the story that would create it and stop. The candidate story is #361 under #356. Leave the blocker graph unchanged. Create no workflow in this spike.

## Bound

This is research for #362. Write the finding. A schedule, a flag, and a merge rule stay unimplemented here.

## Handoff

#365 records the flag for the run this receipt names. When the run is not in production yet, that feature stays blocked until the run exists.
