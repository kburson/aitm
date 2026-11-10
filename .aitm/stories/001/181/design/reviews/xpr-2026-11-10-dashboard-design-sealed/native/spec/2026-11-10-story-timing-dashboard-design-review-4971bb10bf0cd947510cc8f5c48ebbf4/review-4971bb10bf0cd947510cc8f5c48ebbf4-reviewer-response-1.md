<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4971bb10bf0cd947510cc8f5c48ebbf4"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/181/design/story-timing-dashboard-design.md"
artifact_commit: "307c2577e2848331f29bbd16402d82e5d95a3403"
artifact_blob: "9da51a9bfa253bbbd107bf712e7c581d737d49af"
artifact_digest: "sha256:3edf5b36d09c7832c31d69fdbce42391d28aecdaccf21d8bed3fbc25b84b6ccb"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:349b0f6682b403a7d39e3a413ed147008f5b5220a8e947a14d1ba9881a0c1098"
  identity_source: "runtime"
started_at: "2026-11-10T20:41:33.197Z"
submitted_at: "2026-11-10T20:42:36.976Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Reviewed the complete artifact `.aitm/stories/001/181/design/story-timing-dashboard-design.md`, lines 1–55 (full file), at blob `9da51a9bfa253bbbd107bf712e7c581d737d49af`.

The design is coherent and close to acceptable. Slicing (A capture/snapshot, B static dashboard, C product integration) has clear gates. Ownership boundaries with Core and the #100 monitor are explicit. The metric contract (Elapsed, Actual, Owner wait, Cost, Calibration) holds together. I recomputed the example fixture independently: elapsed 09:00–11:45 = 2h 45m; working wall-time union 09:00–11:00 + 11:30–11:45 = 2h 15m; Actual 1.5 + 1.5 + 0.25 = 3.25 agent-hours; owner wait 30m. All of these match the text. I checked one supporting fact because it bore on a potential finding: `attachments/2026-11-10-actual-backfill.md` line 3 confirms that companion "Actual coverage" board fields already exist. Slice A's projection therefore adds no new board field, and I raise no finding there.

One material contract gap remains. The usage input to the snapshot command is described as a single identified receipt, but usage receipts are stored per attributed story. As a result, the determinism key and the Cost selection rule are underspecified (Finding 1).

## Findings

1. **Usage input is one receipt in the command contract, but the storage rule makes it many per-story receipts (material).**
   - Line 25 says a usage receipt is stored "under the attributed story's `attachments/timing/` using the same registration rule". That rule (line 19) splits multi-story batches by proven scope into one receipt per story. A monitor usage report covering ten stories would therefore become up to ten registered receipts.
   - Line 25 also says "The snapshot command reads a pinned commit and an optional identified usage receipt". Line 13 stores a single "usage input identity" and shows "the separate usage cutoff and pricing basis" once at snapshot level. Acceptance 1 (line 49) keys determinism on "the same planning commit, as-of time and usage receipt".
   - Failure scenario: a pinned commit holds registered usage receipts for several stories, possibly from more than one report with different cutoffs or rate versions. An implementer has two readings, and both are wrong:
     - (a) The command takes one receipt. Cost then appears for only one story, and every other row is Unknown even though eligible evidence exists.
     - (b) The command reads every registered usage receipt. That mixes cutoffs and pricing bases under one header, contradicting line 41's "avoid claiming a common cutoff across mismatched sources". The "usage input identity" also stops identifying the input, so Acceptance 1's determinism key is no longer sufficient.
   - Two parts of the contract are also undefined: which receipt wins when one story has usage receipts from two reports, and how a correction or supersession of a usage receipt is selected.

## Required changes

1. Define the snapshot's usage input as a set selector, not a single receipt. For example: a usage report/sequence identity (the "original sequence or report ID" already listed on line 25), resolved to that report's registered per-story receipts in the pinned commit, with one shared cutoff and pricing basis. Store that selector and the resolved receipt digests as the "usage input identity" in the JSON. State that rows with no receipt from the selected report show Cost Unknown. Also state that receipts from other reports in the same commit are ignored for that view, or are rejected if they overlap. Update line 13, line 25 ("an optional identified usage receipt"), and Acceptance 1 (line 49) to use the same term. In Acceptance 1 or 5, add a check that a commit containing usage receipts from two different reports produces a single-cutoff view.

## Optional suggestions

1. In the example fixture (line 35), state that child A, child B and the direct epic work are distinct logical actors. The 3.25 agent-hours figure depends on that: under the line 30 rule, one actor working A and B concurrently would be an unresolved conflict, not additive.
2. Acceptance 1 says "identical regeneration outside the checkout" but does not say whether that covers the HTML as well as the JSON. If the HTML should be byte-identical for the same inputs, say so and forbid wall-clock generation stamps. Otherwise, limit the claim to the normalized JSON.
3. Line 13 requires as-of ≥ the committer timestamp and admits only facts "recorded by the supplied as-of". Consider saying what happens when a receipt in the pinned tree has a recorded UTC later than the commit timestamp, for example because of clock skew. Such a fact is present in the commit but ineligible at the minimum as-of. Either outcome is fine; stating it avoids a silent coverage gap.

## Decision

revisions-requested
