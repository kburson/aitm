# #360 Delivery plan

**Goal**

Deliver a manually triggered CI full sweep with matching semantics.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Deliver the manual CI sweep after #359

- [ ] Bind the shared local manifest and result contract from #359. Decide workflow and runner mapping after #358's capability results and the local proof. Preserve the ordinary CI workflow's inputs, required checks and authority.
- [ ] Add a separately dispatched workflow with distinct compatible category jobs and an aggregate job. Give each job isolated inputs and outputs. Bind artifacts to source, workflow run, attempt, profile and shard. Apply the accepted exclusive and platform requirements.
- [ ] Verify hosted exact-ID and outcome parity with the local reference, including required children. Exercise a failing category and a missing, cancelled or stale receipt. Capture queue, setup and execution intervals and make the job verdict readable without relying on a single shard result.
- [ ] Deliver through the existing PR gate. Record exact hosted success and the negative control before handing off to #361.
