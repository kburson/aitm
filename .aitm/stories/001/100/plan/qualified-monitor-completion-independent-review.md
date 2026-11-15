[18:06:09]
**DESIGN_295: HOLD**

**COMPLETION_100: PASS** (conditions below must be met at activation)

These verdicts cover these exact artifacts:
- `b380c19d69f600ed6f24200049c36f02099fd5b11983b6a74af6e7f0ca319d0f` `2026-11-14-295-claude-evidence-design.md`
- `19a3509697b9aa0c7ad3c6567da17951e3de1f6c357278a214fddf70b2f5446d` `2026-11-14-100-qualified-monitor-completion-proposal.md`

I could not recompute these digests because I had no file access in this session. Both verdicts depend on the bytes matching them. The supporting materials had no digests:
- the three-channel and single-flight receipts
- the Refine HOLD
- the R3 text
- the NA-1 readback

The R3 bytes still can't be checked against `75d073bd…`, which was the Refine HOLD's point B3. That remains open for Refine.

---

## #295 design: HOLD

**What already holds**
- **Gates stay in place.** The design keeps all R3 containment, the receipt and ACK rules, journal fail-closed behaviour, consent and privacy, and the chain from Refine through Close. It makes no estimate claim and no graph edge on its own.
- **No private cursor writes.** It explicitly forbids private write methods, seeding a cursor from a fixture, and direct cursor writes. Progress goes only through `prepare`, `reserve_batch` and `cursor_for`, and is revalidated in a transaction at the end.
- **No generic diagnostic clearing.** It forbids generic suppression and boolean or file pass-ins, requires typed matching to existing obligations, and lists the diagnostic classes that are kept.
- **Custody matches the evidence:**
  - The launcher holds the child's pipes for the whole run, with a fresh run ID and private OTLP credentials.
  - The join on provider request ID matches the evidence, and the separate OTLP client ID namespace is acknowledged.
  - Quota is tied to the serialized single-request pipe interval. This compensates correctly for the quota event having no request ID.
  - The design separates the native cost-state difference from the partial assistant counter.
  - Quota is kept as an account-window observation.
- **The three-process sequence is correct.** Making the enrollment turn the first input of a new process captures its rate event. This fixes the gap the scratch run admitted ("only proved the measured resumed turn").

**Blocking**

**D1. Where the new scope and authority belong depends only on the hour estimate.**
- The Refine HOLD said that supplying a Claude account is new quota authority, which falls under scope limits #295 must not change.
- This design adds a new account authorization issued from ledger custody, a launcher, an OTLP receiver, and changes to the adapter constructor. Most of that is outside the three files R3 names for M08b6.
- It asks for parent-plan acceptance only "if the combined leaf exceeds the accepted work bound." If the estimate fits, #295 grows in authority and files with no parent amendment. That skips an existing gate.
- **Fix:** require explicit parent-plan acceptance of the carrier's authority and file scope whatever its size. Either place it as a separate prerequisite ahead of #295, or accept an explicit R3 amendment that widens M08b6.

**D2. There is no honest path from the carrier to R3's fixture-based tests.**
- R3's tests 1, 2 and 4 must run red then green on literal trunk, using an allowlisted synthetic fixture. Each needs an admitted Claude prior cursor.
- This design limits positive evidence to "a pinned real ordinary run" and forbids fake or transplanted evidence. It does not say how a deterministic, hosted-runnable fixture gets writer-issued carrier evidence.
- That leaves the specific infeasibility in Refine HOLD B1 open.
- **Fix:** specify the fixture mode. For example, the real registry issuer could run over a recorded allowlisted capture with synthetic keys, through the real launcher-evidence interface. State why that is neither transplanted evidence nor cursor seeding. Or state that R3's positive tests depend on the live run and reconcile that with hosted validation.

**Left for later gates (Refine/JIT; not blocking)**
1. **Map each diagnostic to what closes it.** Both trials left 1 coverage-gap and 3 unreconciled-usage diagnostics across 2 claims. For each instance, Refine must name the typed evidence that closes it or confirm it is kept. In particular:
   - the `_quota(frame, None)` gap
   - the `not quota_checked` gap in `run()`
   - all three unreconciled-usage instances

   If any of these is a kept class, such as unknown remaining usage, the positive cursor is not feasible.
2. **Claim count.** Confirm that 2 claims means one each for the enrollment and measured requests, with the warmup excluded. Make that the expected count for "charged exactly once."
3. **Account authorization wording.** The account UUID comes only from the native transcript and OTLP, which are two outputs of the same CLI. `auth status` gives the organization but no UUID. So "independently match" really means corroboration across channels. The operator's choice amounts to trust on first use. Say so, and state what the operator actually checks.
4. **Replay record.** Define the "private replay record": its schema and allowlist, how long it is kept and when it is deleted, and that raw stdout and OTLP bytes are dropped once a keyed digest is taken. After a restart, quota can be checked only against its commitment, not derived again from the source. State that explicitly.
5. **Cold-read step table.** Give a numbered sequence covering arm, the enrollment dispatch, the epoch commit at the first native boundary, admission, the measured dispatch, the initial cold read, and a fresh-writer reopen. List the expected claims, cursor and diagnostics at each read. "Initial cold read" is currently ambiguous about whether it comes before or after the measured turn.
6. **Public paths only in tests.** R3 tests must not read `_read.batch.diagnostics`.

---

## #100 proposal: PASS

**Why it fixes the completion problem**
- NA-1 shows complete dependents for the branch being moved:
  - #204 → {296}
  - #270 → {204}
  - #273 → {270}
  - #272 → {273}
  - #296 → {}
- No base child depends on #204, #270, #272, #273 or #296. The only edge crossing between the two epics is #119 as a prerequisite of #296, which runs from the base outward and is allowed.
- After the move, #100's completion depends only on {119–129, 134, 135, 137, 295} plus integrated acceptance. The base release is no longer blocked.

**What is preserved**
- **#204:** stays open with its prerequisites {203, 210, 270} and its dependent {296}. It keeps the original-owner proof.
- **#296 (M09-Folded):** keeps exactly {119, 204} as prerequisites, zero outgoing edges, and the positive delivery proof.
- **#119:** prerequisites stay {118, 199, 201, 202, 203, 209, 210, 295}, with only #295 open.
- **#295:** prerequisite {210}, dependent {119}.
- **Epic #2:** its link is not touched.

**Required at activation**
1. **Name what it supersedes.** The accepted record must state that it replaces R3's "direct Epic #100 child" and "Epic #100 follow-up" parentage for M09-Folded (#296), and leaves all other R3 text in force.
2. **Give the sibling an exact identity.** Replace the "provisionally" titled sibling with an exact title and stable plan key, then record its numeric ID through native readback, as R3 required for M09-Folded.
3. **Capture the full child sets first, including closed issues.** The NA-1 #100 list appears to contain only open children: closed M-stories such as #210 are missing. So:
   - capture the complete #100 child set, open and closed, before any write
   - verify #270's children are exactly {271, 272, 273} as a precondition, not only afterwards
   - stop if the set differs, so that #269 and #282 "stay where they are"
4. **Pin the sibling's placement.** The sibling's own parent must be absent, or exactly equal to #100's parent, and it must not be linked to #2. There must be zero dependency edges between the sibling and #100 in either direction. #100's own prerequisites {101, 102} and dependent {2} must read back unchanged.
5. **Read back after each move.** Check the graph after each single reparent, so a partial write can't leave an issue with no parent unnoticed. The proposal's reconciliation rule then applies.

**Compatible enhancements (optional):**
- Record a closure manifest for #100 listing the exact remaining child set and the support-matrix entry that marks foreground Claude Agent overlap as partial coverage.
- Mirror the R3 rule that a failed verification leaves the prior graph in place.
