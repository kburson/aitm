# #357 Execution-category classification

The exact union of the two collected inventories contains **2,321 unique pytest IDs in 71 source files** at trunk commit `9843874bd00ffa1255b3595987106d5af51dceb3`, tree `b8ca66991842e6b360cf09f0e36b25c693d48390`. Each ID has one placement and a source witness. The register reconciles with zero missing, extra or duplicate IDs.

| Category | Exact IDs in union | macOS collected | Ubuntu collected |
| --- | ---: | ---: | ---: |
| Fast unit | 483 | 483 | 483 |
| Slow unit | 0 | 0 | 0 |
| Local integration | 1,570 | 1,568 | 1,568 |
| Systems integration | 268 | 263 | 268 |
| Outside the four categories | 0 | 0 | 0 |
| Unresolved placement | 0 | 0 | 0 |
| **Total** | **2,321** | **2,314** | **2,319** |

- [Category register](../attachments/2026-11-20-357-category-register.tsv) gives the pytest profile, exact ID, category, host observations, witness key and unit timing disposition. A witness key resolves to a row in the [source and fixture witnesses](../attachments/2026-11-20-357-source-witnesses.tsv).
- [macOS collection](../attachments/2026-11-20-357-collected-nodeids.tsv) and [Ubuntu collection](../attachments/2026-11-20-357-ubuntu-nodeids.tsv) retain original profile order. [Reconciliation and checksums](../attachments/2026-11-20-357-classification-evidence.json) list each exact platform difference, the historical audit delta and evidence hashes.

## Boundaries used for placement

Apply the most specific witness in this order: exact parameterized ID, test function or class-qualified test method, then module. A module rule covers the shared behavior boundary. Parameter values and fixture overrides that change the boundary take precedence. A supported test carries its category even on a host where it skips.

- Unit tests exercise an isolated behavior. A temporary argument, real Git fixture used only to supply an opaque input, or mocked provider response can support a unit assertion. Charge the real fixture setup to the timing.
- Local integration tests observe cooperating components, persisted state, Git objects or files in bounded fixtures. A real subprocess or signer used solely to arrange a fixture is captured as an execution dependency.
- Systems integration tests observe a real host facility, installed environment, or process or tool boundary that is part of the behavior being proven. Examples include native no-replace rename, watch events, installed console enrollment, cross-process ownership and real signature admission. Simulated Darwin ancestry and real Linux process custody have different witnesses even within the same module.
- There are no outside-category IDs and no unresolved placements in the observed universe. Slow unit remains a supported category with zero assignments on this measured baseline. #358 should preserve that empty assignment in its experiments.

## Unit cost calibration

Every unit ID ran serially three times in fresh pytest processes, with a private `--basetemp` and the cache provider disabled. All 1,449 observations contain passed setup, call and teardown. Retain the proposed **100 ms** cutoff on the median of each ID's three total-phase observations. This leaves the common unit workload well below the cutoff without treating setup outliers as stable slow cases. Across the 483 per-ID medians, p50 was **0.610 ms**, p95 was **6.605 ms** and maximum was **90.533 ms**. Two IDs crossed 100 ms in an individual observation. Their medians stayed below 100 ms and the register flags their variability.

The first sample and two immediate repetitions show the effect of re-running the locked selection. Operating-system disk caches were uncontrolled. Timings cover the macOS unit cohort only, exclude pytest startup and collection, and are unsuitable as hosted latency estimates. Integration placement comes from the behavior boundary. The phase observer omits nested subtest reports because their time is already included in the parent call. [Raw phase samples](../attachments/2026-11-20-357-unit-timing.tsv) · [Observer used](../attachments/phase_timing.py)

## Host evidence and limitations

| Profile | Root | macOS | Ubuntu |
| --- | --- | ---: | ---: |
| Product | `packages/aitm-usage/tests` | 1,519 | 1,524 |
| CI helpers | `tools/ci/tests` | 706 | 706 |
| Board | `tools/board_sync/tests` | 13 | 13 |
| Dashboard | `tools/story_dashboard/tests` | 61 | 61 |
| Native opt-in | `packages/aitm-usage/native-tests` | 15 | 15 |

Each host returned exit zero with the same ordered IDs in two collections of each profile. Both used CPython 3.13.9, uv 0.10.6 and pytest 9.2.0 from the trunk lock. macOS was arm64/APFS. Ubuntu 24.04.5 was local Docker arm64 and used the exact trunk archive. Hosted images, schedulability, cross-category interference and outcomes for the entire suite remain outside this experiment.

- The product profile shares 1,517 IDs. Five inotify cases are defined on Linux only. The no-replacement refusal parametrization uses OS errno numbers in its IDs. Darwin `[45]` and Ubuntu `[95]` are ENOTSUP. Darwin `[78]` and Ubuntu `[38]` are ENOSYS. All four exact IDs remain distinct in the register.
- The 15 opt-in Darwin checks collect on Ubuntu and skip at setup. All 15 passed in the macOS probe. The two exact `test_linux_scope_staging_and_hook_recheck_external_process_incarnation` cases collect on both hosts, passed on Ubuntu and skipped on macOS for lack of Linux procfs. Including the watcher and publication cases, the focused probes returned **39 passed / 2 skipped on macOS** and **31 passed / 15 skipped on Ubuntu**.
- `test_darwin_watch.py` imports helpers from the product tests directory, so add it to the module path for native collection and execution. The source witnesses also retain conditional dependencies, including the historical planning Git object, a normalization-alias filesystem case and the installed console. A register value of `collected` records discovery with no outcome claim.

## Reconciliation with #285

The [historical inventory](../../../002/285/plan/audit-inventory.json) contained 1,740 IDs in 42 families. All 42 family paths remain and 29 families were added. The exact sets share 1,736 IDs, with 585 IDs newly observed and four historical IDs absent. Two absent IDs were Darwin-specific verifier capability parameters replaced by Linux capability controls. The other two were the APFS and native-ACL inventory capability parameters replaced by portable capability checks. Exact historical IDs and the new and changed family lists are in the reconciliation record. The audit's partial phases were used to point at fixture costs. This spike uses fresh timing data for each unit placement.

## Reproduction and #358 handoff

Use the commands in the [collection checkpoint](2026-11-20-357-collection-checkpoint.md) independently for all five profiles. For Ubuntu, run those commands with the same lock in an Ubuntu 24.04 arm64 working directory unpacked from `git archive 9843874bd00ffa1255b3595987106d5af51dceb3`. Keep the checkout and output separate. For the focused host probe, run the native profile together with `test_host_watch.py`, `test_host_fs_publication.py` and the exact base function `test_grok_scope_receipts.py::test_linux_scope_staging_and_hook_recheck_external_process_incarnation`, using their product paths and the native import path.

For timings, read the register with a TSV reader and write the unit IDs, one per line in register order, to an argument file per profile outside the checkout. From the pinned source root use the locked interpreter and the phase observer directory on `PYTHONPATH`. Run once per profile for each of three samples with fresh output and fixture locations.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH="$PWD:$PWD/tools/ci:$observer_dir" \
AITM_357_PHASE_TIMING="$phase_output" \
packages/aitm-usage/.venv/bin/python -m pytest \
  -c packages/aitm-usage/pyproject.toml --rootdir "$PWD" \
  -p no:cacheprovider -p phase_timing --basetemp "$private_fixtures" -q "@$node_ids"
```

#358 inherits the per-ID assignment and witness dependencies. Compare serial and concurrent outcomes before making any concurrency claim. Keep temporary fixtures, source exports, cache, installed interpreter, native process state and output receipts attributable to their own invocations. Verify host capabilities and separate expected skips from missing execution. Production test code, the hosted PR path map and CI retain their existing behavior.
