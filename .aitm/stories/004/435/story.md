---
schema: "aitm.story/v0"
id: 435
title: "[Epic] Portable agent effort and cost management"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/435"
parent: null
children: [436, 437, 438, 439, 440, 441, 442, 443, 444, 445]
blocking: []
blocked-by: []
created: "2026-11-25T03:15:49Z"
updated: "2026-11-25T14:05:15.252Z"
last-branch: "planning"
estimate: {"agent-hours": 27.5, "size": "Feature"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-refinement-and-engagement-backfill.md"], "attachments": []}
expansions: []
trips: []
---

# [Epic] Portable agent effort and cost management

[GitHub #435](https://github.com/kburson/aitm/issues/435) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Deliver session-scoped agent effort, observed usage and cost evidence for stories and epic trails across Codex, Claude Code and Grok Build.

Research source [#426](https://github.com/kburson/aitm/issues/426) and the [implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

Start with the portable receipt store and story attribution. Use small portable Python adapters around existing provider harnesses. Qualify Linux and macOS first and run Windows fixtures early. Preserve privacy, unknown coverage and usage provenance. AIPR sealed decisions retain their existing authority.

This epic is separate from #100. The existing monitor, cutover, and accepted dependencies stay outside this delivery.

## Delivery sequence

- [#436 Portable receipt schema and transactional store](../436/story.md)
- [#437 Bind agent attempts to stories and link unattached work](../437/story.md)
- [#438 Session-scoped capture and exact-recovery interface](../438/story.md)
- [#439 Capture provider-reported Codex usage](../439/story.md)
- [#440 Capture provider-reported Claude Code usage](../440/story.md)
- [#441 Capture provider-reported Grok Build usage](../441/story.md)
- [#442 Roll up epic trails, handoffs and overlapping agent effort](../442/story.md)
- [#443 Report agent effort and usage with compatible snapshot exports](../443/story.md)
- [#444 Reconcile AIPR companion usage receipts](../444/story.md)
- [#445 Qualify the portable agent effort release](../445/story.md)

## Delivery progress

The foundation and three provider adapters were delivered through [PR #446](https://github.com/kburson/aitm/pull/446), [#447](https://github.com/kburson/aitm/pull/447), [#448](https://github.com/kburson/aitm/pull/448), [#449](https://github.com/kburson/aitm/pull/449), and [#450](https://github.com/kburson/aitm/pull/450).

[#442](../442/story.md) delivered epic trail rollups in [PR #451](https://github.com/kburson/aitm/pull/451). [#443](../443/story.md) delivered portable effort reports and legacy snapshot compatibility in [PR #452](https://github.com/kburson/aitm/pull/452).

## Refinement

**Size Feature. Estimate 27.5 agent-hours.** [Sizing basis and evidence](<plan/2026-11-25-refinement-and-engagement-backfill.md>).
