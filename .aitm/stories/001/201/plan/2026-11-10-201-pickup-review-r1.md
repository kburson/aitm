# #201 independent JIT review, round 1

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup. November 10, 2026 (America/Chicago).

# Independent review of #201 M08b2 JIT

**Verdict: HOLD** on `e0785282da87a8df6bc8cfce7f0ba79ecc5bd5ccd79afe46d112b42ddb9f595e`

This verdict covers only #201. I didn't use any tools, so I couldn't recompute the SHA-256. The verdict applies to the bytes as they appear in this packet under that digest.

The design is sound. The plan holds because it leaves seven correctness or cap points open, and those must be fixed in a revised JIT before Develop.

## What passes

- **v1 history:** first claims, the original project, scope, time and ClaimEvidence stay immutable. The plan rewrites no legacy rows, does no schema guessing and adds no side state file. The revision-one fingerprint is derived lazily and correctly. The plan also correctly rules out the old claim digest as a substitute, because that digest includes scope and time basis.
- **Migration transaction:** the plan uses `BEGIN IMMEDIATE`, avoids `executescript` inside the transaction, and makes `user_version=2` part of the same transaction. It refuses unknown, mixed or foreign state, injects a failure before COMMIT and tests retry. That design is correct, since SQLite DDL and the user version are both transactional.
- **Writer-issued authority:** `ScopeState.verified_revision` is called inside the write transaction on the issued batch. A supplied DTO is never accepted. The immediate predecessor must equal the durable head, and a skipped or held predecessor is never staged by implication. Revision numbers, filenames and counters confer nothing. Dispute precedence is preserved.
- **v1 epoch join:** the join reuses the delivered `_admitted_readers` pattern (`position` or `observed.checkpoint.cursor`, plus a fixed re-authenticated prefix) and requires the same source, locator and incarnation. That is correct.
- **v1 limitation:** the plan honestly says v1 has no raw observation witness beyond the epoch prefix and requires only normalized genesis equality. I accept that limitation, subject to correction 2.
- **Multiple edges in one batch:** the order is safe. Each edge is evaluated against the in-transaction head after every actual stage, so an out-of-order emission can only hold. Later ordinals rise monotonically because each successor's later ordinal must exceed the head's. Ordering the latest view by `(sequence, later_ordinal)` is correct.
- **Exclusions:** there is no quota refinement, content dispute, fold, ACK or destination write. Every unresolved diagnostic keeps the earlier cursor.
- **Gates:** #119 and #202 stay gated.
- **Cap:** 1.10 + 2.65 = 3.75 hours is nominally within four, but see correction 6.

## Mandatory corrections

1. **Stale no-op must match the whole edge.** A no-op currently needs only a matching `(key, material)`. Require that the stored predecessor ref also matches. On the same locator, the later ordinal and prefix ref must match too. If the same successor material arrives with a different predecessor, or the same locator gives a different ordinal or prefix, that is held for #202. It must not be a REPLAY. Add a RED test for this.

2. **Define what `prefix_ref` covers and pin the rewrite tests.** The JIT must say exactly which bytes the #199 `prefix_ref` commits to: from the file start through the later row, or only that row. The claim that v2 "catches a rewrite after the original epoch prefix" is only true for the first meaning. Tests must:
   - rewrite bytes between the epoch prefix and the original row, and between the original row and the head's later row, without changing normalized material, then show v2 holds;
   - pin the documented v1-head behaviour, where only normalized genesis equality is required, as a named limitation test.

   Record the limitation in the PR and the retrospective.

3. **Cover a later edge that arrives after the cursor has advanced.** `verified_revision` needs the original and predecessor proofs in the same batch. Once positive progress moves the cursor past an original row (possible whenever no obligations are left), a later edge read from that cursor can never be proved. It holds forever and pins that stream's cursor. Choose one of these, and test whichever you pick:
   - (a) the cursor never advances past an original whose later edges could still arrive; or
   - (b) such an edge holds, with a named limitation, an owning successor and #119 still gated.

4. **Make the schema the same on both paths.** Use one shared DDL constant for both fresh v2 creation and the v1→v2 migration. The migration may only `CREATE TABLE`; it must never `ALTER` a v1 table, so reword "Alter the same pinned database". Keep separate exact v1 and v2 `_supported_schema` values. Add a test that a migrated store's `_schema_objects` equal a fresh v2 store's. State whether `foreign_keys` is actually enforced. If it isn't, treat the FKs as declarative and enforce ordering in code.

5. **Say what happens if the code is reverted.** State that v1 code refuses a v2 store and fails closed, that there is no downgrade path, and that implicit upgrade-on-open is acceptable only because the journal is dormant and no production or runtime stores exist. Add a test that v1 validation refuses v2.

6. **Make the cap enforceable.** At 2.25 hours, Task 1 must be GREEN and committed, and the RED tests for core succession and restart (`test_causal_revision_survives_stale_replay_after_restart`) must exist. If not, hold. Name the split line in advance: for example, historical-head `as_of` plus multiple edges in one batch, as a new leaf that directly blocks #119. Clarify that the "new persisted type" trigger excludes the planned revision payload.

7. **Pin the view contract.** Specify `PendingClaim.sequence` for a revised key. I recommend the sequence of the revision that is visible. Also specify the resulting `as_of` ordering. Decide now whether a revision identity field is exposed; drop the "if". Downstream gates depend on this.

## Not blocking: check before Develop

The packet shows only `state: closed` for #199. Read back Completed and Project Done for #199, along with the Ruff, whitespace and raw coverage floor evidence, before the Start Date is set.
