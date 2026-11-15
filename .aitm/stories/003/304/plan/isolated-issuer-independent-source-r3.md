[08:15:00]
**SOURCE_304: PASS**

I reviewed only the evidence in your packet. I had no shell access, so I could not recompute any digest. I checked them for consistency only.

**The three previous HOLD blockers are resolved**

1. **Test inventory:**
   - Base has 1280 tests. Adding the 14 issuer test IDs gives 1294.
   - Adding `test_usage_console_help` gives 1295. That matches the hosted candidate count and the local run (1295 passed).
   - That test is explained as existing wheel-smoke coverage that only the candidate job collects. The workflow excerpt agrees: the candidate pytest command adds `tools/ci/tests/test_cli_evidence.py`.
   - The issuer file shows 14 IDs, and 14 passed. Both previously missing tests are listed. `baseline_missing` is empty.
2. **Audit text reconciliation:**
   - The accepted audit and the merged-base audit differ only in the `Commit` line. The diff has one hunk, and the line numbers 1658, 2462, 2675, 1942, 1822 and 2750 are the same on both sides.
   - Moving from `4cfb418` to `454bddc`, the `monitor_registry.py` and `monitor_scope.py` files are byte-identical.
   - `monitor_journal.py` changed under #310. Even so, `prepare`, `_record_live_exclusion`, `_fresh_view`, `_reserve`, `_settled_side` and `settle_disposition` keep the same AST.
   - The 1599/1745 numbers in the JIT text refer to literal trunk `6b64ea8`, not to the audit file. That conflict no longer applies.
3. **Enclosing handler proof:**
   - `enclosing_function` now records which function holds each match.
   - The test pins three facts:
     - `.decision` is read only by `(monitor_journal.py, prepare)` and `(monitor_scope.py, _confirm_live_exclusion)`.
     - `_confirm_live_exclusion` is called only from `_record_live_exclusion`.
     - `_record_live_exclusion` is called only from `prepare`.
   - `handler-mutation-red.log` shows that renaming the handler to `moved_prepare` makes this test fail.

**Everything is bound to the same commit**
- PR #309 head `a79ac1d`, base `454bddc` and tree `58e5970` are the same across the signed hosted run, the inventory and the pilot's `source` block.
- The hosted reviewed tree equals the tested tree.
- The diffstat matches the diff: 4 files, 436 + 3 + 431 + 541 = 1411 insertions and 1 deletion.
- The pilot passed on Darwin arm64 with Grok 1.0.77, build `50ca579fa996` and the expected digest. It found exactly 1 observation and 1 boundary, was refused after revoke, and did not exercise the journal cursor.

**The earlier non-blocking items are fixed**
- The copy-refusal test now checks the exact refusal message and that the target file does not exist.
- Fixture teardown and the late-recheck test now check the exact refusal type.
- A test now covers the rule that a check from any thread other than the issuer's owner fails closed.

**Remaining non-blocking items, not gating**
- `test_reader_exceptions_fail_closed_and_fresh_writer_starts_closed`, `test_valid_owner_signature_is_bound_to_revision_and_lease` and `test_signed_supersession_invalidates_the_prior_generation` still use `pytest.raises(_LiveSourceUnavailable)`, which also accepts subclasses. Only the reader-exception test is meant to prove the exact refusal type, and it doesn't add a `type(...) is` check.
- The AST comparison doesn't list `reserve`, `reserve_batch` or `_write_progress` as unchanged. The behavior is still covered: the hosted admission and rollback tests call those paths on the exact head and compare the saved durable state.
- The handler-location check matches functions by name only, not by class. The reachability scan still skips `build`, `dist`, `.scratch` and symlinked files.
- The mutation red log comes from the earlier `304-confirmation` run. That holds only because the PR source changes are unchanged since then.
