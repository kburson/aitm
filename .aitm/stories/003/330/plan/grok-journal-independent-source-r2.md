[16:26:51]
SOURCE_330: PASS

**Basis: head `bc1a43f9`, tree `9571299`, base `30e1a13d`**

- **Product files are unchanged since R1.** The only change from `0ead2c6e` to `bc1a43f9` is in `tests/test_monitor_grok_delivery.py` (`e455d693..550534eb`).
  - `monitor_journal.py` (`42f74037`) and `monitor_writer.py` (`fd02dfa4`) are the blobs R1 accepted.
  - The three changed paths are the same, with no schema 8 and no outside edit.
- **Tests:** locked local run 1473 passed; focused run 14 passed (9 earlier tests plus 5 new). The signed hosted run 43768376715 passed on the same head and tree, and its control blobs match the prior verified gate.

**Each recovery case checked against the supplied test source:**

1. **Genuine old native snapshot.** `test_retained_legacy_journal_snapshot_restores_for_both_readers`:
   - Real Codex journal rows decode under the frozen legacy shapes (`_LegacyClaim`, `_LegacyPendingClaim`, `StreamCursor`), compared claim by exact key.
   - After a later advance, a restore returns `as_of() == earlier`, and `cursor_for` returns the prior cursor.
   - Because the same legacy reader decodes these rows successfully, the refusals in case 2 must come from the usage type, not from replica drift.
2. **Current Grok snapshot and old wire refusal.**
   - The old shapes raise `ValueError` on the real persisted Grok claim rows, on `PendingClaim`, and on the `_GrokProgress` BLOB.
   - Restoring after a second ACK returns `as_of() == before` and the exact sealed progress.
   - An idempotent ACK replay writes nothing new.
3. **Independent new coordinator lease.** Exhausting the fixture releases the lease. A fresh `Registry(...).writer()` with a new `ScopeState` then refuses `prepare` ("authority") and leaves durable progress untouched.
4. **Original rival capture edge and dispute.**
   - The rival gets a real `CaptureChange` APPLIED, a distinct checkout and a distinct incarnation, producing the same observation key.
   - The result is DISPUTED, with ownership kept by the original project.
   - There is no progress write, one dispute row whose contender is the rival, and the rival ledger sequence stays 0.
5. **Pre-enrollment and stable policy exclusion before payload.**
   - `read_delta` is patched to fail for the whole test.
   - Pre-enrollment refuses at the epoch precheck with no coverage change.
   - A bare consent bit under a fresh writer yields `_LiveSourceUnavailable`, an `UNQUALIFIED_SOURCE`/`unknown` exclusion, and no claims or progress.
6. **Observational cursor and legacy helper/guard refusals.**
   - An adapter-issued `GrokCheckpoint` cursor is refused by `reserve` ("not issued together").
   - `_source_checkpoint` refuses the verified Grok cursor.
   - The `monitor_writer.py:69–76` guard refuses a changed revision in both `_monitor_revision` and `commit`, with destination sequence 0.
7. **Persisted transcript sentinels.** The native path, session ID, native event ID and a prompt confirmed present in the source file are all absent from the stored claims, progress and `delivery_acks` bytes.

**Non-blocking residuals**

- `_pair` has no direct Grok-cursor refusal test; only `_source_checkpoint` and the public `cursor_for` are exercised.
- Only the revision arm of the writer guard is exercised; the surface and time-basis arms are not.
- Journal snapshot save and restore use test-local SQLite backup helpers rather than a product journal backup API.
- The two direct `__wrapped__` fixture uses don't release the lease if an assertion fails early.
- The R1 note on `NativeSurface` vs `.value` in `_grok_stream` still stands.

All existing protected merge, native Close, runtime scope and 4.0h cap gates remain in force.
