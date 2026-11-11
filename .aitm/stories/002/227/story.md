---
schema: "aitm.story/v0"
id: 227
title: "[#181 C01] Pin producer capabilities and shared acceptance fixtures"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/227"
parent: 181
children: []
blocking: []
blocked-by: [193]
created: "2026-11-11T14:02:13Z"
updated: "2026-11-11T14:15:58Z"
last-branch: "planning"
estimate: {"agent-hours": 2.25, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-11-227-c01-qualification-design.md"], "plan": ["plan/2026-11-11-227-c01-qualification.md", "plan/2026-11-11-227-c01-jit.md"], "attachments": ["attachments/qualification.md", "attachments/qualification.json", "attachments/shared-fixtures.json"]}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "C01", "path": ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md", "publication": "20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b", "raw-sha256": "b3bec939fd3012c17f2a8d303d5189de974cbe50da8c8cfb1d7d7deb14e4b4f2", "section-sha256": "f1812b0aa479c657dad43304f26ab696f09bb79d0e4a8c603def4aa169bea9aa"}
---

# [#181 C01] Pin producer capabilities and shared acceptance fixtures

Parent #181. Read-only qualification from the [accepted Slice C plan](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c01-freeze-input-and-parity-evidence).

Proposed implementation effort 2.25 agent-hours. Priority P1. Delivered A/B handoff #193 is the prerequisite.

- [ ] Pin delivered source, Core and monitor capability, A/B receipt inventory and existing Project field mappings.
- [ ] Reproduce the exact #181 and #111 fixtures and verify pinned byte digests.
- [ ] Define the shared C03/C05/C06 cases for parallel work, independent clocks, tool inclusion, missing usage and unauthenticated input.
- [ ] Record exact tests, observed outcomes and open upstream dependencies on planning.

This child qualifies evidence without changing product code, metric fields, monitor state or projection authority.

## Reviewed pickup

[Design](design/2026-11-11-227-c01-qualification-design.md)

[Plan](plan/2026-11-11-227-c01-qualification.md) · [JIT](plan/2026-11-11-227-c01-jit.md)

## Qualification

[Evidence](attachments/qualification.md) · [Machine readback](attachments/qualification.json) · [Shared fixtures](attachments/shared-fixtures.json)

[Independent qualification review](plan/reviews/qualification-review.md)

[Qualification sign-off](retro/2026-11-11-227-qualification-signoff.md)
