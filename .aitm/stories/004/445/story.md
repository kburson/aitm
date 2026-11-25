---
schema: "aitm.story/v0"
id: 445
title: "Qualify the portable agent effort release"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/445"
parent: 435
children: []
blocking: []
blocked-by: [439, 440, 441, 443, 444]
created: "2026-11-25T03:17:38Z"
updated: "2026-11-25T14:34:37.647Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "L"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-portable-release-qualification.md"], "attachments": ["attachments/pilot-results.md", "attachments/445-live-portable-effort-pilot.json"]}
expansions: []
trips: []
---

# Qualify the portable agent effort release

[GitHub #445](https://github.com/kburson/aitm/issues/445) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Run Linux/macOS qualification and early Windows fixture/import checks. Pilot one same-provider story and one cross-provider epic trail. Publish bounded overhead, coverage, and privacy evidence.

## Dependencies

- #439
- #440
- #441
- #443
- #444

## Refinement

**Size L. Estimate 3.5 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Qualification

[Release qualification plan](plan/2026-11-25-portable-release-qualification.md).

[PR #454](https://github.com/kburson/aitm/pull/454) opened at `990582b8960ed2cab1ce9cb98853da68267f302a`. An installed pure wheel passed all 122 local macOS fixtures. Qualification includes [ordinary CI](https://github.com/kburson/aitm/actions/runs/45634555848) and the [hosted portability matrix](https://github.com/kburson/aitm/actions/runs/45634556081).

The [live pilot](attachments/pilot-results.md) matched 93,953 native tokens across four unique observations and verified byte-identical restart settlement and replay.
