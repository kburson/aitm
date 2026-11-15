[07:21:01]
**REFINE_119_NARROW: PASS.** The narrowed #119 scope is consistent with the accepted M09a split, the native graph readback, the cited storage and lease seams and the 3.6-hour estimate. It acknowledges known-version compatibility without widening scope. The items under "Carry forward to JIT" have to be settled at JIT.

**How I checked this:** this session had no repository or shell tools. I checked the plan only against the excerpts, graph, board and PR/Close records in your request, not against trunk `2b3225e`. Nothing was changed: no production code, lifecycle gate, board or graph edit.

### What checks out
- **#310 Close:** #310 is `CLOSED/COMPLETED` at 13:19:14Z, after PR #311 merged at 13:19:04Z. The merge commit `2b3225e` is the stated literal trunk, and the merge passed ordered-parents and zero-diff checks. The board shows #310 as Done at 229.9 with size S, estimate 1.25.
  - Your records don't show the native-Close SHA `54d937da`. The Close itself is confirmed, so this doesn't block.
- **Graph:** all of #119's prerequisites are closed, including #300 and #310. #120, #122 and #296 are open dependents. #119 is in Refine at rank 230, size M, estimate 3.6, as the accepted amendment requires.
- **Estimate:** 1.20 + 0.85 + 0.65 + 0.90 = 3.60. The re-split trigger is 1.20 + 0.85 = 2.05 hours for receipt plus ACK storage, which matches the amendment's re-estimate rule.
- **Ownership:** each piece stays with its owner:
  - #310: journal-only candidates.
  - #122: publication witness and external publication.
  - #120 and #121: scheduling and process lifetime.
  - #126: legacy identity bridging.
  - #204, Epic #2, C01 and cutover: unchanged.
  - Excluded from this slice: scheduler, background jobs, report, public command, cleanup and live rollout.
- **Storage and lease seams:**
  - `Ledger.writer` already provides the project guard, the writer lease and pinned root/store directories.
  - `_write_transaction` already rechecks the paths, compares the key with HMAC and validates identity inside `BEGIN IMMEDIATE`.
  - The journal `transaction()` checks the version on entry and exit.
  - `monitor_revisions` has no destination receipt and journal v6 has no ACK table, so the plan really does need new additive storage.
  - Ordering two separate commits through copied-proof readback, rather than pretending they share one transaction, is correct.
- **Authority:** pseudonyms give no journal grant, and claims, observations or labels passed in from Python carry no ACK authority. The ACK is authenticated against the installed registered project and the current canonical claim and revision. The forged-pseudonym negative control is assigned.
- **Compatibility:** the plan correctly names the places a new version would break today:
  - `monitor_as_of` accepts only `== MONITOR_SCHEMA_VERSION`.
  - `publication_candidate` coverage requires `== _COVERAGE_SCHEMA_VERSION`.
  - The `_validate_identity` version set and `_supported_schema` stop at v6.
  - `_dispute_changes_in` accepts only v3 to v6.
  - `upgrade_monitor_schema` returns early only on `== v2`.
  - After an upgrade the stored identity changes, so the writer must reopen or rebind.

  Deriving the unsupported-version test from the actual version set, and refusing a known version number with a missing or substituted table, is the right shape. Widening #310's version gates so v7 stores keep the same coverage and dispute meaning is compatibility, not new rights.
- **Assigned behaviors:** each test the amendment assigns has a matching item in the Refine:
  - `restart_at_reserve_commit_and_ack`
  - `stale_ack_never_rewinds`
  - `full_destination_queue_preserves_independent_progress`
  - `late_conflict_after_ack…without_new_write`
  - the pseudonym negative control
  - old/unsupported schema guards

### Carry forward to JIT (none blocks this Refine)
1. **Watermark keying:** say what the acceptance watermark is keyed by. To keep both stale-ACK monotonicity and independent destination progress while a shared stream is blocked, it has to be per destination at least, or per destination and claim revision. A single journal-wide contiguous tail would contradict the independent-progress test.
2. **What "reserve" means:** the storage budget contains only a receipt and an ACK. So "reserve" must be an in-transaction read of the expected revision with no durable row, and a restart after reserve is the same as a restart before the destination commit. If JIT finds that a durable reservation is needed, that is new storage and falls under the 2.05-hour re-split rule.
3. **Conflict between destination commit and ACK:** pin the result when the canonical claim or revision changes inside that window. It should be a deterministic rejected or historical ACK with no new destination write. The superseded obligation should leave capacity accounting, and the dispute should stay with #310 and #122.
4. **Two-project settlement check:** add the amendment's "settlement after recovery preserves two distinct project scopes" assertion to `test_full_destination_queue_preserves_independent_progress`. The Refine verification list doesn't carry it explicitly.
5. **Upgrades stay explicit:** the v2→v3 ledger and v6→v7 journal upgrades must stay explicitly selected, like the existing `upgrade_monitor_schema`, with no implicit upgrade inside `attach`, `ack` or the readers. Ledgers left at v2 and journals at v6 must keep their catalog and on-disk values byte-for-byte.
6. **Receipt authentication:** bind how the journal verifies a ledger receipt: which key MACs it, and that the ledger snapshot is read before the journal `BEGIN IMMEDIATE`. The receipt must be append-only so that reading the ledger first and the journal second leaves no race.
7. **`Ledger._write_transaction` from `monitor_writer.py`:** prefer the "minimal support in `ledger.py`" seam over calling the private method directly from another module, and name it at JIT.

The Refine allows JIT to start now. Make sure the JIT binding records items 1–7.
