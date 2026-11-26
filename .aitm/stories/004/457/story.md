---
schema: "aitm.story/v0"
id: 457
title: "Capture and publish session-owned agent turn receipts"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/457"
parent: 456
children: []
blocking: [458, 461]
blocked-by: []
created: "2026-11-25T16:06:16Z"
updated: "2026-11-26T00:11:37.857Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-25-session-owned-turn-capture.md"], "plan": ["plan/2026-11-25-session-owned-turn-capture-plan.md"], "attachments": ["attachments/timing/457-kickoff-native-engagement-20261125-457.json", "attachments/timing/457-kickoff-native-usage-20261125.json", "attachments/timing/457-delivery-native-engagement-20261125-457.json", "attachments/timing/457-delivery-native-usage-20261125.json", "attachments/qualification/457-provider-qualification.json", "attachments/qualification/457-remote-publication.json", "attachments/qualification/457-route-readback.md", "attachments/timing/457-delivery-refresh-engagement-20261125-457.json", "attachments/timing/457-delivery-refresh-usage-20261125.json", "attachments/qualification/457-aipr-qualification.json", "attachments/qualification/457-grok-desktop-plan-review.md", "attachments/timing/457-grok-plan-review-usage-20261125.json", "attachments/timing/457-grok-plan-review-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-setup.md", "attachments/timing/457-desktop-scratch-setup-usage-20261125.json", "attachments/timing/457-desktop-scratch-setup-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-readback.md", "attachments/timing/457-desktop-scratch-readback-usage-20261125.json", "attachments/timing/457-desktop-scratch-readback-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-retry-verification.md", "attachments/timing/457-desktop-scratch-retry-usage-20261125.json", "attachments/timing/457-desktop-scratch-retry-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-replay-fix.md", "attachments/timing/457-desktop-replay-fix-usage-20261125.json", "attachments/timing/457-desktop-replay-fix-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-replay-fix.json", "attachments/qualification/457-disposable-desktop-approved-retry.md", "attachments/timing/457-desktop-approved-retry-usage-20261125.json", "attachments/timing/457-desktop-approved-retry-engagement-20261125-457.json", "attachments/qualification/457-disposable-desktop-approved-retry.json", "attachments/qualification/457-disposable-desktop-post-restart.md", "attachments/qualification/457-disposable-desktop-post-restart.json", "attachments/timing/457-desktop-post-restart-usage-20261125.json", "attachments/timing/457-desktop-post-restart-engagement-20261125-457.json", "attachments/qualification/457-grok-desktop-callback-advisory.md", "attachments/timing/457-grok-desktop-callback-advisory-usage-20261125.json", "attachments/timing/457-grok-desktop-callback-advisory-engagement-20261125-457.json", "attachments/qualification/457-desktop-route-probe-preflight.md", "attachments/timing/457-desktop-route-probe-preflight-usage-20261125.json", "attachments/timing/457-desktop-route-probe-preflight-engagement-20261125-457.json", "attachments/qualification/457-desktop-stale-route.md", "attachments/timing/457-desktop-stale-route-usage-20261125.json", "attachments/timing/457-desktop-stale-route-engagement-20261125-457.json", "attachments/qualification/457-desktop-forwarded-route.md", "attachments/qualification/457-desktop-forwarded-route.json", "attachments/timing/457-desktop-forwarded-route-usage-20261125.json", "attachments/timing/457-desktop-forwarded-route-engagement-20261125-457.json", "attachments/qualification/457-delivery-report.md", "attachments/timing/457-delivery-closeout-usage-20261125.json", "attachments/timing/457-delivery-closeout-engagement-20261125-457.json"]}
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

After restarting Desktop, the scratch hooks recorded the child start and failed child and owner stop callbacks. The owner prompt callback was absent. The two retained receipts from this run replayed byte-identically after a story switch and fresh process. [Post-restart evidence](attachments/qualification/457-disposable-desktop-post-restart.md).

Grok reviewed the callback failure and proposed a bounded direct-composer test plus defensive capture changes. [Independent advisory](attachments/qualification/457-grok-desktop-callback-advisory.md).

The scratch-only route diagnostic passed local checks and awaits approval of the five modified scratch commands. [Diagnostic preflight](attachments/qualification/457-desktop-route-probe-preflight.md).

The five diagnostic approvals saved. The open Desktop chat ran the obsolete scratch command, so its forwarded turn did not qualify the new diagnostic. [Stale command evidence](attachments/qualification/457-desktop-stale-route.md).

The scratch comparison confirmed that the Desktop composer delivered the owner prompt callback while the forwarded route did not deliver it to the diagnostic. Both composer callbacks settled against #457 after switching to #458 and running replay in fresh processes. [Composer and forwarded comparison](attachments/qualification/457-desktop-forwarded-route.md).

[PR #460](https://github.com/kburson/aitm/pull/460) passed independent exact-head review and merged to `trunk` at `87bc3d8a2875884014b59281117f68b9d63fabee`. The ordered parents and reviewed tree were verified on the remote. [Delivery report](attachments/qualification/457-delivery-report.md) · [Implementer sign-off](retro/2026-11-25-delivery-sign-off.md).

[Spike #461](https://github.com/kburson/aitm/issues/461) owns agent self-publication at story closeout.

GitHub readback confirmed Closed as completed at 2026-11-26T00:11:01Z. Project 24 read back Done with PR #460 linked.

## Actual agent engagement

**111m 09.925s observed (1.8528 agent-hours), partial coverage.** The current verification turn is measured through 2026-11-26T00:10:24.611Z. Includes the independent delivery review and coordination. Claude reported 75.317 s for the successful review invocation. Native engagement for that review was unavailable. Independent engagement is summed including overlap. [Timing receipt](attachments/timing/457-delivery-closeout-engagement-20261125-457.json).

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
| Codex approved scratch rerun verification | 2m 55.206s | 6,203,136 | 14,124 | 6,660 | $1.397023 | — | — |
| Codex disposable chat identity check | 0m 05.155s | 51,200 | 21,808 | 104 | $0.049776 | — | — |
| Codex approved disposable owner test | 0m 08.211s | 109,696 | 799 | 98 | $0.013548 | — | — |
| Codex approved disposable subagent test | 0m 02.985s | 36,736 | 797 | 10 | $0.005368 | — | — |
| Codex post-restart scratch verification | 5m 24.891s | 2,082,432 | 65,564 | 12,140 | Unknown | — | — |
| Codex post-restart disposable owner test | 3m 03.269s | 940,928 | 20,493 | 1,552 | $0.150599 | — | — |
| Codex post-restart disposable subagent test | 2m 53.510s | 3,106,560 | 48,607 | 2,188 | $0.429750 | — | — |
| Codex Desktop callback advisory coordination | 2m 01.913s | 1,269,888 | 20,254 | 4,732 | $0.214817 | — | — |
| Grok Desktop callback advisory | Unknown | 8,832 | 10,206 | 3,230 | — | $0.030061 | — |
| Codex Desktop route probe preflight | 2m 29.431s | 1,543,552 | 18,156 | 5,904 | $0.249707 | — | — |
| Codex Desktop stale route diagnosis | 2m 16.727s | 1,499,776 | 12,170 | 3,888 | $0.213198 | — | — |
| Codex stale scratch owner test | 1m 22.995s | 297,984 | 27,340 | 437 | $0.088848 | — | — |
| Codex stale scratch subagent test | 0m 02.756s | 40,320 | 777 | 10 | $0.005686 | — | — |
| Codex Desktop forwarded route coordination | 3m 21.974s | 2,578,176 | 19,932 | 8,100 | $0.378682 | — | — |
| Codex forwarded scratch owner test | 0m 10.160s | 123,264 | 966 | 106 | $0.015318 | — | — |
| Codex forwarded scratch subagent test | 0m 03.436s | 41,344 | 766 | 10 | $0.005766 | — | — |
| Codex composer scratch owner test | 0m 08.448s | 124,544 | 685 | 103 | $0.014854 | — | — |
| Codex composer scratch subagent test | 0m 03.945s | 41,600 | 842 | 10 | $0.005944 | — | — |
| Claude exact-head review startup | Unknown | 0 | 0 | 0 | — | — | $0.000000 |
| Claude exact-head source review | Unknown | 337,505 | 79,413 | 9,517 | — | — | $0.446540 |
| Codex Story 457 acceptance assessment | 0m 39.456s | 851,712 | 11,298 | 1,418 | $0.121947 | — | — |
| Codex Story 457 delivery closeout | 5m 59.117s | 6,345,088 | 43,386 | 11,764 | $0.838921 | — | — |
| **Observed subtotal** | **111m 09.925s** | 138,510,475 | 1,273,217 | 261,743 | $25.938765 | $0.085698 | $1.060419 |

**Combined cost reference for the observed work $27.084881.** Codex uses GPT-6.2 Sol Standard API rates. Grok values are provider-reported. Claude qualification values are provider list equivalents and Claude review values use Standard API list rates. New input includes cache writes where reported. **Verified billed cost is unknown.** [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Claude model rates](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) · [Sanitized usage evidence](attachments/timing/457-delivery-closeout-usage-20261125.json).
