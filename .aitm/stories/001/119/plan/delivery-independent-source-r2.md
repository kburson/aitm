[09:59:49]
SOURCE_119: PASS. The recovery adds only tests, and it closes all five R1 blockers without changing the product R1 accepted against the JIT and B1–B9.

I could only read the supplied diff, helper excerpts and evidence. This session had no shell or file tools, so I didn't grep the head tree or rerun anything. The test results come from the signed evidence: 1312 tests passed locally and in hosted run 43731237387 on tree `1344a37`, which matches both the verified and reviewed tree. Product coverage is 12126/13213 in both.

## R1 blockers

| # | R1 blocker | Recovery evidence | Status |
|---|---|---|---|
| 1 | Version and layout refusal, with bytes preserved | The new catalog-refusal test covers four cases: v3 set to version 4, v3 with the receipt table dropped, v2 with a malformed receipt table, and a stale expected head. Each one refuses, and the durable bytes are identical before and after. | Closed |
| 2a | Write interruption | An SQLite authorizer blocks the receipt insert after the `commits` and `monitor_revisions` inserts. The insert order is asserted, the head and rows are unchanged, and the receipt reads back as `None`. A retry then commits at head+1, which also shows no orphan row was left. | Closed |
| 2b | Foreign owner | Writer B committing ticket A raises `_DeliveryRefused("belongs to another project")`, and B gains no rows. | Closed |
| 2c | Ledger key replaced under a held writer | `commit` and `_readback` raise "identity changed", and `ack` raises `_DeliveryRefused`. After the key is restored, the same inputs ACK successfully, so the refusal comes from the key change. | Closed |
| 2d | Destination key pin | After an ACK under K1, a ledger rebuilt with K2 and a matching `key_id` is refused at `attach` with "Destination ledger key changed". The tail and journal tip don't move. | Closed |
| 3a | Content dispute before ACK | `reserve_delivery`, `commit` and a new `ack` all refuse. The destination receipt stays intact (no compensating write) and the journal tip stays at the dispute. | Closed |
| 3b | New ACK for the first owner after an ownership dispute | The `ack_before_dispute=False` case makes a fresh ACK at `prior + 1`. It then replays identically, and an altered digest is refused. | Closed |
| 3c | Tampered `monitor_revisions.payload` | `ack` raises `_DeliveryRefused` and the journal tip is unchanged. | Closed |
| 4 | v3 backup, restore and installer | Restore brings back the saved v3 point, with the receipt matching exactly. A forged seal fails inside `_validate_delivery_receipts`: it runs exactly once, on the staged root, with the expected reason, and the live store's bytes don't change. The installer probe on a v3 project rejects a wheel offering only v1 and v2 ("schema is incompatible") and accepts one offering all three. v1 and v2 projects pass with both lists. | Closed |
| 5a | B's destination history | Both projects' histories are now compared as exact sets after settlement. | Closed |
| 5b | Exact #310 candidate | The full `PublicationCandidate` is checked against a separately rebuilt `monitor-journal-publication-v1` pseudonym. | Closed |

## The other checks you asked for

- **Rollback:** the ledger rolls back on an interrupted write (2a). Every refused ACK leaves the journal tip where it was.
- **Historical versus new ACK:** both are covered by the parametrized late-conflict test.
- **First-owner custody:** 3b.
- **Exact candidate readback:** 5b.
- **Both destination histories:** 5a.
- **v3 compatibility:** schema (1), restore and installer (4).
- **Scope and gates:** the recovery changes only `test_monitor_delivery.py` and `test_monitor_ledger_version.py`. The policy, gate, verifier, observer and lock blobs are unchanged. The only workflow change is the inherited schedule and fixture-location change from maintenance PR #319, which is documented.

## Non-blocking notes

- **Unpinned error messages:** several negative tests don't use `match=`, so they show that a refusal happens but not which check made it:
  - the four catalog-refusal cases;
  - the three content-dispute refusals;
  - the tampered-payload ACK;
  - the ACK under the replaced key.

  The cause is still clear in each case: either a passing control differs only by the fault, or the refused call succeeds on the same inputs elsewhere. Adding `match=` would make that explicit.
- **One untested path:** no test replays a historical ACK after a *content* dispute; it is only tested after an ownership dispute. R1 confirmed the product checks for an existing ACK before the current claim, so the path doesn't depend on the dispute type.
- **Set comparison:** the history checks compare sets rather than counts. That's safe because the primary key on `(key, revision)` rules out duplicate rows.
- R1's other non-blocking notes still stand: the database-wide foreign-key check, the cost of the capacity scan, the unwrapped `TypeError`/`ValueError` paths, and the journal's `== 7` version check.
