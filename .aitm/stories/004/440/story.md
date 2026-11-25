---
schema: "aitm.story/v0"
id: 440
title: "Capture provider-reported Claude Code usage"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/440"
parent: 435
children: []
blocking: [444, 445]
blocked-by: [438]
created: "2026-11-25T03:17:28Z"
updated: "2026-11-25T03:22:27Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Capture provider-reported Claude Code usage

[GitHub #440](https://github.com/kburson/aitm/issues/440) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Normalize per-result usage, deduplicated finalized requests, cache fields and partial cancelled results. Qualify supported configured interactive and recovery routes.

## Dependencies

- #438
