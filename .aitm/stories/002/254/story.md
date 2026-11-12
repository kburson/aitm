---
schema: "aitm.story/v0"
id: 254
title: "[M6 V07] Show evidence summaries, bumps and retrospectives"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/254"
parent: 247
children: []
blocking: [256]
blocked-by: [251]
created: "2026-11-12T00:32:59Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.25, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V07] Show evidence summaries, bumps and retrospectives

[GitHub issue #254](https://github.com/kburson/aitm/issues/254) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v07-254)

Proposed implementation estimate **3.25 agent-hours**. Internal predecessors: #251.

Released safe document and outcome references; display missing or unapproved content as such.

## Acceptance criteria

- [ ] Expose sourced design and plan summaries, fixed links to the approved full design and plan documents, bumps, lessons, retrospectives and advisory confidence from supported read-only exports.
- [ ] Use approved summary values and fixed provenance links, enforce visibility scope and handle unapproved or absent material without exposing private content.
- [ ] Test hostile or unavailable document inputs, revision provenance, current versus historical artifacts and accessible disclosure.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
