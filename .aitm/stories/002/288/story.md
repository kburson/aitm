---
schema: "aitm.story/v0"
id: 288
title: "[#133] Improve dependency selection for a measured TIA gap"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/288"
parent: 133
children: []
blocking: [292]
blocked-by: [142, 285, 286]
created: "2026-11-14T13:09:50Z"
updated: "2026-11-15T02:29:36Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-14-288-grok-fixture-edge-plan.md", "plan/local-validation.md", "plan/replay-summary.json", "plan/local-test.log", "plan/reviews/plan-review.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Improve dependency selection for a measured TIA gap

Parent #133. Rank 110.

Improve one measured gap in dependency selection for fixtures, imports or child processes. Run affected tests and negative controls and retain full fallback for unknown impact. Follow-up gaps can receive separately ranked stories.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Exact fixture dependency

[Reviewed plan](plan/2026-11-14-288-grok-fixture-edge-plan.md) · [Local and seeded evidence](plan/local-validation.md) · [PR #302](https://github.com/kburson/aitm/pull/302).
