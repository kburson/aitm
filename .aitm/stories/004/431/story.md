---
schema: "aitm.story/v0"
id: 431
title: "[Spike] Deliver a usage receipt with every headless XPR turn"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/431"
parent: 426
children: []
blocking: []
blocked-by: [430]
created: "2026-11-24T15:08:31Z"
updated: "2026-11-24T15:08:31Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Deliver a usage receipt with every headless XPR turn

[GitHub issue #431](https://github.com/kburson/aitm/issues/431)

Research parent: #426.

Start after #430 has recorded its findings.

## Question

Can the existing XPR handoff carry a machine-produced receipt back to the orchestrator for every reviewer turn and keep that cost distinct from the orchestrator's own work?

## Experiment

Request usage explicitly in each XPR handoff. Using the routes qualified by the prior spikes, run a real two-round headless XPR and exercise each supported provider as reviewer. The reviewer harness or its session-owned launcher attaches settled usage to the turn result. Bind the receipt to story, run, attempt, review, round, and verified provider turn. If measurement arrives after the text, verify delivery as a correlated completion rather than invoking the reviewer again. Replay one delivery and exercise one interrupted or unmeasurable turn. Verify the result remains usable, the cost appears once when evidenced, and gaps stay visible. Demonstrate a story subtotal with a separate orchestrator line.

Deliver sanitized handoff evidence, a receipt example, and a summary of provider-specific limitations to inform the research epic's strategy decision.
