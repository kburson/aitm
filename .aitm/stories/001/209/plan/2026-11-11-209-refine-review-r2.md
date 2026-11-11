# #209 independent Refine review round 2

Claude Opus 5.5 high. Reviewed artifact SHA-256 `c20f8af889015ec24f1bb6b78f1fd2a989347bbeb74fa4df35f463f052f25b80`. Packet SHA-256 `cd58c8a8136706d3a9148b23e799ce0383b230fedee3a5616352003298e51be0`.

**PASS**

This review covers the amended #209 Refine only, judged against the packet as supplied. I didn't recompute SHA-256 `c20f8af8…`. A PASS here authorizes no JIT, Develop or later gate.

## B1: resolved, and it was a round-one reviewer error

- **Current read-back:** `[118,199,201,202,203,204,209,210]` has eight entries and includes #202.
- **Original round-one read-back:** `[118, 199, 201, 202, 203, 204, 209, 210]` is the same eight entries and also includes #202.
- **What went wrong:** round one listed only seven and left out #202. That misread the packet's own evidence. The artifact's original "all eight" claim was correct.
- **No change needed:** no edge needs restoring and none was changed. The artifact now gives the exact list.
- **Graph checks:**
  - #209 is blocked only by #203, which is Closed Completed.
  - #209 blocks #119 and #210.
  - #210 is blocked by #209.
  - #204 is blocked by #203 and #210.
  - #209 is a child of #100 at Rank 228.1, in Backlog.
  - This matches the accepted split, with no cycle.

## B2: resolved

| Obligation | Where the amended text covers it |
|---|---|
| Which store and starting version | Private RoutingJournal SQLite, v3 to v4. The ScopeState artifact is explicitly unchanged. |
| Atomic migration and retry | Admits exact v1, v2 and v3 layouts, with intermediate checks in the same transaction. Requires atomic interruption and idempotent retry. |
| Old rows and historic views | Old rows stay byte-equivalent. Pre-v4 claims, disputes, revisions, cursors and historic views are unchanged. |
| Wrong formats | Unknown, mixed or wrong-key stores refuse. Frozen v1, v2 and v3 readers refuse v4 at the schema gate and leave the database and sidecars intact. |
| Replay identity | The command UUID is the replay key, with one proposal per hold. An exact live replay returns the same record and sequence. Changed bytes, or a different command for the same hold, refuse before mutation. |
| Failure before commit | The final current-authority check runs before commit. On failure, the staged sequence and row roll back. Committed records stay readable. |

## Round-one nonblocking items

| # | Item | Status |
|---|---|---|
| 1 | Settlement contract | Carried: #210 settlement and #204 folded intent each land as one atomic change, with no duplicate JournalChange. #210's JIT picks the entry point. |
| 2 | Byte comparison | Carried: ScopeState bytes, routing view, holds, cursors and prior journal rows are compared before and after record and replay. |
| 3 | #209 read-back | Carried. |
| 4 | Probe provenance | Carried: base commit, tree and four probe file hashes are recorded. Separately named Claude quota-only, generic, mixed and OVERLAP_UNVERIFIED controls are required. |
| 5 | Late-overlap fixture | Carried: the legacy disposition is labelled as fixture setup outside `record_disposition`, and the projection is tied to the journal sequence. |
| 6 | Copied-scope assertion | Carried: a copy with a different original scope must refuse causal revision, and prior usage and progress stay intact. |
| 7 | "Lost queue grant" | Partly carried: renamed to "revoked grant" but still not defined. |
| 8 | Estimate headroom | Not re-argued. See note E below. |

## Nonblocking (for the exact #209 JIT)

**A. Consumed request vs. replay.** The final authority check fails on a "consumed typed request", but an exact live replay must still return the same record. The JIT must say that a request consumed by this exact record counts as replay, not refusal. Otherwise replay can never succeed.

**B. Replay after authority lapses.** The JIT should fix what an exact replay returns once current authority has lapsed. Lapse can come from hold expiry, revocation, or a later #210 change to the hold. The text suggests it refuses with no mutation while the record stays readable through history. This also covers retries after a crash that happened after commit.

**C. One proposal per hold.** If #210 later finds a recorded proposal stale, the hold stays held, and no new command can propose for it. That is safe, because it fails closed, but the hold may never be able to make progress. The JIT should state this outcome on purpose and confirm #210 never needs a second proposal on the same hold.

**D. Undefined terms.** Define "revoked grant" and "wrong-key store". Remove the repeated sentence "An exact live replay returns the same record."

**E. Estimate.** B2 added migration from three versions plus three frozen-reader controls, and the estimate is still 3.90h of a 4.00h cap.
- That holds up only because the strict-store seams from #199 and the earlier versions are reused.
- The 2.25h checkpoint, which requires a GREEN v4 migration, is the right early test of that risk.
- The JIT should re-measure. If its estimate goes over 4.00h, take the custody split before Develop rather than at the checkpoint.

**F. Claude quota-only fixture.** The probe still shows no isolated Claude quota-only result; its Claude run reports three diagnostics together. The JIT must show that a real completed quota-only fixture can be built. If it can't, record it as a named gap that stays held.

**G. Project fields.** Size and Estimate are null on #209's Project item. Set them, and read back Rank 228.1, at JIT acceptance.
