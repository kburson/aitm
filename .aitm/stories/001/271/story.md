---
schema: "aitm.story/v0"
id: 271
title: "[#270 A] Qualify native Claude foreground closure"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/271"
parent: 270
children: []
blocking: [272]
blocked-by: [269]
created: "2026-11-13T04:32:19Z"
updated: "2026-11-13T04:39:19Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/270/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#270 A] Qualify native Claude foreground closure

[GitHub #271](https://github.com/kburson/aitm/issues/271) · [#270](../270/story.md)

Project 24 Rank 228.951.

Evidence-only first slice of #270 under Epic #100. Start from completed spike #269. Qualify one pinned macOS Claude Code 2.1.318 foreground Agent invocation through a monitor-owned disposable process, with a pause after normal parent warm-up, a prospective observed child prefix, a directly observed process exit, and an exact closed native file set and byte extents. Exercise missing or extra native artifacts, stale or appended prefixes, recovered or ambiguous completion, and the distinction between an observed lifecycle and eligible scope.

Retain reproducible checks and a sanitized receipt. Bound the investigation to two active agent-hours. No new capture permission, child epoch, scope route, claim, journal change or production hooks. The admission design and its independent re-acceptance follow this slice. #270 and #204 remain open. Epic #2, C01 and production cutover are excluded.

## Independent closure qualification

The independent recovery passed the controlled native closure evidence. It qualified the prospective observation and terminal file fence for the proposed admission design. It issued no ownership or child capture epoch. [Native report](plan/2026-11-12-271-claude-native-closure.md) · [Independent PASS](plan/independent-native-review.md).
