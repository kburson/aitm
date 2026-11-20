# #358 Delivery plan

**Goal**

Prove which categories can start together and what must be isolated.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Investigate the execution boundaries

- [x] Bind the accepted #357 finding and re-collect if source or profile changes. Preserve the worktree and fixture layout used by the reference.
- [x] Make a resource table per category and exception. Inspect conftests, temp and control paths, cwd/home, installed tools, coverage files, child-evidence paths, caches, ports, locks, watch backends and filesystem semantics.
- [x] Compare serial outcomes with simultaneous independent pytest invocations using private basetemp, state, caches and output. Re-run a discrepancy serially and concurrently. Distinguish contention, permission/configuration faults and resource collisions.
- [x] Inspect runner and dependency setup for independent hosted jobs. Retain approved probe receipts if available and explicitly list hosted claims that still need validation. Name any host-wide reservation, incapable runner, or workload that must serialize.
- [x] Publish command and result evidence, exact test witnesses, and a matrix with compatible pairs, isolation, platform and fallback rules. Work in disposable fixtures and planning evidence only.

- [x] Verify Grok's independent exact-head PR review before merge.

[Findings](2026-11-20-358-isolation-findings.md).
