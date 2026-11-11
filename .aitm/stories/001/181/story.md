---
schema: "aitm.story/v0"
id: 181
title: "Deliver the local story timing dashboard"
kind: "epic"
state: "done"
issue: "https://github.com/kburson/aitm/issues/181"
parent: null
children: [186, 187, 188, 189, 190, 191, 192, 193, 227]
blocking: []
blocked-by: []
created: "2026-11-10T19:31:49Z"
updated: "2026-11-11T14:44:06Z"
last-branch: "planning"
estimate: {"agent-hours": 26.0, "size": "Feature", "scope": "A and B only"}
priority: "P1"
origin: ".aitm/stories/000/2/design/core-design.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/story-timing-dashboard-design.md"], "plan": ["plan/story-timing-dashboard-implementation-plan.md", "plan/refinement.md", "plan/leaf-stories.md", "plan/leaf-issue-receipt.json", "plan/2026-11-11-181-slice-c-refinement.md", "plan/2026-11-11-181-slice-c-implementation-plan.md"], "attachments": ["attachments/2026-11-10-actual-backfill.md", "attachments/2026-11-10-actual-backfill.json", "attachments/timing-and-usage-coordination.md", "attachments/2026-11-10-local-dashboard-handoff.md", "attachments/2026-11-11-production-scope-transfer.md", "attachments/2026-11-11-181-closure-readback.md"]}
expansions: []
trips: []
---

# Deliver the local story timing dashboard

[GitHub issue #181](https://github.com/kburson/aitm/issues/181)

## User story

As the AITM project owner, I want a local dashboard I can use now to see progress, recorded agent effort and evidenced owner waits, and inspect token cost when there is verified usage.

## Delivered acceptance

- [x] Capture, attribute and retain planning evidence with explicit scope and coverage. Include in-turn tool execution in Actual and exclude owner waits, idle and unattended execution.
- [x] Compute per-story and epic Actual from qualified evidence. Inspect direct epic and descendant effort, and show elapsed time and observed working wall time separately from additive agent-hours.
- [x] Reproduce pinned snapshots and generate a standalone local dashboard with filters and evidence drilldowns. Keep Partial or Unknown visible and show Cost only from independent verified usage.
- [x] Verify a manual board readback and document the offline workflow. Reproduce the historical evidence and retain the read-only C01 qualification.
- [x] Record the production scope transfer to the owning epic or milestone. Preserve the original requirements and review artifacts at their published revisions.

## Backfill evidence and coordination

- [Historical Actual backfill](attachments/2026-11-10-actual-backfill.md) with board readback and exact rollup inputs. Partial coverage excludes the snapshot from calibration.
- [Coordination with Core and the usage monitor](attachments/timing-and-usage-coordination.md) with the responsibility split, wall-clock and additive effort model, and rubric rule.

## Reviewed design

[Story timing and early dashboard](design/story-timing-dashboard-design.md) was accepted at raw digest `sha256:ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5`. The near-term slices are sanitized evidence on planning, a reproducible local snapshot and an offline dashboard. The later integration reuses Core C23/C25/C44 and monitor M07/M13/M14.

- [Read-only feasibility evidence](design/read-only-feasibility.md)
- [Author check](design/reviews/sar-2026-11-10-dashboard-design/review-manifest.md)
- [Independent Codex review](design/reviews/spr-2026-11-10-dashboard-design/review-manifest.md)
- [Cross-provider review and exact final acceptance](design/reviews/xpr-2026-11-10-dashboard-design-sealed/review-manifest.md)

## Refined and reviewed implementation plan

[Refinement](plan/refinement.md) sets a P1 estimate of 26.0 implementation agent-hours for A/B. The [accepted plan](plan/story-timing-dashboard-implementation-plan.md) binds to raw digest `sha256:147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80`. The [leaf catalog](plan/leaf-stories.md) lists eight verified Backlog children with nine reciprocal dependency edges. A01 leads capture. B01 starts after the snapshot, with no dependency on Core #2 or the monitor #100.

[Native plan review](plan/reviews/xpr-2026-11-10-dashboard-plan-sealed/review-manifest.md) · [Independent Codex review](plan/reviews/spr-2026-11-10-dashboard-plan/review-manifest.md). This was the accepted A/B baseline at the Planning checkpoint.

## Local dashboard handoff

[Delivered A/B evidence and timing readback](attachments/2026-11-10-local-dashboard-handoff.md)

## Slice C refinement and plan review

[Current capability and dependency readback](plan/2026-11-11-181-slice-c-refinement.md) · [Reviewed Slice C plan](plan/2026-11-11-181-slice-c-implementation-plan.md) · [Plan review](plan/reviews/2026-11-11-181-slice-c-review.md).

The reviewed Slice C checkpoint recorded a conditional plan for automatic Actual and Cost and a preliminary **21.25 h** integration estimate. The existing manual Actual and offline dashboard use verified planning receipts. Automatic Actual needs Core's pinned read and qualified activity, legacy adoption where applicable, and the supported GitHub writer. Automatic Cost separately needs monitor M13/M14 and the compatible Core C44 receiver. Hosted viewing uses master #1 M6. The plan records the precise open dependencies and capability gates. The owner reassigned the unfinished production work during closure.

### C01 read-only qualification

[#227 Pin producer capabilities and shared acceptance fixtures](../../002/227/story.md) follows the delivered #193 handoff.

[C01 evidence and exact parity readback](../../002/227/attachments/qualification.md) records the completed read-only baseline. The production owners inherit the gates in the reviewed Slice C plan.


## Owner-approved scope transfer and closure

[Production ownership, dashboard delivery evidence and sign-off](attachments/2026-11-11-production-scope-transfer.md) records the decision to complete this epic for the local dashboard and C01 qualification. The reviewed production requirements follow their owning backlog and milestone drafts. [Epic retrospective and sign-off](retro/2026-11-11-181-epic-signoff.md).


[GitHub and AITM-PY closure readback](attachments/2026-11-11-181-closure-readback.md).
