---
schema: "aitm.story/v0"
id: 174
title: "[#133 T37] Rehearse merge-only holds"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/174"
parent: 133
children: []
blocking: [177]
blocked-by: [162, 170, 171]
created: "2026-11-10T16:52:23Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T37", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "d2a1cd75cb8cbaf16746b4b8ef06424c4b78a3dfa0c5ac1611d6dbefac7e4f98"}
---

# [#133 T37] Rehearse merge-only holds

[GitHub issue #174](https://github.com/kburson/aitm/issues/174) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L775)

**Required predecessors** [T25 #162](../162/story.md), [T33 #170](../170/story.md), [T34 #171](../171/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T37. Rehearse merge-only holds — 4h, P1, T25/T33/T34

**Owns** isolated coverage, skip and unavailable-evidence fixtures
and their separate receipts.
**Interface** verified merge-only hold results for T41.

- [ ] After passing selected validation in the isolated fixture,
  observe scheduled coverage-floor miss and, in a distinct run,
  an undisposed skip of an unselected test. For each, retain
  denied ordinary merge and fresh allowed ordinary work.
- [ ] Inject broken scheduled setup with no outcomes and retain
  evidence of the merge hold and permitted work. Neither a missing
  report nor a skipped case can impersonate a verified failing test.
