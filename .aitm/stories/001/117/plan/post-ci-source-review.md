# #117 independent source re-review, attempt 2

Reviewer **Claude Opus 5.5, medium**. Verdict returned November 10, 2026 at 21:14 UTC. Off-platform packet review. Exact head `1b47aa275370482e7b822ce80883549f15158d82`, tree `200b4b337bd1e0f784aba4adff7689d80158858f`, base `0175e77c398dc97c59db166fa64e2e9a673b4b40`. Signed hosted run 42902029986 attempt 1.

# PASS: #117 M07a at `1b47aa2`

**Verdict: PASS.** The original HOLD is fixed and I found no material regression in the diff. As instructed, I reviewed only this packet, used no tools and treated the signed CI evidence as given.

## How the fix works in `ScopeState._apply`

1. **Order of checks.** `_require_boundary` still runs first. It needs the writer-owned sealed proof, rechecks the batch and anchor, and confirms the command's bytes, authority and Develop owner proof. An exact retry of a command that already has an event still returns `old.reported` with nothing saved.
2. **Any existing hold for the command ID is now final.** If the hold's position or digest doesn't match the retry, the code raises `ConflictError`. Otherwise it drops the authorization and returns:
   - `HELD` when the hold is `HELD` or `GAP`. This behaves the same as before.
   - `REJECTED` when the hold is `RESOLVED`. Before this fix, that case reached `_timeline` and `_save`.
   - The affected span is the hold's own span in both cases.

   Neither path calls `_timeline` or `_save`, so a rejected proposal can no longer take effect later.
3. **Effects of the change.** The only path that behaves differently is the one for `RESOLVED` holds, so the blocker is fixed with the smallest possible change. The same rule covers `Mark`, because `apply_mark` goes through `_apply` too. Expired holds still report `HELD` and release no usage.

## How `receipt` behaves

`receipt()` checks committed events first, then disposition resolutions (keyed by the disposition's own ID), then holds. H never gets an event, so `receipt(H)` keeps returning the stored `RESOLVED` hold.

The snapshot is never written on the rejection path, so nothing changes between calls and the receipt stays the same before and after a retry or restart.

## The new regression test

`test_resolved_hold_rejects_original_handoff_after_restart` covers what you asked about:

- **Append-only stream:** both H (`held_at`) and D (`resolved_at`) are appended and stay in the stream. The test asserts `held_at < resolved_at < hold.affected.end`, which matches the scenario in the original HOLD.
- **Before reopening:** the disposition resolves the hold, `receipt(H)` equals the resolved hold, and routing at `held_at` returns `original` (A-116).
- **After reopening the writer:** the test builds a fresh `ScopeState`, authorizes H again, rereads the source and verifies H at the same `held_at` target. That retry is a real attempt to apply H. Then:
  - the status is `"rejected"`;
  - `affected` equals the resolved hold's span;
  - `view().events` is unchanged, so no new event was saved;
  - `receipt(H)` still equals `resolved`;
  - routing at `held_at` still returns `original`, so the prior owner keeps the attribution after the reopen.

## CI

Head, tree and base match the packet, the status is `pass` and all six jobs are present. There are 748 tests, which is 747 plus the new one. Product coverage is 91.13% (9096 of 9981 lines) and helper coverage is 94.76% (778 of 821). The two new trunk paths in `tools/ci/tia/` are byte-identical in the candidate and in trunk, and they don't touch scope code.

## Advisory (not blocking)

1. **Retry and receipt return different types.** A retry returns `HandoffDisposition(REJECTED)`, but `receipt()` returns the `ProofHold`. The `HELD` path already worked this way, so this isn't new. M07b #182 should handle both types when it admits commands.
2. **The test doesn't check that the authorization was used up.** It doesn't assert that the rejected retry dropped H's authorization. The code does drop it.
3. **One advisory is still open from the first review.** The raw replay still reports `baseline_tests: 713`, while the pickup recorded 714. This needs reconciling before closure, and the helper count still doesn't appear in the replay. The other advisories from the first review still apply as written.
