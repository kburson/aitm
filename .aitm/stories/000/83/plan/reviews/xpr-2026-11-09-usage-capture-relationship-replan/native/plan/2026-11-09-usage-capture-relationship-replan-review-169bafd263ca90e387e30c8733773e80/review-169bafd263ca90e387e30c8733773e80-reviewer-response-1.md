<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-169bafd263ca90e387e30c8733773e80"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md"
artifact_commit: "cb260cbf200a1dc4a9c9bf51ba3c28446940230a"
artifact_blob: "0d14bcf7f40c3e8b3ad101cb79af54b2ea0cdb71"
artifact_digest: "sha256:808783745a4d374df12f84505c37b0e0a0d496bdcb263877ef34b579cd1b3c86"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:b8abc3f5780ff388a9c4be71d3699780de9374625a3555d8e60b340df430ea14"
  identity_source: "runtime"
started_at: "2026-11-09T16:29:24.792Z"
submitted_at: "2026-11-09T16:32:37.289Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent XPR review of `.aitm/stories/000/83/plan/usage-capture-relationship-replan.md` at sealed digest `sha256:808783745a4d374df12f84505c37b0e0a0d496bdcb263877ef34b579cd1b3c86` (commit `cb260cb`, blob `0d14bcf`).

**Read evidence.** I read the artifact fresh with the Read tool in two contiguous chunks of at most 20 lines: lines 1–20, then 21–26. The second chunk reached EOF at line 26. Neither chunk was truncated or replaced by an omission marker. This is the first turn of this review ID, so no prior response or dispositions exist to verify.

For context I read these files in full:

- the accepted first amendment `plan/usage-capture-replan.md` (lines 1–51, EOF);
- baseline plan lines 30–109, which hold the sizing table, the command contract and the U01, U02 and U13 sections;
- the #86 `story.md`, `design/design.md`, `plan/implementation-plan.md`, `plan/jit.md` and `plan/pickup-review.md`;
- the SAR record for this amendment: manifest, reviewer and author responses, and `patch-000.diff`.

I also read the earlier XPR turn-1 reviewer response, but only to match its format. I did not rely on the SAR conclusion.

Only the join and submit commands were available to me. I could not run Git, check that the candidate and integration commits exist, or recompute the SHA-256 on line 3. Product source is not checked out in this planning worktree, so I could not inspect U02's inbox lock or drain loop directly.

**Lineage observation (not a finding).** SAR accepted different bytes, `sha256:2e2d9eea…5c1` at `c6553b7` (25 lines). Commit `cb260cb` later strengthened item 1 with in-ledger graph recomputation and item 2 with a mutex-held drain snapshot. It also added regressions for forged revisions, invalid children, graph-invalid effects and an interleaved publisher. There is no SPR record for this amendment in this worktree. Line 3 and the resume gate (line 25) already require SAR, SPR and XPR acceptance of the exact accepted bytes, so this is a gate the author must close, not a defect in the text. The #86 repair plan and JIT should pin the final digest, not `2e2d…`.

**Verified as sound.**

- *Exact pins.* The candidate `544844a…` on `codex/aitm-usage-u13` matches the #86 `story.md` (line 47). The integration base `67e888d…` matches #86 `pickup-review.md` (line 11) and `jit.md` (line 3). The prior-amendment pin `7df41b26…` matches the #86 design (line 3) and plan (line 3).
- *Diagnosis.* Both defects are real contract gaps and not implementation slips. The first amendment (line 18) says "Ledger append consumes validated records" but never forbids a generic `apply` of relationship types. U02's row (line 28) defines identity, digest and disposition, but no ordering among queued commands. Ordering by opaque ID is a natural reading of that gap, and it reverses causally dependent relationship commands.
- *Ownership.* Line 13 widens U13 by exactly two `ledger.py` checks and the relationship-publication adaptations in `scopes.py`. It keeps U02's provider command order and boundary attestation (line 16), and U08 and U06 ownership. This fits the first amendment's rule that unassigned edits need replanning (line 38), and it supplies the planning return that #86 plan line 16 anticipated ("If this requires an unassigned ledger.py edit, return to planning").
- *Admission (item 1).* The plan rejects direct `apply` for both relationship types, for same-project and foreign-project payloads, before any durable write. `commit_command` must match type, project and command ID, and effects are committed atomically with the disposition. The validation order (exact replay, then expected-sequence check, then recomputation) keeps replays idempotent and makes recomputation deterministic against the fixed sequence.
- *Ordering (item 2).* Allocating the order under the publication lock and persisting it atomically with the command gives a total order that survives a restart. Keeping the order outside the canonical bytes, digest and ID keeps exact replay idempotent. Snapshotting under the same mutex and then releasing it before commits avoids holding the lock across ledger work. I traced the "allocate within the outstanding queue" option through four cases and found no inversion as long as committed-but-unretired items still count as outstanding:
  - publishing while a snapshot is in flight;
  - publishing after a partial retirement;
  - publishing after a full drain;
  - a crash between commit and retirement.
- *Regressions.* The first bullet covers the reported bypass and its forged variants. The second reproduces the reported inversion with deliberately reversed IDs on the real CLI while the writer lease is held. It also covers supersession of a later parent with older fixed views intact, an interleaved partial drain, restart order, idempotent replay and conflicting replay.
- *Estimate and hold.* Forty-five agent-minutes on top of an observed nine-minute interval fits easily within U13's three-hour cap. The 48.5-hour, thirteen-leaf aggregate and the four-hour leaf cap are unchanged, and a stop rule covers forecast breach or new unassigned scope. Line 25 holds all other leaves.
- *Lifetime and activation.* The lifetime design, issue IDs and dependency order continue (line 3). Epic #2 stays unstarted and Core C01 stays blocked on qualified #83 activation (line 25). No Core work is introduced.

**Areas needing revision.** Two precision gaps remain in the new shared-path contracts. The plan does not say where the U13 graph validator lives, how `ledger.py` reaches it, or what a "verified equivalent" is. That leaves module ownership and the trust mechanism open (F1). The drain's behaviour when an earlier ordered relationship command fails, is malformed or has an ambiguous order is also unstated. A skip-and-continue drain would bring back the reported inversion (F2).

## Findings

1. **F1 (required): The validator's location, import direction and "verified equivalent" are unspecified in a shared write path.** Line 15 requires `commit_command` in `ledger.py` to obtain the complete effect tuple "from the same U13 graph validator used by the dispatcher". It may instead "use a verified equivalent that direct callers cannot bypass". The amendment does not name the module that holds the validator.
   - U13's stated files (line 13: `types.py` envelopes, CLI, "relationship projection", tests) do not clearly include a validator module. If the validator lives in `rollup.py`, U01's `ledger.py` would import a U13 feature module that itself imports `LedgerView` from `ledger.py`. That is an inverted layer and an import cycle. A new module would be an unassigned file. The first amendment (lines 18 and 38) rules out a runtime registry.
   - An injected validator, such as a callable passed to `commit_command` or registered by the dispatcher, is exactly what a direct caller could replace with a permissive one.
   - "Verified equivalent" might mean a sealed token or a MAC over the effect tuple. That would add key handling to `ledger.py`, which goes beyond the "two narrow write-admission checks" on line 13.

   An implementer could choose any of these readings. Several of them breach ownership or reopen the bypass, and the result would be a second hold.

2. **F2 (required): Drain behaviour on a failed, malformed or ambiguously ordered relationship command is unstated, and skip-and-continue reproduces the reported defect.** Item 2 requires publication order between relationship commands that wait together. It requires "Refuse malformed or ambiguous ordered publication safely". It says a partial drain "preserves the relative order of all remaining commands". It does not say what the drainer does with later commands when an earlier one fails to reach a committed disposition. Examples are a transient write error, a validator exception, or a malformed or duplicate-order entry found at drain time.

   Concrete failure: a parent repair (order 1) fails transiently. The drain continues to the graduation (order 2), which is graph-invalid without the repair, so it receives a *final, immutable* rejection. The repair then succeeds on the next drain. The valid graduation is permanently refused, which is the outcome described on line 7.

   "Relative order of all remaining commands" still holds in that trace, because only the repair remains. So the text does not exclude it. U02's general drain may reasonably isolate per-command failures for markers or quarantine malformed files, and that pattern would carry over by default. "Safely" for an ambiguous order, such as two pending commands sharing one order value, is also undefined. It could mean halt, reject both, or choose one. The regression list has no case for a failing first command or for malformed or duplicate order entries.

## Required changes

1. **(F1)** In item 1, name the module that holds the relationship graph validator, and state these points.
   - (a) The module is U13-owned, either an existing U13 file or one named file added to U13's list. It has no import dependency on `ledger.py` beyond typed records and a read-only view interface, so `ledger.py` can import it statically without a cycle. An equivalent is a pure function over `types.py` records that both the dispatcher and `ledger.py` call.
   - (b) `commit_command` calls it statically. The validator is never passed in, injected or registered by callers.
   - (c) Either delete the "verified equivalent" alternative or define it concretely, together with its ownership and test.

   Keep the stated limit of two narrow checks in `ledger.py`.
2. **(F2)** In item 2, state the drain rule for relationship commands.
   - (a) Apply them strictly in publication order. Stop the relationship drain at the first command that does not reach a committed disposition, and leave it and all later relationship commands queued for the next drain. Alternatively, define an equivalent rule that never gives a later relationship command a final disposition before every earlier one has one.
   - (b) Define the safe outcome for a malformed or ambiguous order found at drain time, such as a missing order, a duplicate order value, or a non-closed shape. This could be a fail-closed halt of the relationship drain with a sanitized diagnostic, or a final rejection of the specific malformed entry only when its position is unambiguous. Never reorder.
   - (c) Add regressions:
     - inject a failure on the first of two queued dependent relationship commands, and show the second is neither applied nor finally rejected until the first commits;
     - show that a duplicate-order or malformed-order entry is refused without reordering or consuming later commands.

   These regressions fit within the 45-minute forecast. If they do not, record that under the existing stop rule.

## Optional suggestions

1. **O1 (forged rejections).** Recomputation on line 15 applies "for any new accepted relationship write". A direct `commit_command` caller could still record a final *rejected* disposition for a valid relationship command. That permanently refuses it without changing effects. Consider requiring that any final relationship disposition, accepted or rejected, match the validator outcome at the expected sequence. Add one forged-rejection case to the first regression bullet.
2. **O2 (reset proof).** If the implementation chooses "allocate within the outstanding queue", name its reset proof in the regression list. The cases are: publish during an in-flight snapshot, publish after partial retirement, publish after a full drain, and a crash between commit and retirement. In each case a newly published command must sort after every still-outstanding command.
3. **O3 (U08 compatibility).** State that non-relationship commands, including U08's later source-anchor command, pass through the closed transport shape without an order field or ordering logic. U08 then adds only its codec and dispatch case and needs no edit to U13's ordering path.
4. **O4 (lineage record).** Cite or link the #86 source-review record and the disposable probe evidence on line 7, so that the #86 repair plan and the later exact-head source review can trace both reproduced defects to retained evidence. Pin the final accepted digest of this amendment in the #86 repair plan and JIT, not the SAR digest `2e2d…`.

## Decision

revisions-requested
