[10:49:09]
REFINE_120: PASS

**Boundary.** The plan matches the accepted M10 split.
- **In scope:** one private AF_UNIX wake ingress, the Active/Settling/Parked scheduler, explicit park, the generic bounded sender and the private launcher contract.
- **Out of scope:** native descriptors, provider configuration, activation and the Grok-specific proposal producer belong to the successor installer story, which appears to be #320. The coordinator process, wake completion and root-watch reconciliation stay in #121.
- The scheduler never writes the native cursor or assigns work scope. It adds no routing journal schema and no new qualification authority from socket credentials.
- The descriptor-path check is explicitly attributed to M10b, not #120.

**Graph.**
- Prerequisites #115 and #119 are closed.
- #120 blocks #121 and #320, both open. One edge row lists #115, #120 and #304 as blockers, consistent with #121 depending on #120.
- #320 sits at Rank 285, after #120 at Rank 240, so the order is consistent.

**Tests.**
- The plan names the scheduler test file and its three tests (park then late write reopens, stale stop cannot park a newer turn, duplicate or missing hooks stay idempotent).
- It adds negative ingress cases: wrong UID, unsafe endpoint, invalid length and unknown locator.
- It also covers hint privacy, retention of work after a failed or interrupted scan, the bounded sender, and per-project starvation.
- The delivery tests run alongside.
- A fake coordinator exercises #119 capacity fairness and acknowledgment.

**Estimate.** 1.45 + 1.25 + 0.8 = 3.5 hours, matching the Board (3.5, Size M, Refine, Rank 240). That is under the 4.0-hour cap with 0.5 hours of margin. The seams it reuses all exist at `ab9db800`: `_pin_directory`, `ControlInbox`, `default_monitor_root`, `_ServiceEvidence`, `_private_child`, `_publish` and `SourceLocator`.

**Missing from the packet (not blocking):**
1. The fourth edge row (#121, #124, #304, #320) has no owning issue. #121's Rank is not given, so I could not confirm that #121 is ranked after #120.
2. Restart recovery is not a named test. The plan says a restart discards the lease and recovers from the retained hint plus the native cursor, so JIT should add that test explicitly.
3. The plan supports Darwin `getpeereid` and Linux `SO_PEERCRED`, but it does not say how the platform that isn't running the tests will be checked. JIT should state whether that uses CI, a skip with a mock, or a ctypes signature test.
4. `_pin_directory` and `_publish` are module-private in `ledger.py` and `scopes.py`. Reusing them from the scheduler may need a small refactor, which should come out of the 1.25-hour ingress and persistence slice.

**Risk.** The 1.25-hour ingress slice is the tightest part: two ctypes peer-credential paths, the socket path bound (104 bytes on Darwin, 108 on Linux), inode verification and framing. If JIT's frozen contracts grow that slice by more than about 0.5 hours, re-Refine instead of proceeding.
