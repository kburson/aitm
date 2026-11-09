---
schema: "aitm.story/v0"
id: 83
title: "[Story] Capture AITM agent usage continuously during Core bootstrap"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/83"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-09T13:53:47Z"
updated: "2026-11-09T13:57:32Z"
last-branch: "planning"
estimate: {agent-hours: null, size: null}
priority: "P1"
origin: "Owner brainstorming for Core dogfooding, 2026-11-09"
files: {draft: "draft.md", events: "events.jsonl", design: [], plan: [], attachments: []}
expansions: []
trips: []
---

# [Story] Capture AITM agent usage continuously during Core bootstrap

[GitHub issue #83](https://github.com/kburson/aitm/issues/83) · [Core #2](../2/story.md) · [C44 / #51](../51/story.md) · [Measurement spike #73](../73/attachments/report.md)

As an AITM maintainer, I want collection running during normal work on this repository so brainstorming, planning, review, development, delivery and housekeeping all contribute usage evidence to the right draft, task or feature.

The initial deliverable is a running local collector, a durable ledger and a verified export. [Brainstorming proposal](draft.md). Priority P1 reflects early bootstrap value. Implementation scope and estimates follow design review. The story has no required dependency on an installed Core and is tracked separately from the accepted Core implementation leaves.
