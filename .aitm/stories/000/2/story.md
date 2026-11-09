---
schema: aitm.story/v0
id: 2
title: "[Epic] aitm-core: story store, state machine, CLI, extension API"
kind: epic
state: backlog
issue: https://github.com/kburson/aitm/issues/2
parent: 1
children: []
blocking: []
blocked-by: []
created: 2026-11-08T19:24:20Z
updated: 2026-11-09T06:37:02Z
last-branch: planning
last-worktree: /Users/kpburson/projects/aitm-workspace/planning
estimate: { agent-hours: 180, size: XL }
priority: P1
original-estimate: { agent-hours: 180, size: XL, priority: P1, source: refinement.md }
origin: .aitm/drafts/2026-11/20261108-1310-core
files:
  draft: draft.md
  events: events.jsonl
  design: [design/core-design.md]
  plan: []
  attachments: []
expansions: []
trips: []
---

# [Epic] aitm-core: story store, state machine, CLI, extension API

**GitHub issue:** [kburson/aitm#2](https://github.com/kburson/aitm/issues/2)

## User story

As a developer running agents on stories
I want a core that stores every story's records on the `planning` branch and walks stories through the state machine
So that state, timing and evidence are recorded by the tool, never repaired by hand

## Scope

`aitm-core`: the `.aitm/` story store (ideas, drafts, stories), git-plumbing writes to `planning`, the rebuildable SQLite index, the state machine (entry guards, resident actions, exit guards), the one-expansion limit and trip rule, advisory and enforce modes, the `aitm` CLI, the extension API, and the git-host and backlog provider interfaces. GitHub itself lives in a separate extension.

## Metadata

- **Origin:** [`draft.md`](draft.md), from the master brainstorm [`../1/draft.md`](../1/draft.md)
- **Created:** 2026-11-08

## Dependencies

- **Parent:** [#1](../1/story.md) · **Blocking:** none · **Blocked by:** none

<details><summary>State history (generated from events.jsonl)</summary>

```json
[
  { "ts": "2026-11-08T19:24:20Z", "state": "backlog", "from": null }
]
```

</details>

## Refinement

Initial Refine estimate: **180 implementation agent-hours**, **XL epic**, **P1**. [Rationale and provenance](refinement.md). Plan decomposition and review are being prepared under the scoped owner assignment; historical Backlog state is retained until supported reconciliation. No implementation is authorized.
