---
schema: "aitm.story/v0"
id: 251
title: "[M6 V04] Show story progress, hierarchy and detail"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/251"
parent: 247
children: []
blocking: [252, 253, 254, 255]
blocked-by: [250]
created: "2026-11-12T00:32:57Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V04] Show story progress, hierarchy and detail

[GitHub issue #251](https://github.com/kburson/aitm/issues/251) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v04-251)

Proposed implementation estimate **3.5 agent-hours**. Internal predecessors: #250.

Released Core story and hierarchy export through V03.

## Acceptance criteria

- [ ] Render progress, state and parent/child navigation from the exported story graph. Support project/epic, lifecycle and coverage filters.
- [ ] Use an explicit empty, partial, orphaned or held view when ancestry or source evidence is missing. Filter and navigate consistently at desktop and narrow widths.
- [ ] Prove linked story identity, no leakage through excluded descendants, readable details, accessible keyboard navigation and no state changes from the viewer.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
