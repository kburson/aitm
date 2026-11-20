# #361 Delivery plan

**Goal**

Run the accepted CI sweep on a recurring schedule.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Activate the schedule after #360

- [x] Inspect the default-branch schedule and #360 workflow, current runner capacity and downstream receipt consumers. Choose a documented UTC cadence, overlap policy and enable/disable path. Decide whether to share or supersede the existing advisory schedule from that evidence and update any dependent contract through its owning scope.
- [x] Add one schedule trigger using #360's sweep implementation and receipts. Document the expected slot, delay, run and attempt identifiers and operator readback for missed or incomplete results.
- [ ] Prove the trigger wiring with static checks and a manual run, then deliver through the governed PR gate. Observe the first actual scheduled run and reconcile all planned shard outcomes to its exact source and attempt. Retain the observed delay and gaps where applicable.
- [ ] Obtain independent acceptance of the activation evidence and record the schedule's handoff to epic acceptance.

## Activation checkpoint

The existing scheduled full suite shadow runs at 03:47 UTC and has separate receipts. Activate this story by adding one off-hour UTC slot to `category-full-sweep.yml`. Keep manual and scheduled runs in one workflow concurrency group on trunk. Let an active sweep finish and document how GitHub replaces a pending run when a newer one arrives. To disable scheduled registration, remove only the schedule block through the repository's normal PR route. Use the workflow's event-filtered Actions history and the attempt-specific aggregate verdict to distinguish delayed registration, an absent slot, and an incomplete run.

[#360 signed off](../../360/retro/2026-11-20-360-sign-off.md) on the authenticated hosted run. The chosen slot is daily at 23:23 UTC, away from the top of the hour and the separate 03:47 UTC advisory schedule. Record the first actual registration and job start against that slot. The epic was in Dev when this story entered Dev.

## Test checkpoint

[PR #415](https://github.com/kburson/aitm/pull/415) adds the trigger and operator instructions after #360 closed. The manual event still checks the trunk ref and repository default branch. GitHub targets the default branch for scheduled events, so the same trunk requirement applies there without relying on manual event metadata. Actionlint v1.7.12 passed, the existing execution jobs were compared byte for byte and the separate advisory workflow was verified on its existing 03:47 UTC slot. The [canonical PR run](https://github.com/kburson/aitm/actions/runs/44833232145) and exact-head Grok review are in progress.
