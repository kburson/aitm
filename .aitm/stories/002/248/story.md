---
schema: "aitm.story/v0"
id: 248
title: "[M6 V02] Render and qualify the downloadable preview bundle"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/248"
parent: 247
children: []
blocking: [252]
blocked-by: [249]
created: "2026-11-12T00:32:54Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V02] Render and qualify the downloadable preview bundle

[GitHub issue #248](https://github.com/kburson/aitm/issues/248) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v02-248)

Proposed implementation estimate **3 agent-hours**. Internal predecessors: #249.

Same sequencing as V01. Local and downloadable preview only.

## Acceptance criteria

- [ ] Render sanitized JSON and standalone HTML from the same approved object. Show primary and detailed reasons, evidence-through UTC, last verified UTC, publication time, pin, pending waits and staleness.
- [ ] Validate an atomic content-addressed bundle and serialized last-valid pointer. Cover reversed completion, stale lineage/cutoff, incomparable scope profiles, partial writes, replay and prior bundle retention.
- [ ] Rebuild the pinned #139 before/after and synthetic fixtures. Verify browser pin and manifest digest separately, check redaction canaries across outputs and diagnostics, and preserve make dashboard.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
