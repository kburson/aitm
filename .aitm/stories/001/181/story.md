---
schema: "aitm.story/v0"
id: 181
title: "Measure story engagement and owner waits across the workflow"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/181"
parent: null
children: [186, 187, 188, 189, 190, 191, 192, 193, 227]
blocking: []
blocked-by: []
created: "2026-11-10T19:31:49Z"
updated: "2026-11-11T14:03:54Z"
last-branch: "planning"
estimate: {"agent-hours": 26.0, "size": "Feature", "scope": "A and B only"}
priority: "P1"
origin: ".aitm/stories/000/2/design/core-design.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/story-timing-dashboard-design.md"], "plan": ["plan/story-timing-dashboard-implementation-plan.md", "plan/refinement.md", "plan/leaf-stories.md", "plan/leaf-issue-receipt.json", "plan/2026-11-11-181-slice-c-refinement.md", "plan/2026-11-11-181-slice-c-implementation-plan.md"], "attachments": ["attachments/2026-11-10-actual-backfill.md", "attachments/2026-11-10-actual-backfill.json", "attachments/timing-and-usage-coordination.md", "attachments/2026-11-10-local-dashboard-handoff.md"]}
expansions: []
trips: []
---

# Measure story engagement and owner waits across the workflow

[GitHub issue #181](https://github.com/kburson/aitm/issues/181)

## User story

As the AITM project owner, I want to see how much time agents have spent working on each story, how long they waited for my response, and what their token usage cost, so I can track work in progress and understand where delivery time went.

## Acceptance criteria

- [ ] Capture timestamped workflow progress and separately classified engagement, waiting for the owner, and idle intervals across brainstorming, design, refinement, planning, review, implementation, testing, delivery, and sign-off. Record explicit owner requests and their response or resolution boundaries. Record tool execution and return boundaries so in-turn tool time is distinguishable from owner waits, idle time, and unattended machine or CI time outside the turn. A gap in events alone does not establish engagement or an owner wait.
- [ ] Bind qualified agent-engagement intervals to a stable agent, native turn, story or draft, phase, and applicable attempt. Preserve scope through draft graduation, story switches, interruptions, retries, and review handoffs. Keep interval and source provenance so the workflow timeline can be compared with native turn activity.
- [ ] Project each child story's **Actual** to AITM-PY Backlog as total qualified agent-engagement seconds divided by 3,600. Include time spent running or waiting for tools invoked within a qualified, story-bound agent turn, counted once within that turn. Exclude owner wait, idle time, and unattended execution outside the turn. Include work across phases and retain distinct implementation-attempt time for lifecycle limits.
- [ ] Compute epic **Actual** as the sum of unique descendant stories' engagement plus directly attributed epic planning and orchestration. Count overlapping observations of the same agent activity once. Sum independently engaged agents even when their work overlaps. Keep direct epic time and the descendant subtotal inspectable.
- [ ] Report owner wait, idle, workflow elapsed time, and measurement coverage separately from **Actual**. Historical backfill uses attributable evidence, preserves partial or Unknown coverage, and gives neither missing intervals nor unstarted work a fabricated zero. Publish a partial numeric value only when its coverage can be surfaced with it.
- [ ] Keep turn-level token usage and rate evidence independent of timing. Populate **Cost** from the monitor's attributable API-equivalent usage, with priced and unpriced coverage preserved. Tool execution and wait duration add no charge by themselves. Charge tool output tokens only when they appear in a measured provider request. Missing cost never blocks a timing update, and timing never substitutes for token usage.
- [ ] Verify replay and board readback with concurrent agents, a scope switch, an owner wait, and incomplete telemetry. For example, two children with 900 and 1,800 engagement seconds plus 900 seconds of direct epic engagement yield **1.0 h** on the epic. The child totals include tool time within their turns. Adding 1,800 seconds of owner wait leaves **Actual** at **1.0 h**. Increasing tool runtime within a turn increases **Actual** by that amount if it does not overlap already counted time, with no change to **Cost** when measured tokens are unchanged.

- [ ] Store elapsed delivery boundaries and qualified agent intervals so elapsed delivery time and additive agent-hours can be reproduced from the same snapshot. Display them separately. Parallel actors add effort while their overlapping minutes pass once on the wall clock.
- [ ] For the planning rubric, compare a retained estimate to Actual for the same phase window and agent scope. Keep partial or Unknown records available for analysis and out of calibration.

## Related work

Reuse the eligible activity and implementation clock in #28, qualified review timing in #34, and usage/outcome contracts in #51. Integrate the usage monitor from #100 and the GitHub Project projection. Use #100 and #133 as historical backfill and board verification cases where retained evidence supports them.

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

[Native plan review](plan/reviews/xpr-2026-11-10-dashboard-plan-sealed/review-manifest.md) · [Independent Codex review](plan/reviews/spr-2026-11-10-dashboard-plan/review-manifest.md). Slice C retains its integration checkpoint and separate refinement. Parent status is Planning.

## Local dashboard handoff

[Delivered A/B evidence and timing readback](attachments/2026-11-10-local-dashboard-handoff.md)

## Slice C refinement and plan review

[Current capability and dependency readback](plan/2026-11-11-181-slice-c-refinement.md) · [Reviewed Slice C plan](plan/2026-11-11-181-slice-c-implementation-plan.md) · [Plan review](plan/reviews/2026-11-11-181-slice-c-review.md).

Slice C has a conditional plan for automatic Actual and Cost and a preliminary **21.25 h** integration estimate. The existing manual Actual and offline dashboard use verified planning receipts. Automatic Actual needs Core's pinned read and qualified activity, legacy adoption where applicable, and the supported GitHub writer. Automatic Cost separately needs monitor M13/M14 and the compatible Core C44 receiver. Hosted viewing uses master #1 M6. The plan records the precise open dependencies and capability gates. Slice C remains at the planning checkpoint.

### C01 read-only qualification

[#227 Pin producer capabilities and shared acceptance fixtures](../../002/227/story.md) follows the delivered #193 handoff.
