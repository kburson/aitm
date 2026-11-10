---
schema: "aitm.story/v0"
id: 156
title: "[#133 T19] Connect trusted scheduled evidence and freshness"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/156"
parent: 133
children: []
blocking: [157]
blocked-by: [155]
created: "2026-11-10T16:51:40Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T19", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "e8615ca7504525400a0d1cb784eeaaf9fc84ea4948d8bcbc08a4ff47e87cfbd3"}
---

# [#133 T19] Connect trusted scheduled evidence and freshness

[GitHub issue #156](https://github.com/kburson/aitm/issues/156) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L469)

**Required predecessors** [T18 #155](../155/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T19. Connect trusted scheduled evidence and freshness — 3h, P1, T18

**Owns** `tools/ci/tia/health_ingress.py`,
`test_tia_health_ingress.py`, and the disposable host's evidence
read identity. **Interface**
`refresh_host_evidence(expected, provider, now) -> HealthEvent`.

- [ ] `test_read_identity_and_missed_dispatch_hold` rejects candidate
  ingestion and records missed schedule under a scoped read-only
  hosting API identity. Refuse replay, wrong workflow or revision,
  and expired evidence.
- [ ] On the trusted host, run the independent freshness check and
  feed only T15's verified facts to the continuity-bound authority.
  V(health_ingress) and the isolated delayed/missing dispatch proof
  pass without granting merge or workspace credentials.
