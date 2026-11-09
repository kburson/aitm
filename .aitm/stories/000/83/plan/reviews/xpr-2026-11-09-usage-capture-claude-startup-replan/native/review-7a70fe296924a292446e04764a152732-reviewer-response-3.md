<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-7a70fe296924a292446e04764a152732"
role: "reviewer"
turn: 3
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md"
artifact_commit: "dca7d8f4446b229fd64b46a1251e32d7d8597af2"
artifact_blob: "17969b7dab995ce5a1f63acc5473ac25b246c6fb"
artifact_digest: "sha256:bbfbae3508646b570345eeaadbb13ad0e186edce13cc3d1f02448761ebf157bc"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:244e5d7d1a1fb132a5c9cc1aafdf5abe671f403f4dc35b7fa8b82eb3ade730eb"
  identity_source: "runtime"
started_at: "2026-11-09T22:41:37.617Z"
submitted_at: "2026-11-09T22:47:21.007Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 3 of the independent native XPR review of `.aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md` at sealed digest `sha256:bbfbae3508646b570345eeaadbb13ad0e186edce13cc3d1f02448761ebf157bc` (commit `dca7d8f`, blob `17969b7`).

**Read coverage.** I read the revised artifact fresh with the Read tool in two contiguous ranges of at most 20 lines: lines 1–20, then offset 21 with limit 20, which returned lines 21–23. `wc -l` reports 23 lines, so the second range reached EOF. Coverage is complete. No line was truncated or replaced by an omission marker. I also read author response 2 (lines 29–51, EOF; lines 1–28 are protected frontmatter).

Only the submit command and read-only file tools were available. I did not run Git or inspect private native records or the scanner source.

**Disposition verification.**

- **F4: resolved.** Line 21 now bounds earlier U03 work at 2.25 agent-hours and shows the derivation:
  - The two windows total about 42 calendar minutes. In turn 2 I confirmed them against #87 `events.jsonl`: 16:49:36–17:18:47 UTC and 18:04:48–18:17:33 UTC.
  - Three times 42 minutes is 126 minutes, rounded up to 135 minutes, which is 2.25 h.
  - With the 0.75 h repair reserve, the total is 3.0 h, within the existing 3.5-hour U03 cap.

  The stated rule now yields the stated bound.
- **Turn-2 optional suggestion 1: adopted.** Line 3 now says the held timed segment "began with two queue rows without a checkout". This agrees with the diagnostic and with line 9, where the attachments carry `cwd` and `gitBranch` that are never used as authority.
- **Turn-2 optional suggestion 2: adopted.** Line 9 now requires the literal top-level `type` `attachment`, and nested `type` `hook_success` or `hook_additional_context` respectively. Together with the closed key sets, typed fields, `SessionStart`, the root-session and non-sidechain requirements, and the parent chain, this gives the source reviewer an exact matcher specification. The private records are not needed to check it.

**Unchanged and still sound.** I re-read the full text. Nothing else changed in substance since turn 2, and the following remain intact:

- the exact-cardinality, ordered, contiguous prefix, with exclusion only after the complete origin is authenticated (line 7);
- the closed queue and attachment envelopes, and the rule that any extra key keeps the hold (lines 7–9);
- no checkout, enrollment, usage, quota, scope or watermark from matched rows, with cursor continuity still authenticated by their original bytes and ordinals (line 9);
- the ownership limits and the ban on bypasses (line 11);
- RED/GREEN with the expanded negative set, including the case of a prefix at EOF with no origin and zero committed frames; the SQLite proof on the original retained source; restart, archive and prefix continuity; a protected normal PR with merge-tree verification; and the count-only check over the 13 retained sources (line 15);
- SAR, SPR and XPR gating; #87 reopening on `e65c86b…`; wheel rebuild and regeneration of collector evidence; no qualification from old collector state; rehearsal before production install; and Core #2 kept outside execution (line 17);
- U11 at 1.5 + 2.0 = 3.5 h, and the workload sum of 520.033927 s rounded up to 520.034 s, leaving 1,279.966 s of the 1,800 s cap (lines 21–23).

**Gate observation (not a finding).** No SAR or SPR review directory for this amendment is visible in this worktree. Line 17 already requires both, together with native XPR, on exact bytes before #87 reopens. The author must close that gate.

## Findings

None.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
