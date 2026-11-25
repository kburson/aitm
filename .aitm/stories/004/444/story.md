---
schema: "aitm.story/v0"
id: 444
title: "Reconcile AIPR companion usage receipts"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/444"
parent: 435
children: []
blocking: [445]
blocked-by: [437, 440, 441]
created: "2026-11-25T03:17:36Z"
updated: "2026-11-25T14:22:50.857Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-aipr-companions.md"], "attachments": ["attachments/444-live-aipr-companions.json", "attachments/pr-453-source-review.md", "attachments/trusted-pr-453.json", "attachments/pr-453-test-mix.json", "attachments/timing/444-delivery-native-engagement-20261125-444.json", "attachments/444-agent-cost.json"]}
expansions: []
trips: []
---

# Reconcile AIPR companion usage receipts

[GitHub #444](https://github.com/kburson/aitm/issues/444) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Validate sealed decisions separately from usage. Exercise two rounds, delayed and reversed delivery, interruption and replay on existing qualified routes. Preserve failed Codex attempt usage and its sealed-review gap.

## Dependencies

- #437
- #440
- #441

## Refinement

**Size M. Estimate 3 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Implementation

[Companion receipt plan](plan/2026-11-25-aipr-companions.md).

[PR #453](https://github.com/kburson/aitm/pull/453) opened at `8a460de58119d09a1d0b38a834a623e154b3ab45`. The focused effort and catalog run passed 134 tests. [Hosted run](https://github.com/kburson/aitm/actions/runs/45632218637).

The [live pilot](attachments/444-live-aipr-companions.json) exercised two rounds on Claude and Grok and one interruption per provider. All six native receipts replayed byte-identically after reversed round delivery and SQLite reopen. Four sealed decisions were independently verified against the reviewer, artifact and response. All four disposable brokers read back offline.

The [independent source review](attachments/pr-453-source-review.md), [trusted verifier](attachments/trusted-pr-453.json), and all six hosted jobs passed on the same candidate.

## Delivery

[PR #453](https://github.com/kburson/aitm/pull/453) merged to `trunk` at `e4c41649f6ccdba33396cf9af46d5cf98102c842`. The merged tree matches the reviewed and attested tree. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).

GitHub closed #444 as completed and Project 24 read back Done.

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Claude reported list equivalent | Grok reported USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex delivery | 12m 0.169s | 10,642,816 | 75,438 | 29,317 | $1.508328 | — | — |
| Codex independent review | 1m 24.602s | 416,896 | 28,152 | 2,977 | $0.127764 | — | — |
| Claude AIPR round 1 | 0m 20.022s | 154,833 | 28,916 | 2,204 | — | $0.153167 | — |
| Claude AIPR round 2 | 0m 12.697s | 123,091 | 4,357 | 1,433 | — | $0.044055 | — |
| Claude AIPR interrupted | 0m 10.119s | 77,752 | 25,224 | 626 | — | $0.114919 | — |
| Grok AIPR round 1 | 0m 46.963s | 210,816 | 47,958 | 2,251 | — | — | $0.146084 |
| Grok AIPR round 2 | 0m 20.237s | 127,360 | 34,710 | 1,010 | — | — | $0.094629 |
| Grok AIPR interrupted | 0m 15.399s | 70,528 | 42,816 | 825 | — | — | Unknown |
| **Delivery subtotal (known amounts)** | **15m 30.208s** | **11,824,092** | **287,571** | **40,643** | **$1.636091** | **$0.312142** | **$0.240713** |

**Observed delivery engagement 0.2584 agent-hours.** The subtotal includes concurrent reviewer activity and excludes explicitly timed passive CI waits. The delivery turn is measured through retained activity at 2026-11-25T14:22:50.719Z. Interrupted pilot turns have partial token coverage. **Verified billed story cost is unknown.**

Cached input uses provider-reported cache reads. New input includes cache creation. Output includes reasoning where counted by the provider.

Codex estimates use GPT-6.2 Sol standard rates per retained request. Claude values use native list-price equivalents. Grok USD uses native settled turn ticks at 10 billion ticks per USD. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [xAI tick conversion](https://docs.x.ai/developers/cost-tracking#how-it-works) · [Engagement evidence](attachments/timing/444-delivery-native-engagement-20261125-444.json) · [Cost calculation inputs](attachments/444-agent-cost.json)
