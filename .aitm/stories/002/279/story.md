---
schema: "aitm.story/v0"
id: 279
title: "[#133] Rehearse manual repair and verified trunk recovery"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/279"
parent: 133
children: []
blocking: []
blocked-by: [278]
created: "2026-11-13T05:14:32Z"
updated: "2026-11-13T11:30:16Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-13-279-manual-recovery-plan.md", "plan/reviews/plan-review.md", "plan/local-test.log", "plan/shadow.json", "plan/actual-repair.py"], "attachments": []}
expansions: []
trips: []
---

# [#133] Rehearse manual repair and verified trunk recovery

<!-- aitm-133-advisory-manual-recovery -->

Parent #133. Rank 90. Required predecessor #278.

Consume the durable advisory incident. Use one nominated repair through existing #103 and independent review, then verify a fresh complete green run on repaired current trunk before operator resume. Exercise stale green, repeated failure, infrastructure-only recovery and rollback with an active incident. Keep merge and pause operations manual.

[Reviewed replacement scope](https://github.com/kburson/aitm/blob/7d5e0d332ef328c48c4e3428089cb33253c65a8e/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).

## Reviewed plan

[Implementation plan](plan/2026-11-13-279-manual-recovery-plan.md) · [Independent review](plan/reviews/plan-review.md).

## Tested manual recovery

[Local tests](plan/local-test.log) · [Actual repair and green push in shadow](plan/shadow.json) · [Rehearsal script](plan/actual-repair.py) · [PR #284](https://github.com/kburson/aitm/pull/284). The replacement keeps late authenticated failures, revokes stale acknowledgments and binds explicit operator acknowledgment to exact current artifact and timestamp evidence.
