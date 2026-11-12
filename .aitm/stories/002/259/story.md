---
schema: "aitm.story/v0"
id: 259
title: "[M6 V12] Qualify priced Cost replay and board-to-view parity"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/259"
parent: 247
children: []
blocking: [260]
blocked-by: [252, 258]
created: "2026-11-12T00:33:03Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V12] Qualify priced Cost replay and board-to-view parity

[GitHub issue #259](https://github.com/kburson/aitm/issues/259) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v12-259)

Proposed implementation estimate **3.5 agent-hours**. Internal predecessors: #252, #258.

Qualified #230, including #123/#124 and Core #51, plus M2 Cost field/readback contract and authorized scope. [The reviewed replan](../230/plan/2026-11-11-230-cost-dependency-replan.md) resolves the former completion-accounting hold. #230 now belongs to Core #2 and still waits for #51, #123 and #124.

## Acceptance criteria

- [ ] Verify the pinned pricing report, rate basis, cutoff, scope and independent usage watermark against the same approved viewer and board publication.
- [ ] Prove verified priced subtotal with Partial coverage in the viewer, held board projection for incomplete price, replay, later usage refresh, and no effect on timing.
- [ ] Retain real-data authorized readback and provenance without raw provider evidence in the hosted bundle.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
