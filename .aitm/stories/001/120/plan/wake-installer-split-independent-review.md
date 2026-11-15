[10:08:40]
AMEND_120: PASS

**R1 blocking items: all four are resolved**

1. **The three named tests.** #120 owns all three by name.
   - The duplicate and missing hook test now has a clear level. It runs as a scheduler test against a fake coordinator, with idempotent consumed wake retirement and a retained cursor.
   - M10b adds a producer-level test where duplicate native events reach the same keyed scheduler path.
   - Recovery from lost hooks stays with #121's native fallback.
2. **Scheduler behaviour.** #120 owns all of it:
   - Active, Settling and Parked states.
   - Coalescing by provider, session and verified turn.
   - Concurrent turns, resume, retained cursors and bounded quiet backoff.
   - Allowlisted keyed hints.
   - Owning `test_monitor_scheduler.py` and running green with `test_monitor_delivery.py`.
3. **Lost or refused wake.** Each stage now has an owner:
   - #120 runs sender-budget tests for absent, saturated and refusing ingress.
   - M10b tests each installed carrier in an isolated provider home with the monitor unavailable or refusing. The provider must finish within its accepted budget, and #120's JIT freezes that budget.
   - #121 owns native reconciliation and recovery.
4. **No embedded paths.** #120 owns the stable launcher contract. M10b checks that all three installed descriptors contain no checkout, private-state or socket path.

**The rest of the original M10 excerpt has an owner**

- **Ownership by child:**
  - **#120:**
    - Contract, socket and peer checks:
      - `notify` and `take_due`, with any acknowledgment interface accepted at JIT.
      - The same-user socket and the pinned bind-and-verify strategy.
      - Peer UID rejection (the Darwin and Linux peer-credential contract), message bounds and unauthorized locators.
    - Wake handling:
      - Nonblocking best-effort sends.
      - Monotonic deadlines and bounded work units.
      - Fairness quota.
      - Consumed wake retirement.
    - Park, scope and settings authority:
      - Park and advisory wakes leave scope unchanged.
      - The authority over the launcher's private settings.
  - **M10b:**
    - The three owned installers.
    - Preserving foreign hooks and native trust.
    - Unchanged tracked files.
    - Checking owner approval and the pinned provider surface by reusing #120's approved-source checks and the pinned event.
    - A refused install loses no existing authority.
    - The Grok producer follows the M05 carrier, then M07 admission, then the adapter's qualified completion. A generic wake never issues a marker.
  - **#125:** M15 isolated-home rehearsal.
- **Exact source approval and privacy:**
  - #120 keeps the approved-source gate and resolves locators transiently.
  - M10b reuses the same checks.
- **Durable completion:** this is now pinned to the adapter's native completion, not #121's wake acknowledgment. M10b therefore needs no edge to #121.

**Gates, Rank and graph**

- **Gates:** #120 keeps "pending narrowed Refine and JIT", and the existing four-hour cap is checked at JIT. M10b gets its own Refine, JIT, Test, independent source review, verified delivery and native Close.
- **Rank:** the readback now confirms 240 (#120) < 250 (#121) < 280 (#124) < 285 (M10b) < 290 (#125). This matches every edge, and R1's unverified-rank note is closed.
- **Graph:**
  - M10b's only prerequisite is #120. Its M07 dependency is reached through #120 → #119 → #118 → #117, all closed.
  - #121 stays {115, 120, 304}.
  - #125 becomes {121, 124, 304, M10b}.
  - The graph has no cycles.
  - The unlabelled `[126]` array is #125's dependents.

**Not blocking: record these at JIT or activation**

- **Ingress persistence:** the amendment says hints are filtered "before publishing", which is the sender side. #120's JIT should also state that ingress persists only allowlisted keyed fields, whatever the sender sends. The original says "before persistence".
- **Checked ctypes:** the original requires checked ctypes for peer credentials. #120's JIT should name it explicitly.
- **Fairness test:** JIT should name a test for fairness when another project is blocked, not only freeze the quota.
- **Story records at activation:** update #120's `blocking` frontmatter from `[121]` to `[121, M10b]`. Read #120's dependents back as {121, M10b}.
- **#120 estimate:** scaling R1's high estimate still gives about 4.4 hours. The narrowed Refine must re-check it against the cap.

I reviewed only the amendment, story record, prior result and readbacks you supplied. I did not open the repository or any source files.
