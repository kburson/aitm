---
schema: "aitm.story/v0"
id: 429
title: "[Spike] Measure usage from an orchestrator-launched headless run"
kind: "spike"
state: "review"
issue: "https://github.com/kburson/aitm/issues/429"
parent: 426
children: []
blocking: [430]
blocked-by: [428, 432]
created: "2026-11-24T15:08:25Z"
updated: "2026-11-24T20:01:57Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/headless-results.md", "attachments/headless-receipt.json", "attachments/independent-evidence-review.md"]}
expansions: []
trips: []
---

# [Spike] Measure usage from an orchestrator-launched headless run

[GitHub issue #429](https://github.com/kburson/aitm/issues/429)

Research parent: #426.

Start after #428 and #432 have recorded their findings.

## Question

What extra cost evidence does launching a headless worker provide, and is headless launch necessary to get the measurements the interactive tactics could not obtain?

## Experiment

Launch one explicitly enrolled, disposable worker per harness. Capture the supported terminal or streaming result for that process, using a bounded wrapper that exits with the run. Compare with the interactive and retrospective evidence. Exercise a fresh run, resume, and one interrupted run. Distinguish turn deltas from cumulative totals and explain changes in billing or entitlements when the launch route differs. Verify that retries and resumes do not charge the same work twice. Treat this as process-level capture and leave turn API qualification to the next spike.

Deliver a three-provider comparison plus the minimum launch and capture mechanism for each demonstrated path.

## Additional controls from #426

- Keep each worker on the provider's native harness and its supported authentication route. Use a bounded launch/capture adapter that exits with the run. Compare structured terminal output, a terminal event, and a one-shot exact lookup where available. Record the measured gain over #427–#428 and the gap that remains.
- Record assignment identity before launch, provider session identity and resume boundaries. Capture which quantities are cumulative, direct-only, or inclusive of child work. Retain native token and cache categories and provider cost units. Report missing fields and differences in subscription versus API entitlements explicitly.
- Compare a replayed capture of the same execution with an actual retry. Retain separately evidenced usage from interrupted and retried execution and count each native observation once. Keep this probe at process scope and hand turn-level questions to #430.

## Results

[Research findings](attachments/headless-results.md) · [Sanitized receipt](attachments/headless-receipt.json) · [Independent evidence review](attachments/independent-evidence-review.md).
