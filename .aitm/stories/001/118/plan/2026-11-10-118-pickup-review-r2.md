# #118 independent pickup review, round 2

Reviewer **Claude Opus 5.5, high**. Off-platform exact pickup and split on November 10, 2026.

# #118 re-review: M08a pickup PASS, M08b split HOLD

**M08a pickup: PASS.** **M08b split: HOLD**, because one accepted M08 obligation has no owner. Fixing it means adding one sentence to the split.

I did not use any tools for this review. I could not check the two SHA-256 values, the Closed/Done state of #117, #182 and #194, PR #198, the baseline numbers, or any source outside this packet.

## M08a pickup: PASS

| Item | Result | Basis |
|---|---|---|
| **B1** | Fixed | Durable disputes now cover only a verified competing owner. Changed same-owner content is held, keeps the earlier cursor and pending bytes, and creates no durable conflict in M08a. "A higher integer or changed token count is insufficient" closes the numeric-succession shortcut. The split repeats this rule. |
| **B2** | Fixed | `read_source(..., cursor=prior)` checks the prior physical prefix through `_capture_position(..., fixed=checkpoint.cursor)`. It then calls `read_delta(current, None, ..., _capture_limit=native_cursor)`, which re-reads the whole prefix. This makes replay after reopen work: already-staged observations come back and are absorbed by the exact-content idempotence rule. Nothing can be skipped by a frontier held in memory. A missing `batch.cursor` is now refused. Replay from the prior cursor after reopen is inside the checkpoint. |
| **B3** | Fixed, and narrower than my first fix | The source shows that only REQUEST boundaries with a serial, same-turn, unambiguous receipt carry `receipt.reference`. Turn-start boundaries never do. Making receipt-linked boundaries the obligation, and matching each one to a durable ScopeState event or hold, is the correct rule. My earlier "every boundary" fix would have blocked on boundaries that are only structural. The receipt-at-end-of-batch test is required. |
| **B4** | Fixed | `publish_noreplace` already maps to `renameatx_np` with `0x4` (RENAME_EXCL), which returns False on EEXIST. That removes most of the extra store cost I flagged, and an empty target is refused. The figures add up: 1.10 + 0.85 + about 0.30 for the copy-key fixture fits in 2.25 hours. The remaining 1.50 hours covers claims/transactions (0.60), integration (0.45) and reserve (0.45). Rollback now comes after the checkpoint, with a stop-and-re-review rule and a reopen limit under four hours. |

All of my earlier non-blocking amendments are addressed:
- The `source_key_id` check happens before `source_evidence()`.
- A fresh write-time `ScopeState.view(batch)` is issued at write time.
- The lease token is invalidated when the writer's context exits, and there is a test that uses an old handle after reopen.
- Both accepted test names are mapped.
- The copy fixture is inside the checkpoint.

**Wording fixes. None of these blocks the pickup:**
1. **Recorded dispute versus cursor.** The pickup says an already recorded ownership dispute is "replay-safe", but also lists a "competing owner" among the things that keep the cursor in place. Because every read re-reads the full prefix, the second reading would stall that stream permanently once a dispute exists. Both readings are safe for a dormant slice, so pick one. I recommend: an exact, durably recorded dispute settles that obligation for cursor movement, and only a new competing owner that isn't recorded yet blocks.
2. **Ambiguous or conflicting receipts.** When `context.ambiguous` or `context.conflict` is set, `receipt` becomes `None`. The boundary then looks like an ordinary request boundary that isn't linked to a receipt. Add one fixture showing this surfaces as a kept diagnostic or a tainted hold, and doesn't let the cursor advance silently.
3. **Copy key without a session reference.** `stream_ref` falls back to `locator` when `session_ref` is missing. The copy fixture should cover that case too. A copy must either deduplicate on the adapter's observation key or be held. It must never produce a second canonical claim.
4. **"First owning project" versus "every claim".** The pickup stores span and epoch for the first owning project, but the split says every claim. Make the dispute record carry the competing project's epoch eligibility too, or align the wording.

## M08b split: HOLD

| Item | Result |
|---|---|
| **S1** | Fixed. Both documents now carry the same same-owner hold rule, and stale or copied revisions cannot release a dispute. |
| **S2** | Fixed. Every claim stores source, surface, session, stream, the half-open native span, and the capture epoch generation and boundary reference. Because M08a is dormant source, M08b can change the schema version without a migration. Saying that explicitly would make it airtight. |
| **S3** | Fixed. `test_causal_revision_survives_stale_replay_after_restart` and `record_disposition` are assigned to M08b. |
| **S4** | Fixed. If a missing covering producer would reorder M09 or M11, #119 is held and the changed parent plan needs independent re-acceptance. A narrow re-split cannot clear that. Unknown overlap produces no positive proof. |

The dependencies are correct: M08b depends on #118 and blocks #119, #118 stays a direct prerequisite of #119, and rank 225 sits between them.

**Why it's on HOLD: the accepted rule "Incomparable content becomes disputed" has no owner.**
- The accepted M08 contract has three outcomes for revisions:
  - a causal successor supersedes the current revision;
  - identical or proven-older revisions have no additive effect;
  - incomparable content becomes disputed.
- M08a now holds every changed same-owner revision, which is correct.
- M08b is assigned the causal successor and stale (older) revisions only.
- Nothing assigns the step that turns held same-owner content proven *incomparable* into a durable dispute.
- Without it, that hold never resolves, and #119 would start with the obligation silently dropped.

**Fix:** add one line to M08b:
> M08b turns held same-owner changed content into a causal successor, a proven-older no-op, or a durable incomparable-content dispute. Each outcome is bound to the exact predecessor and the later evidence span. A hold that M08b cannot decide stays held and keeps the cursor replayable.

Once that line is in, the split is a PASS.
