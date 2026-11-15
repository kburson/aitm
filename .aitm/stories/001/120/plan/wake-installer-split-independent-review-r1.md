[10:06:47]
**AMEND_120: HOLD.** One blocking condition: the amendment doesn't say which child owns several accepted M10 tests and behaviours. The topology, edges, ranks, estimates and scope are otherwise sound.

**Blocking condition.** Before #120 is narrowed, every item in the accepted M10 excerpt needs an explicit owner. As written, these items have no owner, or their owner is unclear:

1. **Three named tests:** `test_park_final_catchup_then_late_write_reopens`, `test_stale_stop_cannot_park_newer_turn` and `test_duplicate_and_missing_hooks_keep_idempotent_progress`. For the duplicate/missing-hooks test, state whether it is scheduler-level (#120), producer-level (M10b) or split between them.
2. **Scheduler behaviour #120 should own:**
   - Active, Settling and Parked scheduling states.
   - Coalescing by provider, session and verified turn.
   - Concurrent turns, resume, retained cursors and bounded quiet backoff.
   - Persisting only allowlisted keyed hints, with unauthorized context filtered out before persistence.
   - Running green with `test_monitor_delivery.py` and owning `test_monitor_scheduler.py`.
3. **"A lost or refused wake must allow the provider to proceed":** the R1 reviewer moved the installed-carrier "provider not stalled" check to M10b. The amendment leaves it out of M10b. It needs a sender-budget test in #120, an installed-carrier test in M10b, and recovery through native reconciliation staying with #121.
4. **No embedded checkout, state or socket path in the installed command:** #120 owns the launcher contract. M10b must assert it against all three installed descriptors.

Without this list, narrowing #120 can silently drop accepted behaviour. Allocating it doesn't change the topology.

**Checks that pass**
- **Smallest change:** the split matches R1's proposed extraction exactly. 1.5 + 1.25 + 0.75 = 3.5 h for #120, and 2.0 + 0.5 = 2.5 h for M10b, totalling 6.0 h. No new product scope is added. The JIT freeze list only closes gaps R1 already flagged.
- **M07 edge:** the readback confirms #120 → #119 → #118 → #117, all closed, with #117's own prerequisite #116 closed. #115 is a direct prerequisite of #120 and is closed. "#120 is the only incoming edge" holds.
- **#121 preserved:** its exact set is {115, 120, 304}, unchanged, with no installer edge. This correctly replaces R1's shorthand that #121 would be "blocked only by #120".
- **#125 preserved:** its old set is {121, 124, 304}, plus the new M10b edge. Coordinator #121 and the new installers M10b both feed the installed-service rehearsal at #125 through native edges.
- **Rank:** 240 (#120) < 285 (M10b) < 290 (#125) is consistent with the edges. M10b has no edge to #124, so its 280 rank only sets ordering.
- **Sign-offs:** each child keeps its own Refine, JIT, Test, source review, delivery and Close. Rehearsal and qualification keep their existing evidence requirements. Epic #2, C01 and production cutover stay out of scope.

**Not blocking (record these at activation or JIT)**
- **Unverified ranks:** the supplied readback contains no ranks, so the 280 for #124, the 290 for #125 and #121's rank are unverified. Add a rank readback to the activation evidence.
- **Unlabelled arrays:** the last two arrays (`[121]` and `[126]`) have no label. I didn't rely on them.
- **"Durable completion":** state that the Grok producer's durable completion is the existing adapter completion, not #121's wake completion. If it meant #121's, M10b would need a #121 edge.
- **Thin margin on #120:** scaling R1's top estimate of 7.5 h gives about 4.4 h for #120, over the cap. The narrowed Refine must re-check it against the four-hour cap.
- **Limits of this review:** I had no file or shell access in this session. I reviewed only the supplied amendment, story record, R1 receipt and native readback. I didn't open the source files or the repository.
