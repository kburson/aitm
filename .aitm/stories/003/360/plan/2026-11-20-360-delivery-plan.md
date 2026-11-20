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

## Test checkpoint

[PR #409](https://github.com/kburson/aitm/pull/409) targets trunk base `aded698fdcae8616adefc21c6a64b4f560d7ca3e` with head `ac94f3f9fe207aadcddcb6ee4f7fc82fa683bf29` and tree `bb94080a358e6d921c08d12a6b606745cececf06`. Three new tests and the seven inherited contract tests pass. The matrix assigns shared and Linux-only IDs to Ubuntu, and Darwin-only and opt-in native IDs to Darwin. Artifact names and receipt seals bind the workflow attempt.

[Grok's exact-head PR review](https://github.com/kburson/aitm/pull/409#pullrequestreview-5996159543) passed the code and named canonical CI and the trusted verifier as remaining merge gates. Local matrix qualification is running. The protected default branch registers the new dispatch after merge. A successful hosted manual run and incomplete-run control remain story closure gates.
