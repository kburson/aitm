# #359 Delivery plan

**Goal**

Deliver the opt-in local full sweep from the accepted research.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Deliver the local command after both spikes pass

- [x] Resolve the manifest format, command entry point, runner selection and fixture layout from the accepted findings. Review existing `tools/ci/tia/shards.py` and `tools/ci/pytest_evidence.py` for reuse against the required contract.
- [x] Test exact disjoint assignment, new and mismatched IDs, exceptions, missing capabilities, required skip/child evidence, nonzero exits, interruption and missing or stale receipts. Pin expected behavior to the accepted isolation matrix.
- [x] Build one opt-in sweep entry point and documented replay commands. Keep per-shard state and receipts private and run exclusive work where the matrix requires it.
- [x] Compare exact inventory and outcomes on the same source against a serial full reference. Show concurrency where allowed and demonstrate controlled failure and absent worker handling. Deliver through exact-head tests and independent review.

## Pickup and exact candidate

Both research predecessors have delivered. The local implementation in [PR #408](https://github.com/kburson/aitm/pull/408) uses the five pytest profiles and reviewed #357 category catalog. It checks inventory before execution, makes standalone copies with the historical planning fixture, and runs each nonempty lane in a supervised process group that preserves the service signal disposition. Per-lane seals bind the plan and hashes of the stock pytest phase and child evidence. The serial mode is the full unsharded reference. The intake catalog adds seven specifically witnessed contract tests.

Target `trunk`, base `9843874bd00ffa1255b3595987106d5af51dceb3`, head `ab9cba596dcf780e950e382ade6010648f572ea6`, tree `27246059c946b67ffa9229c59b6cbc72dd71d4eb`. The story is in Test. Seven focused contract tests passed. Serial and parallel full runs on the same tree and canonical CI have started. Grok must review the current exact head before merge.

## Replacement candidate

Initial head `ab9cba596dcf780e950e382ade6010648f572ea6` passed canonical CI and the full serial sweep of 2,321. Two full concurrent attempts refused a monitor journal fixture setup at the source-custody guard. The first failed case passed five focused replays. A controlled sibling creation invalidated the ancestor ctime check while preserving the file's identity and contents.

[PR #408](https://github.com/kburson/aitm/pull/408) now has head `1ae9553498e37591d1a6e583954e9af6a2bb883d`, tree `56a2841e8091d6a2b848ff1744cfb75256e6fc9c`, against base `9843874bd00ffa1255b3595987106d5af51dceb3`. The runner provisions all lane directories before launching and moves pytest basetemp outside shared system temp. It retains a short private TMPDIR for native socket fixtures. All seven focused tests pass. Fresh exact local runs and canonical CI are in progress. The first head's results remain historical.

[Verified delivery receipt](../plan/2026-11-20-359-delivery.json).
