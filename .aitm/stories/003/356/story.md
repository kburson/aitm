---
schema: "aitm.story/v0"
id: 356
title: "Shard tests by execution category"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/356"
parent: null
children: [357, 358, 359, 360, 361]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-20T14:30:11Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-20-356-delivery-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Shard tests by execution category

[GitHub issue #356](https://github.com/kburson/aitm/issues/356) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 560. Priority P2. Size Feature.

Decompose one claim out of #133 into an independent epic. Divide the collected tests into execution categories and run those categories as parallel shards for a full sweep.

Ordinary local selection and the hosted pull-request path map stay the short path. The scheduled sweep is the run that uses every shard.

The categories are fast unit, slow unit, local integration, and systems integration. The classification spike names any collected test that fits none of those four.

## Research, then development

1. #357 classifies the collected tests.
2. #358 finds what blocks running each category as its own pytest invocation, locally and as separate CI jobs. It is blocked by #357.
3. #359 runs a local full sweep as those shards. It is blocked by #357 and #358.
4. #360 runs the same sweep in CI. It is blocked by #359.
5. #361 schedules that CI sweep. It is blocked by #360.

Spike stories write findings and create no production software. Feature stories stay blocked until the receipts they depend on are accepted.

## Starting material

Read #285, #286, #148, #290, #292, #293, #294, and #337. Advisory shard code and the refused cutover are evidence. They are the starting point for the spikes.

This epic is independent of #351, #362, and #370. Development does not start from this epic.

#370 decides how one Python program selects affected tests on every operating system. This epic classifies tests by execution category.

## Full-sweep acceptance

- Reconcile shards to the exact collected inventory for the declared source and runner profiles. Every eligible ID has one assignment. Record platform exclusions, registration or collection failures, skip reasons, and exceptions by exact ID. A test outside the four categories still needs an explicit disposition before the sweep can claim completeness.
- Demonstrate isolation and account for passed, failed, skipped and missing outcomes. Compare with the serial reference of the same source and workload. Report elapsed time and, for hosted runs, setup and queue time.
- Observe an actual scheduled default-branch sweep with an authentic run and attempt, exact source and complete per-shard receipts. Record any delay or missing result as such. The ordinary local selector, hosted PR path map and governed #103 gate keep their existing authority. #362 owns failure-flag behavior, and #351 and #370 remain independent.

The delivery sequence follows the accepted evidence from one child to the next. #357 is active. The downstream plans are conditional until the named receipts are accepted.

[Delivery plan](plan/2026-11-20-356-delivery-plan.md).
