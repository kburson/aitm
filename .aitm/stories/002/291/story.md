---
schema: "aitm.story/v0"
id: 291
title: "[#133] Rehearse a human-operated trunk merge hold"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/291"
parent: 133
children: []
blocking: [294]
blocked-by: [279, 289]
created: "2026-11-14T13:09:51Z"
updated: "2026-11-14T13:12:59Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#133] Rehearse a human-operated trunk merge hold

Parent #133. Rank 120.

Rehearse the human-operated trunk-only hold on a disposable target. Verify ordinary agents cannot merge or push to the held target, other refs remain writable, only the designated separate human can approve one repair through the normal review path, and stale green cannot lift the hold. Keep live rules unchanged.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.
