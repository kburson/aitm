# #112 independent design, plan and JIT review

Recorded UTC `2026-11-10T14:40:17Z`. Declared manual review in a separate Claude Code 2.1.318 session. The provider response reported `claude-opus-5-5`; high effort was requested. The installed peer-review wrapper did not resolve a current registered skill, so this review used the manual checklist route.

The input included the full JIT with SHA-256 `7510c5f7866746972b8f40d759b62dabfd61f5de38528be2780bdb7a0d768f1b`.

## Review verdict: **PASS**

### Required findings

None. Nothing in the input shows a requirement gap, a broken dependency or a replay hazard that should block pickup.

### Advisory findings (non-blocking; fix during implementation)

1. **The file list is narrower than the accepted plan, and only partly shown in the input.**
   - **Evidence:** Accepted M02 lists `service.py` and `install.py` as files whose native calls move to the new helper. The JIT changes only `host_fs.py`, `scopes.py`, `export.py` and `backup.py`.
   - **What the extracts support:** `service._publish_exact` and both `install` extracts call `_publish`. The plist update uses same-directory `os.replace`. So the JIT's reasoning holds for the code shown.
   - **What is not shown:** The "operation record publication" path the JIT names is not in any extract.
   - **Action:** The implementer should confirm that `service.py` and `install.py` contain no direct `_rename_exclusive`, `_RENAME_*` or ctypes rename references. If any exist, follow the JIT's own rule and return to Planning.

2. **The JIT doesn't say how the new error reaches each caller's domain error.**
   - **Evidence:** The design has `host_fs` raise "a sanitized host filesystem error" for any failure other than EEXIST. It also says callers "retain their existing … domain errors." The baselines raise `LedgerError` (scopes), `ExportError` (export) and `BackupError` (`_swap_store`).
   - **Action:** Each caller should catch the host error and raise its existing domain error. Add a test per caller that asserts the domain error type, so a new exception type can't slip past CLI error handling unconverted.

3. **The JIT names fewer tests than the accepted plan.**
   - **Evidence:** The JIT says only "the scoped tests." Accepted M02 names the new file `T/test_host_fs_publication.py`, its three tests, and the green suites `test_scopes.py`, `test_export.py` and `test_install.py`.
   - **Action:** Use the accepted plan's names. Also run the backup and service suites, since the JIT now routes those paths through the shared helper.

4. **The probe evidence covers a different exchange shape than restore uses.**
   - **Evidence:** `_swap_store` exchanges `state` between two different parent directories (`staged.fd` and `project.fd`). The JIT probe "synced their parent", in the singular, which suggests both entries shared one parent.
   - **Action:** Make sure the candidate run on the ext4 volume includes a cross-parent `RENAME_EXCHANGE` test with both parent syncs. The planned "both restore parent syncs" test should cover this if it uses two parents.

5. **Some error-safety details aren't spelled out.**
   - **errno capture:** Bind with `use_errno=True` and read errno straight after the call. The baselines already rely on `ctypes.get_errno()`.
   - **Refused primitives:** On Linux, `EINVAL` and `ENOSYS` must raise. On Darwin, `ENOTSUP` must raise. None of these may return False.
   - **Test:** Add one where a failure other than EEXIST (for example `EACCES`) raises rather than returning False. That keeps the replay path limited to EEXIST.

6. **Other existing tests may break.** The JIT retargets only the two export race tests. Any other test in the scopes, install or backup suites that patches `_rename_exclusive`, `_RENAME_EXCL` or `_RENAME_SWAP` will also need retargeting.

### Checks that passed (based only on the input)

- **Requirements:** The JIT keeps the accepted helper names and both behaviours. No-replace publication returns False only on EEXIST; exchange either succeeds atomically or raises, with no emulated fallback. Callers keep their parent fsync after success.
- **Replay and same-directory replacement:** The export collision path still feeds into `_check_replay`. The deliberate `replace_pending` and plist `os.replace` paths stay as they are.
- **Dependencies:** The preflight says #111 is closed and Done and is #112's only predecessor. The trunk SHA prefix `c0371cc` matches the JIT's merge SHA.
- **Separate exchange probe:** The JIT states it, as accepted M02 requires.
- **Estimate:** 2.5 hours against a 4-hour cap is plausible for four source files, ctypes bindings, red/green tests and runs on two platforms.
- **Pickup:** The JIT names a fresh branch from the pinned trunk targeting trunk, who owns it, what closure requires, and when to return to Planning. Native providers and systemd are correctly left to #129.

### What I actually reviewed

Only the text supplied: the JIT body, the accepted M02 extract, the preflight observations, and the baseline extracts for scopes `_publish`, export `_publish_staged`, backup `_swap_store`, service `_publish_exact` and three install fragments.

### Not independently verified

I took these from the input and did not check them myself:
- Both SHA-256 values: the JIT's and the #100 plan's.
- GitHub issue states, the trunk and planning SHAs, branch protection rules and the CI run result.
- The Docker/ext4 probe and its result.
- That the baseline extracts are complete.

The implementer confirmed that service and installer have no direct native rename binding and that only the two named export race tests patch the legacy seam. The candidate will preserve domain errors, cover unrelated errno refusal and exercise the real cross-parent restore path with both parent syncs.
