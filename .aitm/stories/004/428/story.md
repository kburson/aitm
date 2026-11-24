---
schema: "aitm.story/v0"
id: 428
title: "[Spike] Retrieve cost later for an explicitly named session"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/428"
parent: 426
children: []
blocking: [429]
blocked-by: [427]
created: "2026-11-24T15:08:22Z"
updated: "2026-11-24T15:41:04Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/retrospective-results.md", "attachments/retrospective-receipt.json", "attachments/independent-evidence-review.md"]}
expansions: []
trips: []
---

# [Spike] Retrieve cost later for an explicitly named session

[GitHub issue #428](https://github.com/kburson/aitm/issues/428)

Research parent: #426.

Start after #427 has recorded its findings.

## Question

Can the orchestrator retrieve usage for an exact existing or closed session later without enrolling it first or keeping a process running?

## Experiment

Use independently bounded sessions with unrelated work outside the target interval. After completion, try documented session fetch, export, or history interfaces. If needed, test a one-shot lookup of evidence for the exact native session identity, without root discovery or polling. Compare immediate and delayed retrieval, including after resume, and test that an ambiguous identity yields a gap. Determine whether the evidence resolves a turn, a marked interval, or only a session total, and which retention or permissions apply.

Deliver replayable evidence and a matrix of what survives, how long it was observed to survive, and whether it can be mapped to an authenticated story boundary.

## Results

[Findings](attachments/retrospective-results.md) · [Sanitized receipt](attachments/retrospective-receipt.json) · [Independent evidence review](attachments/independent-evidence-review.md). · [Sign-off](retro/sign-off.md).
