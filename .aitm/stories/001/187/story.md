---
schema: "aitm.story/v0"
id: 187
title: "[#181 A02] Resolve timing attribution and the legacy seed"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/187"
parent: 181
children: []
blocking: [188]
blocked-by: [186]
created: "2026-11-10T21:02:15Z"
updated: "2026-11-11T02:27:48Z"
last-branch: "codex/aitm-187-timing-attribution"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A02", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "451ef49534a5b97aba0fd2923b597cb190c96d664fdbad78a7cf418923c41927"}
---

# [#181 A02] Resolve timing attribution and the legacy seed

[GitHub issue #187](https://github.com/kburson/aitm/issues/187) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L64)

Required predecessors #186. The proposed estimate is 3.75 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A02. Resolve timing attribution and the legacy seed

- [ ] Test `test_stable_observation_and_seed_overlap`. Replaying identical scope and payload counts once. Two scopes or roles for one observation hold both assignments. Two different keys for the same actor concurrently attributed to different child stories hold the overlapping span in both. Nonoverlapping portions remain eligible with partial coverage. Potential legacy overlap without correspondence stays unresolved. The registered #181 v0 seed has ten story rows with typed phase, role and attempt Unknown; unregistered or digest-mismatched copies add nothing.
- [ ] Run red. Implement `resolve_timing` using stable identity independent of mutable attribution. Resolve one direct assignment per observation. Detect overlapping same-actor contributions across direct stories before the metric fold, including distinct observation keys. Hold each unresolved overlap, retaining unaffected spans and a gap for every implicated scope. Distinguish replay, conflict, unsupported and missing evidence. Treat the v0 receipt at the accepted digest as the only multi-story legacy seed. Take direct intervals from it; its rollup numbers are readback checks.
- [ ] Run green and retain tests that demonstrate double-count prevention and recovery boundaries. Proven production split/reassignment and migration use the C qualification checkpoint.

## Delivery evidence

[Accepted design, plan and JIT](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
