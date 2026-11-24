---
schema: "aitm.story/v0"
id: 430
title: "[Spike] Qualify a callable result-and-usage turn for each XPR provider"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/430"
parent: 426
children: []
blocking: [431]
blocked-by: [429]
created: "2026-11-24T15:08:28Z"
updated: "2026-11-24T20:18:48Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/xpr-turn-results.md", "attachments/xpr-turn-receipt.json", "attachments/independent-evidence-review.md"]}
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

## Additional controls from #426

- Exercise the actual native headless XPR route and record version, surface, authentication and billing mode. Use a small route adapter and treat an API-key alternative as a separate evidence row.
- For two turns sharing one reviewer session, verify the native identity of each result and its usage. Test a result that appears before usage, then correlate a terminal event or exact lookup without requesting another model turn. Reconcile cumulative counters where applicable and disclose any aggregation that cannot be split safely.
- Preserve native units, cache categories, and whether the usage includes nested work. Distinguish measured usage, provider-reported cost indicators or verified charges, API-equivalent estimates, and pending or unavailable evidence. Record the smallest per-route capture contract and its coverage boundaries.

## Results

[Research findings](attachments/xpr-turn-results.md) · [Sanitized receipt](attachments/xpr-turn-receipt.json) · [Independent evidence review](attachments/independent-evidence-review.md).
