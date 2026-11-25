---
schema: "aitm.story/v0"
id: 443
title: "Report agent effort and usage with compatible snapshot exports"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/443"
parent: 435
children: []
blocking: [445]
blocked-by: [442]
created: "2026-11-25T03:17:34Z"
updated: "2026-11-25T13:50:13.197Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-effort-report.md"], "attachments": []}
expansions: []
trips: []
---

# Report agent effort and usage with compatible snapshot exports

[GitHub #443](https://github.com/kburson/aitm/issues/443) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Add portable CLI and deterministic views by story, epic, role, provider and unattached work. Separate usage, estimate, indicator, and verified billing. Verify read-only legacy snapshot compatibility without changing published export bytes.

## Dependencies

- #442

## Refinement

**Size M. Estimate 3 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Implementation

[Effort reporting plan](plan/2026-11-25-effort-report.md).

[PR #452](https://github.com/kburson/aitm/pull/452) opened against `trunk` at head `133342fc127b6547dcfde48812185859de4683c1`. The focused local effort and legacy export suite passed 145 tests. [Hosted CI](https://github.com/kburson/aitm/actions/runs/45627558227).
