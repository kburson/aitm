---
schema: "aitm.story/v0"
id: 148
title: "[#133 T11] Plan isolated test shards"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/148"
parent: 133
children: []
blocking: [149]
blocked-by: [139]
created: "2026-11-10T16:51:21Z"
updated: "2026-11-12T20:02:44Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T11", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "a63010c5e5b2d73b9b5ef11e15a214424c179c411dab425172f63cb11f4fe1db"}
---

# [#133 T11] Plan isolated test shards

[GitHub issue #148](https://github.com/kburson/aitm/issues/148) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L336)

**Required predecessor** [T02 #139](../139/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T11. Assign isolated test shards — 3h, P2, T02/T08

**Owns** `tools/ci/tia/shards.py`, `test_tia_shards.py`.
**Interface** `assign(collection, inventory, selection, durations, limits) -> ShardPlan`.

- [ ] `test_balancing_keeps_isolation_group` keeps APFS and process
  groups intact, deterministically places ties, and verifies a
  disjoint exact union by package, lane and platform.
- [ ] Assign only compatible groups; an absent required runner holds
  the gate. Start with a maximum of two independent jobs per package
  and lane as an experimental setting. T35 owns retuning from
  observed queue and setup costs. V(shards)
  passes for unknown durations, zero selection and reruns.

## Current scope

Deliver advisory shard assignments from the supplied versioned T02 inventory and exact keys. Validate lanes and isolation groups, and prove a stable, exact disjoint union. [Current replan](../133/plan/2026-11-12-133-advisory-and-qualification-replan.md).
