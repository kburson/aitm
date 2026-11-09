<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-7a70fe296924a292446e04764a152732"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md"
artifact_commit: "38749071f4c603340bae8ea57ee27514ffada22a"
artifact_blob: "8f0d942be29f98c7f70624d8df822919dd49b5d2"
artifact_digest: "sha256:4b45a8781ddd8e527affb4219b80c6fc0106e3bc87c9091843506e82c2a89f51"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:244e5d7d1a1fb132a5c9cc1aafdf5abe671f403f4dc35b7fa8b82eb3ade730eb"
  identity_source: "runtime"
started_at: "2026-11-09T22:41:37.617Z"
submitted_at: "2026-11-09T22:46:19.687Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of the independent native XPR review of `.aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md` at sealed digest `sha256:4b45a8781ddd8e527affb4219b80c6fc0106e3bc87c9091843506e82c2a89f51` (commit `3874907`, blob `8f0d942`).

**Read coverage.** I read the revised artifact fresh with the Read tool in two contiguous ranges of at most 20 lines: lines 1–20, then offset 21 with limit 20, which returned lines 21–23. `wc -l` reports 23 lines, so the second range reached EOF. Coverage is complete. No line was truncated or replaced by an omission marker. I also read author response 1 in full (lines 1–53) and my turn-1 response.

**Other context checked.**

- `.aitm/stories/000/87/events.jsonl`, all 24 lines' `ts`/`from` fields via grep, to check the U03 window derivation.
- The U11 and workload figures, recomputed from the artifact's own stated inputs.

Only the submit command and read-only file tools were available. I could not see the private native records, the 13 retained sources or the scanner source. The enumerated key sets therefore rest on the author's statement that they were compared with all 13 retained startup shapes.

**Disposition verification.**

- **F1: resolved.** Line 7 now requires exactly one enqueue, one dequeue, one hook-success attachment and one hook-additional-context attachment. They must be contiguous, in that order, and immediately followed by the authenticated first user origin. Any repeat, reorder, omission, extra row or incomplete chain keeps the hold. Exclusion applies only once the complete origin is authenticated. Untimed bookkeeping is explicitly unchanged and does not break timed contiguity. Line 15 adds negatives for: duplicated or reordered rows; a missing queue row or missing additional-context; a wrong origin parent; and a complete prefix at EOF with no verified origin and zero committed frames.
- **F2: resolved.** Line 9 closes both attachment top-level key sets (12 common keys, plus `rendered` and `renderedRole` on additional-context only). It also closes both nested hook objects, with typed fields. Any extra top-level or nested key keeps the hold, and line 15 adds the "unexpected attachment keys" negative. The envelope includes `cwd` and `gitBranch`, but line 9 still says these records supply no checkout and that hook checkout is never authority. Checkout authority is therefore unchanged.
- **F3: partly resolved.**
  - *U11 bound.* 60 + 20 + 10 minutes = 1.5 h. The span from 21:44:54 to 22:39:40 UTC is 54 m 46 s, so 60 minutes covers it. 1.5 + 2.0 = 3.5 h, which equals the non-workload portion exactly.
  - *Workload interval.* 112.962016 + 402.047576 + 5.024335 = 520.033927 s, which rounds up to 520.034 s. 1,800 − 520.034 = 1,279.966 s. The derivation now appears in the artifact.
  - *U03 within cap.* Line 21 now states that the 0.75 h falls within the existing 3.5-hour cap.
  - *U03 earlier-work bound.* This bound is arithmetically inconsistent (F4 below).

**Previously verified points.** These remain sound in the revision: the diagnosis pin, U03 ownership and the exclusions on line 11, the cursor and continuity rule, the RED/GREEN and SQLite proof, wheel rebuild, evidence regeneration and fresh-native rules, rehearsal before production install, and Core #2 exclusion. The new count-only check of the 13 sources, and the rule that a changed hook configuration keeps the hold and returns to Planning, meet my turn-1 optional suggestions 1 and 3.

## Findings

1. **F4 — The U03 earlier-work bound does not follow from its own derivation (low–moderate, estimates).** Line 21 says U03 had "two roughly 29- and 13-minute delivery windows". It then bounds earlier work "by 1.5 agent-hours by allowing three times their combined calendar interval plus rounding." #87 `events.jsonl` confirms two separate windows:
   - develop from 16:49:36 to 17:18:47 UTC (29 m 11 s);
   - develop from 18:04:48 to 18:17:33 UTC (12 m 45 s).

   Together they last about 42 minutes, and three times that is about 126 minutes, or 2.1 h. That exceeds the stated 1.5 h, so the rule as written gives a larger bound than the one recorded. The cap still fits with the correct figure: 2.1 h, or 2.25 h rounded, plus 0.75 h is at most 3.0 h of 3.5 h. The fault is the stated number and derivation, not the feasibility. This is the checkability gap F3 asked to close, so the published bound must match its own rule.

## Required changes

1. **(F4)** In line 21, make the U03 bound match its derivation. Either:
   - state a conservative earlier-work bound of at least 2.1 h (for example 2.25 h), and show that it plus the 0.75 h reserve stays within 3.5 h; or
   - keep 1.5 h and replace the "three times … plus rounding" rule with a derivation that actually yields it.

## Optional suggestions

1. Line 3 calls the held startup segment "cwd-free". Line 9 now shows that both attachments carry `cwd` and `gitBranch`; only the queue rows lack checkout, as the diagnostic says. Consider saying that the queue rows were cwd-free, or that the segment had no authenticated checkout, so the two lines agree.
2. Line 9 says "Use the observed subtype values" for the attachment `type` and nested `type` fields. If publishing them is acceptable, name the exact literal values, as `SessionStart` already is, so the source reviewer can check the matcher against the plan without the private records.

## Decision

revisions-requested
