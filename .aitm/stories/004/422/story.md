---
schema: "aitm.story/v0"
id: 422
title: "[Spike] Measure test automation timing, coverage, and sharding"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/422"
parent: null
children: []
blocking: [423]
blocked-by: []
created: "2026-11-23T00:30:26Z"
updated: "2026-11-23T00:32:15Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Measure test automation timing, coverage, and sharding

[GitHub issue #422](https://github.com/kburson/aitm/issues/422)

## Question

Where does test automation spend its time, what parallelism does it actually achieve, and how much wall time does sharding save with code coverage collected?

## Evidence to deliver

- Inventory automated test lanes and their operating systems, triggers, coverage configuration, and evidence sources. Include ordinary PR CI, helper tests, affected/mapped checks, and the scheduled category sweep. Flag coverage-disabled lanes and any gaps in artifact retention.
- Produce a machine-readable per-test table keyed by run attempt, lane, shard, worker, node ID, and attempt. Include setup, call, teardown, elapsed test time, and outcome. Report skips, collection errors, retries, and child processes where observable.
- Measure job and test-worker concurrency separately using observed time intervals. Report configured and observed workers, peak concurrency, overlap, aggregate worker time, and longest shard. Separate queue, bootstrap, collection, test execution, coverage processing, and artifact upload.
- Compare serial and sharded runs at the same source tree, runner class, test inventory, and coverage settings. Verify test union, outcomes, and coverage parity. Report wall-clock speedup, imbalance, and added overhead. Label existing sweep evidence separately when it uses different coverage settings.
- Preserve raw receipts and a concise results report with source SHA, run IDs and attempts, commands, coverage totals, and limitations. Hand the baseline to the TIA spike.

Use an isolated worktree and a disposable draft PR for experiments. Leave the draft unmerged.

Experiment workspace: [draft PR #424](https://github.com/kburson/aitm/pull/424).
