---
schema: "aitm.story/v0"
id: 353
title: "[Spike] Find the process boundary for trusted local test observation"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/353"
parent: 351
children: []
blocking: [355]
blocked-by: []
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

# [Spike] Find the process boundary for trusted local test observation

[GitHub issue #353](https://github.com/kburson/aitm/issues/353) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 450. Priority P2. Size S.

Question: why did local test observation share a process with the code under test, and what process boundary does a pre-commit run need before its result can be trusted?

#146 showed a pytest observer sharing a process with the candidate. #267 showed pytest-testmon missing real failures. Explain that boundary and name the condition a later run must meet.

## Bound

This is research for #351. Write the finding. Production code and CI stay unchanged. The boundary is described here. It is implemented by the feature story.

## Handoff

#355 implements the accepted finding together with the report from #354.
