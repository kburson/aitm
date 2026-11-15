[07:28:08]
JIT_119: PASS, with nine conditions (B1–B9 below) that must be met before or during the first red tests.

**Limits of this check:** I had no repository or shell tools in this session, so I checked the plan only against the excerpts, the Refine and its verdict in your request. I did not read baseline `2b3225e`. This worktree is checked out on `codex/aitm-300-journal-coverage`, not the baseline, so the plan's baseline blob check still has to run on a checkout of `2b3225e`. I changed nothing.

### Gate checks
- **Scope:** matches the narrowed Refine.
  - #310 keeps journal-only candidates. #122 keeps the publication witness. #120 and #121 keep scheduling. #126 keeps legacy bridging.
  - Epic #2, C01, #204, production cutover and the release gates are untouched.
  - There is no scheduler, public command or cleanup.
- **Storage:** exactly two additive tables: `monitor_delivery_receipts` in ledger v3 and `delivery_acks` in journal v7.
  - `reserve_delivery` is a read with no durable row, so there is no third reservation store.
- **Estimate:** 1.20 + 0.85 = 2.05 for receipt plus ACK; 0.65 + 0.90 for the rest; total 3.60.
  - The JIT adds custody details but no new storage, so exceeding 2.05 hours is not plausible. The #310 version-gate widening fits the 0.90 compatibility bucket.
- **Locks and custody:**
  - The plan forbids taking the project lock inside a journal SQL transaction.
  - It reuses the existing `_write_transaction` path re-check, HMAC key compare and `BEGIN IMMEDIATE` identity validation.
  - It compares identity on every commit and readback.
  - It pins the destination key through the existing v7 ACKs.
  - Restart gets a fresh writer for the same project root and key.
- **Opt-in versions:**
  - Upgrades are explicit, need the expected head or tip, and accept no other source version: the ledger upgrade needs exactly v2 and the journal upgrade needs exactly v6.
  - The new version is added to the recognized set, not opened up to a numeric range.
  - Setting `user_version` alone, or a substituted table, still refuses.
  - The plan matches the gates in the excerpts: `monitor_as_of` uses `==`, `_supported_schema` and `_validate_identity` stop at v6, and `upgrade_monitor_schema` returns early only on `==` v2.
- **Receipt/ACK join:**
  - Ledger receipts are append-only, keyed (key, revision), with a foreign key to `monitor_revisions`, and sealed with the project key.
  - ACKs are sealed with the journal service key.
  - An exact replay returns the stored proof without moving the head.
  - Interrupting the ledger transaction rolls back.
- **Late revisions and disputes:**
  - A superseded claim or a content dispute before ACK refuses the new ACK.
  - A prior ACK replays its historical result.
  - There is no compensating write, and late content conflicts go to #310.
- **Watermark:** derived as MAX(`claim_sequence`) per (project, destination key). It needs no stored state and cannot rewind because ACKs are append-only.
- **Pending cap and other progress:**
  - The cap applies only on v7. It is checked only before a new claim or successor write, after known replay and disputes are checked.
  - A full destination returns the existing `ClaimStatus.HELD`.
  - The excerpt confirms `_complete` already holds the cursor when any outcome is `HELD`, so other streams keep moving through `reserve_batch`.

### Refine carry-forwards
| # | Item | Status |
|---|---|---|
| 1 | Watermark keyed per destination | Met: per (project, destination key), MAX `claim_sequence` |
| 2 | "Reserve" is transient | Met: no insert, commit or cursor change |
| 3 | Conflict between commit and ACK | Met: ACK refused, history replays, superseded claim leaves the count. Condition B7 fixes the result type |
| 4 | Two-project settlement assertion | Met: it is in the full-queue test. Condition B8 tightens it |
| 5 | Upgrades stay explicit | Met: no automatic upgrades; v2 and v4–v6 stay at their versions |
| 6 | How the receipt is authenticated | Met: project-key MAC, ledger read before the journal `BEGIN IMMEDIATE`, append-only. Condition B1 removes a conflicting phrase |
| 7 | Named ledger seam | Met: `_commit_monitor_delivery` and `_monitor_delivery_receipt` exist, so `monitor_writer.py` never calls `_write_transaction` directly |

### Conditions to meet before or during the first red tests
- **B1 – No ledger read inside the ACK transaction.** The plan reads the receipt before the journal `BEGIN IMMEDIATE`, but later says "before the project read" inside it, which contradicts that.
  - Inside the journal transaction, compare only against the receipt read earlier, plus re-checking the pins.
  - Order the locks as coordinator first, then project writer, and never the reverse.
- **B2 – Find every hard-coded v6 check.** Before editing, grep for every `== / != / >= _COVERAGE_SCHEMA_VERSION` comparison and every schema-creation path, and decide each one so a v7 store is never upgraded again or refused.
  - Do the same for ledger `_supported_schema`: it uses `==` MONITOR and must add tables cumulatively up to v3.
  - Test that registry `_register`/`Ledger.open` and the legacy `as_of` read work on v3.
- **B3 – Revision numbers must be unique.** Confirm on the baseline that the journal revision number is unique and strictly increasing per non-disputed claim key. Same key and revision with a different digest must already be a content dispute.
  - Also confirm the ledger accepts a skipped revision. For example, revision 2 is delivered after revision 1 was superseded before delivery.
  - If either is false, the ACK and receipt primary keys need `claim_sequence`, and that is a re-split check.
- **B4 – Which claims count toward the cap.** Bind that claims committed before `enable_delivery` count as obligations, and test it.
  - The cap must fail closed: an ACK with a missing or invalid seal counts as unresolved or refuses. It never lowers the count.
  - Adding an index on `claims(project)` in v7 is allowed. It is an index, not a store.
- **B5 – Use a real MAC for the receipt seal.** Confirm `pseudonymize` gives a full keyed HMAC over the whole canonical receipt with domain separation and no length or charset limits. If not, use a private HMAC helper with the same key.
- **B6 – Ledger foreign keys.** The ledger excerpt has no `_validate_foreign_keys`. Either turn on and check `foreign_key_check` around the v3 upgrade and the delivery commit, or rely on the authenticated join read and say so explicitly.
- **B7 – Disputed claims can't be delivered.** `reserve_delivery` and `commit` refuse content-disputed claims. Every refusal of a new ACK raises one named error type deterministically.
  - An ownership dispute keeps the original owner's claim deliverable and counted.
- **B8 – Test details.** The restart test must cover three separate points:
  - after `reserve_delivery`, before the commit;
  - after the commit, before the ACK;
  - after the ACK, replayed.

  The full-queue test must assert two things:
  - the shared stream's cursor stays held while the second project's claims in that stream are still recorded;
  - an independent stream advances.
- **B9 – Re-split check.** Re-run the 2.05-hour check after B3. Any new durable reservation table or extra primary-key restructuring sends this back to independent split acceptance.

Nothing in this review changes the existing delivery gates, so signed hosted Test, independent source, verified delivery and native Close are still required separately.
