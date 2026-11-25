---
schema: "aitm.story/v0"
id: 436
title: "Portable receipt schema and transactional store"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/436"
parent: 435
children: []
blocking: [437, 438]
blocked-by: []
created: "2026-11-25T03:17:19Z"
updated: "2026-11-25T03:26:40Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Portable receipt schema and transactional store

[GitHub #436](https://github.com/kburson/aitm/issues/436) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Version strict portable receipt and enrollment types. Persist immutable attempts and exact evidence, idempotent replay, pending delivery, valid revision refinement, and conflict isolation. Verify restart, concurrent replay, and rollback.

## Initial implementation

The initial work is scoped to the portable Python API and local project state. Provider capture, user-facing commands, and release qualification are follow-on stories.

## Draft implementation

[PR #446](https://github.com/kburson/aitm/pull/446) covers #436 and #437. The initial Python API passed 20 focused tests on macOS and Linux. The PR is open as a draft.
