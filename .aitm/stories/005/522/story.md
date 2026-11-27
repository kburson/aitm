---
schema: "aitm.story/v0"
id: 522
title: "[Epic] M7 History import and validated corpus"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/522"
parent: 1
children: []
blocking: [523]
blocked-by: [72, 525]
created: "2026-11-27T05:59:07Z"
updated: "2026-11-27T06:20:53.280Z"
last-branch: "planning"
estimate: {"agent-hours": 18.5, "size": "Feature", "scope": "milestone refinement forecast"}
priority: null
origin: ".aitm/drafts/2026-11/20261108-1310-history-import"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/history-import-design.md"], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] M7 History import and validated corpus

[#522](https://github.com/kburson/aitm/issues/522) · Parent [#1](../../000/1/story.md) · Backlog

## Scope

Import and validate the legacy history corpus using a released Core data and reader contract. Hand off the sealed corpus to [#523](https://github.com/kburson/aitm/issues/523). The rubric is a consumer of the export.

## Prerequisites

Native blockers: [#72](https://github.com/kburson/aitm/issues/72), [#525](https://github.com/kburson/aitm/issues/525).

Source access is gated on the qualified read-only adapter and handoff receipt from [#525](https://github.com/kburson/aitm/issues/525), under M2 [#524](https://github.com/kburson/aitm/issues/524). M7 may start once its own prerequisites are satisfied.

## Design

[Draft design](design/history-import-design.md) · [Graduated draft](draft.md) · [Native readback](../../000/1/plan/2026-11-26-m7-m8-graduation.json). Size, estimate, and bounded child decomposition remain for refinement.

## Reviewed sizing and delivery order

**Rank 260 · Feature · 18.5 implementation agent-hours.** Validated legacy corpus and handoff to #523. The provider adapter and rubric work have their own estimates. [Claude Opus 5.5 XPR](design/reviews/spec/2026-11-27-history-import-design-review-da800297e0b0c147b91cbdf5f1aad338/review-da800297e0b0c147b91cbdf5f1aad338-review-manifest.md).
