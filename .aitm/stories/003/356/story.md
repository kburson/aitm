---
schema: "aitm.story/v0"
id: 356
title: "Shard tests by execution category"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/356"
parent: null
children: [357, 358, 359, 360, 361]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-18T20:56:33Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Shard tests by execution category

[GitHub issue #356](https://github.com/kburson/aitm/issues/356) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 500. Priority P2. Size Feature.

Decompose one claim out of #133 into an independent epic. Divide the collected tests into execution categories and run those categories as parallel shards for a full sweep.

Ordinary local selection and the hosted pull-request path map stay the short path. The scheduled sweep is the run that uses every shard.

The categories are fast unit, slow unit, local integration, and systems integration. The classification spike names any collected test that fits none of those four.

## Research, then development

1. #357 classifies the collected tests.
2. #358 finds what blocks running each category as its own pytest invocation, locally and as separate CI jobs. It is blocked by #357.
3. #359 runs a local full sweep as those shards. It is blocked by #357 and #358.
4. #360 runs the same sweep in CI. It is blocked by #359.
5. #361 schedules that CI sweep. It is blocked by #360.

Spike stories write findings and create no production software. Feature stories stay blocked until the receipts they depend on are accepted.

## Starting material

Read #285, #286, #148, #290, #292, #293, #294, and #337. Advisory shard code and the refused cutover are evidence. They are the starting point for the spikes.

This epic is independent of #351, #362, and #370. Development does not start from this epic.

#370 decides how one Python program selects affected tests on every operating system. This epic classifies tests by execution category.
