---
schema: "aitm.story/v0"
id: 426
title: "[Research Epic] Session-scoped agent cost for story runs"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/426"
parent: null
children: [427, 428, 429, 430, 431]
blocking: []
blocked-by: []
created: "2026-11-24T15:08:19Z"
updated: "2026-11-24T15:08:34Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Research Epic] Session-scoped agent cost for story runs

[GitHub issue #426](https://github.com/kburson/aitm/issues/426)

## Research question

Which tactics let AITM measure agent usage and cost for an assigned story run, including the orchestrator's own work and each headless XPR reviewer turn, without a persistent host monitor?

Related to [Epic #100](../../001/100/story.md). This is a separate top-level research epic. Its findings inform a later decision on #100.

## Experiment rules

Use disposable, bounded workloads on Codex, Claude Code, and Grok Build. Record exact harness, version, surface, authentication/billing mode, session and turn boundaries, supported fields, and evidence provenance. Use the actual XPR headless route for cross-provider probes. Keep raw traces private and retain sanitized receipts. Distinguish measured tokens or credits, provider-reported charges, API-equivalent estimates, and gaps. Record each tactic as demonstrated, unsupported, or inconclusive for each tested surface.

Run the spikes in order, one at a time. Close each with evidence and hand forward the limits and unanswered questions. A negative result still completes a spike when the tested boundary and evidence are clear. Use only the session in scope and disposable helpers that exit with the experiment.

## Research exit

Compare the tactics on existing-chat support, autonomous assignment, own-orchestrator coverage, per-turn XPR fidelity, delayed recovery, billing comparability, permissions, and maintenance burden. Recommend the smallest evidence-supported strategy and quantify its gaps. Present the options and recommendation for a decision before changing the delivery plan in #100.

## Investigation ladder

1. #427 Measure the orchestrator from its existing interactive chat
2. #428 Retrieve cost later for an explicitly named session
3. #429 Measure usage from an orchestrator-launched headless run
4. #430 Qualify a callable result-and-usage turn for each XPR provider
5. #431 Deliver a usage receipt with every headless XPR turn
