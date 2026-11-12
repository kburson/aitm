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
blocked-by: [143, 171, 267]
created: "2026-11-10T16:52:18Z"
updated: "2026-11-12T20:02:44Z"
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

**Required predecessors** [T06 #143](../143/story.md), [T34 #171](../171/story.md), [T35L #267](../../002/267/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Qualification amendment

Apply the [#133 execution and selection amendment](../133/plan/2026-11-11-133-test-execution-and-advisory-selection.md).
Add the following comparisons to the existing qualification report.

- [ ] Compare the local serial reference with `pytest-xdist` using
  `max(1, floor(0.8 × available_cores))` workers for eligible Python tests.
  Record available cores, worker count, elapsed time, fixture isolation,
  test IDs and outcomes, line and branch coverage, and required child
  coverage. Exercise the one-worker floor and integer rounding.
- [ ] Run hosted shards as distinct jobs on separate ephemeral instances.
  Compare full serial, full sharded, and selected runs on the same
  candidate and compatible runner scopes. Record per-job setup and
  execution, total elapsed time, queue time, p50/p95, and runner cost.
  Preserve the 3/6/10-minute envelopes and require complete same-attempt
  inventory, outcomes, coverage, and child evidence.
- [ ] Compare `pytest-testmon` suggestions and any ordering benefit with
  the trusted selector and full-run results. Report added candidates,
  missed impacts, extra tests, cache/collection overhead, and net time
  saved. Include a Python edit, a non-code fixture or configuration
  change, and missing or incompatible history. Show that uncertain
  impact still runs the full applicable suite even when testmon suggests
  no tests. The report grants testmon no gate authority.

Use the existing #172 estimate and predecessors for planning. Recheck the
qualification recipe and estimate at refinement before dispatch. The
[#197 hold](../139/plan/delivery-checklist.md) and #159's blockers apply
independently of this qualification work.

[Local testmon advisory trial](attachments/2026-11-11-172-testmon-advisory-trial.md)
records a Python dependency cluster and a missed data-file regression.

[Parallel Python hosted qualification](attachments/2026-11-11-172-parallel-python-hosted-qualification.md)
records exact serial parity and the measured local and hosted execution times.

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

## Local advisory evidence

[#267](../../002/267/story.md) supplies local measurement evidence. #171 still gates the hosted comparison, and #178 retains this broader qualification dependency. [Current replan](../133/plan/2026-11-12-133-advisory-and-qualification-replan.md).
