---
schema: "aitm.story/v0"
id: 253
title: "[M6 V06] Show workflow flow history"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/253"
parent: 247
children: []
blocking: [256]
blocked-by: [251]
created: "2026-11-12T00:32:58Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V06] Show workflow flow history

[GitHub issue #253](https://github.com/kburson/aitm/issues/253) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v06-253)

Proposed implementation estimate **3 agent-hours**. Internal predecessors: #251.

Released workflow and event export with pinned source scope.

## Acceptance criteria

- [ ] Show cumulative flow, cycle time per state, lead time, transition paths and loopbacks for the selected project and period.
- [ ] Distinguish open intervals, phase changes, rework, missing events and scope exclusions. Do not infer duration or state from unverified timing.
- [ ] Prove deterministic ordering, open and completed paths, multiple attempts, empty results and missing history.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
