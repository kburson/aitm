---
schema: "aitm.story/v0"
id: 435
title: "[Epic] Portable agent effort and cost management"
kind: "epic"
state: "done"
issue: "https://github.com/kburson/aitm/issues/435"
parent: null
children: [436, 437, 438, 439, 440, 441, 442, 443, 444, 445]
blocking: []
blocked-by: []
created: "2026-11-25T03:15:49Z"
updated: "2026-11-25T14:41:10.672Z"
last-branch: "planning"
estimate: {"agent-hours": 27.5, "size": "Feature"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-refinement-and-engagement-backfill.md"], "attachments": ["attachments/2026-11-25-release-delivery.json", "attachments/timing/435-delivery-native-engagement-20261125-435.json", "attachments/435-agent-cost.json"]}
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

[#444](../444/story.md) delivered AIPR companion receipt reconciliation in [PR #453](https://github.com/kburson/aitm/pull/453).

[#445](../445/story.md) qualified the portable release on three hosts and verified the live pilot in [PR #454](https://github.com/kburson/aitm/pull/454).

## Refinement

**Size Feature. Estimate 27.5 agent-hours.** [Sizing basis and evidence](<plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Release

All ten child stories are Done. The final release is on `trunk` at `1956fecf716e06236a9741afc0a3e49643835e1e`. [Epic release sign-off](retro/2026-11-25-epic-release-sign-off.md) · [Qualification matrix](../445/attachments/qualification-matrix.md).

GitHub closed #435 as completed and Project 24 read back Done with all nine delivery PRs linked.

The epic recorded **1.9116 observed agent-hours**, including **1.8623 child agent-hours** and the direct closeout below. Coverage is partial.

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Claude reported list equivalent | Grok reported USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex epic closeout | 2m 57.249s | 3,274,752 | 11,031 | 8,107 | $0.820679 | — | — |
| **Direct epic closeout subtotal** | **2m 57.249s** | **3,274,752** | **11,031** | **8,107** | **$0.820679** | **—** | **—** |

**Observed direct epic closeout 0.0492 agent-hours**, with partial coverage through 2026-11-25T14:41:10.409Z. Verified billed cost is unknown.

Cached input counts cache reads. New input includes cache creation. Output includes reasoning where counted by the provider. Codex estimates use GPT-6.2 Sol standard rates. Claude and Grok amounts retain their respective native bases. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [xAI tick conversion](https://docs.x.ai/developers/cost-tracking#how-it-works) · [Engagement evidence](attachments/timing/435-delivery-native-engagement-20261125-435.json) · [Cost calculation inputs](attachments/435-agent-cost.json)
