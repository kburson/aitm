[09:25:49]
PASS

This PASS covers only the amended plan as a design for delivering M08b4c. It does not support closing #210, starting #204 or starting #119. The plan lists four cases as unsupported:
- undisputed single-owner holds
- GAP-only or mixed outcomes
- same-project content disputes
- legacy, missing-rival and unrelated-diagnostic cases

I wasn't given the accepted #210 scope text, so I can't say whether any of these cases is a required member of #210. Closure stays undetermined until that check is done.

## Previous findings

| # | Finding | Status |
|---|---|---|
| 1 | Output type | Met. Each side requires `custom_tool_call_output` (row 249), and `function_call_output` is a negative for each side. |
| 2 | Effective-view consumers | Met. Consumers of `view`, `_timeline` and `prior.held` are listed. The private issuer lives only inside the journal transaction: it is never persisted, cached or returned by the legacy `view()`. |
| 3 | Method #204 extends | Met. `settle_disposition` calls `_build_settlement_change`. #204's folded intent goes into that payload in the same sequence. `record_disposition` stays frozen. |
| 4 | Narrowed scope vs closure | Met in substance, with condition A below. Each unsupported case must be checked before closure. A proposed GAP stays held and gives no effective GAP or progress. |
| 5 | Supported shape | Met. Project IDs, command/grant IDs and physical sources must be distinct. `_claim` makes a same-project ownership dispute impossible. The positive fixture uses two registered projects. |
| 6 | Per-side negative matrix | Met. The full matrix runs on each side while the other side is valid, including expired hold vs expired grant. Retained condition 5 is restated. |
| 7 | Late same-turn usage mechanism | Met. The turn closes at `task_complete`, so a later same-turn row raises `COVERAGE_GAP` and the journal refuses to advance. This is tested after commit, on replay and after restart. If the parser behaves differently, work stops for a bounded amendment. |
| 8 | v5 upgrade trigger and old reader | Met. v5 is created only at the first committed pair, in the same transaction. Read-only and v4 paths never migrate. The old binary refuses v5 and rollback means restoring the pre-upgrade store. `as_of` before the upgrade is byte-equivalent to v4. |
| — | Clarifications | Met. A competing legacy resolution stalls that source without regressing anything. Behaviour after the grant expires is stated. 6abd6f4 is in review scope and keeps the legacy pins. Snapshot bytes are compared at issuance and at commit, with no single shared issuer. Rows 254/255 supersede the earlier mismatched sample. |

## Binding conditions

These are readings of the existing text plus tests that fit inside steps 1–3. They don't need another review.

- **A. Closure and sequencing.** The opening line "#204 and #119 follow verified delivery" is governed by the conditional rule in the scope section. Delivering M08b4c does not complete #210.
  - "#210 and its blockers stay open" means #210 stays open and its dependents stay blocked: #119 as well as #204.
  - "Verified completion" in step 4 means #210 has been verified complete after that check.
- **B. Tests the plan states but does not list.** Add these to step 3:
  - After commit, a competing legacy resolution, or a v4 proposal on a hold the pair already settled, stalls new routing for that source. No cursor regresses and the pair history is unchanged.
  - After commit, the original hold expiring does not undo the release.
  - A corrupt or mismatched pair found on load stalls that source.
- **C. Retry after commit.**
  - Say whether settlement uses up the grants. If it does, the "exact retry returns the same sequence" branch can never happen, so keep just one rule.
  - Refusing an expired or consumed grant must be distinguishable from "never committed". Test that `as_of` returns the pair after that refusal.
- **D. Consumer list.** The plan says `prepare` and `_fresh_view` are the only consumers of `view()` "for admitted routing". Final source review must confirm there are no other production callers of `view()`, or list any non-routing callers as reading the original snapshot.
- **E. Rollback claim.** The plan says the old binary refuses a v5 file. Prove it with a test or a cited existing unknown-version check.
- **F. Approval record.** Link the owner's approval of the completion anchor (the recorded #210 completion-receipt follow-up) in the delivery record.
