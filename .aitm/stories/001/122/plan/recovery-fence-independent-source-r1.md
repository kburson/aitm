[11:09:41]
SOURCE_122: HOLD

The code meets the JIT on almost every reviewed axis. The hold rests on one binding condition that the diff neither enforces nor proves, and on missing base provenance for the helper excerpts. Neither should require a change to the code's structure.

## Blocking

**H1. Condition 6: journal-store containment is unproven.**
- `RecoveryFence._session` treats `writer.root` as the journal rollback root.
- The excerpts show that the lease (`root / _COORDINATOR_FILE`) and the source key (`_SOURCE_KEY_FILE` under `_pin_directory(self.root)`) are physically inside that root.
- Nothing in the diff, the tests or the excerpts shows that `RoutingJournal._store` is under `writer.root`. Condition 6 makes that containment binding and a Refine trigger.
- **To clear:**
  - Cite the store-path derivation at the exact base.
  - Add a target-file assertion that the store, key and lease all overlap `writer.root` through `_overlaps`.
  - Preferably, also add the same check at runtime in `_session`.
  - If the store path cannot be reached without a non-target edit, return to Refine.

**H2. Base provenance.**
- The JIT and the helper excerpts are at `ab9db800`, but #321's base is `e9b92172`. The control-blob comparison covers only the signed controls.
- Supply either an empty `git diff ab9db800 e9b92172` for `ledger.py`, `scopes.py`, `monitor_journal.py`, `monitor_registry.py` and `types.py`, or fresh excerpts taken at `e9b92172`.
- Also excerpt these helpers, which the diff relies on but which were not supplied:

| Helper | What the excerpt must show |
|---|---|
| `scopes._publication` | Its lock semantics, and that it leaves no entry in the witness directory |
| `scopes._read_private` | It does not follow links and has a size bound, since the "bounded envelope" claim depends on it |
| `_encode`/`_decode` | A canonical round-trip |
| `RoutingJournal._store.evidence` | It never calls `source_evidence()` |

## Verified against the diff and excerpts

**Candidate authority**
- Types are checked exactly, and a `bool` sequence is refused.
- The candidate is reconstructed through `publication_candidate`. Zero or duplicate matches are held.
- Only the reconstructed instance is witnessed and returned.
- `ValueError`/`LedgerError` from either readback is held before any append.
- A keyless registry is held before `_store.evidence` is touched, and a test asserts that no key file is created.

**Same-sequence set binding**
- The set digest is length-prefixed, with a sequence and count header and lexical (basis, identity) order. It is keyed under the new namespace `monitor-recovery-candidates-v1`.
- A digest mismatch at a witnessed sequence is held. An unwitnessed older candidate is held.
- A new member at the high-water sequence appends only when the digests match.
- The #310 two-dispute commit is fenced at ordinals 1 and 2.

**Chain**
- Names must be contiguous. `.publishing-*` names are ignored, and any other name is held.
- Ordinal, predecessor seal, `key_id`, seal and canonical bytes are all checked before any reuse or append.

**Durability**
- `_publish(replace_pending=False)` is used.
- A `False` return leads to an exact readback, a directory fsync and `check()`.
- An exact replay goes through `_confirm_readback`.
- The lease is rechecked after the body on every return path.

**Physical roots**
- The witness root is pinned.
- `_overlaps` is symmetric and reuses the `_physical_ancestry` idiom.
- Equal and nested roots are tested.

**Recovery**
- Witnessed publications are reconfirmed against the journal in chronological order. The last authenticated boundary is returned.
- A missing or mismatched anchor holds.
- The old-witness copy holds at ordinal 1 and refuses `protect`.

**Receiver**
- At most one (key, digest) is admitted per (publication, receiver). A fresh key or changed bytes is refused before attempt 1.
- A pending replay returns `can_send=False`.
- Absence counts only for the latest attempt and is consumed durably by the successor append.
- A late acceptance from any opened attempt is terminal, and absence arriving after acceptance is held.
- There is no default verifier.
- The proof is persisted only as a SHA-256 digest.

**Claude coverage**
- The test uses the delivered fixture path and cites the exact delivered test.
- `Ledger.open`, `Ledger.writer` and `ack` are patched to fail, and `as_of()` is unchanged.
- A directory-fsync fault is followed by a successful retry.

**Scope:** only the two target files are changed.

**Condition 4:** the seals are `pseudonymize` outputs under new namespaces, which is the same pattern as `monitor-journal-publication-v1`. I read this as compliant. One consequence is that seals and set digests also validate as `SourceRef`, so receiver and key references cannot be distinguished from seals by type. This is non-blocking.

## Non-blocking (carry forward)

1. **Recovery hold is per-instance.**
   - A fresh `RecoveryFence` starts unheld, and `recover(None)` always holds, so normal operation cannot use `recover`.
   - `protect` checks only the candidate's own sequence. A journal rolled back below the witnessed high-water and then re-advanced past it would be fenced by a fresh instance.
   - This is within the JIT as written, because the fork rule covers sequences at or below the high-water.
   - #123/#126 must run `recover(anchor)` on every fence instance after any restore. Cheap in-slice hardening would be to reconfirm the high-water set before appending a new sequence.
2. **Test gaps.**
   - A stray `.publishing-*` file (fsynced but not linked) is never exercised. The before-link mock writes nothing.
   - The after-link variant runs the full `_publish`, including the directory fsync. The Claude test is what covers the link-before-directory-fsync window.
   - These cases are missing: a gap in the middle of the chain, a rollback root inside the witness root, and an aliased path.
3. **Held disposition is never persisted.** The JIT says to persist "or held disposition". The functional effect is nil.
4. **Exception types are inconsistent.** A `TypeError` or `KeyError` from decoding or the verifier escapes `_session`/`recover`. No append happens, but the error contract is inconsistent.
5. **Read cost.** Every call reads the whole chain, and `recover` performs O(n²) journal reads.
6. **Evidence.** The checkpoint records `conservative_elapsed_upper_hours: 0.1051`, which the delivery owner should check for plausibility. The red logs are supplied only as hashes.

Clearing H1 and H2 is sufficient for re-review.
