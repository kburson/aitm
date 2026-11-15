[12:31:26]
JIT_325: PASS

The JIT is exact, stays within two files and holds on the provided evidence. I ran no tools, so ancestry and blob pins are attested here, not re-executed. The pins below bind the implementation without widening scope.

## Prior Refine conditions

1. **Scanner freeze.** `_directory`, `_DIRECTORY_FLAGS` and `_file_id` are pinned read-only at blob `ccb5e121`. A change by #326 waits for #325 Close.
   - The flags lack a literal `O_CLOEXEC` bit, but this is satisfied by mechanism. CPython creates `os.open` descriptors non-inheritable (PEP 446, 3.13 docs).
   - The probe shows `noninheritable: true` on both native hosts.
   - No scanner edit is warranted.
2. **`/proc/self/fd` enrollment.** It uses `IN_ONLYDIR` without `IN_DONT_FOLLOW`, runs while the traversal fd is live, verifies identity before and after, and asserts the mask.
3. **Aliasing.** Duplicate keys or duplicate physical roots are refused. Distinct overlapping roots share one kernel watch with per-key membership and one consistent mask.
4. **Directory moves.** Move-in enrolls and reconciles. Move-out invalidates or rebuilds. Both are exercised.
5. **Root events.**
   - Linux `DELETE_SELF`, `MOVE_SELF`, `UNMOUNT` and `IGNORED` trigger a physical recheck. So do Darwin `RootChanged`, `Mount` and `Unmount`, with `WatchRoot` set at create.
   - Distinct `ROOT_LOST` and `ROOT_REPLACED` outcomes are produced, with no silent adoption.
   - Darwin drop, `MustScanSubDirs` and wrap events become a reconcile.
6. **Close vs. `events()`.** There is a single consumer lock. A close-on-exec wake pipe is signaled before the lock is taken, and fds are retired only after poll returns. Darwin wakes through the queue condition. The wake and the absence of stale fds are tested.
7. **Callback.** It never throws and only classifies and coalesces. The `CFUNCTYPE` object is held through a successful join. The thread is a daemon. A failed join preserves ownership.
8. **No-transcript proof.** A subprocess audit hook proves zero payload opens.
9. **Carry-over.** Literal trunk `f235fe00` and #120 Closed (state `closed`) are accepted. This checkout is still the #120 branch, so implementation must start from `f235fe00`.

## Other checks

- **Custody, bounds and fallback.**
  - Resource custody is concrete on both backends.
  - The queue is bounded at 256, with critical slots reserved per root.
  - Registrations are bounded at 1024 per root and 4096 total, with a 32768-entry scan bound and injectable bounds.
  - Fallback is per root and only applies when identity is trustworthy.
- **Probe evidence.** The probe covers bounded CF run-loop waits, fd-bound Linux registration and a real Linux overflow, with deterministic fault tests.
- **Scope and gates.** The target is exactly two new files, and the watcher stays dormant until #121.
  - Signed Test, independent source review, verified delivery and native Close are kept.
  - #129's real arm64 and x86-64 release qualification is kept.
- **Estimate.** 3.0 h (1.25 + 1.25 + 0.50). At the 2.0 h checkpoint both backends must deliver a real event and retire resources safely. Stop at 4.0 h or at any added product path.

## Binding implementation pins (all within the two files)

- **A. Run-loop retain.** Release the tracked run-loop retain under the same lock that guards the caller's wake/stop, after the last possible wake. No `CFRunLoopWakeUp` may reach a released reference. Never hold the queue lock across native calls or I/O.
- **B. Recheck mapping.**
  - `ENOENT` → `ROOT_LOST`.
  - `ELOOP`, `ENOTDIR` or an identity mismatch → `ROOT_REPLACED`.
  - Any other `OSError` → `ROOT_LOST`. Identity is untrustworthy there, so there is no fallback.
  - After a critical outcome the root is terminal: it gets no further hints and its registrations are retired.
- **C. Shared watches.** Call `inotify_rm_watch` only when a descriptor's root set is empty. Discard events and `IN_IGNORED` for retired descriptors without attributing them.
- **D. Capability limits.** `ENOSPC`, `EMFILE`, registration-bound exhaustion and scan-bound exhaustion all lead to per-root fallback. That root's partial registrations are retired with membership awareness, and other roots are unaffected.
- **E. Read buffer.** Size the buffer for at least one maximal record (16 + `NAME_MAX` + 1). A truncated trailing record is treated as overflow.
- **F. Audit assertion.** `dir_fd` opens report only the component name. So assert that every `open` event carries `O_DIRECTORY` and that none names a payload. Writers run outside the audited subprocess. Optionally assert `os.get_inheritable(fd) is False` on the yielded fd, with no scanner change.
- **G. Overflow burst.**
  - Churn a small fixed file set past `/proc/sys/fs/inotify/max_queued_events`, under a timeout.
  - The burst needs no sysctl change, and the rebuild stays far below 32768 entries.
- **H. Delivery check.** At start, confirm that `f235fe00` contains the #120 merge and that `scan.py` is blob `ccb5e121`. At delivery, the candidate-tree diff against `f235fe00` must be exactly the two added paths.

This verdict authorizes implementation of #325 only under the accepted gates.
