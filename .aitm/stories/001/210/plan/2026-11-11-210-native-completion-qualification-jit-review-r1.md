# #210 qualification JIT initial HOLD

Claude Opus 5.5 high. Packet SHA-256 `1aecf2a99390327603eec32bdfeb257244596864d7f5578d35621309d06ab6a1`.

HOLD

**Decision:** The slice is the right shape. It is read-only. It adds an opt-in reader that does no extra work by default. It reuses the existing `REQUEST` receipt and `verify_boundary` instead of inventing new authority. It leaves cursors, journal and codecs alone, and it does not require a genuine positive before the code is written. I don't require a second owner approval. The problem is that this reader defines what will later count as the genuine native positive. That makes its acceptance rule (the predicate it uses to accept a completion) the release gate's evidence, and four parts of that rule are still underspecified. The fixes below are text amendments to the JIT, not a redesign.

## What passes as written
- **Provenance:** the witness is tied to the existing receipt-linked `REQUEST` boundary (ordinal 60 in the probe) and the actual close. It is the first unique match under `verify_boundary`, so the later `TURN` receipt (ordinal 63) can't win.
- **Prefix integration:** the witness comes only from the verified selected rescan. Unverified or superseded scans are discarded. There is no fallback from a frame the scanner rejected. The fixed prefix and actor are rechecked.
- **Compatibility:** next-turn checkpoint suppression, diagnostics, the three verbs and the `custom_tool_call_output` pin all stay. The other output type is tested as a negative.
- **Deferred accounting:** later same-turn usage is a required negative. Byte-for-byte checks of durable state and cursor are required.

## Required corrections

1. **Pin which path delivers the witness, and add a differential test.** In the probe, every phase returns through the `BOUNDARY_UNVERIFIED` early return with `cursor=cursor`. That is because the neutral-marker suppression leaves `provider_checkpoint` empty. The JIT must:
   - say the witness travels only on that path, only when `scope_verified` is true, and alongside the unchanged diagnostic;
   - add a test showing `observations`, `boundaries`, `diagnostics` and `cursor` are identical with the sink on and off.

2. **Define what may sit between the accounting counter and `task_complete`.** "Fully reconciled final response" and "single current candidate" leave this open. Either:
   - require that the receipt-linked response is the turn's last response, with no tool call, response, usage or boundary between its changed-total counter and the close; or
   - state exactly how intervening same-turn activity is accounted.

   Add a negative fixture with a second tool call and response after the disposition response but before completion. Also pin "closing row at the fixed frontier" to mean: the close is the last committed frame, there are no look-ahead frames after it, and the committed frontier equals the physical capture limit.

3. **Detect terminal errors and persistence warnings with a closed allowlist.** Use only recognized `task_complete` fields and only permitted intervening row kinds. An unknown field, an error payload, a warning or error event, or `turn_aborted` must fail closed. Add fixtures for:
   - a persistence warning (currently a condition with no test);
   - a pending compaction;
   - a parallel call;
   - pre-cutoff rows;
   - a quota-only tick (it must not count as accounting);
   - a timed counter only;
   - a missing baseline;
   - a counter regression.

4. **Confirm the accounting classification is actually computed on this read.** `counter()` returns before computing `complete` when `record_usage` is off. If the neutral-marker scope read runs with it off, the JIT must say how "complete usage classification" is obtained without changing the ordinary output. A missing classification must count as unqualified. The accounting frame must also have emitted no `COVERAGE_GAP` or `UNRECONCILED_USAGE`.

5. **Keep `verify_boundary` reuse pure, and make the evidence type unusable elsewhere.** The JIT must state that `completion_witness` records nothing: no verified-boundary or authorization state, and no `_batches` mutation beyond today's. It returns a new private-constructed type that no existing route, journal or settlement API accepts. Add a test that passing it, or its `VerifiedBoundary`, to the existing next-turn `verify_route_disposition`/settlement paths is refused. Also require `kind is REQUEST`, `boundary_ref == codex_request_boundary_reference(command_id)`, and `anchor_ref is None` on both the request frame and the close frame.

6. **List the qualification-level negatives in Task 2.** Each must return unavailable with no state write:
   - a non-`Disposition` command;
   - an unauthorized command or a digest mismatch;
   - the wrong project, checkout, source or surface;
   - a hold span that does not end at or before the close, or a hold that has changed or expired;
   - a hold that already has a next-turn proposal (no supersede path);
   - a prefix or actor that changed between the read and the qualification;
   - a stale, foreign or unregistered batch;
   - a copied or foreign transcript;
   - a default `qualify_completion=False` batch passed to `completion_witness`.

7. **Make the bound actionable.** State what the 0.75 h checkpoint decides. At 1.60 h, stop and record a split that keeps every native gate. Say whether the genuine Desktop attempt counts inside 1.60 h. Also record a known risk for that attempt: the parser recognizes only the canonical `aitm-usage --project …` form. So a genuine run needs Desktop's own exec environment to resolve `aitm-usage` to the isolated launcher without touching the installed one. If it can't, record that as the gap; don't use an absolute-path variant.

## Unchanged
- A genuine Desktop positive is still required before any release, and this evidence grants no cursor or settlement.
- These stay outside this slice: existing next-turn proofs and storage, CI gates, #204/#119 (gated until #210 delivers), Epic #2, C01 and production.

Once these corrections are added to the JIT text, it should pass with no further design change.
