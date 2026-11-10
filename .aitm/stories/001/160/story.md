---
schema: "aitm.story/v0"
id: 160
title: "[#133 T23] Qualify full repair outside broken base controls"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/160"
parent: 133
children: []
blocking: [161]
blocked-by: [152, 157]
created: "2026-11-10T16:51:50Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T23", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "a165a3b8b60e70b85b8f4e97f195a344286aa2054d37957335ca69d271b6a90b"}
---

# [#133 T23] Qualify full repair outside broken base controls

[GitHub issue #160](https://github.com/kburson/aitm/issues/160) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L550)

**Required predecessors** [T15 #152](../152/story.md), [T20 #157](../157/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T23. Qualify full repair outside broken base controls — 3.5h, P1, T15/T20

**Owns** disposable repair-route fixtures and capability report.
**Interface** a pinned trust/control route and full evidence receipt
or explicit refusal.

- [ ] In an approved isolated target, run a base with broken lock or
  workflow/setup and a fully passing exact repair candidate. Bootstrap
  the trusted controller from a separately pinned qualified source,
  install the exact candidate with its approved lock, and verify
  candidate coverage, native and child evidence, wheel and file checks.
- [ ] Refuse a red candidate and missing, mislabeled or unapproved
  reference inventory. Demonstrate normal independent review and
  gate-control disposition. Without this proof, hold T24 and its
  descendants. T07/T09 alone do not qualify this alternate route.
