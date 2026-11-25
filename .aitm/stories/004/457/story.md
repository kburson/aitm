---
schema: "aitm.story/v0"
id: 457
title: "Capture and publish session-owned agent turn receipts"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/457"
pr: "https://github.com/kburson/aitm/pull/460"
parent: 456
children: []
blocking: [458]
blocked-by: []
created: "2026-11-25T16:06:16Z"
updated: "2026-11-25T18:24:13.177Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-25-session-owned-turn-capture.md"], "plan": ["plan/2026-11-25-session-owned-turn-capture-plan.md"], "attachments": ["attachments/timing/457-kickoff-native-engagement-20261125-457.json", "attachments/timing/457-kickoff-native-usage-20261125.json", "attachments/timing/457-delivery-native-engagement-20261125-457.json", "attachments/timing/457-delivery-native-usage-20261125.json", "attachments/qualification/457-provider-qualification.json", "attachments/qualification/457-remote-publication.json", "attachments/qualification/457-route-readback.md"]}
expansions: []
trips: []
---

# Capture and publish session-owned agent turn receipts

[GitHub #457](https://github.com/kburson/aitm/issues/457)

Implement the session-owned capture path recommended in #455. Reuse #435 enrollment, adapters, storage, and AIPR companion evidence.

## Acceptance

- The live chat agent binds its own and each supervised worker, subagent, SPR or XPR turn when it starts or dispatches. A small caller-owned helper persists private routing state and writes sanitized immutable receipts scoped to the story on `planning`.
- Qualify automatic live capture and exact delayed recovery on the advertised Codex, Claude Code and Grok Build routes. Exercise change of story, resume or compaction, interruption, handoff, out-of-order completion, replay, and pending or unattached work. Keep the Codex sealed-review gap explicit.
- Demonstrate remote publication under existing branch protection. Use one scoped writer for registration, handle concurrent pushes and ambiguous delivery by readback, and refuse conflicting identities. Test cross-project isolation, privacy, and overlap without duplicate usage.
- Measure processing and publication overhead and record any additional model turns. Keep provider transcripts private and AIPR decisions under their existing authority.

Carry the useful narrow checks from #127, #128 and #129 forward. #137 supplies Linux Grok evidence if that route is advertised. [Spike findings](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/455-findings.md)

## Kickoff

Drafted the [session capture design](design/2026-11-25-session-owned-turn-capture.md). An independent builder check identified three requirements to make explicit: minimum live route coverage, exact native launch binding, and remote writer fallback. The draft includes each. The owner accepted the design. [Implementation plan](plan/2026-11-25-session-owned-turn-capture-plan.md).

## Delivery candidate

[Draft PR #460](https://github.com/kburson/aitm/pull/460) carries the implementation. [Qualification checkpoint](attachments/qualification/457-route-readback.md).

## Actual agent engagement

**35m 53.860s observed (0.5983 agent-hours), partial coverage.** The current turn is measured through 2026-11-25T18:24:13.002Z. Independent engagement is summed including overlap. Provider launches with no exact start are listed as Unknown. [Timing receipt](attachments/timing/457-delivery-native-engagement-20261125-457.json).

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Grok reported USD | Claude list-equivalent USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex kickoff | 4m 10.569s | 2,786,176 | 45,583 | 10,240 | $0.472184 | — | — |
| Codex kickoff builder check | 0m 23.331s | 494,336 | 4,151 | 797 | $0.065706 | — | — |
| Codex implementation and qualification | 14m 34.395s | 13,652,096 | 112,482 | 35,434 | $1.944514 | — | — |
| Codex provider adapter and live probes | 8m 19.312s | 10,718,976 | 119,127 | 19,730 | $1.507452 | — | — |
| Codex publication and plan review | 5m 42.520s | 4,089,344 | 32,583 | 14,835 | $0.622450 | — | — |
| Codex headless probe 1 | 0m 02.803s | 15,232 | 8,715 | 5 | $0.019003 | — | — |
| Codex headless probe 2 | 0m 02.718s | 15,232 | 10,114 | 5 | $0.021801 | — | — |
| Codex independent source review | 2m 37.658s | 999,296 | 74,003 | 6,602 | $0.313956 | — | — |
| Claude Code qualification 1 | Unknown | 0 | 24,251 | 4 | — | — | $0.097040 |
| Grok Build qualification | Unknown | 8,832 | 9,803 | 23 | — | $0.016429 | — |
| Claude Code qualification 2 | Unknown | 649 | 2,249 | 4 | — | — | $0.009097 |
| Claude Code qualification 3 | 0m 00.554s | 649 | 2,245 | 4 | — | — | $0.009081 |
| **Observed subtotal** | **35m 53.860s** | 32,780,818 | 445,306 | 87,683 | $4.967065 | $0.016429 | $0.115218 |

**Combined cost reference for the observed work $5.098711.** Codex values use GPT-6.2 Sol Standard API rates applied to native requests. Grok values are provider-reported and Claude values are provider list equivalents. New input includes cache writes where reported. **Verified billed cost is unknown.** [Model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Sanitized usage evidence](attachments/timing/457-delivery-native-usage-20261125.json).
