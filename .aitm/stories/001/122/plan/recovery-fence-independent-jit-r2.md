[10:30:02]
JIT_122: PASS

Implementation is authorized at trunk `ab9db80098849e323d5122eb47bf48f377107058`. Edits are limited to `src/aitm_usage/monitor_recovery.py` and `tests/test_monitor_recovery_fence.py`, with a 3.8h budget, Size M, and the 2.4h and 4.0h stops armed. The binding conditions below are clarifications of the plan, not scope changes.

## R1 premise correction

R1 blocker 1 assumed that one journal sequence holds at most one identity. That is false.

- `test_journal_only_candidate_verifies_distinct_disputes_at_one_sequence` passed at the exact commit and tree.
- In that test, a single `reserve_batch` commit produces two disputes with `first.sequence == second.sequence` and `one.identity != two.identity`.
- Both reconstruct deterministically and leave `as_of()` unchanged.

R1's "second identity at a witnessed sequence = fork" rule would have held a valid delivered #310 behaviour. The revised rule replaces it correctly.

## R1 blockers

| # | Item | Disposition |
|---|---|---|
| 1 | Same-sequence fork | **Closed.** All candidates at a sequence come from one commit, so the set at sequence N is fixed once N is committed. A keyed digest over the complete coverage ∪ dispute set at N, in lexical (basis, identity) order, therefore separates the two cases. A valid pair {A,B} seals digest D, and both members match D. A restored-then-reappended N gives {C}, {A,C} or {A} with digest D′≠D, which is held even when the individual identity validates. A restore that reproduces an identity-equal set is the same publication, not a fork. The rules "older unwitnessed held" and "new member only at current high-water and present in both sets" close the remaining paths. |
| 2 | Per-publication/receiver uniqueness | **Closed.** At most one key and digest is allowed per (FencedPublication, receiver). A fresh key is refused before attempt 1, a reused key with other bytes is refused, and a test for this is named. |

## R1 conditions 3–8

| # | Condition | Disposition |
|---|---|---|
| 3 | Trusted-anchor limits | **Adopted.** Gaps, damage and predecessor breaks hold. A proper prefix is stated to be indistinguishable from an older chain. The explicit (ordinal, seal) anchor is retained independently. Joint rollback of the witness root and its anchor is excluded, and #126 supplies the production anchor. |
| 4 | No-replace fsync | **Proven.** With `replace_pending=False`, `scopes._publish` does: `O_EXCL\|O_NOFOLLOW` temp at 0600 → `fsync(fd)` → `check()` → `publish_noreplace` (returns `False` if the name exists) → `fsync(directory.fd)` → `check()`. `HostFilesystemError` maps to `LedgerError`. No edit to `scopes.py` is needed. |
| 5 | Rollback root completeness | **Adopted.** The journal root is derived from the writer. Project stores are explicit, and an empty set is valid. Production completeness belongs to #125/#126. |
| 6 | Acceptance vs absence scoping | **Adopted.** Acceptance from any durably opened attempt is terminal for the triple. Absence applies to the current pending attempt only. |
| 7 | #124 receiver contract | **Adopted.** The receiver must deduplicate on key or permanently reject the absent attempt. Otherwise absence does not confer eligibility. |
| 8 | Fence ordering liveness | **Adopted.** #123 drives candidates in journal order. |

Late acceptance and one-use absence are also correct as written:

- Absence eligibility is consumed durably when the successor intent opens, so a restart cannot replay it.
- A conflicting acceptance overrides absence and is terminal.
- Absence arriving after an acceptance cannot reopen sending.

## R1 missing proofs

- **Change-listing APIs: closed.**
  - The signatures are `coverage_changes(after_sequence: int)` and `dispute_changes(after_sequence: int)`, both returning `tuple[JournalChange, ...]`.
  - Both range-check against `_tip` and SELECT inside a transaction scoped to the call.
  - The delivered tests assert that `as_of()` and the readbacks are unchanged afterwards.
- **Lease and key access: closed.**
  - `Registry.writer()` yields a leased `Registry`, and `.lease` raises once custody ends.
  - `source_evidence()` returns `_ServiceEvidence` with `.key` and `.key_id`.
  - `validate_source_ref` authenticates `SourceRef`.
  - None of this needs journal, ledger or scopes code.
- **Pin and ancestry primitives: closed.**
  - `_pin_directory` checks owner, mode and ACL, uses `O_NOFOLLOW`, and rechecks the identity chain through `check()`.
  - `_physical_ancestry` returns `(dev, ino)` ancestors with casefolded NFC tails.
  - `_guard_path` shows the overlap idiom, including firmlinks.
  - Directory hard links are not a supported APFS user case.
- **No-exporter claim: closed.** No `capture_monitor_backup` exists in src, and M16 owns it. The whole-root treatment is conservative regardless.
- **Claude fixture: closed, with one qualification.**
  - In `admitted_sources`, the Claude source is admitted and approved while the native SOURCE is qualified.
  - `prepare` on the Claude source fails qualification and yields the UNQUALIFIED_SOURCE coverage change.
  - `Ledger.open` and `Ledger.writer` are patched to `project_access`.
  - The excerpt omits the `def` line. Binding it to the passed node relies on file and context, and the test author must cite the exact function.

## Binding implementation conditions (no scope change)

1. **Key side-effect.**
   - `source_evidence()` initializes a key and saves registry state when none exists. The fence must hold, without calling it, when `writer.view().source_key_id is None`.
   - It must then call `validate_source_ref(reconstructed.identity)` with that evidence.
   - Add an assertion that a forged candidate against a keyless registry creates no key file.
2. **Type-strict comparison.**
   - `_CandidateBasis` compares equal to `"ownership"`. Require exact types: `PublicationCandidate`, `_CandidateBasis`, `SourceRef`, and `int` (not `bool`).
   - Witness and return only the reconstructed instance, never the caller's.
3. **Error normalization.** Map `coverage_changes`'s `ValueError` (from a future or stale sequence) and `dispute_changes`'s `LedgerError` both to held, with no append.
4. **Digest encoding.**
   - The set digest is length-prefixed and includes sequence and member count.
   - All seals use new domain labels that are distinct from `monitor-source-namespace/v1`, `monitor-source-proof/v1`, `monitor-source-ref/v1` and `monitor-journal-publication-v1`.
5. **Readback barrier.**
   - When `_publish` returns `False` at the expected ordinal, perform an exact byte readback.
   - Then `fsync` the directory and run `check()` before returning success, following the `view(_confirm_publication=True)` pattern.
   - Stray `.publishing-*` names are ignored and never treated as envelopes. Any other unexpected name holds.
6. **Root derivation.**
   - The derived journal rollback root must physically contain the journal store, the source key and the coordinator lease.
   - Apply overlap checks in both directions between the witness root and each rollback root.
   - If the journal store's path cannot be derived from the writer or journal without a non-target edit, that is the existing Refine trigger.
7. **Monitor identity.** Derive the monitor identity from writer-held state, such as `key_id` or the namespace from `evidence.as_of()`. Needing new registry or journal code is a Refine trigger.
8. **Same-sequence liveness.** #123 must fence every member of a sequence before advancing the high-water mark. Otherwise a skipped same-sequence member becomes permanently held. This extends R1 item 8.
9. **#124 payload clause.** "#124 queues changed compatible payloads explicitly" creates no exception on this path. A second digest for the same (publication, receiver) is always refused here.

## Ownership and triggers

The triggers are unchanged and are confirmed to be present in the plan:

- **Ownership:** #123 owns rendering and journal-order driving. #124 owns transport, verifier adapters and the receiver dedup contract. #125 owns the installed layout. #126 owns snapshot enumeration, current-tail verification and the expected anchor. There is no activation in this slice.
- **2.4h checkpoint:** guarded `protect`, the authenticated chain, recovery, and the three non-receiver named tests must be green before any receiver work begins. Re-project the total at that point.
- **Refine triggers:** a projected total above 4.0h, a missed checkpoint, any edit to a journal, ledger, scopes or other non-target module, or a required new candidate issuer. Any of these returns to Refine. A receiver-slice split needs an M12 amendment placed upstream of #124.
- **Delivery gates:** focused tests with `test_monitor_journal.py` and `test_monitor_delivery.py`, the complete locked suite, signed hosted validation on the exact candidate, independent source review, verified delivery, native Close, and receipt and report ownership preserved in the planning and Project readback.

The budget margin is roughly 0.0–0.2h, so the checkpoint is the operative control.
