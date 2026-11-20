Verdict: PASS
https://github.com/kburson/aitm/pull/407
Base: 5393b8972698d7725ab41189a38226dfcc11c3d2
Head: bcd23343416998b403d026abb0ca87ba351a5b40

## Scope

Planning-only spike receipt for #358 on `planning`. The diff updates `.aitm/stories/003/358/story.md`, `events.jsonl`, and `plan/2026-11-20-358-delivery-plan.md`, and adds `plan/2026-11-20-358-isolation-findings.md`, `attachments/2026-11-20-358-isolation-evidence.json`, and `attachments/2026-11-20-358-local-evidence.zip`. No product, CI, or workflow code changes. Story state moves `backlog` → `develop` at `2026-11-20T15:33:56Z` with a matching `core.state.entered` event and `last-branch: codex/358-category-isolation`. The plan leaves “Verify Grok's independent exact-head PR review before merge” open. This review is that exact-head check.

The spike question is which category processes can start together and what must be isolated. The findings answer it for one macOS host and leave full corrected parity to #359 and hosted category jobs to #360.

## What holds

The inline experiment JSON (`schema` `aitm.358-isolation-experiment/v1`) matches the findings narrative, and the profile totals partition.

- Serial profiles are 15 native + 1,519 product + 13 board + 706 ci + 61 dashboard = 2,314.
- Category shards are 483 fast-unit + 0 slow-unit + 1,568 local-integration + 263 systems-integration = 2,314.
- The same IDs split back by profile: product 106+1,297+116 = 1,519, ci 346+239+121 = 706, board 12+1 = 13, dashboard 19+31+11 = 61, native 15.
- Phase-report counts match across layouts for every profile (product 4,555, ci 2,118, board 39, dashboard 257, native 45).
- Serial checks are 2 skips and 1 failure (2,311 passed). Concurrent checks are the same 2 procfs skips and 2 failures (2,310 passed). `outcomes_identical` and `all_exits_zero` stay false.
- The only phase delta is `packages/aitm-usage/tests/test_service_process.py::test_real_service_crash_enrollment_and_private_state` (serial call passed, concurrent call failed). That leaves 2,313 IDs with matching phase multisets, including one shared failure.
- Skip witnesses match on both layouts: the two `test_linux_scope_staging_and_hook_recheck_external_process_incarnation` cases, reason “Requires the Linux proc filesystem”.
- `cli-help` and `service-one-shot` each have count 1 and return code 0 on both layouts.
- Integer start/finish epochs match every `elapsed_seconds` value. Serial wall time is 615 s (`1795189361 − 1795188746`). Concurrent wall time is 437 s (`1795189803 − 1795189366`). Within each category, profiles are sequential; the three categories overlap. Fast-unit, local-integration, and systems-integration product shards can overlap for about 2.3 s while fast-unit product is alive; local and systems stay overlapped much longer. `three_product_shards_overlap_seconds` of 2.268 fits that window.
- Focused replays match the two causal claims. `shell-background-service` exits 1 with `signal_handler` `"1"` (`SIG_IGN`) and runs ~18.8 s. `standalone-service-serial` and `standalone-service-concurrent` exit 0 with `default_int_handler` in ~5 s. The concurrent service, history, and fast-unit controls actually overlap (`start_ns` within the same second) and exit 0. History serial and concurrent standalone replays exit 0. The signal probe records foreground `default_int_handler` and noninteractive shell background `"1"`.
- Pinned source is trunk `9843874bd00ffa1255b3595987106d5af51dceb3`, tree `b8ca66991842e6b360cf09f0e36b25c693d48390`, on macOS 26.6.2 arm64/APFS, CPython 3.13.9, pytest 9.2.0, uv 0.10.6. That commit is the code under test; this PR head only carries the planning receipt.
- Resource table and same-host pair matrix name private checkout, env, uv cache, basetemp, state, Unix-socket temp paths, receipts, and a complete Git object store (historical object `17761cc1928fd916cf32a9c078d4a742bfcb32b8`, no `objects/info/alternates`). Empty slow-unit is recorded as having no pytest exit. Platform skips and incapable runners are hold/skip conditions. Ubuntu run `44739335469` and `scheduled-full-shadow.yml` are cited as different plans, with real category-job proof left to #360.
- Internal links among the new story, plan, findings, and JSON/zip paths resolve. `files.plan` and `files.attachments` list the new artifacts.

CPython preserving `SIG_IGN` across startup, so a shell-backgrounded worker never installs `KeyboardInterrupt`, is the right reading of `signal_handler: "1"` versus `default_int_handler`. The initial concurrent service failure is a launch-disposition fault. The shared dashboard failure is a checkout-layout fault (`git clone --shared`). Both are reproduced in the focused controls. No third outcome split is present in `phase_report_differences`.

## Evidence limits

These limits are disclosed so the acceptance claim stays tied to what this review actually saw. They do not overturn the written macOS result.

- This review did not execute pytest, the archived scripts, or any repository command. It did not unpack `attachments/2026-11-20-358-local-evidence.zip`, recompute `archive_sha256` `84bdae431ef12c98746a024dd1ca6213fd1613857ea27599e33ccbbfd59ab784`, or recompute `register_sha256` `0204389741ccefb4a1e1f013b8547c9f9b418dd462a0131d4c69e8cd10e7ba3c`. The patch stores the zip as a binary diff. Zip member list, script text, raw pytest tracebacks, and secret scanning of the archive are outside this review. The coordinator attestation that the zip checksum and ID-union comparison match the captured receipts is the check for those bytes.
- The shared failing nodeid is named in `plan/2026-11-20-358-isolation-findings.md` (`tools/story_dashboard/tests/test_timing.py::TimingMetrics::test_real_seed_parity_at_historical_pin`) and is the test the standalone history replays collect. The JSON records aggregate failure counts and the service-test delta, and does not itself list that shared nodeid. Counts allow exactly one shared failure. Identity of that failure in the initial full runs sits in the findings prose plus the zip.
- ID-level union is supported here by the partition arithmetic above. The nodeid lists and the #357 TSV were not re-diffed in this review.
- The resource table covers AF_UNIX and socketpairs. It does not name a TCP port witness. A host-port collision that failed a test would appear in the phase delta; none does.
- The GitHub Actions run URL was not re-fetched. The findings already treat that run as a different execution plan.

## Merge

Safe to merge to `planning` as the #358 diagnostic receipt. It records private-layout concurrency for the three nonempty categories on this Darwin host, requires a complete Git object store and normal `SIGINT` handling, and keeps hosted jobs and the full corrected sweep on #359 and #360. `outcomes_identical: false` remains the correct initial-run result. Ticking the plan’s review box would be a later commit; this review covers head `bcd23343416998b403d026abb0ca87ba351a5b40`.
