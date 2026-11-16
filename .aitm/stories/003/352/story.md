---
schema: "aitm.story/v0"
id: 352
title: "[Spike] Name the condition that blocks local test selection"
kind: "spike"
state: "review"
issue: "https://github.com/kburson/aitm/issues/352"
parent: 351
children: []
blocking: [354]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-16T21:48:51Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-16-352-findings.md", "plan/reviews/2026-11-16-352-independent-findings-review.md", "retro/2026-11-16-352-spike-delivery.md"], "attachments": ["attachments/2026-11-16-352-selection-probe.json", "attachments/timing/2026-11-16-spike-review-352.json"]}
expansions: []
trips: []
---

# [Spike] Name the condition that blocks local test selection

[GitHub issue #352](https://github.com/kburson/aitm/issues/352) · [Parent #351](../351/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 440. Priority P2. Size S.

Question: on current trunk, what single condition prevents a local plan from naming the tests for one uncommitted production edit?

Known observations to test: `python -m tools.ci.tia.local --plan` returns unavailable, and `tools/ci/path_map.py` selects from committed trees, so an uncommitted edit is invisible. Name the blocking condition and the smallest investigation result that lets a later story name those tests.

## Bound

This is research for #351. Write the finding. Production code, the hosted path map, and CI stay unchanged.

Read #143, #267, #339, `tools/ci/tia/local.py`, and `tools/ci/path_map.py`.

## Handoff

#354 implements the accepted finding. It stays blocked until this receipt is accepted.

## Spike pickup

[Investigation plan](../351/plan/2026-11-16-351-local-tia-spike-plan.md) · [Plan SAR passed](../351/plan/reviews/2026-11-16-351-spike-plan-sar.md).

[Findings](plan/2026-11-16-352-findings.md) · [Machine receipt](attachments/2026-11-16-352-selection-probe.json).

[Independent review accepted](plan/reviews/2026-11-16-352-independent-findings-review.md) · [Signed retrospective](retro/2026-11-16-352-spike-delivery.md).
