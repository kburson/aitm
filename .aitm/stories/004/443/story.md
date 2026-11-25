---
schema: "aitm.story/v0"
id: 443
title: "Report agent effort and usage with compatible snapshot exports"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/443"
parent: 435
children: []
blocking: [445]
blocked-by: [442]
created: "2026-11-25T03:17:34Z"
updated: "2026-11-25T14:05:15.252Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: null
origin: ".aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-effort-report.md"], "attachments": ["attachments/pr-452-source-review.md", "attachments/trusted-pr-452.json", "attachments/pr-452-test-mix.json", "attachments/timing/443-delivery-native-engagement-20261125-443.json", "attachments/443-agent-cost.json"]}
expansions: []
trips: []
---

# Report agent effort and usage with compatible snapshot exports

[GitHub #443](https://github.com/kburson/aitm/issues/443) · [Source plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md)

Parent #435. Follow the [#426 implementation plan](https://github.com/kburson/aitm/blob/65951b8f/.aitm/stories/004/426/plan/2026-11-24-agent-effort-cost-implementation-plan.md).

## Acceptance

Add portable CLI and deterministic views by story, epic, role, provider and unattached work. Separate usage, estimate, indicator, and verified billing. Verify read-only legacy snapshot compatibility without changing published export bytes.

## Dependencies

- #442

## Refinement

**Size M. Estimate 3 agent-hours.** [Sizing basis and evidence](<../435/plan/2026-11-25-refinement-and-engagement-backfill.md>).

## Implementation

[Effort reporting plan](plan/2026-11-25-effort-report.md).

[PR #452](https://github.com/kburson/aitm/pull/452) opened against `trunk` at head `133342fc127b6547dcfde48812185859de4683c1`. The focused local effort and legacy export suite passed 145 tests. [Hosted CI](https://github.com/kburson/aitm/actions/runs/45627558227).

The first hosted candidate failed shard collection because six IDs were absent from the test catalog. The replacement at `118c415eb0b1f8ef98fe982381d8e8bb3761e462` registers all six as local integration cases. The focused report and catalog run passed 157 tests. [Replacement hosted run](https://github.com/kburson/aitm/actions/runs/45627810253).

[Independent source review](attachments/pr-452-source-review.md) held the first passing hosted candidate for three findings.

The revised candidate at `069b8d6b8b8514010d6eae7d166288247667120b` addresses all three findings and passes 157 focused local tests. [Revised hosted run](https://github.com/kburson/aitm/actions/runs/45628903336).

All six hosted checks passed on the revised candidate. The independent re-review passed the same tree.

## Delivery

[PR #452](https://github.com/kburson/aitm/pull/452) merged to `trunk` at `953a051f4954a14a8aeb8c310a561cafbede6185`. The merge tree matches the reviewed and tested tree. [Delivery sign-off](retro/2026-11-25-delivery-sign-off.md) · [Trusted verifier](attachments/trusted-pr-452.json).

GitHub closed #443 as completed and Project 24 read back Done.

## Agent activity and cost

| Agent turn | Observed engagement | Observed tokens | Codex standard API estimate | Grok reported USD |
| --- | ---: | ---: | ---: | ---: |
| Codex delivery | 18m 6.109s | 11,356,020 | $1.826166 | — |
| Codex independent review 1 | 3m 7.690s | 1,419,818 | $0.340710 | — |
| Codex independent review 2 | 0m 39.118s | 417,328 | $0.073406 | — |
| **Delivery subtotal (known amounts)** | **21m 52.917s** | **13,193,166** | **$2.240282** | — |

**Observed delivery engagement 0.3647 agent-hours.** The subtotal includes concurrent independent agent activity and excludes explicitly timed passive CI waits. The delivery turn is measured through retained activity at 2026-11-25T14:04:41.908Z. **Verified billed story cost is unknown.**

Codex estimates use GPT-6.2 Sol standard API rates per request with cached inputs priced separately. Amounts cover retained requests through the measurement cutoff. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Engagement evidence](attachments/timing/443-delivery-native-engagement-20261125-443.json) · [Cost calculation inputs](attachments/443-agent-cost.json)
