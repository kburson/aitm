[13:08:23]
SOURCE_325: PASS

This review covers the supplied source, diff and evidence only. I ran no tools, so blob, tree and SHA-256 identities are checked for consistency across the artifacts, not recomputed.

## Scope and evidence

- **Two-file scope.** The candidate diff against `f235fe00` adds exactly `host_watch.py` (`0ad17f4a`) and `test_host_watch.py` (`65939b28`). These match the tree listing.
  - Nothing imports `host_watch` outside its test, so the watcher stays dormant until #121.
  - `scan.py` is untouched. `_directory`, `_DIRECTORY_FLAGS` and `_file_id` are imported unchanged, which satisfies Pin H at the source level.
- **One candidate across all evidence.** Head `4df14d9e` and tree `c6469cd6` agree across:
  - the local record,
  - the signed hosted run (`status: pass`, `reviewed_tree == tree`),
  - the exact Linux arm64 receipt (`real_kernel_queue_overflow: true`, `no_payload_opens: true`, network disabled).
- **Signed controls.** The six control blobs are identical to the prior verified gate. Hosted and local product coverage agree at 13278/14628.
- **Platform test counts.** Linux collects 7 common + 5 ABI tests, for 12. Darwin collects 7 common + 8 flag cases + 4 lifecycle tests, for 19. Both match the logs, so the platform gating is correct and the common cases run on both hosts.
- **Correction.** The red log shows the new test failing (`1 failed, 18 deselected`). It passes in the 19-test Darwin run.
  - The test is behavioral: rename the root, observe `ROOT_LOST`, then require the owner thread to have exited without calling `close()`.
  - The `while owned and not stop` guard exits only after the final stack is popped and closed. The loop retain is then released under `_ownership`.
  - Before the fix, the owner kept running `CFRunLoopRunInMode` against a mode with no sources.

## Implementation pins

- **A. Run-loop retain.** The retain is taken and released under `_ownership`. `_notify` runs only under that lock and only while `_loop` is set, so no wake can reach a released reference. Native calls never run under `_condition`.
- **B. Recheck mapping.** `_Root.check` maps:
  - `ENOENT` and any other `OSError` → `ROOT_LOST`
  - `ELOOP`, `ENOTDIR` or a chain mismatch → `ROOT_REPLACED`

  After the outcome, `_lost` makes the root terminal. `_check` then deletes the root, drops it from both backends and clears its fallback.
- **C. Shared watches.** `inotify_rm_watch` runs only when a descriptor's member set is empty. Events and `IN_IGNORED` for retired descriptors resolve to `()` and are not attributed. Shared `/proc` and `Linux` dicts mean retired roots never re-enroll.
- **D. Capability limits.** `ENOSPC`, `EMFILE`, per-root and total registration bounds, the scan bound and the time slice all lead to `drop(key)` plus per-root fallback. The `ENOSPC` test proves other roots are unaffected.
- **E. Read buffer.** It is 64 KiB, which is far more than one maximal record. A short header, an overrun length or an empty read becomes overflow. On overflow, earlier parsed records are discarded.
- **F. Audit test.** The audit hook is installed after imports. Every `open` must carry `O_DIRECTORY` and must not name the payload, with `other_opens == 0`. The writer runs in the parent.
- **G. Overflow burst.** The test reads `max_queued_events` without a sysctl change. It churns one file past that bound under an 8 s limit; touch and unlink produce at least 3 events per iteration, so `max/2 + 16` iterations exceed the bound. The rebuild covers one directory.
- **H.** Satisfied, as described above.

## Behavioral checks

- **CF callback lifetime.** `CFUNCTYPE` objects stay in `_callbacks` and are cleared only after a verified join. A failed join raises and keeps `WatchSet._darwin` and its callbacks; the join-timeout test covers this.
  - During the startup-timeout path, the thread's bound target keeps the object alive.
  - Callbacks run only inside `_run` on the owner thread, so stream teardown cannot overlap a callback.
- **No blocking or filesystem work in the callback.** The callback only ORs flags, bounded at 4096. It uses a non-blocking `RLock` acquire, and contention escalates to `callback-pressure`, which reconciles every live root. Exceptions are contained.
- **Startup cleanup.** `ExitStack` runs LIFO in the order stop, invalidate, release stream, release array, release string, then the loop is released under the lock. The start-failure test asserts this exact sequence. Each stack is closed exactly once, whether popped on retirement or closed in `finally`.
- **Root loss and replacement.**
  - Darwin `RootChanged`, `Mount` and `Unmount` wake the consumer. `_check` runs before every drain, so a replaced inode's `CHANGED` is overwritten by the critical outcome.
  - Linux unmount resolves to `ROOT_REPLACED`. No path is re-adopted.
- **Overlapping roots.** Duplicate keys and duplicate physical identities are refused. Overlapping roots share one descriptor with per-key membership, under a constant mask with `IN_ONLYDIR` set, no `IN_DONT_FOLLOW` and no `IN_MASK_ADD`. Both keys receive the hint.
- **Linux enrollment.** Each directory is registered through `/proc/self/fd/N` while the no-follow fd is live. Identity is checked before and after registration against the pinned root chain. `scandir` never follows symlinked directories. Directories moved in and out are both exercised.
- **Close versus `events()`.** The wake pipe is written before `_consumer` is taken. Both fds are retired only after poll returns. The EBADF check proves the inotify fd and both pipe fds are gone. On Darwin, `notify_all` wakes the condition wait.

## Non-blocking observations

These do not affect the verdict.

1. The `CFRunLoopRunInMode` return code is bound but not inspected. With the `owned` guard, a mode with no sources cannot occur while the loop runs, and each wait is bounded at 0.05 s.
2. The mask is asserted at the `inotify_add_watch` call boundary, not read back from fdinfo. A single constant mask without `IN_MASK_ADD` makes these equivalent.
3. Linux fallback persists across overflow rebuilds. After its last root is lost, the Linux backend keeps an idle inotify fd until `close()`. Both are bounded and within scope.
4. Hints coalesce per root, so the 256-hint bound and the `queue-bound` path are never reached by any test.

#326 (admission and enumeration), #121 (scheduling and journal) and #129 (arm64/x86-64 release qualification) keep their accepted ownership. Verified delivery and native Close remain the next gates.
