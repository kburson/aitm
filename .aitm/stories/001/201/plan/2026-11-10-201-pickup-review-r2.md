# #201 independent JIT review, round 2

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup. November 10, 2026 (America/Chicago).

# Independent re-review of #201 M08b2 JIT (round two)

**Verdict: PASS** on `302b2220f9f887e7ea55526ee043d667682b3df65f84eb357735ff8a74d3a67f`

This verdict covers only #201 and the plan bytes shown in this packet. I used no tools, so I couldn't recompute the SHA-256. The verdict applies to the bytes as they appear here under that digest. It doesn't authorize Develop by itself: the checks listed at the end still apply.

## Round-one corrections

1. **Replay must match the whole edge: closed.** Every v2 replay, current or older, now gets the fresh edge issued by the writer. It then compares four fields:
   - successor material
   - predecessor material
   - the actual later ordinal
   - the prefix ref

   All four must match, both for the same locator and for an exact archive. If the successor material matches but the predecessor, ordinal or prefix differs, the edge is held for #202. "Same successor material with changed predecessor" is now a named RED test. A changed ordinal on its own needs no separate test, because `prefix_ref` keys the row ordinal into its own namespace, so any ordinal change also changes the prefix.

2. **What `prefix_ref` covers: closed.** The plan now defines it as a keyed fingerprint of every raw byte from the start of the file through the committing row, including that row's terminator, together with the stream and ordinal. It is not a hash of the row alone.
   - Two rewrite tests are pinned: one between the epoch prefix and the original row, and one between the original row and the durable head. Both leave the normalized material unchanged.
   - A named fixture shows the v1-layout genesis limitation, and the plan requires it to be recorded in the PR and the retrospective.
   - These tests would fail if the delivered prefix only hashed one row, so they also confirm the definition.

3. **A later edge arriving after the cursor has advanced: closed, but only through the test.** The plan picks neither (a) nor (b). It argues the problem can't happen: `read_source` checks the supplied prefix and then reads cold from `None`.
   - Your note says the delivered source showing that `None` call is in the packet. It isn't: the body of `read_source` doesn't appear anywhere above.
   - So I'm not relying on that claim. I accept the correction because of the required journal-level fixture: a real earlier issued ScopeState cursor, then a later successor, then proof that the original and the predecessor are both seen, with genuine quota still pinning the cursor.
   - The packet does support the claim indirectly. `verified_revision` needs both the original and the predecessor in `batch._proofs`, and the journal's existing REPLAY path re-reads rows that were already claimed.
   - If that fixture can't pass without changing ScopeState, the work falls outside the four files #201 may write, and #201 must hold. That doesn't count as a reason to choose (a) or (b) during Develop.

4. **Same schema on both paths: closed.**
   - One shared `CREATE TABLE` constant is used for both fresh v2 creation and the migration, with no ALTER.
   - The v1 and v2 schema tuples stay separate, and a test checks that a migrated store's schema equals a fresh v2 store's.
   - Foreign keys are stated to be enforced on the write connection, and a test checks that. Parent `commits` rows are inserted before children, which matches the existing `_record_sequence` ordering.
   - The migration runs under `BEGIN IMMEDIATE` with single-statement DDL and no `executescript`, and `user_version=2` commits in the same transaction. It is checked for custody before commit, and a failure before commit followed by a retry is tested.

5. **Reverting the code: closed.** v1 code refuses a v2 store and fails closed, with a test showing neither store is modified. There is no downgrade path. Upgrading on open is limited to this dormant private store.

6. **An enforceable cap: closed.**
   - At the 2.25-hour checkpoint, Task 1 must be GREEN and committed, and the RED tests for core succession and `test_causal_revision_survives_stale_replay_after_restart` must exist. Otherwise #201 holds.
   - The split line is named in advance: multiple edges in one batch and full historical-head projection move to a new #100 leaf.
   - The planned revision payload is excluded from the "new persisted type" trigger.
   - The estimate is 1.10 + 2.65 = 3.75 hours.

7. **The view contract: closed.**
   - `PendingClaim.revision: int = 1` is appended last, so existing construction still works.
   - For a revised key, `sequence` is the sequence of the visible revision.
   - Claims are ordered by the immutable first insertion, `(claims.sequence, key)`.
   - `as_of` returns the latest edge at or before the requested sequence, and the first project, scope, time basis and ClaimEvidence stay unchanged.

## Obligations you asked me to check

- **Unresolved obligations stay replayable.** Quota, aggregate diagnostics, native holds and terminal receipts all keep the earlier cursor even when valid claims stage. Positive progress still only happens when nothing is outstanding.
- **SQLite changes are strictly additive.** There is one new STRICT table and no rewrite of v1 rows. `_STORE` and the application ID are unchanged, and there's no side file. Disputes take precedence and a replay can't clear one.
- **Dependency gates are intact.** #199 reads back CLOSED, COMPLETED and Project Done. #201 directly blocks #119 and #202, and #202–#204 stay direct #119 blockers.

## Before setting Start Date (not blocking)

1. **Remaining baseline evidence.** Read back the Ruff and whitespace results and the raw 10,236/11,175 and 778/821 line counts. The packet only shows the 948 and 182 pass counts, plus a path to the coverage JSON.
2. **Rank for the contingent split.** Ranks 226 (#201) and 227 (#202) leave no whole number between them. If the split is triggered, its own independent split review must settle the rank, either by renumbering or some other ordering, before any native edit.
3. **The `read_source` fixture.** Treat the cold-read fixture from point 3 as a hard gate. If it fails, #201 holds rather than being redesigned within the four files.
