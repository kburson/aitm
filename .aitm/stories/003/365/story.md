---
schema: "aitm.story/v0"
id: 365
title: "Record the scheduled-failure flag"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/365"
parent: 362
children: []
blocking: [366]
blocked-by: [363, 364]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-22T21:45:03Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-21-365-delivery-plan.md", "plan/2026-11-21-365-jit-and-test.md", "plan/2026-11-22-365-actions-token-amendment.md"], "attachments": ["attachments/2026-11-21-365-trusted-draft-pr-419.json"]}
expansions: []
trips: []
---

# Record the scheduled-failure flag

[GitHub issue #365](https://github.com/kburson/aitm/issues/365) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 650. Priority P2. Size S.

Publish one durable advisory from the authenticated scheduled sweep into the store specified by #364. Begin development after both #363 and #364 receipts are accepted and their ordering and storage contracts agree.

## Acceptance

- A qualifying failure sets or refreshes the alert with the exact attempt and time. A distinct later verified scheduled success clears it. Duplicate, stale, unrelated, cancelled or incomplete events preserve the last verified decision.
- Reconcile from authenticated Actions history. Serialize the two publication triggers and retain the ordering watermark on clear. Fail safely on incomplete history, store errors and ambiguous writes. Verify deterministic replay using an isolated record.
- Bind the publisher to the one advisory store outside the sweep workflow. Verify the deployed record against authentic scheduled history and document recovery for missed updates.
- Deliver the PR to `trunk` with canonical CI, trusted verification and an independent Grok PR review on the current candidate before merging. #366 begins after verified delivery.

[Delivery plan](plan/2026-11-21-365-delivery-plan.md).

[Pickup and candidate verification](plan/2026-11-21-365-jit-and-test.md).

[Owner-approved Actions token amendment](plan/2026-11-22-365-actions-token-amendment.md).

[Verified delivery and sign-off](retro/2026-11-22-365-sign-off.md).
