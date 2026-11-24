# #423 TIA selection against independent full-suite runs

The comparison used the exact #422 delivery, `45db935ac73911b95320a3e38d19f177cedd4fd2`, as the literal parent and selector tooling. The #422 covered reference passed 1,549 product IDs in 105.916 runner seconds with branch and subprocess coverage. This spike measured an uncovered advisory workload of 1,549 product and CLI IDs plus 251 CI helpers on the clean control. Compare the paired spike lanes for speed. [#422 timing and coverage record](https://github.com/kburson/aitm/blob/45db935ac73911b95320a3e38d19f177cedd4fd2/docs/spikes/2026-11-22-422-test-timing.md) · [#422 hosted baseline](https://github.com/kburson/aitm/actions/runs/45318611754/attempts/1).

The suite-level selector used its exact PR input adapter on GitHub-hosted Ubuntu 24.04 x64. The probe emits `local_advisory` provenance. The hosted workflow, image release, ordered synthetic merge parents, tested tree, and artifact ZIP attest where that invocation ran. Each synthetic case is independently reproducible from a single patch to the exact base. The branch runs its own push-only workflow with read-only repository access, and synthetic mutants exist only in runner scratch. The pinned required path map was classified separately on each identical candidate. [Experiment draft #425](https://github.com/kburson/aitm/pull/425) · [Pinned harness workflow](https://github.com/kburson/aitm/blob/ecfe5d9adfc6e763aeea592126269849f22a56e6/.github/workflows/shadow-423.yml) · [Hosted matrix, attempt 1](https://github.com/kburson/aitm/actions/runs/45404317943/attempts/1).

## Measurement

The [reviewed protocol](../plan/experiment.md) predeclared the expected behavior, the safety bounds, and the two failure signatures. Pytest independently sealed candidate inventory and controls before the selector ran. The full oracle and the selected execution ran in fresh same-tree checkouts on one runner for each case, with Python 3.13.9, locked dependencies, three product workers, serial helpers, and coverage disabled in both lanes. The full lane ran first. Full fallback ran a second full-sized lane. Observed IDs and setup, call, and teardown outcomes were reconstructed from raw controller and worker receipts.

Times are single-shot seconds. Pytest wall includes subprocess launch, collection, and execution. Net savings subtract selected pytest wall and probe wall from full pytest wall. Installation, independent collection, queue, and artifact transfer are outside net savings. Small differences in full-sized pairs include ordering and runner noise. The required path map column reports the independent classification only.

## Results

| Case | TIA | PR map | IDs run | Probe s | Selected s | Full s | Net Δ s | Net % |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clean | selected | full | 7/1,800 (0.4%) | 12.441 | 11.943 | 111.425 | +87.041 | +78.1% |
| leaf | selected | full | 20/1,800 (1.1%) | 12.540 | 12.395 | 113.275 | +88.340 | +78.0% |
| transitive | full | full | 1,800/1,800 (100.0%) | 19.160 | 150.192 | 160.230 | -9.122 | -5.7% |
| shared | full | full | 1,800/1,800 (100.0%) | 12.237 | 104.538 | 110.897 | -5.878 | -5.3% |
| docs | full | checks | 1,800/1,800 (100.0%) | 12.442 | 102.108 | 109.833 | -4.717 | -4.3% |
| add | full | full | 1,801/1,801 (100.0%) | 12.389 | 103.168 | 111.989 | -3.568 | -3.2% |
| rename | full | full | 1,800/1,800 (100.0%) | 12.290 | 103.575 | 109.347 | -6.518 | -6.0% |
| delete | full | full | 1,799/1,799 (100.0%) | 12.643 | 102.833 | 111.299 | -4.177 | -3.8% |
| dynamic | full | full | 1,800/1,800 (100.0%) | 12.186 | 103.581 | 112.637 | -3.130 | -2.8% |

| Case | Oracle failures | Missed failures | Outcome mismatches | Extra IDs | Extra test modules | Additional runner suites |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| clean | 0 | 0 | 0 | 0 | 0 | — |
| leaf | 8 | 0 | 0 | 0 | 0 | — |
| transitive | 2 | 0 | 0 | 0 | 0 | — |
| shared | 0 | 0 | 0 | 0 | 0 | — |
| docs | 0 | 0 | 0 | 1793 | 44 | unit |
| add | 0 | 0 | 0 | 1788 | 43 | — |
| rename | 0 | 0 | 0 | 1788 | 43 | — |
| delete | 0 | 0 | 0 | 1788 | 43 | — |
| dynamic | 0 | 0 | 0 | 1780 | 43 | — |

Extra IDs and source modules are above the predeclared behavioral scope and allowed controls. Additional runner suites are extra category labels above that same bound. Transitive and shared use the full predeclared scope. Dynamic also has a separate full safety bound, with zero extra IDs against it.

## What the cases show

TIA reproduced all ten case-specific oracle failures. No selected ID had a different outcome or phase result. The leaf was the only edited candidate that narrowed. Seven edited cases ran their whole advisory inventory and cost 3.130–9.122 s more after the probe.

- **Leaf.** The plan identified all 13 Linux watcher IDs and seven mandatory controls. The selected lane reproduced the eight startup-reason failures with the same phases and outcomes. All eight passed in the clean oracle. It ran 1.1% of the full inventory and saved 88.340 s, or 78.0% of the full lane, including probe overhead.
- **Clean control.** With no changed paths, TIA kept the seven mandatory controls. This corrects the predeclared full-mode prediction for the control. The wrong-tree probe returned `unavailable` with zero assignments.
- **Shared fixture and dynamic import.** The shared-conftest branch was reached in shared. In dynamic, the previously bounded watcher leaf gained an unresolved loader and TIA ran every ID. Both oracle outcome vectors matched clean. The dynamic result matches the declared full safety bound and exceeds the leaf behavior set by 1,780 IDs after controls.
- **Docs.** The tested README-only tree gave `unclassified-change` and a full advisory run. The independent required PR map returned `checks`. The full outcome vector matched clean. The measured advisory selection exceeded the zero-behavior scope by 1,793 IDs after the controls.
- **Inventory edits.** Independent collection observed exactly one new ID for add, one removed and one replacement for rename, and one removed for delete. Removed IDs never ran. All three fell back to full. The probe found existing dynamic readers in `test_monitor_inventory.py` and `test_monitor_qualification.py` on both sides. Rename and delete also reported removed obligations. Add exceeded its module-and-controls scope by 1,788 IDs even though it correctly enrolled the new test.
- **Transitive.** The seeded directory refusal propagated from `sources/scan.py` through `host_watch.py` to the watcher. The full oracle and separate fallback lane reproduced both failures, including the predeclared unavailable-root signature. Both failing IDs passed clean. The probe reached shared conftest and reported dynamic-import uncertainty. The runner image revision differed from the other cases. Both transitive lanes shared that image and runner.

The matrix covers Linux process, filesystem, and watcher tests in the pinned advisory workload, exact synthetic PR-tree inputs, mandatory control execution, and the nine cases shown. It does not estimate a repository-wide false-negative rate, assess macOS-native tests, or establish narrow behavior for unresolved or shared dependencies. The required PR decision is logged for comparison. Production CI, branch rules, path map, and TIA policy are unchanged.

## Reproduction and custody

The [machine-readable comparison](comparison.json) names every job, case identity, fallback reason, expectation digest, exact failure and excess IDs, per-profile outcome counts and timings, ZIP digest, and retained archive hash. Each [structured receipt](receipts/) includes the exact candidate patch and tested commit header, sealed expected and observed IDs, outcome phases, runtime commands, and probe and path-map output. The ZIPs are original GitHub attempt artifacts. The structured copies retain the experiment data beyond Actions retention. The [recomputation](recompute.py) verifies the Actions metadata and all nine ZIP digests, reconstructs tests from worker/controller phases, and independently checks inventory deltas, seed signatures, and scores. Negative control output is in the clean receipt.
