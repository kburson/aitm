# #112 independent post-CI source review

Recorded November 10, 2026. Declared manual, off-platform review from a separate Claude Code 2.1.318 session. The provider reported `claude-opus-5-5`, with high effort requested. No native GitHub review was submitted.

Review packet SHA-256 `e357ed7a862eebe67058dd1e87524ec4306a8a0c080604029fd1e5295b39a960`. Exact six-file full-index diff SHA-256 `861d3c6d8b86c9918a975a1f16fac5235f10e15c9d49a2dda0b4ceea6e57340b`. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/42837579428/attempts/1).

## #112 M02 independent source review: candidate `b04b011` / tree `29d903c`

### Verdict: **PASS**

I found no required source findings. The source meets the accepted M02 contract and the reviewed JIT design. Three evidence items below (E1–E3) need to be reconciled or recorded in the delivery record before closure. None of them requires changing the candidate tree, so the exact hosted run stays valid.

### Required findings

None.

### Review by area

**Specification compliance**
- The new functions match the accepted contract exactly:
  - `publish_noreplace(src_dir: int, src: str, dst_dir: int, dst: str) -> bool`
  - `exchange_entries(...) -> None`
  - Both are in `packages/aitm-usage/src/aitm_usage/host_fs.py`.
- The required test file `tests/test_host_fs_publication.py` exists and contains all three required test names. It also adds tests for an unavailable native binding, leaf-name-only entries, and error translation with cleanup.
- `RENAME_EXCHANGE` gets its own probe, as the accepted plan requires: the committed exchange test, plus the separate ext4 probe in evidence item 1.
- The accepted M02 named `service.py` and `install.py`. The JIT says those files reach the new functions through the existing `scopes._publish` helper, and the caller snippets support that. I accept that handling. Any module that still imported `_rename_exclusive`, `_RENAME_EXCL` or `_RENAME_SWAP` would fail at import, and the full suite and Ruff passed after those names were removed.
- The intentional same-directory replacement is unchanged. The `replace_pending` path still uses `os.replace` (`scopes.py` `_publish`).

**Correctness on Darwin and Linux**
- **Darwin:** `renameatx_np` with `RENAME_SWAP=0x2` for exchange and `RENAME_EXCL=0x4` for no-replace. These values are correct.
- **Linux:** `renameat2` with `RENAME_NOREPLACE=0x1` and `RENAME_EXCHANGE=0x2`. These values are correct.
- Each call sets one flag only, and the argument and return types are checked through ctypes.
- errno handling is sound: errno is cleared before the call, `use_errno=True` gives a thread-local copy, and it is read after the call.
- Only no-replace treats `EEXIST` as "destination exists" and returns `False`. An exchange that fails with `EEXIST` raises, and there is no emulated fallback.
- Other platforms raise. So does a missing symbol, for example glibc older than 2.28 or a missing `CDLL` symbol.
- Name checks reject `""`, `.`, `..`, `/` and NUL before encoding, so a C string can't be cut short and no path can escape the pinned parent directory.
- `_swap_store` now uses `STORE_NAME` where it used the literal `b"state"`. The two match: `test_directory_exchange_and_durability` hard-codes `state`, calls the real `_swap_store`, and passed in the hosted run.

**Cleanup and failure safety**
- **Export:** if `publish_noreplace` raises, `published` is never assigned, so the existing cleanup path runs. A collision (`False`) still goes to `_check_replay`.
- **Backup:** a collision and a host error both still raise `BackupError`, which is the same behavior as before.
- **Restore exchange:** a refused exchange leaves both directories unchanged. Tests check this for `ENOTSUP`, `ENOSYS`, `EINVAL` and `EACCES`, comparing inode identity and sentinel contents.
- **Parent fsync:** both parent directories are synced only after the swap is visible, in staged-then-project order (`test_directory_exchange_and_durability`).
- **Scope and export staging:** refusal leaves no leftover staging entries (`test_publication_failure_preserves_caller_errors_and_cleans_stage`).

**Error translation**
Each caller converts `HostFilesystemError` into its own domain error with `from None`, and the messages carry no path details:
- `scopes.py` raises `LedgerError`.
- `export.py` raises `ExportError`.
- `backup.py` raises `BackupError` in both `backup` and `_swap_store`.

The scope message for an unavailable binding changed. The full suite passing shows no test depended on the old wording.

**Both export race tests (`tests/test_export.py`)**
- The diff touches only four kinds of lines: the saved real function, the stub signature (the `flags` argument is dropped), the delegation call, and the `monkeypatch` target, which is now `export.publish_noreplace`, the name export actually calls.
- Every assertion is untouched context, so both original assertions are kept: complete atomic visibility and the parent-sync check in the first test, and no substitute publication in the second.
- Both races still inject at the exact publication call and then call the real path.

**Handling of the two changed CI test files**
- `tests/test_export.py`: **accept.** Only the race injection point was retargeted; assertions are unchanged.
- `tests/test_host_fs_publication.py`: **accept.** It is new and has 16 cases (2 + 1 + 4 + 3 + 5 + 1), which matches the delivery record's 16.

### Evidence gaps

- **E1 (must reconcile before closure).** The hosted subject shows `baseline_tests: 547` and `tests: 564`, a difference of 17. The diff adds only 16 test cases and deletes none. The packet doesn't explain what `baseline_tests` counts (possibly the `python-base` job), how the two changed test files were treated in that baseline, or where the 17th test comes from.
- **E2.** The accepted plan says "Run red". The delivery record doesn't record a red run.
- **E3.** The Linux `renameat2` branch never runs a real native call in hosted CI, which is Darwin/APFS only. Its unit test replaces the native binding (with a fake `CDLL`, or with a refusing stub). Linux correctness rests on:
  - the off-CI ext4 receipt, for which the packet gives only output digests, not logs;
  - a custom caller harness, not the committed pytest suites;
  - a different image (Debian bookworm, CPython 3.13.9) for the caller harness, because CPython 3.13.18 in the #102 image fails to import pricing. That failure reproduces on the untouched base, so it isn't caused by this change. It belongs with #129 runtime selection, as the receipt already says.

  The record should state these limits clearly.
- **Minor (non-blocking):**
  - No test covers an exchange that fails with `EEXIST`, or `.` as a name; I checked both by reading the code.
  - The packet shows no search confirming that no other native rename call sites remain. The import argument above covers this, but a runtime attribute lookup inside an untested path can't be ruled out from the packet.
  - The five Codex-reader failures during the overlapping local run touch nothing in this diff, and the hosted run passed.

### What I actually reviewed

I read only the read-only packet:
- the exact JIT;
- the accepted M02 section and the host OS boundary section of the spec;
- the complete six-file diff;
- the caller snippets from `service` and `install`;
- the ext4 evidence;
- the delivery record;
- the authenticated run observation (six jobs, all successful, attempt 1, at head `b04b011`);
- the downloaded subject fields.

What I did not do:
- I didn't recompute the diff SHA-256 or the blob IDs.
- I didn't read the full files outside the diff hunks. For example, I took as given that `sys` is imported in `host_fs.py`, how `published` is initialized in `export.py`, and that `_publish` cleans up in a `finally`. I relied on the passing suites for these points.
- I didn't execute anything, access GitHub, or check the filesystem myself.

All hosted and ext4 results above are as reported in the packet.

## Implementer disposition

- E1. Compared the complete authenticated base and candidate test inventories. No baseline test was removed. The exact difference is the 16 new M02 cases and the candidate lane's existing CI-only `tools/ci/tests/test_cli_evidence.py::test_usage_console_help`. Replaying the delivered gate against the raw archives reproduced the signed result.
- E2. The initial test-first run produced 15 expected failures for the missing host interface or binding seam and one pass for the already implemented Darwin durability behavior. The same file passed all 16 cases after implementation.
- E3. Hosted validation ran on Darwin/APFS. Linux evidence comes from separate credential-free runs with the exact candidate tree on local arm64 ext4. The custom harness used real calls and successful fsync on both parents. The proof record distinguishes the boundary run on CPython 3.13.18 from the caller run on CPython 3.13.9 and records the import failure on the untouched base. [Ext4 proof](../attachments/ext4-publication-proof.md).
- A search of the full candidate package found the native rename symbols only in `host_fs.py`. No code or test change was required after this review.
