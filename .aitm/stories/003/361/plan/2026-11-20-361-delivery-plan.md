# #361 Delivery plan

**Goal**

Run the accepted CI sweep on a recurring schedule.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Activate the schedule after #360

- [x] Inspect the default-branch schedule and #360 workflow, current runner capacity and downstream receipt consumers. Choose a documented UTC cadence, overlap policy and enable/disable path. Decide whether to share or supersede the existing advisory schedule from that evidence and update any dependent contract through its owning scope.
- [x] Add one schedule trigger using #360's sweep implementation and receipts. Document the expected slot, delay, run and attempt identifiers and operator readback for missed or incomplete results.
- [x] Prove the trigger wiring with static checks and a manual run, then deliver through the governed PR gate. Observe the first actual scheduled run and reconcile all planned shard outcomes to its exact source and attempt. Retain the observed delay and gaps where applicable.
- [x] Obtain independent acceptance of the activation evidence and record the schedule's handoff to epic acceptance.

## Activation checkpoint

The existing scheduled full suite shadow runs at 03:47 UTC and has separate receipts. Activate this story by adding one off-hour UTC slot to `category-full-sweep.yml`. Keep manual and scheduled runs in one workflow concurrency group on trunk. Let an active sweep finish and document how GitHub replaces a pending run when a newer one arrives. To disable scheduled registration, remove only the schedule block through the repository's normal PR route. Use the workflow's event-filtered Actions history and the attempt-specific aggregate verdict to distinguish delayed registration, an absent slot, and an incomplete run.

[#360 signed off](../../360/retro/2026-11-20-360-sign-off.md) on the authenticated hosted run. The chosen slot is daily at 23:23 UTC, away from the top of the hour and the separate 03:47 UTC advisory schedule. Record the first actual registration and job start against that slot. The epic was in Dev when this story entered Dev.

## Test checkpoint

[PR #415](https://github.com/kburson/aitm/pull/415) adds the trigger and operator instructions after #360 closed. The manual event still checks the trunk ref and repository default branch. GitHub targets the default branch for scheduled events, so the same trunk requirement applies there without relying on manual event metadata. Actionlint v1.7.12 passed, the existing execution jobs were compared byte for byte and the separate advisory workflow was verified on its existing 03:47 UTC slot. The [canonical PR run](https://github.com/kburson/aitm/actions/runs/44833232145) and exact-head Grok review are in progress.

## Default-branch activation

[PR #415](https://github.com/kburson/aitm/pull/415) merged at 23:08:52 UTC as `8ab84ba0590286d4655ea94e4d9de99f25ea1f2e` after the [exact-head Grok pass](https://github.com/kburson/aitm/pull/415#pullrequestreview-6000515753), all six [canonical PR jobs](https://github.com/kburson/aitm/actions/runs/44833232145/attempts/1) and the [trusted verifier](../attachments/2026-11-20-361-trusted-verifier.json). The workflow fetched from GitHub at trunk matched the reviewed tree. [Manual rehearsal](https://github.com/kburson/aitm/actions/runs/44834609313) registered on that merge and its first expected scheduled slot is 2026-11-20 23:23 UTC.

The [manual rehearsal](https://github.com/kburson/aitm/actions/runs/44834609313/attempts/1) passed on the activated default branch. Its [authenticated receipt](../attachments/2026-11-20-361-manual-acceptance.json) matches the #360 acceptance run for all 2,333 IDs and 7,083 phases, includes both required successful children and verifies all six artifact digests. The real schedule event remains the final activation test.

At 2026-11-20T23:34:22Z GitHub's schedule-filtered workflow API still showed zero registered runs. The [first-slot observation](../attachments/2026-11-20-361-first-slot-checkpoint.json) captures the authenticated result. This is a pending registration, and does not establish that the event was dropped. Story #361 stays in review.

The follow-up check at 2026-11-20T23:53:21Z again returned zero registered scheduled runs. The manual result and deployed source are verified. Closure requires a recorded schedule event and reconciled receipt from its actual attempt.

## Scheduled acceptance

[GitHub schedule run 44864075824, attempt 1](https://github.com/kburson/aitm/actions/runs/44864075824/attempts/1) closed the registration gap. The [activation receipt](../attachments/2026-11-21-361-scheduled-acceptance.json) records actual registration, job start, exact source, all shard outcomes and verdict reconciliation. [Grok accepted the activation evidence](../attachments/2026-11-21-361-grok-activation-review.md). See the [signed closeout](../retro/2026-11-21-361-sign-off.md).
