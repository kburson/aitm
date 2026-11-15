[14:20:12]
**AMEND_121_ENROLLMENT: PASS**, with the Refine conditions below. This decision does not authorize code and does not stand in for #329's independent JIT.

## Is prospective enrollment required?

Yes. Three accepted contracts require it:

- **M06** says "Preserve per-stream enrollment." Trunk implements that as `Registry.enroll_stream`. It admits a stream that was not present at the original command, because it only requires that the edge is in `view.permissions`. Re-enabling the edge for each stream is not the accepted model; the M06 re-enable tests concern edge intervals, not new sessions.
- **M11** discovers new directories and reconciles them after overflow or restart without a queued event. A discovered Grok stream with no epoch makes that discovery inert for routing.
- **M18/M19** require resume, fork overlap, late writes and crash catch-up through production admission. Under #329's H6 negative control, a forked or newly opened Grok session on an enabled edge routes nothing without another `capture enable`.

No accepted contract permits a qualified source to need a fresh capture-enable for each session. I found none in the excerpts, and the requirement would contradict `enroll_stream`'s existing semantics.

## Is it currently unowned?

Yes, and nothing smaller already owns it:

- **#329** H6 explicitly disowns automatic enrollment and directs a separate story ranked before #121. Widening #329 would reopen its JIT.
- **#330** owns only single-admission consumption in journal prepare for already-enrolled streams.
- **#121**'s accepted split owns `monitor.py`, `service.py` and `test_monitor_watches.py`. It cannot reach `monitor_registry.py`. The trunk `enroll_stream` rejects any non-`VerifiedBoundary` boundary, so #121 cannot call it for Grok.
- Having the coordinator queue a capture command on the user's behalf would be a synthetic, non-owner-authorized command. That violates M06's `ControlInbox` contract and is not acceptable.

## Authority check

The proposal's authority source is the durable edge grant from an explicitly applied command, bound to the exact live generation. That matches `enroll_stream`'s existing authority and is not a watch event. It is the "new, explicitly verified writer operation" that #329's negative control anticipates. The negative control therefore stays valid until M11e lands, and #329 must still ship and test it unchanged.

## Conditions for Refine/JIT (not blocking)

1. **Codec compatibility.** If an edge grant with zero streams needs a same-file addition, it must preserve #329 H3:
   - an empty Grok registry still produces literal older bytes;
   - an older binary still fails closed on any new row;
   - the golden constants are not changed, or are explicitly re-derived under #329's rules.
2. **Pre-witness spans must be visible.** For a fresh stream first seen after work already exists, the unclaimed prefix before the start point must surface as an explicit unknown or gap. Losing it silently would weaken M11 and M18 catch-up. Add a named test for a session created and completed while the monitor was down.
3. **Pending disables block.** The fail-closed check must read pending inbox disables at the time of the call, not only committed permissions. Test this with the same ordering #121 will use.
4. **File ownership.** Confirm whether #330 touches `monitor_scope.py` or `monitor_registry.py`. #330 and M11e are independent and adjacent in rank, so any overlap needs explicit sequencing or a split.
5. **Rank value.** Verify the project's Rank field accepts 249.5. If it doesn't, renumber without moving #330 or #121 relative to each other or their dependents.
6. **Spliced excerpt.** The pasted section labeled M12 contains the M18 body. My findings rest on that M18 text. Refine should cite the exact Epic section.
