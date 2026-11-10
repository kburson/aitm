# #118 independent pickup review, round 3

Reviewer **Claude Opus 5.5, high**. Off-platform exact pickup and split on November 10, 2026.

# #118 third review: M08a pickup PASS, M08b split PASS

**`548354846c55dea7ee3462a226bcae73f642647f55eaf8209cf78fd2e611e58f` (M08a pickup): PASS**
**`3ebb10df4b8b6c9b5416ed7f2e2b9e76688207248aa2bb67fe9aa84ae9f6202f` (M08b split): PASS**

I used no tools, as you asked. That means I couldn't check either hash, the Closed/Done state of #117, #182 and #194, PR #198, the baseline figures, or any source outside this packet. Both verdicts depend on the packet being exact.

## What you asked me to confirm

| Item | Result | Basis |
|---|---|---|
| **Missing owner (the reason for the earlier HOLD)** | Fixed | The M08b bullet now opens by owning all three accepted outcomes: a causal successor, a proven-older no-op, or a durable incomparable-content dispute. Each decision is bound to the exact predecessor and the later native evidence span. If the evidence can't decide the outcome, the hold stays and the earlier cursor stays replayable. That covers the accepted "incomparable content becomes disputed" rule, and no hold is left without an owner. |
| **Prior cursor policy** | Consistent | The pickup takes the conservative choice: an ownership dispute keeps the earlier frontier replayable, including its exact replays, until M08b records an authenticated disposition. The batch paragraph already lists "competing owner" as something that blocks the cursor, so the two passages now agree. "Replay-safe" now means only "adds no duplicate state", so it no longer conflicts with the cursor rule. A stalled stream is acceptable because the store is dormant. |
| **Archived copy without a native session** | Fixed | When the scanner falls back to a locator key, the read is held. It never creates a second canonical identity. There is a test for it in the transaction bullet. |
| **Scope diagnostic case** | Fixed | The tests now include an ambiguous or conflicting native response whose kept diagnostic blocks cursor movement. |
| **Epoch metadata** | Fixed | Every first-owner claim and every verified competing-owner dispute stores source, surface, session, stream, the half-open span, and the epoch generation and boundary reference. The dispute also keeps the rival project's span and eligibility evidence, without a second usage payload. The split uses the same wording. It also now says the M08a store is dormant and that any new schema needs its version independently reviewed. That closes my earlier S2 note. |
| **#119 gate** | Unchanged | M08b depends on #118 and blocks #119. #118 stays a direct prerequisite of #119, at rank 225. The rule to hold #119 and get re-acceptance if M09 or M11 would be reordered is still there. |
| **Earlier PASS items (B1–B4, S1, S3, S4)** | Not regressed | The delta only touches the lines above. |

## Carry-forward notes (not blocking)

1. **Who releases a stalled stream.** The pickup now says M08b's "authenticated disposition" releases the cursor frontier held by an ownership dispute. The split gives M08b `record_disposition`, but it doesn't say in so many words that this releases a held frontier. M08b's own Refine should set one cursor policy for both kinds of dispute: competing-owner and same-owner incomparable. Without that, a stream with a durable dispute stays stalled forever when #119 starts.
2. **The "existing kept diagnostic" may not exist.** The ambiguous/conflict test assumes the adapter already emits a kept diagnostic when the receipt becomes `None`. If it doesn't, adding one would mean changing an adapter, and that is outside the two approved source seams. In that case, stop and re-review rather than widening the scope.
3. **Budget.** The new fixtures (no-session hold, ambiguous diagnostic) and the rival-span fields land after the 2.25-hour checkpoint, in the 0.90-hour claims bucket. The plan already says to stop at the checkpoint and reopen before four hours.
