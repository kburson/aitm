[05:47:14]
**SPLIT_119: PASS**

All five blockers from the earlier hold are resolved by the supplied evidence. The ownership split, sizing and graph amendment are consistent with each other.

### Earlier blockers
1. **Storage is now proven, and the size accounts for it.**
   - `_MONITOR_SCHEMA` has only `monitor_revisions (key, revision, sequence, payload)`, so there is no destination receipt or lineage binding.
   - The journal v6 tables have no ACK or tail table. They are identity, commits, claims, disputes, progress, claim_revisions, content_disputes, route_dispositions, paired_settlements and source_coverage.
   - #119 now budgets this as new additive guarded storage: 1.20 h for the receipt and 0.85 h for ACK lineage and the tail.
2. **The `publication_candidate` edge has an owner.** M09a owns it and checks exact sequence, canonical bytes and journal identity, then rereads the stored row. Caller-built `JournalChange` values that are forged, ambiguous, from the future or substituted are rejected.
3. **The tests are mapped.**
   - M09a owns `test_unqualified_source_gap_publishes_without_project_write_or_ack`.
   - #119 owns the other four named tests and both assertions: the blocked stream's cursor stays replayable, and settlement after recovery keeps two distinct project scopes.
4. **The M16 guard is covered.** #119 owns the negative control proving a project pseudonym alone can't seed a service claim. The supplied record shows #126 is "[M16] Backup, legacy adoption and rollback", so the legacy bridge correctly stays there.
5. **Both terms are defined.** A destination is the exact pinned registered ledger identity. The test driver is a single local `RoutingJournal` with no #120/#121 code.

### Ownership and sizing
- **Seams:** M09a is journal-only and touches only `monitor_journal.py` plus focused tests. #119 creates `monitor_writer.py` and extends `ledger.py`. Capacity stays with ACK resolution, so it isn't split off on its own.
- **#119 arithmetic:** 1.20 + 0.85 + 0.65 + 0.90 = 3.60 h, which is Size M. That is about 0.4 h under the old cap, now with storage explicitly budgeted rather than left to JIT.
- **M09a:** 1.25 h, Size S, which fits the single-file, read-only validation scope.
- **Calibration:** the #300 data point (3.2 h estimated, 0.1122 h actual) only partially applies, but it doesn't suggest the estimates are too low.
- **Re-estimate:** #119 stays in Refine and is re-estimated independently before JIT, so 3.6 h is a provisional budget, not a commitment.

### Graph amendment
- **New edges:** M09a has parent #100, Rank 229.9 (before #119's 230), and #300 (closed) as its sole prerequisite, and it blocks #119. That adds no cycle.
- **#119's prerequisites are unchanged:** all nine are closed (#118, #199, #201–203, #209, #210, #300, #303). The direct edge from #300 to #119 is now redundant, but keeping it is harmless.
- **#119's dependents are unchanged:** #120, #122 and #296 are open and still depend directly only on #119. M09a doesn't block them directly.
- **The third readback is empty.** I'm reading it as "no M09a item exists yet", meaning no duplicate. It doesn't affect the verdict, but please confirm that's what it is before creating the item.

### Conditions for M09a's JIT (not blockers)
- **Disputes can share a sequence.** In both `disputes` and `content_disputes`, `sequence` isn't unique: `disputes` is keyed by (key, contender, digest, evidence) and `content_disputes` by key. So a dispute candidate must be bound to the full stored row identity plus its canonical bytes, not to the sequence alone. Otherwise a legitimate change could be wrongly rejected as "ambiguous", or one could be swapped for another at the same sequence.
- **The new dispute field must keep the exclusivity check.** `JournalChange.__post_init__` currently ensures coverage is never combined with a disposition or a paired settlement. The new dispute field needs the same exclusivity. Existing paired settlements and dispositions must not be reclassified, as the plan already says.
- **`PublicationCandidate` stays fenced by #122.** It must not be exported, reported or wired to any consumer before #122.
- **Re-split rule for #119:** if the JIT check of physical identity and schema transition pushes the receipt plus ACK storage above 2.05 h (1.20 + 0.85), re-split #119 rather than absorbing the overrun.
