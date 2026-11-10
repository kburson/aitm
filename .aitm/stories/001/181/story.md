---
schema: "aitm.story/v0"
id: 181
title: "Measure story engagement and owner waits across the workflow"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/181"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-10T19:31:49Z"
updated: "2026-11-10T19:52:02Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/000/2/design/core-design.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/2026-11-10-actual-backfill.md", "attachments/2026-11-10-actual-backfill.json", "attachments/timing-and-usage-coordination.md"]}
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
