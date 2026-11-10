---
schema: "aitm.story/v0"
id: 105
title: "[CI2] Verify canonical PR evidence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/105"
parent: 103
children: []
blocking: [106]
blocked-by: [104]
created: "2026-11-10T02:57:05Z"
updated: "2026-11-10T04:56:02+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/103/plan/implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/leaf-planning-review.md"], "attachments": []}
expansions: []
trips: []
---

# [CI2] Verify canonical PR evidence

[GitHub issue #105](https://github.com/kburson/aitm/issues/105) · [Parent #103](../103/story.md) · [Parent plan](../103/plan/implementation-plan.md).

Prerequisite [#104](../104/story.md).

Deliver the read-only verifier for the canonical Actions workflow, exact live PR and attempt. Exercise stale base, insufficient identity, wrong workflow and incomplete attempts with real-shape fixtures. Use CI1 and manual readback through its own delivery, then verify the trusted copy. The helper coverage floor is 90%.

Refined forecast **3.5 implementation agent-hours**. Leaf stays in Backlog pending its own design and pickup gates.

The [leaf design](design/design.md) and [implementation plan](plan/implementation-plan.md) passed [independent scoped planning review](plan/leaf-planning-review.md). Verified predecessor delivery, applicable authority and an exact fresh JIT still gate Develop.
