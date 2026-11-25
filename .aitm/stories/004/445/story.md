---
schema: "aitm.story/v0"
id: 445
title: "Qualify the portable agent effort release"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/445"
parent: 435
children: []
blocking: []
blocked-by: [439, 440, 441, 443, 444]
created: "2026-11-25T03:17:38Z"
updated: "2026-11-25T14:38:51.058Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "L"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-portable-release-qualification.md"], "attachments": ["attachments/pilot-results.md", "attachments/445-live-portable-effort-pilot.json", "attachments/qualification-matrix.md", "attachments/trusted-pr-454.json", "attachments/pr-454-source-review.md", "attachments/timing/445-delivery-native-engagement-20261125-445.json", "attachments/445-agent-cost.json"]}
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

The [live pilot](attachments/pilot-results.md) matched 93,953 native tokens across four unique observations and verified pending settlement across restart and byte-identical replay.

The [release qualification matrix](attachments/qualification-matrix.md), [independent review](attachments/pr-454-source-review.md), and [trusted verifier](attachments/trusted-pr-454.json) passed for the exact candidate.

## Delivery

[PR #454](https://github.com/kburson/aitm/pull/454) merged to `trunk` at `1956fecf716e06236a9741afc0a3e49643835e1e`. Its tree matches the verified candidate. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).

GitHub closed #445 as completed. Project 24 read back Done with PR #454 linked.

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Claude reported list equivalent | Grok reported USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex delivery | 11m 18.219s | 10,713,344 | 66,231 | 27,426 | $2.719267 | — | — |
| Codex independent review | 2m 1.570s | 465,664 | 38,225 | 4,277 | $0.165786 | — | — |
| Codex initial pilot turn 1 | 0m 3.541s | 15,232 | 10,142 | 8 | $0.021887 | — | — |
| Codex initial pilot turn 2 | 0m 2.732s | 15,232 | 10,152 | 8 | $0.021907 | — | — |
| Codex accepted pilot turn 1 | 0m 3.275s | 15,232 | 10,142 | 8 | $0.021887 | — | — |
| Codex accepted pilot turn 2 | 0m 2.719s | 15,232 | 10,152 | 8 | $0.021907 | — | — |
| Claude accepted pilot | 0m 3.706s | 0 | 24,457 | 12 | — | $0.097944 | — |
| Grok accepted pilot | 0m 4.828s | 8,832 | 9,818 | 60 | — | — | $0.016600 |
| Claude initial launch without native result | Unknown | Unknown | Unknown | Unknown | — | Unknown | — |
| **Delivery subtotal (known amounts)** | **13m 40.590s** | **11,248,768** | **179,319** | **31,807** | **$2.972643** | **$0.097944** | **$0.016600** |

**Observed delivery 0.2279 agent-hours**, with partial coverage through 2026-11-25T14:38:13.160Z. Verified billed story cost is unknown.

Cached input counts cache reads. New input includes cache creation. Output includes reasoning where counted by the provider. Codex estimates use GPT-6.2 Sol standard rates. Claude and Grok amounts retain their respective native bases. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [xAI tick conversion](https://docs.x.ai/developers/cost-tracking#how-it-works) · [Engagement evidence](attachments/timing/445-delivery-native-engagement-20261125-445.json) · [Cost calculation inputs](attachments/445-agent-cost.json)
