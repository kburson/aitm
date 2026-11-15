[10:25:26]
JIT_122: HOLD

Two plan defects conflict directly with the review criteria: same-sequence identity, and no repeated external effects. Several load-bearing APIs are also asserted without evidence. Both defects can be fixed by amending the text inside the two target files. Neither needs Refine unless one of the triggers below fires.

## Blocking defects (amend the plan text, then re-run JIT)

1. **Same-sequence fork is not refused.**
   - The plan says: "Same-sequence candidates with different durable typed identities remain distinct."
   - `publication_candidate` enforces a single tip with sequence in `(0, tip]`. Each `JournalChange` carries exactly one of coverage or dispute. Coverage and dispute therefore share one sequence space.
   - So a second identity at an already-witnessed sequence can only come from a rollback fork or a forgery.
   - As written, the sentence can be read as accepting it. That would let a restored-then-reappended journal escape the fence.
   - **Required text:** a candidate whose sequence is ≤ the witnessed high-water mark and whose identity differs from the witnessed identity at that sequence is a fork. It is refused and recorded as held. "Distinct" means only that it is never treated as an exact retry.
   - Add an explicit fork test to the existing same-sequence case.

2. **One publication can be exported more than once to the same receiver.**
   - The plan refuses reuse of a receiver and key with a different digest. It does not refuse the same FencedPublication and receiver under a fresh operation key.
   - A caller can therefore open a second attempt-1 intent and send twice.
   - **Required text:** at most one operation key and one digest may exist per (FencedPublication, receiver). There are two ways to achieve this:
     - derive the key deterministically from the publication identity and the receiver reference, or
     - durably refuse a second key.
   - If #123 legitimately needs re-renders, the plan must name that policy explicitly. Otherwise a single key is the rule.
   - Add a test for "same publication + receiver, new key → refused".

## Corrections required before PASS (wording or conditions, no scope change)

3. **Truncation overclaim.**
   - "A truncated or modified chain also holds" is true only for:
     - ordinal gaps,
     - torn or modified envelopes,
     - predecessor-seal breaks.
   - Truncating the tail of a self-chained series is indistinguishable from an older witness.
   - State this residual plainly: witness-root rollback is outside the threat model, and that is why the root must sit outside every rollback root.
   - Do not test a claim the design cannot make.

4. **Publish primitive semantics.** The plan reuses `scopes.py:274 _publish` but supplies no evidence that it:
   - fsyncs the parent directory, or
   - refuses an existing target name. Using `os.replace` semantics would let a crash-replay overwrite ordinal N.

   Condition: envelope publication must be no-replace (exclusive link/rename) and must fsync both the file and the directory. If `_publish` lacks either property, implement it locally in `monitor_recovery.py`. Editing `scopes.py` is out of scope.

5. **Rollback root completeness.**
   - The fence cannot verify that a caller-supplied root list is complete.
   - Derive the journal root from the leased writer rather than accepting it from the caller.
   - Accept project stores explicitly. An empty project set is valid for the journal-only Claude case.
   - Record "root-set completeness in production" as owned by #125/#126.

6. **Accepted vs. absence scoping.**
   - Absence must bind the exact current attempt. The plan has this right.
   - Accepted evidence should bind the full (receiver, key, digest) triple and be honored for any already-opened attempt. Otherwise a late acceptance of attempt 1 after attempt 2 opens is misclassified as "held".
   - Accepted evidence is terminal.

7. **Receiver contract for #124 (record it, do not implement it).**
   - Successors reuse identical key and bytes. The guarantee that a verified absence never yields two effects therefore depends on the receiver either:
     - deduplicating on operation key, or
     - permanently rejecting the absent attempt.
   - State this as a precondition that #124 verifier adapters must satisfy.

8. **Fence ordering liveness (non-blocking).**
   - Because older candidates are refused, consumers must fence in journal order. Otherwise a skipped dispute becomes permanently unpublishable.
   - Note this as a #123 obligation.

## Missing proof (supply at JIT re-run)

- **Change-listing APIs.**
  - The exact signatures and read-only behaviour of `coverage_changes(after)` and `dispute_changes(after)` at `ab9db800`.
  - Neither appears in the evidence.
- **Lease and key access.** The writer-lease handle API, and how `monitor_recovery` obtains `_ServiceEvidence.key_id` plus a keyed-seal capability from the active writer.
  - The excerpt shows only that `key_id = sha256(key)` and that `SourceRef` tags are HMAC-keyed.
  - It does not show that a lease holder can reach them without new journal code.
- **`_pin_directory` and `_physical_ancestry`.** Their signatures, and whether they cover owner and mode checks and alias detection (symlink and hard-link/inode). Only line anchors were supplied.
- **No-exporter claim.** "No monitor-side snapshot exporter ships" is asserted, not shown.
  - A grep of `ab9db800` for `capture_monitor_backup`, or for any monitor journal/key copy, would close this.
  - The conservative whole-root treatment is sound regardless.
- **Claude fixture.** The control node `test_unqualified_source_gap_publishes_without_project_write_or_ack` passed at the exact commit and tree with a recorded command. This satisfies Refine entry condition 1.
  - Nothing shows that its fixture is the Claude source the plan calls "qualified-policy".
  - Cite the fixture's source and policy lines.

## Verified from the supplied evidence

- **Candidate fields.**
  - The fields are `sequence`, `basis` and `identity: SourceRef`.
  - `identity` is `_publication_reference(evidence, "monitor-journal-publication-v1", basis, sequence, material)`, which is keyed under the service key.
  - Store identity is not a candidate field. The plan correctly carries `key_id` in the witness, derives it from the writer and confirms it on reopen. This closes Refine entry condition 2.
- **Snapshot enumeration.**
  - M16 places monitor snapshot enumeration and current-tail verification in #126.
  - The backup excerpt swaps only `STORE_NAME`.
  - Treating the whole journal root plus the project stores as rollback roots is conservative and correct. This closes entry condition 3, subject to the grep above.
- **Interrupted append.** "Prepared" until a file and directory fsync plus revalidation barrier passes. No external-visibility assertion is made.
- **Intent and evidence model.**
  - Intent is written behind a durable barrier.
  - Exact replay is idempotent.
  - Absence eligibility is one-use and consumed durably when the successor is created, so it survives restart.
  - There is no default verifier, the verifier is closed and gets its own fixture key, no output bytes are stored, and no clock or receipt heuristics are used.
- **Ownership and gates.**
  - Ownership is respected: #123 owns rendering and #124 owns transport and verifiers. There is no activation, and the four named tests are present verbatim.
  - The delivery gates are listed: locked suite, signed hosted validation, independent source review, verified delivery, native Close.

## Budget

- Components: 1.55 + 0.75 + 0.85 + 0.65 = 3.8h, leaving a 0.2h margin before the four-hour stop.
- Amendments 1 and 2 add roughly 0.1–0.2h of state checks and tests, which leaves essentially no margin.
- That is realistic only with the split armed.
- **Checkpoint:** if `protect`, the witness chain, recovery and the three non-receiver named tests are not green by 2.4h, stop. Route the receiver slice through Refine. Refine has already ruled that any split amends M12 and must sit upstream of #124.

## Exact hold and return-to-Refine triggers

Return to Refine, not JIT, if any of these occur:

- Obtaining the lease, `key_id` or a keyed-seal capability requires adding or changing code in any routing-journal, ledger or scopes module. That is a new journal issuer, owned by closed #310's area.
- `coverage_changes` or `dispute_changes` do not exist with read-only `after` semantics at `ab9db800`.
- Any edit outside `src/aitm_usage/monitor_recovery.py` and `tests/test_monitor_recovery_fence.py` becomes necessary.
- The projected implementation total exceeds 4.0h, or the 2.4h checkpoint is missed.

**Release condition:** amend items 1–2, adopt conditions 3–7 into the plan text, supply the five missing proofs, then re-run JIT. No implementation is authorized meanwhile.
