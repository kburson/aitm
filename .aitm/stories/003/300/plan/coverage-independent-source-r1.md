[22:14:49]
SOURCE_300: HOLD

**Findings**

1. **The stability-selector tests don't actually test most of its guards.** This is in `test_only_stable_profile_denials_become_coverage`, the tests for the selector `_stable_live_exclusion`.
   - Every case except `omitted` runs against `SOURCE`, which has exactly one matching supported installation.
   - For that input the last line, `len(matches) <= 1 and (not source.supported() or not matches)`, already returns `False`.
   - So the tests would still pass if you deleted any of these checks:
     - the `_LiveProfile` type check
     - `profile.lease is not lease`
     - the root path and `_pinned(profile.root)` checks
     - `callable(profile.current)`
     - `validate_source_ref(profile.generation)`
     - `len(matches) <= 1`
   - None of the JIT's "lease/profile/root/key mismatch", "duplicate matches" or "unavailable verifier" routes is really covered.
   - **Fix:** apply those changes to a profile when the source is matrix-excluded (Claude after `qualify`) or has no matching installation, and assert no coverage and that the store stays at v4. Add duplicate matches on an unsupported tuple, a profile of the wrong type, and an untouched profile with Claude that does produce one event.

2. **Paired settlements after a coverage-first upgrade to v6 are untested.** The only paired test goes v5 → v6, with the paired settlement already in place.
   - Nothing tests v4 → v6 through coverage followed by a new paired settlement, i.e. `settle_disposition` → `_enable_paired` on a v6 store.
   - The diff doesn't change `_enable_paired`, and the supplied evidence doesn't show its version guard.
   - The JIT requires it to be a no-op on v5 and v6. If it only skips v5, a v6 store would try to create `paired_settlements` again or reset the schema version to 5. Either would break paired history.
   - **Fix:** add a test that records coverage first, then settles a real paired disposition. Assert the store stays at v6, the coverage event survives, and `as_of` includes the settlement. If the guard is wrong, fix it.

3. **`coverage_changes` has no explicit authorization check.** `prepare`, `_record_live_exclusion`, `_enable_coverage` and `_confirm_live_exclusion` all call `self._writer.lease` / `self.registry.lease`. `coverage_changes` relies only on `self._store.transaction()`.
   - The JIT says reads are allowed only through the live private writer and its pinned lease.
   - **Fix:** add `self._writer.lease` (or show that `transaction()` already checks it). Add a test that a `RoutingJournal` whose writer has exited, or whose lease was lost, can't read coverage.

4. **The test for rejected variants doesn't prove the decoder rejects them.** In `test_coverage_rejects_reserved_variants_even_with_a_valid_row_seal`, the payload and seal are rewritten but the `identity` key isn't.
   - The read would be rejected by the key mismatch alone, whether or not the decoder rejects the variant.
   - **Fix:** recompute `identity` from the altered identity encoding under `journal-coverage-key-v1`, so the only remaining defect is the reserved reason, extent or broader-root field.

**Note (not blocking)**

The Grok preflight puts `_stream`, `cursor_for` and a new `_grok_admission` call in `prepare` inside the try block. The accepted JIT puts the catch directly around the first `read_source` call and doesn't name `_grok_admission`.
- This also changes the error for a Grok source that is unqualified or lacks consent: it now gets the qualification refusal instead of the old cursor refusal.
- A qualifying Grok still gets the old cursor refusal and no payload is read, which the test shows.
- Please record this as a JIT amendment.

**Verified**

These match the JIT and need no changes:
- **Transaction order:** lease → confirmation → enable → dedupe or (`_tip + 1`, commit row, insert) → confirmation → lease. A failed second check rolls back the DDL and both rows, and the store stays at v4.
- **Errors in confirmation:** the listed errors map to the original refusal, and lease loss still raises the lease error from `finally`.
- **Schema:** v6 DDL, `>=` membership and rejection of v7.
- **Upgrades:** reading leaves v4/v5 stores alone; recording coverage upgrades them lazily.
- **Dedupe:** a restart writes no new row and no extra commit.
- **Readback:** each row is checked for canonical bytes, key, seal and commit binding.
- **`JournalChange.coverage`:** the new field can't be combined with a disposition or paired value.
- **No new claims, cursors or ACK; healthy progress:** claims, cursors, dispositions and settlements in `as_of` are unchanged.
- **Results:** the locked suite passed (1272) and all 31 focused cases passed.
