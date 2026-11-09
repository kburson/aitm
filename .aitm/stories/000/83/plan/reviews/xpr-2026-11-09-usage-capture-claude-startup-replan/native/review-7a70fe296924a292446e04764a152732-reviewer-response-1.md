<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-7a70fe296924a292446e04764a152732"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md"
artifact_commit: "d2cd73e5188da7d6741ff89c136edfcf9bbe941d"
artifact_blob: "624c3ad4ded6aa3f59352ec4268efaca42e0bf61"
artifact_digest: "sha256:3dcc535fbb89c26cfcf5999f0e649f7c9b25fbeeb92f432dcec65b319f9b65f3"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:244e5d7d1a1fb132a5c9cc1aafdf5abe671f403f4dc35b7fa8b82eb3ade730eb"
  identity_source: "runtime"
started_at: "2026-11-09T22:41:37.617Z"
submitted_at: "2026-11-09T22:43:50.529Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent native XPR review of `.aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md` at sealed digest `sha256:3dcc535fbb89c26cfcf5999f0e649f7c9b25fbeeb92f432dcec65b319f9b65f3` (commit `d2cd73e`, blob `624c3ad`).

**Read coverage.** I read the artifact fresh with the Read tool in one contiguous range: offset 1, limit 20. `wc -l` reports 19 lines, so that range (lines 1–19) reached EOF. Coverage is complete. No line was truncated or replaced by an omission marker. This is the first turn of this review ID, so there are no earlier author dispositions to check.

**Context read.** I also read the following, only to verify the artifact's claims:

- `.aitm/stories/000/96/attachments/claude-startup-diagnostic.md`, lines 1–7 (EOF);
- the cumulative forecast in `usage-capture-desktop-marker-replan.md`, lines 15–19;
- `leaf-stories.md` rows U03 (3.5 h) and U11 (4 h);
- the #87 estimate lines and `source-review.md` line 7, which records about 21 implementer minutes;
- the #96 estimate lines and `desktop-marker-recovery-jit.md` line 11, which sets a recovery forecast of at most 2.5 remaining non-workload hours;
- `83/attachments/agent-usage.md`, via targeted grep;
- the earlier desktop-marker XPR turn-1 reviewer response, only to match format.

My tools were limited to the join and submit commands plus read-only file tools. I did not run Git, inspect the scanner source (product source is not checked out in this planning worktree), or see the private native records. Claims about the native row shapes rest on the artifact and the diagnostic.

**Gate observation (not a finding).** This worktree holds no SAR or SPR review directory for this amendment. Line 15 already makes SAR, independent SPR and native XPR on exact bytes a precondition. The author must close that gate before reopening #87. The text itself is not defective.

**Verified as sound.**

- *Diagnosis and evidence pin.* Line 3 matches the diagnostic. Both name protected merge `e65c86b…` (PR #98) and Claude Code 2.1.318 format-1. Both say two timed queue operations, then two timed SessionStart attachments, then the first checkout-bearing user row. The outcome matches: 24 projected frames, zero committed, one held source, zero admitted usage, and look-ahead reaching the target at native ordinal 33. Both also say the same ordering appeared in 13 retained sources. The diagnostic keeps native scope proof separate from ledger admission. It also records that workspace trust was not changed.
- *Ownership and narrow scope.* Line 7 places the change in U03 / #87, in the scanner and its tests only. Line 9 rules out changes to the adapter, marker or receipt matcher, service, ledger, schemas, provider input, cutoff skipping, workspace trust and provider roots.
- *Fail-closed prefix.* Recognition applies only strictly before the authenticated first origin, only on the existing pinned Claude route, and only with the same explicit session, a valid native timestamp and the existing format checks. Queue rows must have exact key sets. Attachments must be root-session and non-sidechain, form a fixed parent chain (hook-success with null parent, then additional-context whose parent is that hook-success), and lead to an origin user row whose native parent is the additional-context attachment. Any unrecognized timed prefix row keeps the hold. Line 9 forbids crossing any unresolved usage-bearing, unfamiliar, malformed or wrong-session row, and keeps genuinely unanchored first segments held until exact enrollment.
- *Checkout authority.* Matched rows supply no checkout, enrollment, usage, quota, accounting context, scope or watermark. Later checkout identity is not assigned to earlier rows. Content and hook checkout are not treated as authority. Rows after the origin stay on the ordinary adapter path, so receipt-chain handling is unchanged.
- *Cursor continuity.* Excluded rows still authenticate the cursor and continuity through their original bytes and ordinals. Line 13 requires checks for restart, archive and prefix continuity.
- *Retained evidence and repaired-release proof.* Line 13 requires RED on the released scanner, GREEN on both real orders, and SQLite proof that the original retained source and command settle through the exact installed scanner and adapter. That proof must show the intended first measured request after enrollment and no out-of-scope usage. Source bytes stay unchanged and private. Line 15 requires both wheels to be rebuilt and all collector-produced evidence regenerated. Old collector state, sequence, status, health and receipts cannot qualify the repaired wheel. Fresh native execution is required wherever chronology or freshness is missing. Production install waits for the real isolated GUI recovery rehearsal.
- *Core exclusion.* Line 15 leaves Core #2 outside execution and keeps the approved production project identity and lifetime service.

The fail-closed design is sound. Three gaps make it less precise or checkable than it needs to be at XPR, set out below.

## Findings

1. **F1 — The prefix sequence's cardinality, order and mandatory membership are implied, not stated (moderate, fail-closed precision).** Line 7 says the "contiguous allowlist comprises only the observed queue enqueue … and dequeue …, then the two observed SessionStart attachment forms." It does not say:
   - that each of the four rows must appear exactly once;
   - that they must appear in exactly the order enqueue → dequeue → hook-success → hook-additional-context → origin;
   - that a partial sequence (for example, attachments with no queue rows, or queue rows with no additional-context attachment) does not match.

   An implementer could read "allowlist" as a set of permitted row kinds. That reading would accept repeated enqueue/dequeue pairs, several hook-success attachments (one per configured SessionStart hook), reordered rows, or subsets. The parent-chain rule limits some of these, but queue rows have no UUID chain. They are bound only by position and session, so their count and order must be explicit.

   The negative coverage on line 13 also misses cases that matter most for this rule:
   - duplicated or reordered prefix rows;
   - a missing queue row or a missing additional-context attachment;
   - an origin whose native parent is not the additional-context attachment (only "unrelated hook parent" on the attachment is listed);
   - a complete matching prefix at EOF with no origin yet. This is the live-tailing case: the rule must keep the hold and must not commit and later reinterpret.

2. **F2 — Attachment acceptance is not a closed key set, unlike the queue rows (moderate, fail-closed precision).** Line 7 gives exact native key sets for queue rows. For attachments it says only "the observed typed envelope and bounded hook metadata." "Bounded" is not defined. It could mean size, a key subset, or allowed values. So the amendment does not say whether an attachment with extra top-level or nested fields matches or holds. The "apparent usage" negative covers one such field. It does not establish the general rule that any key outside the enumerated envelope keeps the hold. The fail-closed guarantee depends on that rule.

3. **F3 — The forecast cannot be checked against the remaining caps (moderate, estimates).**
   - **U11.** `desktop-marker-recovery-jit.md` line 11 set a recovery forecast of at most 2.5 remaining non-workload hours inside the 3.5-hour portion. Line 19 now allows "no more than 2.25 further U11 non-workload agent-hours within its 3.5-hour non-workload portion." That only fits if no more than 1.25 non-workload hours have been used through the second pause. The amendment states no consumed-to-date figure or bound, so a reviewer cannot confirm that 2.25 fits. The desktop-marker amendment's forecast (lines 15–19) did give observed intervals before asserting fit.
   - **Workload interval.** "520.034 seconds … through the second pause" and "leaving at least 1,279.966 seconds" appear nowhere else in the committed `.aitm` tree. `agent-usage.md` does not record this interval, and neither the #96 diagnostic nor the earlier #96 diagnostics do either. The figure may be correct, but it has no durable source pointer.
   - **U03 wording.** "Keep the 3.5-hour U03 … estimates. Allow up to 0.75 additional U03 agent-hour" can be read as raising U03 to 4.25 h. The recorded #87 intervals (about 21 implementer minutes plus the 30-minute supplement) suggest it fits inside 3.5 h, but the text should say so.

## Required changes

1. **(F1)** In line 7, state that the excluded prefix is exactly one enqueue, one dequeue, one hook-success attachment and one hook-additional-context attachment, contiguous and in that order, followed immediately by the verified origin. Any repeat, reorder, omission, extra hook attachment or partial sequence must keep the hold. Exclusion takes effect only after the origin is authenticated; until then the matched rows stay held. In line 13, add negative coverage for: duplicated or reordered prefix rows; a missing queue row or missing additional-context attachment; an origin whose native parent is not the additional-context attachment; and a complete matching prefix at EOF with no origin, which must keep holding and commit nothing.
2. **(F2)** In line 7, define attachment acceptance as a closed envelope, as for queue rows. Enumerate the permitted top-level keys and the permitted hook-metadata keys or bounds (privately sourced names are acceptable if publishing them is a concern; then cite the private sanitized key list). State that any other key keeps the hold. Add a negative test for an attachment with an extra unexpected key.
3. **(F3)** In line 19:
   - state U11 non-workload consumption to date, or a conservative upper bound, so that "2.25 further within 3.5" can be checked;
   - give a durable pointer or a short derivation for the 520.034-second workload interval (for example, an `agent-usage.md` or #96 attachment row listing the two workload intervals);
   - say that the 0.75 U03 hour falls within the existing 3.5-hour U03 cap, with consumption to date.

## Optional suggestions

1. As private, count-only evidence, run the repaired scanner read-only over the 13 retained Claude sources and record only aggregate counts: matched, held, failed. This confirms that the exact allowlist covers every observed variant. A variant shape, such as a different number of SessionStart hooks, would otherwise re-stall #96 qualification and only surface later.
2. Say how untimed rows that may appear between prefix rows are handled. For example: they are unchanged from existing scanner behaviour and do not break contiguity. Without this, "contiguous" and "any unrecognized timed prefix row" leave the untimed case implicit.
3. In line 7, note that the observed shape depends on the locally configured SessionStart hook set. If the qualification environment's hooks change (added, removed, or emitting no additional context), the result is a hold and a return to Planning, not a scanner change during execution.

## Decision

revisions-requested
