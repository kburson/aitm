# #358 Parallel category execution findings

The initial serial and concurrent macOS sweeps each covered **2,314 exact IDs** from the accepted [#357 register](../../357/attachments/2026-11-20-357-category-register.tsv). Two setup requirements emerged. The dashboard historical parity test needs a complete standalone Git object store. The real service shutdown test needs normal `SIGINT` handling in the worker and its descendants. The focused corrected replays below show how to satisfy both requirements.

Source was protected trunk `9843874bd00ffa1255b3595987106d5af51dceb3`, tree `b8ca66991842e6b360cf09f0e36b25c693d48390`, on macOS 26.6.2 arm64/APFS with the locked CPython 3.13.9, pytest 9.2.0 and uv 0.10.6. The serial reference used one pytest process per profile. The category run started three category processes after locked setup, with one pytest invocation per nonempty profile within each category. Each had a separate clean checkout, environment, uv cache, short private temp location, basetemp and evidence output. The shard lists preserved original collection order within each profile.

## Outcome comparison

| Initial layout | Exact IDs | Passing | Skipped | Failed | Test elapsed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Serial | 2,314 | 2,311 | 2 | 1 | 615 s |
| Concurrent | 2,314 | 2,310 | 2 | 2 | 437 s |

The concurrent assignments are 483 fast unit, zero slow unit, 1,568 local integration and 263 systems integration. The three product invocations overlapped by 2.268 s. Exact assignments cover each ID once in each layout. Per-ID phase multisets match on 2,313 IDs, including the dashboard failure reproduced by both layouts. The two Linux procfs cases skipped at setup in both. The `cli-help` and `service-one-shot` child witnesses each exited zero in both layouts. These elapsed measurements include the known failures. Full clean outcome parity and concurrent runtime under the corrected layout remain acceptance work for #359.

## Causal replays

- **Standalone Git store.** `tools/story_dashboard/tests/test_timing.py::TimingMetrics::test_real_seed_parity_at_historical_pin` found the historical planning object, then failed in both layouts. `tools/story_dashboard/evidence.py::_Git` rejected the `objects/info/alternates` file created by the initial `git clone --shared`. A standalone local copy with no alternates and the same pinned tree and historical object passed serially and in a concurrent control. Keep historical object `17761cc1928fd916cf32a9c078d4a742bfcb32b8` and use a complete object store. An absent pin can produce a skip and needs explicit disposition.
- **Worker signal handling.** `packages/aitm-usage/tests/test_service_process.py::test_real_service_crash_enrollment_and_private_state` passed serially and timed out in the concurrent run at `_Service.stop`, which sends `SIGINT` and waits 15 seconds. Noninteractive Bash background execution inherited `SIG_IGN` for `SIGINT`; the service depends on Python's `KeyboardInterrupt` handler. A single service test on a standalone checkout reproduced the failure when launched through the shell background route. The same test passed in a foreground invocation and in the concurrent Python-supervised control that preserved the default signal handling across exec. Keep normal signal handling for children and make the coordinator own cancellation and cleanup.

The controlled concurrent replay used separate standalone checkouts for the fast unit pricing test, the dashboard witness and the service witness. This separates launch and Git setup from possible shared-machine contention. No unexplained outcome difference remains in the initial comparison. The corrected controls cover the failing cases. #359 owns the full corrected sweep.

[Comparison and diagnostic readout](../attachments/2026-11-20-358-isolation-evidence.json) · [Raw receipts and replay scripts](../attachments/2026-11-20-358-local-evidence.zip)

## Resources and compatibility

| Resource or boundary | Source witness | Isolation used or required |
| --- | --- | --- |
| Pytest fixtures and imports | `packages/aitm-usage/tests/conftest.py` and the native watch test imports of `test_host_watch` | Separate invocations per category and pytest profile. Use a fresh explicit basetemp and disable the cache provider. The native profile alone adds the product test directory to the import path. |
| Editable package, installed console and wheel upgrades | `tools/ci/tests/test_cli_evidence.py::test_usage_console_help` and `packages/aitm-usage/tests/test_install.py::test_owned_launchagent_and_recoverable_upgrade` | Give each category a separate clean source checkout and locked environment. The installer creates its own temporary runtime and uses a fixture launch controller. Preserve the actual console executable and package metadata. |
| Publication, SQLite and ownership | `packages/aitm-usage/tests/test_install.py::test_restore_fences_publication_until_atomic_swap` and `packages/aitm-usage/tests/test_ledger.py::test_writer_refusal_read_snapshot_and_release_on_process_exit` | Use private state directories and real filesystem capabilities. The race and process locks in these tests operate on the test's own store. A shared state directory would invalidate their independence. |
| Native process state and Unix sockets | `packages/aitm-usage/tests/test_service_process.py::test_real_service_crash_enrollment_and_private_state` and `packages/aitm-usage/tests/test_monitor_scheduler.py::test_real_socket_and_park_cli_retain_only_keyed_wake_bytes` | Fixture-owned subprocesses, private control roots and short temporary path prefixes for AF_UNIX. Child witnesses retain the label and real exit. Product tests use socketpairs or path-bound Unix sockets in temporary directories. |
| Host capabilities | `test_host_watch.py`, `test_host_fs_publication.py` and `packages/aitm-usage/native-tests/` | macOS with APFS exercises the Darwin facilities. Linux needs inotify/procfs and the filesystem primitives used by the fixtures. Linux-only process tests skip on Darwin. The opt-in Darwin watch and ACL tests require a capable Darwin worker. |
| Account ancestry | `packages/aitm-usage/native-tests/test_darwin_acl.py::test_native_home_ancestry_retains_standard_deny_delete_behavior` | Reads the real account's ancestry to check its native ACL semantics. Do not change the account ancestry or substitute a synthetic result. Tests that add ACLs do so on test-owned files. |
| Helper toolchain and Git data | `tools/ci/tests/test_ci_fast_story_shadow.py::test_signature_must_bind_exact_manifest_and_designated_issuer` and `tools/story_dashboard/tests/test_timing.py::TimingMetrics::test_real_seed_parity_at_historical_pin` | Preserve Git objects required by exact historical fixtures and pin the interpreter and evaluated CLI tools. Use a separate temporary Git directory per fixture, disposable SSH keys, and an installed OpenSSH with `-Y`. Do not tie outcomes to mutable author refs. |
| Receipt, cache and optional coverage | `tools/ci/pytest_evidence.py`, `tools/ci/tia/local.py::_temp_environment` and `.github/workflows/ci.yml` | Separate the receipt, basetemp, general temp, uv cache, and environment and artifact output. If coverage is enabled, keep per-invocation files and combine explicitly in the coordinator. This experiment records phase outcomes and child exits. |

The tested configurations use one independent invocation per nonempty category/profile pair. Parent categories can run concurrently, while the profiles inside a category run in the documented order. The slow-unit assignment is empty. Record it as such. An empty assignment has no pytest exit to interpret as success.

| Pair | Same-host disposition |
| --- | --- |
| Fast unit + local integration | Eligible with isolated source, environment, temp and output |
| Fast unit + systems integration | Eligible on a host with the systems capabilities and isolated run state |
| Local integration + systems integration | Eligible with the same private layout and fixture-local locks and subprocesses |
| Slow unit + any category | Empty on this inventory. Apply the same private layout when a measured slow-unit assignment exists |

The two observed failures were explained by the checkout and launch settings. The experiment identified no additional same-host exclusion. The platform-specific tests require the runner with the relevant capability. Host image differences, global locks or workers that cannot provide an isolated filesystem are hold conditions. A missing capability or unsupported profile needs an explicit unavailable or expected-skip disposition. An omitted ID or failed/missing phase receipt prevents a full pass.

## Hosted jobs

Use independent runner instances so one job's caches, paths, process IDs and cleanup cannot affect another job. The existing Ubuntu canonical run for [PR #406](https://github.com/kburson/aitm/actions/runs/44739335469) validates the prior Ubuntu CI setup on the governed PR path. It has a different execution plan. The existing `.github/workflows/scheduled-full-shadow.yml` pins macOS and requires APFS in `tools/ci/run_scheduled_shadow.sh`. Its product and helper scope differs from the five-profile experiment. These references identify runner and tool candidates. Actual category jobs, job queue and setup, artifact identity, failure behavior and union parity need #360 evidence.

For #359, preserve the pinned intake register and detect changes before assigning shards. Preserve the expected different Linux and Darwin node IDs, and the known capability skips, as separate facts. Use the same algorithm in both locations. For #360, start all compatible jobs independently and have an aggregate job verify the planned exact source, profile, shard and attempt. Nothing in this spike changes the ordinary affected-test command, hosted PR path map, CI or the production merge gate.

## Reproduce the local experiment

1. Extract the evidence archive into an empty scratch directory. Supply the accepted `register.tsv` and original Darwin collection TSV from #357. Write one ID per line into `ids/<category>-<profile>` using the Darwin collection order and category lookup. Leave the slow-unit assignment empty.
2. Make four checkout directories named `serial`, `fast-unit`, `local-integration` and `systems-integration`, each pinned to the recorded source. To reproduce the initial diagnostic, use local shared clones. The archived `run.sh` captures each profile into private output. Run `bash run.sh "$scratch" serial "$scratch/serial"`. Then run `concurrent.sh` and `release.sh` with the same scratch root. The latter releases the barrier when all three setups are ready. `compare.py` checks collection and phase parity and emits the reference comparison.
3. To reproduce the focused correction, make three complete standalone local clones named `clean-a`, `clean-b` and `clean-c` and check out the same source. Retain the historical planning object. Run `python3.13 diagnostics.py "$scratch"`. The diagnostic intentionally retains the failed shell-background control and the successful actively supervised replays. The research scripts and defaults are evidence for this pinned experiment.
