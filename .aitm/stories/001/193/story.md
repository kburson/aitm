---
schema: "aitm.story/v0"
id: 193
title: "[#181 B02] Qualify and hand off the local dashboard"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/193"
parent: 181
children: []
blocking: []
blocked-by: [191, 192]
created: "2026-11-10T21:02:23Z"
updated: "2026-11-11T05:22:06Z"
last-branch: "codex/aitm-193-dashboard-handoff"
estimate: {"agent-hours": 2.25, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "B02", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "834894299283f0fe9988e868ecbd95520ed1f1b1c5fd57f72f646106d086fa81"}
---

# [#181 B02] Qualify and hand off the local dashboard

[GitHub issue #193](https://github.com/kburson/aitm/issues/193) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L101)

Required predecessors #191, #192. The proposed estimate is 2.25 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## B02. Qualify and hand off the local dashboard

- [ ] From a clean checkout of the delivered tool, pin the historical seed and then the post-A06 planning commit. Run the snapshot and render commands in a private local output folder. Open the file offline. Record the command, pinned inputs, report/receipt digests and browser observation.
- [ ] Verify the epic, status and coverage filters, a child and epic drilldown, partial historical Actual, scoped elapsed, owner wait, timing watermarks and evidence basis, and Unknown Cost. Refresh from the later snapshot and observe the scoped receipt change while the first pinned JSON remains reproducible. Check the HTML and reports for private payload leakage.
- [ ] Publish the quick start and evidence. The quick start gives exact commands, requirements, the expected local output, how to refresh, and how to inspect coverage. Verify another operator can follow it from the clean checkout.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
