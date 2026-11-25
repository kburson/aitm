---
schema: "aitm.story/v0"
id: 442
title: "Roll up epic trails, handoffs and overlapping agent effort"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/442"
parent: 435
children: []
blocking: [443]
blocked-by: [437]
created: "2026-11-25T03:17:32Z"
updated: "2026-11-25T13:27:16.081Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "L"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-trail-rollup.md"], "attachments": ["attachments/trusted-pr-451.json", "attachments/pr-451-test-mix.json", "attachments/pr-451-source-review.md", "attachments/timing/442-delivery-native-engagement-20261125-442.json"]}
expansions: []
trips: []
---

# Roll up epic trails, handoffs and overlapping agent effort

[GitHub #442](https://github.com/kburson/aitm/issues/442) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Validate story marker lifecycle and detach/attach with exact native boundaries. Sum disjoint usage, session engagement and interval-union wall time without double counting. Reconcile the #433 fixture.

## Dependencies

- #437

## Implementation

[PR #451](https://github.com/kburson/aitm/pull/451) implements the [trail rollup plan](plan/2026-11-25-trail-rollup.md). Delivery requires independent review and trusted verification for the current candidate.

## Refinement

**Size L. Estimate 3.5 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Delivery

[PR #451](https://github.com/kburson/aitm/pull/451) merged to `trunk`. GitHub closed #442 and Project 24 read back Done. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md).

## Actual agent engagement

**31m 10.362s observed (0.5195 agent-hours), partial coverage.** Codex delivery contributed 18m 43.685s, independent Codex review contributed 2m 19.041s, and Grok review contributed 10m 7.636s across four attempts. [Timing receipt](attachments/timing/442-delivery-native-engagement-20261125-442.json).

The sum includes in-turn tool work and independent reviewer turns, including concurrent turns. It excludes 3m 0.017s of explicit passive CI waits. The interrupted Grok attempt is measured through its last retained progress. The Claude review launches did not retain native turn boundaries, so Claude engagement remains unknown. The evidence ends at 2026-11-25T13:24:02.021Z.

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Grok reported USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex delivery | 18m 43.685s | 12,751,744 | 170,834 | 43,114 | $2.047982 | — |
| Codex independent review 1 | 1m 22.054s | 747,392 | 8,620 | 3,148 | $0.123459 | — |
| Codex independent review 2 | 0m 30.184s | 449,280 | 4,313 | 1,147 | $0.065024 | — |
| Codex independent review 3 | 0m 13.403s | 344,704 | 1,952 | 338 | $0.041754 | — |
| Codex independent review 4 | 0m 13.400s | 350,592 | 3,331 | 439 | $0.046111 | — |
| Grok review 1 (interrupted) | 3m 15.690s | Unknown | Unknown | Unknown | — | Unknown |
| Grok review 2 | 1m 48.824s | 8,832 | 22,636 | 10,567 | — | $0.076901 |
| Grok review 3 | 2m 1.616s | 8,832 | 23,644 | 11,539 | — | $0.082238 |
| Grok review 4 | 3m 1.506s | 175,360 | 42,198 | 14,831 | — | $0.177522 |
| Claude review 1 | Unknown | Unknown | Unknown | Unknown | — | — |
| Claude review 2 | Unknown | Unknown | Unknown | Unknown | — | — |
| **Delivery subtotal (known amounts)** | 31m 10.362s | 14,836,736 | 277,528 | 85,123 | $2.324331 | $0.336661 |
| Codex timing backfill (after delivery) | 4m 32.942s | 5,195,776 | 50,272 | 10,640 | $0.726522 | — |
| **Story subtotal including timing backfill** | 35m 43.304s | 20,032,512 | 327,800 | 95,763 | $3.050853 | $0.336661 |

Cached input counts provider-reported cache reads. New input counts input without a cache hit, including cache creation where reported. Output tokens include reasoning where the provider includes it in output. These are model usage counts.

**Combined cost reference for observed delivery $2.660992.** Including the completed timing backfill, the reference is **$3.387514**. These sums combine the Codex API estimate and Grok's reported amount. **Verified billed story cost is unknown.** Usage and cost are unknown for both Claude turns and the interrupted Grok turn. The table covers completed work before this reporting turn.

Codex estimates apply GPT-6.2 Sol standard API pricing to each native request, with cached input priced separately. All observed requests were within the short-context tier. Grok dollars use the native settled turn ticks at 10 billion ticks per USD. The engagement subtotals sum independent agents and exclude passive CI waits. The board's delivery Actual is 0.5195 agent-hours. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [xAI tick conversion](https://docs.x.ai/developers/cost-tracking#how-it-works) · [Engagement evidence](attachments/timing/442-delivery-native-engagement-20261125-442.json)
