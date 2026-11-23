# #423 Test Impact Analysis validation

Run this after [#422](https://github.com/kburson/aitm/issues/422) produces the timing and coverage baseline. Pin the literal parent, test tree, host, inventory and commands per candidate. Record expected suites and the relevant source-to-test witnesses before viewing selector results.

| Candidate | Evidence to establish before running TIA |
| --- | --- |
| Leaf module behavior change | Direct suite ownership and a specific failing behavior assertion |
| Transitive dependency change | A multi-hop import witness and an assertion in the downstream suite |
| Shared fixture or configuration | Every suite the fixture or setting can reach, or grounds for full fallback |
| Documentation only | Whether the specific document is executed or consumed by tests |
| Added, renamed and removed tests | Exact candidate inventory and which suites own the changed or displaced IDs |
| Unresolved or dynamic dependency | Which dependency cannot be bounded and when full fallback is justified |

Use the exact-Git-input probe in [the CI guide](../ci.md#probe-affected-tests-for-exact-git-inputs) for plan evidence. Execute the suite-level selected IDs and the independent full inventory in equivalent private checkouts at the same candidate tree. Exercise the hosted advisory path in its supported mode and capture the ordinary required path-map result independently. Record unavailable paths and explain the cause. Use reversible seeded regressions on scratch candidates and confirm the full oracle reproduces each seed. Preserve selector warnings, reasons and explicit fallbacks.

For each candidate retain the predeclared expectation, selection and execution receipts, all full-run failing IDs, any missed failures, mismatched outcomes on common IDs and excess suites or node IDs. Report selection elapsed time, selected execution time, full execution time, fraction of the full inventory run, and coverage footprint where comparable. Use observed witnesses to explain each excess or missed suite. Treat disagreement between repeat oracle runs as inconclusive.

A passing fixture matrix bounds confidence to its candidates and the current suite-level policy. Keep the same candidate protected CI policy throughout. Attach findings to #423 and keep the experiment PR in draft.
