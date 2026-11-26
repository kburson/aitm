---
schema: "aitm.story/v0"
id: 469
title: "Extend pinned effort pricing to the Claude models used for reviews"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/469"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-26T15:04:26Z"
updated: "2026-11-26T15:06:19.931Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Extend pinned effort pricing to the Claude models used for reviews

## Outcome

Extend the shipped pinned story effort report beyond Codex GPT-6.2 Sol Standard, starting with the Claude model and pricing tier actually used in AITM reviews. Keep the pricing basis and coverage explicit across providers.

## Acceptance

- Pin reviewed rate inputs, source date, model and tier, and use exact native request counters for the chosen Claude route, including applicable cache read and write categories. Qualify only the measured model and rate basis.
- Keep Claude and Codex API-equivalent estimates distinct from Grok's provider-reported amounts and verified billed spend. Preserve measured but unpriced usage and identify incomplete coverage.
- Prove a mixed-provider report with sanitized native receipts. Reopen existing Sol artifacts byte-for-byte and show that late observations or repricing produce a new pinned artifact. Verify compatible producer output for the agreed Core fixture and obtain independent review.

Live Core receiver qualification stays in #230. Provider billing reconciliation and broad model catalog coverage are outside scope.

[Pinned reports #458](https://github.com/kburson/aitm/issues/458) · [Core export #459](https://github.com/kburson/aitm/issues/459) · [Superseded epic #100](https://github.com/kburson/aitm/issues/100)
