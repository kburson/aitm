---
schema: "aitm.story/v0"
id: 362
title: "Flag a scheduled build failure"
kind: "epic"
state: "done"
issue: "https://github.com/kburson/aitm/issues/362"
parent: null
children: [363, 364, 365, 366]
blocking: []
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-23T00:18:22Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-21-362-delivery-plan.md"], "attachments": ["attachments/2026-11-22-362-acceptance.json"]}
expansions: []
trips: []
---

# Flag a scheduled build failure

[GitHub issue #362](https://github.com/kburson/aitm/issues/362) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 620. Priority P2. Size Feature.

Publish one advisory flag when the scheduled category full sweep fails. Clear it when a distinct, later scheduled run of the same workflow passes. A maintainer or agent checking the flag sees the exact failing attempt and time, or sees that the flag is clear. If the record cannot be read or validated, report that the flag is unavailable.

## Verified prerequisite

#361 delivered `.github/workflows/category-full-sweep.yml` on `trunk` in `kburson/aitm`, workflow ID `425235652`, daily at 23:23 UTC (5:23 p.m. CST / 6:23 p.m. CDT). [Scheduled run 44864075824, attempt 1](https://github.com/kburson/aitm/actions/runs/44864075824/attempts/1) passed with verified shard and aggregate receipts. A delayed or absent slot is separate from a completed failure.

## Children

1. #363 confirms the authenticated workflow, run, attempt and outcome contract.
2. #364 selects the shared storage and read contract.
3. #365 publishes the flag once #363 and #364 are accepted and the receipts agree on the ordering and storage contract.
4. #366 provides the read-only check once #365 is delivered.

Move the epic to Dev before starting child work. Each child delivers via its own PR and needs independent Grok PR review on the current candidate before merging. For receipt-only work the target is `planning`. For implementation the target is `trunk` with the normal required CI and trusted verifier.

## Acceptance

- A verified failing scheduled attempt sets the flag. A later verified scheduled success clears it. Replay shows that cancelled, incomplete, manual, duplicate and stale evidence cannot erase a known warning.
- The human and agent check exposes the same current flag and gives an explicit unavailable result when the record is unreadable.
- Verify the deployed read path with an authentic scheduled run and exercise the failure-to-recovery transitions against an isolated record. Verify that the live record matches the last authentic eligible result afterward. Record each child’s delivery and closeout evidence before epic sign-off.

The publisher runs outside the sweep workflow and writes only to the advisory record. The flag is advisory. Merge policy, required checks, workspace pause, repair assignment and scheduling are outside this epic. #277 and #278 are advisory precedents. #361 is delivered evidence, with no new cross-epic blocker.

[Delivery plan](plan/2026-11-21-362-delivery-plan.md).

[Independent Grok planning review](plan/reviews/2026-11-21-362-grok-planning-review.md).

[Aggregate acceptance and signed delivery](retro/2026-11-22-362-sign-off.md).
