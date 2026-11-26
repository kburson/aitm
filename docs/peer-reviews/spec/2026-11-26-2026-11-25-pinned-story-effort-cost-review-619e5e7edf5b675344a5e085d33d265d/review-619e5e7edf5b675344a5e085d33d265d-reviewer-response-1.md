<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-619e5e7edf5b675344a5e085d33d265d"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md"
artifact_commit: "9806f13c39e573ec13d8e0cce61875f657feac15"
artifact_blob: "8c3c77a102d2ee06f78f59c47c8b34750adbf426"
artifact_digest: "sha256:cf54ff6ed44fd650774705cb9b88911c4abe6d80e164918b5f5edf57c4079fda"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:d05378fe03130750b1936004faa46835ce3f83bc69d77971dde2756200e357bb"
  identity_source: "runtime"
started_at: "2026-11-26T02:06:17.062Z"
submitted_at: "2026-11-26T02:06:45.486Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The design is coherent and fails closed in the right places. It pins inputs by Git tree, derives a content-addressed report ID, freezes rendered output, and separates partial report publication from Project Cost projection. I reviewed only the design file. I did not open the linked #443, #181 or #455 documents, so reuse claims about them are unverified. Four gaps leave behavior ambiguous or unverifiable as written.

## Findings

1. **Planning commit versus cutoff is unconstrained.** Inputs are resolved only through the pinned planning commit. Receipt eligibility is decided by observation time against the cutoff. The design never requires the commit to contain all evidence observed at or before the cutoff. A commit older than the cutoff yields a report that omits receipts. Those receipts are not visibly excluded, because exclusion rationale is only defined for receipts found in the tree. Only the coverage roster could expose the gap, and the roster has the same dependency (finding 2).

2. **The coverage record and its `core.evidence.recorded` fact have no stated ordering relative to the pin.** The reporter "reads it from the same planning pin when one exists". The record is "linked" by a fact that binds story, path, cutoff and digest. The design does not say whether that fact must be reachable from the pinned commit. It does not say how the reporter finds the fact for a given story and cutoff. It does not say what happens if the fact exists but the file is absent from the tree, or the reverse. These cases should be named "no record" or "hold", and each needs a test.

3. **Reopen discovery is unspecified.** Reopen takes a caller-supplied ID against "the exact Git artifact", and the published artifact commit is pinned separately from the ID. The user outcome says an owner can open a published report. The design does not say where the ID and artifact commit are recorded for the owner or agent. Examples are the story file, the Cost registration or a report index. Without that, reopen works only for a caller who already holds both values.

4. **Acceptance coverage for the eligible Project Cost path depends on evidence that may not exist.** The design says the repo example uses an actual completed story, "including incomplete coverage where that is all the evidence supports". The scenarios require validating both an eligible candidate and a held case through the #181 dashboard contract. If the real story can only produce a hold, the eligible case needs a named synthetic fixture. The design should say so, and say which story is the real example. #461 is implied but never named.

5. **Several scenario edges in the prose are not in the scenario list.** These are the half-open window edge for a bounded turn, the inclusive cutoff boundary on observation time, and a turn crossing a window edge shown as a gap. Also missing are the GPT-6.2 Sol short- versus long-context band reconciliation and the conflict-holds-publication case. The refusal list and the privacy and bounded-read canaries are present.

## Required changes

1. Add a rule for the relationship between the planning commit and the cutoff. For example, require the commit to be at or after the cutoff on the planning branch. Alternatively, state that a tree missing evidence cannot be detected except through the roster, and make the roster mandatory for any Project Cost projection. Add a test.
2. State whether the evidence fact must be in the pinned tree. State how the reporter locates the fact and record for a story and cutoff. State the outcome for fact without file, file without fact, and digest mismatch.
3. State where the report ID and artifact commit are recorded for later discovery, or explicitly make the caller responsible and say so in the user outcome.
4. Name the real example story. State that the eligible Cost candidate is proved with a fixture if the real evidence cannot reach completeness.
5. Add the missing edge cases from finding 5 to the acceptance scenarios.

## Optional suggestions

1. Split the two long paragraphs in "Immutable inputs and report identity" and "Coverage and time" into numbered requirements. That would let the independent review and the tests trace to them.
2. Clarify whether the "frozen human-readable output" is inside the digested envelope. The text says so, but the ID derivation wording ("before the ID is attached") should say explicitly that the ID is not self-referential.
3. State a size or count bound for the "bounded input reads" canary, so the test has a pass or fail threshold.

## Decision

revisions-requested
