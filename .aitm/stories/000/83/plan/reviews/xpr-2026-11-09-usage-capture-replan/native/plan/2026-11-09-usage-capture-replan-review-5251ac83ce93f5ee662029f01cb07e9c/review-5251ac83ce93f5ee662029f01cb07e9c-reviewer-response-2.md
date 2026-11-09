<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-5251ac83ce93f5ee662029f01cb07e9c"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-replan.md"
artifact_commit: "fa3fa0f4fd68e40c0fb53c641bb8263326458088"
artifact_blob: "17114b365b823c3060e01d776ea6bb34593ced7d"
artifact_digest: "sha256:7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:be2e1af31a171c19a3157ffccc748eaf9c79acb8ac3da44acd18b46ef3aa1d6e"
  identity_source: "runtime"
started_at: "2026-11-09T15:09:08.408Z"
submitted_at: "2026-11-09T15:15:59.993Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of an independent XPR review of `.aitm/stories/000/83/plan/usage-capture-replan.md` at sealed digest `sha256:7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239` (commit `fa3fa0f`, blob `17114b3`).

**Read evidence.** A line count reports 50 lines. The Read tool returned three contiguous ranges of the current artifact: lines 1–20, 21–40 and 41–50. The last range reached EOF at line 50. No output was truncated or replaced with an omission marker. I read the prior author response `review-5251ac83ce93f5ee662029f01cb07e9c-author-response-1.md` in full (lines 1–55) and checked each disposition against the current text, not against the author's summary. The baseline plan, the design and the leaf-issue receipt were read in full during turn 1 of this review. I reused them as context and did not use any earlier review's conclusions. I still could not run commands other than submit, so I did not recompute digests.

**Verification of the turn-1 required findings.**

- **F1 (ownership): resolved.**
  - Line 18 puts the closed record and command unions and their static codec tables in `types.py`. It says ledger append consumes validated records, which makes `ledger.py` data-driven over the union, and it gives U02 ownership of command dispatch in `scopes.py`.
  - The table (lines 29–31) limits U13 and U08 to their own dispatch cases in `scopes.py`. U06 is limited to its `types.py` additions.
  - Line 38 explicitly extends the baseline Files lists. It also bars U03, U04, U05, U07, U09, U10 and U12 from editing `types.py`, `ledger.py` or inbox dispatch, and requires replanning for any unassigned edit. This removes the U03/U13 parallel race I flagged.
- **F2 (inbox recovery): resolved.**
  - The U02 row (line 28) requires consumption and disposition in the same transaction. It states the replay rule as the current recorded disposition, with pending advancing to final once, immutable final dispositions, no overwrite by conflicting bytes, and unpublished temp files ignored.
  - Line 40 adds a real-process kill after commit and before acknowledgment or retirement, with exactly-once application after restart. It also adds a torn temp publication case that checks the diagnostic and private state, and it keeps the original U12 cases.
- **F3 (U11 route and effort): resolved.**
  - Line 46 replaces baseline U11 step 1 in full and names every element U10 requires. These are hydration, two disposable children, focus and return, graduation to a disposable identity, direct and inclusive rollup, an overlapping controlled Claude review, markers on both providers in both arrival orders, participant separation, an owner binding in a dedicated worktree and a marked housekeeping action.
  - It requires U10's validator to recognize controlled elements and refuse fixture-only evidence. This matches baseline U10, which already accepts labeled controlled evidence.
  - It excludes all Core work and states a 0.5-hour forecast with a stop rule. The U11 row (line 32) moves to 4 hours.
- **F4 (QuotaEvidence): resolved.** Line 13 puts the envelope inside the two-hour U01 forecast. Line 20 adds its validation to the retained regressions. Line 34 lists the tests: exact shape, bounded values and precision, UTC, closed source vocabulary, genuine and foreign account references, and refusal of raw handles and task-burn fields.
- **F5 (ACL reach): resolved.** Line 15 extends ACL validation to the guard location, the state and its ancestry, and exposes the validator for U09. Line 42 requires U09 to validate the backup destination before writing and the restore source before accepting bytes, with a real-Mac inherited-ACL case for both. Backup stays lease-free, and restore takes the guard.

**Verification of the turn-1 optional suggestions.** All four were adopted.

- O1: line 15 makes ordinary open refuse existing state with a missing guard, and checks held descriptors against current paths.
- O2: line 24 applies the return-to-planning rule to every leaf.
- O3: line 50 lists the native #86→#90 edge, the revised issue estimates, the refreshed receipt and the reviewed #84 repair plan and JIT.
- O4: line 34 uses an approved normalized bucket label.

**Fresh full-file check.**

- *Arithmetic.* Five leaves rise by 0.5 hours each (U02, U13, U06, U08 and U11), so 46 + 2.5 = 48.5, which matches line 24. Prior hours match the baseline and the receipt, including U11 at 3.5. Every leaf is 4 hours or less.
- *Issue numbers.* #85, #86, #90, #92 and #96 match the receipt.
- *Dependency edge.* The U13→U06 edge is acyclic and adds no critical-path delay.
- *Unchanged sections.* CAS and schema (line 16), sanitized metadata and project-bound pseudonyms (line 17), and the hold and cause section (lines 5–9) are unchanged and remain sound.
- *Owner's scope.* The resume gate (line 50) keeps the #83 activation gate before Core C01. Lines 46 and 50 keep Epic #2 unstarted. Line 3 preserves the lifetime design, and line 46 keeps the C44 consumer seam, so the same collector and ledger continue for the life of AITM.
- *New text.* No new contradictions. Line 28's "Wire exact admission and replay in ledger.py only where needed" agrees with line 18, because U02 is the single `ledger.py` owner after U01.

No required changes remain.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **O5 (owner of missing-guard recovery).** Line 15 says existing state with a missing guard "requires explicit recovery", but no leaf owns that procedure and no command covers it. A short note would close the gap. For example, the U10 runbook could document a manual, guard-verified recovery that validates project and key identity first, with no new CLI command. This affects operations and is not a correctness gap, since ordinary open already refuses.
2. **O6 (no headroom on capped leaves).** U12 (line 40) and U09 (line 42) take on new proof obligations at an unchanged 4 hours, which is already their cap. Line 24's universal stop rule covers this. Their JITs could still name these added cases explicitly so that any deviation shows up early instead of at the cap.
3. **O7 (temp-file lifecycle).** U02 ignores unpublished temporary files (line 28), and U12 proves they are not consumed (line 40). Neither sets a retention or cleanup rule. A collector that runs for the life of AITM should not accumulate orphaned private files in the inbox indefinitely. A bounded cleanup rule, such as age plus guard-held deletion, with a sanitized diagnostic would fit U02's existing scope.

## Decision

accepted
