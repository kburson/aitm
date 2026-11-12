---
schema: "aitm.story/v0"
id: 249
title: "[M6 V01] Build the pinned read-only preview data"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/249"
parent: 247
children: []
blocking: [248]
blocked-by: []
created: "2026-11-12T00:32:55Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V01] Build the pinned read-only preview data

[GitHub issue #249](https://github.com/kburson/aitm/issues/249) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v01-249)

Proposed implementation estimate **3 agent-hours**. Internal predecessors: None within M6.

Formal M6 after M1 release #72. An early bootstrap requires separately recorded sequencing authorization at pickup.

## Acceptance criteria

- [ ] Rebuild from the exact Git planning pin and cutoff with the shipped reader. Verify snapshot and validation bytes and produce a versioned allowlisted view with source and build provenance.
- [ ] Map Unknown, Partial, verified zero, empty reasons, and source admission. Enforce visibility profile, approved values, restricted descendant rollups, and pricing basis. Record evidence through separately from last verified.
- [ ] Trust only pinned operator verification blobs bound to the exact metric, scope and digest. Reproduce the single #139 1,208 ms contribution and exact Actual and working wall verification timestamps. Preserve each source value, coverage, reason and evidence-through time, and leave last verified null without matching verification. Report #209 only in the input audit. Reject forged, transplanted or future evidence.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
