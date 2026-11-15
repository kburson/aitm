[22:31:28]
SOURCE_300: HOLD

**Blocker**

1. **Finding 4 is fixed as requested, but the evidence doesn't show the test is decisive.** The test `test_coverage_rejects_reserved_variants_even_with_a_valid_row_seal` now rebuilds `identity` itself. It uses `json.dumps(..., separators=(",", ":"), sort_keys=True)` on the altered payload with `observed_at` removed. The product computes the key differently, with `_coverage_key`, which runs `_encode(_CoverageIdentity, ...)`.
   - The supplied evidence doesn't show that `_encode` produces the same bytes as that `json.dumps` call.
   - If the two differ, the read is still rejected because the key doesn't match. Rewriting `payload` the test's way could also fail the `canonical != raw` check. Either way the test passes without the decoder rejecting anything.
   - None of the seven mutation probes covers the decoder.
   - **Fix:** add a control case with no override (`{}`). It should rewrite `identity`, `payload` and `seal` the same way and assert `coverage_changes(0)` still returns the original event. Alternatively, add a probe that loosens the reserved reason, extent or field decoding and shows each variant case fails.

**Resolved**

- **Finding 1, the stability selector:** the Claude cases (excluded by the matrix after `qualify`) now reach every guard in `_stable_live_exclusion`:
  - The untouched `valid-matrix-exclusion` case records exactly one event.
  - The cases `duplicates`, `missing-verifier`, `foreign-root`, `replaced-root`, `foreign-generation`, `foreign-lease` and `wrong-profile-type` each assert no coverage and that the store stays at v4.
  - Seven probes match the seven guards (type, lease, root path, `_pinned`, `callable`, `validate_source_ref`, `len <= 1`). Removing any one guard alone makes the test fail.
- **Finding 2, paired settlement after a coverage-first v6 upgrade:** the excerpt shows `_enable_paired` only acts when `version == _SCHEMA_VERSION` (4), so it does nothing on v5 and v6. The new test goes v4 → coverage → v6 → `settle_disposition`. It checks the settlement's sequence, that the store stays at v6, that the coverage event survives, and that `as_of(event.sequence)` has no settlements.
- **Finding 3, authorization on `coverage_changes`:** the excerpt shows `transaction()` calls `self._writer.lease` first. The new test refuses both a writer that has exited and an old journal after the registry is reopened. A new journal on the reopened writer reads the event back.
- **Grok amendment:** it is recorded as narrow, consistent with the code and covered by the tests:
  - **Unqualified Grok:** refused before any payload read.
  - **Exact consent:** gates coverage (0 or 1 event).
  - **Qualified Grok:** keeps the old cursor refusal.
  - **Ordinary metadata failure:** the code swallows it, and it falls through to the cursor refusal.
- **Signed evidence agrees with itself:**
  - **Identifiers:** head `b82eafa…` matches `headRefOid`, and the base and tree hashes match. Status is pass with no failures.
  - **Coverage:** 11532/12546 in every source.
  - **Test counts:** 1277 = 1272 + 5 new tests, and focused 36 = 31 + 5.
  - **Product source:** the source diff contains only product changes. `product_source_matches_first_review` is true. The two identical `7b73752a…` hashes aren't labelled; I read them as the product src trees before and after, which fits that flag.
