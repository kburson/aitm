# #202 independent JIT review, round 2

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup. November 10, 2026 (America/Chicago).

# PASS: #202 M08b3 revised JIT and private schema

**Digest:** `1b790d66144dc7ca0445efd378ae72b1f1af1e8f400610934efc075b4b31aecb`

I used only the packet: no tools, edits or traffic. I could not hash the bytes myself, so this verdict covers the plan text as presented under that digest.

## Round-one corrections

| # | Correction | Result |
|---|---|---|
| 1 | Fixture order | **Fixed.** r3A is appended to live without staging. r3B is presented first and must be HELD with no row. r3A is then staged as PENDING, and the identical r3B is retried and must be DISPUTED. Because the same r3B flips from HELD to DISPUTED, the first HELD is shown to come only from the missing accepted child. |
| 2 | Compare against every accepted state | **Fixed.** The contender's typed usage is checked against the first claim, the common predecessor, the accepted child and every later descendant, inside the transaction. A difference only in revision number stays HELD. Controls (a), (b) and (c) are all present. |
| 2a | Unchanged common usage | **Correct.** The native case is allowed to produce no edge, so the result must be no row. The guard is tested separately against the real durable common payload. Every positive path uses real native producer proofs. |
| 3 | Archive negatives and prefix | **Fixed.** An exact archive of r3A returns REPLAY with no row. A stale r1/r2 archive writes no row. `prefix_ref` must be equal across the two physical locators. If it isn't, the work holds at the checkpoint for a new JIT. |
| 4 | Independent carrier | **Fixed.** The contender needs a different approved source ID from both the first claim and the accepted child. It also needs a distinct incarnation, keyed from device, inode and birthtime. A locator-only change is refused, and an in-place rewrite on the original source stays HELD. |
| 5 | Precedence and return value | **Fixed.** The content check runs after the different-project branch and before the known-material REPLAY lookup. A key with an ownership dispute holds the same-owner contender. A different-project contender on a content-disputed key still gets its own ownership row. The return value is `ClaimDisposition(DISPUTED, key, owner, dispute_sequence)`. REDs prove precedence in both directions. |
| — | Whole replay edge | **Correct.** The predecessor proof is re-issued from the same batch and must match the durable common v2 row on predecessor ref, material, ordinal and prefix. A v1 genesis-only predecessor stays HELD. |
| 6 | Payload | **Fixed.** `_ContentDisputePayload` and `_ContentEdge` are closed and fully typed. On read, the common and child rows must have sequence ≤ the dispute sequence, and the child's predecessor must equal the stored common ref. |
| 7 | One dispute per key for the store's life | **Fixed.** It is append-only with no resolution path. #203 needs its own schema review for disposition storage and for any dispute recorded after a disposition. |
| 8 | Task 1 files and old-reader proof | **Fixed.** Task 1 commits only the store file and its test. The PRAGMA-2 rollback test is named exactly and keeps its parameter IDs. Old v1 and v2 readers come from the frozen trunk SHAs, run in subprocesses against copies of the store, with a byte check. |
| — | Migration | **Sound.** The v1 path is one `BEGIN IMMEDIATE`: it checks the intermediate schema against the exact v2 tuple and sets `user_version=3` once. The v2 path appends only the v3 table. The shared CREATE gives identical fresh and upgraded schemas. Rollback injection covers both old versions. |
| 9 | #204 gate | **Fixed.** #204 is read back as a direct #119 blocker before Develop and again before Close. Live readback shows #202, #203 and #204 open. |
| — | Downstream gates | **Retained.** #202 gates #119 and #203. #119 is not released while #203 or #204 is open. |

Budget is 1.10 + 2.80 = 3.90 hours, under the 4-hour cap. The 2.25-hour checkpoint and the predeclared split are concrete.

## Notes for execution

These don't change the plan. They are how I read it, and Develop should test against them:

1. **Old-reader refusals must have the right cause.** Each subprocess should be shown to refuse at the journal schema-version gate, not at an earlier registry or ledger incompatibility. If an old reader changes the `-shm` bytes, treat that as a finding and hold. Don't loosen the byte criterion.
2. **Check every outcome in a re-read.** After a dispute, a live or archive re-read should give:
   - genesis and the common predecessor: HELD
   - both dispute members: DISPUTED
   - r4A: HELD
   
   When a key has both dispute types, an exact replay of the first material stays ownership-DISPUTED.
3. **Dispute creation comes after the REPLAY lookup.** Only the check for an existing content row comes before it. The exact-archive r3A REPLAY test pins this order.
4. **Extra read-time checks:**
   - `accepted.origin` equals the first claim's evidence.
   - The accepted edge's locator, incarnation and prefix equal the durable child row.
   - The contender's source ID differs from the first claim's.
5. **"Active" means "recorded"** in this schema. It does not imply a lifecycle.
6. **The budget margin is 0.10 hours.** Any growth goes to the checkpoint split, not into stretching the cap.
