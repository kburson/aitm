---
schema: "aitm.story/v0"
id: 358
title: "[Spike] Find what blocks parallel category runs"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/358"
parent: 356
children: []
blocking: [359]
blocked-by: [357]
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

# [Spike] Find what blocks parallel category runs

[GitHub issue #358](https://github.com/kburson/aitm/issues/358) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 500. Priority P2. Size S.

Question: given the accepted classification, what prevents each category from running as its own pytest invocation at the same time, locally and as separate CI jobs?

The hosted path-map check remains the ordinary pull-request path. Name the conditions a later parallel run must satisfy, including any test that cannot share a machine with another category.

## Bound

This is research for #356. Write the finding. Shards, jobs, and a schedule stay unimplemented in this story.

Stay blocked until #357 is accepted.

## Handoff

#359 implements the accepted classification and this finding together.
