# #403 hosted Ubuntu requalification after owner review

Disposition **PASS** for the two exact advisory cases. Keep #370 open for receipt acceptance. The required workflow, path map, evaluator, verifier, branch rules, and pinned #355 command retain their current roles.

[Astra-reviewed plan](2026-11-19-370-import-chain-list.md) · [Machine-readable receipt](2026-11-20-370-import-chain-review-requalification.json) · [Implementation PR #406](https://github.com/kburson/aitm/pull/406) · [Hosted run 44739335720, attempt 1](https://github.com/kburson/aitm/actions/runs/44739335720/attempts/1).

## Exact trees

Both jobs fetched the previously authenticated PR merge commits by SHA and verified their ordered parents and trees. They ran on GitHub-hosted Ubuntu 24.04 x64 with pinned CPython 3.13.9 and three xdist product workers. Both used advisory tool commit `fefa1b1a2a1201d052a109d7e15090705253e26e` and qualification workflow commit `d6b6a17db54169cf9b9d57005c83ace29c56f2ed`. Each case ran its comparison on a single runner and on the same tested merge. The full contract contained 1,525 product and CLI tests plus 251 CI helpers.

| Case | Literal base | Divergence | PR head | Tested merge | Tested tree |
| --- | --- | --- | --- | --- | --- |
| [narrow](https://github.com/kburson/aitm/pull/404) | `9e36e31af98e954ed82d745bcbde8e3e12b80623` | `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9` | `dcb0143a1f11480e2c9320f778fc0dcedf435b9e` | `4f825997a90979e7482b53f390597e857ca68704` | `546665c24af2fb203d7ecd8f96b48dcc20f6a9da` |
| [full](https://github.com/kburson/aitm/pull/405) | `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9` | `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9` | `92f54d8fe506bb424db7200b2e0c5b2e01534d45` | `52d3f13fe7ec9e31cca5f7af74c4b8abbfb4aa67` | `878a56d30c07fe37c28305976439d96350cc1ca0` |

## Outcomes and elapsed seconds

The combined lane time includes locked setup, planning where applicable, and pytest command wall time. The fallback and full-map rows reuse the full execution on that tree and add their own planning overhead. Queueing, runner provisioning, artifact upload, the separate green baseline, the post-run probe recheck, and negative controls are outside these timings.

| Case | Lane | Outcomes | Plan | Pytest | Combined |
| --- | --- | --- | ---: | ---: | ---: |
| Narrow | Advisory selected | 12 passed, 8 seeded failures | 10.532 | 15.950 | 26.546 |
| Narrow | Path map full | 1,768 passed, 8 seeded failures | 0.165 | 206.336 | 206.565 |
| Narrow | Full suite | 1,768 passed, 8 seeded failures | 0.000 | 206.336 | 206.400 |
| Full | Advisory full | 1,776 passed | 10.739 | 211.774 | 222.577 |
| Full | Path map full | 1,776 passed | 0.164 | 211.774 | 212.002 |
| Full | Full suite | 1,776 passed | 0.000 | 211.774 | 211.838 |

## Divergent-base narrow mutation

The sole path in both PR comparisons was `packages/aitm-usage/src/aitm_usage/host_watch.py`. The production-only mutation changed the startup reconciliation reason to `seeded-startup`. The literal-base watch suite passed all 13 tests in 1.868 seconds of pytest execution. Candidate watch test bytes matched the literal base.

The advisory run assigned 20 nodes, including 7 mandatory checks. The import witnesses show `test_host_watch.py` importing `aitm_usage.host_watch` in both snapshots. Every full-run failure was present in the advisory run with the same outcome and passed the green baseline. The exact failing IDs were

- `packages/aitm-usage/tests/test_host_watch.py::test_close_wakes_blocked_consumer`
- `packages/aitm-usage/tests/test_host_watch.py::test_linux_new_and_moved_directories_reconcile`
- `packages/aitm-usage/tests/test_host_watch.py::test_linux_registration_bound_falls_back_for_one_root`
- `packages/aitm-usage/tests/test_host_watch.py::test_linux_reports_real_queue_overflow_and_rebuilds`
- `packages/aitm-usage/tests/test_host_watch.py::test_native_watch_reports_change_and_retires_resources`
- `packages/aitm-usage/tests/test_host_watch.py::test_root_loss_and_replacement_are_terminal[None]`
- `packages/aitm-usage/tests/test_host_watch.py::test_root_loss_and_replacement_are_terminal[directory]`
- `packages/aitm-usage/tests/test_host_watch.py::test_root_loss_and_replacement_are_terminal[symlink]`

## Full fallback

The two matching path sets contained only `packages/aitm-usage/src/aitm_usage/monitor_registry.py`. Reverse import traversal reached `packages/aitm-usage/tests/conftest.py`, so the probe assigned the full candidate inventory. All 1,776 tests passed. Both cases had zero advisory outcome mismatches and zero missed failures.

## Evidence checks and boundary

- Verified artifact ZIP digests against the GitHub API and matched the hosted jobs, tool commit, ordered merge parents, tested trees, Linux image, and instrumented pytest outcomes.
- Reconciled complete setup, call, and teardown phases for every reported node. The wrong-tree and wrong-parent controls returned unavailable with zero assignments. A deliberately incomplete full-test receipt was rejected. The post-run probe reproduced the snapshot digest and assignment in each case.
- Preserved the exact node inventories, failures, import witnesses, disjoint bounds, fallback reasons, and lane timings in the machine-readable receipt. [Narrow job](https://github.com/kburson/aitm/actions/runs/44739335720/job/136298690296) · [Full job](https://github.com/kburson/aitm/actions/runs/44739335720/job/136298690655).
- Canonical find_spec bounds include the named target and package initializers. A missing static import uses plausible module paths at the supported roots. Reader reach and unproven package search paths retain full fallback. Runtime file reads continue to rely on declared file inputs.
- The earlier qualification remains evidence for the earlier tool revision. This receipt supersedes it for the current PR head. [Initial qualification](2026-11-20-370-import-chain-shadow-findings.md).
