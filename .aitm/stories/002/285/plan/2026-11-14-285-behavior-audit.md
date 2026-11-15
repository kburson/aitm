# #285 Behavior and execution cost audit

The exact trunk inventory contains 1,740 unique test IDs in 42 source families. The current gate directly invokes 1,412 of them. See the [pinned inventory](audit-inventory.json), [collection and timing provenance](2026-11-14-285-behavior-audit-checkpoint.md), and [behavior by source family](audit-families.tsv). The family table records scope and disposition for all 42 modules. The remaining rows under investigation need detailed case-level evidence before test changes. Unreported individual durations remain unknown.

## Duplicate discovered

The monitor journal's `test_pair_refuses_one_bad_side_without_moving_either_frontier` forms a cross-product of owner/rival and seven refusal cases. In both `swap-owner` and `swap-rival`, the test creates both valid proofs in the same order, calls `good.reverse()` on the same list, then calls the same settlement operation. The branches differ only in a selected carrier and index that the swap code never reads. Both assert refusal, unchanged historical view, durable journal rows and scope bytes, and retained schema version 4. The 5.13s setup for the hosted `swap-owner` phase is a measured consolidation candidate.

A future test-inventory change could retain one swapped-pair test with all assertions and retain both sides for the other cases. Late usage, a copied proof, withdrawn grant, expired hold, changed route, and disabled capture each operate on the selected side. Native proof corruption and the real process, filesystem and installed-upgrade checks are separate behavioral witnesses and stay in scope. Dropping either ID would fail the current #103 protected-base comparison. Retain both rows in this phase and carry this finding forward for an independently reviewed inventory policy decision.

## Recommended first consolidation under #103

In the same high-cost monitor journal family, `test_pair_settles_two_frontiers_and_preserves_first_ownership` repeatedly reconstructs the latest journal snapshot between settlement and the next write. It reads the settled result, reads the dispute set, then reconstructs the same claim list again for each existing claim. Consolidate those redundant reads into a single post-settlement snapshot and keep the exact node ID. Preserve the prior-sequence historical snapshot, both revised cursors, the unchanged scope file and holds, the two persisted progress rows and the explicit second settlement with its post-replay sequence check. #287 owns the test edit, the focused regression witness on a disposable fixture, exact inventory parity and matched timings. Savings are unknown until measured.

## Further investigation

The two largest product files contain 149 and 136 IDs. Scope authority checks and journal role boundaries should be classified separately from their fixture costs. The hosted duration sample shows recurring journal setup, but does not establish fixture reuse safety. Installation, activation and subprocess evidence each carry expensive checks at real product boundaries. Explore setup optimizations without reducing those observations. For adapters, discovery, and other large input families, compare expected outcomes, input contracts and historical regressions before changing parameter coverage.

No tests or production controls changed in this audit. The comparison is tied to the recorded revision and timing sample. It provides no estimate of 3,000-test runtime.
