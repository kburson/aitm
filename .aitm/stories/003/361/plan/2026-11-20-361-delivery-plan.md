# #361 Delivery plan

**Goal**

Run the accepted CI sweep on a recurring schedule.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Activate the schedule after #360

- [ ] Inspect the default-branch schedule and #360 workflow, current runner capacity and downstream receipt consumers. Choose a documented UTC cadence, overlap policy and enable/disable path. Decide whether to share or supersede the existing advisory schedule from that evidence and update any dependent contract through its owning scope.
- [ ] Add one schedule trigger using #360's sweep implementation and receipts. Document the expected slot, delay, run and attempt identifiers and operator readback for missed or incomplete results.
- [ ] Prove the trigger wiring with static checks and a manual run, then deliver through the governed PR gate. Observe the first actual scheduled run and reconcile all planned shard outcomes to its exact source and attempt. Retain the observed delay and gaps where applicable.
- [ ] Obtain independent acceptance of the activation evidence and record the schedule's handoff to epic acceptance.

## Activation checkpoint

The existing scheduled full suite shadow runs at 03:47 UTC and has separate receipts. Activate this story by adding one off-hour UTC slot to `category-full-sweep.yml`. Keep manual and scheduled runs in one workflow concurrency group on trunk. Let an active sweep finish and document how GitHub replaces a pending run when a newer one arrives. To disable scheduled registration, remove only the schedule block through the repository's normal PR route. Use the workflow's event-filtered Actions history and the attempt-specific aggregate verdict to distinguish delayed registration, an absent slot, and an incomplete run.

[The #360 delivery hold](../../360/plan/2026-11-20-360-delivery-plan.md#delivery-hold) leaves this story in Backlog. Choose the exact UTC slot after the hosted workflow is accepted, then verify manual wiring and observe a real scheduled occurrence.
