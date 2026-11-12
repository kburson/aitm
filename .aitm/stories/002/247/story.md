---
schema: "aitm.story/v0"
id: 247
title: "[Epic] M6 Viewer"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/247"
parent: 1
children: [249, 248, 250, 251, 252, 253, 254, 255, 256, 258, 257, 259, 260]
blocking: []
blocked-by: []
created: "2026-11-12T00:31:36Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 43.5, "size": "Feature", "scope": "accepted backlog decomposition"}
priority: null
origin: ".aitm/drafts/2026-11/20261108-1310-viewer"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["attachments/2026-11-11-1-hosted-dashboard-coverage-design.md"], "plan": ["plan/2026-11-11-247-m6-viewer-decomposition.md"], "attachments": ["attachments/2026-11-11-1-hosted-dashboard-coverage-design.md", "attachments/2026-11-11-1-m6-read-only-preview-plan-review.md", "attachments/2026-11-11-1-m6-read-only-preview-plan.md", "attachments/2026-11-11-1-m6-read-only-preview-refinement.md", "attachments/2026-11-11-139-m6-timing-pilot-readback.json", "attachments/2026-11-11-139-m6-timing-pilot.md"]}
expansions: []
trips: []
---

# [Epic] M6 Viewer

[GitHub issue #247](https://github.com/kburson/aitm/issues/247) · [Product Epic #1](../../000/1/story.md)

Deliver the local viewer, then a static hosted viewer with progress, flow, timing and Cost, bumps, evidence summaries, retrospectives, and Discuss. Use the reviewed read-only preview to prove the pinned metrics and publication model.

[Graduated draft](draft.md) · [Accepted decomposition](plan/2026-11-11-247-m6-viewer-decomposition.md) · [#139 timing pilot](attachments/2026-11-11-139-m6-timing-pilot.md)

All items are in Backlog. Each needs its own reviewed and accepted JIT implementation plan at pickup. Formal M6 implementation follows released M1. See the plan for M2, timing, Cost and authorized hosting gates.

## Backlog items

- [V01 #249 Build the pinned read-only preview data](../249/story.md)
- [V02 #248 Render and qualify the downloadable preview bundle](../248/story.md)
- [V03 #250 Consume released Core exports and serve the local viewer](../250/story.md)
- [V04 #251 Show story progress, hierarchy and detail](../251/story.md)
- [V05 #252 Show timing, Cost and evidence coverage in the local viewer](../252/story.md)
- [V06 #253 Show workflow flow history](../253/story.md)
- [V07 #254 Show evidence summaries, bumps and retrospectives](../254/story.md)
- [V08 #255 Add a read-only Discuss handoff](../255/story.md)
- [V09 #256 Qualify a static hosted build with synthetic data](../256/story.md)
- [V10 #258 Qualify real-data GitHub Pages hosting and issue links](../258/story.md)
- [V11 #257 Qualify timing replay and board-to-view parity](../257/story.md)
- [V12 #259 Qualify priced Cost replay and board-to-view parity](../259/story.md)
- [V13 #260 Qualify M6 release and publish the viewer tutorial](../260/story.md)

[Full decomposition review](plan/reviews/2026-11-11-247-m6-decomposition-acceptance.md) · [Backlog readback](plan/backlog-hydration-receipt.json)

## Cost integration dependency update

[The reviewed #230 replan](../230/plan/2026-11-11-230-cost-dependency-replan.md) resolves the prior #100 completion-accounting hold. #259 retains its qualified #230 and M2 gates. #260 retains #259 and its other accepted prerequisites.
