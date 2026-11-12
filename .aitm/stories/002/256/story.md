---
schema: "aitm.story/v0"
id: 256
title: "[M6 V09] Qualify a static hosted build with synthetic data"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/256"
parent: 247
children: []
blocking: [258]
blocked-by: [252, 253, 254, 255]
created: "2026-11-12T00:33:00Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V09] Qualify a static hosted build with synthetic data

[GitHub issue #256](https://github.com/kburson/aitm/issues/256) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v09-256)

Proposed implementation estimate **3.75 agent-hours**. Internal predecessors: #252, #253, #254, #255.

Use an explicitly authorized synthetic route at JIT. No real-data destination or hosted issue-link claim.

## Acceptance criteria

- [ ] Build the complete static viewer from a pinned safe fixture. Select and qualify a default-branch manual dispatch; evaluate recurring refresh as a separate behavior using measured latency and a declared freshness target.
- [ ] Verify that a failed, superseded or stale build retains the last valid artifact. Prove origin, manifest, browser digest, pin, visibility profile and anonymous-access behavior on the authorized synthetic route.
- [ ] Keep workflow code on trunk and distinguish viewer refresh from the separate every-push planning audit.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
