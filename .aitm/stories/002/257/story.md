---
schema: "aitm.story/v0"
id: 257
title: "[M6 V11] Qualify timing replay and board-to-view parity"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/257"
parent: 247
children: []
blocking: [260]
blocked-by: [252, 258]
created: "2026-11-12T00:33:01Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V11] Qualify timing replay and board-to-view parity

[GitHub issue #257](https://github.com/kburson/aitm/issues/257) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v11-257)

Proposed implementation estimate **3.5 agent-hours**. Internal predecessors: #252, #258.

Supported timing scope from #229 (native) or #228 (legacy), plus M2 field/readback contract. Declare supported path at JIT; an unselected path remains explicitly unsupported.

## Acceptance criteria

- [ ] Compare direct, descendant and inclusive Actual and wait/elapsed scope against the same pinned approved view and verified board values. Include #227 shared fixtures and #139 pilot as preserved historical inputs.
- [ ] Verify independent timing freshness when usage is absent, scoped unsupported evidence, exact decimal board rounding and live authorized readback. Keep pricing outside timing parity.
- [ ] Prove stable pinned replay and document differences attributable to scope or watermark.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
