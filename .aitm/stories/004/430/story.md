---
schema: "aitm.story/v0"
id: 430
title: "[Spike] Qualify a callable result-and-usage turn for each XPR provider"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/430"
parent: 426
children: []
blocking: [431]
blocked-by: [429]
created: "2026-11-24T15:08:28Z"
updated: "2026-11-24T15:10:05Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Qualify a callable result-and-usage turn for each XPR provider

[GitHub issue #430](https://github.com/kburson/aitm/issues/430)

Research parent: #426.

Start after #429 has recorded its findings.

## Question

For each cross-provider headless XPR harness, can an orchestrator request exactly one turn through a supported API, SDK, or structured CLI interface and receive the review result plus settled usage for that same turn?

## Experiment

Probe the route used or usable by XPR for Codex, Claude Code, and Grok Build. Send two requests to a persistent review session and correlate each outcome with provider evidence using verified session and turn identities. Test reused sessions, cumulative deltas, terminal usage after result text, model or cache-specific fields, and a failed or interrupted turn. Record whether the usage arrives in the same response, a terminal event, or a separately correlated lookup. Evaluate alternate API-key routes separately when their accounting or entitlements differ from the actual headless harness.

Deliver the smallest callable contract and a pass, unsupported, or inconclusive result per provider and route. Preserve the original provider units and evidence basis.
