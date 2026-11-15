[10:20:59]
**REFINE_122: PASS.** One evidence gap carries to JIT entry. The control output `1 passed in 0.64s` has no command, node ID or commit. It corroborates the coverage case but does not prove it. This PASS rests on the native edges, the merge ancestry and the exact producer source.

## R1 blockers

1. **Candidate authority: resolved.**
   - #310 is titled "Create verified journal-only publication candidates", which is M09a.
   - It is closed, and its merge `2b3225e0` is an ancestor of `ab9db800`.
   - #310 appears in #119's prerequisites, and #119's sole prerequisite set for #122 is `[119]`. This matches the accepted split's "#119 sole direct dependency".
   - The single producer is named: `RoutingJournal.publication_candidate`.

2. **ACK vs candidate: resolved.**
   - The Refine now matches the source. The typed candidate is the authority, the ACK stays private, and there is no ACK-backed API.
   - The excerpted `publication_candidate` checks the following:
     - It rejects a non-`JournalChange` input, a sequence outside `(0, tip]`, a non-null `disposition` or `paired`, and anything other than exactly one of `coverage` or `dispute`.
     - It requires the v6 schema.
     - It reads exactly one row via `_COVERAGE_ROWS`.
     - It requires both typed equality and canonical `_encode` equality.
     - It sets the basis to `COVERAGE`.
   - It therefore accepts any committed `JournalCoverage`. That structurally answers R1's missing fact.

3. **Dispute scope: resolved.**
   - Accepted M09a text authorizes ownership and content dispute candidates.
   - M12 fences "every other publication" through the generic `protect(PublicationCandidate)`.
   - #122 adds no dispute policy and no dispute tests.

4. **Fenced input: resolved.** The fenced input is the typed `PublicationCandidate`, taken after an exact journal-controlled readback. The 3.8h estimate now has a fixed primary input. Its components sum correctly: 1.55 + 0.75 + 0.85 + 0.65.

## R1 non-blocking items

- **Rollback boundary: anchored.**
  - Backup writes `KEY_NAME`, `DATABASE_NAME` and the authority names into the staged store.
  - `_swap_store` exchanges only `STORE_NAME`.
  - The witness must sit outside the `STORE_NAME` tree and the journal root. A witness root inside, aliased to or containing a rollback target is rejected.
- **Claude test name:** stated exactly.
- **No synthetic receipt:** zero synthetic receipts or ACKs is stated.
- **#124 edge:** #124 depends on #123, which depends on #122. "Transport through #123" is consistent with that chain.

## Split trigger vs M12

- **Sound.** The receiver slice is separable: `record_export_intent`, `record_receiver_evidence` and the interrupted-export test. The remaining three tests still cover `protect` and restore. The M13 consumer behind the fence is unaffected.
- **Clarification (non-blocking).** The two trigger sentences diverge. The first says to return to Refine; the second only says to split. Both should route through Refine, for three reasons:
  - Any split amends accepted M12, as the M09 precedent did. The split leaf must sit upstream of #124.
  - A new journal-side issuer falls outside M12's files, which are only `monitor_recovery.py` and its test. It falls inside closed #310's ownership.
  - Splitting the receiver work frees hours but does not authorize that issuer. The return to Refine must place it.

## JIT entry conditions

- Rerun the delivered coverage test by exact node ID at `ab9db800`, and record the command and its output. The expected test is the M09a test `test_unqualified_source_gap_publishes_without_project_write_or_ack` or the Claude-specific equivalent. This also confirms that "qualified-policy Claude coverage" equals the unqualified-source gap case.
- Confirm that the `PublicationCandidate` fields include the store identity, basis and sequence. The excerpt is truncated before the candidate is constructed and splices into `backup.py` without a label.
- Anchor the monitor-side snapshot enumeration. Only the project backup and restore paths were excerpted.
