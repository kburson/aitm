[06:55:53]
SOURCE_310: HOLD

**Scope:** I reviewed only the pasted JIT, the diff, the helper excerpts and the receipts. I ran no tools and did not recompute the hash of `producer-source-exact.diff`. The diffstat (277+75+88 = 440, insertions only) matches the pasted diff. The receipt's `tree` equals its `reviewed_tree`. `tested` (677ad9f) is not the PR head (2e8236c); I'm treating it as the PR merge commit, but nothing supplied shows that.

## Blocking JIT mismatches

1. **Refusal of unrecognized schema versions isn't proven.**
   - By inspection, the code refuses them: `!= _COVERAGE_SCHEMA_VERSION` on the coverage path, and the range `_CONTENT_DISPUTE_SCHEMA_VERSION <= v <= _COVERAGE_SCHEMA_VERSION` on the dispute path.
   - That check relies on `_store._current_version` returning the raw value. The JIT calls this "the existing store validator", but its body isn't in the supplied helpers.
   - No test sets a future `user_version` (for example 7) on either path. The only version tests are v4 coverage and v2 dispute.
   - The JIT says "no future version qualifies" and asks that unrecognized versions be refused, so this needs a v7 refusal test for both `publication_candidate` paths and for `dispute_changes`.
2. **"Replaced full row" isn't tested.**
   - The storage tampering in the tests only overwrites one column with `{}`: `source_coverage.payload` and `disputes.evidence`. That proves malformed rows are refused, not substituted ones.
   - `replace(first.dispute, record=second.dispute.record)` and `identity=two.identity` change the input, not the stored row.
   - Missing case: a stored row replaced by another row that is valid and canonical. For coverage, that means a row that decodes but whose seal or sequence doesn't match. For disputes, it means a valid row moved to a different key or sequence. The refusal of that case is what matters.
3. **The new canonical-byte checks in the dispute readers never run.**
   - `_encode(...).encode() != raw` in `_verified_ownership_change` and `_verified_content_change` is the main new check for disputes.
   - The only tamper input, `b"{}"`, almost certainly fails at `_decode` before reaching this comparison.
   - JIT: "malformed canonical bytes". It needs a test with bytes that decode correctly but aren't canonical, such as reordered keys or extra whitespace, for both ownership and content.

## Non-blocking defects and notes

- **Some errors escape the sanitized message.** Only `ValueError` and `LedgerError` are normalized (as the JIT says), but a row with the wrong SQLite storage type raises other errors that come through unsanitized:
  - `UUID(None)` raises `TypeError`.
  - `re.fullmatch` on a non-str digest raises `TypeError`.
  - An incoming `record.key` that isn't a `SourceRef` raises `AttributeError`.

  These still refuse, but the message isn't the shared sanitized one.
- **`dispute_changes` has no upper bound.** Its query is `d.sequence > ?` with no `<= _tip`, so a future row is listed rather than refused unless a foreign key from disputes to `commits` prevents it (not shown). `publication_candidate` does enforce `<= tip`.
- **`_JournalDispute.__post_init__` checks only the record type.** It doesn't enforce `SourceRef`, `UUID`, or lowercase 64-hex for `row_digest`. Mismatches are still caught later by full equality plus the canonical `_encode` comparison.
- **`PublicationCandidate` is public and can be built without verification.** #122 must not treat an instance as proof of verification.
- **The restart readback isn't checked for destination access.** The second `writer()` block runs outside the `Ledger.open`/`Ledger.writer` monkeypatch.
- **"Existing named coverage test":** the diff adds `test_unqualified_source_gap_publishes_without_project_write_or_ack` as a new test. Whether that name is the locked one can't be checked from these artifacts.
- **Test count:** 1277 → 1281 is +4, but only 3 test functions were added. That's presumably from fixture parametrization, but nothing supplied shows it.

## What matches the JIT

- **Fields and types:**
  - `JournalChange` gets a trailing optional `dispute` and rejects it combined with coverage, disposition or paired.
  - Disposition and paired behavior is unchanged.
  - The closed `_CandidateBasis` holds coverage, ownership and content.
- **Ownership SELECT:**
  - Columns, LEFT JOIN, `d.sequence=? AND d.key=?` and `ORDER BY sequence,key,contender,digest,evidence` match the JIT.
  - A missing claim raises an error instead of being dropped.
  - Original project and contender UUIDs are checked for canonical form, and the digest is checked as 64 lowercase hex.
  - `_stored_claim` runs, followed by `_encode(_ClaimPayload, validate_ref)`.
  - Evidence is decoded, re-encoded and compared to the stored bytes.
- **Content SELECT:** columns, predicates and ordering match. `_stored_content_dispute` is reused, and `row_digest` is `sha256(raw)`.
- **HMAC inputs and namespaces:** both namespaces are correct. The array order for ownership, content, coverage and dispute candidates matches. `json.dumps` uses the specified flags, and a StrEnum serializes as its plain value.
- **`publication_candidate` checks:**
  - It uses one read transaction and requires an exact `JournalChange`, exactly one of coverage or dispute, and `0 < seq <= tip`.
  - Coverage must be v6 only and the sole `_COVERAGE_ROWS` row, sealed and committed through `_stored_coverage`, with equality checked both as dataclasses and as canonical bytes.
  - A dispute must match exactly one stored row by sequence, key, full equality and canonical `_JournalDispute` encoding; sequence alone doesn't select it.
  - The `transaction()`/lease handling sits outside the `try`, so it keeps its existing behavior.
- **No destination, publication, ACK or mutation surfaces:** no writes, schema changes or key material are added, and the v2 test confirms the stored version and rows are unchanged.

## Separation

This verdict covers the source review only. It doesn't touch the review action or the existing gate decisions. Epic #2, C01 and the production cutover weren't assessed.
