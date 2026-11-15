[16:05:48]
SOURCE_330: HOLD

**Source verified at `0ead2c6e`, tree `3f843c53`**

The product source matches R1–R7 as far as the supplied diff shows. The hold is about missing required evidence, not a product defect.

- **Admission is used once.** `prepare` takes one `_GrokAdmission` and passes the same `locator` object to `read_source(..., _grok_admission=grok)`. The `finally` block deletes the admission only when `_grok_admissions.get(id(grok)) is grok` (monitor_journal.py ~1120–1155). The ordinary-error catch-and-fallthrough is removed, and the `_LiveSourceUnavailable` coverage entry is kept.
- **Unauthenticated streams do not open payload.** The `_GrokEpoch` identity precheck runs before `read_source` (~1126–1135).
- **Cursor progress is sealed and per-stream.**
  - `_grok_stream` builds a five-part key from a pseudonymized locator and contains no raw path.
  - `_grok_progress` seals the stream together with the canonical `GrokCheckpoint`.
  - `_cursor` decodes by surface and recomputes the seal for equality (~1089–1097).
  - `_write_progress` writes the `_GrokProgress` BLOB (~2199–2209).
  - `_reserve` refuses an equal or regressed offset (~2224–2232).
  - The legacy `StreamCursor` path and `_source_checkpoint` are unchanged and refuse a `GrokCheckpoint`.
- **Completion is per-provider.** For Grok, `settled = 0`, so the paired frontier is skipped (~1186, ~2236). The `_complete` Grok branch (~1809–1829) needs every observation selected and an exact APPLIED event whose `native_boundary` matches. A resolved hold stays held, which fails closed as the JIT accepted.
- **Claims preserve the original epoch, cost and ownership.**
  - `_grok_claim_evidence` (~1858–1905) requires the proof to be eligible for the current project and hookless claims to carry no story.
  - It requires exactly one matching epoch, and takes `typed.start`/`end` with that epoch's own generation and start boundary.
  - An exact retry also requires `first.evidence == position` (~1995–1999).
  - Revision is pinned to 1.
- **Codecs.** `PendingClaim` is local to `monitor_journal.py`, which clears the open JIT condition. The union fields keep the legacy golden bytes, as the first test shows.
- **Writer.** `monitor_writer.py:69–76` is the only Grok branch. It checks surface, time basis and revision 1, and leaves the key, commit, readback and ACK paths unchanged.
- **Scope.** Exactly three paths changed, with no schema, DDL or outside edit.

**Holds (all in `packages/aitm-usage/tests/test_monitor_grok_delivery.py`, nine tests, 392 lines)**

1. **R8 older-reader refusal is not demonstrated.**
   - No test has an unchanged older reader decode the activated Grok `_ClaimPayload`/`PendingClaim` or the `_GrokProgress` bytes and refuse them closed.
   - No test then reads a separately retained compatible legacy snapshot.
   - The refusal is plausible from the exact codec, but R8 requires it to be shown.
2. **R8 #122 restore is only partly covered.** `test_pinned_grok_destination_restore_preserves_row_and_lost_ack` covers only the destination ledger. Nothing exercises journal-side backup/restore of legacy state and of a current Grok snapshot.
3. **Required R9 cases are absent:**
   - **New-writer hold.** Every reload reuses `f.writer` with a fresh `ScopeState`, so "a new writer has no assumed grant and leaves durable progress untouched" is never exercised.
   - **Current owner conflict.** The rival test covers destination-project refusal, not a competing claim owner held or disputed without a write to the contender.
   - **Typed policy exclusion.**
   - **No eligible Grok path before enrollment.**
   - **No path using an observational cursor.**
   - **Bridge type refusals:**
     - the `_DeliveryRefused` branch at monitor_writer.py:70–75 is untested;
     - legacy `_pair`/`_source_checkpoint` refusing a `GrokCheckpoint` is untested.
   - **No raw path, prompt or native ID stored:** no assertion over the persisted `progress`, `claims` or `delivery` rows.

**Non-blocking:** `_grok_stream` puts `NativeSurface` (an enum) in `stream[1]`, while the legacy key uses the `.value` string. This works only because of `StrEnum` equality and str binding. Using `.value` would match the legacy key exactly.

**To clear:** add these cases to the same test file. No product edit is expected unless the older-reader test shows a non-closed decode, in which case return to Refine. The changed head then needs the locked local Test and the same-head signed hosted Test again before a fresh independent source review. The protected merge, native Close and 4.0h cap remain in force; at most 0.25h of budget is left.

SOURCE_330: HOLD
