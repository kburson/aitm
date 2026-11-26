---
schema: "aitm.story/v0"
id: 461
title: "[Spike] Validate agent-owned settlement and publication at story closeout"
kind: "spike"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/461"
parent: 456
children: []
blocking: []
blocked-by: [457]
created: "2026-11-26T00:04:56Z"
updated: "2026-11-26T01:28:17.329Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/457/attachments/qualification/457-desktop-forwarded-route.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-agent-owned-closeout.md", "plan/2026-11-25-forwarded-route-addendum.md"], "attachments": ["attachments/qualification/461-forwarded-capture.md", "attachments/qualification/461-forwarded-capture.json", "attachments/qualification/461-closeout-findings.md", "attachments/qualification/461-closeout-readback.json", "attachments/effort/session/2033d1a0782e55bba0b7bad845bb36106ab6ad725d74e5bcbc4cda04c9119d04-r1.json", "attachments/effort/session/f16038236a38d5aaaa636948e9cb9467a6c61e5e6ef029c765ccd9e0dcf2c858-r1.json", "attachments/qualification/461-closeout-usage.json", "attachments/qualification/461-independent-delivery-review.md", "attachments/qualification/461-agent-cost.json"], "retro": ["retro/2026-11-25-delivery-sign-off.md"]}
expansions: []
trips: []
---

# [Spike] Validate agent-owned settlement and publication at story closeout

[GitHub #461](https://github.com/kburson/aitm/issues/461)

Follow-up to #457 in Epic #456. Validate whether the chat agent can settle and publish its own and supervised turn receipts using the existing caller-owned helper and planning writer.

## Experiment

- Use a disposable Desktop chat and a bounded enrolled story. Capture the owner and one supervised subagent. Leave at least one callback pending until native retention is available. Switch the active story before settlement and reopen the store in a fresh process.
- Have the chat agent invoke the supported retry and publish commands as part of ordinary story closeout. Verify exact owner and subagent receipts land once on the original story on protected `planning`. Repeat the same batch and verify identical remote bytes with no duplicate registration.
- Exercise an unavailable or ambiguous publication result using the existing authorized writer and readback. Verify unresolved evidence stays visible and unassigned when the original binding cannot be proved.
- Record the exact operator steps, extra model turns, timing, review and cost, publication authority, and any required human intervention. Recommend the smallest viable closeout workflow. Keep collection session-owned and use existing project permissions.

[Composer and delayed recovery evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/004/457/attachments/qualification/457-desktop-forwarded-route.md)

## Refined acceptance

- Reuse the qualified disposable Desktop composer path. Enroll #461 and capture one owner and one child. Record at least one durable pending terminal callback, switch the active story, and settle exact retained evidence in fresh CLI processes.
- The same Desktop chat agent freezes and publishes the original story batch with the supported CLI. Read both receipts back from protected planning and compare canonical bytes, identity uniqueness and story assignment after repeat publication.
- Demonstrate a publication refusal through the shipped writer and a separate missing-binding control. Preserve pending evidence and show that uncertain attribution cannot enter either story's batch.
- Deliver sanitized results, independently reviewed plan and evidence, elapsed time and turn usage where observed, publication authority, human actions, and a recommendation. Keep closeout turn coverage and unknown costs visible. The spike permits an evidence-backed negative result and owns no product changes.

[Qualification plan](plan/2026-11-25-agent-owned-closeout.md)

Claude Sonnet 5.5 accepted the revised plan in the brokered XPR. The exact accepted artifact and review rounds are pinned in the [XPR manifest](../../../../docs/peer-reviews/plan/2026-11-26-2026-11-25-agent-owned-closeout-review-6917279c6cb365288f72331515479504/review-6917279c6cb365288f72331515479504-review-manifest.md).

The direct-forwarded capture reproduced the owner-start gap. The retained child stayed unassigned after exact retry in the separate control. [Forwarded capture checkpoint](attachments/qualification/461-forwarded-capture.md).

The disposable agent recovered and published the two exact forwarded turns through the authorized writer. GitHub independently confirmed both bytes and replay remained at the same commit. The composer qualification remains outside the observed #461 result. [Closeout findings](attachments/qualification/461-closeout-findings.md).

[Delivery review](attachments/qualification/461-independent-delivery-review.md) · [Coordinator sign-off](retro/2026-11-25-delivery-sign-off.md).

## Agent Cost

| Agent turn | Measured seconds | Cached input tokens | New input tokens | Output tokens | Cost reference USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Desktop owner capture | 8.242 | 125,568 | 912 | 86 | $0.015241 |
| Desktop supervised child | 2.943 | 42,112 | 728 | 5 | $0.005717 |
| Desktop closeout authority refusal | 16.899 | 127,872 | 5,585 | 610 | $0.030057 |
| Desktop authority readback | 26.447 | 244,864 | 6,010 | 976 | $0.046266 |
| Desktop publication turn | 51.433 | 433,408 | 4,732 | 1,800 | $0.070805 |
| Claude plan XPR round 1 | 33.759 | 289,646 | 35,345 | 4,044 | $0.210753 |
| Claude plan XPR round 2 | 15.863 | 251,553 | 8,260 | 1,930 | $0.077475 |
| Claude addendum XPR attempt, unsealed | 15.657 | 161,378 | 28,651 | 1,694 | $0.147662 |
| Claude delivery evidence review 1 | 41.344 | 658 | 12,064 | 5,291 | $0.101228 |
| Claude delivery evidence review 2 | 36.598 | 12,720 | 12,326 | 4,839 | $0.200190 |
| Claude delivery evidence review 3 | 7.453 | 25,044 | 9,899 | 1,043 | $0.252716 |
| Coordinator turn through native frame | Unknown | 18,585,472 | 338,094 | 48,236 | Unknown |
| **Measured subtotal** | **256.638** | **20,300,295** | **462,606** | **70,554** | **$1.158110** |

Recorded time sums separate observations, including overlap. Desktop and brokered review rows use native boundaries. The delivery review rows use Claude CLI elapsed. New input includes cache writes. The coordinator usage covers native request frames through 2026-11-26T00:46:07.451Z and is partial. Coordinator engagement and cost are Unknown at this cutoff. Verified billed charges are Unknown. [Usage and cost evidence](attachments/qualification/461-agent-cost.json).

## Reopened qualification

The owner asked Grok to reopen #461 and finish the accepted composer test. The forwarded experiment verified exact recovery and publication for that route. The original composer delayed-settlement criterion remains open. The previous receipt identities are retained with their fallback provenance.
