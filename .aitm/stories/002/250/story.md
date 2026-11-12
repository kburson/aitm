---
schema: "aitm.story/v0"
id: 250
title: "[M6 V03] Consume released Core exports and serve the local viewer"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/250"
parent: 247
children: []
blocking: [251]
blocked-by: []
created: "2026-11-12T00:32:56Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V03] Consume released Core exports and serve the local viewer

[GitHub issue #250](https://github.com/kburson/aitm/issues/250) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v03-250)

Proposed implementation estimate **3.75 agent-hours**. Internal predecessors: None within M6.

M1 released Core #72, versioned index/read/export contracts and installed consumer support.

## Acceptance criteria

- [ ] Pin a released Core export, generate TypeScript types from its JSON Schema and test supported/unsupported versions and malformed input.
- [ ] Read one consistent local index snapshot through the supported interface. Package a static viewer shell and expose a loopback-only local entry point through the released extension API without Node at runtime.
- [ ] Verify a clean install, schema mismatch and missing data failures, local origin isolation, and reproducible export by pin. Establish viewer build checks required by repository policy before product TypeScript delivery.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
