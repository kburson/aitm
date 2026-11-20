# #359 Delivery plan

**Goal**

Deliver the opt-in local full sweep from the accepted research.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Deliver the local command after both spikes pass

- [ ] Resolve the manifest format, command entry point, runner selection and fixture layout from the accepted findings. Review existing `tools/ci/tia/shards.py` and `tools/ci/pytest_evidence.py` for reuse against the required contract.
- [ ] Test exact disjoint assignment, new and mismatched IDs, exceptions, missing capabilities, required skip/child evidence, nonzero exits, interruption and missing or stale receipts. Pin expected behavior to the accepted isolation matrix.
- [ ] Build one opt-in sweep entry point and documented replay commands. Keep per-shard state and receipts private and run exclusive work where the matrix requires it.
- [ ] Compare exact inventory and outcomes on the same source against a serial full reference. Show concurrency where allowed and demonstrate controlled failure and absent worker handling. Deliver through exact-head tests and independent review.
