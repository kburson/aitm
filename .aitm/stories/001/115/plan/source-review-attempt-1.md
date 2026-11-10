# #115 independent source review hold

Declared-manual Claude Code `claude-opus-5-5` with medium effort requested. Head `803ce4e86b7e49b6d327b71a3865f0816af38a82`, tree `a22dccc417716be8ba1704b36acae87fe9bfc420`. Signed [hosted run 42867102377 attempt 1](https://github.com/kburson/aitm/actions/runs/42867102377/attempts/1) passed on that candidate.

## Review of AITM #115 M05 at 803ce4e: HOLD

I reviewed only the supplied packet: the accepted pickup, the clarifications, the carrier report, the baseline shapes, the signed evidence and the full diff. I did not replay hosted CI, the raw provider captures or the raw rate-source response. I also did not recompute the diff SHA-256.

## Blocking finding

**B1. A keyed snapshot dispute holds the whole stream and can never resume.**
- **Where:** `sources/grok.py:677-678`, inside `GrokAdapter._read_delta`:
  ```python
  if disputes:
      return AdapterBatch(diagnostics=disputes, cursor=cursor)
  ```
- **What changes:** if `_reconcile` produces any keyed dispute, the read returns no observations and no boundaries. The cursor stays where it was. This includes completed native turns whose snapshot rows matched cleanly. The test `test_internally_conflicting_snapshot_disputes_the_matched_turn` locks this in. On a cold read it expects zero observations, even though only turn A is disputed and turn B matched.
- **Why the hold never ends:** `_reconcile` runs again on every read against all retained completions. The snapshot keeps prior turns unchanged as it grows, so the same dispute comes back every time. The adapter has no input for a recorded disposition. One contradictory snapshot row therefore withholds every later native turn in that session, with nothing to release it.
- **Contract conflict:** the pickup says "No charge can be emitted for affected observations in the same batch" and "Hold the affected batch and cursor when the conflict cannot be keyed." A keyed dispute should go to M08 as an incomparable-content dispute. Here a snapshot, which is not the authoritative record, ends up blocking unrelated native turns that are eligible to count.
- **Required fix:**
  - Emit the keyed disputes and drop only the affected observations and boundaries (A, if it is new).
  - Emit unaffected new turns and advance the cursor.
  - Add a test where turn A is disputed while turn B is emitted, then repeat the read and check the result is the same.
  - Decide explicitly whether native duplicate `IDENTITY_CONFLICT` should also hold the cursor. Native overlap holds are covered by the contract.

## Checks that passed

**Scope and receipts**
- The adapter reads only `updates.jsonl` and the sibling `usage.json`, both through confined no-follow opens with identity checks.
- The receipt verifier is injected, receives exactly (session, prompt, hook `eventId`), and its result must pass `validate_source_ref`.
- A forged reference, a missing receipt, or a hook that did not succeed gives no boundary. A receipt from a late hook cannot be backdated onto an earlier completion. Two different verified receipts for the same prompt are disputed.
- No destination ledger opens. The fixture patches `Ledger.open` and `Ledger.writer` to fail the test.

**Source identity**
- The packet's head, base and tree all match the signed evidence: six jobs, 629 tests against a baseline of 592.
- `tested=dede6b2…` is not the head commit. That is consistent with a merge-ref run, but the link to tree `a22dccc` rests on the signed verifier. I did not check it independently.
- The +1 test in `tools/ci/tests/test_cli_evidence.py` is not explained by the diff, which does not touch `tools/ci`. It needs a one-line explanation (for example, a test parametrized over files in the tree).

**Origin**
- The pinned Darwin/arm64/1.0.77/`50ca579fa996`/digest/format 1 tuple is enforced. `lineage_id` must equal the session ID.
- The origin is re-verified at read time. A missing or mismatched origin, including Linux, returns `UNSUPPORTED_FORMAT` with no observations and no cursor advance.

**Late arrivals, native-only turns, snapshots and restart**
- Native-only turns count and get an `UNRECONCILED_USAGE` gap. A snapshot alone counts nothing.
- The snapshot window is [0 s, 1 s) using true instants, and the second-straddling fixture covers it. Out-of-window and ambiguous rows become non-keyed gaps.
- Restart is covered at every row split. Exact retry is idempotent.
- Cursor tampering is caught: the prefix, incarnation, cutoff and inherited prompt IDs are bound by a keyed anchor. Rewind, size or turn-limit gaps, and a seconds/milliseconds mismatch all hold.

**Confidentiality**
- Raw IDs, paths and hook names are sentinel-checked in the cursor, boundaries and observations. Exception paths drop raw content. Fixture IDs and timestamps are synthetic.

**Legacy compatibility**
- `types.py`, `export.py`, the ledger and `2026-11-09.json` are untouched.
- The Codex and Claude cursor bytes round-trip.
- `Provider` still refuses `grok`, and `MonitorObservation` rejects Grok models.
- The `scan.py` change is an internal signature change only.

**Rate provenance**
- The URL, the 2026-11-10 retrieval date and SHA-256 `cf323be0…c440` match the pickup exactly.
- Rates are 2 / 0.5 / 6 USD per million tokens, for `grok-4.7` only. A price is given only when input including cache is strictly under 200,000 tokens.
- Cache creation is fixed at null, and any positive cache creation makes the price Unknown. `grok-4.7-build` is Unknown, and there are no Claude cache-time-to-live (TTL) buckets.
- Provider cost ticks are kept separate from the estimate.

## Non-blocking issues

1. **A turn in progress holds the batch.** It blocks all earlier completed turns in the same delta and raises `BOUNDARY_UNVERIFIED` on every poll. The cursor could instead commit at the last completion offset.
2. **One cancelled turn holds the session permanently.** That matches the contract as written, but it is a liveness risk for M18/M19.
3. **Mixed-up inputs fail silently.** `ProviderAdapter.read_delta` and `GrokAdapter.read_delta` return an empty batch, with no diagnostic, when given the other adapter's locator or cursor.
4. **Untested refusal paths:**
   - `verify_origin` returning `None`
   - the origin changing between discovery and read
   - a row type outside the allowlist
   - non-empty `background_tasks`
   - a hook and completion for different prompts
   - a byte fixture for a pre-M05 `MonitorRevision`
5. **Positive cache creation is an assumption.** The code assumes the native `inputTokens` includes cache creation. The capture only had zero cache creation, so this is unproven. Pricing is Unknown in that case, but the token buckets would still be affected.

## Source and fixture proof versus native production admission

Everything here is source and fixture proof. It comes from one controlled two-turn macOS arm64 capture with synthetic IDs and timestamps, single model calls and zero cache creation, plus a dictionary standing in for the receipt verifier.

None of it is native production admission. The receipt authority, the verifier and routing belong to M07. Live qualification across arm64 and x86-64 belongs to M18/M19. Linux enablement belongs to M05-LG. There was no production activation.
