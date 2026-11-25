---
schema: "aitm.story/v0"
id: 437
title: "Bind agent attempts to stories and link unattached work"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/437"
parent: 435
children: []
blocking: [438, 442, 444]
blocked-by: [436]
created: "2026-11-25T03:17:21Z"
updated: "2026-11-25T03:26:40Z"
last-branch: "planning"
estimate: {"agent-hours": 1.5, "size": "S"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Bind agent attempts to stories and link unattached work

[GitHub #437](https://github.com/kburson/aitm/issues/437) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Bind receipt ownership to immutable enrollment and exact provider turn identity across story changes and fresh-agent handoffs. Add one authorized late link per unattached observation. Refuse conflicting, cross-project and mixed-turn attribution.

## Dependencies

- #436

## Initial implementation

The initial work is scoped to the portable Python API and local project state. Provider capture, user-facing commands, and release qualification are follow-on stories.

## Draft implementation

[PR #446](https://github.com/kburson/aitm/pull/446) covers #436 and #437. The initial Python API passed 20 focused tests on macOS and Linux. The PR is open as a draft.
