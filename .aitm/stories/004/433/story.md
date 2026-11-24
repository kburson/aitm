---
schema: "aitm.story/v0"
id: 433
title: "[Spike] Measure usage and time across epic trails"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/433"
parent: 426
children: []
blocking: []
blocked-by: [431]
created: "2026-11-24T19:20:11Z"
updated: "2026-11-24T21:55:51Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/epic-trail-results.md", "attachments/epic-trail-receipt.json", "attachments/independent-evidence-review.md"]}
expansions: []
trips: []
---

# [Spike] Measure usage and time across epic trails

[GitHub issue #433](https://github.com/kburson/aitm/issues/433)

Research parent: #426. Run after #431 records its findings.

## Question

Can AITM account for a long-lived native orchestrator session across multiple child stories, including an unattended overnight-style run, without assigning work by chat alone or requiring a persistent host monitor?

## Experiment

Use disposable child stories and an unrelated control chat on the same account. Run a bounded trail with each available native orchestrator surface, or record which cases that surface cannot support. Use the qualified headless XPR routes from #430–#431 for delegated work. Use session-owned, short-lived capture adapters.

1. **Sequential reuse.** Keep one orchestrator session open while it executes and closes one child and starts another. Record explicit end and start markers at verified turn or request boundaries. Include an idle interval and a resume or overnight-style continuation. Verify that work before assignment, between stories, and after closure is attributed only when there is an explicit binding. Exercise a mixed or ambiguous boundary and report the unsupported portion.
2. **Parallel work.** Run two child stories concurrently in separately identified headless sessions, with the orchestrator still active. Exercise a nested delegation and a headless XPR turn where supported. Bind each worker to the assigned story and attempt at launch. Deliver one late receipt after the orchestrator switches children and replay one receipt. Verify the receipt stays with its original assignment, the unrelated chat stays outside both stories, and parent aggregates and child detail do not count the same native observation twice.
3. **Handoff and time.** Detach one agent partway through a story and record its engaged time and measurement boundary. Resume the same story in a fresh context and record the successor's contribution through closure. Use AITM's engaged-time definition, including in-scope tool waits and excluding idle or owner waits. Preserve each agent/session contribution and report elapsed wall time separately, since parallel engaged intervals can overlap.
4. **Unattached work.** Capture a bounded brainstorming or spike-development session before any story is assigned. Retain its stable receipt and timing identity in an unattributed pool. Later assign the evidenced scope to the appropriate story with an explicit, auditable link. Test replay and a conflicting attribution. Verify prior observations remain traceable and the usage and time enter story and epic rollups once.

## Evidence

Produce sanitized assignment markers, handoff and delayed-attribution examples, and reconciled per-session, per-story, and epic totals. Show orchestrator, worker, and reviewer contributions, coverage gaps, engaged time, and elapsed time. Distinguish genuinely shared epic work from child-specific work. Report timing or usage that cannot be safely split as a gap. Record provider, harness version, surface, authentication and billing mode, and whether each boundary was demonstrated, unsupported, or inconclusive. A bounded overnight-style rehearsal may simulate the idle interval. State what unattended behavior was actually observed.

## Results

[Research findings](attachments/epic-trail-results.md) · [Sanitized receipt](attachments/epic-trail-receipt.json) · [Independent evidence review](attachments/independent-evidence-review.md).
