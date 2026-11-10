---
schema: "aitm.story/v0"
id: 145
title: "[#133 T08] Implement qualified complete collection"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/145"
parent: 133
children: []
blocking: [146, 148]
blocked-by: [144]
created: "2026-11-10T16:51:15Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T08", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "d70d4c13f5b61e3affb2df4501b17e9bb51aa310b55ada6d1bbee78bcfe22707"}
---

# [#133 T08] Implement qualified complete collection

[GitHub issue #145](https://github.com/kburson/aitm/issues/145) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L291)

**Required predecessors** [T07 #144](../144/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T08. Implement qualified complete collection — 4h, P1, T07

**Owns** `tools/ci/tia/collect.py`, `test_tia_collect.py` and the
qualified T07 collection adapter.
**Interface** `collect(candidate, control_identity, runner_identity) -> CollectionProof`.

- [ ] `test_new_candidate_id_cannot_be_hidden_before_assignment`
  exercises deletion of a newly discovered case even when the base
  inventory still matches. Reject when completeness is unprovable.
- [ ] Establish the complete collection before creating assignments.
  Use T07's isolated mechanism. Bind exact candidate, qualified
  observer, controls and platform. V(collect) and the hosted attack
  fixture pass independently of how many IDs later execute.
