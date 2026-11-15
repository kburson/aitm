[06:26:19]
**SOURCE_304: HOLD**

I used only the supplied evidence. I couldn't recompute any digest, so I checked them for consistency only.

**Unresolved blockers**

1. **The test inventory is stale and doesn't match the reviewed head.**
   - The signed inventory says 1290 tests, with 13 new node IDs. The gate and the local run both report 1292.
   - `test_isolated_qualification.py` now has 14 tests, and all 14 passed locally. The inventory leaves out two of them: `test_closed_resolver_cannot_copy_the_unpatched_codex_fixture` and `test_revocation_is_terminal_and_writer_thread_is_private`.
   - The inventory lists `tools/ci/tests/test_cli_evidence.py::test_usage_console_help` as new. The full diffstat changes only 4 files, and none of them is that file, so nothing explains why this test is new.
   - Fix: re-sign the inventory at `d511c86` / `d2168c6` with 15 new node IDs (1277 + 15 = 1292). Then either explain why `test_usage_console_help` is collected on the candidate but not on base `4cfb418`, or correct the base count.

2. **The supplied listings contradict the audit-digest claim.**
   - The accepted digest `94be…` differs from the base digest `327a…`. The record says the texts match exactly except for the commit label.
   - The two listings supplied also differ in every line number (for example `_recheck_batch` moves from 1599 to 1658, and `settle_disposition` from 1745 to 1911). All three blob digests differ too.
   - The caller/callee structure is identical, which is the part that matters. But either the recorded claim is wrong, or the digests cover text that wasn't supplied.
   - Fix: supply the two audit texts that produce those digests, or a diff between them, showing they differ only in labels, line numbers and blob digests. Then correct the record.

3. **The reachability test no longer enforces JIT condition 3.**
   - The old test tied each check to a specific function:
     - `.decision` read only in `(monitor_journal.py, prepare)` and `(monitor_scope.py, _confirm_live_exclusion)`;
     - `_confirm_live_exclusion` called only from `_record_live_exclusion`;
     - `_record_live_exclusion` called only from `prepare`.
   - The new test records only the file name. Moving the `.decision` handler or the recorder call out of `prepare` into `reserve` would still pass.
   - Fix: during the whole-module walk, track the enclosing function (or `<module>`) and restore the function-level assertions.

**Resolved**
- **Prior blocker 2 (pilot not tied to source):**
  - The pilot's source commit and tree (`d511c86` / `d2168c6`) match the gate's tree, and the record includes the runner and issuer digests.
  - The runner checks tracked files are clean before and after the run, and the pilot log digest (`36bf97…`) is recorded.
  - The post-revoke check now requires the exact type and `decision is None`.
- **Prior blocker 3 (hosted check):**
  - A new test runs the resolver and copy without patches.
  - Fixture teardown checks that the original functions are restored.
  - Teardown also opens a fresh writer after the activated one closes, and checks that `_live_profile is None` and `read_source` is refused.
- **Prior blocker 4 (reachability gaps), except item 3 above:**
  - The test now walks every module in the repo.
  - It checks string constants and attribute access outside the defining module.
  - It reads `scripts`, `gui-scripts` and all entry-point groups in every `pyproject.toml`.
- **Prior blocker 5:** the exact `type(...) is` check is in place, `installation` and `generation` are asserted exactly, and the commit tip and claim count are read back.
- **Prior blocker 6:** `_install_isolated_profile` now sets `_live_profile` and returns an `_InstallationProof`. Creating the issuer moved to `_prepare_isolated_issuer`, and the AST test covers both functions.
- **Prior non-blocking items:**
  - Revoke is now final, and a test covers it.
  - Ordering is documented: the issuer is bound to its owner thread.
  - The earlier local failure is recorded as not reproduced.

**Non-blocking (new)**
- The copy-refusal test passes on any `LedgerError`, including one from pinning the directory. Assert the refusal message, or show the same bytes copy into the same parent when the resolver admits them.
- In fixture teardown and in `test_late_recheck_refusal_is_private_and_rolls_back`, `pytest.raises` still accepts subclasses.
- The reachability scan silently skips directories named `build`, `dist` or `.scratch`, and symlinked files, so a first-party module there wouldn't be checked.
- Because the issuer is bound to one thread, currentness checks from any other thread fail closed. Document this in case the monitor ever reserves from another thread.
