---
schema: "aitm.story/v0"
id: 429
title: "[Spike] Measure usage from an orchestrator-launched headless run"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/429"
parent: 426
children: []
blocking: [430]
blocked-by: [428]
created: "2026-11-24T15:08:25Z"
updated: "2026-11-24T15:10:03Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Measure usage from an orchestrator-launched headless run

[GitHub issue #429](https://github.com/kburson/aitm/issues/429)

Research parent: #426.

Start after #428 has recorded its findings.

## Question

What extra cost evidence does launching a headless worker provide, and is headless launch necessary to get the measurements the interactive tactics could not obtain?

## Experiment

Launch one explicitly enrolled, disposable worker per harness. Capture the supported terminal or streaming result for that process, using a bounded wrapper that exits with the run. Compare with the interactive and retrospective evidence. Exercise a fresh run, resume, and one interrupted run. Distinguish turn deltas from cumulative totals and explain changes in billing or entitlements when the launch route differs. Verify that retries and resumes do not charge the same work twice. Treat this as process-level capture and leave turn API qualification to the next spike.

Deliver a three-provider comparison plus the minimum launch and capture mechanism for each demonstrated path.
