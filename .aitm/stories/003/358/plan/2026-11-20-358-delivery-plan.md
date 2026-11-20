# #358 Delivery plan

**Goal**

Prove which categories can start together and what must be isolated.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Investigate the execution boundaries

- [ ] Bind the accepted #357 finding and re-collect if source or profile changes. Preserve the worktree and fixture layout used by the reference.
- [ ] Make a resource table per category and exception. Inspect conftests, temp and control paths, cwd/home, installed tools, coverage files, child-evidence paths, caches, ports, locks, watch backends and filesystem semantics.
- [ ] Compare serial outcomes with simultaneous independent pytest invocations using private basetemp, state, caches and output. Re-run a discrepancy serially and concurrently. Distinguish contention, permission/configuration faults and resource collisions.
- [ ] Inspect runner and dependency setup for independent hosted jobs. Retain approved probe receipts if available and explicitly list hosted claims that still need validation. Name any host-wide reservation, incapable runner, or workload that must serialize.
- [ ] Publish command and result evidence, exact test witnesses, and a matrix with compatible pairs, isolation, platform and fallback rules. Independently review the pinned result. Work in disposable fixtures and planning evidence only.
