# #118 independent exact source review

Reviewer **Claude Opus 5.5, medium**. Off-platform verdict, November 10, 2026. Signed hosted run 42922357862 attempt 1. Native GitHub review is absent. The reviewer received the full exact diff, the accepted pickup and split, target refresh, authenticated receipt and trusted raw replay.

# Verdict: PASS for #118 M08a

I found no blockers for head `db814e9e8d37e08860e822baed72f917132541a6` and tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad` against literal trunk `679c328204ab797aabdc9a9f93fbf1085d03bb65`. I used only this packet and ran no tools.

## Authority traced through the diff

**Writer custody**
- `Registry.writer()` sets `writer._writer = None` in a `finally` block before the lease closes. Because of that, a reused descriptor cannot bring an old handle back to life.
- `JournalStore._check_root` checks that the lease is the same object and that the root identity matches. `transaction`, `evidence` and `prepare` all touch `writer.lease` first.
- `test_retired_writer_cannot_reopen_or_use_saved_store` covers both a saved store and a reopen through the old handle.

**Source key**
- The store refuses a key ID of `None` before it calls `source_evidence()`.
- `_check_authority` checks three things on every pinned operation: the key is 32 bytes, its SHA-256 matches the expected identity, and the file identity hasn't changed.
- A replacement key with identical bytes is refused. All four key states are covered: uninitialized, unrecorded, missing and changed.

**Genesis and publication**
- Staging is `O_EXCL` 0600 with an identity re-check, then a single-transaction schema, a `TRUNCATE` checkpoint, validation of the database and both sidecars, and fsync.
- Publication uses `publish_noreplace`, which refuses a pre-existing empty target both before and during the race. The old path-based rename isn't used.
- An interrupted root sync is confirmed on reopen. A foreign or damaged store is refused, and its bytes and identity are left untouched.

**Handle authority**
- `_candidates` and `_batches` are per-journal `WeakValueDictionary` maps that require the exact issued object (`is`).
- `reserve` also requires `candidate._read.progress is progress`.
- `replace()` clones, cursors from a different batch, and handles from a foreign journal all fail.

**Fresh authority at write time**
- Inside `BEGIN IMMEDIATE`, `_reserve` does the following in order:
  1. Re-reads the stored cursor and compares it with the prior or progress cursor.
  2. Calls `_fresh_view` with `_confirm_publication=True`.
  3. Recomputes `resolve_route` for each selected observation and requires it to equal the prepared route.
  4. Derives the capture epoch from the current registry.
  5. Repeats the confirmed view and registry comparison before commit.
- A scope or capture change between prepare and reserve therefore invalidates the prepared authority instead of being trusted.

**Visible-but-unsynced state**
- `prepare` may route from a scope event that is visible but not yet synced. However, the reservation is authorised only by the confirmed view.
- `test_journal_reconfirms_visible_scope_replacement_before_durable_progress` shows the failed fsync rolling back both the journal and the cursor, then settling only after confirmation succeeds.

## Narrow routes from the pickup

**Copy identity**
- Claims are keyed by the adapter's native observation key, and the digest excludes physical location. An exact copy gives `REPLAY` and the original claim evidence and cursor are kept.
- The copy stream gets its own cursor. A distinct native retry gets its own key.
- A copy without a verified session is refused at `_stream`, so it never falls back to a locator key.

**First-owner rivalry**
- The first `INSERT` is immutable; there is no `UPDATE` path.
- A rival project adds one dispute row, deduplicated on (key, contender, digest, evidence), with no second payload.
- The first owner is unchanged and the rival stream's cursor doesn't move. Exact retries add nothing. `as_of(before.sequence)` reconstructs the earlier view after reopen.

**Original capture epoch**
- `_evidence` selects the last epoch whose ordinal is at or before the observation's start. It requires that epoch to be enabled and the project to be in `proof.eligible_projects`.
- A later disable or re-enable boundary sits past the observation, so it cannot reassign the observation's epoch.

**Unapplied terminal receipts**
- `_boundaries_settled` blocks the cursor unless one of two things exists:
  - an event at the exact position with an equal native boundary and an `APPLIED` or `REJECTED` outcome, or
  - a resolved hold with a matching receipt pseudonym.
- Any boundary that isn't a `SourceBoundary` also blocks. The terminal fixture proves the cursor stays put, settles after `apply_mark`, and leaves earlier claims unchanged.

**Old or mixed cursors**
- The stored cursor must equal the prior or the progress cursor. Any advance must increase the offset strictly.
- A stale prepared read raises `ConflictError`. A replaced incarnation starts a separate stream with no carried cursor, and `read_source` refuses it.

**Batch completeness**
- The cursor moves only when all of these hold:
  - there are no diagnostics;
  - every selected outcome is `PENDING` or `REPLAY`;
  - every observation outside the selection is excluded for all registered projects and has no overlapping unresolved hold;
  - every receipt is settled.
- A singular reserve on a batch with several observations keeps the prior cursor across reopen. Rollback is atomic, as `test_reservation_and_cursor_commit_together` shows.

**Phase boundaries**
- There is no destination write, acknowledgement, public view, coordinator runtime or fence.
- Revisions other than the first are held for the same owner or a new key. M08b (#199) owns succession.

**Privacy**
- Only normalized usage, the scope, keyed references validated with `validate_source_ref`, UUIDs, ordinals and digests are persisted.

## Follow-up observations (not blockers)

1. **Owner stream stalls after a dispute.** Every read re-reads the stream from the start, so the disputed key appears in the first owner's later batches too. That returns `DISPUTED` and freezes the owner's cursor, even though new claims are still staged. This is consistent with "keeps the earlier frontier replayable", but #199 should state that the release covers the owner's stream as well as the rival's.
2. **Scope is part of the claim digest.** Scope positions are keyed by `source_id`. If a copy's scope timeline differs from the original stream's, a same-owner exact copy may return `HELD`, and whichever stream is read first fixes the claim's scope. This fails safe (no double charge), but #199 should separate scope disagreement from usage changes.
3. **A third source seam.** `ScopeState.view(..., _confirm_publication=...)` isn't one of the pickup's two named seams. It is private, defaults to off, and was added in response to the preflight finding. The checklist should record it explicitly.
4. **Evidence counts don't match.** The raw replay reports `baseline_tests: 876`, but the documented baseline is 877. The diff deletes no tests and adds exactly 43 (30 store and 13 routing), which is consistent with 877 + 43 = 920. Reconcile this before Close. The checklist also still says the hosted run is "pending".
5. **Test gaps worth adding:**
   - usage that follows an unapplied receipt before apply (this verdict relies on the accepted M07 `resolve_route` holding that usage);
   - a scope mark or capture disable between `prepare` and `reserve`, which should raise;
   - a fixture with a revision other than the first;
   - a byte scan of the journal for sentinel values.
6. **Leftover staging directories.** `.journal-initializing-*` directories left by a crash are never swept. They contain only the key ID, inside the private root.
7. **Invalidation raises rather than holds.** A route invalidated between prepare and reserve raises `LedgerError` instead of returning `HELD`. That is acceptable for this dormant slice; M11 callers will need to prepare again.
