---
schema: "aitm.story/v0"
id: 337
title: "[#133] Measure full PR validation and rehearse rollback to #103"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/337"
parent: 133
children: []
blocking: []
blocked-by: [323]
created: "2026-11-15T23:37:40Z"
updated: "2026-11-15T23:49:35Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/003/323/plan/2026-11-15-323-missed-slot-recovery-results.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/start.json", "plan/2026-11-15-337-full-pr-and-rollback-plan.md", "plan/production-readout.md", "plan/production-evidence.zip"], "attachments": []}
expansions: []
trips: []
---

# [#133] Measure full PR validation and rehearse rollback to #103

Parent #133. Required predecessor #323, delivered. Rank 160, 4 implementation agent-hours, M, P2.

Measure the complete PR path on a declared cohort of real production pull requests, tracing PR open, provider runs and retries, queue, required checks, coverage, wheel smoke, signed evidence, trusted verification, independent review and merge wherever directly observable. Retain identity, timings, exclusions and evidence gaps.

Rehearse a forward rollback to the exact ordinary full verifier and required evidence on a disposable protected GitHub repository. Copy the existing production trunk rules and add the proposed app-bound exact-check enforcement without a bypass on the normal gate. Exercise a separate trunk hold and a selected-only candidate, stop selection, restore a reviewed full-only state, prove missing, failed and superseded evidence does not authorize a merge, verify a current full green, then acknowledge and release the hold. Retain native GitHub decisions, exact test and verification receipts, and independent review.

Production is read-only apart from issue, board and planning records. #103 remains unchanged. This story conveys no cutover approval.

[Delivered #323 recovery](https://github.com/kburson/aitm/blob/214794c5ab0faf016608615f95b21d67765f260a/.aitm/stories/003/323/plan/2026-11-15-323-missed-slot-recovery-results.md).

## Pickup

[Verified native Dev state, rank and dependencies](plan/start.json).

## Measurement and rehearsal

[Bounded plan](plan/2026-11-15-337-full-pr-and-rollback-plan.md).

## Production baseline

Eight consecutive delivered PRs from the measurement window. [Timings](plan/production-readout.md) · [Native evidence and replay](plan/production-evidence.zip). The [rehearsal plan](plan/2026-11-15-337-full-pr-and-rollback-plan.md) binds all six canonical job contexts.
