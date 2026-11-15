[05:55:11]
**REFINE_310: PASS**

I checked this against the supplied text only. The code excerpts are spliced fragments, so I can't verify anything they don't show.

### Accepted scope
- **Matches the accepted split.** #310 is the journal-only part split off #119 ("M09a"): it lives in `monitor_journal.py` plus focused tests. It adds no write path, no schema upgrade, no project guard, no ACK, no queue and no consumer.
- **Graph matches the readback.** The parent is #100 at Rank 229.9. The only prerequisite is #300, which is closed. The only dependent is #119. #120, #122 and #296 still depend only on #119.
- **Dispute variant is consistent with the split's conditions.** It is exclusive, keeps the existing constructors and does not reclassify dispositions or paired settlements. Binding to the full row identity and digest, not the sequence alone, covers the shared-sequence case. The split's #122 fence holds because nothing is exported, reported or wired.

### Reuse of persisted facts
- **Coverage:** `coverage_changes` already reads verified coverage inside a transaction, with tip bounds and a schema-version gate (`_COVERAGE_ROWS`, `_stored_coverage`). Reusing `JournalCoverage` unchanged works.
- **Disputes:** `_fresh_view` already reads `disputes` and `content_disputes` up to a watermark. It validates refs, decodes evidence and joins `claims` for the project. That is a sufficient base for the readback.

### Estimate
- 0.35 + 0.35 + 0.40 + 0.15 = 1.25 h, Size S, matching the board.
- The test share is plausible for one named test plus six guards. #300's actual time (0.11 h against 3.2 h estimated) gives no sign the estimate is too low.

### Ownership and separation
- **#310** owns `test_unqualified_source_gap_publishes_without_project_write_or_ack` and the listed guards. #119 keeps its four tests, its storage and the ACK work.
- **#122:** #310 only stays fenced from it and does not depend on it.
- **Excluded:** Epic #2, C01 and the production cutover are explicitly out of scope.

### Conditions for JIT (not blockers)
1. **The ownership-dispute type has no digest or project.** `OwnershipDispute` has neither field, and `_fresh_view` sorts by `digest` but never selects it.
   - JIT must freeze SQL that selects the digest and joins `claims` for the project.
   - The digest and project must be carried without changing the positional constructor of `OwnershipDispute` or `JournalChange`. Use a trailing default field or a wrapper type.
2. **The evidence-key primitive isn't shown.** Nothing supplied shows a keyed-hash/MAC API on `self._store.evidence`. The candidate identity must reuse the existing key. If it needs new key material, stored state or a separate store, return to Refine.
3. **Clarify "durable keyed shape".** It should mean a deterministic, non-persisted identity computed over the checked change. Any persisted shape breaks "no new write path" and means returning to Refine.
4. **Exclusivity:**
   - The new dispute field must reject any combination with `coverage`, `disposition` or `paired`.
   - It must hold exactly one of an ownership dispute or a content dispute.
   - The existing disposition+paired behaviour stays as it is.
5. **Version gate:** `coverage_changes` returns nothing below the coverage schema version. `publication_candidate` should reject in that case, not issue a candidate. Add a guard test for it.
6. **Where `coverage_changes` sits:** the excerpt shows it under `JournalView` but it uses `self._store`. JIT should confirm its actual owner (probably `RoutingJournal`) before reusing it inside the candidate's read transaction.
7. **Test wording:** in the named test, "publishes" should assert only that a candidate is issued, with no project write, no ACK and no consumer involved.
