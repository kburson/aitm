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
updated: "2026-11-26T00:30:58.044Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/457/attachments/qualification/457-desktop-forwarded-route.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-25-agent-owned-closeout.md", "plan/2026-11-25-forwarded-route-addendum.md"], "attachments": ["attachments/qualification/461-forwarded-capture.md", "attachments/qualification/461-forwarded-capture.json"]}
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
