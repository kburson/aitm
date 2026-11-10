# #116 M06 independent liveness re-review

Claude Opus 5.5, medium effort, completed the independent local review on November 10, 2026. Candidate head `7946c056bb8cdfaf6cd61786296da933be272cbd`, tree `2ed3b6987d46eec348e2e10e9f54a4fc58cfd9b8`, trunk base `37a22922f072e39c35434ae645a1c20692b8da01`. [Signed hosted evidence](https://github.com/kburson/aitm/actions/runs/42882811950/attempts/1).

# AITM #116 M06 liveness repair review: head `7946c056`, tree `2ed3b698`

**Verdict: HOLD.** The repair resolves the idle-stream and deleted-stream stalls, but one blocker remains. If an enrolled transcript is moved to another place inside the approved installation, the disable command stays queued forever, and every later capture command on that project/source edge is stuck behind it. This is the same kind of problem as the earlier blocker A.

I reviewed only this packet and used no tools. The signed evidence names head `7946c056`, tree `2ed3b698` and base `37a22922`. It reports `pass` for all six jobs, tested on merge commit `57c1572e`, with 705 tests and no failures. I'm relying on it as given and didn't replay it or check the signature.

## Earlier hold items

| Item | Status |
|---|---|
| A: an idle stream stalls the edge | **Resolved.** The writer arms at the current physical file position, which counts every row including malformed and oversized ones. A partial last row is gapped. The second pass checks the same fixed byte prefix, so a quiet stream reaches its fence. Tested for the `idle` case, across a restart. |
| A: a deleted stream stalls the edge | **Resolved when the file leaves the installation.** A strict metadata walk sees neither the old file name nor the same physical file anywhere, and records the last verified prefix plus an open-ended gap. Tested for `removed` and `removed-after-arm`. |
| Ordering of requests still in progress | **Resolved for the queued path.** The fence is the file size at arming, including a partial row. Open Codex turns are gapped from their start row and Claude unfinished requests from their original row. Tested for an open turn, a partial row, a row completed after arming, and Claude quiet, streamed and tool cases. A small leftover on the direct path is listed under non-blocking items. |

## Blocking finding: a stream moved inside the approved installation holds the edge forever

There are two code paths, and both end in a permanent hold:

1. **The callback supplies the stream at its new path.** Discovery finds the same `stream_ref` at a different file name, so `_make_arm` → `_capture_position` → `_capture_cursor_identity` raises `_ChangedSource` because the name differs. That is an `OSError`. `_make_arm` only converts `_CaptureDiscontinuity`, so the error reaches the loop's final `except (LedgerError, OSError, ValueError): held = True`. The strict walk in `_locator_lost` is never consulted.
2. **The callback omits the stream.** `_locator_lost` sees that the old name is gone (`at_locator` false) but finds the same physical file elsewhere (`same_incarnation` true). It skips the `not same_incarnation` branch and the prefix and size checks only apply to the file at the old name, so it returns `None`. The result is `BoundaryUnavailable` and a hold.

Neither state ever clears, so:
- `capture disable` stays `queued proof-unavailable`;
- the later re-enable or disable on the edge is skipped through `held_edges`;
- `enroll_stream` and direct `set_permission` stay blocked while the command is pending.

Reads stay fenced, so this fails closed for data. For liveness it is the same failure as the earlier blocker A.

**How likely this is:**
- Codex archives sessions by moving rollout files into `archived_sessions`. If the approved root covers both directories, an ordinary archive action triggers this. I can't tell from the packet which root is approved.
- The scanner test `test_capture_locator_presence_finds_moved_inode_and_replacement_type` confirms the walk reports a moved file this way (`not at_locator and same_incarnation`).
- The registry tests avoid this case. `test_returning_original_stream_needs_prospective_enrollment` and `test_reappearing_stream_invalidates_an_earlier_absence` both move the file to `tmp_path`, outside the root.
- The handling is also inconsistent: a temporary move outside the root is gapped, while a lasting move inside it holds forever.

**Authority:** the pickup says a moved archive must not count as *absent*. It also says that when "the old locator now prove[s] a permanent discontinuity, use the bounded gap rule," and that a discontinuity "cannot reject an otherwise valid disable." A stable full walk showing the old name gone and the same file elsewhere proves the old locator is discontinuous. It isn't absence, and it isn't ambiguous.

**Needed:**
- Treat a stable walk that finds the old name gone and the same file elsewhere as `_LocatorLoss.CHANGED`: record the last verified prefix plus an open-ended gap, and never claim the session ended.
- Treat the related case the same way: a different file at the old name while the original file sits elsewhere. Today that also returns `None`.
- Route a supplied candidate whose name differs from the enrolled cursor through `_locator_lost` instead of the generic `OSError` hold.
- Add registry tests for a disable with an enrolled stream moved inside the approved root, both before and after arming, once with the callback supplying the new path and once with it omitted.
- Check that a later re-enable on the edge then applies, and that the moved stream can't re-enroll under its old key or backfill its gap.

## Required before PASS: Claude gaps can reach back over completed history

`_capture_gap_start` (Claude branch) rebuilds the session from offset 0. It adds every `request_prefix` entry with `not item.complete and item.tokens != _EMPTY`, with no lower limit.

Consider an interrupted Claude response: `stop_reason` is null and it never finishes. That is the same shape as the `streamed` fixture. Its original row number then becomes `gap_start` on every later queued capture change for that stream.

`span_disposition` returns `UNKNOWN` as soon as any epoch's gap overlaps a span. So:
- completed requests after the interrupted one, which sit wholly inside an admitted interval, become `UNKNOWN` for settlement of already-staged evidence;
- if the interrupted row comes before an earlier fence, spans in a disabled interval become `UNKNOWN` instead of `EXCLUDED`.

This conflicts with the M06 rule that "a span wholly in an admitted epoch remains eligible … even if its revision arrives after disable," and with the design rule that a disabled interval stays excluded. The refinement's "earliest affected original ordinal" covers an affected request that crosses the fence, and an abandoned request from earlier in the session doesn't cross it.

**Needed:** do one of the following, with a test in which an interrupted request is followed by completed requests before a disable and then a re-enable:
- limit Claude's held row numbers to requests that can still cross the current fence, never earlier than the stream's latest fence or its verified base; or
- show that `request_prefix` drops abandoned provisional requests.

## Verified areas

- **Source identity and revocation:**
  - `_capture_candidate` checks the root's physical identity, the key, the namespace, a unique current stream, and the platform, surface and provider.
  - `_verify_capture_tuple` checks the client and format version against the file's own startup row.
  - A substituted root, a platform change, a version change, a rewritten prefix or an in-place session swap all commit the disable with the last verified prefix plus an open-ended gap. The replacement root is never read.
  - Restoring the original root or file doesn't reopen reads (`source_read_allowed` false, `capture_read_limit` `(0, None)`).
- **Fixed absolute positions:**
  - `_capture_extent` hashes and counts the same descriptor bytes. The saved arm is rechecked with `fixed=saved.position` and never moves.
  - A file that grows after arming leaves the fence in place.
  - Zero-offset origin authentication works, and an empty truncated file can't claim an origin.
- **Pending read limits and durable progress:**
  - While a disable is pending, each stream is limited to its arm, or to its verified base or progress if it has no arm.
  - `CaptureProgress` carries a service-keyed proof bound to the edge, file name, file identity, offset and row number. A forged row number is held, never used.
  - Progress beyond an arm is refused.
- **Explicit gaps without backfill:**
  - An open-ended gap epoch is skipped by later commands, and only a fresh `enroll_stream` with exact continuity closes it (proof offset ≥ `position`, row number > the fence).
  - The returning-stream test confirms `UNKNOWN` over the gap.
- **Temporary versus permanent evidence:**
  - A missing callback result, duplicate candidates, transient I/O and a parser `ValueError` hold the command.
  - A proven loss commits a disable and can reject an enable.
  - An absence proof is recomputed on each pass and never saved.
- **Queue order and atomicity:**
  - The registry enforces one pending command per project/source edge. Later commands are skipped through `held_edges` and wait for it.
  - Arms are saved before application is tested, and a pass that adds new arms saves again before applying.
  - The submission order is only compared within one pass, never after a command is retired.
- **Ownership:** the native-proof-only direct path is kept, and the tail-fence, gap and progress proofs use separate key namespaces. No scheduler, journal, service or adoption work was added.

## Non-blocking items

1. **Deleted approved root.** If the whole approved root is permanently gone, `ENOENT` becomes `BoundaryUnavailable` and holds forever when the edge has streams. Reads stay closed through `_pinned`. Consider stating that this permanent hold is accepted, or add an owner cancel later.
2. **Later re-enable gaps a disabled interval.** For an enable whose stream is armed only in a later pass, `later=True` gaps from the disable fence. The disabled interval then reports `UNKNOWN` instead of `EXCLUDED`. Limit the gap to where the arm starts for enables.
3. **Direct-path partial row.** `_native_delta` derives `last_ordinal` from the checkpoint offset plus the boundaries it saw. A row that was only partly written when the frontier was recorded, and later completes as a boundary, could still become the direct fence. Using the snapshot's full row count, partial row included, as the floor would close this.
4. **Change to ordinary scans.** `_validation_ref` now raises `_CaptureDiscontinuity` (reported as `SOURCE_REPLACED`) for an offset-zero cursor whose `startup_digest` is empty. Normal `scan` callers could see this, which goes against "no change to normal read_delta." Please confirm no provider produces an origin without a startup digest.
5. **Inconsistent enable outcomes.** For an enable, a proven tuple or discontinuity loss rejects the command through `_CaptureSourceLost`, while a strict-walk `CHANGED` result gaps and applies. Both fail closed, but one outcome would be clearer.

**Verdict: HOLD.** The moved-stream blocker needs fixing and tests, and the Claude reach-back needs either a lower limit or proof that abandoned requests are dropped.
