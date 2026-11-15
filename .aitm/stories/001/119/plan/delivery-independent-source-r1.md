[09:33:56]
SOURCE_119: HOLD. The product code matches the JIT and B1–B9. The hold is for missing JIT-required negative and compatibility tests, so source code can stay as it is unless the new tests find a problem.

I reviewed only the diff and helper excerpts you supplied. This session had no shell or file access, so I could not grep the head tree or rerun the tests. Where I say coverage is missing, it means the supplied diff doesn't show it. If an existing parametrized test already covers the case, point to it instead of adding one.

## Blockers (tests only)

1. **Ledger version and layout refusal.** The JIT says future version, layout mismatch and stale expected head must refuse and preserve the current bytes.
   - Only the stale head is tested: `ConflictError` from `upgrade_delivery_schema(previous.sequence + 1)`.
   - Add a v3 ledger with `user_version = 4`.
   - Add a v3 `user_version` without `monitor_delivery_receipts`.
   - Add a v2 database carrying an extra or altered receipt table.
   - Each case must refuse, and each must show the database file is byte-identical before and after.
   - The journal side already covers v7-without-table and v8.

2. **Write interruption, and owner or key substitution.** The JIT says tests cover all three. None appear.
   - **Interruption:** force a failure after the `commits` insert inside `_commit_monitor_delivery`, for example by patching `pseudonymize` or the receipt insert. Then assert no `commits` row, no `monitor_revisions` row, no receipt row and an unchanged head.
   - **Owner:** `ProjectDelivery.attach(journal, writer_B).commit(ticket_A)` must refuse. The path is the `_monitor_revision` project check.
   - **Ledger key:** replace the key file under a held writer. Then `commit`, `_readback` and `ack` must refuse through `_require_delivery_writer` and `_write_transaction`.
   - **Destination key pin:** after an ACK under key K1, `ack` or `attach` under K2 must refuse in `_require_destination_in`. This is the "wrong-key" negative and currently no test reaches it.

3. **B7 refusals not exercised.**
   - A content dispute before ACK must make `reserve_delivery`, `commit` and a new `ack` refuse. The late-conflict test only produces an ownership dispute.
   - A new ACK must still succeed for the original owner after an ownership dispute. Only the historical replay is tested.
   - A tampered `monitor_revisions.payload` must refuse. Only the receipt `seal` is tampered.

4. **B2 v3 compatibility in backup and install.** `backup.py` and `install.py` changed, but no test in the diff covers them. Add:
   - A backup restore of a v3 ledger with delivery rows that passes.
   - The same restore with a tampered receipt, which must be rejected by `_validate_delivery_receipts`.
   - `_probe_runtime` on a v3 project: reject a wheel that only offers `[legacy, monitor]`, and accept the full three-version list.
   - The same probe on v1 and v2 projects: both lists must still be accepted.

5. **Weak assertions in two of the four accepted tests.**
   - B8 says to verify both scoped histories after settlement. `test_full_destination_queue_preserves_independent_progress` checks A's ledger rows and the journal's project set, but never B's destination ledger history. Add that check.
   - `test_late_conflict…` only checks `publication_candidate(change).basis == "ownership"`. The JIT asks for the exact journal-only candidate through #310, so compare the full candidate.

## Verified against the JIT (no change needed)

- **Storage:** both tables, their STRICT columns, primary keys and foreign keys match. The journal adds `delivery_claim_project`, which B4 allows.
- **Explicit upgrades:**
  - The ledger upgrade only goes from v2, returns the identity if already v3, checks the expected head, runs the foreign-key check before and validates the catalog after.
  - The journal upgrade only goes from v6, accepts an existing v7, and checks the tip and coordinator lease in one transaction.
  - New stores are still created at the old versions, and nothing upgrades automatically.
- **Recognized versions:**
  - A journal at `user_version = 7` without the table is refused, and `user_version = 8` is refused as unsupported.
  - Coverage, dispute and `_enable_coverage` checks treat v7 like v6.
  - On the ledger, `monitor_as_of` and `upgrade_monitor_schema` behave the same on v3 as on v2.
- **Custody and ordering (B1):**
  - `commit` checks the ticket in a journal read transaction before the ledger write transaction.
  - `ack` rereads the receipt and row from the ledger before `BEGIN IMMEDIATE`.
  - Inside the journal transaction, only file pin checks, the key file read and the registry view happen. There is no ledger SQL and no writer acquisition.
  - The coordinator lease is asserted on every check.
- **Append-only seals and retry:**
  - The receipt seal covers the full encoded bytes. Readback checks the commit, row and receipt join, both keys, the payload digest and the identity.
  - An exact retry returns the stored receipt without moving the head.
  - These are rejected: a receipt-less row, a different payload for the same key and revision, and a newer revision already in the ledger.
  - The ACK is sealed with the journal service key. A historical replay is checked before the current claim. A changed receipt is refused.
  - All new-ACK refusals become `_DeliveryRefused`.
- **Capacity:**
  - Only the latest revision of each key counts. Content-disputed keys are skipped, and an ACK must match both the revision and the claim sequence.
  - Replacing an unresolved revision is always allowed, while a successor after an ACK needs room.
  - The check runs only right before a new claim or successor is written, and v4–v6 journals bypass it.
  - The HELD result keeps the shared stream's cursor in place while the other project's claims are still recorded. An independent stream keeps advancing.
- **Tail:** the high-water mark never moves backwards (tested by ACKing two claims out of order).
- **Qualified-source policy:** no qualification code changed. The fixture's default path is unchanged when `independent_copy=False`.

## Non-blocking notes

- `_commit_monitor_delivery` runs `PRAGMA foreign_key_check` over the whole database on every delivered row, which scales with total ledger size. Scoping it to `foreign_key_check(monitor_delivery_receipts)` and `(monitor_revisions)` would still satisfy B6.
- `_delivery_capacity` walks every claim of the project for each new claim, including an HMAC check on each ACK. That follows the JIT's shape, but it becomes a scaling cost once v7 is enabled.
- Some refusals surface as the wrong error type:
  - `_monitor_revision` only converts `ValueError`, so a `TypeError` or `AttributeError` escapes `commit` unwrapped.
  - In `_delivery_claim`, a `ValueError` from `UUID(project)` escapes `reserve_delivery` unwrapped.
  - `enable_delivery` raises `ConflictError` for a non-int tip, where the ledger's upgrade raises `ValueError`.
- The journal's `_supported_schema` uses `== 7` rather than `>= 7`. That is correct while 7 is the highest version, but it isn't cumulative as B2 describes.
- `_DeliveryAck` stores only the claim key, not the full PendingClaim. The receipt's claim digest (SHA-256 of the canonical claim) still binds the ACK to the exact claim, so this works as an equivalent.
