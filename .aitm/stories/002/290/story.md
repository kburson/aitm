---
schema: "aitm.story/v0"
id: 290
title: "[#133] Benchmark full-suite execution above 3,000 tests"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/290"
parent: 133
children: []
blocking: [293]
blocked-by: [148, 285, 289]
created: "2026-11-14T13:09:51Z"
updated: "2026-11-15T13:15:52Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-15-290-full-suite-benchmark-plan.md", "plan/benchmark.py", "plan/check-workload.py", "plan/workload.json", "plan/check-path-layout.py", "plan/path-layout-control.log", "plan/first-layout-diagnostics.md", "plan/first-layout.log", "plan/first-layout-affected.txt", "plan/first-layout-focused-serial.log", "plan/2026-11-15-290-isolated-worker-checkpoint.md", "plan/isolated-workers-3-cold.json", "plan/isolated-workers-3-warm.json", "plan/second-layout-projected.log", "plan/first-worker-ancestor-events.jsonl", "plan/2026-11-15-290-benchmark-results.md", "plan/benchmark-review.md", "plan/benchmark-readout.json", "plan/benchmark-evidence.zip", "plan/exact-source-check.json", "plan/replay-native-coverage.py", "plan/exact-source-check.py", "plan/readout.py", "plan/pack-evidence.py", "plan/report.py", "plan/reproduce.md", "plan/delivery.json", "plan/closure-receipt.json"], "attachments": []}
expansions: []
trips: []
---

# [#133] Benchmark full-suite execution above 3,000 tests

Parent #133. Rank 120.

Benchmark the full reference above 3,000 with representative workload composition, first comparing private parallel workers and then duration-balanced hosted shards if helpful. Reconcile exact inventory, outcomes, coverage and required native children. Publish cold/warm timing and queue costs.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Benchmark plan

[Measurement plan](plan/2026-11-15-290-full-suite-benchmark-plan.md) pins the source, workload composition and evidence required for comparison.

## Benchmark implementation and layout diagnostics

[Harness](plan/benchmark.py) · [Fixed workload](plan/workload.json) · [First-layout diagnosis and retained trace](plan/first-layout-diagnostics.md). The corrected isolated matrix is running.

## Isolated worker checkpoint

[Measured cold and warm worker runs](plan/2026-11-15-290-isolated-worker-checkpoint.md) passed all assignments. Serial reference and final comparison are in progress.

## Reviewed benchmark result

[Measured comparison](plan/2026-11-15-290-benchmark-results.md) · [Exact readout](plan/benchmark-readout.json) · [Retained evidence](plan/benchmark-evidence.zip) · [Signed independent review](plan/benchmark-review.md) · [Reproduction](plan/reproduce.md).

Three local workers measured a 2.64× speedup across the two layouts on the 3,020-assignment projected workload. All test phases and native child evidence reconciled. Hosted fast-path qualification remains work for #293.

## Closure

[Verified closure receipt](plan/closure-receipt.json).
