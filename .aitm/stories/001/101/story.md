---
schema: "aitm.story/v0"
id: 101
title: "[Spike] Validate Grok Build CLI usage and scope evidence"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/101"
parent: null
children: []
blocking: [100]
blocked-by: []
created: "2026-11-10T00:36:15Z"
updated: "2026-11-10T00:42:05Z"
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

## Partial evidence

[Retained evidence report](attachments/report.md). The current Grok Build CLI sign-in was rejected before any model turn. Retained usage and native completion metadata corroborate a candidate whole-turn source and prompt lineage. The controlled two-story park and resume test is pending a refreshed sign-in.
