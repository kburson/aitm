---
schema: "aitm.story/v0"
id: 161
title: "[#133 T24] Validate repair on a broken base"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/161"
parent: 133
children: []
blocking: [162]
blocked-by: [159, 160]
created: "2026-11-10T16:51:52Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T24", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "4e6ac4d604c166701f8976490c9399e46a7df8e52991ee9876895f30eb0705ec"}
---

# [#133 T24] Validate repair on a broken base

[GitHub issue #161](https://github.com/kburson/aitm/issues/161) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L566)

**Required predecessors** [T22 #159](../159/story.md), [T23 #160](../160/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T24. Validate repair on a broken base — 4h, P1, T22/T23

**Owns** `tools/ci/tia/repair.py`, `.github/workflows/tia-repair.yml`,
`test_tia_repair.py`.
**Interface** `verify_repair(candidate, incident, reference) -> FullProof`.

- [ ] `test_broken_base_setup_and_full_candidate` pins the base
  failure, records reference inventory at its actual revision,
  and refuses a selected-only or partial two-failure repair.
- [ ] Run an independently qualified trusted full candidate route
  when base controls cannot run, using T23's qualified route and
  T10's ordered reference dispositions. Permit only incident-accounted
  base-side gaps, preserve candidate floors and independent
  disposition for gate changes. V(repair) and the isolated broken
  lock/setup case pass.
