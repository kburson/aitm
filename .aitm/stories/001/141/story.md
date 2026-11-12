---
schema: "aitm.story/v0"
id: 141
title: "[#133 T04] Derive Python and package edges"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/141"
parent: 133
children: []
blocking: [142]
blocked-by: [139, 140]
created: "2026-11-10T16:51:04Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T04", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "8834c6ab0466869c48e118e34b3064ff1ef86a362aaecc5e4db66a6f6c0b6165"}
---

# [#133 T04] Derive Python and package edges

[GitHub issue #141](https://github.com/kburson/aitm/issues/141) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217)

**Required predecessors** [T02 #139](../139/story.md), [T03 #140](../140/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T04. Derive Python and package edges — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/python_graph.py`, `test_tia_python_graph.py`.
**Interface** `build_graph(snapshot, provider_policy) -> Graph` with
directed consumer/input edges and unresolved scope records.

- [ ] `test_import_alias_relative_reexport_cycle` preserves exact
  edges through initializers and module owners. `test_dynamic_scope`
  records unknown readers and package reachability.
- [ ] Resolve static imports with Python AST and trusted package-root
  mapping. Include pytest fixture and configuration scopes from
  qualified inputs. V(python_graph) passes. Neither a cycle nor an
  ambiguous namespace package silently drops a potential edge.

## Wave 3 refinement draft

Rank 30. The required predecessors are Closed as completed and marked Done. [Refinement draft](plan/2026-11-11-141-refinement-draft.md).
