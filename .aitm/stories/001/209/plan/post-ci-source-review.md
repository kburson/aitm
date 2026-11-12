# #209 independent exact source re-acceptance

Claude Opus 5.5 medium, off-platform. Head `dab76d25ffdce10d5782e14b5b1ea02f617b235c`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88`, literal trunk `56266ed30bbc572b7e56bc64777e802be264c23f`. Packet SHA-256 `75e44ccd237913caf83e7955be9d98d05c4e3729a16430f27cc0e428085696c3`.

PASS

I worked only from the supplied packet and used no tools. I did not recompute any SHA, check the signature, or run tests. This PASS covers exact source acceptance of candidate `dab76d25…` with tree `b4a757f1…` on literal trunk `56266ed3…`. It does not authorize merge or Close.

## The three earlier HOLD findings are fixed

**1. The Claude copy is held because of scope alone.** The test is `test_journal_holds_independently_admitted_claude_copy_with_changed_scope` in `tests/test_monitor_journal.py`.
- It wraps `RoutingJournal._reserve_revision` and calls it twice on the same connection with the same position, registry, sequence, first claim, held value and content.
- Before the calls, it shows the inputs that could cause a different refusal are equal: `time_basis`, `usage.observed_at` and `_claim_span(position) == _claim_span(first.evidence)`.
- With the copy's `scope=None`, the call returns `held` and never reaches `verified_revision` (`not witness_checks`).
- A version of the copy that differs only by `route.scope = first.material.scope` gets past the scope check and reaches the witness check exactly once, on `(copy._read.batch, candidate.observation)`.
- So the scope field alone decides the outcome. The source and duplicate usage are the same in both calls, so neither can explain the difference.
- `checked == [reproduced]` proves the public `reserve` actually ran through this path.
- The saved view, the copy cursor and the live cursor are all unchanged.

**2. The store really goes through v3 before the upgrade.** The test is `test_v3_upgrade_preserves_native_journal_historical_views`.
- The downgrade now runs an explicit `COMMIT`.
- A separate read-only `_open` then shows `user_version == 3` and that `route_dispositions` no longer exists. Admission accepts only the exact v3 schema, so this is a real v3 store.
- After reopening, `journal._store.transaction()` shows `user_version == 4`, which proves `JournalStore` ran the migration.
- After the upgrade, `as_of()`, `as_of(early.sequence)`, the earlier rows from `_prior_journal_rows` and the cursor all match their pre-upgrade values on real native data.

**3. A replay after resolution is refused.** The test is `test_journal_disposition_preserves_old_projection_when_late_claim_arrives`.
- Around `record_disposition`, the scope file bytes, `scopes.view()` and the cursor are unchanged.
- After `scopes.dispose(case.legacy, …)` resolves the hold, a replay raises `LedgerError("Current scope hold cannot authorize")`.
- After that refusal, the journal view, the resolved scope view and its bytes, and the cursor are all unchanged.
- The replay after the later usage is still refused, and the before/at/after and post-restart historical comparisons are still there.

## Earlier non-blocking notes, also addressed

- `withdrawn` is now its own case in `test_journal_disposition_requires_live_issuer_even_on_replay`.
- `contender_key not in …observation_keys` together with the expected result shows that a scope hint missing a real overlap does not drop it. `_affected_disposition_keys` never reads hints.
- `_assert_claude_cold_read_preserves_cursor` brings back the original no-rate-event case under the baseline ID, using `explicit_quota=False` and asserting that no row is a `rate_limit_event`. The quota case now has its own ID (`explicit_quota=True`). Both check `route.scope` on the candidates.

## Product source

The product source is unchanged from the version the earlier review accepted:
- **Store:** `_supported_schema`, `_validate_identity` and `_initialize_database` support strict v1 to v4. The migration in `JournalStore` checks each intermediate version (v2, then v3 only when the store is older), then sets `user_version 4` once and re-checks identity and foreign keys.
- **Recording:** `record_disposition` checks the commit row and sequence atomically, re-checks authority just before commit, and rolls back on failure. Replay and conflict handling (`ConflictError`) are as accepted.
- **Reading:** `_stored_disposition` is the strict reader. `_affected_disposition_keys` checks each origin separately and requires strict half-open overlap.
- **Out of scope here:** the recording path writes no settlement, effective hold, folded intent or ACK. #210, #204 and M09 keep that work.
- **Old readers:** the frozen v1, v2 and v3 readers all refuse v4 at the schema gate. Database bytes are unchanged, and the sidecars are in their clean-close state.

## Evidence

- **Test IDs:** 1,071 retained + 31 new = 1,102. The 31 new IDs are the 29 from before plus `withdrawn` and `explicit_quota`.
  - No IDs exist only in the hosted run, and the hosted and local candidate sets are equal.
  - All 196 helper IDs from the current base are retained.
- **Coverage:**
  - Product went from 10,655/11,604 (91.82%) to 10,730/11,681 (91.86%).
  - Helper coverage is unchanged at 806/849.
  - Both stay above the raw 90% floors.
- **Hosted run:** attestation run 43136444518 attempt 1 passed. It names the same head, tree and base, and all six jobs are listed.
- **CI controls:** the refreshed control audit shows that only the two journal test files differ from trunk. The workflow and the CI toolchain files match trunk byte-for-byte.

## Non-blocking notes

1. The scope-only control goes through the private `_reserve_revision` seam with a stubbed witness. It is a sound comparison of two calls, but it is not an end-to-end refusal reason. If the product ever adds a typed refusal reason, assert that instead.
2. Two local three-worker runs each failed three different inherited tests, all of which passed when run alone. The trigger is still unknown. Keep it on record and don't rerun until it passes.
3. The hosted baseline has 1,070 tests and the local one has 1,071. The extra local test is `test_usage_console_help`, recorded as a fixed control.
4. The JIT's suggestion to also run the trunk at the time as a v3 reader probe was not taken up. The frozen v3 reader `12825389…` covers this.

Next gates for the owner: recheck the base, PR state, merge rules and native graph, then merge at the expected head and verify parent order, tree and ancestry, then complete Close.
