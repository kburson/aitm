[06:01:06]
**JIT_310: HOLD**

I checked this against the supplied text only. The excerpts are spliced fragments, so anything they don't show is listed as unverified, not assumed.

### Blockers

1. **The frozen ownership SQL can't run the claim check the JIT itself requires.**
   - The JIT says to "verify the original stored claim row before treating `c.project` as durable destination custody."
   - The frozen query selects only `d.key,d.contender,c.project,d.digest,d.evidence,d.sequence`. It never selects `c.payload` or `c.digest`, so `_stored_claim(first, digest)` (the check the content path uses) can't run.
   - Nothing supplied shows that `claims.project` is covered by the claim digest or any seal. Today, `as_of` uses `UUID(project)` as stored, without checking it.
   - **Fix:** add `c.payload,c.digest` to the select and run `_stored_claim` before using the project. Also state exactly what it proves about `project`. If the project isn't digest-bound, call it "the stored project, same as `as_of`," not authenticated custody.

2. **The inner join can silently drop dispute rows, so "one wrapper per canonical stored row" isn't guaranteed.**
   - `as_of` reads `disputes` without joining `claims`.
   - The shown part of the `disputes` schema has no `REFERENCES claims(key)`. That part is cut off, so I can't confirm it.
   - With `JOIN claims`, an ownership dispute with no claim row would vanish from `dispute_changes` while still appearing in `as_of`.
   - **Fix:** use `LEFT JOIN` and refuse any row with no claim. Alternatively, prove the foreign key from the full schema blob.

3. **The dispute path has no version guard.**
   - `content_disputes` comes from a separate schema fragment (`_CONTENT_DISPUTE_SCHEMA`), so older stores may not have the table.
   - The JIT gates coverage only ("v6 or later recognized"). It sets no version floor for `dispute_changes` or the dispute branch of `publication_candidate`, and no ceiling for "future" schemas.
   - The value v6 isn't visible in the evidence.
   - **Fix:** name the constant to compare against (`_COVERAGE_SCHEMA_VERSION`, not a literal 6), plus the content-dispute version constant and the highest recognized version. State that below the floor, `dispute_changes` returns ownership disputes only or refuses, and that a dispute candidate is refused. Add one test for an older dispute-schema store.

4. **The candidate and row identities aren't specified exactly.**
   - `pseudonymize(namespace, raw_reference)` takes a namespace matching `[a-z][a-z0-9-]{0,63}` and a non-empty `str`.
   - The JIT names neither namespace and doesn't define how a row, change and basis become `raw_reference`. That means:
     - field order and separators
     - bytes written as hex (the evidence bytes and `d.payload`)
     - the UUID text form
     - the sequence in decimal
     - a basis tag (`coverage` / `ownership` / `content`)
   - Without this, staying the same across restarts and differing for rows at the same sequence can't be tested exactly, and a later recovery consumer can't recompute the identity.
   - **Fix:** freeze both namespace strings and the exact encoding in the JIT.

### Conditions (fold into the revision, not blockers)

- **Ownership `d.digest` is checked for format only.** Its derivation isn't shown. Either verify it, or reduce the "corrupt rows" claim to what is actually checked: service references, exact evidence re-encoding and the digest format.
- **`validate_source_ref` can raise `ValueError` as well as `LedgerError`.** Malformed input fails in `split`/`fromhex` with `ValueError`. Every refusal path must turn both into the same refusal.
- **Name the evidence re-encoder and give its codec blob.** The #309 safety argument cites "codec blobs", but only four file blobs are listed.
- **Missing tests:** a wrong key and a corrupt row on the dispute path, and a retry that still refuses the same ambiguous row.

### Verified as stated

- **Split and scope:** the trunk base, the closed #300 prerequisite, and the fences around #119, #122 and #309 are consistent with the Refine.
- **`JournalChange` change:** a trailing optional `dispute` field keeps positional constructors and the `JournalView` layout working. Rejecting it alongside coverage, disposition or paired extends the existing `__post_init__`.
- **Coverage readback:** reading at the exact sequence via `_COVERAGE_ROWS` + `_stored_coverage`, with `_tip` bounds, is sound because `source_coverage.sequence` is `UNIQUE`. Reusing those helpers directly settles the Refine question about who owns `coverage_changes`.
- **Content disputes:** `content_disputes.key` is the primary key, so only ownership disputes can share a key and sequence. Matching on the whole row identity is the right fix.
- **Refine conditions 2 and 3:** the keyed-reference functions (`pseudonymize`, `validate_source_ref`) are now shown. The identity is deterministic, isn't stored and uses no new key.
- **No new write or consumer:** the JIT adds no schema, sequence, ACK or consumer.
- **Estimate:** 1.25h, Size S, is still plausible. The fixes are spec-only. #300's actual time came in far under its estimate, which points the other way from an overrun.
