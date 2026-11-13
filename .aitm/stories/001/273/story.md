---
schema: "aitm.story/v0"
id: 273
title: "[#270 C] Verify Claude admission across restart and refusal cases"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/273"
parent: 270
children: []
blocking: [270]
blocked-by: [272]
created: "2026-11-13T04:32:21Z"
updated: "2026-11-13T04:32:21Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/270/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#270 C] Verify Claude admission across restart and refusal cases

[GitHub #273](https://github.com/kburson/aitm/issues/273) · [#270](../270/story.md)

Project 24 Rank 228.953.

Third slice of #270 under Epic #100. After independently accepted and delivered admission, verify both original owner and exact physical spans under reopen and restart. Test missing, foreign, extra, duplicated, replaced and ineligible sources, later append, recovery, permission change, scope handoff and partial failure without weakening the capture or scope rules. Preserve fail-closed behavior and ordinary diagnostics. No folded journal intent or project ACK. #204 owns the atomic intent and continues to block #119. Epic #2, C01 and production cutover are excluded.
