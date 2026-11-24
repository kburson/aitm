---
schema: "aitm.story/v0"
id: 427
title: "[Spike] Measure the orchestrator from its existing interactive chat"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/427"
parent: 426
children: []
blocking: [428]
blocked-by: []
created: "2026-11-24T15:08:20Z"
updated: "2026-11-24T15:08:20Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Measure the orchestrator from its existing interactive chat

[GitHub issue #427](https://github.com/kburson/aitm/issues/427)

Research parent: #426.

## Question

Can a running orchestrator assign capture to its own existing chat and return the cost of its own story work while remaining interactive?

## Experiment

Use the current interactive orchestration route first. In bounded sessions on Codex, Claude Code, and Grok Build, place an unrelated turn before assignment and perform two assigned turns. Test harness-local self-report or a session-scoped end-of-turn callback. Verify whether the final result-producing turn can settle through a callback or receipt without requiring another model turn. Separate orchestration from any delegated/provider costs. Record whether assignment and reporting require operator intervention, and what fields an interactive session can prove. Leave retrospective lookup and headless launch for later spikes.

Deliver a surface matrix and sanitized evidence showing assignment boundary, own-cost reporting path, and any gap at the final turn.
