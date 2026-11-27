<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-e3cc08fe8be7c89350666f9039583e47"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/523/design/rubric-design.md"
artifact_commit: "321f4a60d1d1d869544d2c4a9fdd8ee2e5bc9d4e"
artifact_blob: "af48d426f0f66147dc84b9975018df8191c4362c"
artifact_digest: "sha256:282f7ac2895191588bd4a269b27cb31ac48d9f8a4949680b82c97fc72f970197"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:ccfbf0dbfc3eb87af66bc7531a32efd2cbe447123438520bcef6f325dd23dfdc"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:28.208Z"
submitted_at: "2026-11-27T06:17:31.267Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of an independent XPR review of `.aitm/stories/005/523/design/rubric-design.md` at sealed digest `sha256:282f7ac2895191588bd4a269b27cb31ac48d9f8a4949680b82c97fc72f970197` (commit `321f4a60`, blob `af48d426`).

**Read evidence.** The Read tool returned the whole revised artifact in one range, lines 1–58, ending at EOF with no truncation or omission marker. I read the author response for turn 1 in full (lines 1–53). I also checked each disposition against the artifact text myself rather than trusting the author's summary. I used no shell commands other than the submit command, and I did not recompute the digest.

**Verification of turn-1 dispositions.**

- *F1 (completion contract): resolved.* Line 30 now chooses option (a). M8 delivers the installed pipeline with fixture proofs and an explicit insufficient-evidence result for live data. Quantile evaluation and promotion or refusal are exercised on fixtures. Activation of a live-trained model is a separate readiness decision, with its own gates: MAE/bias against the baseline, interval coverage by supported kind, and the predeclared minimum sample and thresholds. This gives the 4 h quantile row (line 53) a testable acceptance that does not depend on the current corpus, where 0 of 363 records are eligible (line 36). It also agrees with line 40's baseline-only path.
- *F2 (temporal leakage): resolved.* Line 22 admits comparables for backtests, live proposals and replay only if their qualifying Close and verified label existed before the target estimate's cutoff. It pins an as-of index for each estimate and excludes late settlement, corrections and later closes. Line 31 adds the matching proof: a later Close or a late-arriving Actual cannot enter an earlier index, and the original snapshot reproduces. This covers both evaluation and reproduction, which were the two concerns raised.
- *F3 (child count): resolved.* Line 36 now names six children, including "packaging and release proof". These map one-to-one onto the six table rows (lines 50–55) and line 58's "six-child-sized".
- *F4 (C07 collision): resolved.* Lines 46 and 50 now say "#181 C07". The link `../draft.md#c07-intake-from-181` resolves from `design/` to `.aitm/stories/005/523/draft.md`, whose heading "C07 intake from #181" produces that slug.
- *Optional suggestions.* Suggestion 1 (deferred signals and lesson retrieval) is handled at line 58. Suggestions 2 (proposal schema ownership and Core boundary) and 3 (publishable-view restriction on explanations) are handled at line 23. Suggestion 4 (redundant line 42) was not taken, which is fine.

**Regression check.** The estimate total is unchanged: 3.5 + 3.5 + 3.5 + 4 + 3.5 + 3.5 = 21.5, which matches line 46. Every row is still at or under 4 h. The authority boundary (line 7), the prerequisites (line 9) and the M7 handoff (lines 40–42) are unchanged and still consistent with `story.md` and the M7 design. The new text in lines 22, 23, 30, 31 and 58 does not contradict the admission rules in lines 13–17.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Line 23 defers the Core boundary ("extension or CLI boundary selected at refinement"), and line 30 creates a separate live-activation readiness decision. Neither appears in line 36's list of items that need reviewed refinement. Adding both there, and naming who owns the live-activation decision, would keep them from being lost at child creation.

## Decision

accepted
