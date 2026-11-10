---
schema: "aitm.story/v0"
id: 101
title: "[Spike] Validate Grok Build CLI usage and scope evidence"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/101"
parent: null
children: []
blocking: [100]
blocked-by: []
created: "2026-11-10T00:36:15Z"
updated: "2026-11-10T02:53:03Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/report.md"]}
expansions: []
trips: []
---

# [Spike] Validate Grok Build CLI usage and scope evidence

[GitHub issue #101](https://github.com/kburson/aitm/issues/101)

Research prerequisite for [#100](../100/story.md). The retained deliverable is a sanitized evidence report with exact environment and provider builds, demonstrated capabilities, explicit gaps and design or plan implications.

Verify native Grok Build CLI usage identity, token fields, pricing provenance, lifecycle evidence and scope boundaries with a small synthetic workload on a pinned client. Check replay, park and resume where supported.

The two spikes can run concurrently. The report is the deliverable and any probe code is disposable.

## Research result

[Published report](attachments/report.md). Grok Build CLI 1.0.77 emitted two verified native prompt boundaries and matching usage in one resumed session. The disposable scope receipts demonstrate feasibility. The production adapter must independently validate receipt authority, versioned token semantics, missing evidence, and inherited or conflicting histories. Provider-reported cost remains separate from billed spend and comparable API-equivalent estimates.

## Completion sign-off

The published report fulfills the controlled Grok research deliverable. Report SHA-256 `34a27af1e20669f5ec5bd23dc0c1424d3ba3a5750f33c7d3fd1f132b529e2164` at `989d7fedb8b1686e9bb555b7f6f713ddf9dc3cff`. GitHub readback verified Completed at `2026-11-10T02:53:00Z` and AITM-PY Backlog Done. The research demonstrates the native signal path on the tested macOS build. Production admission and Linux qualification remain delivery gates.
