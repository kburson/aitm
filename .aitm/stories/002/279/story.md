---
schema: "aitm.story/v0"
id: 279
title: "[#133] Rehearse manual repair and verified trunk recovery"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/279"
parent: 133
children: []
blocking: []
blocked-by: [278]
created: "2026-11-13T05:14:32Z"
updated: "2026-11-13T05:14:05Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#133] Rehearse manual repair and verified trunk recovery

<!-- aitm-133-advisory-manual-recovery -->

Parent #133. Rank 90. Required predecessor #278.

Consume the durable advisory incident. Use one nominated repair through existing #103 and independent review, then verify a fresh complete green run on repaired current trunk before operator resume. Exercise stale green, repeated failure, infrastructure-only recovery and rollback with an active incident. Keep merge and pause operations manual.

[Reviewed replacement scope](https://github.com/kburson/aitm/blob/7d5e0d332ef328c48c4e3428089cb33253c65a8e/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).
