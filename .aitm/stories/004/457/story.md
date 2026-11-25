---
schema: "aitm.story/v0"
id: 457
title: "Capture and publish session-owned agent turn receipts"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/457"
parent: 456
children: []
blocking: [458]
blocked-by: []
created: "2026-11-25T16:06:16Z"
updated: "2026-11-25T21:58:06.109Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-25-session-owned-turn-capture.md"], "plan": ["plan/2026-11-25-session-owned-turn-capture-plan.md"], "attachments": ["attachments/timing/457-kickoff-native-engagement-20261125-457.json", "attachments/timing/457-kickoff-native-usage-20261125.json", "attachments/timing/457-delivery-native-engagement-20261125-457.json", "attachments/timing/457-delivery-native-usage-20261125.json", "attachments/qualification/457-provider-qualification.json", "attachments/qualification/457-remote-publication.json", "attachments/qualification/457-route-readback.md", "attachments/timing/457-delivery-refresh-engagement-20261125-457.json", "attachments/timing/457-delivery-refresh-usage-20261125.json", "attachments/qualification/457-aipr-qualification.json", "attachments/qualification/457-grok-desktop-plan-review.md", "attachments/timing/457-grok-plan-review-usage-20261125.json", "attachments/timing/457-grok-plan-review-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-setup.md", "attachments/timing/457-desktop-scratch-setup-usage-20261125.json", "attachments/timing/457-desktop-scratch-setup-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-readback.md", "attachments/timing/457-desktop-scratch-readback-usage-20261125.json", "attachments/timing/457-desktop-scratch-readback-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-retry-verification.md", "attachments/timing/457-desktop-scratch-retry-usage-20261125.json", "attachments/timing/457-desktop-scratch-retry-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-replay-fix.md", "attachments/timing/457-desktop-replay-fix-usage-20261125.json", "attachments/timing/457-desktop-replay-fix-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-replay-fix.json", "attachments/qualification/457-disposable-desktop-approved-retry.md", "attachments/timing/457-desktop-approved-retry-usage-20261125.json", "attachments/timing/457-desktop-approved-retry-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-approved-retry.json"]}
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

Grok recommends qualifying first in an isolated Desktop chat and scratch repository. The original approval request is on hold. [Independent second opinion](attachments/qualification/457-grok-desktop-plan-review.md).

The disposable Desktop chat and standalone repository are staged for the live check. [Scratch setup evidence](attachments/qualification/457-disposable-desktop-setup.md).

The owner reported running the disposable test. Desktop and scratch readback did not expose the test turn or callbacks. [Readback checkpoint](attachments/qualification/457-disposable-desktop-readback.md).

The authorized scratch retry completed the owner and supervised subagent turns. Callback evidence was absent, and the candidate rejected both retained reads. [Retry verification](attachments/qualification/457-disposable-desktop-retry-verification.md).

PR #460 now recovers both retained Desktop turns and preserves their #457 receipts through an actual story switch and fresh process. The live callback retest awaits approval of the exact scratch folder and updated scratch hooks. [Replay fix and callback diagnosis](attachments/qualification/457-disposable-desktop-replay-fix.md).

The approved scratch retry completed both turns. Retained replay passed again, while live callbacks still produced no receipts. [Approved retry evidence](attachments/qualification/457-disposable-desktop-approved-retry.md).

## Actual agent engagement

**80m 20.031s observed (1.3389 agent-hours), partial coverage.** The current verification turn is measured through 2026-11-25T21:58:05.595Z. Includes the completed owner and supervised child turns after approval and the directly related approval guidance. Live callbacks yielded no receipts. The retained replay added no model calls. Independent engagement is summed including overlap. [Timing receipt](attachments/timing/457-desktop-approved-retry-engagement-20261125-457.json).

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Grok reported USD | Claude cost reference USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex kickoff | 4m 10.569s | 2,786,176 | 45,583 | 10,240 | $0.472184 | — | — |
| Codex kickoff builder check | 0m 23.331s | 494,336 | 4,151 | 797 | $0.065706 | — | — |
| Codex implementation and qualification | 30m 49.771s | 42,264,832 | 210,129 | 70,114 | $7.625337 | — | — |
| Codex provider adapter and live probes | 8m 19.312s | 10,718,976 | 119,127 | 19,730 | $1.507452 | — | — |
| Codex publication and plan review | 5m 42.520s | 4,089,344 | 32,583 | 14,835 | $0.622450 | — | — |
| Codex headless probe 1 | 0m 02.803s | 15,232 | 8,715 | 5 | $0.019003 | — | — |
| Codex headless probe 2 | 0m 02.718s | 15,232 | 10,114 | 5 | $0.021801 | — | — |
| Codex independent source review | 2m 37.658s | 999,296 | 74,003 | 6,602 | $0.313956 | — | — |
| Codex independent source review 2 | 1m 10.436s | 870,784 | 18,557 | 2,783 | $0.152022 | — | — |
| Codex independent source review 3 | 0m 49.212s | 766,592 | 10,371 | 1,918 | $0.116581 | — | — |
| Codex independent source review 4 | 0m 21.344s | 342,144 | 3,030 | 807 | $0.048344 | — | — |
| Claude Code qualification 1 | Unknown | 0 | 24,251 | 4 | — | — | $0.097040 |
| Grok Build qualification | Unknown | 8,832 | 9,803 | 23 | — | $0.016429 | — |
| Claude Code qualification 2 | Unknown | 649 | 2,249 | 4 | — | — | $0.009097 |
| Claude Code qualification 3 | 0m 00.554s | 649 | 2,245 | 4 | — | — | $0.009081 |
| Claude AIPR review 1 (no seal) | 0m 37.161s | 260,227 | 45,301 | 4,622 | — | — | $0.253419 |
| Claude AIPR review 2 (sealed) | 0m 38.676s | 262,677 | 43,393 | 4,543 | — | — | $0.245242 |
| Codex coordination of Grok second opinion | 3m 30.362s | 5,640,832 | 18,011 | 7,652 | $1.314990 | — | — |
| Grok Desktop qualification plan review | Unknown | 8,832 | 10,571 | 5,350 | — | $0.039207 | — |
| Codex scratch Desktop setup | 3m 25.547s | 5,591,552 | 21,378 | 7,785 | $1.320597 | — | — |
| Codex disposable Desktop chat bootstrap | 0m 12.641s | 69,248 | 14,528 | 329 | $0.039271 | — | — |
| Codex scratch Desktop evidence readback | 1m 38.768s | 3,620,608 | 9,174 | 3,545 | $0.813993 | — | — |
| Codex coordination and retry verification | 3m 19.785s | 6,680,320 | 15,165 | 7,897 | $1.515179 | — | — |
| Codex disposable Desktop owner test | 0m 08.504s | 87,936 | 957 | 95 | $0.011658 | — | — |
| Codex disposable Desktop subagent test | 0m 03.770s | 29,568 | 779 | 10 | $0.004615 | — | — |
| Codex replay fix and scratch qualification | 4m 58.018s | 9,937,792 | 35,762 | 11,256 | $2.299446 | — | — |
| Codex scratch callback diagnosis | 2m 12.427s | 5,964,160 | 34,537 | 4,048 | $1.391700 | — | — |
| Codex scratch callback diagnosis follow-up | 0m 11.566s | 828,928 | 820 | 323 | $0.173911 | — | — |
| Codex scratch folder location | 0m 06.945s | 411,008 | 679 | 133 | $0.086913 | — | — |
| Codex project trust instructions | 0m 21.749s | 1,240,192 | 6,878 | 596 | $0.284490 | — | — |
| Codex scratch folder and trust explanation | 0m 31.923s | 1,259,392 | 6,070 | 1,177 | $0.293813 | — | — |
| Codex disposable chat lookup | 0m 12.499s | 847,616 | 958 | 349 | $0.178590 | — | — |
| Codex scratch hook review discovery | 0m 16.437s | 848,640 | 5,307 | 554 | $0.199266 | — | — |
| Codex bundled CLI hook review verification | 0m 59.334s | 3,913,600 | 9,655 | 1,627 | $0.845745 | — | — |
| Codex approved scratch rerun verification | 2m 07.340s | 4,411,648 | 9,584 | 4,989 | $0.995501 | — | — |
| Codex disposable chat identity check | 0m 05.155s | 51,200 | 21,808 | 104 | $0.049776 | — | — |
| Codex approved disposable owner test | 0m 08.211s | 109,696 | 799 | 98 | $0.013548 | — | — |
| Codex approved disposable subagent test | 0m 02.985s | 36,736 | 797 | 10 | $0.005368 | — | — |
| **Observed subtotal** | **80m 20.031s** | 115,485,482 | 887,822 | 194,963 | $22.803205 | $0.055636 | $0.613878 |

**Combined cost reference for the observed work $23.472719.** Codex uses GPT-6.2 Sol Standard API rates. Grok values are provider-reported. Claude qualification values are provider list equivalents and Claude review values use Standard API list rates. New input includes cache writes where reported. **Verified billed cost is unknown.** [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Claude model rates](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) · [Sanitized usage evidence](attachments/timing/457-desktop-approved-retry-usage-20261125.json).
