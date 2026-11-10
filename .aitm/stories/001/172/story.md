---
schema: "aitm.story/v0"
id: 172
title: "[#133 T35] Measure selection and sharding qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/172"
parent: 133
children: []
blocking: [178]
blocked-by: [143, 171]
created: "2026-11-10T16:52:18Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T35", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "9e320f703f2a576c7bc82615bdb7aca2015b3b1f3c5fbb82c3b9d56449dd51de"}
---

# [#133 T35] Measure selection and sharding qualification

[GitHub issue #172](https://github.com/kburson/aitm/issues/172) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L747)

**Required predecessors** [T06 #143](../143/story.md), [T34 #171](../171/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T35. Measure selection and sharding qualification — 3h, P2, T06/T34

**Owns** `tools/ci/tia/qualification.py`, `test_tia_qualification.py`,
and a sanitized timing and selector report.
**Interface** `summarize(episodes, profile) -> QualificationReport`.

- [ ] `test_report_requires_each_mode_window_and_lane` checks 3/6/10
  envelopes, p50/p95, no-test N/A and excluded queue, and rejects
  mixing unrelated runners or attempts.
- [ ] Apply the pinned recipe. Use T01 to forecast runner minutes before
  dispatch and return an over-cap recipe for review. Seed off-path
  defects, local drift
  and full fallback on the representative candidates. Report co-run
  contention, missed impacts and retuning separately. V(qualification)
  passes and each accepted sample has a bound run receipt.
