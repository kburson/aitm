---
schema: "aitm.story/v0"
id: 102
title: "[Spike] Investigate Linux usage provider compatibility"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/102"
parent: null
children: []
blocking: [100]
blocked-by: []
created: "2026-11-10T00:36:15Z"
updated: "2026-11-10T00:37:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Investigate Linux usage provider compatibility

[GitHub issue #102](https://github.com/kburson/aitm/issues/102)

Research prerequisite for [#100](../100/story.md). The retained deliverable is a sanitized evidence report with exact environment and provider builds, demonstrated capabilities, explicit gaps and design or plan implications.

Inspect the available Codex CLI, Claude Code and Grok Build CLI Linux surfaces and probe Linux filesystem, file watching, locking, atomic publication and user-service requirements. Label container evidence and full user-service qualification separately.

The two spikes can run concurrently. The report is the deliverable and any probe code is disposable.
