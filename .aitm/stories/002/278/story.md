---
schema: "aitm.story/v0"
id: 278
title: "[#133] Publish a durable CI warning and nominate one repair"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/278"
parent: 133
children: []
blocking: [279]
blocked-by: [277]
created: "2026-11-13T05:14:22Z"
updated: "2026-11-13T05:14:05Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#133] Publish a durable CI warning and nominate one repair

<!-- aitm-133-advisory-durable-warning -->

Parent #133. Rank 80. Required predecessor #277.

Consume authenticated advisory intake. Serialize a versioned incident, deduplicate exact-attempt notifications, retain known failures and invalidate stale repair and recovery. In shadow, verify an operator-visible warning, lost-response retry and restart. Ask the operator to pause ordinary trunk work and nominate one repair owner. The warning grants no merge or pause authority.

[Reviewed replacement scope](https://github.com/kburson/aitm/blob/7d5e0d332ef328c48c4e3428089cb33253c65a8e/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).
