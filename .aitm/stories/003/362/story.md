---
schema: "aitm.story/v0"
id: 362
title: "Flag a scheduled build failure"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/362"
parent: null
children: [363, 364, 365, 366]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T13:52:04Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Flag a scheduled build failure

[GitHub issue #362](https://github.com/kburson/aitm/issues/362) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 560. Priority P2. Size Feature.

Decompose one claim out of #133 into an independent epic. Publish one flag when the scheduled build fails and clear it when a later scheduled build of the same workflow passes. A person or an agent who checks the flag sees the failing run and the time, and decides what to do.

The flag is a warning. Merges, workspace pause, and repair-owner nomination stay outside this epic. This epic does not create the scheduled run.

## Research, then development

1. #363 names the scheduled run to watch.
2. #364 names the place a person and an agent can both read one flag.
3. #365 records the flag from that run in that place. It is blocked by #363 and #364.
4. #366 shows the flag when a person or an agent checks it. It is blocked by #365.

When #363 finds that the scheduled run is not in production yet, #365 stays blocked until that run exists. The story that would create the run is #361 under #356. That fact is written in the spike receipt. It is not a blocker edge from this epic to #356.

## Starting material

#277 and #278 show an advisory warning with no merge authority. #278 also paused work and named a repair owner. That pause and nomination stay outside this epic. #158 shows a merge fence accepting a moved base. The flag stays off the merge route.

This epic is independent of #351 and #356. Development does not start from this epic.
