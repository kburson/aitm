---
schema: "aitm.story/v0"
id: 282
title: "[Spike] Measure Claude subagent telemetry coverage and story impact"
kind: "spike"
state: "refine"
issue: "https://github.com/kburson/aitm/issues/282"
parent: 100
children: []
blocking: []
blocked-by: []
created: "2026-11-13T11:05:01Z"
updated: "2026-11-13T11:23:28Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "M"}
priority: null
origin: ".aitm/stories/001/204/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-13-119-qualified-sources-reacceptance-draft.md"], "attachments": []}
expansions: []
trips: []
---

# [Spike] Measure Claude subagent telemetry coverage and story impact

[GitHub #282](https://github.com/kburson/aitm/issues/282) · [Epic #100](../100/story.md)

Project 24 Rank 229.5. This evidence spike has no native blocker edges.

## Epic #100 evidence spike

Determine how often Claude Code Agent subagents affect per-story measurement and whether native OpenTelemetry can independently corroborate request membership and usage for #204. Start from the controlled macOS 2.1.318 feasibility run. It matched five unique provider requests to the native transcripts, including both child requests. The synthetic cost share is a proof of measurement feasibility. It is not an estimate of production prevalence.

- Use a small, defined sample of already approved AITM project sources and story windows. Read only metadata and counters needed for the study. Retain keyed IDs and sanitized aggregates. Record observed sessions, prompts and stories containing the affected pattern, eligible requests and verified overlap. Publish sample dates, denominators, missing data and how representative the sample is.
- Measure affected share separately for request count, token categories and estimated API cost. Keep active time and story progress coverage separate. If the affected share can only be estimated at prompt or project level, do not allocate it to stories. Report unknown when a reliable denominator is unavailable.
- In a disposable local capture, test whether Claude's native telemetry can be joined to distinct provider requests and the exact child and parent without prompt or tool text. Compare a direct turn and a foreground Agent turn. Test duplicate delivery, dropped telemetry and restart. Treat telemetry as corroboration. It does not establish original project ownership, capture permission, or a qualifying pre-request boundary on its own.
- Limit the study to two active agent-hours before disposition. Return whether the result justifies a separate qualification design and give a quantitative answer for the sampled workload. Never apply a correction multiplier to the ledger.

Evidence only. No dependency, capture, reporting, or production changes. Epic #2, C01 and production cutover are excluded.

## Initial feasibility result

Claude 2.1.318 sent five distinct API request events to a local receiver in one synthetic session. All five joined the corresponding native transcript usage by server request identity. Both child requests carried the same child agent ID and shared their parent prompt ID. The child contributed 47.2% of estimated API cost within the one Agent prompt, with the tool-free control excluded from the denominator. This sample cannot estimate project or story prevalence. No report or ownership authority was issued. [Sanitized receipt](plan/claude-otel-feasibility.json).

The separate [qualified-source release draft](plan/2026-11-13-119-qualified-sources-reacceptance-draft.md) is ready for independent re-acceptance if pursued. Existing journal tests passed for nested overlap, mixed diagnostics and keeping the prior frontier on partial input. The tested package tree matches current remote trunk `b1ff8ce027608da942ec8ac1c7bc124500c5f145`. This is baseline evidence. It does not certify the replacement blocker.

[Bounded sample and replay findings](plan/2026-11-13-282-claude-otel-findings.md). [Reproduction](plan/claude-otel-reproduction.md). Actual records only bounded coordinator progress.
