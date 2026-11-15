[15:03:15]
**SOURCE_329: HOLD**

This review covers the exact candidate `161fbb94` (tree `02771dc6`, base `84b936d1`) and its four paths, using only the supplied diff and evidence. Cut arithmetic, codecs, receipts and the #330 boundary match the accepted JIT. Three issues block, and each one names exact code and a reachable behavior regression.

## Blocking findings

**B1. A pending command with frozen cuts crashes strict reads with an untyped `TypeError` (violates H4 multi-stream and H6 bound routing).**

The fault is in `monitor_registry.py:~486`, inside `_grok_span_disposition`:
```python
cut = next(
    (cut.ordinal for current, cut in record.cuts if current == identity),
    None,
)
```
- `record.cuts` holds `_GrokFrozenCut` instances, which are slotted dataclasses and cannot be unpacked. `_GrokPending.__post_init__` and `_grok_read_fences` both read them correctly through `item.identity` and `item.cut`.
- The generator walks every cut on the edge. So any strict read of either the quiet stream or the armed stream crashes once `admit_span` or `_observation_proofs` reaches a span below its bound.
- The trigger is a disable (or an enable over an active epoch) where one stream is quiet with completed turns not yet read, and another stream is armed.
- The result is that `read_source` raises a raw `TypeError` instead of `_GrokCaptureHeld` or a routed or held result.
- Tests miss this:
  - `test_grok_open_disable_waits…` only reads while `pending.cuts == ()`.
  - `test_grok_quiet_cut_is_frozen…` only reads after commit, with a quiet stream cut at 0.
- **Fix:** `(item.cut.ordinal for item in record.cuts if item.identity == identity)`.
- **Test:** add one where both streams are read during a mixed pending. Spans at or below each stream's own bound get their expected disposition, and nothing above a bound routes.

**B2. A held terminal on the armed turn wedges the disable instead of cutting back to the verified start (violates H4).**

The fault is in `sources/grok.py:417-418` and `:477-478`:
- `complete` raises `_Held` when `stop_reason != "end_turn"` (or when usage fails to parse) before it appends any `_GrokTerminalSpan`.
- In trace mode, `read` re-raises it (`if not self.strict: raise`).
- `_grok_capture_offer` then converts that to `_GrokCaptureHeld("Grok capture material is unavailable")`.

The consequence:
- If the open turn is cancelled, `arm.open_start` is never reached.
- The disable stays queued forever, the permission stays enabled, and every same-edge successor waits behind it.
- Reads stay capped at P, so there is no leak, but the behavior contradicts H4: a held terminal should make disable cut at the verified start while enable stays queued.
- `test_grok_bad_open_terminal_closes_disable_at_verified_start` covers only an `end_turn` with an unverified receipt.

**Fix:** in trace mode, record the armed turn's held terminal as `verified=False`, still keyed to its start. **Test:** add a case where the armed turn ends with a non-`end_turn` stop reason, and a case where its usage is malformed.

**B3. The accepted failure matrix is not exercised (violates H11 and H6).**

- **H11:** `test_strict_grok_attempt_holds_at_start_and_can_retry` parametrizes only `["missing", "invalid", "wrong-verifier", "failed"]`.
  - The `no-issuer`, `multi` and `late` branches, plus the `else` branch for an unmatched event ID, are dead.
  - Including the duplicate-receipt test, 5 of the nine cases run.
  - "All nine stay held with no hookless fallthrough" is unproven for `late` in particular, because that outcome depends on product timing checks that no test exercises.
- **H6:** no test covers fork or incarnation replacement on an already-admitted stream.
  - The path is the `"incarnation or generation changed"` branch in `_read_grok`.
  - `add_stream` creates a new session, which is the late-stream case, not a replacement.
  - The `"generation"` match exercises only the profile half of that branch.

## Verified (no finding)

- **Codecs:**
  - The goldens assert `626314e3…` and `7e56be80…` (E2).
  - Extended-empty input is refused, and decode tries the native shape first. An old binary fails closed on `grok_records`.
  - The `_RegistryWithGrok.__post_init__` call chain and the cross-pending command/edge uniqueness checks are correct.
- **Cuts:**
  - Quiet stream: start = end = P.
  - Open turn: the cut is (terminal row + 1, `byte_end`), so the ordinal and the prefix byte end are kept separate.
  - The excluded and included open-turn arithmetic checks out against `_grok_span_disposition`'s epoch logic.
  - Frozen prefixes are rechecked before commit.
- **H7:** with no callback, `BoundaryUnavailable` leaves the command queued with no receipt. The Codex command applies and the same-edge successor waits.
- **Offer authority:** the identity-keyed sink, re-entrancy refusal and reuse test all hold.
- **H8:** after the read, the code rechecks the lease, live identity, root, origin and strict prefix. A seeded admission is popped once.
- **H10/H11:**
  - `UNSUPPORTED_FORMAT` is raised before any read.
  - A strict hold resumes at the start of the attempt.
  - `grok-capture-delta-v1` is domain-separated, and the observational-cursor refusal is tested.
- **Routing:**
  - A mark needs exactly one APPLIED event at its exact position with the same `GrokBoundary`.
  - Hookless turns get a project route with no story.
  - `apply_mark` re-derives the boundary from strict proofs.
- **H5:**
  - A same-writer cold reload passes the prior strict checkpoint to the real `read_delta`.
  - Replacement holds with `"generation"`, and revoke or a new lease holds with `"authority"`.
- **E3/E4:** `monitor_types.py` is untouched, and `GrokBoundary` is imported at runtime.
- **Scope:** exactly four paths, and #330's journal refusal is preserved.

## Non-blocking, carried to re-review

- **Verifier binding:**
  - `_grok_verifiers.setdefault((source_id, generation), reader.verify_receipt)` binds to the first reader object that applies a command. It does not bind to a verifier selected by the profile.
  - The wrong-verifier test is adapter-only.
  - Before Close, add a product-level test where a second `ScopeState` reader under the same lease is held.
  - Confirm that the production reader's verifier is selected per generation.
- **H9 receipt joins:** the fixture uses a dict verifier (`refs.get`), not the #304 issuer's selected verifier. State explicitly whether "independent inputs" covers this.
- **E1:** the `mergeCommit.oid` record for #326 is not in this packet.

## Disposition

- **Rework size:** B1 is a one-line fix plus a test. B2 is a small trace-mode change plus two tests. B3 adds four parametrize IDs and one replacement test. Together this is about 0.5h, inside the remaining matrix allocation and under the 4.0h cap.
- **Re-review scope:** the new head's diff for `_grok_span_disposition`, the `_NativeWalk` trace path, and the new tests, plus fresh hosted evidence for the new tree.
- **Gates:** all gates, the four-path limit, the #330 boundary and the enrollment exclusion are unchanged.

**SOURCE_329: HOLD**
