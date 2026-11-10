---
schema: "aitm.story/v0"
id: 167
title: "[#133 T30] Bridge governed Claude operations"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/167"
parent: 133
children: []
blocking: [169]
blocked-by: [166]
created: "2026-11-10T16:52:06Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T30", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "bd6d0c4224a93b202a145a3607a32712ed3ff68756d39b7a08eeb196e5efe091"}
---

# [#133 T30] Bridge governed Claude operations

[GitHub issue #167](https://github.com/kburson/aitm/issues/167) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L661)

**Required predecessors** [T29 #166](../166/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T30. Bridge governed Claude operations — 3.5h, P1, T29

**Owns** `tools/ci/tia/harness_claude.py`, `test_tia_harness_claude.py`
and the isolated Claude qualification carrier.
**Interface** `adapt_claude(event, enrollment) -> GuardRequest`.

- [ ] `test_claude_enrolled_hooks_deny_expired_lease` exercises
  pickup, resume, stop notification and governed mutations on the
  T28-qualified Claude Code surface, reusing T29's decision contract.
- [ ] Rehearse connected and disconnected Claude sessions and
  verify read-only and authorized incident actions. V(harness_claude)
  and native Claude evidence pass. Further admitted harnesses require
  separate equivalent qualification before enrollment.
