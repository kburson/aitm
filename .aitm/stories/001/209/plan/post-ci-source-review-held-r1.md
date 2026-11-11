# #209 exact source review HOLD

Claude Opus 5.5 medium, independent off-platform source review. Head `b1ec12ad4767edffe3c407dc909556faa39a01fa`, tree `080a9b47a73681e399b73477b67875811efdd234`, literal trunk `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`. Packet SHA-256 `40108faccd6843326b7a3ee46a443fcff60294d2e788994a73eddcc69f7f4bd7`.

HOLD

The product code meets the accepted Refine and JIT. Three test gaps stop acceptance: in each, the JIT's specific requirement isn't proved by what the tests assert. All three fixes are test-only and stay inside the four approved paths.

## Blocking findings

1. **The Claude copy test doesn't prove that the changed scope causes the refusal.**
   - The test is `test_journal_holds_independently_admitted_claude_copy_with_changed_scope` in `tests/test_monitor_journal.py`.
   - The JIT says: "The copy must refuse revision specifically because scope differs."
   - The test shows that the copy's scope is `None` while the live scope is `command.scope`, and that `reserve(...)` returns `"held"`. It never shows why it was held.
   - The copy differs in two ways at once: a different source (`UUID(int=7)`) and a different scope. It also reproduces the same observation key and successor material.
   - The baseline test `test_claude_conflict_requires_distinct_usage_and_current_independent_custody` already holds copies whose usage isn't distinct. So the hold here could come from the duplicate usage or source custody, not the scope.
   - **Fix:** add a same-scope copy control that is otherwise identical and is not held for the scope reason. Alternatively, assert the specific refusal reason or diagnostic. Either way, keep the existing assertions on the saved view and both cursors.

2. **The native v3-upgrade test may never actually create a v3 store.**
   - The test is `test_v3_upgrade_preserves_native_journal_historical_views`.
   - Inside `_open(database, write=True)` it runs `BEGIN IMMEDIATE`, `DROP TABLE route_dispositions` and `PRAGMA user_version = 3`, but never `COMMIT`.
   - The store's own migration path issues an explicit `COMMIT`; `test_legacy_upgrade_uses_one_transaction_and_only_final_version` counts it. If `_open` only closes the connection, the downgrade rolls back. The store would still be v4, and the later `as_of` checks would pass without testing anything.
   - Nothing in the test checks that the store reached v3 before it is reopened.
   - **Fix:** commit the downgrade explicitly. Then, before reopening, assert `user_version == 3` and that `route_dispositions` is gone. After reopening, assert `user_version == 4`.
   - The store-level tests (`_assert_exact_legacy_upgrade` with version 3) do still prove the rows stay byte-identical. So this is a missing proof of historical view stability on native data, not a known product defect.

3. **The late-overlap test doesn't check a replay after resolution.**
   - The test is `test_journal_disposition_preserves_old_projection_when_late_claim_arrives`.
   - The JIT says: "A fresh proposal replay fails after the later usage and after resolution."
   - The test refuses a replay after `_finish_disposition_turn`. It doesn't try one after `scopes.dispose(case.legacy, …)` resolves the hold.
   - The JIT also asks for "prove the #209 record did not move the hold or cursor" in this sequence. This test doesn't check the scope bytes or cursor around `record_disposition`; only the gap/resolved test does.
   - **Fix:** after `dispose`, add a `pytest.raises(LedgerError)` replay check and confirm the views are unchanged. Also check the scope bytes and cursor before and after `record_disposition`.

## Verified

**Store (`_monitor_journal_store.py`)**
- `_supported_schema` builds v1 to v4 as cumulative versions.
- `_validate_identity` admits {1, 2, 3, 4} and nothing else.
- `_initialize_database` adds `route_dispositions` before setting version 4.
- The migration in `JournalStore` verifies exact v2, then v3 only when the store is below that version, then adds the v4 table.
- It sets `user_version 4` once, then validates identity with the pinned key and checks foreign keys.
- These tests cover it: one transaction with a single final version, rollback and retry for v3 (`interrupt` and `replace-directory`), exact v3 upgrade with `content_disputes` rows kept, and the route-disposition table's foreign key, STRICT type and both UNIQUE constraints.

**Old readers refuse v4**
- The frozen readers v1 `1452999b…`, v2 `5324a80b…` and v3 `12825389…` each refuse at the schema gate ("Unsupported routing journal schema version").
- The database bytes are unchanged.
- The `-shm` hash is 32 KiB of zeros and the `-wal` hash is an empty file, which is the clean-close state.

**Row and sequence are atomic (`RoutingJournal.record_disposition`)**
- The authority check, conflict lookup, `_record_sequence`, insert and final `require_route_disposition(change) != record` recheck all happen in one write transaction.
- `test_journal_disposition_rolls_back_sequence_and_row_on_final_recheck` shows that when the second check fails, neither the sequence nor the row is left behind, and a retry then gets `before.sequence + 1`.

**Replay and conflicts**
- A matching payload returns the stored change with its original sequence.
- The same command with a changed payload, or a different command for the same hold, raises `ConflictError`, and the view is unchanged.
- Current authority is required even on replay. Tests cover a copy, a foreign issuer, a consumed request, a revoked grant and an expired witness.

**Stored-row reader (`_stored_disposition`)**
- It checks the commit join, that row and payload UUIDs match and differ from each other, the 64-hex digests, a nonempty span, a Codex TURN terminal, a receipt keyed to the command, session/stream and prefix-stream agreement, ordinal ordering, the hold-state and outcome rules, and exact canonical bytes.
- Tests cover five tamper cases. A lower `as_of` limit still skips the bad row.

**Per-origin overlap (`_affected_disposition_keys`)**
- Each origin is checked against its own project: the first claim, the ownership contender, and both edges of a content dispute.
- Matching needs the exact source, surface, session and stream, with strict half-open overlap.
- Results are deduplicated and sorted by key value.
- The test covers touching endpoints on both sides and every kind of foreign coordinate.

**Historical stability**
- `as_of` projects only rows at or before the limit, using claims and disputes from the same snapshot.
- In the late-overlap test, the views before, at and after the disposition, and after a restart, compare as expected.

**Holds, routes and progress unchanged** (`test_journal_records_native_disposition_without_settlement`, gap and resolved)
- The scope file bytes, `scopes.view()`, the cursor, the earlier rows and the earlier view are all unchanged.

**Diagnostics come from distinct real sources**
- Claude quota: provider, source, stream, `ordinal == quota_at`, and the raw row is a `rate_limit_event`.
- Codex generic gap: provider CODEX, and the raw row is `task_complete`.
- The overlap and mixed tests assert the raw `toolUseResult` and the UNKNOWN availability.
- Grok: a keyed `IDENTITY_CONFLICT`, the `prepare` refusal that records the missing admission, and the Codex claim and cursor unchanged.

**Test IDs and coverage**
- 1,071 retained + 29 new = 1,100. The 29 new IDs match the list.
- No IDs exist only in the hosted run, and the hosted and local candidate sets are equal. All 182 helper IDs are retained.
- Product coverage rose from 10,655/11,604 to 10,730/11,681, and the ratio didn't fall. Helper coverage is unchanged at 778/821.
- The REDs failed on the missing `record_disposition`, and the focused suite then passed (120 passed).
- The hosted attestation names the same head, tree and base.

**Ownership boundaries**
- No settlement, effective hold, folded intent or ACK path was added.
- The comment about the lock gap is in the code.
- #210, #204 and M09 keep the work they own.

## Non-blocking notes

- No test shows that a capped hint which misses a real overlap is ignored. The code never reads hints, so this only needs one assertion.
- A withdrawn reader witness isn't exercised separately from the expired case.
- The retained baseline `test_claude_revision_cold_reads_behind_an_earlier_persisted_cursor` now adds an invalid rate event, so the scenario it originally covered has changed. Confirm that the earlier missing-quota case is still covered somewhere else.
- The Claude quota control asserts source and stream but not scope.

Once these test-only fixes are in, this needs a new exact head and tree, the six hosted jobs, a fresh signed attestation and raw replay, and re-acceptance.
