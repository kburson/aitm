<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9a51371a617cede221ea4d64ee80b210"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md"
artifact_commit: "5e4628835c246bed52938c76f370a0491670ad8e"
artifact_blob: "2061d457edce4d7738a00072bd0b05d44e235b47"
artifact_digest: "sha256:fb4a62308fb971dc8862d16175a0cb1c5cac3be69f96500f748895ad50ea135f"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:9cec225cc3095656c7d62b2ee43a2ad3b6ff7fc0d1605ea367ee75313ed320c6"
  identity_source: "runtime"
started_at: "2026-11-09T22:14:19.201Z"
submitted_at: "2026-11-09T22:18:57.799Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of the independent XPR review of `.aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md`, now at sealed digest `sha256:fb4a62308fb971dc8862d16175a0cb1c5cac3be69f96500f748895ad50ea135f` (commit `5e46288`, blob `2061d45`).

**Read evidence.** I read the current artifact fresh with the Read tool from line 1 with a 20-line limit. The file has 20 lines, so that one contiguous range (lines 1–20) reached EOF. A follow-up read at offset 21 confirmed the file is 20 lines. Nothing was truncated or replaced by an omission marker. I read the author's turn-1 response (`author-response-1.md`, lines 1–53, EOF). I checked each disposition against the revised artifact text, not the author's summary, using my turn-1 response (F1–F3, O1–O4) as the baseline. Only the join (turn 1) and submit commands were available. I did not rejoin, run Git or inspect product source. Product source is not checked out in this planning worktree.

**Disposition verification.**

- **F1 (identity rule for reused evidence) — resolved.** Line 13 now allows only early authorization, costs and original provider-native inputs to carry forward with their original provenance. Reused provider inputs must be reprocessed with the repaired wheel. The line says explicitly that no old-wheel ledger row, cursor, status, heartbeat, rehearsal outcome or receipt field qualifies the repaired release. Every mandatory collector-produced proof must be recreated with the repaired merge tree and wheel. That is the separation required change 1 asked for, and it agrees with line 9's merge-tree and wheel verification. The amendment also adds that the first diagnostic lacked the required pre-poll capture time, so that actual case is repeated. This tightens the identity rule rather than loosening it.
- **F2 (cap and forecast anchor) — resolved.** The new "Cumulative forecast" section (line 19) sets the U04 repair, focused review and locked verification at up to 0.75 agent-hour on top of earlier recorded work. The resumed U11 non-workload qualification gets up to 2.5 agent-hours within the existing 3.5-hour non-workload portion. Both are charged cumulatively to each existing leaf allowance, and the 0.5 agent-hour controlled workload allowance is also cumulative. Observed earlier intervals are kept as observations without inventing engagement time: about 35 minutes of U04 implementation, about ten minutes of U11 to diagnosis, and 113 seconds from the first live marker to diagnosis. The stop rule now has a concrete anchor: "Stop and replan before a forecast overrun." Line 15 still keeps the four-hour leaf caps and the 48.5-hour epic.
- **F3 (route condition) — resolved.** Line 7 now takes reading (b). The zero-or-one-LF tolerance applies to every otherwise exact marker wrapper that reaches the existing supported Codex scanner and adapter route. The scanner still requires its already approved client and format, and the Desktop client is cited only as the source that exposed the shape. No route witness is introduced, and no provider or client admission is widened. Generic stripping and arbitrary-code parsing remain forbidden.

**Optional suggestions.**

- O1 (pin the base) was adopted. Line 13 reopens #88 on exact protected trunk `c2f3582d07d0f3dfeb680ab565fb3a5c5339d2ac` and requires a fresh pin for any remote base drift.
- O2 (explicit identity comparison) was substantially adopted. Line 7 now says to "leave the remaining canonical wrapper, typed command and opaque receipt validation unchanged", which, together with "only as carrier framing", is a sufficient check for the source reviewer.
- O3 (cover both observed calls) and O4 (repaired-wheel version distinctness) were not adopted. Both were optional. Line 13's rule to recreate every mandatory proof on the repaired tree and wheel, and line 9's wheel verification, already cover the identity concern behind O4.

**Re-verified unchanged scope.** On the current bytes I re-checked the remaining scope:

- U04 ownership is still limited to the Codex adapter and its tests (line 7).
- RED, GREEN, the read-only original-record proof, the full serial locked suite, independent source review and protected-trunk delivery are all still required (line 9).
- The SAR, SPR and XPR gate, the preserved prior U04 acceptance with a separate repair receipt, and the fresh reviewed JIT for #96 remain (line 13).
- The isolated proof and rehearsal still come before production installation, and the full real receipt must be validated before #83 closes (line 13).
- The project identity and eventual ledger are the same, and Core #2 stays excluded (line 13).
- Lifetime scope, metrics, installed command and the C44 handoff are unchanged (line 15).

The package remains the permanent collector. The SAR and independent SPR records for these exact bytes are still not visible in this worktree. Line 13 makes them a gate for the author to close; they are not a defect in the text.

**Observation (not a finding).** Line 19 says the forecasts "fit the remaining caps" and that prior U04 review and coordinator verification are "tracked separately". I cannot check the recorded prior U04 totals from here. The source reviewer and the JIT should confirm the cumulative U04 figure against the four-hour cap when #88 reopens.

## Findings

None. F1, F2 and F3 from turn 1 are resolved in the current bytes, and the revision introduced no new defects.

## Required changes

None.

## Optional suggestions

1. **O3 (carried forward)** — The read-only proof could show that both observed single-line calls (line 3) join correctly, or record why only the first is in scope.

## Decision

accepted
