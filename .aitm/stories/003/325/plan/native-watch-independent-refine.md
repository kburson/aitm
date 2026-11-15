[12:26:21]
REFINE_325: PASS

#325 is ready for its own JIT. The two-file ownership, the trust boundary, the absence of any authority, both native lifecycles, dormancy and the 3.0 h / 4.0 h estimate all hold. I found no incomplete prerequisite and no needed split. The gaps below are behaviors to pin at JIT. All of them fit in `host_watch.py` and `test_host_watch.py` within the estimate.

## Verified

- **Ownership.** W edits only `host_watch.py` and `test_host_watch.py`. `test_monitor_watches.py` stays with #121.
- **Trust boundary.** `sources.scan._directory` opens one name at a time with `dir_fd`. Every component is therefore the final component of its own `open`, so a no-follow flag applies to the whole chain. It rejects relative paths and `..`, and returns per-component `(dev, ino, birthtime)`. This is the right helper. The capture-side `_directory(raw, private=…)` calls `resolve(strict=True)`, so it follows symlinks and is correctly not used.
- **No transcript or writer authority.** W opens only directories, emits hints with no authority, and never opens a regular file. Darwin enrollment is path-based and weaker than Linux's fd-bound enrollment. That is acceptable because the worst outcome is a spurious reconcile, never data access.
- **Darwin lifetime.** One thread owns all CF and FSEvents calls. Run-loop waits are bounded. The callback is released only after a successful join. A join timeout keeps the resources and reports failure. This matches the probe (`dedicated_thread_stopped: true`).
- **Linux lifecycle.** There is one `IN_NONBLOCK|IN_CLOEXEC` fd with a bounded watch-descriptor map. Enrollment is fd-bound through `/proc/self/fd`. If that path is unavailable, or the kernel returns `ENOSPC` on the watch limit, the affected roots fall back to reconcile hints for those roots only. Overflow or stale state triggers a rebuild. Closing the fd releases every registration.
- **Coverage split.** Darwin arm64 and Linux arm64 are covered by real smoke runs plus deterministic fakes. #129 keeps x86-64 and per-target recursive-overflow qualification.
- **Dormancy.** Nothing imports `host_watch` until #121. No test starts a service.
- **Estimate.** 3.0 h, Size M, 2 h checkpoint, 4 h cap. This is credible given both APIs are already probed.

## JIT conditions of record (non-blocking)

1. **Cross-leaf freeze on `scan._directory`.** I owns `sources/scan.py` and runs in parallel with W. Pin W as a read-only consumer of `_directory`, `_DIRECTORY_FLAGS` and `_file_id` as they exist on trunk `f235fe00`. If I must change any of them, I gains W as a prerequisite instead of editing them in parallel. JIT must also confirm that `_DIRECTORY_FLAGS` includes `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`.
2. **`/proc/self/fd` enrollment flags.** Call `inotify_add_watch` with `IN_ONLYDIR` and **without** `IN_DONT_FOLLOW`. `IN_DONT_FOLLOW` would register the magic-link inode itself, not the directory. Do the enrollment while the `_directory` context still holds the fd. Add a test that asserts the mask.
3. **Watch-descriptor aliasing.** The kernel returns the existing descriptor when the same inode is added twice, for example nested or duplicate roots. Map each descriptor to a set of root keys and always use the same mask. JIT must fix whether a conflicting key or alias is coalesced or rejected, as the story already requires.
4. **Directory moves.** Treat `IN_MOVED_FROM|IN_ISDIR` as stale state: drop the moved subtree's registrations, or rebuild that root. Otherwise moved-out directories keep emitting under the root and leak descriptor slots. Treat `IN_MOVED_TO|IN_ISDIR` like creation: enroll it and reconcile. Add both to the subdirectory-enrollment test.
5. **Root events.**
   - Map these to a physical recheck: Linux `IN_DELETE_SELF`, `IN_MOVE_SELF`, `IN_IGNORED` and `IN_UNMOUNT`, and Darwin `RootChanged`, `Unmount` and `Mount`. Darwin needs `kFSEventStreamCreateFlagWatchRoot` to deliver `RootChanged`.
   - The recheck emits root-lost or root-replaced.
   - Never re-enroll a replaced inode silently. Re-admission belongs to the coordinator.
   - Darwin drop, `MustScanSubDirs` and `EventIdsWrapped` flags become a root-level reconcile.
6. **Linux close vs. `events()`.**
   - `close()` must not close the inotify fd while another thread is blocked in `select`/`poll`, because the fd number could be reused.
   - Either serialize close with a lock and a wake fd, or document `WatchSet` as single-consumer and test that.
   - On both backends, `close()` must wake a blocked `events(timeout)`.
7. **Callback discipline.**
   - The Darwin ctypes callback only does a non-blocking, coalescing enqueue and never raises.
   - Keep the `CFUNCTYPE` object referenced through join.
   - Make the thread a daemon so a retained, leaked thread cannot block interpreter exit.
8. **No-transcript proof.** In `test_host_watch.py`, add a `sys.addaudithook` `open` assertion: only directory opens occur during enrollment and event delivery.
9. **Carry-over.** Confirm that `f235fe00` is on trunk and contains #120. This checkout is still `codex/aitm-120-wake-scheduler`.

## Residual risk (accepted, no change)

- **Deprecated Darwin API.** `FSEventStreamScheduleWithRunLoop` is deprecated in favor of a dispatch queue. The probe shows it works on Darwin 25. Revisit only if #129 qualification fails.
- **Inode reuse.** ext4 reuses inode numbers, so a `(dev, ino)` match alone can accept a recreated root between admission and enrollment. Hints carry no authority and #326 re-verifies, so this costs latency only.

The JIT, signed Test, independent source review, verified delivery and native Close all still apply. This verdict authorizes no implementation.
