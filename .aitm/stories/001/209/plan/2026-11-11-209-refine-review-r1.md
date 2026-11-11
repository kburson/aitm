# #209 independent Refine review round 1

Claude Opus 5.5 high. Reviewed artifact SHA-256 `59bed848a1f0d2aca3372a995cad13c20b8ba1bf6e8e25806b00168a142b9582`. Packet SHA-256 `2ff34f47adb7677a0e52cfaa99e1f52678dd16f5d379cabeead3a4cccffe9250`.

HOLD

This covers the #209 Refine text exactly as it appears in the packet. I didn't recompute SHA-256 `59bed848…`. It is a review of Refine only. It authorizes no JIT, Develop or later gate.

## Blocking

**B1. The native graph claim conflicts with the packet's own read-back.**
- **What the Refine says:** "#119, which retains all eight dependencies."
- **What the read-back shows:** #119's blocked-by list has seven entries: #118, #199, #201, #203, #204, #209 and #210. #202 is not in it.
- **Why this blocks:** Either the count is wrong, or a direct #202 → #119 edge was dropped during the #203 split. The split required "Recheck all parent, project, direct #119 and successor edges", so this has to be settled.
- **Fix:** Change the claim to the exact seven-item list and give evidence that #202 was never a direct #119 dependency. If the edge was lost, restore it under the split's rules and read it back.

**B2. Additive storage compatibility is asserted, not specified.** The Refine only says "one strict additive v4 table" and "committed GREEN v4 migration". The #199 schema-review rule (admission from the old version, atomic change and retry, old rows, historic views, unknown formats) is what makes "strict v4 compatibility" in the split something you can check. None of it is named. Add Refine-level obligations for:
1. **Which store:** which store "v4" refers to (the RoutingJournal schema, not the #203 scope artifact) and the current version it starts from.
2. **Migration safety:** an atomic migration from the old version, plus retry or crash recovery that is idempotent.
3. **Old rows:** existing journal, claim and revision rows stay byte-equivalent, and historical views from before v4 are unchanged.
4. **Wrong formats:** older code and wrong, mixed or unknown versions fail closed.
5. **Replay identity:** the replay key for `record_disposition` is stated. An exact replay returns the same record, and reusing a key with a different proposal is refused.
6. **Pre-commit failure:** if the current-authority check fails, the call refuses and writes no row. Today only the behaviour after commit is stated ("affects current authority only").

The 3.90h estimate and the 2.25h checkpoint can't be judged until these are in scope.

## Verified (no change needed)

- **Delivery prerequisite**
  - PR #211 merged as `b0f8ac79…` with tree `6b684109…`, and the parents and zero diff were verified.
  - #203 is CLOSED COMPLETED and Project Done (Rank 228, M, 3.85).
- **Graph edges**
  - #209 is blocked only by #203 (closed).
  - #209 blocks #119 and #210.
  - #210 is blocked by #209.
  - #204 is blocked by #203 and #210.
  - There is no cycle, and this matches the approved split.
- **Proposal vs. settlement**
  - The Refine is explicitly recording-only and doesn't move the hold or cursor.
  - Settlement, the effective hold and both frontier proofs stay with #210, and folded intent stays with #204.
  - The rule that "no release can rely on the EOF read" is respected.
- **Late overlap**
  - Overlap is tested on native coordinates with a nonempty half-open interval.
  - Keys are used only to deduplicate and order, and capped keys are treated as hints.
  - Projections are tied to the sequence: a later claim changes only newer views.
  - Touching endpoints, foreign/copy cases and hints that miss a real overlap are all required.
  - The probe ("exact prior span [41,62) … without rewriting bytes") passed.
- **Held diagnostics**
  - Grok contradiction stays held, the Codex claim and cursor are intact, and there is no admitted Grok claim to seed.
  - The Claude aggregate and quota cursor is preserved, and the Claude copy with a different scope is held.
  - Probe result: 5 passed. M09 owns publication and ACK.
- **Bound**
  - One M leaf at 3.90h is under the split's 4h cap.
  - The checkpoint at 2.25h has concrete exit criteria (committed GREEN v4 migration, real proposal and late-overlap REDs).
  - The fallback is an additive store custody split that needs independent review and its own JIT, and the existing gates stay.

## Nonblocking (carry into the amendment or the exact JIT)

1. **#203 review binding condition 1 is not carried.** The frozen `record_disposition` / `JournalChange` contract must let M08b4c's settlement and #204's folded intent each land as one atomic change without a second change. "Does not settle #210's API" is consistent with this but doesn't state it.
2. **Unchanged state needs a byte comparison.** Mirror #203 condition 6: compare the private ScopeState artifact bytes, `view()` / routing view, holds, cursors and existing journal rows before and after recording and replay. The current text covers only "hold or cursor".
3. **Missing read-back for #209.** Read back #209's Project item (Rank 228.1, Status, Size, Estimate) and its #100 parent. Neither appears in the packet.
4. **Probe provenance.**
   - Record the probe's base commit and fixture hash, and label each JSON read-back with its issue and relation.
   - "Codex gap alone matches quota diagnostic code" is not the Claude quota-only case. Make complete Claude quota-only, same-code generic, mixed and OVERLAP_UNVERIFIED separate named cases.
5. **Late-overlap fixture.** The second claim in [41,62) depends on a legacy disposition releasing the hold. The JIT should label that as fixture setup outside the #209 path and say how the #209 projection treats it.
6. **Copied-scope assertion.** Name the causal-revision refusal assertion for the copied observation with a changed scope, as the split assigned to M08b4b.
7. **Undefined term.** Define "lost queue grant".
8. **Estimate headroom.** The cap leaves only 0.10h of headroom. If B2's added controls push the estimate over 4.00h, use the custody-split fallback now instead of after the 2.25h checkpoint.
