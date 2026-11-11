# #227 C01 qualification evidence

**Outcome.** Passed the read-only qualification for #181 Slice C. Automatic field updates remain gated.

## Verified historical parity

A clean detached reader at [delivered dashboard source](https://github.com/kburson/aitm/commit/bc8063b66522ed3a27c95d1bb0546f1e73249612) ran all **61 dashboard tests** with Python 3.13.9. Both historical planning views reproduced byte-for-byte. The validation files bind their snapshot bytes. The #181 standalone HTML also matched. Full SHA-256 values and cutoffs are retained in the [machine readback](qualification.json).

- **#181** at `3a28d392ad0c5782b1898b387a4ecbc8e694ecb1` and `2026-11-11T05:33:20Z` has **10,605,711 ms Partial Actual**. It includes 13,754 ms direct orchestration and 10,591,957 ms across eight descendants. The 27 distinct timing receipt blobs across these nine items matched their journal registrations and exact SHA-256 values.
- **#111** at `17761cc1928fd916cf32a9c078d4a742bfcb32b8` and `2026-11-11T04:23:16Z` has **774,000 ms implementation elapsed** and **Unknown all-phase elapsed**. The historical backfill seed digest matched the accepted design. Both views used an empty usage selector.

To reproduce, use the pinned source with both planning objects available locally. Run the following for each pin and cutoff. Use a fresh output directory outside every Git checkout, then compare the exact digests in the machine readback.

```sh
python3.13 -m unittest discover -s tools/story_dashboard/tests
python3.13 -m tools.story_dashboard.snapshot --repo "$reader" --commit "$pin" \
  --as-of "$cutoff" --output "$output"
python3.13 -m tools.story_dashboard.render --snapshot "$output/snapshot.json" \
  --output "$output/dashboard.html"
shasum -a 256 "$output/snapshot.json" "$output/validation.json" "$output/dashboard.html"
```

## Shared fixture readback

[Portable fixtures for C03, C05 and C06](shared-fixtures.json) define synthetic scopes and half-open intervals. All six cases passed the local checks against the delivered timing fold and legacy usage selector.

| Case | Observed |
| --- | --- |
| Additive and owner wait | 3,600,000 ms Actual with or without 1,800,000 ms owner wait. |
| In-turn tool | One additional qualified 60,000 ms tool span within a separate bound turn brings Actual to 3,660,000 ms. Two distinct pinned synthetic snapshots selected the same usage receipt and both returned $0.0125. |
| Parallel work | 3.25 h Actual, 2h 45m elapsed, 2h 15m observed working wall time and 30m owner wait. |
| Missing and unauthenticated usage | Qualified timing remains measurable when Cost is Unknown. The pre-held timing input contributes no value and carries a gap. The unverified usage receipt produces Unknown Cost with an unverified-usage gap. |

The fixture records ancestry, actor, logical turn, role, attempt, phase and coverage for downstream consumers. The paired local snapshots retain their disposable pins, the same usage receipt digest and exact amounts.

The unauthenticated timing case exercises the fold after rejection. C03 owns qualification of native admission; C05 and C06 own production Project and hosted viewer parity.

## Current capability readback

The [current trunk pin](https://github.com/kburson/aitm/commit/b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5) includes #203 via #211. #203 read back Closed Completed and Done. The installed legacy `aitm-usage 0.1.0` exposes rollup and fixed-sequence export. Running the current source's monitor report with a disposable UUID returned `monitor-report-unavailable` with exit 1. Publication, report window, cutoff and rate basis are unavailable for the fenced production route. No production ledger was opened.

The Project readback matched all nine manual Actual values and Partial labels, with Cost blank. Actual and Cost are NUMBER fields. Actual coverage is TEXT. Elapsed and Owner wait were absent at readback. See exact field IDs in the machine record. Qualification used read-only Project calls.

- **Automatic Actual** still needs the supported Core read and activity/review/attempt contracts (#23, #28, #34, #36), Core release qualification #72, applicable adoption #53–#56, and M2's authorized writer.
- **Automatic Cost** still needs Core #51, monitor #123/#124, and M2's writer. The open monitor predecessor and host qualification statuses are retained in the machine readback. Timing continues independently of usage.
- **Hosted viewer** remains owned by M6. M2 and M6 were draft contracts at readback.
