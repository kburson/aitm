# Production PR timing and custody

The final successful #103 attempt completed in under ten minutes on all eight observed PRs. From the first CI registration through the final exact signed job, p50 was **22m 01s**, p95 was **45m 55s**, and **8/8** reached the routine fifteen-minute boundary. The seven historical pre-merge verifier receipts put p95 at **46m 31s** from first registration. These are observed full-gate baseline results. The cohort provides no selected-route or fallback qualification for a replacement gate. [The readiness decision and timing policy](https://github.com/kburson/aitm/blob/6d2a29fdfcef865c6769bfefe1cc07ddc628302f/.aitm/stories/002/294/plan/2026-11-15-294-cutover-and-rollback-plan.md)

## Cohort

The fixed eligibility window includes every same-repository PR opened after [#319](https://github.com/kburson/aitm/pull/319) merged at 15:12:14 UTC and merged into literal `trunk` by 23:35:00 UTC on November 15, 2026. The GitHub PR listing extends below the start and the filtered Actions listing contains all 26 returned runs. The eight included PRs are [#321](https://github.com/kburson/aitm/pull/321), [#322](https://github.com/kburson/aitm/pull/322), [#324](https://github.com/kburson/aitm/pull/324), [#327](https://github.com/kburson/aitm/pull/327), [#328](https://github.com/kburson/aitm/pull/328), [#332](https://github.com/kburson/aitm/pull/332), [#333](https://github.com/kburson/aitm/pull/333) and [#334](https://github.com/kburson/aitm/pull/334). #313, #318 and #319 opened before rollout. #336 was open at cutoff. Five canonical PR runs in the time window belonged to branches opened before rollout, and one belonged to open #336. The PR pairs #321/#322 and #322/#324 were open concurrently for 9m 36s and 16m 32s, respectively.

## Clock definitions and results

The GitHub PR `created_at` starts the whole-PR clock. The first matching canonical GitHub Actions `CI` run `created_at` measures first provider registration. GitHub does not supply a separate triggering-event delivery timestamp in these records. Final exact registration is the first observed run for the landed HEAD. Actual attempt start comes from attempt `run_started_at`. Per-job queue is provider job `created_at` through `started_at`. This queue starts after dependencies are met for downstream jobs. The signed endpoint is the later of signed archive creation and successful `aitm-ci` completion, which was job completion on all eight. The independently traceable source-review endpoint is the protected planning event recording or explicitly referencing an exact passing review receipt. It is a time by which the review was recorded. UTC timestamps and full identities are in the machine-readable results.

The p50 and p95 below use nearest rank, with missing timestamps counted separately. For n=8, p50 is the fourth sorted sample and p95 is the maximum. Times are rounded to the nearest second here. Counts compare exact seconds at or above each threshold. The under-ten-minute p95 and routine fifteen-minute boundary apply to the story verdict from first trigger, for which first registration is the available clock. Individual stage and merge timings illustrate delay sources.

| Interval | n | Missing | p50 | p95 | ≥10m | ≥15m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PR open → first registration | 8 | 0 | 3s | 4s | 0 | 0 |
| First registration → first observed hosted runner start | 8 | 0 | 2s | 3s | 0 | 0 |
| PR open → first native signer success on any head | 8 | 0 | 7m 36s | 19m 37s | 3 | 1 |
| PR open → first registration of final HEAD | 8 | 0 | 15m 54s | 39m 00s | 7 | 5 |
| Final HEAD registration → final successful attempt start | 8 | 0 | 0s | 8m 49s | 0 | 0 |
| Final successful attempt start → exact signed job complete | 8 | 0 | 7m 10s | 8m 36s | 0 | 0 |
| Final HEAD registration → exact signed job complete, including reruns | 8 | 0 | 7m 12s | 15m 59s | 2 | 2 |
| First registration → exact signed job complete, including prior heads and reruns | 8 | 0 | 22m 01s | 45m 55s | 8 | 8 |
| PR open → exact signed job complete | 8 | 0 | 22m 05s | 45m 58s | 8 | 8 |
| Exact signed job complete → historical pre-merge verifier | 7 | 1 | 34s | 36s | 0 | 0 |
| First registration → historical pre-merge verifier | 7 | 1 | 30m 31s | 46m 31s | 7 | 7 |
| First registration → historical verifier and recorded exact source review | 7 | 1 | 32m 00s | 52m 17s | 7 | 7 |
| PR open → landed merge | 8 | 0 | 26m 23s | 54m 48s | 8 | 8 |

The first-registration lower bound for #324 is 15m 29s to the final exact signed job. Its historical pre-merge verifier and independent source-review clocks are missing. The first-registration-to-review comparison includes the later of verification and review in the seven observed cases. PR open to merge includes contributor rework, retry gaps, review and delivery. It is whole-PR elapsed time.

| PR | Attempts | Final Actions run / attempt | Open → first CI | Open → first native signer success | Final attempt start → signed job | Open → final signed job | Open → pre-merge verifier | Open → exact review recorded | Open → merge |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| #321 | 3 | 43740103948 / 1 | 4s | 14m 56s | 7m 50s | 38m 42s | 39m 13s | 39m 21s | 41m 37s |
| #322 | 5 | 43743853023 / 1 | 3s | 19m 37s | 6m 58s | 45m 58s | 46m 34s | 52m 20s | 54m 48s |
| #324 | 2 | 43742232612 / 2 | 2s | 7m 35s | 7m 15s | 15m 31s | Unavailable | Unavailable | 16m 32s |
| #327 | 3 | 43749437105 / 1 | 3s | 10m 24s | 7m 12s | 19m 07s | 19m 43s | 19m 51s | 26m 23s |
| #328 | 2 | 43753448120 / 1 | 4s | 5m 26s | 5m 57s | 18m 28s | 19m 02s | 19m 13s | 21m 11s |
| #332 | 3 | 43761760430 / 2 | 4s | 7m 02s | 7m 10s | 32m 04s | 32m 38s | 34m 41s | 34m 48s |
| #333 | 3 | 43768376715 / 1 | 3s | 7m 36s | 8m 36s | 30m 09s | 30m 34s | 32m 03s | 32m 10s |
| #334 | 2 | 43770857943 / 1 | 4s | 7m 43s | 6m 11s | 22m 05s | 22m 39s | 24m 51s | 24m 58s |

### Canonical lanes and steps

Times are for the final successful attempt of each PR, with n=8 throughout. The first four jobs run in parallel. The collector waited 2s p50 and 3s p95 after the last dependency finished. The signer waited 2s p50 and 3s p95 after the collector. The signed upload preceded final job completion by 2s p50 and 3s p95.

| Lane | Job queue p50 / p95 | Job elapsed p50 / p95 | Main step elapsed p50 / p95 |
| --- | --- | --- | --- |
| `python-base` | 2s / 3s | 3m 15s / 3m 59s | Isolated trusted base inventory and outcomes 3m 04s / 3m 45s |
| `python` | 2s / 3s | 6m 26s / 7m 28s | Candidate input checks 1s / 1s. Test, coverage and child witness step 6m 05s / 7m 07s. Wheel build and installed smoke 1s / 2s at provider precision |
| `quality` | 2s / 2s | 22s / 26s | Lint and format 15s / 17s |
| `file-checks` | 2s / 3s | 14s / 23s | Tracked Markdown, YAML and JSON 5s / 6s |
| `collect-evidence` | 2s / 3s | 12s / 17s | Evaluate and assemble candidate 1s / 1s |
| `aitm-ci` | 2s / 3s | 11s / 23s | Sigstore attestation step 3s / 11s |

Candidate evidence also reports 4s / 9s for dependency setup, 6m 02s / 7m 02s for the post-setup tests and coverage script, and 6m 06s / 7m 07s through the wheel smoke (p50 / p95). All eight final Python receipts marked the uv cache warm. The candidate report field named `queue` measures first-attempt run creation through candidate job start, which is a separate clock at 3s / 26s over six observed values. The workflow leaves this field null on reruns. The native per-job queue above is available for both reruns and all final lanes. Final signed reports contain 1,367–1,487 candidate tests and 1,351–1,472 baseline tests. The cohort contains eight merged PRs over one observation window, with warm final attempts and an existing project workload. It provides neither a long-run percentile estimate nor a 3,000-test projection.

### Attempt history and exact identity

Twenty canonical run IDs for the included PRs cover 23 attempts, with 16 successes and seven cancellations. Seven PRs refreshed their heads. Three run IDs were rerun, including a cancelled older head on #322 and the successful final-head reruns on #324 and #332. #322 also changed the observed signed base from `9de9dbb…` on its intermediate head to `3675e98…` on its delivered head. The exact-candidate interval keeps those changes, including the periods before the final run existed. No required final candidate was omitted for having a cancellation or a rerun.

#324 reports native success at 17:45:53 UTC for attempt 1. GitHub’s retained artifact listing contains only attempt 2 evidence, which uploaded at 17:53:46 UTC. Attempt 1 accounts for the earliest provider signer success, while attempt 2 supplies the time-bound proof used in the final cohort. The reviewed GitHub PR diff changes `README.md` and `docs/blocked-by.md`, so it is outside the existing shadow's `docs/`-only scope. #332's final head attempt 1 had a cancelled Python job, failed collector and skipped signer. Its full attempt 2 succeeded on the same head. The native history does not establish the reasons for all cancellations or for the green #324 rerun.

The signed archive identifies run, attempt, PR, base, head, synthetic commit, tree and signed subject. Replay verified all 15 retained signed archives and their exact commit associations. It replayed the canonical immutable controls, complete job set and authenticated check IDs for all eight final candidates, confirmed the native landed commits use the same ordered parents and tree, and matched all available pre-merge verifier receipts on exact archive ID, SHA-256, subject, jobs, controls and coverage. GitHub returned empty PR-association arrays on historical attempts at readback. Four unproved cancelled attempts across #321 and #322 are included on the unique matching head branch and run time window alone. Two cancelled attempts (#327 and #333) are also corroborated by native PR commit history, as is the first native success on #324 with no retained signed archive. One cancelled attempt on #332 shares its head with the exact later signed proof. GitHub's native Reviews list was empty for each PR. Protected planning carries seven independent exact-candidate review receipts. #324 has neither a historical pre-merge verifier receipt nor a time-bound independent review in these retained sources.

The current verifier's live reference checks depend on an open PR and the then-live target/merge refs. Historical replay establishes immutable proof and independently checks the original protected verifier receipts when available. It does not manufacture open-PR state or a timestamp for the missing receipt. The active native `trunk` rules readback shows PR-required, deletion and non-fast-forward controls and zero required approvals. It has no native required status check. Capture used read-only GitHub requests and the pinned public Sigstore CLI. The canonical workflow bytes and control blob identities agree with the rollout and all eight final receipts. No production workflow, ref or ruleset was changed by this measurement.

## Reproduction

- `cohort.json` preserves the fixed eligibility rule. `capture.py` reproduces the read-only provider requests. `capture-planning.py` exports review and verifier evidence from protected planning commit `6d1f04145dbf60771c1dc476c484d8bde94c3335`.
- `raw/` includes provider PRs, timelines, commits, attempts, per-job steps, artifact listings and signed ZIPs, the downloaded immutable check records, trusted verifier and all signed control source files from rollout commit `75d4bc06657f93f77d6b07e3ae2605cb1c9a269f` and the retained public Sigstore trust root. To recapture the rollout files and public trust root, run capture-trusted.py with a code checkout containing the rollout commit. Live source can be collected again, with possible API retention or readback changes. The recorded data is sufficient for replay.
- From an extracted archive, run `shasum -a 256 -c SHA256SUMS`, then `PYTHONDONTWRITEBYTECODE=1 python3 historical.py` using pinned `gh` 2.97.0 and `PYTHONDONTWRITEBYTECODE=1 python3 measure.py`. The two scripts recreate `replay/historical-validation.json` and `replay/production-metrics.json`. They replay the retained signature bundle with the saved public trust root and perform no production CI or writes.
