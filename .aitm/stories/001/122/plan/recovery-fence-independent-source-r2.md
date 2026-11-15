[11:26:07]
SOURCE_122: PASS

Both H1 and H2 are cleared against candidate PR #321: head `476af6ff`, tree `d551e285`, base `e9b92172`. The verdict rests on supplied text only, because I recomputed no hashes, blobs, signatures or runs. The evidence I could not inspect is listed below.

## H1: journal-store containment is cleared

**Store path, read from the base source**
- `_monitor_journal_store._STORE = "routing-journal-v1"`.
- The store's `__init__` pins `writer.root` and then `root.path / _STORE`, so the store is `writer.root / _STORE` by construction.
- Using this constant is a read-only import, so no non-target edit and no Refine trigger.

**Runtime guard in `_session`**
- `_check_store(rollback, journal_store)` runs before the yield and again after it.
- It reuses the journal's own physical checks:

| Check | What it proves |
|---|---|
| `lease.identities[:-1] == rollback.identities` | The lease is a direct physical child of the pinned rollback root |
| Key read through `rollback.fd` with `O_NOFOLLOW`, the same `_file_identity` and a SHA-256 key-id match | The key is the same file and lives in that root |
| `_StoreIdentity.check(journal_store)` | The store directory is the one the journal captured |

- Witness overlap is now checked against the pinned `rollback.path`.
- That root contains the store, key and lease, so both overlap directions hold through the symmetric `_overlaps`.

**Test**
- `test_journal_store_key_and_lease_share_the_derived_rollback_root` asserts `_overlaps` for all three paths.
- It also checks direct-child `samestat` through `rollback.fd` with `follow_symlinks=False`. This is the substantive physical proof. The `key.parent` overlap check alone is trivial.

## H2: base provenance is cleared on the recorded evidence

**Base blobs**
- Six base blobs are recorded as identical between `e9b92172` and `ab9db800`. They are `ledger.py`, `monitor_journal.py`, `monitor_registry.py`, `scopes.py`, `types.py` and the store module.
- The six signed control blobs also match.

**Helper excerpts I asked for, now supplied**

| Helper | What the excerpt shows |
|---|---|
| `_publication` | It `flock`s the pinned directory fd itself, so it creates no entry in the witness directory |
| `_read_private` | It opens with `O_NOFOLLOW\|O_NONBLOCK` through `dir_fd`, runs the `_private` and ACL checks, caps the read at `MAX_COMMAND_BYTES + 1`, and runs `samestat` |
| `_encode` | It uses `sort_keys` and compact separators |
| `_decode` | It refuses duplicate fields and maps `TypeError`/`ValueError`/`RecursionError` to `ValueError` |
| `_records` | It enforces byte-exact re-encoding, so the round trip is canonical |
| `_store.evidence` | It returns the cached `_evidence` and never calls `source_evidence()` |

`_read_evidence` refuses a missing key before it calls `source_evidence()`.

## Effect on R1/JIT contracts: none are regressed

1. **Condition 1 (key side-effect).** The keyless gate still runs before any store access, and `_check_authority` only reads, so the keyless test still holds.
2. **Conditions 5 and 6 (rollback roots).** These are strengthened, because the root is now pinned and checked against the journal's captured identities.
3. **Durability, chain, same-sequence set and receiver contracts.** The patch does not touch them.
4. **Post-append custody failure.** If the post-yield check fails after a durable append, the call is held. This is the same semantics as the existing `lease.check()`:
   - `protect` recovers by exact replay.
   - An `_OpenedAttempt` stays pending with `can_send=False`, which costs liveness but not safety.
5. **Scope.** Only the two target files changed. All clauses, ownership, triggers and delivery gates remain as written.

## Non-blocking (carried forward, plus new items)

1. **The test's negative half does not isolate the new guard.** `self._journal._store.evidence` runs before the new pins, so a symlinked store is probably refused by the existing journal guard. The containment assertions are what clear H1, and no red-before-green run of the new test was supplied.
2. **Lock order.** `_publication(directory)` takes the `flock` before the overlap checks.
   - If a caller passed a witness root whose lock it already holds through another fd, the call would block instead of holding. This was already true before the patch.
   - Moving the overlap checks ahead of the lock is a cheap hardening.
3. **`KeyError` may escape `_decode`.** `_decode` does not catch `KeyError`, and `_wire`'s field-set check is not shown. A malformed envelope may still escape `protect`/`recover` as a non-`LedgerError`. It still fails closed, because nothing is appended.
4. **Witness is not checked against the store directly.** The witness is checked against `rollback.path` only, not also against `journal_store.path`. This is sound while the store is a physical child of the rollback root.
5. **Earlier items 1–3, 5 and 6 remain open.** These are the per-instance recovery hold, the remaining test gaps, the unpersisted held disposition, the read cost, and the elapsed-time and red-log evidence.

## Missing evidence (text-only, no tools)

- I did not recompute any digest: blob IDs, the diff, log or coverage SHA-256 values, `archive_digest`, `subject_digest`, or the hosted run and its signature.
- No `git ls-tree d551e285` was supplied to bind blobs `38ab2a57` and `c0def86f` to the signed tree. Only the internal consistency of the diff index lines was checked.
- These excerpts are elided or absent:
  - how the store's `__init__` assigns `_evidence` when the store already exists
  - `_StoreIdentity.check`
  - `_PinnedPath.identities`
  - `_private`
  - `_wire` key validation
  - the value of `MAX_COMMAND_BYTES`
- There is no updated elapsed-time or budget figure for this recovery cycle. The delivery owner must confirm the projected total is at or below 4.0h, or the Refine trigger applies.

## Remaining gates (unchanged)

- verified delivery
- native Close
- receipt and report ownership in the planning and Project readback
