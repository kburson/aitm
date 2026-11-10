# #116 M06 exact moved-locator and Claude history re-review

Claude Opus 5.5, medium effort, completed the independent local source review on November 10, 2026. Candidate head `950e0262dba4e2db1b4fe573c898d4b65d7e8ce5`, tree `57e46ef74951a44b21533816171aa3057502178e`, trunk base `37a22922f072e39c35434ae645a1c20692b8da01`. [Signed hosted evidence](https://github.com/kburson/aitm/actions/runs/42889263878/attempts/1).

# AITM #116 M06 follow-up re-review: head `950e0262`, tree `57e46ef7`

**Verdict: PASS.** Both source findings pass, and I found no concrete regression caused by this diff.

I used only this packet and no tools. The signed result names head `950e0262`, tree `57e46ef7` and base `37a22922`, tested on merge commit `6e64c065`. It reports `pass` for all six jobs, with 714 tests and no failures. I'm relying on that result as given; I didn't replay it or check the signature. The count rose by 9 from the 705 at the held head. That matches the 8 new moved-stream test cases plus the new `abandoned` case.

## Finding 1: a stream moved inside the approved installation stalls the edge

**PASS.**

- **Moving is kept separate from absence.** `_locator_lost` now decides first on `locator_is_original`:
  - Old name empty but the same file elsewhere (`same_incarnation`) → `CHANGED`.
  - A different file at the old name (`at_locator`) → `CHANGED`.
  - Neither name nor file found anywhere → `ABSENT`.
  - Original file still at the original name → it falls through to the prefix and size checks. A stream the callback omits while its file still exists returns `None` and is held, as before.

  A moved archive therefore can't count as absent, and a stable walk that proves the old locator is discontinuous uses the bounded gap rule.
- **The supplied-new-path route is fixed.** `_ChangedSource` (an `OSError`) is now caught with `BoundaryUnavailable` and sent to the strict walk instead of the generic hold. The final `except` drops `OSError` only because the earlier branch now handles it. If the walk itself fails, the command is still held.
- **Disable finishes either way.** The test matrix covers callback supplied and omitted, before and after arming, and old name empty and reused: 8 cases, all applied.
  - A moved stream gets `(previous, None)`, so any saved arm is discarded and the gap starts at the last verified prefix. This is conservative and fails closed.
  - `[start, prefix)` stays `ELIGIBLE` and `[prefix, prefix+1)` is `UNKNOWN`. The moved path is never read as a new origin.
- **The moved stream stays gapped.**
  - `enroll_stream` with a proof from the moved path raises `LedgerError`.
  - `[prefix, current)` stays `UNKNOWN`, so there's no backfill.
  - `capture_read_limit(...).ordinal == 0`.
- **A later enable proceeds for healthy streams.**
  - The resume applies on the second pass and `source_read_allowed` is true.
  - The healthy stream's `[fence, enabled_at)` is `EXCLUDED` and `[enabled_at, +1)` is `ELIGIBLE`.

## Finding 2: Claude gaps reach back over completed history

**PASS.**

- **In the adapter (Claude branch):**
  - Only requests that are native to this exact `stream_ref` and have non-empty tokens count. Nested or unqualified streams can't move the bound.
  - `start = max(first_unverified, last_complete + 1)`.
  - Unfinished requests below `start` are no longer held, and neither is `_first_unretained_request` (it now takes `start=`). An abandoned provisional request followed by a completed one therefore can't open a gap.
- **In the registry:**
  - Every candidate gap start is raised to at least `max(earliest, ·)`, i.e. no earlier than `base.ordinal`, so nothing reaches below the verified base.
  - Gaps are computed for disables only. The disabled interval before an enable fence keeps `EXCLUDED`, and this also resolves earlier non-blocking item 2.
- **Spans that are still current or cross the fence remain unresolved.**
  - The `streamed` and `tool` cases still give `UNKNOWN` at `admitted_end+1`.
  - In the `abandoned` case, a span crossing the enable fence (`enabled_at-1 .. enabled_at+1`) is `UNKNOWN`, through the epoch crossing.
  - If clamping leaves no gap (base equals the fence), a crossing span still crosses the epoch boundary and stays `UNKNOWN`.
- **The `abandoned` test covers the requested sequence:** an interrupted request 3, completed requests 4 and 5, a disable, then a resume. The completed span stays `ELIGIBLE` after both the disable and the re-enable. `[expected, enabled_at)` stays `EXCLUDED`, even with provisional request 7 sitting just before the enable fence.

## Other earlier non-blocking items

- **Item 3 (direct-path partial row): closed.** Lines 787–791 refuse a direct arm unless the size equals the checkpoint offset and size and mtime are stable before and after the read. The fence uses the physical `next_ordinal`.
- **Item 4 (empty startup digest): closed.** `_origin` always sets `startup_digest` on a valid origin. An unsupported origin has no provider.
- **Items 1 and 5:** unchanged and still non-blocking.

## Notes (not regressions)

1. **Enable root check.** For enables, the `_check_capture_root` call that used to follow `_capture_gap_start` no longer runs. This is safe if `_capture_position` or `_capture_candidate` already re-checks the pinned root. The packet doesn't show those functions, so please confirm.
2. **`unsettled` lower bound.** The Claude `unsettled` row number is limited only to `≥ first_unverified`, not `≥ start`. The registry clamp to the base still applies, and the `abandoned` fixture doesn't exercise a stale held commit run before later completed requests. A dead commit run followed by completed requests would close this.
3. **Assumes one request at a time per stream.** The rule "a later completed request closes an earlier provisional one" holds if requests in one stream finish in order. Concurrent main-thread requests in one stream would need another look. A truly live request that crosses the fence is still `UNKNOWN` through the epoch crossing.
4. **Broader walk trigger.** `len(supplied) == 1` became `if supplied`, so duplicate candidates now also reach the strict walk. That walk can only prove loss and record a gap, never confirm a boundary. Duplicates with the original file intact still return `None` and hold, which is consistent with the pickup.

The implementer confirmed that `_make_arm` rechecks the pinned approved root after reading the physical capture position for both directions. The disable-only adapter read adds another recheck. The independent reviewer did not submit a native GitHub review.
