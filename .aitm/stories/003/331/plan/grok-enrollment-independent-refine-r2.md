[15:35:28]
**REFINE_331: PASS**

The amended body closes all five prior HOLD items inside the same three files. Receipt plus reconstructed body is the correct and sufficient proof of a retained applied publication.

## Applied-publication proof

The supplied `apply_pending` shows why this works:

- It computes `digest = command.payload_digest` over the full `_encode(ControlCommand)` wire: ID, payload and format.
- It appends `ControlReceipt(id, APPLIED, digest)` to `receipts` in application order and runs `_save(view)`.
- Only after that does it call `inbox.discard`.

So once the queue file is discarded, the committed receipt is the only retained proof, and nothing else is available to read. Rebuilding `ControlCommand(receipt.command_id, CaptureChange(edge, enabled))` and matching the digest does three things:

- It binds that receipt ID to this exact edge and its enable or disable bit.
- It separates enable from disable, and APPLIED from REJECTED.
- It makes "latest in committed receipt order" a sound way to detect a superseding disable.

A crash after save but before discard leaves a queued residue that already has a receipt. That residue only causes a hold until the next drain retires it, so it fails safe. No new ControlInbox API is needed: `publication()` and `iter_pending()` are already public.

## The five corrections

1. **Grant alternative, only when needed.** It is required for a qualified empty-root grant or any retained enrollment. Bytes stay identical when neither exists, and the legacy goldens are kept. ✓
2. **Grant derivation.** The grant comes only from the latest APPLIED receipt plus a reconstructed digest match, live permission, a non-conflicting pinned installation, and an active epoch at the current profile generation. Otherwise it holds and falls back to an explicit owner enable. A fourth file requires going back to the scope decision. ✓
3. **The #329 empty-enable wait is named.** With a verified callback and zero streams, it becomes a root permission grant that opens no transcript and invents no cut. A missing callback or missing authority still holds. The pinned tests `test_grok_command_without_callback_holds_only_its_edge` (:138) and `test_new_grok_stream_does_not_inherit_present_stream_cut` (:750) stay exact. No supplied test pins the callback-present empty wait. ✓
4. **Invariants and retirement.** The story refuses:
   - a duplicate active grant;
   - a missing or invalid grant receipt;
   - a same-ID pending command;
   - an unknown witness;
   - an enrolled identity with no supporting epoch.

   Disable ends the grant atomically with the epoch ends. Ended grants keep their gap provenance. ✓
5. **Citations.** The story cites the exact M06, M11, M18 and M19 sections in both plan files. ✓

The other recovery corrections also hold. Enrolled epochs stay at the grant's existing capture generation, never `1+max`. Witness and pre-witness extent are durable, and the pre-witness span is never attributed.

## #330 map and estimates

- **Paths are disjoint.** #330 owns `monitor_journal.py`, `monitor_writer.py` and `test_monitor_grok_delivery.py`. #331 owns `monitor_registry.py`, `monitor_scope.py` and `test_monitor_grok_enrollment.py`.
- **Compatible with #330 R5.** #330 reads `monitor_scope.py` (`_take_grok_admission`) and the registry read-only. Enrolled streams are ordinary `_GrokEpoch` rows at their existing generation, so R5's epoch selection is unchanged.
- **Estimates are unchanged.** #330 is 3.75h against a 4h cap. #331 is 2.75h provisional, with a 1.375h checkpoint and a 4h cap.

## Carried to JIT (not blocking)

- Confirm that `CaptureChange` is fully determined by (project, source, enabled). If it carries any extra field, reconstruction fails and the item goes back to scope.
- Pin how a re-issued enable on an already-enabled edge without a provable grant behaves. It must create no duplicate epoch or generation bump.
- Hold `_take_grok_admission`, the `_GrokEpoch` shape and the existing `_RegistryWithGrok` decode fixed. Whichever of #330 or #331 develops second re-pins the merged blobs. If #330's "not proven" codec dependency forces an extraction, re-map against #331's closed alternative.
- Pin the #121 gap handoff API and the down-while-created test. Confirm that the first-seen-mid-turn exclusion still leaves a post-witness hookless turn available for M18/M19.

No Develop approval or gate changes are made here. All Test, review, delivery and Close gates and the standing exclusions remain.
