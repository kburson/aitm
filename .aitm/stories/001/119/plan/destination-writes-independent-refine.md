[05:43:13]
**REFINE_119: HOLD**

Prerequisites, exclusions and architectural fit are acceptable. The 3.9-hour estimate is not supported by the evidence you supplied, and the stated scope leaves out one accepted public edge.

### What checks out
- **Prerequisites:** All nine direct prerequisites are closed (#118, #199, #201–203, #209, #210, #300, #303). #300 merged to trunk at `4cfb418…` and provides `coverage_changes(after_sequence)`.
- **Qualified-cost exclusions:** Epic #2, C01, production cutover, reporting, export, network and scheduler changes are all excluded. Live receipt/fold processing goes to #295/#296, publication to #122, the legacy bridge to #126, and scheduling to #120/#121. No exclusion leaks in.
- **Architectural fit:** The design fits the code you supplied. The project write goes through `Ledger.writer()`/`_write_transaction` under the existing writer lease, then the journal ACK runs as a separate step. Because the ledger and journal are separate stores, recovery depends on rereading the existing receipt rather than writing again, which is the correct pattern. Claims are rebuilt from the stored row instead of trusting the incoming `PendingClaim` fields, and `as_of` keeps its current behaviour.
- **Arithmetic:** 1.1 + 1.0 + 0.8 + 1.0 = 3.9.

### Blockers
1. **Storage needs are unproven, and they decide the size.** The Refine requires four kinds of saved state:
   - an authenticated destination receipt that can be reread after a crash;
   - a "distinct durable lineage binding" on project monitor writes;
   - an accepted publication tail, so a stale ACK can be detected and never rewinds it;
   - a per-destination count of unresolved claims.

   None of these appears in the supplied evidence. `_MONITOR_SCHEMA` isn't shown, and the journal tables shown (claims, content revisions, disputes, dispositions, settlement, coverage) have nothing for ACKs or a publication tail. The Refine leaves the "new persistence model" question to JIT, but with only 0.1 h under the cap that is the sizing question itself. Refine must answer it with evidence: either show that the existing `monitor_revisions` rows (through the authenticated codec) and existing journal tables hold all four, or treat this as new persistence and split.
2. **One public edge is missing from scope.** M09 defines `RoutingJournal.publication_candidate(change: JournalChange) -> PublicationCandidate`. The Refine names only `attach`, `commit` and `ack`. It must name this fourth edge and say that the supplied `JournalChange` is checked by rereading the stored row at its sequence. A caller can construct a `JournalChange`, the same way incoming `PendingClaim` fields can't be trusted.
3. **Tests aren't tied to the M09 checklist.** Acceptance must require these five named tests:
   - `test_restart_at_reserve_commit_and_ack_yields_one_row`
   - `test_stale_ack_never_rewinds_publication`
   - `test_full_destination_queue_preserves_independent_progress`
   - `test_late_conflict_after_ack_produces_dispute_without_new_write`
   - `test_unqualified_source_gap_publishes_without_project_write_or_ack`

   It must also require the two M09 assertions: a blocked stream's cursor stays replayable, and settlement after recovery keeps two distinct project scopes.
4. **The M16 guard is unassigned.** The M09 contract says "a project pseudonym alone cannot seed a service claim." The evidence doesn't show that #126 is M16. Either add a negative test for this guard to #119 or cite where #126's scope accepts it.
5. **Two terms need defining.**
   - Capacity: the Refine says "per-project unresolved capacity count" but M09 says "per destination". State that a destination is the pinned ledger identity.
   - "Under the same coordinator": #120/#121 own the coordinator, so state that this means a test-local driver of one `RoutingJournal`, with no coordinator code.

### Calibration
The #300 figure (3.2 estimated, 0.1122 actual) has partial coverage only ("partial coordinator progress"). It can't support 3.9 hours or argue against it.

### Recommended split
Unless Refine shows that all four kinds of saved state fit the existing tables, split along the least-coupled seam:

- **#119a, about 1.0 h:** `PublicationCandidate` type plus `RoutingJournal.publication_candidate`.
  - Covers journal-only `UNQUALIFIED_SOURCE` coverage and already-supported disputes.
  - Each change is checked against the stored row and its sequence.
  - Zero destination writes and no ACK.
  - Touches only `S/monitor_journal.py` and depends only on #300.
  - Owns `test_unqualified_source_gap_publishes_without_project_write_or_ack`.
- **#119b, about 2.9 h, after #119a:** `attach`, `commit`, `ack`, receipt reread, stale-ACK protection, late conflict to dispute (reusing #119a's candidate path), and per-destination capacity and backpressure.
  - Owns the other four named tests and both assertions.
  - The 1.1 h of headroom absorbs any new receipt or ACK storage.

Capacity is not a valid split on its own: what counts as "unresolved" depends on how ACKs resolve.
