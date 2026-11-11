# #203 independent JIT review round 2

Claude Opus 5.5 high. Reviewed plan SHA-256 `85251276ccb766489794e39be47f1ed52d78a8a566e76b502c5372a0e049d9b2` on November 10, 2026 America/Chicago.

# PASS

This PASS covers the amended JIT `85251276…` as supplied, read against the retained HOLD and the Refine split `0158b267…`. I did not recompute either hash, and I used no tools. It authorizes Develop on this text only. The live rechecks the JIT already requires still apply.

## B1–B3

| Item | Status | Basis in the amended text |
| --- | --- | --- |
| **B1** What `require_route_disposition` does after issuance | Resolved | `require` re-runs the issuance conditions: the terminal is still unsettled and the physical extent is current. Appending later usage makes it refuse even with both prefixes intact, so `require` now behaves like issuance and reissuance. It also refuses after `expire()`, after a real legacy `dispose`, when the queue item is consumed, when the reader advertisement is withdrawn or expired, and when the grant is revoked. An expired RESOLVED proposal refuses before `expire()` runs. Work step 3 tests each of these against tokens already issued. |
| **B2** Legacy writers on a v2 file | Resolved | Legacy mark/handoff, default `hold`, `expire` and legacy `dispose` carry both new collections through byte-exact, and v2 writes stay v2. Default-path v1 writes keep the exact old shape. Each writer and the v1 path gets a RED/GREEN test. Replaying `retain_route_target=True` on a legacy hold with no saved target raises and publishes nothing. |
| **B3** Which hold states admit a proposal | Resolved | GAP may be proposed for a HELD target with retained proof, or a retained target that `expire()` moved to GAP. An opt-in hold that would be GAP at birth raises before publication, so a born-GAP hold never has a target. A target already changed by a legacy `_Resolution` refuses both kinds of proposal. The new `hold_state` field (HELD or GAP, and HELD whenever the outcome is RESOLVED) records which case applied. |

## Earlier non-blocking items: all addressed

1. **`_apply`:** The proposal path calls no `_apply`, no legacy `dispose`, and no other mutation besides the one record publication.
2. **Lock order:** The coordinator writer is taken first. The inbox publication lock is then held across queue verification, scope publication and confirmation. Imports stay local to avoid the module cycle. `open_grant` plus `require_witness` check the reader advertisement as well as the sealed item.
3. **Prefix is not a cursor:** There is an explicit assertion that no progress or journal path consumes either prefix.
4. **Known limitation:** The JIT states that once later usage is appended, the proof cannot be reissued after a restart, and that #210 must qualify its own settlement authority.
5. **Evidence:** The readback now shows #202 Done at Rank 227, #203 in Backlog at Rank 228, and #204 and #119 OPEN. The diff between the baselines has only the two dashboard files, and Ruff lint shows "All checks passed!".

## Earlier conditions

- **Refine binding condition 2 (later-usage outcome):** Met for issuance, reissuance and `require`. The parser still sees the receipt, and the cursor carries no settlement authority.
- **Binding condition 8 (source/session/stream equality):** Present in work step 2.
- **Fixtures:** Rows are monotonic, usage deltas are positive, and nothing is backdated or zero-delta. The genuine later-usage control stays.
- **Unchanged state:** Scope, holds, journal bytes and prior cursors are compared across issuance and replay. See note 4 about the view.

## Custody and compatibility

- The v1 dataclass, file and decoder stay byte-compatible.
- The v2 payload is closed. Mixed, foreign and unknown formats refuse before mutation.
- The old reader refuses v2 and leaves the file byte-identical.
- A reader without a writer sees only events and holds.
- No production caller opts in, so production writes no v2.
- A visible publication whose directory sync failed issues no token until reopen and an exact recheck. A persisted record alone never grants authority.

## The proof cannot settle anything

It is proposal-only. The terminal must be the final TURN, there must be no cursor, and only BOUNDARY_UNVERIFIED may be present. Nothing may be appended past the prepared read, and the proof records no claim that later usage is absent. The durable hold keeps its state, nothing reaches the view or routing, `require` never writes, and the prefixes stay out of the cursor and journal paths. Nothing in the text lets the proof move a cursor or change a hold.

## Native gate and branch identity

- **Branch:** `codex/aitm-203-native-disposition-proof`, owned by Codex.
- **Baseline:** literal trunk `e4701f2e…`, tree `f62fbd48…`.
- **Graph:** unchanged from the accepted readback.
  - 203 blocks 209, 204 and 119.
  - 209 blocks 210 and 119.
  - 210 blocks 204 and 119.
  - 204 is blocked by 203 and 210.
  - 119 is blocked by 118, 199, 201, 202, 203, 204, 209 and 210.
- All of these are #100 children, there is no cycle, and #209 and #210 sit at Ranks 228.1 and 228.2 in Backlog.
- The bounds hold: 3.85 hours under the 4-hour cap, with the checkpoint at 2.25 hours.

## Non-blocking notes for Develop

1. **The two supplied `_require_boundary` bodies disagree.** The "Relevant literal source" ends with `return self._apply(command, receipt)`. The "Complete relevant helpers" version ends at the Mark/Handoff `_development_proof` check. Confirm the actual body on `e4701f2e` before Develop. The proposal must not call `_apply` either way.
2. **Scope of "at most one disposition per hold."** The decoder must count this within `route_dispositions` only. Otherwise the tested sequence "proposal, then real legacy `dispose`" would produce a file the decoder rejects. Keeping the two collections apart is enforced at issuance, in one direction. Say this in the code comment or test name.
3. **Clock and lock order for `require`.** Name the clock `require_witness` uses: `ScopeState._now()` or the inbox's `_scope_now()`. Have `require_route_disposition` use the same writer-then-inbox lock order as issuance.
4. **The view comparison.** Compare `view()` explicitly before and after issuance and replay. "No view or routing effect follows" deserves a direct assertion.
5. **Hand-off to #210.** A HELD GAP proposal that `expire()` overtakes can never be reissued: replay requires the current `hold_state`, and a second command refuses. This is conservative. Record it for #210 alongside the restart limitation.
