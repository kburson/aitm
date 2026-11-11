---
schema: "aitm.story/v0"
id: 192
title: "[#181 B01] Render and filter the offline dashboard"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/192"
parent: 181
children: []
blocking: [193]
blocked-by: [190]
created: "2026-11-10T21:02:22Z"
updated: "2026-11-11T05:05:05Z"
last-branch: "codex/aitm-192-offline-dashboard"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "B01", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "812c755038cb76206a1edcbf672935444cfe4c8f02d18c72b94757f391c439d2"}
---

# [#181 B01] Render and filter the offline dashboard

[GitHub issue #192](https://github.com/kburson/aitm/issues/192) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L95)

Required predecessors #190. The proposed estimate is 3.75 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## B01. Render and filter the offline dashboard

- [ ] Test `test_offline_render_and_escaped_evidence` against an A05 snapshot with partial, missing and complete values and hostile story text. Assert valid scoped labels, direct/child detail, the planning commit and committer time, snapshot as-of, usage selector/cutoff/rate basis and per-measure timing evidence-through UTC and basis. Include an Unknown-watermark row. Reject a physically resolved output within a Git worktree, including a symlink into one. Story text cannot close the data script or inject markup, JS, or a link. A hostile destination in a link field is inert, and a valid story and evidence destination remains usable. The output contains all required assets and no automatic network request.
- [ ] Run red. Implement the standalone HTML renderer and command. Filter by epic, status and coverage. Show State, Last progress, Estimate with scope, Actual, elapsed or scoped age, Owner wait, Cost, and evidence coverage. Detail shows separate cutoffs, timing basis and phase/role contributions, direct plus descendant totals, and canonical links. Derive story links from the validated repository and numeric issue ID. For supplied evidence URLs, allow only parsed HTTPS URLs for the pinned GitHub repository and approved issue or commit-scoped planning blob paths. Reject other schemes, user information, ports, queries and noncanonical paths, and render their labels as text. Consume A05's totals without computing a second timing or pricing fold in the browser.
- [ ] Run green and open the fixture file offline. Verify the filters and one drilldown and its evidence watermark in a browser and retain the observation with the candidate. Preserve a local output path outside the tracked checkout.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
