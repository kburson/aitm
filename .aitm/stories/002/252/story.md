---
schema: "aitm.story/v0"
id: 252
title: "[M6 V05] Show timing, Cost and evidence coverage in the local viewer"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/252"
parent: 247
children: []
blocking: [256, 257, 259]
blocked-by: [248, 251]
created: "2026-11-12T00:32:57Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V05] Show timing, Cost and evidence coverage in the local viewer

[GitHub issue #252](https://github.com/kburson/aitm/issues/252) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v05-252)

Proposed implementation estimate **3.75 agent-hours**. Internal predecessors: #248, #251.

The UI can be qualified with safe fixtures and unavailable states. Live timing and Cost are qualified by V11 and V12.

## Acceptance criteria

- [ ] Present Actual, elapsed, owner wait, working wall time, direct/descendant totals and Cost with independent value, coverage, reason, basis and source/verification times.
- [ ] Own the versioned approved metric view over the released Core export. Produce the same pinned metric payload for the local viewer, hosted build and M2 readback comparison, with independent timing and usage watermarks. Preserve the preview semantics without introducing a second timing or pricing fold. Show Unknown, supported Partial and verified zero, and label pricing basis.
- [ ] Prove parallel actors, in-turn tools, scope changes, missing usage, stale evidence and exact estimate scope. Keep Partial or Unknown outside calibration.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
