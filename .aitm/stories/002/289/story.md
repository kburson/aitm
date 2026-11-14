---
schema: "aitm.story/v0"
id: 289
title: "[#133] Qualify scheduled full-suite validation on trunk in shadow"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/289"
parent: 133
children: []
blocking: [290, 291]
blocked-by: [277, 279]
created: "2026-11-14T13:09:50Z"
updated: "2026-11-14T13:12:59Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#133] Qualify scheduled full-suite validation on trunk in shadow

Parent #133. Rank 110.

Qualify a default-branch-only scheduled full run and read-only evidence contract in shadow. Verify exact SHA, run/attempt identity, full outcomes, delayed/missing evidence, and genuine failure retention. Exercise a separate scheduled-evidence route into the #278 warning and #279 recovery flow in shadow. Keep the existing gate and trunk protections.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.
