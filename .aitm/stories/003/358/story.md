---
schema: "aitm.story/v0"
id: 358
title: "[Spike] Find what blocks parallel category runs"
kind: "spike"
state: "review"
issue: "https://github.com/kburson/aitm/issues/358"
parent: 356
children: []
blocking: [359]
blocked-by: [357]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-20T16:04:54Z"
last-branch: "codex/358-category-isolation"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-20-358-delivery-plan.md", "plan/2026-11-20-358-isolation-findings.md", "plan/reviews/2026-11-20-358-grok-pr-review.md", "plan/2026-11-20-358-delivery.json"], "attachments": ["attachments/2026-11-20-358-isolation-evidence.json", "attachments/2026-11-20-358-local-evidence.zip"]}
expansions: []
trips: []
---

# [Spike] Find what blocks parallel category runs

[GitHub issue #358](https://github.com/kburson/aitm/issues/358) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 580. Priority P2. Size S.

Question: given the accepted classification, what prevents each category from running as its own pytest invocation at the same time, locally and as separate CI jobs?

The hosted path-map check remains the ordinary pull-request path. Name the conditions a later parallel run must satisfy, including any test that cannot share a machine with another category.

## Bound

This is research for #356. Write the finding. Shards, jobs, and a schedule stay unimplemented in this story.

Stay blocked until #357 is accepted.

## Handoff

#359 implements the accepted classification and this finding together.

## Acceptance criteria

- On the accepted #357 inventory, compare serial and concurrent pytest invocations locally and assess separately hosted jobs on the required runner profiles. Record which cases were demonstrated and which remain unverified.
- Identify shared fixture, checkout, cache, coverage, subprocess, filesystem, tool and host-state dependencies with exact test witnesses. Record minimum isolation, platform requirements and tests that require exclusive execution.
- Publish the commands, outcomes, timings, constraints, and a scheduling and isolation matrix for #359. A discrepancy needs a reproduced witness and explicit disposition. Independent acceptance of the diagnostic receipt releases #359.

[Delivery plan](plan/2026-11-20-358-delivery-plan.md).

[Isolation findings](plan/2026-11-20-358-isolation-findings.md) · [Experiment evidence](attachments/2026-11-20-358-isolation-evidence.json).

[Grok review](plan/reviews/2026-11-20-358-grok-pr-review.md) · [Delivered planning evidence](plan/2026-11-20-358-delivery.json) · [Sign-off](retro/2026-11-20-358-sign-off.md).
