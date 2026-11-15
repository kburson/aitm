[07:17:34]
SOURCE_310: PASS

**Scope:** I only read what you pasted: the JIT, the R1 review, the recovery diff, the helper excerpts and the receipts. This session has no shell or file tools, so I didn't recompute the diff or log hashes. I also couldn't confirm independently that the product source is unchanged from R1, and I've taken that as you supplied it.

## The three R1 blockers

1. **Future-version refusal: fixed.**
   - Both tests set `user_version = 7` and get "Unsupported routing journal schema" from the coverage `publication_candidate`, the dispute `publication_candidate` and `dispute_changes`.
   - Each refusal comes right after the same input passed. In the coverage test, `reopened.publication_candidate(stored) == candidate` passes just before. In the dispute test, `second` was last shown unchanged (`unchanged == second`).
   - The match text can only come from `transaction()` → `_current_version` → `_validate_identity`, whose allowed set excludes 7. That code sits outside the `try`, so the refusal comes from the existing store validator and the existing transaction behavior is kept, as the JIT requires.
   - The stored version is confirmed to still be 7 afterwards, so nothing was written.
2. **Replaced full row: fixed.**
   - **Coverage:** the substitute row is valid and canonical. `alternate` is encoded with `validate_ref`, `_decode(replacement) == alternate` is asserted, the identity is recomputed with `_coverage_key`, and the old seal is kept.
     - Both `publication_candidate` and the stored reader refuse it; `coverage_changes` fails with "Invalid private journal coverage". So the stored-row validator catches it, not just a mismatch with the input.
     - After restoring the row, the same candidate is issued again.
   - **Ownership:** a canonical row is moved to an earlier sequence that exists in `commits`.
     - `publication_candidate(first)` refuses.
     - The moved row reads back and issues a candidate with a different identity.
     - `second` is unaffected.
3. **Both canonical byte checks are reached: fixed.**
   - Both tests use `raw + b" "`. They assert that `_decode` still accepts it for `ClaimEvidence` and for `_ContentDisputePayload`, so the failure has to come after decoding.
   - **Ownership:** `_decode` with `validate_ref` is the only check before the comparison. The claim columns, UUIDs and digest are untouched.
   - **Mutation evidence is consistent:**
     - The tampered bytes also change `raw.hex()`, and for content the row digest, so the identity changes. `publication_candidate` would therefore still refuse even with the comparisons disabled.
     - That means the comparisons carry the outcome only on the reader path, and the two "DID NOT RAISE" failures should be the `dispute_changes` assertions. That fits your description and the "2 failed, 1 passed" result (the pre-content-schema test touches neither comparison).
     - This proves that the stored content validator and `_decode` both accept the trailing space without the new comparison.

## Proof identities

- The tested commit `a500768` has parents `4cfb418` (literal trunk) and `300fba8` (the PR #311 head). Its tree `84028ef` equals both `tree` and `reviewed_tree`. This settles the open R1 question about tested vs. head.
- The +4 tests are the 3 new tests plus the unchanged wheel smoke. No baseline nodes are missing, which settles the R1 count note.
- The signed run (attempt 1) passed. Locally, 1281 passed and 5 of 5 targeted tests passed.
- The restart readback now runs inside the `Ledger.open`/`Ledger.writer` monkeypatch, which settles another R1 note.
- `dispute_changes` has no upper bound in its query, but `REFERENCES commits` plus `_validate_foreign_keys` effectively bound it.

## Non-blocking residuals

- **Content relocation isn't tested.** No test moves a valid, canonical content-dispute row to a different sequence or key. The `altered` content substitute is refused, but probably by the semantic `_stored_content_dispute` check. The selection code is shared with ownership, which is proven.
- **Moved dispute rows get new candidates.** A relocated ownership row issues a fresh valid candidate. This matches the JIT's limit that dispute rows are opaque and trusted only through journal custody, but #122 must not treat a dispute candidate as authenticating the row independently.
- **v7 doesn't reach the new version checks.** The range checks inside the `try` never run for v7, so they act only as a second line of defense.
- **Earlier R1 notes still stand:**
  - Exceptions other than `ValueError` and `LedgerError` on malformed input (for example a non-`SourceRef` `record.key`) still refuse, but not with the sanitized message. The STRICT schema now rules out the storage-type cases.
  - `_JournalDispute.__post_init__` still checks only the record type.
  - `PublicationCandidate` can still be built publicly without verification.
- **Locked coverage test name:** I still can't tell from these artifacts whether `test_unqualified_source_gap_publishes_without_project_write_or_ack` is the locked test name.

This verdict covers source recovery only. Delivery and native Close stay with the existing external gates. Epic #2, C01 and the production cutover weren't assessed.
