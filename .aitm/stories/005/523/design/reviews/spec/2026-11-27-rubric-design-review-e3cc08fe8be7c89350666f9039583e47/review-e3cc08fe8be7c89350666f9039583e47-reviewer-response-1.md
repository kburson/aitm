<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-e3cc08fe8be7c89350666f9039583e47"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/523/design/rubric-design.md"
artifact_commit: "8862808e2dd2062df1c0d2e156e6711c2dbaabbb"
artifact_blob: "f995dee4153dfa571e63ab7ddbaa6e6ae7cc7f92"
artifact_digest: "sha256:c1b737d1b81f0627f046b2bea35e5e1561336a5af5f8ea0165a2e0dd65d2c3d6"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:ccfbf0dbfc3eb87af66bc7531a32efd2cbe447123438520bcef6f325dd23dfdc"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:28.208Z"
submitted_at: "2026-11-27T06:14:52.890Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent XPR review of `.aitm/stories/005/523/design/rubric-design.md` at sealed digest `sha256:c1b737d1b81f0627f046b2bea35e5e1561336a5af5f8ea0165a2e0dd65d2c3d6` (commit `8862808e`, blob `f995dee4`).

**Read evidence.** The Read tool returned the whole artifact in one range, lines 1–59, ending at EOF with no truncation or omission marker. This is the first turn of this review ID, so there are no prior dispositions to check. For context I read the following files in full: the graduated draft `.aitm/stories/005/523/draft.md` (lines 1–40, which includes the "C07 intake from #181" section), `.aitm/stories/005/523/story.md` (lines 1–39), and the M7 design `.aitm/stories/005/522/design/history-import-design.md` (lines 1–65). I also ran a targeted search for "C07" across `.aitm`. I used only the join and submit commands and no other shell commands. I did not recompute the digest.

**Verified as sound.**

- *Authority boundary (line 7).* The plugin only advises. Core keeps estimate recording, state guards and the four-hour leaf limit. This matches the draft's "Feeds Refine and Plan exit guards" without giving the plugin any write authority.
- *Prerequisites (line 9, line 42).* The native blockers #51, #72, #229 and #522 match `story.md` `blocked-by: [51, 72, 229, 522]`. The #228 substitution rule (a complete comparable pair plus an explicit edge reconciliation) matches `story.md` lines 33–35.
- *Label admission (lines 13–17).* Matching story/attempt, phase, role/actor, boundaries and measurement basis, and excluding rollups, incomplete or disputed Actual, owner wait, idle time and late revisions, faithfully carries forward the #181 C07 intake (draft line 32). It keeps exclusion reasons, which matches the draft's "available for diagnosis outside calibration". It also allows no-Cost pairs (line 9, line 31), which matches "Verify a complete pair can qualify without usage".
- *M7 handoff alignment (lines 38–42).* The pinned items (manifest location/digest, schema, scope/cutoff, dispositions, source digests, validation receipt, read fixture) match M7's "Handoff receipts" delivery list (M7 line 50). The anchor `#handoff-receipts` resolves to M7 line 46. M8 keeps the comparability and sufficiency decision, which matches M7 lines 36 and 50.
- *Feature hygiene (line 15).* Only features available at estimate time, a pinned estimate phase, and treating trips, expansions and pivots as outcomes are the right way to prevent label leakage. Separating owner pivots from planning error carries out the draft's "human pivots (recorded separately …)".
- *Estimate arithmetic (lines 48–56).* 3.5 + 3.5 + 3.5 + 4 + 3.5 + 3.5 = 21.5, which matches line 46. Every row is at or under 4 h. Rank 270 follows M7's 260, which is consistent with line 58.

**Areas needing revision.** The main gap is what "done" means for M8 given the design's own observation that 0 of 363 records are eligible. Without an explicit sparse-corpus completion contract, the quantile and promotion children have no defined acceptance (F1). Retrieval-based evaluation can also leak future outcomes unless comparables are time-bounded (F2). Two smaller consistency items affect child creation (F3, F4).

## Findings

1. **F1 (required): Completion criteria are undefined when the corpus is insufficient, which line 36 says is the current state.** Line 36 records zero eligible records among 363. Line 40 says a reproducible M7 export "can legitimately yield too few qualifying labels" and that learned calibration then stays unavailable. Line 30, however, makes MAE/bias comparison, interval coverage and per-kind results release gates. Line 22's baseline is "by supported story class", and with zero labels no class is supported. The estimate (line 53) budgets 4 h for "Quantile model and held-out evaluation" with no statement of what that child proves if real data cannot support a holdout. As written, an implementer cannot tell whether M8 closes with:
   - (a) the full pipeline proven on synthetic or fixture corpora, with live calibration left as a gated later activation; or
   - (b) live calibration demonstrated on real eligible data, which would make M8 blocked until enough native Close outcomes accumulate. That is an unlisted dependency on elapsed delivery time.

   The design must pick one and state it in the release gates. If (a), the gates need fixture-proof acceptance for the quantile and promotion paths and an explicit statement that the numeric thresholds are set later. If (b), the design must name the data-accumulation dependency and rethink the rank and estimate. Line 58 ("Set the approved sample and evaluation rules before model promotion") does not settle this, because it doesn't say whether promotion is inside M8's scope.

2. **F2 (required): Comparable-story retrieval has no temporal cutoff, so evaluation and live proposals can leak outcomes.** Line 29 groups related stories and attempts to prevent leakage, and line 15 restricts features to what was available at estimate time. Neither constrains the *retrieval index*. During backtesting, a target's comparables, and their Actual, must come only from stories whose qualifying Close preceded the target's estimate time. Otherwise the baseline and the kNN-style retrieval (draft line 21) are scored with information that did not exist at estimate time. That inflates the line 30 comparison against the baseline. The same rule matters for reproducing earlier proposals (line 24): reproduction must rebuild the index as of that proposal's snapshot cutoff. Add an explicit "comparables admitted only if closed before the estimate cutoff" rule to step 2 or the evaluation gates, and prove it in line 31's deterministic-assembly tests.

3. **F3 (required): The decomposition lists five children but the estimate has six rows.** Line 36 lists five children: corpus admission, feature extraction and index, baseline and retrieval, quantile evaluation, and proposal and retraining loop. The table (lines 50–55) and line 58 ("six-child-sized") add a sixth: "Packaging, compatibility and release proof". Line 32's release gate needs that work, so the table is probably right, but line 36 should name the sixth child so that child creation and the JIT do not drop it or fold it into another 3.5 h row.

4. **F4 (required): "C07 comparability intake" collides with Core C07.** Lines 46 and 50 say "C07" with no qualifier. In this planning tree, `C07` also keys Core story #12 ("Committed configuration and routing anchors", `plan_key: "C07"`), which is unrelated. The intended source is the #181 slice-C item `c07-verify-estimate-comparability` (draft lines 30–36). A future reader or tooling that resolves plan keys could misattribute the 1.5 h. Write it as "#181 C07 comparability intake" and link it to the draft section.

## Required changes

1. F1: State M8's completion contract for a corpus with too few labels: either fixture-proven pipeline with live calibration gated later, or live calibration required plus the named dependency. Align line 30's gates and the 4 h quantile row with that choice.
2. F2: Add a temporal admission rule for comparables (closed before the target's estimate cutoff) for evaluation, live proposals and reproduction, and add it to line 31's proofs.
3. F3: Name the packaging/compatibility/release-proof child in line 36 so it matches the six-row table.
4. F4: Qualify "C07" as the #181 intake item at lines 46 and 50.

## Optional suggestions

1. The draft lists defects after acceptance, expansions, trips, discovered work, loop-backs and tokens/cost as training signals, plus "lessons are retrieved into the planner's context packet" (draft lines 19–21). The design narrows the target to engaged agent-hours and treats those as outcomes (line 15) without saying whether lesson retrieval and the other signals are deferred or dropped. A one-line "out of scope for M8 / deferred to …" note would keep that narrowing deliberate and traceable.
2. Line 23's "typed proposal at Refine or Plan" does not name the Core surface that consumes it, such as an extension hook or plugin contract in #72, or who owns the proposal schema. Naming it, or recording it as a refinement decision next to line 36's open items, would make line 32's "installed optional package against released Core" gate concrete.
3. Comparable story IDs and evidence surfaced in proposals (lines 7, 23) should follow M7's permitted-field and publishable-view boundary (M7 lines 20 and 25), so the plugin does not expose excluded legacy content through its explanations.
4. Line 42 restates the #228 rule from line 9 and adds nothing new. It could be dropped or reduced to a pointer.

## Decision

revisions-requested
